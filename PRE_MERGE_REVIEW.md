# Pre-Merge Review — Guidelines and Guardrails

**Purpose:** A repeatable, incremental review checklist used by the maintainer/AI agent before every pull-request merge in this repository. This is a human-led review protocol, not an automated test suite. No pytest or local command execution is assumed.

The reviewer must inspect the actual GitHub diff, repository state, documentation and available workflow evidence. A checklist item is not a pass merely because the code looks plausible.

## 1. Review record (complete for every PR)

Record this in the PR description or review summary:

- PR number and link:
- Base branch and head branch:
- Exact head commit SHA reviewed:
- Scope / milestone:
- Files and behavior affected:
- Review date:
- Verdict: **READY TO MERGE / HOLD / NEEDS USER DECISION**
- Known limitations and follow-up work:

Always review the latest head SHA. If new commits arrive after review, re-check the changed files and any affected checklist items before merging.

## 2. Status vocabulary

Use exactly one status for each applicable check:

- **PASS** — directly inspected or verified with evidence.
- **FAIL** — a defect, regression, missing requirement or unsafe condition was found.
- **NOT VERIFIED** — evidence or capability is unavailable. Never silently treat this as PASS.
- **N/A** — genuinely not applicable; give a short reason.

A PR is not ready when a critical item is FAIL or NOT VERIFIED. Explain the reason in plain language. Do not hide uncertainty behind a green-looking summary.

## 3. Mandatory checks — every PR

### A. Scope and incremental delivery
- [ ] The PR has one clear, bounded milestone.
- [ ] The changes are no larger than needed for that milestone.
- [ ] No unrelated refactor, cleanup, deletion or feature has slipped in.
- [ ] The implementation follows the agreed sequence; later-stage work has not been pulled forward.
- [ ] Deferred work and known limitations are explicitly listed.
- [ ] The change can be reviewed as a small, understandable unit.

### B. Repository integrity and architecture
- [ ] Existing folder hierarchy, naming, lifecycle and versioning conventions are preserved.
- [ ] Existing working features and user-facing pages are not unintentionally changed.
- [ ] Repository responsibilities and boundaries remain clear.
- [ ] No duplicate or competing implementation is introduced without a reason.
- [ ] Existing workflows, deployment paths and branch conventions are preserved unless the PR explicitly changes them.
- [ ] No unrelated files or generated artifacts are committed.

### C. Correctness and evidence
- [ ] Every changed behavior is traced from input to output at a high level.
- [ ] Important assumptions, edge cases and failure paths are considered.
- [ ] Any claimed test or validation has actually been run and its result inspected.
- [ ] Workflow success is not confused with application success (for example, a workflow can succeed while a provider returns blocked or empty data).
- [ ] If execution is unavailable, the item is marked NOT VERIFIED and the merge decision reflects the risk.
- [ ] No success, compatibility, security or deployment claim is made without evidence.

### D. Security, privacy and data handling
- [ ] No credentials, tokens, private keys, personal data or secrets are committed.
- [ ] Private content is not written to public logs, fixtures, screenshots, artifacts or documentation.
- [ ] Inputs, outputs, permissions and trust boundaries are considered for changed interfaces.
- [ ] Authentication is not replaced by CORS, obscurity or client-side checks.
- [ ] Destructive, irreversible or externally visible actions are guarded and documented.
- [ ] New dependencies, external services and data transfers are justified.

### E. Maintainability and documentation
- [ ] Names, module boundaries and error handling are understandable.
- [ ] Documentation reflects what is implemented now, not a future intention.
- [ ] README and relevant module docs are updated when behavior, setup, architecture or workflow changes.
- [ ] The engineering handoff/status document is updated for material milestones.
- [ ] Setup instructions do not assume the user can run local commands unless an alternative is provided.
- [ ] No stale instructions or contradictory status statements remain.

### F. Regression and release safety
- [ ] Existing GitHub Pages behavior and deployment workflow are preserved unless explicitly in scope.
- [ ] Changed workflows/configuration have been inspected for unintended triggers or permissions.
- [ ] Rollback/recovery implications are understood for schema, data and deployment changes.
- [ ] The PR is based on the intended target branch and has no unexplained divergence.
- [ ] The final diff and changed-file list have been inspected, not just the PR description.

## 4. Change-specific checks

Only apply relevant sections. Mark others N/A with a reason.

### Python / data pipeline / research modules
- [ ] Inputs and outputs have clear contracts and stable formats.
- [ ] Empty, malformed, duplicate and partial results are handled.
- [ ] Network/provider errors, rate limits, blocks and timeouts are represented honestly.
- [ ] Retries, concurrency and request volume are bounded.
- [ ] No media/content is downloaded or stored unless explicitly in scope.
- [ ] Provenance is retained so results can be traced to source, query and run.
- [ ] Small-sample validation precedes wider/bulk execution.

### Frontend / GitHub Pages
- [ ] Existing routes, pages and asset gallery remain intact.
- [ ] Static hosting assumptions are respected; no server-side behavior is assumed on Pages.
- [ ] Mobile layout and basic navigation are considered.
- [ ] Loading, empty, error and unavailable states are represented.
- [ ] No private API data is exposed in browser bundles or public artifacts.
- [ ] Any API integration uses the intended authenticated boundary.

