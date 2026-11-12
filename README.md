# KSK Asset Gallery

A public, static gallery for selected visual-asset references used in Kabhi Socha Kya (KSK).

- `index.html` renders the gallery.
- `assets.json` is a curated, publishable display index.
- Preview media remains hosted by original providers; this repository does not redistribute downloaded media.
- The authoritative asset registry and detailed internal workflow remain in the private KSK repository.

## Local preview

```bash
python -m http.server 8000
```

Open http://localhost:8000/.

## GitHub Pages

This repository includes a GitHub Actions deployment workflow at `.github/workflows/pages.yml`. In Settings → Pages, choose **GitHub Actions** as the deployment source if prompted.

Expected site URL: https://mayiaskusth-rgb.github.io/ksk-asset/

## Publishing policy

Only publish records intentionally selected for public display. Check that metadata contains no private notes, internal paths, credentials, or confidential workflow details. A gallery card is not rights clearance: assess each asset for intended use and distribution territory.

Original asset and rights pages are linked on every card. Remote previews may fail if a source blocks hotlinking; source links remain available.
