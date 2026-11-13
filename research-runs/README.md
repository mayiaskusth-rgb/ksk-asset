# KSK Research Runs

This area stores **curated, public-safe outputs** from repeatable research workflows such as YouTube Outlier Intelligence.

It is separate from the visual asset gallery:
- `assets.json` remains the curated visual-asset index used by the gallery.
- `research-runs/` stores research run summaries and selected evidence references.
- The private `kabhi-socha-kya` repository remains the source of truth for pipeline code, prompts, configuration, internal notes and restricted working data.

## Publication boundary

This repository is public. Never publish:
- API keys, credentials or personal data.
- Private or licensed transcripts unless redistribution is explicitly permitted.
- Bulk comments, user identifiers or other personal information.
- Downloaded video/audio binaries or copyrighted thumbnails.
- Internal deliberations, unreviewed claims or confidential notes.

A public report may include video URLs, public metadata snapshots, concise original analysis, timestamp references and source citations where permitted. Check provider terms and rights before publishing any derived material.

## Run layout

```text
research-runs/
  README.md
  index.json
  YTI-YYYY-NNN/
    report.md
    run_summary.json
    outlier_table.csv
    evidence/
      source_links.json
```

Only create a run folder after its outputs have been reviewed for public release. Raw collection data and full transcripts should remain in an appropriately private store, not this public repository.

## Run index

`index.json` is a lightweight index of published runs. Add an entry only after the report and its public-safe artifacts have been committed.
