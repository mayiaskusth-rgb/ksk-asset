import { SELF, env } from "cloudflare:test";
import { describe, expect, it } from "vitest";

const APP_ORIGIN = "https://mayiaskusth-rgb.github.io";
const TEST_PASSWORD = "test-owner-password-only";
let sessionToken = "";

async function login(password = TEST_PASSWORD): Promise<Response> {
  return SELF.fetch("https://worker.test/api/auth/login", {
    method: "POST",
    headers: { "content-type": "application/json", Origin: APP_ORIGIN },
    body: JSON.stringify({ password }),
  });
}

async function authenticatedFetch(path: string, init: RequestInit = {}): Promise<Response> {
  if (!sessionToken) {
    const response = await login();
    expect(response.status).toBe(200);
    sessionToken = (await response.json() as { token: string }).token;
  }
  const headers = new Headers(init.headers);
  headers.set("authorization", "Bearer " + sessionToken);
  if (init.body && !headers.has("content-type")) headers.set("content-type", "application/json");
  return SELF.fetch("https://worker.test" + path, { ...init, headers });
}

describe("KSK private research API", () => {
  it("exposes only a minimal health response without authentication", async () => {
    const response = await SELF.fetch("https://worker.test/health");
    expect(response.status).toBe(200);
    expect(await response.json()).toEqual({ ok: true, service: "ksk-research-api" });
  });

  it("rejects unauthenticated reads and writes", async () => {
    const read = await SELF.fetch("https://worker.test/api/videos/efjBiVN_N3M");
    expect(read.status).toBe(401);
    const write = await SELF.fetch("https://worker.test/api/videos", {
      method: "POST", headers: { "content-type": "application/json" },
      body: JSON.stringify({ video_id: "efjBiVN_N3M" }),
    });
    expect(write.status).toBe(401);
  });

  it("rejects incorrect passwords and issues short-lived sessions for the owner", async () => {
    const bad = await login("incorrect-password");
    expect(bad.status).toBe(401);
    const good = await login();
    expect(good.status).toBe(200);
    expect(await good.json()).toMatchObject({ expires_in: 1200 });
  });

  it("saves, deduplicates, versions, and retrieves transcripts through authenticated Worker routes", async () => {
    const videoId = "efjBiVN_N3M";
    const videoResponse = await authenticatedFetch("/api/videos", {
      method: "POST", body: JSON.stringify({ video_id: videoId, title: "Integration test video", channel_name: "KSK Tests" }),
    });
    expect(videoResponse.status).toBe(201);

    const firstText = "This is the first manually added transcript.";
    const firstResponse = await authenticatedFetch(`/api/videos/${videoId}/transcripts`, {
      method: "POST", body: JSON.stringify({ content_text: firstText, language_code: "en" }),
    });
    expect(firstResponse.status).toBe(201);
    const first = await firstResponse.json() as { transcript_id: string; revision: number };
    expect(first.revision).toBe(1);

    const duplicateResponse = await authenticatedFetch(`/api/videos/${videoId}/transcripts`, {
      method: "POST", body: JSON.stringify({ content_text: firstText, language_code: "en" }),
    });
    expect(duplicateResponse.status).toBe(200);
    expect(await duplicateResponse.json()).toMatchObject({ transcript_id: first.transcript_id, revision: 1, unchanged: true });

    const secondText = "This is the edited transcript with a correction.";
    const secondResponse = await authenticatedFetch(`/api/videos/${videoId}/transcripts`, {
      method: "POST", body: JSON.stringify({ content_text: secondText, language_code: "en" }),
    });
    expect(secondResponse.status).toBe(201);
    expect(await secondResponse.json()).toMatchObject({ revision: 2 });

    const readResponse = await authenticatedFetch(`/api/videos/${videoId}`);
    expect(readResponse.status).toBe(200);
    const saved = await readResponse.json() as { video: { video_id: string; title: string }; transcripts: Array<{ revision: number; content_text: string; language_code: string }> };
    expect(saved.video).toMatchObject({ video_id: videoId, title: "Integration test video" });
    expect(saved.transcripts).toHaveLength(2);
    expect(saved.transcripts.map((transcript) => transcript.revision)).toEqual([2, 1]);
    expect(saved.transcripts[0]).toMatchObject({ content_text: secondText, language_code: "en" });
    expect(saved.transcripts[1]).toMatchObject({ content_text: firstText, language_code: "en" });
  });

  it("rejects a session token with a modified signature", async () => {
    const token = sessionToken || (await (async () => {
      const response = await login();
      return (await response.json() as { token: string }).token;
    })());
    const response = await SELF.fetch("https://worker.test/api/videos/efjBiVN_N3M", {
      headers: { authorization: "Bearer " + token.slice(0, -1) + (token.endsWith("a") ? "b" : "a") },
    });
    expect(response.status).toBe(401);
  });
});
