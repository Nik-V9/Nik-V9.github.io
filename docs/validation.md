# Website validation — September 2026

Local validation for the September 2026 website release, including the final content edits.

## Build and content

- Python standard-library build completes without network access or third-party packages.
- 63 HTML pages generated, including the homepage, legacy redirects, news archive, and error page.
- Exactly 13 research entries, seven highlighted works, and seven tab panels.
- Both content and browser checks verify rendered highlights against the content settings,
  so changing the selected works does not require editing a fixed list in the checks.
- Research is ordered by first public release; publication venues are independent of sorting.
- All generated local links, fragments, images, fonts, video paths, and required files resolve.
- The current CV PDF is byte-for-byte identical to the version on the original `master` branch.
- The exact requested footer is present.

## Browser checks

Chrome 152.0.7977.84:

- All seven panels checked at 360, 390, 768, 1024, and 1440px widths; no page-level horizontal overflow.
- Keyboard arrow navigation, wraparound, Home/End, selected-tab focus, and shareable fragments pass.
- Browser back/forward, reload, direct research-entry links, and malformed-fragment fallback pass.
- 200% text enlargement preserves readable layouts without page-level overflow.
- Videos play while visible and pause offscreen and in inactive tabs. Pause/resume controls work.
- Reduced motion and data-saving preferences prevent automatic video loading; explicit play still works.
- Blocked autoplay leaves the poster and play control available.
- All 13 research posters decode correctly.
- All content remains visible with JavaScript disabled; printing exposes all seven sections.
- No JavaScript errors or failing local requests during the browser run.

WebKit 26.5 with iPhone 13 emulation:

- All seven panels render without page-level overflow.
- Muted inline autoplay, tap-to-pause/resume, and inactive-panel pause pass.
- Reduced-motion handling and selected-tab persistence on reload pass.
- No JavaScript errors.

Desktop and mobile screenshots were visually reviewed for typography, spacing, portrait treatment,
research highlights, media, awards, talks, outreach, and tab overflow. Screenshots and machine-readable
results live in the ignored `test-results/` directory.

These are browser and device-emulation checks, not tests on physical phones or tablets.

## External links

Checked 92 distinct homepage destinations. The old IBM hackathon repository returned 404 and was
replaced with the verified public repository under `Nik-V9`, including its legacy redirect.
IARPA’s canonical WRIVA URL returned 403 to the automated checker; the supplied official destination
is retained. Other checked homepage destinations responded successfully.

## Reproduce

```sh
python3 scripts/build.py
python3 scripts/check.py
python3 -m http.server 8000 --bind 127.0.0.1 --directory _site
```

In another terminal, with Google Chrome installed:

```sh
python3 -m venv .venv
.venv/bin/pip install playwright
.venv/bin/python scripts/browser_check.py
```

Browser tooling is optional and is not needed to build or deploy the site. Generated output and
test screenshots are ignored by Git.
