# KSK Cloudflare Persistence

This directory defines the backend foundation for the YouTube Research Explorer. It is deliberately separate from the existing GitHub Pages frontend and from the Python research engine.

## Responsibilities

- **GitHub** remains the source of truth for code, reviews, versioning, tests and deployment configuration.
- **GitHub Pages** continues to host the existing static Research Explorer and asset gallery.
- **Cloudflare Workers** will expose a small authenticated API.
- **Cloudflare D1** will persist projects, research runs, canonical video records, review decisions, transcripts, notes and analysis results.
- **Python / GitHub Actions** will fetch saved transcript content through the API when analysis runs, then write structured findings back.

Cloudflare is a runtime and persistence layer, not a replacement for GitHub repositories.

## Safety boundary

Do not connect the existing repository root to a generic Worker deployment. The current repository contains the public static website and its Pages workflow. The Worker must be deployed from this dedicated directory with its own Wrangler configuration and entry point.

Never put API secrets, Cloudflare account tokens, Access service tokens, private transcripts or user notes in this public repository.

The API must be protected before any write or private read endpoint is exposed. Preferred initial browser access is Cloudflare Access in front of a dedicated API hostname, with Worker-side authorization checks. The browser must use the Access-supported login/session flow for cross-origin API calls; verify cookie and CORS behaviour in a real mobile-browser test before integrating the public Pages UI. CORS is not authentication. Do not rely on an unguessable URL or a secret embedded in frontend JavaScript. The first deployment is single-user/private; do not assume the schema is ready for multiple independent users or tenants.

## Data model

The first schema is in [schema.sql](schema.sql). It is designed for the intended lifecycle, but the first implementation/test will use only a narrow subset:

1. Create or retrieve one canonical video record by YouTube video ID.
2. Save a manually pasted transcript with source and language metadata.
3. Retrieve that transcript from a separate client.
4. Update the transcript without duplicating the canonical video.
5. Confirm that unauthorized requests are rejected.

The schema also reserves structures for multiple projects, research runs, discovery provenance, Keep / Drop / Review decisions, human notes, analysis runs and evidence-backed findings. Those features are not part of the first persistence test.

## Video lifecycle decisions

A review decision is not deletion. 'keep', 'drop' and 'review_later' are reversible states. Dropped videos remain available for audit and can be restored. The reason and reviewer note are stored separately from machine-generated analysis.

Manual additions use added_via = 'manual' and enter the same video lifecycle as discovered results.

A canonical video is keyed by YouTube video ID. Project membership and research-run appearances are separate relationships, so the same video can appear in multiple projects or runs without duplicating its transcript.

## Transcript handling

- Transcript text is private application data and must remain in D1 or another private storage service.
- Do not commit transcripts, transcript excerpts, personal notes or analysis output containing private material to this public repository.
- Preserve language, caption type, source method, retrieval time, content checksum and status.
- Manual paste is a supported source; automated providers can be added later behind the same transcript contract.
- Keep transcript revisions rather than silently overwriting the only copy.

## Environments and deployment

Use separate development and production Worker environments and separate D1 databases. Do not point test workflows at production data.

The Worker will be deployed from cloudflare/ using a dedicated Wrangler configuration. The GitHub integration must be configured to use this directory as its project root, not the repository root. Deployment configuration will be added only after the Worker implementation and tests are ready.

Initial account setup, D1 creation, Access policy setup and secret configuration require the account owner's explicit actions in Cloudflare. No account token or credential should be pasted into chat or committed.

## First milestone acceptance criteria

- [ ] Worker code and API contract reviewed.
- [ ] D1 database created for development.
- [ ] Access protection configured and verified.
- [ ] One video can be saved and retrieved.
- [ ] A manually pasted transcript can be saved and retrieved by video ID.
- [ ] Duplicate saves update/create transcript revisions without duplicating the video.
- [ ] Unauthorized read/write requests fail.
- [ ] Automated tests pass.
- [ ] No production deployment or migration until development test passes.

## Current status

Architecture and schema proposal only. No Cloudflare resources have been created, no Worker has been deployed, and no live database exists yet.
