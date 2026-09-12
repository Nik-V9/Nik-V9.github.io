#!/usr/bin/env python3
"""Render the site using Python's standard library. No network or dependencies."""
from pathlib import Path
from html import escape
from string import Template
from urllib.parse import urlsplit
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '_site'
BASE = 'https://nik-v9.github.io'
TABS = [('featured-research', 'Featured Research'), ('awards', 'Awards'),
        ('press', 'Press'), ('talks', 'Talks'), ('service', 'Service'),
        ('outreach', 'Outreach'), ('projects', 'Projects')]


def read(name):
    return json.loads((ROOT / 'content' / name).read_text())


def link(label, url):
    if urlsplit(url).scheme not in ('', 'https', 'http', 'mailto'):
        raise ValueError(f'Unsupported URL: {url}')
    return f'<a href="{escape(url, quote=True)}">{escape(label)}</a>'


def resources(items):
    return '<div class="resource-links">' + ''.join(link(*item) for item in items) + '</div>' if items else ''


def page(body, title='Nikhil Keetha', path='/', description=None):
    profile = read('profile.json')
    description = description or profile['description']
    schema = {'@context': 'https://schema.org', '@type': 'Person',
              'name': profile['name'], 'url': BASE + '/',
              'image': BASE + '/assets/media/portrait.jpg',
              'jobTitle': 'Ph.D. candidate in Robotics',
              'affiliation': [{'@type': 'Organization', 'name': 'Carnegie Mellon University'},
                              {'@type': 'Organization', 'name': 'Meta'}],
              'sameAs': [url for _, url in profile['socials'] if url.startswith('https://')]}
    return Template((ROOT / 'templates/page.html').read_text()).substitute(
        title=escape(title), description=escape(description, quote=True),
        canonical=escape(BASE + path, quote=True), body=body,
        structured_data=json.dumps(schema, ensure_ascii=False).replace('<', '\\u003c'))


def research_row(paper):
    title = paper['title']
    authors = []
    for name in paper.get('authors', []):
        author = f'<strong>{escape(name)}</strong>' if name == 'Nikhil Keetha' else escape(name)
        if name in paper.get('equal_contribution', []):
            author += '<sup aria-label="equal contribution">*</sup>'
        authors.append(author)
    byline = ', '.join(authors) if authors else escape(paper['team'])
    media = paper['media']
    visual = (f'<img src="{escape(media["poster"])}" alt="{escape(media["alt"])}" '
              f'width="{media["width"]}" height="{media["height"]}" loading="lazy" decoding="async">')
    if media.get('video'):
        visual += (f'<video data-src="{escape(media["video"])}" data-title="{escape(paper["short_title"])}" '
                   'muted loop playsinline preload="none" aria-hidden="true" tabindex="-1"></video>'
                   f'<button class="video-toggle" type="button" aria-label="Play {escape(paper["short_title"])} teaser" '
                   'aria-pressed="false"><span aria-hidden="true">▶</span></button>')
    distinction = f' <span class="distinction">· {escape(paper["distinction"])}</span>' if paper.get('distinction') else ''
    highlighted = ' highlighted' if paper['highlighted'] else ''
    return (f'<article class="research-row{highlighted}" id="{paper["id"]}" data-release="{paper["release_date"]}">'
            f'<figure class="teaser">{visual}</figure><div class="research-text">'
            f'<h3 class="paper-title">{link(title, paper["url"])}</h3>'
            f'<p class="authors">{byline}</p><p class="venue">{escape(paper["venue"])}{distinction}</p>'
            f'{resources(paper["links"])}<p class="takeaway">{escape(paper["summary"])}</p></div></article>')


def activities(items):
    result = '<ul class="activity-list">'
    for item in items:
        title = link(item['title'], item['url']) if item.get('url') else escape(item['title'])
        detail = f'<p class="activity-detail">{escape(item["detail"])}</p>' if item.get('detail') else ''
        result += (f'<li class="activity"><div class="activity-date">{escape(item["date"])}</div>'
                   f'<div><p class="activity-title">{title}</p>{detail}{resources(item.get("links", []))}</div></li>')
    return result + '</ul>'