### Database / schema / persistence
- [ ] Schema is reviewed for primary keys, foreign keys, uniqueness, nullability and indexes.
- [ ] The schema has actually been executed against the target-compatible engine/version, or is clearly NOT VERIFIED.
- [ ] Foreign-key enforcement is checked, not assumed.
- [ ] Create/read/update/delete behavior and invalid references are considered.
- [ ] Transactions/atomicity are checked for multi-step state changes.
- [ ] Revision/history semantics are explicit; old records are not silently overwritten where history is required.
- [ ] Duplicate, retry and idempotency behavior is understood.
- [ ] Data size limits, validation and retention/deletion behavior are documented.
- [ ] Migration and rollback implications are documented.
- [ ] Development/test data is separated from production data.

### API / authentication / Cloudflare
- [ ] Request and response contracts are documented.
- [ ] Authentication and authorization are enforced server-side for every private endpoint.
- [ ] Unauthorized and unauthenticated requests are tested or marked NOT VERIFIED.
- [ ] CORS is treated only as a browser access policy, never as authentication.
- [ ] Payload size, field validation, rate limits and error responses are defined.
- [ ] Secrets are configured outside source control.
- [ ] Worker deployment is isolated from the static GitHub Pages deployment.
- [ ] Access/session behavior is verified in the intended browser/device before frontend integration.
- [ ] No production resource or secret is created without explicit owner authorization.

### Workflow / CI / automation
- [ ] Trigger conditions and permissions are least-privilege.
- [ ] Secrets are not printed or exposed in logs.
- [ ] Failures are visible and do not produce misleading success artifacts.
- [ ] Workflow artifacts contain only intended, safe data.
- [ ] Cost, runtime, concurrency and external-service usage are bounded.

## 5. Incremental validation ladder

Do not jump directly from a design to a full rollout. Use the smallest meaningful proof for the current milestone:

1. **Inspect:** read the diff, surrounding code, docs and workflow configuration.
2. **Static reasoning:** trace contracts, state transitions, permissions and failure cases.
3. **Smallest executable check:** when available, run only the narrow validation for this milestone (for example, schema execution or one parser fixture).
4. **Single-item end-to-end check:** use one representative record/video/request and verify the stored/retrieved result.
5. **Negative check:** verify at least one invalid, unauthorized, blocked or failure path where relevant.
6. **Revision/regression check:** verify updates preserve required history and existing behavior.
7. **Expand gradually:** only after the small case passes, increase sample size or enable the next component.

If a step cannot be run in the available environment, record NOT VERIFIED, explain what evidence is missing, and do not imply that a later step has passed.

## 6. Merge decision rules

### READY TO MERGE
Use only when:
- All mandatory checks are PASS or justified N/A.
- All relevant change-specific critical checks are PASS.
- No unresolved high-impact risk remains.
- The exact reviewed head SHA matches the current PR head.
- Documentation and handoff are accurate.

### HOLD
Use when:
- Any critical check is FAIL or NOT VERIFIED.
- Security/privacy, data loss, backwards compatibility or deployment boundaries are uncertain.
- A required small-sample or negative-path validation has not been completed.
- The diff is too broad or contains unexplained changes.

### NEEDS USER DECISION
Use when:
- A product/architecture trade-off cannot be resolved from agreed project principles.
- A paid provider, external service, production resource, secret, irreversible operation or deployment requires owner authorization.
- The change alters an agreed scope or behavior.

Do not merge a HOLD item to maintain momentum. Split the work, add evidence, or explicitly ask for the decision needed.

## 7. Project-specific permanent guardrails

- Work in small increments: one or two representative items first, review and improve, then a few more, and only later bulk processing.
- GitHub is the source of truth for code, reviews and version history.
- GitHub Pages remains the static frontend and asset gallery; do not turn the repository root into a server deployment.
- The YouTube Intelligence Engine remains an independent research-engineering product. It is not an automatically running KSK editorial agent.
- The private KSK editorial/production system and public research-engineering repository retain separate responsibilities.
- Private transcripts, notes and other private research content must never be committed to this public repository.
- A provider returning blocked, empty or partial data is a valid recorded outcome, not a successful data acquisition.
- Never run bulk discovery, transcript extraction or expensive provider calls before the agreed small-sample review.
- Never create Cloudflare resources, deploy Workers, configure paid services or add secrets without explicit authorization.
- Preserve review history and reversible decisions; do not silently erase prior Keep / Drop / Review later decisions.
- Keep README and `youtube-intelligence/HANDOFF.md` aligned with actual implementation and validation status.

## 8. Required final review summary

Before every merge, provide the user a short summary in plain language:

1. **What changed:** one or two sentences.
2. **What I checked:** the important checks and evidence.
3. **What I could not verify:** list explicitly; say “None” only when true.
4. **Risks / follow-ups:** only material items.
5. **Verdict:** READY TO MERGE, HOLD, or NEEDS USER DECISION.
6. **Exact commit reviewed:** short SHA.

The user should not need to run commands or interpret test output to understand the decision. If a check requires account access or a real device that is unavailable to the agent, say so plainly and ask only for the specific action or authorization needed.

## 9. Checklist discipline

- Use this document before every merge, including documentation-only changes.
- Re-evaluate relevant items when new commits arrive; previous approval does not automatically cover a new head SHA.
- Do not weaken or delete a guardrail merely because it blocks a merge. Change this policy only through a separately reviewed, documented decision.
- Keep the review proportional: do not invent unnecessary tests for a tiny change, but never skip a relevant risk because the PR is small.
