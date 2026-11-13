# KSK Cloudflare Persistence

Small private API for the YouTube Research Explorer. GitHub remains the code/versioning source; GitHub Pages remains the static frontend; Python/GitHub Actions remain the research/analysis runtime. This Worker is deployed only from this directory.

## First API slice

- `GET /health`: non-sensitive liveness response.
- `POST /api/videos`: create/update a canonical YouTube video and link it to the default project (or supplied project ID).
- `GET /api/videos/{video_id}`: return video metadata and transcript revisions, newest first.
- `POST /api/videos/{video_id}/transcripts`: save a manual transcript. Identical content is idempotent; changed content creates a new revision.

All private routes validate the Cloudflare Access JWT signature, issuer, audience and expiry. CORS is intentionally not enabled yet; the first test uses an API client through Access, before connecting the public Pages frontend. Transcript bodies are limited to 512 KiB. API responses are marked no-store.

## Local development

Requires Node.js 20+ and Wrangler 4.

```sh
cd cloudflare
npm install
npm run db:migrate:local
npm test
npm run dev
```

Wrangler configuration now points to the owner-created development database `ksk-research-dev` (`31c27fa9-cd26-4ac2-867d-710096093dad`). Access settings remain explicit placeholders because the Cloudflare Zero Trust onboarding requested payment details and the owner chose not to provide them. Do not deploy while the Access values are placeholders. Local CI runs the D1 migration against SQLite-backed D1 and exercises the persistence schema; authenticated Worker endpoint success and remote D1 remain unverified.

## Cloudflare setup (owner action)

1. The development D1 database `ksk-research-dev` has already been created and its ID is configured in `wrangler.toml`.
2. Authentication remains the blocker: the current Worker uses Cloudflare Access JWT validation, but no Access application/policy has been created because the account onboarding prompted for card details. Do not ask the owner to enter payment details.
3. Before deployment, choose and implement a secure owner-only authentication route that does not require paid/verified Zero Trust onboarding, or revisit Access only if the owner independently confirms it is available without payment details.
4. Only after authentication is configured and reviewed, apply the remote migration and request explicit deployment approval.

No account token, Access secret, transcript or private note belongs in Git. Access JWT validation happens in the Worker as a second enforcement layer; do not expose the Worker API without an Access application and matching audience configured.

## First manual API experiment

After the development Worker is securely authenticated and deployment is explicitly approved, use an authenticated API client/browser session to:
1. POST one video ID to `/api/videos`.
2. POST a manually copied transcript to `/api/videos/{id}/transcripts`.
3. GET `/api/videos/{id}` and verify revision 1 is present.
4. POST the same transcript again and verify it returns the same revision (no duplicate).
5. POST a corrected transcript and verify revision 2 appears.
6. Repeat a private GET without an Access token and verify HTTP 401.

Do not use a real private transcript in test artifacts. No public Pages UI integration, bulk ingestion, review-decision API or analysis endpoints are included yet.
