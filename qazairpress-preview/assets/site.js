/* Buildless progressive enhancement. The HTML remains useful without JavaScript. */
(() => {
  'use strict';
  const $ = (s, root = document) => root.querySelector(s);
  const $$ = (s, root = document) => [...root.querySelectorAll(s)];
  const menu = $('.menu-toggle');
  const nav = $('#navigation');
  const closeMenu = () => {
    nav?.classList.remove('open');
    menu?.setAttribute('aria-expanded', 'false');
    menu?.setAttribute('aria-label', 'Открыть меню');
  };
  menu?.addEventListener('click', () => {
    const open = menu.getAttribute('aria-expanded') !== 'true';
    menu.setAttribute('aria-expanded', String(open));
    menu.setAttribute('aria-label', open ? 'Закрыть меню' : 'Открыть меню');
    nav.classList.toggle('open', open);
  });
  $$('#navigation a').forEach(a => a.addEventListener('click', closeMenu));
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && nav?.classList.contains('open')) {
      closeMenu(); menu.focus();
    }
  });
  document.addEventListener('click', e => {
    if (!e.target.closest('.header')) closeMenu();
  });

  const catalog = $('#catalogFilters');
  if (catalog) {
    const cards = $$('.product-card', $('#catalogGrid'));
    const keys = ['q', 'category', 'sort', 'power', 'pressure', 'flow'];
    const controls = Object.fromEntries(keys.map(k => [k, catalog.elements.namedItem(k)]));
    const initial = new URLSearchParams(location.search);
    for (const key of keys) {
      const value = initial.get(key);
      if (value === null) continue;
      const el = controls[key];
      if (el.tagName !== 'SELECT' || [...el.options].some(o => o.value === value)) el.value = value;
    }
    if (['power', 'pressure', 'flow'].some(k => controls[k].value)) $('.technical-filters').open = true;
    const normalize = s => s.toLocaleLowerCase('ru').replace(/ё/g, 'е').replace(/[\s,.-]+/g, '');
    const apply = (updateUrl = true) => {
      const data = Object.fromEntries(keys.map(k => [k, controls[k].value.trim()]));
      const hasSpecs = !!(data.power || data.pressure || data.flow);
      let visible = 0;
      const order = [...cards].sort((a, b) => {
        if (data.sort === 'asc') return +a.dataset.price - +b.dataset.price;
        if (data.sort === 'desc') return +b.dataset.price - +a.dataset.price;
        if (data.sort === 'power') return (Number(a.dataset.power) || Infinity) - (Number(b.dataset.power) || Infinity);
        return cards.indexOf(a) - cards.indexOf(b);
      });
      for (const card of order) {
        const match = (data.category === 'all' || data.category === card.dataset.category) &&
          normalize(card.dataset.name).includes(normalize(data.q)) &&
          (!hasSpecs || card.dataset.category === 'compressors') &&
          (!data.power || +card.dataset.power === +data.power) &&
          (!data.pressure || +card.dataset.pressure === +data.pressure) &&
          (!data.flow || +card.dataset.flow >= +data.flow);
        card.hidden = !match;
        if (match) visible++;
        $('#catalogGrid').append(card);
      }
      $('#resultCount').textContent = `Показано ${visible} из ${cards.length} позиций`;
      $('#emptyState').hidden = visible !== 0;
      if (updateUrl) {
        const params = new URLSearchParams();
        for (const key of keys) if (data[key] && data[key] !== 'all' && data[key] !== 'default') params.set(key, data[key]);
        const query = params.toString();
        history.replaceState(null, '', location.pathname + (query ? '?' + query : ''));
      }
    };
    catalog.addEventListener('submit', e => e.preventDefault());
    catalog.addEventListener('input', () => apply());
    catalog.addEventListener('reset', () => setTimeout(() => apply(), 0));
    window.addEventListener('popstate', () => location.reload());
    apply(false);
  }

  const messageFor = form => {
    const data = new FormData(form);
    const values = [
      ['Модель / тема', data.get('model')], ['Имя', data.get('name')],
      ['Телефон', data.get('phone')], ['Компания', data.get('company')],
      ['Город поставки', data.get('city')], ['Мощность, кВт', data.get('power')],
      ['Давление, бар', data.get('pressure')], ['Расход, м³/мин', data.get('flow')],
      ['Требования к воздуху', data.get('air')], ['Оборудование и задача', data.get('task')]
    ];
    return ['Здравствуйте! Прошу подготовить предложение QazAirPress.',
      ...values.filter(([, v]) => String(v || '').trim()).map(([k, v]) => `${k}: ${String(v).trim()}`),
      `Страница: ${location.pathname}`].join('\n');
  };
  const bindForm = form => {
    form.addEventListener('submit', event => {
      event.preventDefault();
      const phone = form.elements.namedItem('phone');
      phone.setCustomValidity(phone.value.replace(/\D/g, '').length >= 10 ? '' : 'Укажите телефон: не менее 10 цифр.');
      if (!form.reportValidity()) return;
      const url = 'https://wa.me/77761717111?text=' + encodeURIComponent(messageFor(form));
      const fallback = $('.wa-fallback', form);
      fallback.href = url; fallback.hidden = false;
      $('.form-status', form).textContent = 'Текст готов. Проверьте его в WhatsApp и нажмите «Отправить».';
      // Navigate synchronously after a real submit: avoids popup blockers and false success.
      location.assign(url);
    });
    form.elements.namedItem('phone').addEventListener('input', e => e.target.setCustomValidity(''));
  };
  $$('.lead-form').forEach(bindForm);

  let dialog;
  let lastTrigger;
  const openLead = (trigger, model) => {
    lastTrigger = trigger;
    if (!dialog) {
      dialog = document.createElement('dialog');
      dialog.className = 'lead-dialog';
      dialog.setAttribute('aria-labelledby', 'dialogTitle');
      const script = document.querySelector('script[src$="assets/site.js"]');
      const privacy = new URL('../privacy.html', script.src).href;
      dialog.innerHTML = `<button type="button" class="dialog-close" aria-label="Закрыть форму">×</button><span class="eyebrow">QazAirPress / Запрос предложения</span><h2 id="dialogTitle">Получите предложение</h2><p class="chosen-model"></p><form class="lead-form"><input name="model" type="hidden"><div class="form-grid"><label>Ваше имя<input name="name" autocomplete="name" minlength="2" maxlength="90" required></label><label>Телефон<input name="phone" type="tel" inputmode="tel" autocomplete="tel" maxlength="30" required placeholder="+7 ___ ___ __ __"></label><label>Компания<input name="company" autocomplete="organization" maxlength="120"></label><label>Город поставки<input name="city" autocomplete="address-level2" maxlength="100" required></label><label class="full">Что нужно вашему производству?<textarea name="task" rows="3" maxlength="1500" placeholder="Мощность, давление, расход, требования к воздуху"></textarea></label></div><label class="consent"><input type="checkbox" name="consent" required><span>Согласен передать данные QazAirPress через WhatsApp. <a href="${privacy}">Обработка данных</a></span></label><button class="btn primary" type="submit">Открыть запрос в WhatsApp ↗</button><p class="form-note">Проверьте текст в WhatsApp и нажмите «Отправить».</p><p class="form-status" role="status" aria-live="polite"></p><a class="wa-fallback" hidden>Открыть подготовленное сообщение ↗</a></form>`;
      document.body.append(dialog);
      bindForm($('.lead-form', dialog));
      $('.dialog-close', dialog).addEventListener('click', () => dialog.close());
      dialog.addEventListener('click', e => { if (e.target === dialog) dialog.close(); });
      dialog.addEventListener('close', () => { document.body.classList.remove('modal-open'); lastTrigger?.focus(); });
    }
    dialog.querySelector('[name="model"]').value = model;
    $('.chosen-model', dialog).textContent = model || 'Подбор оборудования для вашего производства';
    $('.form-status', dialog).textContent = '';
    $('.wa-fallback', dialog).hidden = true;
    document.body.classList.add('modal-open');
    dialog.showModal();
  };
  $$('[data-lead]').forEach(a => a.addEventListener('click', e => {
    if (e.ctrlKey || e.metaKey || e.shiftKey || e.altKey) return;
    e.preventDefault(); openLead(a, a.dataset.lead);
  }));
})();
