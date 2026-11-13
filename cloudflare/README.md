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

Wrangler configuration has a harmless placeholder D1 UUID and placeholder Access settings. Replace them only after creating the development D1 database and Access application. Do not deploy with placeholder settings. The local tests cover liveness, rejection of unauthenticated private requests and migration seeding. The authenticated save/retrieve/revision flow is the first development-D1 integration check after account setup.

## Cloudflare setup (owner action)

1. Create a D1 database named `ksk-research-dev`.
2. Replace the database ID in `wrangler.toml`.
3. Create a Cloudflare Access self-hosted application for the Worker hostname; restrict it to the owner's email.
4. Set `ACCESS_TEAM_DOMAIN` and `ACCESS_AUD` from the Access setup.
5. Apply the migration to the development database and deploy from this directory only.

No account token, Access secret, transcript or private note belongs in Git. Access JWT validation happens in the Worker as a second enforcement layer; do not expose the Worker API without an Access application and matching audience configured.

## First manual API experiment

After the development Worker is deployed behind Access, use an authenticated API client/browser session to:
1. POST one video ID to `/api/videos`.
2. POST a manually copied transcript to `/api/videos/{id}/transcripts`.
3. GET `/api/videos/{id}` and verify revision 1 is present.
4. POST the same transcript again and verify it returns the same revision (no duplicate).
5. POST a corrected transcript and verify revision 2 appears.
6. Repeat a private GET without an Access token and verify HTTP 401.

Do not use a real private transcript in test artifacts. No public Pages UI integration, bulk ingestion, review-decision API or analysis endpoints are included yet.
