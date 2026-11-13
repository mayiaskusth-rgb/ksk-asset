import { env } from "cloudflare:test";
import { describe, expect, it } from "vitest";

const videoId = "d1Persist01";

describe("D1 persistence contract", () => {
  it("persists a canonical video and project membership", async () => {
    await env.DB.prepare(
      "INSERT INTO videos (video_id, canonical_url, title) VALUES (?, ?, ?)",
    ).bind(videoId, `https://www.youtube.com/watch?v=${videoId}`, "D1 persistence test").run();

    await env.DB.prepare(
      "INSERT INTO project_videos (project_id, video_id, added_via) VALUES ('default', ?, 'manual')",
    ).bind(videoId).run();

    const saved = await env.DB.prepare(
      `SELECT v.video_id, v.title, pv.project_id, pv.added_via
       FROM videos v JOIN project_videos pv ON pv.video_id = v.video_id
       WHERE v.video_id = ? AND pv.project_id = 'default'`,
    ).bind(videoId).first<{
      video_id: string;
      title: string;
      project_id: string;
      added_via: string;
    }>();

    expect(saved).toEqual({
      video_id: videoId,
      title: "D1 persistence test",
      project_id: "default",
      added_via: "manual",
    });
  });

  it("retains transcript revisions and prevents duplicate revision numbers", async () => {
    const transcript1 = "First manually pasted transcript.";
    const transcript2 = "Corrected manually pasted transcript.";

    await env.DB.prepare(
      `INSERT INTO transcripts
       (transcript_id, video_id, revision, status, source_type, source_provider, language_code, caption_type, content_text, content_sha256)
       VALUES (?, ?, 1, 'available', 'manual', 'manual_paste', 'en', 'unknown', ?, 'hash-v1')`,
    ).bind("d1-transcript-v1", videoId, transcript1).run();

    await env.DB.prepare(
      `INSERT INTO transcripts
       (transcript_id, video_id, revision, status, source_type, source_provider, language_code, caption_type, content_text, content_sha256)
       VALUES (?, ?, 2, 'available', 'manual', 'manual_paste', 'en', 'unknown', ?, 'hash-v2')`,
    ).bind("d1-transcript-v2", videoId, transcript2).run();

    const revisions = await env.DB.prepare(
      "SELECT revision, content_text FROM transcripts WHERE video_id = ? ORDER BY revision",
    ).bind(videoId).all<{ revision: number; content_text: string }>();

    expect(revisions.results).toEqual([
      { revision: 1, content_text: transcript1 },
      { revision: 2, content_text: transcript2 },
    ]);

    await expect(env.DB.prepare(
      `INSERT INTO transcripts
       (transcript_id, video_id, revision, status, source_type, content_text)
       VALUES ('d1-transcript-duplicate-revision', ?, 2, 'available', 'manual', 'duplicate')`,
    ).bind(videoId).run()).rejects.toThrow();
  });

  it("enforces foreign keys for video-to-project membership", async () => {
    await expect(env.DB.prepare(
      "INSERT INTO project_videos (project_id, video_id, added_via) VALUES ('missing-project', ?, 'manual')",
    ).bind(videoId).run()).rejects.toThrow();
  });

  it("persists append-only review events", async () => {
    await env.DB.prepare(
      "INSERT INTO video_review_events (review_event_id, project_id, video_id, previous_decision, new_decision, reason_code) VALUES (?, 'default', ?, NULL, 'keep', 'test')",
    ).bind("d1-review-event-1", videoId).run();

    const events = await env.DB.prepare(
      "SELECT previous_decision, new_decision, reason_code FROM video_review_events WHERE project_id = 'default' AND video_id = ?",
    ).bind(videoId).all();

    expect(events.results).toHaveLength(1);
    expect(events.results[0]).toMatchObject({
      previous_decision: null,
      new_decision: "keep",
      reason_code: "test",
    });
  });

  it("allocates the next revision when content reverts to an older version", async () => {
    await env.DB.prepare(
      `INSERT INTO transcripts
       (transcript_id, video_id, revision, status, source_type, source_provider, language_code, caption_type, content_text, content_sha256)
       VALUES ('d1-revert-v1', ?, 1, 'available', 'manual', 'manual_paste', 'en', 'unknown', 'original', 'hash-original')`,
    ).bind(videoId).run();
    await env.DB.prepare(
      `INSERT INTO transcripts
       (transcript_id, video_id, revision, status, source_type, source_provider, language_code, caption_type, content_text, content_sha256)
       VALUES ('d1-revert-v2', ?, 2, 'available', 'manual', 'manual_paste', 'en', 'unknown', 'corrected', 'hash-corrected')`,
    ).bind(videoId).run();

    await env.DB.prepare(`INSERT INTO transcripts
      (transcript_id, video_id, revision, status, source_type, source_provider, language_code, caption_type, content_text, content_sha256)
      VALUES ('d1-revert-v3', ?, (SELECT COALESCE(MAX(revision), 0) + 1 FROM transcripts WHERE video_id = ?),
        'available', 'manual', 'manual_paste', 'en', 'unknown', 'original', 'hash-original')`)
      .bind(videoId, videoId).run();

    const revisions = await env.DB.prepare(
      "SELECT revision, content_sha256 FROM transcripts WHERE video_id = ? ORDER BY revision",
    ).bind(videoId).all<{ revision: number; content_sha256: string }>();
    expect(revisions.results).toEqual([
      { revision: 1, content_sha256: "hash-original" },
      { revision: 2, content_sha256: "hash-corrected" },
      { revision: 3, content_sha256: "hash-original" },
    ]);
  });

});
