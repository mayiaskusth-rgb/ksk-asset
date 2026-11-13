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
- Private routes validate Cloudflare Access JWT signature, issuer, audience and expiry. Missing/invalid configuration fails closed.
- CORS currently allows the GitHub Pages origin `https://mayiaskusth-rgb.github.io` and credentialed browser requests. CORS is not authentication and does not permit unauthenticated API access.

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

Cloudflare Access onboarding previously requested payment details. The owner declined to provide card details. No Access application/policy exists and the Access team/audience values remain placeholders. Do not ask for card details, do not ask for tokens/passwords in chat, do not deploy while authentication is unresolved, and do not expose an unauthenticated public API.

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

After CI passes and a secure Access/browser architecture is established:

1. Confirm Access can protect the Worker and support browser requests from the GitHub Pages origin without weakening GET/POST authorization.
2. Test preflight handling and third-party cookie behavior on Android. If cross-site Access cookies do not work, prefer a same-origin/custom-domain architecture; do not store long-lived credentials in public JavaScript or localStorage.
3. Obtain explicit approval before applying the remote D1 migration or deploying the Worker.
4. Open an existing shortlisted video, paste its YouTube transcript, save it, and retrieve it.
5. Verify identical text does not create a duplicate revision and edited text creates the next revision.
6. Verify unauthenticated reads and writes are rejected.

Do not add bulk imports, automated transcript-provider fallback, analysis endpoints, or any public unauthenticated write path in this first persistence slice.
