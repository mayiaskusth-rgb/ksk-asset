import { SELF } from "cloudflare:test";
import { describe, expect, it } from "vitest";

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
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ video_id: "efjBiVN_N3M" }),
    });
    expect(write.status).toBe(401);
  });

});