def homepage():
    profile, research, data, legacy = (read(name) for name in
        ['profile.json', 'research.json', 'activities.json', 'legacy.json'])
    body = '<main id="main"><header class="profile"><div class="profile-copy">'
    body += f'<h1>{escape(profile["name"])}</h1>'
    body += ''.join(f'<p>{paragraph}</p>' for paragraph in profile['bio_html'])
    body += f'<p class="personal">{escape(profile["personal"])}</p>'
    body += '<ul class="socials" aria-label="Contact and profiles">'
    body += ''.join(f'<li>{link(*social)}</li>' for social in profile['socials']) + '</ul></div>'
    body += ('<a class="portrait-link" href="/assets/media/portrait.jpg" aria-label="View portrait of Nikhil Keetha">'
             '<picture><source srcset="/assets/media/portrait.webp" type="image/webp">'
             '<img class="portrait" src="/assets/media/portrait.jpg" alt="Nikhil Keetha" width="700" height="683" '
             'fetchpriority="high"></picture></a></header>')
    body += '<nav class="tabs" aria-label="Sections">' + ''.join(
        f'<a class="tab" id="tab-{id}" href="#{id}">{label}</a>' for id, label in TABS) + '</nav>'
    sections = {}
    sections['featured-research'] = ('<p class="section-intro">Selected work, newest first. '
        + link('Full publication list on Google Scholar', profile['scholar']) + '.</p>'
        + '<div class="research-list">'
        + ''.join(research_row(p) for p in sorted(research, key=lambda p: (p['release_date'], p['id']), reverse=True))
        + '</div><p class="selected-note">A few works are <span class="highlight-key">highlighted</span>. '
          '* indicates equal contribution.</p>')
    sections['awards'] = activities(data['awards'])
    sections['talks'] = activities(data['talks'])
    sections['press'] = ''.join('<div class="press-group"><h3>' + escape(group['project']) + '</h3><ul class="press-list">'
        + ''.join('<li>' + link(item['title'], item['url']) + '<span class="press-meta">' + escape(item['meta']) + '</span></li>'
                  for item in group['items']) + '</ul></div>' for group in data['press'])
    sections['service'] = ''.join('<div class="content-group"><h3>' + escape(group['title']) + '</h3>'
        + '<ul class="compact-list">' + ''.join('<li>' + text + '</li>' for text in group['items_html']) + '</ul></div>'
        for group in data['service'])
    sections['outreach'] = ''.join('<article class="outreach-row">'
        + f'<img src="{escape(item["image"])}" alt="{escape(item["title"])}" width="160" height="100" loading="lazy">'
        + '<div><h3>' + link(item['title'], item['url']) + '</h3><p>' + escape(item['description']) + '</p></div></article>'
        for item in data['outreach'])
    sections['projects'] = '<div class="content-group"><h3>Research collaborations</h3>'
    sections['projects'] += '<p>At CMU, I have worked on collaborative research with these partners and programs:</p><ul class="compact-list">'
    sections['projects'] += ''.join('<li>' + (link(item['name'], item['url']) if item.get('url') else escape(item['name']))
        + '</li>' for item in data['collaborations']) + '</ul></div>'
    sections['projects'] += '<div class="content-group"><h3>Earlier software projects</h3><ul class="compact-list">'
    sections['projects'] += ''.join('<li>' + link(item['title'], item['url']) + '<br><span class="activity-detail">'
        + escape(item['description']) + '</span></li>' for item in sorted(legacy['projects'], key=lambda x: x['order'])) + '</ul></div>'
    for id, label in TABS:
        body += f'<section class="panel" id="{id}"><h2 class="panel-title">{label}</h2>{sections[id]}</section>'
    return page(body + '</main>')


def write(path, content):
    target = OUT / path.lstrip('/')
    if path.endswith('/'):
        target /= 'index.html'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content)


def redirect(path, destination, title):
    absolute = BASE + destination if destination.startswith('/') else destination
    content = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>{escape(title)} — Nikhil Keetha</title>'
        f'<link rel="canonical" href="{escape(absolute, quote=True)}">'
        f'<meta http-equiv="refresh" content="0; url={escape(destination, quote=True)}"></head>'
        f'<body><p>{link("Continue to " + title, destination)}</p></body></html>')
    write(path, content)


def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / 'assets', OUT / 'assets')
    write('/index.html', homepage())
    write('/.nojekyll', '')
    legacy = read('legacy.json')
    for item in legacy['redirects']:
        redirect(item['path'], item['url'], item['title'])
    for path, destination, label in [('/publications/', read('profile.json')['scholar'], 'Publications'),
        ('/service/', '/#service', 'Service'), ('/projects/', '/#projects', 'Projects'),
        ('/cv/', '/assets/pdf/Nikhil_CV.pdf', 'CV'), ('/teaching/', '/#service', 'Teaching'),
        ('/repositories/', 'https://github.com/Nik-V9', 'GitHub')]:
        redirect(path, destination, label)
    archive_header = '<header class="archive-header">' + link('← Nikhil Keetha', '/')
    news_list = '<ul class="activity-list">'
    for item in reversed(legacy['news']):
        news_list += '<li class="activity"><div class="activity-date">' + escape(item['date']) + '</div><div>' + item['html'] + '</div></li>'
        body = '<main id="main" class="archive-content">' + archive_header + '<h1>Earlier update</h1></header>'
        body += '<p class="activity-date">' + escape(item['date']) + '</p><p>' + item['html'] + '</p></main>'
        write(item['path'], page(body, 'Earlier update — Nikhil Keetha', item['path']))
    news_body = '<main id="main" class="archive-content">' + archive_header + '<h1>Earlier updates</h1></header>' + news_list + '</ul></main>'
    write('/news/', page(news_body, 'Earlier updates — Nikhil Keetha', '/news/'))
    redirect('/news.html', '/news/', 'Earlier updates')
    posts = [item for item in legacy['redirects'] if item['path'].startswith('/blog/')]
    blog_body = '<main id="main" class="archive-content">' + archive_header + '<h1>Earlier writing</h1></header><ul class="compact-list">'
    blog_body += ''.join('<li>' + link(item['title'], item['url']) + '</li>' for item in reversed(posts)) + '</ul></main>'
    write('/blog/', page(blog_body, 'Earlier writing — Nikhil Keetha', '/blog/'))
    for path in ['/blog/2021/', '/blog/2022/', '/blog/2023/', '/blog/page/2/']:
        redirect(path, '/blog/', 'Earlier writing')
    write('/404.html', page('<main id="main"><h1>Page not found</h1><p>' + link('Return to Nikhil Keetha’s website', '/')
                           + '.</p></main>', 'Page not found — Nikhil Keetha', '/404.html'))
    canonical_paths = ['/', '/news/', '/blog/'] + [item['path'] for item in legacy['news']]
    write('/sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        + ''.join('<url><loc>' + BASE + path + '</loc></url>' for path in canonical_paths) + '</urlset>\n')
    write('/robots.txt', 'User-agent: *\nAllow: /\nSitemap: ' + BASE + '/sitemap.xml\n')
    print(f'Built {sum(1 for _ in OUT.rglob("*.html"))} HTML pages in {OUT}')


if __name__ == '__main__':
    build()
