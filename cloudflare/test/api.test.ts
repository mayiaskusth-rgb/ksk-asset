import { SELF, env } from "cloudflare:test";
import { describe, expect, it } from "vitest";

const APP_ORIGIN = "https://mayiaskusth-rgb.github.io";
const TEST_PASSWORD = "test-owner-password-only";
let sessionToken = "";

async function login(password = TEST_PASSWORD, clientIp = "198.51.100.10"): Promise<Response> {
  return SELF.fetch("https://worker.test/api/auth/login", {
    method: "POST",
    headers: { "content-type": "application/json", Origin: APP_ORIGIN, "cf-connecting-ip": clientIp },
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
    const bad = await login("incorrect-password", "198.51.100.11");
    expect(bad.status).toBe(401);
    const good = await login(TEST_PASSWORD, "198.51.100.12");
    expect(good.status).toBe(200);
    expect(await good.json()).toMatchObject({ expires_in: 1200 });
  });

  it("rate limits repeated login attempts from one client IP", async () => {
    const ip = "198.51.100.77";
    for (let attempt = 0; attempt < 5; attempt++) {
      const response = await login("incorrect-password", ip);
      expect(response.status).toBe(401);
    }
    const blocked = await login(TEST_PASSWORD, ip);
    expect(blocked.status).toBe(429);
    expect(await blocked.json()).toMatchObject({ error: "too_many_login_attempts" });
  });

  it("saves, edits in place, deduplicates, and retrieves one current transcript", async () => {
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

    const editedText = "This is the edited transcript with a correction.";
    const editResponse = await authenticatedFetch(`/api/videos/${videoId}/transcripts`, {
      method: "POST", body: JSON.stringify({ content_text: editedText, language_code: "en" }),
    });
    expect(editResponse.status).toBe(200);
    expect(await editResponse.json()).toMatchObject({ transcript_id: first.transcript_id, revision: 1, updated: true });

    const readResponse = await authenticatedFetch(`/api/videos/${videoId}`);
    expect(readResponse.status).toBe(200);
    const saved = await readResponse.json() as { video: { video_id: string; title: string }; transcripts: Array<{ revision: number; content_text: string; language_code: string }> };
    expect(saved.video).toMatchObject({ video_id: videoId, title: "Integration test video" });
    expect(saved.transcripts).toHaveLength(1);
    expect(saved.transcripts[0]).toMatchObject({ revision: 1, content_text: editedText, language_code: "en" });
  });

  it("rejects a session token with a modified signature", async () => {
    const token = sessionToken || (await (async () => {
      const response = await login();
      return (await response.json() as { token: string }).token;
    })());
    const response = await SELF.fetch("https://worker.test/api/videos/efjBiVN_N3M", {
      headers: { authorization: "Bearer " + token.split(".")[0] + "." + (token.split(".")[1][0] === "a" ? "b" : "a") + token.split(".")[1].slice(1) },
    });
    expect(response.status).toBe(401);
  });
});
