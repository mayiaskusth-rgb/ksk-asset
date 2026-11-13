-- KSK YouTube Research persistence schema
-- SQLite / Cloudflare D1.
-- Private user content (transcripts, notes, findings) must never be copied to public fixtures.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS projects (
    project_id TEXT PRIMARY KEY,
    project_key TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'archived')),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS research_runs (
    run_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL REFERENCES projects(project_id),
    topic TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'created' CHECK (status IN ('created', 'running', 'completed', 'failed', 'cancelled')),
    source TEXT NOT NULL DEFAULT 'youtube_search',
    config_json TEXT NOT NULL DEFAULT '{}',
    started_at TEXT,
    completed_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- One canonical record per YouTube video, independent of project or run.
CREATE TABLE IF NOT EXISTS videos (
    video_id TEXT PRIMARY KEY,
    canonical_url TEXT NOT NULL,
    title TEXT,
    channel_name TEXT,
    channel_id TEXT,
    duration_seconds INTEGER CHECK (duration_seconds IS NULL OR duration_seconds >= 0),
    published_at TEXT,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    metadata_source TEXT,
    metadata_retrieved_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- A video may be used by multiple projects without duplicating its transcript.
CREATE TABLE IF NOT EXISTS project_videos (
    project_id TEXT NOT NULL REFERENCES projects(project_id),
    video_id TEXT NOT NULL REFERENCES videos(video_id),
    added_via TEXT NOT NULL DEFAULT 'discovery' CHECK (added_via IN ('discovery', 'manual', 'import')),
    lifecycle_status TEXT NOT NULL DEFAULT 'active' CHECK (lifecycle_status IN ('active', 'archived')),
    review_decision TEXT NOT NULL DEFAULT 'unreviewed' CHECK (review_decision IN ('unreviewed', 'keep', 'drop', 'review_later')),
    review_reason_code TEXT,
    review_note TEXT,
    reviewed_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (project_id, video_id)
);


-- Append-only human review history. Current state remains on project_videos;
-- this table preserves every decision transition and its reason/note.
CREATE TABLE IF NOT EXISTS video_review_events (
    review_event_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    video_id TEXT NOT NULL,
    previous_decision TEXT CHECK (previous_decision IS NULL OR previous_decision IN ('unreviewed', 'keep', 'drop', 'review_later')),
    new_decision TEXT NOT NULL CHECK (new_decision IN ('unreviewed', 'keep', 'drop', 'review_later')),
    reason_code TEXT,
    reviewer_note TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id, video_id) REFERENCES project_videos(project_id, video_id)
);

CREATE INDEX IF NOT EXISTS idx_review_events_membership
    ON video_review_events(project_id, video_id, created_at DESC);

CREATE TABLE IF NOT EXISTS research_run_videos (
    run_id TEXT NOT NULL REFERENCES research_runs(run_id),
    video_id TEXT NOT NULL REFERENCES videos(video_id),
    query_id TEXT NOT NULL DEFAULT '',
    query_text TEXT,
    result_rank INTEGER CHECK (result_rank IS NULL OR result_rank > 0),
    discovered_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (run_id, video_id, query_id)
);

-- Keep transcript revisions so corrections/provider changes are auditable.
CREATE TABLE IF NOT EXISTS transcripts (
    transcript_id TEXT PRIMARY KEY,
    video_id TEXT NOT NULL REFERENCES videos(video_id),
    revision INTEGER NOT NULL CHECK (revision > 0),
    status TEXT NOT NULL CHECK (status IN ('available', 'no_captions', 'blocked', 'failed', 'pending')),
    source_type TEXT NOT NULL CHECK (source_type IN ('manual', 'youtube_captions', 'provider_api', 'other')),
    source_provider TEXT,
    language_code TEXT,
    caption_type TEXT CHECK (caption_type IS NULL OR caption_type IN ('creator', 'automatic', 'generated', 'unknown')),
    content_text TEXT,
    segments_json TEXT,
    content_sha256 TEXT,
    retrieved_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (video_id, revision),
    CHECK ((status = 'available' AND content_text IS NOT NULL) OR status <> 'available')
);

CREATE INDEX IF NOT EXISTS idx_transcripts_video_created ON transcripts(video_id, created_at DESC);

CREATE TABLE IF NOT EXISTS video_notes (
    note_id TEXT PRIMARY KEY,
    video_id TEXT NOT NULL REFERENCES videos(video_id),
    project_id TEXT REFERENCES projects(project_id),
    note_type TEXT NOT NULL DEFAULT 'review' CHECK (note_type IN ('review', 'research_question', 'observation', 'editorial', 'other')),
    content TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS analysis_runs (
    analysis_run_id TEXT PRIMARY KEY,
    video_id TEXT NOT NULL REFERENCES videos(video_id),
    transcript_id TEXT REFERENCES transcripts(transcript_id),
    agent_name TEXT NOT NULL,
    agent_version TEXT NOT NULL,
    rubric_version TEXT,
    status TEXT NOT NULL DEFAULT 'queued' CHECK (status IN ('queued', 'running', 'completed', 'failed')),
    input_sha256 TEXT,
    started_at TEXT,
    completed_at TEXT,
    error_code TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS findings (
    finding_id TEXT PRIMARY KEY,
    analysis_run_id TEXT NOT NULL REFERENCES analysis_runs(analysis_run_id),
    category TEXT NOT NULL,
    finding_json TEXT NOT NULL,
    evidence_json TEXT NOT NULL DEFAULT '[]',
    confidence REAL CHECK (confidence IS NULL OR (confidence >= 0 AND confidence <= 1)),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_project_videos_review ON project_videos(project_id, review_decision, updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_run_videos_video ON research_run_videos(video_id, discovered_at DESC);
CREATE INDEX IF NOT EXISTS idx_analysis_runs_video ON analysis_runs(video_id, created_at DESC);
