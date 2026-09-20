/* ===========================================================================
   Shared front-end helpers.
   - CSRF header injection for fetch()
   - Toast system
   - Modal open / close
   - Mobile navbar toggle
   - Lucide icon rendering (inline SVG <i data-lucide="...">)
   - Small helpers (money format, debounce)
   =========================================================================== */

(function () {
  'use strict';

  // ---------------------------------------------------------------- CSRF
  // Expose the token so any fetch() call can attach it as a header.
  window.csrf = function () {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
  };

  // Wrap fetch so every non-GET request carries the CSRF header automatically.
  const rawFetch = window.fetch.bind(window);
  window.fetch = function (url, options) {
    options = options || {};
    const method = (options.method || 'GET').toUpperCase();
    if (method !== 'GET' && method !== 'HEAD') {
      options.headers = Object.assign({}, options.headers || {}, {
        'X-CSRF-Token': window.csrf(),
        'X-Requested-With': 'fetch'
      });
    }
    return rawFetch(url, options);
  };

  // ---------------------------------------------------------------- Toasts
  function ensureToastStack() {
    let stack = document.querySelector('.toast-stack');
    if (!stack) {
      stack = document.createElement('div');
      stack.className = 'toast-stack';
      stack.setAttribute('aria-live', 'polite');
      document.body.appendChild(stack);
    }
    return stack;
  }

  window.toast = function (message, kind, timeout) {
    const stack = ensureToastStack();
    const el = document.createElement('div');
    el.className = 'toast ' + (kind || 'info');
    el.textContent = message;
    stack.appendChild(el);
    const t = timeout || 3600;
    setTimeout(function () {
      el.style.transition = 'opacity 220ms ease-out, transform 220ms ease-out';
      el.style.opacity = '0';
      el.style.transform = 'translateY(-6px)';
      setTimeout(function () { el.remove(); }, 240);
    }, t);
  };

  // ---------------------------------------------------------------- Modals
  window.openModal = function (id) {
    const m = document.getElementById(id);
    if (!m) return;
    m.classList.add('open');
    document.body.style.overflow = 'hidden';
    const focusable = m.querySelector('button, [href], input, select, textarea');
    if (focusable) setTimeout(function () { focusable.focus(); }, 40);
  };

  window.closeModal = function (id) {
    const m = document.getElementById(id);
    if (!m) return;
    m.classList.remove('open');
    document.body.style.overflow = '';
  };

  // Click on the backdrop (not the inner card) closes the modal.
  document.addEventListener('click', function (e) {
    if (e.target.classList && e.target.classList.contains('modal-backdrop')) {
      e.target.classList.remove('open');
      document.body.style.overflow = '';
    }
    if (e.target.classList && e.target.classList.contains('panel-backdrop')) {
      e.target.classList.remove('open');
      document.body.style.overflow = '';
    }
  });

  // ESC closes any open modal / panel.
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      document.querySelectorAll('.modal-backdrop.open, .panel-backdrop.open')
        .forEach(function (el) {
          el.classList.remove('open');
          document.body.style.overflow = '';
        });
    }
  });

  // ---------------------------------------------------------------- Navbar
  document.addEventListener('click', function (e) {
    const toggle = e.target.closest('[data-nav-toggle]');
    if (toggle) {
      const nav = toggle.closest('.navbar-glass');
      if (nav) nav.classList.toggle('open');
    }
  });

  // ---------------------------------------------------------------- Lucide
  // Small inline replacement so we don't pull the full Lucide JS bundle.
  // Usage: <i data-lucide="car" aria-hidden="true"></i>
  const ICONS = window.__LUCIDE_INLINE__ || {};

  function renderIcons(root) {
    (root || document).querySelectorAll('i[data-lucide]').forEach(function (el) {
      const name = el.getAttribute('data-lucide');
      const svg = ICONS[name];
      if (!svg) return;
      const size = el.getAttribute('data-size') || '18';
      const wrapper = document.createElement('span');
      wrapper.style.display = 'inline-flex';
      wrapper.style.alignItems = 'center';
      wrapper.style.justifyContent = 'center';
      wrapper.style.width = size + 'px';
      wrapper.style.height = size + 'px';
      wrapper.innerHTML = svg
        .replace('width="24"', 'width="' + size + '"')
        .replace('height="24"', 'height="' + size + '"');
      el.replaceWith(wrapper);
    });
  }
  window.renderIcons = renderIcons;
  document.addEventListener('DOMContentLoaded', function () { renderIcons(); });

  // ---------------------------------------------------------------- Helpers
  window.formatINR = function (n) {
    n = Number(n || 0);
    const whole = Math.floor(n);
    const frac = Math.round((n - whole) * 100);
    const s = String(whole);
    let head = s, tail = '';
    if (s.length > 3) {
      head = s.slice(0, -3);
      tail = s.slice(-3);
      const parts = [];
      while (head.length > 2) {
        parts.unshift(head.slice(-2));
        head = head.slice(0, -2);
      }
      if (head) parts.unshift(head);
      head = parts.join(',');
    } else {
      head = s;
    }
    return '\u20b9' + head + (tail ? ',' + tail : '') +
           '.' + String(frac).padStart(2, '0');
  };

  window.debounce = function (fn, ms) {
    let t;
    return function () {
      const args = arguments, ctx = this;
      clearTimeout(t);
      t = setTimeout(function () { fn.apply(ctx, args); }, ms || 250);
    };
  };

  // ---------------------------------------------------------------- Demo social buttons
  document.addEventListener('click', function (e) {
    const btn = e.target.closest('[data-social]');
    if (!btn) return;
    e.preventDefault();
    const name = btn.getAttribute('data-social');
    window.toast(name + ' sign-in is not enabled in this demo.', 'info');
  });
})();