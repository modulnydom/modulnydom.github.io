/* Homepage model comparison, sourced from the existing catalog. */
(() => {
  'use strict';
  const source = document.getElementById('machineData');
  const panel = document.getElementById('machinePreview');
  const options = document.querySelector('[data-machine-options]');
  if (source && panel && options) {
    let models;
    try { models = JSON.parse(source.textContent); } catch { return; }
    const buttons = [...options.querySelectorAll('[data-machine-index]')];
    const image = panel.querySelector('[data-machine-photo]');
    const request = panel.querySelector('.machine-request');
    const detail = panel.querySelector('.machine-detail-link');
    const show = index => {
      const model = models[index];
      if (!model) return;
      buttons.forEach((button, i) => button.setAttribute('aria-pressed', String(i === index)));
      image.srcset = `${model.smallImage} 440w, ${model.image} 1000w`;
      image.src = model.image;
      image.alt = `${model.name} — фото модели`;
      for (const [key, value] of [['name', model.model], ['price', model.price], ['power', model.power], ['flow', model.flow], ['pressure', model.pressure], ['number', `${String(index + 1).padStart(2, '0')} / ${String(models.length).padStart(2, '0')}`]]) {
        panel.querySelector(`[data-machine-${key}]`).textContent = value;
      }
      detail.href = model.url;
      request.href = model.requestUrl;
      request.dataset.lead = model.name;
      // The common lead dialog reads data-lead at click time, preserving the selected model.
    };
    buttons.forEach((button, index) => {
      button.addEventListener('click', () => show(index));
      button.addEventListener('keydown', event => {
        let next;
        if (event.key === 'ArrowRight' || event.key === 'ArrowDown') next = (index + 1) % buttons.length;
        if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') next = (index - 1 + buttons.length) % buttons.length;
        if (event.key === 'Home') next = 0;
        if (event.key === 'End') next = buttons.length - 1;
        if (next === undefined) return;
        event.preventDefault();
        show(next);
        buttons[next].focus();
      });
    });
    options.hidden = false;
  }

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (!reduceMotion && 'IntersectionObserver' in window) {
    const targets = [...document.querySelectorAll('[data-reveal]')];
    document.body.classList.add('reveal-ready');
    const observer = new IntersectionObserver(entries => {
      for (const entry of entries) if (entry.isIntersecting) {
        entry.target.classList.add('is-revealed');
        observer.unobserve(entry.target);
      }
    }, { rootMargin: '0px 0px 35px 0px', threshold: 0.03 });
    targets.forEach(element => observer.observe(element));
  }
})();
