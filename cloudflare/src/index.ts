interface Env {
  DB: D1Database;
  ACCESS_TEAM_DOMAIN: string;
  ACCESS_AUD: string;
}

type AccessClaims = { iss?: string; aud?: string | string[]; exp?: number; nbf?: number; email?: string };

let cachedKeys: { expiresAt: number; keys: JsonWebKey[] } | undefined;
const APP_ORIGIN = "https://mayiaskusth-rgb.github.io";

function json(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store", "access-control-allow-origin": APP_ORIGIN, "access-control-allow-credentials": "true", "vary": "Origin" },
  });
}

function decodeBase64Url(value: string): Uint8Array {
  const normalized = value.replace(/-/g, "+").replace(/_/g, "/");
  const binary = atob(normalized.padEnd(Math.ceil(normalized.length / 4) * 4, "="));
  return Uint8Array.from(binary, (char) => char.charCodeAt(0));
}

async function accessClaims(request: Request, env: Env): Promise<AccessClaims | null> {
  const token = request.headers.get("cf-access-jwt-assertion");
  if (!token || !env.ACCESS_TEAM_DOMAIN || !env.ACCESS_AUD) return null;

  try {
    const [encodedHeader, encodedPayload, encodedSignature] = token.split(".");
    if (!encodedHeader || !encodedPayload || !encodedSignature) return null;
    const header = JSON.parse(new TextDecoder().decode(decodeBase64Url(encodedHeader))) as { alg?: string; kid?: string };
    const claims = JSON.parse(new TextDecoder().decode(decodeBase64Url(encodedPayload))) as AccessClaims;
    if (header.alg !== "RS256" || !header.kid) return null;

    const issuer = `https://${env.ACCESS_TEAM_DOMAIN}.cloudflareaccess.com`;
    const now = Math.floor(Date.now() / 1000);
    const audiences = Array.isArray(claims.aud) ? claims.aud : [claims.aud];
    if (claims.iss !== issuer || !audiences.includes(env.ACCESS_AUD) ||
        typeof claims.exp !== "number" || claims.exp <= now ||
        (typeof claims.nbf === "number" && claims.nbf > now)) return null;

    if (!cachedKeys || cachedKeys.expiresAt < now) {
      const response = await fetch(`${issuer}/cdn-cgi/access/certs`);
      if (!response.ok) return null;
      const body = await response.json() as { keys?: JsonWebKey[] };
      if (!Array.isArray(body.keys)) return null;
      cachedKeys = { keys: body.keys, expiresAt: now + 300 };
    }
    const jwk = cachedKeys.keys.find((key) => (key as JsonWebKey & { kid?: string }).kid === header.kid);
    if (!jwk) return null;
    const publicKey = await crypto.subtle.importKey(
      "jwk", jwk, { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" }, false, ["verify"],
    );
    const valid = await crypto.subtle.verify(
      "RSASSA-PKCS1-v1_5", publicKey, decodeBase64Url(encodedSignature),
      new TextEncoder().encode(`${encodedHeader}.${encodedPayload}`),
    );
    return valid ? claims : null;
  } catch {
    return null;
  }
}

async function readJson(request: Request, maxBytes: number): Promise<Record<string, unknown> | null> {
  const declaredLength = Number(request.headers.get("content-length") ?? "0");
  if (declaredLength > maxBytes) return null;
  const text = await request.text();
  if (new TextEncoder().encode(text).byteLength > maxBytes) return null;
  try {
    const value = JSON.parse(text);
    return value && typeof value === "object" && !Array.isArray(value) ? value as Record<string, unknown> : null;
  } catch {
    return null;
  }
}

function validVideoId(value: unknown): value is string {
  return typeof value === "string" && /^[A-Za-z0-9_-]{11}$/.test(value);
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    if (request.method === "OPTIONS") {
      const origin = request.headers.get("Origin");
      if (origin !== APP_ORIGIN) return new Response(null, { status: 403 });
      return new Response(null, { status: 204, headers: {
        "access-control-allow-origin": APP_ORIGIN,
        "access-control-allow-credentials": "true",
        "access-control-allow-methods": "GET, POST, OPTIONS",
        "access-control-allow-headers": "content-type, cf-access-jwt-assertion",
        "access-control-max-age": "600",
        "vary": "Origin",
      } });
    }
    if (url.pathname === "/health" && request.method === "GET") {
      return json({ ok: true, service: "ksk-research-api" });
    }

    const claims = await accessClaims(request, env);
    if (!claims) return json({ error: "unauthorized" }, 401);

    if (url.pathname === "/api/videos" && request.method === "POST") {
      const body = await readJson(request, 16 * 1024);
      if (!body || !validVideoId(body.video_id)) return json({ error: "video_id must be a valid 11-character YouTube ID" }, 400);
      const projectId = typeof body.project_id === "string" && body.project_id.length <= 100 ? body.project_id : "default";
      const canonicalUrl = `https://www.youtube.com/watch?v=${body.video_id}`;
      const title = typeof body.title === "string" ? body.title.slice(0, 500) : null;
      const channel = typeof body.channel_name === "string" ? body.channel_name.slice(0, 300) : null;
      try {
        await env.DB.batch([
          env.DB.prepare(`INSERT INTO videos (video_id, canonical_url, title, channel_name)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(video_id) DO UPDATE SET
              title = COALESCE(excluded.title, videos.title),
              channel_name = COALESCE(excluded.channel_name, videos.channel_name),
              updated_at = CURRENT_TIMESTAMP`).bind(body.video_id, canonicalUrl, title, channel),
          env.DB.prepare(`INSERT OR IGNORE INTO project_videos (project_id, video_id, added_via)
            VALUES (?, ?, 'manual')`).bind(projectId, body.video_id),
        ]);
        return json({ video_id: body.video_id, canonical_url: canonicalUrl, project_id: projectId }, 201);
      } catch {
        return json({ error: "could_not_save_video_check_project_id" }, 400);
      }
    }

    const transcriptMatch = url.pathname.match(/^\/api\/videos\/([A-Za-z0-9_-]{11})\/transcripts$/);
    if (transcriptMatch && request.method === "POST") {
      const body = await readJson(request, 600 * 1024);
      if (!body || typeof body.content_text !== "string" || !body.content_text.trim()) {
        return json({ error: "content_text is required" }, 400);
      }
      const content = body.content_text.trim();
      if (new TextEncoder().encode(content).byteLength > 512 * 1024) return json({ error: "transcript_too_large_max_512kb" }, 413);
      const language = typeof body.language_code === "string" ? body.language_code.slice(0, 20) : null;
      const checksum = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(content));
      const hash = Array.from(new Uint8Array(checksum), (b) => b.toString(16).padStart(2, "0")).join("");
      const latest = await env.DB.prepare(
        "SELECT transcript_id, revision, content_sha256 FROM transcripts WHERE video_id = ? ORDER BY revision DESC LIMIT 1",
      ).bind(transcriptMatch[1]).first<{ transcript_id: string; revision: number; content_sha256: string }>();
      if (latest?.content_sha256 === hash) {
        return json({ transcript_id: latest.transcript_id, revision: latest.revision, unchanged: true });
      }
      const transcriptId = crypto.randomUUID();
      try {
        await env.DB.prepare(`INSERT INTO transcripts
          (transcript_id, video_id, revision, status, source_type, source_provider, language_code, caption_type, content_text, content_sha256)
          VALUES (?, ?, (SELECT COALESCE(MAX(revision), 0) + 1 FROM transcripts WHERE video_id = ?),
            'available', 'manual', 'manual_paste', ?, 'unknown', ?, ?)`)
          .bind(transcriptId, transcriptMatch[1], transcriptMatch[1], language, content, hash).run();
        const saved = await env.DB.prepare("SELECT transcript_id, revision FROM transcripts WHERE transcript_id = ?")
          .bind(transcriptId).first<{ transcript_id: string; revision: number }>();
        return json(saved ?? { transcript_id: transcriptId }, 201);
      } catch {
        return json({ error: "could_not_save_transcript_video_must_exist_first" }, 400);
      }
    }

    const videoMatch = url.pathname.match(/^\/api\/videos\/([A-Za-z0-9_-]{11})$/);
    if (videoMatch && request.method === "GET") {
      const video = await env.DB.prepare("SELECT video_id, canonical_url, title, channel_name, created_at, updated_at FROM videos WHERE video_id = ?")
        .bind(videoMatch[1]).first();
      if (!video) return json({ error: "not_found" }, 404);
      const transcripts = await env.DB.prepare(`SELECT transcript_id, revision, status, source_type, language_code, caption_type, content_text, content_sha256, created_at
        FROM transcripts WHERE video_id = ? ORDER BY revision DESC`).bind(videoMatch[1]).all();
      return json({ video, transcripts: transcripts.results });
    }

    return json({ error: "not_found" }, 404);
  },
};
