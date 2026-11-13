interface Env {
  DB: D1Database;
  OWNER_PASSWORD?: string;
  SESSION_SECRET?: string;
  LOGIN_RATE_LIMITER: RateLimit;
}
const APP_ORIGIN = "https://mayiaskusth-rgb.github.io";

function json(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store", "access-control-allow-origin": APP_ORIGIN, "access-control-allow-credentials": "true", "vary": "Origin" },
  });
}

function base64Url(bytes: Uint8Array): string {
  let binary = "";
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary).replace(/=/g, "").replaceAll("+", "-").replaceAll("/", "_");
}

function decodeBase64Url(value: string): Uint8Array {
  const normalized = value.replace(/-/g, "+").replace(/_/g, "/");
  const binary = atob(normalized.padEnd(Math.ceil(normalized.length / 4) * 4, "="));
  return Uint8Array.from(binary, (char) => char.charCodeAt(0));
}

async function hmacKey(secret: string): Promise<CryptoKey> {
  return crypto.subtle.importKey("raw", new TextEncoder().encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign", "verify"]);
}

function constantTimeEqual(left: string, right: string): boolean {
  const a = new TextEncoder().encode(left);
  const b = new TextEncoder().encode(right);
  let difference = a.length ^ b.length;
  const length = Math.max(a.length, b.length);
  for (let i = 0; i < length; i++) difference |= (a[i] ?? 0) ^ (b[i] ?? 0);
  return difference === 0;
}

async function issueSession(secret: string): Promise<string> {
  const payload = base64Url(new TextEncoder().encode(JSON.stringify({
    exp: Math.floor(Date.now() / 1000) + 20 * 60,
    nonce: crypto.randomUUID(),
  })));
  const signature = await crypto.subtle.sign("HMAC", await hmacKey(secret), new TextEncoder().encode(payload));
  return payload + "." + base64Url(new Uint8Array(signature));
}

async function validSession(request: Request, secret: string): Promise<boolean> {
  const authorization = request.headers.get("authorization") ?? "";
  if (!authorization.startsWith("Bearer ")) return false;
  const [payload, signature, extra] = authorization.slice(7).split(".");
  if (!payload || !signature || extra) return false;
  try {
    const valid = await crypto.subtle.verify("HMAC", await hmacKey(secret), decodeBase64Url(signature), new TextEncoder().encode(payload));
    if (!valid) return false;
    const claims = JSON.parse(new TextDecoder().decode(decodeBase64Url(payload))) as { exp?: number; nonce?: string };
    return typeof claims.exp === "number" && claims.exp > Math.floor(Date.now() / 1000) && typeof claims.nonce === "string";
  } catch {
    return false;
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
        "access-control-allow-headers": "content-type, authorization",
        "access-control-max-age": "600",
        "vary": "Origin",
      } });
    }
    if (url.pathname === "/health" && request.method === "GET") {
      return json({ ok: true, service: "ksk-research-api" });
    }

    if (url.pathname === "/api/auth/login" && request.method === "POST") {
      if (request.headers.get("Origin") !== APP_ORIGIN) return json({ error: "forbidden_origin" }, 403);
      const clientKey = request.headers.get("cf-connecting-ip") ?? "unknown";
      const rate = await env.LOGIN_RATE_LIMITER.limit({ key: clientKey });
      if (!rate.success) return json({ error: "too_many_login_attempts" }, 429);
      if (!env.OWNER_PASSWORD || !env.SESSION_SECRET || env.SESSION_SECRET.length < 32) {
        return json({ error: "authentication_not_configured" }, 503);
      }
      const body = await readJson(request, 4 * 1024);
      if (!body || typeof body.password !== "string" || !constantTimeEqual(body.password, env.OWNER_PASSWORD)) {
        return json({ error: "invalid_credentials" }, 401);
      }
      return json({ token: await issueSession(env.SESSION_SECRET), expires_in: 1200 });
    }

    if (!env.SESSION_SECRET || env.SESSION_SECRET.length < 32 || !await validSession(request, env.SESSION_SECRET)) {
      return json({ error: "unauthorized" }, 401);
    }

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

    const transcriptMatch = url.pathname.match(/^\\/api\\/videos\\/([A-Za-z0-9_-]{11})\\/transcripts$/);
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
      try {
        const latest = await env.DB.prepare(
          "SELECT transcript_id, revision, content_sha256 FROM transcripts WHERE video_id = ? ORDER BY revision DESC LIMIT 1",
        ).bind(transcriptMatch[1]).first<{ transcript_id: string; revision: number; content_sha256: string | null }>();
        if (latest) {
          if (latest.content_sha256 === hash) {
            return json({ transcript_id: latest.transcript_id, revision: latest.revision, unchanged: true, updated: false });
          }
          await env.DB.prepare(`UPDATE transcripts
            SET status = 'available', source_type = 'manual', source_provider = 'manual_paste',
                language_code = ?, caption_type = 'unknown', content_text = ?, content_sha256 = ?,
                retrieved_at = CURRENT_TIMESTAMP
            WHERE transcript_id = ?`)
            .bind(language, content, hash, latest.transcript_id).run();
          return json({ transcript_id: latest.transcript_id, revision: latest.revision, unchanged: false, updated: true });
        }
        const transcriptId = crypto.randomUUID();
        await env.DB.prepare(`INSERT INTO transcripts
          (transcript_id, video_id, revision, status, source_type, source_provider, language_code, caption_type, content_text, content_sha256)
          VALUES (?, ?, 1, 'available', 'manual', 'manual_paste', ?, 'unknown', ?, ?)`)
          .bind(transcriptId, transcriptMatch[1], language, content, hash).run();
        return json({ transcript_id: transcriptId, revision: 1, unchanged: false, updated: false }, 201);
      } catch {
        return json({ error: "could_not_save_transcript_video_must_exist_first" }, 400);
      }
    }

    const videoMatch = url.pathname.match(/^\/api\/videos\/([A-Za-z0-9_-]{11})$/);
    if (videoMatch && request.method === "GET") {
      const video = await env.DB.prepare("SELECT video_id, canonical_url, title, channel_name, created_at, updated_at FROM videos WHERE video_id = ?")
        .bind(videoMatch[1]).first();
      if (!video) return json({ error: "not_found" }, 404);
      const transcript = await env.DB.prepare(`SELECT transcript_id, revision, status, source_type, language_code, caption_type, content_text, content_sha256, created_at
        FROM transcripts WHERE video_id = ? ORDER BY revision DESC LIMIT 1`).bind(videoMatch[1]).first();
      return json({ video, transcripts: transcript ? [transcript] : [] });
    }

    return json({ error: "not_found" }, 404);
  },
};
