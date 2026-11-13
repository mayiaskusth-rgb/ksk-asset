import { fetchMock, SELF, env } from "cloudflare:test";
import { afterAll, beforeAll, describe, expect, it } from "vitest";

const keyId = "ksk-api-integration-test-key";
let authorization: string;
let issuer: string;

function base64Url(bytes: Uint8Array): string {
  let binary = "";
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary).replace(/=/g, "").replace(/\\+/g, "-").replace(/\\//g, "_");
}

function encodeJson(value: unknown): string {
  return base64Url(new TextEncoder().encode(JSON.stringify(value)));
}

async function createAccessToken(): Promise<string> {
  const pair = await crypto.subtle.generateKey(
    { name: "RSASSA-PKCS1-v1_5", modulusLength: 2048, publicExponent: new Uint8Array([1, 0, 1]), hash: "SHA-256" },
    true,
    ["sign", "verify"],
  );
  const publicJwk = await crypto.subtle.exportKey("jwk", pair.publicKey);
  const jwks = { ...publicJwk, kid: keyId, alg: "RS256", use: "sig" };
  fetchMock.get(issuer)
    .intercept({ path: "/cdn-cgi/access/certs", method: "GET" })
    .reply(200, { keys: [jwks] });

  const header = encodeJson({ alg: "RS256", typ: "JWT", kid: keyId });
  const payload = encodeJson({
    iss: issuer,
    aud: env.ACCESS_AUD,
    exp: Math.floor(Date.now() / 1000) + 3600,
    nbf: Math.floor(Date.now() / 1000) - 5,
    email: "integration-test@example.invalid",
  });
  const unsigned = `${header}.${payload}`;
  const signature = await crypto.subtle.sign(
    "RSASSA-PKCS1-v1_5",
    pair.privateKey,
    new TextEncoder().encode(unsigned),
  );
  return `${unsigned}.${base64Url(new Uint8Array(signature))}`;
}

async function authenticatedFetch(path: string, init: RequestInit = {}): Promise<Response> {
  const headers = new Headers(init.headers);
  headers.set("cf-access-jwt-assertion", authorization);
  return SELF.fetch(`https://worker.test${path}`, { ...init, headers });
}

describe("KSK private research API", () => {
  beforeAll(async () => {
    issuer = `https://${env.ACCESS_TEAM_DOMAIN}.cloudflareaccess.com`;
    fetchMock.activate();
    fetchMock.disableNetConnect();
    authorization = await createAccessToken();
  });

  afterAll(() => {
    fetchMock.assertNoPendingInterceptors();
  });

  it("exposes only a minimal health response without authentication", async () => {
    const response = await SELF.fetch("https://worker.test/health");
    expect(response.status).toBe(200);
    expect(await response.json()).toEqual({ ok: true, service: "ksk-research-api" });
  });

  it("rejects unauthenticated reads and writes", async () => {
    const read = await SELF.fetch("https://worker.test/api/videos/efjBiVN_N3M");
    expect(read.status).toBe(401);
    const write = await SELF.fetch("https://worker.test/api/videos", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ video_id: "efjBiVN_N3M" }),
    });
    expect(write.status).toBe(401);
  });

  it("saves, deduplicates, versions, and retrieves transcripts through authenticated Worker routes", async () => {
    const videoId = "efjBiVN_N3M";
    const videoResponse = await authenticatedFetch("/api/videos", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ video_id: videoId, title: "Integration test video", channel_name: "KSK Tests" }),
    });
    expect(videoResponse.status).toBe(201);
    expect(await videoResponse.json()).toMatchObject({ video_id: videoId, project_id: "default" });

    const firstText = "This is the first manually added transcript.";
    const firstResponse = await authenticatedFetch(`/api/videos/${videoId}/transcripts`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ content_text: firstText, language_code: "en" }),
    });
    expect(firstResponse.status).toBe(201);
    const first = await firstResponse.json() as { transcript_id: string; revision: number };
    expect(first.revision).toBe(1);

    const duplicateResponse = await authenticatedFetch(`/api/videos/${videoId}/transcripts`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ content_text: firstText, language_code: "en" }),
    });
    expect(duplicateResponse.status).toBe(200);
    expect(await duplicateResponse.json()).toMatchObject({
      transcript_id: first.transcript_id,
      revision: 1,
      unchanged: true,
    });

    const secondText = "This is the edited transcript with a correction.";
    const secondResponse = await authenticatedFetch(`/api/videos/${videoId}/transcripts`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ content_text: secondText, language_code: "en" }),
    });
    expect(secondResponse.status).toBe(201);
    expect(await secondResponse.json()).toMatchObject({ revision: 2 });

    const readResponse = await authenticatedFetch(`/api/videos/${videoId}`);
    expect(readResponse.status).toBe(200);
    const saved = await readResponse.json() as {
      video: { video_id: string; title: string };
      transcripts: Array<{ revision: number; content_text: string; language_code: string }>;
    };
    expect(saved.video).toMatchObject({ video_id: videoId, title: "Integration test video" });
    expect(saved.transcripts).toHaveLength(2);
    expect(saved.transcripts.map((transcript) => transcript.revision)).toEqual([2, 1]);
    expect(saved.transcripts[0]).toMatchObject({ content_text: secondText, language_code: "en" });
    expect(saved.transcripts[1]).toMatchObject({ content_text: firstText, language_code: "en" });
  });
});
