# KSK Cloudflare Persistence

Private persistence API for the independent YouTube Audience Intelligence Engine. It is a separate backend layer; it does not replace GitHub, the GitHub Pages site, or the Python research runtime.

## System boundaries

- **GitHub:** source code, version history, pull requests and CI.
- **GitHub Pages:** static Asset Gallery and Research Run Explorer.
- **Research Explorer:** selected-video Transcript tab for manually pasted transcript input and retrieval.
- **Cloudflare Worker:** authenticated API and request validation.
- **Cloudflare D1:** private structured persistence for video metadata and transcript text.
- **Python / GitHub Actions:** research and analysis execution.

The YouTube Intelligence Engine is independent from the private KSK editorial workflow. It is not a KSK agent and there is no automated runtime integration.

## Runtime resources

- Worker: `ksk-research-api`
- Worker URL: https://ksk-research-api.mayiaskusth.workers.dev
- Worker source/configuration: `cloudflare/src/index.ts`, `cloudflare/wrangler.toml`
- D1 database: `ksk-research-dev`
- D1 database ID: `31c27fa9-cd26-4ac2-867d-710096093dad`
- D1 migrations: `cloudflare/migrations/`
- Manually gated remote migration workflow: `.github/workflows/d1-migrate-remote.yml`

The remote migration workflow was run by the user. The D1 migration ledger showed `0001_initial.sql` applied, and the application tables were visible in the remote database.

## API and authentication

- `GET /health`: minimal public liveness response.
- `POST /api/auth/login`: validates `OWNER_PASSWORD` and returns a short-lived signed session.
- Private video/transcript API routes require a valid bearer session.
- Session lifetime: 20 minutes; HMAC-SHA256 signature uses `SESSION_SECRET`.
- Runtime secrets `OWNER_PASSWORD` and `SESSION_SECRET` are configured as Cloudflare Worker secrets. Never put their values in Wrangler config, GitHub, the browser, README files, or chat.
- The Explorer stores the session token in tab-scoped `sessionStorage`; it does not persist the owner password.
- Login rate limiting uses a Cloudflare Workers Rate Limiting binding: 5 attempts per 60 seconds per client IP per Cloudflare location. This is approximate/eventually consistent and location-local, not a strict global limit.
- CORS allows only `https://mayiaskusth-rgb.github.io` and the required Authorization header. CORS is not authentication.
- `workers.dev` is currently enabled and reachable. Do not describe it as disabled.

## Transcript editor behaviour

The live Explorer is https://mayiaskusth-rgb.github.io/ksk-asset/research.html.

- The Worker URL is built into the page; the user does not configure it in the UI.
- The Transcript tab uses the selected shortlist video's existing YouTube ID/title/channel.
- Opening the tab retrieves the latest transcript.
- First save creates the transcript record; identical content is idempotent.
- Editing and saving updates the latest transcript row in place. The current editor does not create new revision history.
- Older historical rows, if any, are not deleted by this behaviour. The current retrieval path returns the latest transcript.
- UI reports saving, unchanged, saved, updated, and failure states.
- Transcript text is sent to Cloudflare D1 and is not committed to this public repository.

## Verified status — 2026-11-14

- PR #17: initial transcript persistence and UI — merged.
- PR #18: owner-password authentication — merged.
- PR #19: login rate limiting — merged.
- PR #20: manually gated remote D1 migration workflow — merged and run; remote migration/table state checked by the user.
- PR #21: simplified editor and update-in-place save flow — merged as `ac94ad0cdf0ebab3a753643e03418084fdfa44e2`.
- Worker dashboard showed deployment Ready; the public health route returned `{"ok":true,"service":"ksk-research-api"}`.
- User confirmed live end-to-end transcript save, page refresh, and retrieval.

This is a verified basic round trip, not a claim of production-scale reliability or exhaustive security testing.

## Local development and tests

Requires Node.js 20+ and Wrangler 4. The owner currently uses Android and should not be asked to run local shell commands.

```sh
cd cloudflare
npm install
npm run db:migrate:local
npm test
npm run dev
```

## Security and operating constraints

- Never add an unauthenticated private read/write route.
- Never commit Worker secrets, passwords, API tokens, cookies, private transcripts, or personal data.
- Do not request credentials or payment/card details in chat.
- Do not run a remote migration or change deployment/security settings without explicit user approval.
- Keep the supported transcript input path manual copy/paste. Do not repeat automated transcript extraction attempts from GitHub-hosted runners; previous attempts were blocked by YouTube access challenges.
- Preserve auditability and provenance. Do not silently change transcript persistence semantics or delete existing records.
