# Nikhil Keetha’s website

A lightweight, accessible academic website at **https://nik-v9.github.io/**.
HTML and CSS follow the compact academic layout of Alexander Sax and Jon Barron;
the site uses orange accents, seven accessible tabs, and visibility-aware research videos.

## Build and preview

Requires Python 3.10 or newer. The build has no third-party dependencies and makes no network requests.

```sh
python3 scripts/build.py
python3 scripts/check.py
python3 -m http.server 8000 --bind 127.0.0.1 --directory _site
```

Open http://127.0.0.1:8000/. Never edit `_site`: it is generated and ignored by Git.

## Update content

- `content/profile.json`: biography, contact links, and metadata.
- `content/research.json`: selected research, full author lists, links, descriptions, release dates, highlights, and media.
- `content/activities.json`: awards, press, talks, service, outreach, and collaborations.
- `content/legacy.json`: archived news and old redirect destinations.
- `content/media-sources.json`: provenance for the media used here.
- `content/legacy-publications.bib`: preserved bibliography for the later CV update; not published in the generated site.
- `templates/page.html`, `assets/site/style.css`, and `assets/site/site.js`: page shell, visual design, and progressive enhancement.

Research sorts by `release_date` (first public release), independent of the current venue.
The `highlighted` flag changes styling, never order. `equal_contribution` lists the exact author names to mark.
When intentionally changing the selected research set, update its selection checks in `scripts/check.py`.
The two demo entries use team attribution instead of a fabricated publication author list.

Keep the CV at `assets/pdf/Nikhil_CV.pdf` so existing download links keep working. It remains the previous CV until the separate CV update.

Videos are local H.264 MP4 files with static WebP posters. They load only on entering the viewport and pause offscreen,
in inactive tabs, and when the document is hidden. Reduced-motion and data-saving preferences default to posters.
All content remains available without JavaScript, and printing includes every section.

## Deployment

The workflow builds and checks pull requests. A push to `master` or `main` publishes the exact built artifact to the
existing `gh-pages` branch. Manual runs on another branch only build and validate; they do not deploy.
GitHub Pages should continue serving the root of `gh-pages`.

The redesign lives on `website-refresh-2026` for review. The prior site is retained in `origin/archive_oct_2024`.
Merge or cherry-pick the approved redesign into the production branch to publish. Reverting that merge restores the previous workflow and site.

## Validation

`scripts/check.py` verifies the research selection, chronology, seven sections, local links and fragments,
legacy routes, image descriptions, required assets, and approved footer wording. Browser checks for responsive layout,
keyboard navigation, history, media behavior, and no-JavaScript operation are described in `docs/validation.md`.

Existing production analytics uses `G-G7H9CMFQ8S`; localhost does not send analytics.
Lato’s license is included in `assets/fonts/OFL.txt`. Research-media provenance and credits are recorded separately from the template license.
