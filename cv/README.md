# Nikhil Varma Keetha - Curriculum Vitae

An editable, single-column LaTeX CV using Lato, charcoal text, and restrained orange accents.
The draft PDF lives beside this README. The website continues to serve the separately reviewed
copy at `assets/pdf/Nikhil_CV.pdf` until it is explicitly replaced.

## Edit

- `main.tex`: header, contact links, and section order.
- `style.tex`: typography, margins, entry formatting, and footer date.
- `sections/*.tex`: education, experience, awards, research descriptions and links, press, talks,
  projects, service, and outreach. These are ordinary editable LaTeX files, not generated at build time.
- `research.bib`: titles, complete author lists, publication dates, and venue/status lines for the
  13 selected works. The `note` field is the venue/status line shown in the CV. `author+an` marks
  the CV author with `me` and equal contributors with `equal`; these annotations control bold text
  and asterisks. Pomelo and Hyperscape use corporate team attribution as public demos.

The website content was used to seed this CV. Later edits remain independent: update the LaTeX
or bibliography directly, and update website content separately when appropriate. Keep author names
as published; the CV header uses the full name Nikhil Varma Keetha.

## Local build

Use TeX Live, MacTeX, or TinyTeX with XeLaTeX, Biber, and latexmk. Relevant packages are
`biblatex`, `lato`, `fontaxes`, `titlesec`, `enumitem`, `needspace`, `fancyhdr`, `lastpage`, `ragged2e`,
`fontspec`, `microtype`, `geometry`, `xcolor`, `hyperref`, and `tools` (for tabularx).

From the website repository:

```sh
python3 cv/build.py
```

For a portable TeX installation, pass its executable directory:

```sh
python3 cv/build.py --tex-bin /path/to/TinyTeX/bin/universal-darwin
```

The build creates `Nikhil_Varma_Keetha_CV.pdf` and an upload-ready source archive at
`build/Nikhil_CV_Overleaf.zip`. It does not alter the website PDF or deploy anything.
Build intermediates are ignored by Git. The equivalent direct compilation command from this folder is:

```sh
latexmk -xelatex -outdir=build main.tex
```

## Overleaf

Upload `build/Nikhil_CV_Overleaf.zip` as a new Overleaf project, select `main.tex` as the main
document, and use the **XeLaTeX** compiler. Overleaf runs Biber automatically through latexmk.
No custom class, externally installed system font, image asset, or Python script is required.
Upload only these sources; the archive excludes private notes and old template files.

## Review and publish

Render and inspect every page after significant edits. Check page breaks, dates, thesis titles,
GPAs, author names, equal-contribution marks, hyperlinks, and text extraction. Check the final
`build/main.log` for missing references, missing glyphs, and overfull boxes.

After the draft is approved, replace the public download copy locally:

```sh
python3 cv/build.py --publish
python3 scripts/build.py
python3 scripts/check.py
```

Commit the sources, draft PDF, and updated website PDF together. Publishing still uses the
website's existing GitHub Pages workflow; LaTeX is not a dependency of normal website builds.

## Content notes

Education dates and the full header name follow the September 2026 corrections. The M.S. GPA
(4.12/4.0) and B.Tech. GPA (8.94/10.0) are retained from the prior CV; no Ph.D. GPA or expected
graduation date is inferred. The Ph.D. thesis uses the label "Thesis." Appointment and outreach
dates come from the prior personal CV. Current roles, research, awards, talks, and service use
the September 2026 notes and the current website. Research descriptions are preserved.

The six sponsored collaborations do not imply a PI title or a specific grant role. The unused
example awards, cover letter, and resume content shipped with the old Awesome-CV template are
not personal source material for this CV.
