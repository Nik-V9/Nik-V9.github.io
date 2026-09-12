#!/usr/bin/env python3
"""Check generated content, routes, and assets without third-party dependencies."""
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import json
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '_site'


class Document(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.refs = []
        self.errors = []
        self.rows = []
        self.tabs = []
        self.panels = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        id = attrs.get('id')
        if id:
            if id in self.ids:
                self.errors.append(f'Duplicate id: {id}')
            self.ids.add(id)
        for key in ['href', 'src', 'data-src', 'poster']:
            if attrs.get(key):
                self.refs.append(attrs[key])
        if attrs.get('srcset'):
            self.refs.extend(part.strip().split()[0] for part in attrs['srcset'].split(','))
        if tag == 'img' and not attrs.get('alt'):
            self.errors.append('Image missing descriptive alt text')
        if 'research-row' in attrs.get('class', '').split():
            self.rows.append((id, attrs.get('data-release')))
        if 'tab' in attrs.get('class', '').split():
            self.tabs.append(id)
        if 'panel' in attrs.get('class', '').split():
            self.panels.append(id)


def check():
    errors = []
    research = json.loads((ROOT / 'content/research.json').read_text())
    expected = {'mapanything', 'ufm', 'any4d', 'multiperspective', 'hyperscape', 'flowr',
                'rayfronts', 'raven', 'visafe', 'mapitanywhere', 'splatam', 'anyloc', 'foundloc'}
    highlights = {'mapanything', 'ufm', 'any4d', 'multiperspective', 'splatam', 'anyloc'}
    if len(research) != 13 or {p['id'] for p in research} != expected:
        errors.append('Research selection differs from the approved 13 works')
    if {p['id'] for p in research if p['highlighted']} != highlights:
        errors.append('Highlighted selection differs from the approved six works')
    for paper in research:
        date.fromisoformat(paper['release_date'])
        if not paper.get('authors') and not paper.get('team'):
            errors.append(f'Missing attribution: {paper["id"]}')
        if not paper['summary'] or not paper['venue']:
            errors.append(f'Incomplete publication: {paper["id"]}')
    docs = {}
    for path in OUT.rglob('*.html'):
        doc = Document()
        doc.feed(path.read_text())
        docs[path] = doc
        errors.extend(f'{path.relative_to(OUT)}: {e}' for e in doc.errors)
    if not docs:
        errors.append('No generated HTML; run scripts/build.py first')
    for path, doc in docs.items():
        for ref in doc.refs:
            url = urlsplit(ref)
            if url.scheme or url.netloc:
                continue
            if url.path.startswith('/'):
                target = OUT / unquote(url.path).lstrip('/')
            elif url.path:
                target = path.parent / unquote(url.path)
            else:
                target = path
            if target.is_dir():
                target /= 'index.html'
            if not target.is_file():
                errors.append(f'{path.relative_to(OUT)}: Missing target {ref}')
            elif url.fragment and target in docs and unquote(url.fragment) not in docs[target].ids:
                errors.append(f'{path.relative_to(OUT)}: Missing fragment {ref}')
    home = docs.get(OUT / 'index.html')
    if home:
        expected_order = [(p['id'], p['release_date']) for p in sorted(research, key=lambda p: (p['release_date'], p['id']), reverse=True)]
        if home.rows != expected_order:
            errors.append('Rendered research is not in release-date order')
        if len(home.tabs) != 7 or len(home.panels) != 7:
            errors.append('Expected seven tabs and panels')
        plain = re.sub(r'<[^>]+>', '', (OUT / 'index.html').read_text())
        if 'Thanks Jon Barron for the clean template.' not in plain or 'Last updated September 2026.' not in plain:
            errors.append('Footer differs from approved wording')
    for css in (OUT / 'assets/site').glob('*.css'):
        for ref in re.findall(r'url\([\'"]?([^\)\'" ]+)', css.read_text()):
            if ref.startswith('/') and not (OUT / ref.lstrip('/')).is_file():
                errors.append(f'Missing CSS asset: {ref}')
    for path in ['.nojekyll', 'robots.txt', 'sitemap.xml', 'assets/pdf/Nikhil_CV.pdf']:
        if not (OUT / path).is_file():
            errors.append(f'Missing required file: {path}')
    if errors:
        raise SystemExit('\n'.join(errors))
    print(f'PASS: {len(docs)} HTML pages, 13 research entries, six highlights, seven panels, and all local links/assets.')


if __name__ == '__main__':
    check()
