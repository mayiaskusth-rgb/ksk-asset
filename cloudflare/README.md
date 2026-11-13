# KSK Cloudflare Persistence

Private persistence API for the independent YouTube Audience Intelligence Engine. It is a separate backend layer; it does not replace GitHub, the existing GitHub Pages site, or the Python research runtime.

## System boundaries

- **GitHub:** source code, version history, pull requests and CI.
- **GitHub Pages:** existing static Asset Gallery and Research Run Explorer.
- **Research Explorer:** existing shortlist UI; the Transcript tab now accepts manually pasted transcript text for the selected video and requests save/retrieval through the Worker.
- **Cloudflare Worker:** private API only.
- **Cloudflare D1:** private structured persistence.
- **Python / GitHub Actions:** research and analysis execution.

The YouTube Intelligence Engine is independent from the private KSK editorial workflow. No automated integration is implied.

## API contract

- `GET /health`: non-sensitive liveness response.
- `POST /api/videos`: upsert a canonical YouTube video and associate it with a project (default project when omitted).
- `GET /api/videos/{video_id}`: return video metadata and transcript revisions, newest first.
- `POST /api/videos/{video_id}/transcripts`: save manually pasted transcript text.
- Identical content compared with the latest revision is idempotent; changed content creates a new revision. Reverting to older content creates a new revision rather than rewriting history.
- Transcript request body limit: 512 KiB. Responses are marked `no-store`.
- Private routes require an owner password exchanged for a 20-minute HMAC-signed bearer session. The password and signing key are Cloudflare Worker secrets; the browser keeps the short-lived token in memory only. Missing/invalid configuration fails closed.
- CORS allows only the GitHub Pages origin `https://mayiaskusth-rgb.github.io`, with the Authorization header. CORS is not authentication and does not permit unauthenticated API access.

## Current repository status — 2026-11-14

- PR [#17](https://github.com/mayiaskusth-rgb/ksk-asset/pull/17) was merged to main as commit `f755d4da8e7c24bfa4c1bd6f4d89f62cda1939df`. It contains authenticated Worker integration tests, the existing-shortlist transcript UI, CORS handling, and documentation updates.
- The UI uses the selected shortlist record's existing YouTube ID/title/channel. It offers a Worker API URL field, transcript textarea, language code, save action and revision retrieval. The Worker URL is stored in browser localStorage; transcript content is sent to Cloudflare, not committed to GitHub.
- Python CI passed for the updated explorer/test contract on head `60e3fdc7600df823be5ea87294f8b9d460fd1256` (run [43509321262](https://github.com/mayiaskusth-rgb/ksk-asset/actions/runs/43509321262)). The Explorer test was updated to expect the new transcript controls.
- Cloudflare API CI passed on final PR head `5df01cf74072209bf6772d58fbeda7e5a5ea018b` (run [43509893658](https://github.com/mayiaskusth-rgb/ksk-asset/actions/runs/43509893658)). The authenticated test invokes the Worker handler directly, simulates the edge-injected Access assertion, and stubs the JWKS fetch; production authentication code is unchanged.
- Python CI passed on the same PR head (run [43509893760](https://github.com/mayiaskusth-rgb/ksk-asset/actions/runs/43509893760)).
- PR #17 is merged. Main-branch Cloudflare API checks, Python tests and GitHub Pages deployment all passed for merge commit `f755d4da8e7c24bfa4c1bd6f4d89f62cda1939df` (runs [43509948988](https://github.com/mayiaskusth-rgb/ksk-asset/actions/runs/43509948988), [43509949086](https://github.com/mayiaskusth-rgb/ksk-asset/actions/runs/43509949086), and [43509949087](https://github.com/mayiaskusth-rgb/ksk-asset/actions/runs/43509949087)).
- Earlier PRs #14 and #16 were consolidated into the branch/PR #17 development line; use the live PR state rather than old handoff entries when checking merge status.

## Cloudflare account and authentication constraints

The owner-created development D1 database is:

- Name: `ksk-research-dev`
- Database ID: `31c27fa9-cd26-4ac2-867d-710096093dad`

The ID is an identifier, not a credential. It is configured in `wrangler.toml`.

Cloudflare Access onboarding previously requested payment details. The owner declined to provide card details. No Access application/policy is needed for the owner-password design. Do not ask for card details, do not ask for tokens/passwords in chat, and do not expose an unauthenticated public API. Before enabling public use, configure edge rate limiting for `POST /api/auth/login` and set strong random Worker secrets.

## Local development and tests

Requires Node.js 20+ and Wrangler 4. The owner currently uses an Android phone and should not be asked to run local shell commands.

```sh
cd cloudflare
npm install
npm run db:migrate:local
npm test
npm run dev
```

The authenticated Worker integration suite is under active CI verification. Always inspect the latest run on the exact PR head; a passing Python run or older Cloudflare run is not proof that the current API tests pass.

## Deployment and first live test — NOT YET DONE

No remote migration, Worker deployment, authenticated live endpoint test, Android browser test, or transcript upload to D1 has happened. The existence of the D1 database does not prove its schema has been applied.

After CI passes and the Worker is deployed with owner-password authentication:

1. Configure Worker secrets `OWNER_PASSWORD` and `SESSION_SECRET` in Cloudflare; never put either in GitHub or browser storage. Use a long unique password and a random signing secret of at least 32 characters.
2. Configure rate limiting for login attempts at the Cloudflare edge before sharing the endpoint.
3. Obtain explicit approval before applying the remote D1 migration or deploying the Worker.
4. Open an existing shortlisted video, paste its YouTube transcript, save it, and retrieve it.
5. Verify identical text does not create a duplicate revision and edited text creates the next revision.
6. Verify unauthenticated reads and writes are rejected.

Do not add bulk imports, automated transcript-provider fallback, analysis endpoints, or any public unauthenticated write path in this first persistence slice.


## Owner-password authentication update — 2026-11-14

PR [#18](https://github.com/mayiaskusth-rgb/ksk-asset/pull/18) implements an owner-only password exchange for 20-minute HMAC-signed sessions. It replaces the Access JWT dependency and updates the Research Explorer to prompt for the password while retaining the session token in memory only. Required production runtime secrets are `OWNER_PASSWORD` and `SESSION_SECRET` (minimum 32 characters). Configure them as encrypted Worker secrets after deployment; do not add them to `wrangler.toml`, GitHub, or browser storage. Configure edge rate limiting for `POST /api/auth/login` before using the endpoint.

PR #18 is open and CI is pending on its latest head. The Worker is still not deployed; remote D1 migration and live save/retrieve remain unperformed. In Cloudflare Workers Builds, the project/Worker name must be `ksk-research-api` to match Wrangler, and the repository root directory must be `cloudflare`. Keep Cloudflare Access off. The auto-created Workers Builds API token is separate from the runtime Worker secrets.


## Login rate limiting — 2026-11-14

- `POST /api/auth/login` uses the Cloudflare Workers Rate Limiting binding, keyed by the edge-provided client IP, with a threshold of 5 attempts per 60 seconds per Cloudflare location.
- This is an approximate, location-local control; it is not a strict global limit and can be exceeded briefly while counters synchronize. It adds friction to repeated password guessing but does not replace strong unique secrets or monitoring.
- The binding is configured in `wrangler.toml` as `LOGIN_RATE_LIMITER`. Tests cover repeated failed attempts and a blocked subsequent login.
- This change must pass CI and be deployed before the protection is live. Do not treat the currently deployed Worker as rate-limited until then.
