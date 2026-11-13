# KSK Cloudflare Persistence

Private persistence API for the independent YouTube Audience Intelligence Engine. This is a separate backend layer; it does not replace GitHub, the existing GitHub Pages site, or the Python research runtime.

## System boundaries

- **GitHub:** source code, version history, pull requests and CI.
- **GitHub Pages:** existing static Asset Gallery and Research Run Explorer. Keep the current Pages deployment intact.
- **Cloudflare Worker:** proposed private API only; deployed from this directory, never from the repository root.
- **Cloudflare D1:** private structured persistence.
- **Python / GitHub Actions:** research and analysis execution.

The YouTube Intelligence Engine is not a KSK editorial agent. The private kabhi-socha-kya repository remains the source of truth for KSK's editorial and production workflow. No automated integration is implemented.

## First API slice in draft PR #14

- `GET /health`: non-sensitive liveness response.
- `POST /api/videos`: create/update a canonical YouTube video and associate it with a project (default project when omitted).
- `GET /api/videos/{video_id}`: return video metadata and transcript revisions, newest first.
- `POST /api/videos/{video_id}/transcripts`: save a manually supplied transcript.
- Identical content compared with the latest revision is idempotent; changed content creates a new revision. Reverting to an earlier transcript creates a new revision rather than rewriting history.
- Transcript request body limit: 512 KiB. Responses are marked `no-store`.
- Private routes currently validate Cloudflare Access JWT signature, issuer, audience and expiry. CORS and public Pages integration are intentionally not implemented.

## Current repository status — 2026-11-14

- Draft PR [#14](https://github.com/mayiaskusth-rgb/ksk-asset/pull/14), branch `feat/cloudflare-first-persistence-api`, contains the Worker API and initial migration. Its Cloudflare API CI and Python CI passed on head `091d47b76272129e71f5e1ff4080641ec0844fe4`.
- Draft PR [#16](https://github.com/mayiaskusth-rgb/ksk-asset/pull/16), branch `test/local-d1-persistence-contract`, adds local SQLite-backed D1 contract tests. A test-harness fix was committed through `c5afaf634a26f028896e959eabd5701e4f063af0`, but no CI run for that exact head was visible at the last status check. The earlier failed run was for the older head `2b3d926514bf5a73e80561093f564170a8ae48a5`; do not treat it as a result for the fix.
- Both PRs remain open drafts and are not merged. Do not merge, deploy, or apply remote migrations without explicit owner approval.

## Cloudflare account and authentication constraints

The owner has already created the development D1 database:

- Name: `ksk-research-dev`
- Database ID: `31c27fa9-cd26-4ac2-867d-710096093dad`

The ID is an identifier, not a credential. It is configured in `wrangler.toml`.

Cloudflare Access onboarding requested payment details. The owner declined to provide card details. No Access application/policy exists, and the Access team/audience values remain placeholders. **Do not ask the owner to enter card details. Do not deploy while authentication is unresolved. Do not expose an unauthenticated public API.**

The next engineering task is to choose and implement a secure owner-only authentication method that works within the account constraints, fails closed when not configured, and keeps secrets out of Git and chat. Add authenticated endpoint tests before deployment. Do not assume a particular Cloudflare dashboard capability or paid-plan entitlement without verifying it.

## Local development and tests

Requires Node.js 20+ and Wrangler 4. The owner currently has only an Android phone and should not be asked to run local shell commands.

```sh
cd cloudflare
npm install
npm run db:migrate:local
npm test
npm run dev
```

The Vitest/Workers D1 test harness is under active repair in PR #16. Verify CI on the latest PR head before treating the persistence contract tests as passing. The PR #14 API CI pass alone does not prove the D1 contract suite or authenticated API flow.

## Deployment and first live test — NOT YET DONE

No remote migration, Worker deployment, authenticated endpoint test, mobile browser test, or Pages integration has happened. The existence of the D1 database does not prove that its schema has been applied.

After authentication is implemented and tested:

1. Prepare exact phone-friendly Cloudflare dashboard steps for the owner; do not ask for local CLI commands.
2. Obtain explicit approval before applying the remote D1 migration or deploying.
3. Save one canonical video and a manually pasted transcript.
4. Retrieve it and verify revision 1.
5. Save identical text and verify no duplicate revision is created.
6. Save corrected text and verify revision 2.
7. Verify an unauthenticated request is rejected.
8. Only after this bounded test succeeds should mobile UI integration be considered.

Do not add bulk imports, automated transcript-provider fallback, analysis endpoints, or UI integration in this first persistence slice. Do not put transcript text, credentials, tokens, or private notes in this public repository or CI artifacts.
