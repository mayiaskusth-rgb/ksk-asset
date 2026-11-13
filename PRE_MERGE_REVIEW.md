# Pre-merge sanity check

This is a quick second look to catch avoidable mistakes while we experiment. It is not a release process or a reason to slow down.

Before merging, I will:
- Read the actual diff and check that it only changes what we intended.
- Look for obvious breakage, data-loss risks, exposed secrets/private data, and accidental changes to the existing Pages site or workflows.
- Check that the README/handoff still describe reality.
- Run the smallest useful check I can. If I cannot run it, I will say so plainly.
- Keep the experiment small: one or two real examples before expanding.

If I spot a worthwhile fix, I will make it on the PR branch and review the updated diff. I will not add process, tests, abstractions or documentation just for completeness.

For risky changes, I will preserve the current `main` commit before merging so we have a clear recovery point. GitHub also supports reverting a merge commit; a backup branch is an extra safety net, not a substitute for a good review.

The user should get only a short summary: what I checked, anything I could not verify, and whether I recommend merging. No routine status reports or formal checklist ceremony.
