#!/usr/bin/env python3
"""Optional browser regression checks. Requires playwright and an installed Chrome."""
from pathlib import Path
import argparse
import json
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / 'test-results'
LABELS = ['Featured Research', 'Awards', 'Press', 'Talks', 'Service', 'Outreach', 'Projects']


def check(base):
    RESULTS.mkdir(exist_ok=True)
    research = json.loads((ROOT / 'content/research.json').read_text())
    highlights = {paper['id'] for paper in research if paper['highlighted']}
    errors, failed_requests, checks = [], [], []
    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True)
        context = browser.new_context(viewport={'width': 1440, 'height': 1000}, reduced_motion='reduce')
        page = context.new_page()
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('response', lambda response: failed_requests.append(f'{response.status} {response.url}')
                if response.url.startswith(base) and response.status >= 400 else None)
        for width in [360, 390, 768, 1024, 1440]:
            page.set_viewport_size({'width': width, 'height': 1000})
            page.goto(base, wait_until='networkidle')
            page.evaluate('document.fonts.ready')
            assert page.locator('.research-row').count() == 13
            rendered_highlights = page.locator('.research-row.highlighted').evaluate_all('(rows) => rows.map(row => row.id)')
            assert set(rendered_highlights) == highlights
            for label in LABELS:
                page.get_by_role('tab', name=label, exact=True).click()
                assert page.locator('.panel:visible').count() == 1, (width, label)
                assert page.get_by_role('tab', name=label, exact=True).get_attribute('aria-selected') == 'true'
                assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), (width, label, 'horizontal overflow')
                if width in [390, 1440]:
                    page.locator('.panel:visible img').evaluate_all('async imgs => { for (const img of imgs) img.loading = "eager"; await Promise.all(imgs.map(img => img.decode())); }')
                    page.screenshot(path=RESULTS / f'{width}-{label.lower().replace(" ", "-")}.png', full_page=True)
            checks.append(f'All seven panels at {width}px: no page overflow, correct selection')
        page.set_viewport_size({'width': 1440, 'height': 1000})
        page.goto(base)
        page.get_by_role('tab', name='Featured Research', exact=True).focus()
        page.keyboard.press('ArrowRight')
        assert page.get_by_role('tab', name='Awards', exact=True).get_attribute('aria-selected') == 'true'
        page.keyboard.press('End')
        assert page.get_by_role('tab', name='Projects', exact=True).get_attribute('aria-selected') == 'true'
        page.keyboard.press('Home')
        assert page.get_by_role('tab', name='Featured Research', exact=True).get_attribute('aria-selected') == 'true'
        page.keyboard.press('ArrowLeft')
        assert page.get_by_role('tab', name='Projects', exact=True).get_attribute('aria-selected') == 'true'
        checks.append('Keyboard: arrows wrap; Home and End select and focus the correct tab')
        page.goto(base)
        page.get_by_role('tab', name='Awards', exact=True).click()
        page.get_by_role('tab', name='Talks', exact=True).click()
        page.go_back()
        assert page.get_by_role('tab', name='Awards', exact=True).get_attribute('aria-selected') == 'true'
        page.go_forward()
        assert page.get_by_role('tab', name='Talks', exact=True).get_attribute('aria-selected') == 'true'
        page.reload()
        assert page.get_by_role('tab', name='Talks', exact=True).get_attribute('aria-selected') == 'true'
        page.goto(base + '#raven')
        assert page.locator('#raven').is_visible()
        assert page.locator('#featured-research').is_visible()
        page.goto(base + '#%E0%A4%A')
        assert page.locator('#featured-research').is_visible()
        checks.append('Deep links, malformed fragments, reloads, and browser back/forward')
        page.goto(base)
        page.add_style_tag(content='html {font-size: 200% !important}')
        for label in LABELS:
            page.get_by_role('tab', name=label, exact=True).click()
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), ('200% text', label)
        page.screenshot(path=RESULTS / '200-percent-text.png', full_page=True)
        checks.append('200% text enlargement: all panels remain within the viewport')
        page.goto(base)
        assert page.locator('video').evaluate_all('(vs) => vs.every(v => v.paused && !v.getAttribute("src"))')
        checks.append('Reduced motion: posters only, no automatic video downloads')
        page.emulate_media(media='print')
        assert page.locator('.panel:visible').count() == 7
        checks.append('Print: all seven sections visible')
        page.emulate_media(media='screen', reduced_motion='no-preference')
        page.goto(base + '#featured-research')
        video = page.locator('#multiperspective video')
        video.scroll_into_view_if_needed()
        page.wait_for_function('!document.querySelector("#multiperspective video").paused')
        page.locator('#multiperspective .video-toggle').click()
        assert video.evaluate('(v) => v.paused')
        page.locator('#multiperspective .video-toggle').click()
        page.wait_for_function('!document.querySelector("#multiperspective video").paused')
        page.get_by_role('tab', name='Awards', exact=True).click()
        assert page.locator('video').evaluate_all('(vs) => vs.every(v => v.paused)')
        page.get_by_role('tab', name='Featured Research', exact=True).click()
        page.locator('#anyloc').scroll_into_view_if_needed()
        page.wait_for_function('document.querySelector("#multiperspective video").paused')
        checks.append('Media: visible autoplay, pause/resume, offscreen pause, inactive-panel pause')
        # Scroll every row into view and wait for its poster to decode.
        for row in page.locator('.research-row').all():
            row.scroll_into_view_if_needed()
            row.locator('img').evaluate('(img) => img.decode()')
        checks.append('All 13 research posters decode')
        plain_context = browser.new_context(java_script_enabled=False, viewport={'width': 390, 'height': 844})
        plain = plain_context.new_page()
        plain.goto(base)
        assert plain.locator('.panel:visible').count() == 7
        assert plain.locator('.research-row').count() == 13
        assert plain.evaluate('document.documentElement.scrollWidth <= innerWidth')
        checks.append('JavaScript disabled: all content and anchor navigation available')
        blocked_context = browser.new_context(viewport={'width': 1440, 'height': 1000})
        blocked_context.add_init_script('HTMLMediaElement.prototype.play = function () { return Promise.reject(new DOMException("Autoplay blocked", "NotAllowedError")); };')
        blocked = blocked_context.new_page()
        blocked.goto(base + '#featured-research', wait_until='networkidle')
        assert blocked.locator('#multiperspective img').is_visible()
        assert blocked.locator('#multiperspective video').evaluate('(v) => v.paused && !v.classList.contains("is-playing")')
        assert blocked.locator('#multiperspective .video-toggle').is_visible()
        checks.append('Blocked autoplay: visible poster and usable play control')
        saving_context = browser.new_context(viewport={'width': 1440, 'height': 1000})
        saving_context.add_init_script('Object.defineProperty(navigator, "connection", {value: {saveData: true}});')
        saving = saving_context.new_page()
        saving.goto(base + '#featured-research', wait_until='networkidle')
        assert saving.locator('video').evaluate_all('(vs) => vs.every(v => v.paused && !v.getAttribute("src"))')
        saving.locator('#multiperspective .video-toggle').click()
        saving.wait_for_function('!document.querySelector("#multiperspective video").paused')
        checks.append('Data saving: no automatic downloads, explicit play works')
        assert not errors, errors
        assert not failed_requests, failed_requests
        checks.append('No JavaScript errors or failing local requests')
        browser.close()
    (RESULTS / 'browser-report.json').write_text(json.dumps({'checks': checks, 'errors': errors, 'failed_requests': failed_requests}, indent=2) + '\n')
    print('\n'.join('PASS: ' + message for message in checks))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--base-url', default='http://127.0.0.1:8000/')
    check(parser.parse_args().base_url)
