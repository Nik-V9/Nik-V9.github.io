(() => {
  'use strict';
  const navigation = document.querySelector('.tabs');
  if (!navigation) return;
  const tabs = [...navigation.querySelectorAll('.tab')];
  const panels = [...document.querySelectorAll('.panel')];
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const videos = [...document.querySelectorAll('.teaser video')];
  const videoStates = new Map(videos.map(video => [video, {visible: false, paused: false, manual: false}]));
  const buttonFor = video => video.parentElement.querySelector('.video-toggle');
  const shouldPlay = video => {
    const state = videoStates.get(video);
    return state.visible && !state.paused && !document.hidden && !video.closest('.panel').hidden &&
      (!reducedMotion.matches || state.manual) && (!navigator.connection?.saveData || state.manual);
  };
  function updateButton(video) {
    const button = buttonFor(video);
    const playing = !video.paused;
    button.setAttribute('aria-label', `${playing ? 'Pause' : 'Play'} ${video.dataset.title} teaser`);
    button.setAttribute('aria-pressed', String(playing));
    button.querySelector('span').textContent = playing ? 'Ⅱ' : '▶';
  }
  async function syncVideo(video) {
    if (!shouldPlay(video)) {
      video.pause();
      updateButton(video);
      return;
    }
    if (!video.src) {
      video.src = video.dataset.src;
      video.load();
    }
    try {
      await video.play();
      if (!shouldPlay(video)) video.pause();
    } catch (_) {
      // The poster and play button remain usable when autoplay is unavailable.
    }
    updateButton(video);
  }
  function syncAll() { videos.forEach(syncVideo); }
  for (const video of videos) {
    video.addEventListener('playing', () => { video.classList.add('is-playing'); updateButton(video); });
    video.addEventListener('pause', () => updateButton(video));
    video.addEventListener('error', () => {
      video.classList.remove('is-playing');
      buttonFor(video).hidden = true;
    });
    buttonFor(video).addEventListener('click', () => {
      const state = videoStates.get(video);
      state.paused = !video.paused;
      state.manual = true;
      syncVideo(video);
    });
  }
  const observer = 'IntersectionObserver' in window ? new IntersectionObserver(entries => {
    for (const entry of entries) {
      videoStates.get(entry.target).visible = entry.isIntersecting;
      syncVideo(entry.target);
    }
  }, {threshold: .15}) : null;
  videos.forEach(video => {
    if (observer) observer.observe(video);
    else { videoStates.get(video).visible = true; videoStates.get(video).paused = true; }
  });
  function selectPanel(id, updateHistory = false) {
    const panel = panels.find(item => item.id === id) || panels[0];
    panels.forEach(item => { item.hidden = item !== panel; });
    tabs.forEach(tab => {
      const selected = tab.hash === `#${panel.id}`;
      tab.setAttribute('aria-selected', String(selected));
      tab.tabIndex = selected ? 0 : -1;
    });
    const selectedTab = tabs.find(tab => tab.hash === `#${panel.id}`);
    const left = selectedTab.offsetLeft - navigation.offsetLeft;
    if (left < navigation.scrollLeft) navigation.scrollLeft = left;
    if (left + selectedTab.offsetWidth > navigation.scrollLeft + navigation.clientWidth)
      navigation.scrollLeft = left + selectedTab.offsetWidth - navigation.clientWidth;
    if (updateHistory && location.hash !== `#${panel.id}`) history.pushState(null, '', `#${panel.id}`);
    syncAll();
  }
  function panelFromHash() {
    let id;
    try { id = decodeURIComponent(location.hash.slice(1)); } catch (_) { id = ''; }
    const target = document.getElementById(id);
    return target?.closest('.panel')?.id || panels[0].id;
  }
  navigation.setAttribute('role', 'tablist');
  navigation.setAttribute('aria-label', 'Explore my work');
  for (const tab of tabs) {
    tab.setAttribute('role', 'tab');
    tab.setAttribute('aria-controls', tab.hash.slice(1));
    tab.addEventListener('click', event => {
      if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      selectPanel(tab.hash.slice(1), true);
    });
    tab.addEventListener('keydown', event => {
      let index = tabs.indexOf(tab);
      if (event.key === 'ArrowRight') index = (index + 1) % tabs.length;
      else if (event.key === 'ArrowLeft') index = (index - 1 + tabs.length) % tabs.length;
      else if (event.key === 'Home') index = 0;
      else if (event.key === 'End') index = tabs.length - 1;
      else if (event.key === ' ') { event.preventDefault(); selectPanel(tab.hash.slice(1), true); return; }
      else return;
      event.preventDefault();
      tabs[index].focus({preventScroll: true});
      selectPanel(tabs[index].hash.slice(1), true);
    });
  }
  panels.forEach(panel => {
    panel.setAttribute('role', 'tabpanel');
    panel.setAttribute('aria-labelledby', `tab-${panel.id}`);
    panel.tabIndex = 0;
  });
  selectPanel(panelFromHash());
  document.documentElement.classList.add('js-tabs');
  window.addEventListener('popstate', () => selectPanel(panelFromHash()));
  window.addEventListener('hashchange', () => selectPanel(panelFromHash()));
  document.addEventListener('visibilitychange', syncAll);
  reducedMotion.addEventListener('change', () => {
    videoStates.forEach(state => { state.manual = false; });
    syncAll();
  });
})();

// Keep the existing production analytics property; local previews do not report visits.
if (location.hostname === 'nik-v9.github.io') {
  window.dataLayer = window.dataLayer || [];
  window.gtag = function () { window.dataLayer.push(arguments); };
  window.gtag('js', new Date());
  window.gtag('config', 'G-G7H9CMFQ8S');
  const analytics = document.createElement('script');
  analytics.async = true;
  analytics.src = 'https://www.googletagmanager.com/gtag/js?id=G-G7H9CMFQ8S';
  document.head.appendChild(analytics);
}
