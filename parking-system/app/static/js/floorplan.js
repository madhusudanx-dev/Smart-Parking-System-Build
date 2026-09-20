/* ===========================================================================
   Live slot map.  Renders slots from /api/slots onto an SVG, polls every 5s,
   applies filters and reports slot selection.
   =========================================================================== */

(function () {
  'use strict';

  var SVG_NS = 'http://www.w3.org/2000/svg';
  var state = {
    root: null,
    levelId: null,
    slots: [],
    filter: 'all',
    selectedId: null,
    timer: null,
    interactive: true
  };

  function el(tag, attrs) {
    var e = document.createElementNS(SVG_NS, tag);
    if (attrs) Object.keys(attrs).forEach(function (k) {
      e.setAttribute(k, attrs[k]);
    });
    return e;
  }

  // --------------- SVG mini-icons for tile corners ---------------
  function iconPaths(type) {
    if (type === 'ev') {
      return 'M13 2 3 14 12 14 11 22 21 10 12 10 13 2';
    }
    if (type === 'women') {
      return 'M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z ' +
             'M9 12l2 2 4-4';
    }
    return '';
  }

  function renderSlot(s) {
    var g = el('g', {
      'class': 'fp-slot ' + s.status +
               (s.slot_type !== 'standard' ? ' ' + s.slot_type : ''),
      'data-id': s.id,
      'data-type': s.slot_type,
      'data-code': s.code,
      'data-status': s.status,
      'tabindex': state.interactive ? '0' : '-1',
      'role': 'button',
      'aria-label': s.code + ', ' + s.slot_type + ' slot, ' + s.status
    });
    g.style.color = '';

    var x = s.pos_x, y = s.pos_y, w = 100, h = 66;

    // Rounded tile
    g.appendChild(el('rect', {
      x: x, y: y, width: w, height: h, rx: 12,
      'class': 'tile'
    }));

    // Icon (EV / women) in the top-left corner
    var ip = iconPaths(s.slot_type);
    if (ip) {
      var icon = el('path', {
        d: ip,
        transform: 'translate(' + (x + 10) + ',' + (y + 8) +
                   ') scale(0.55)',
        fill: 'none',
        stroke: 'currentColor',
        'stroke-width': 2.2,
        'stroke-linecap': 'round',
        'stroke-linejoin': 'round'
      });
      g.appendChild(icon);
    }

    // Slot code text
    var code = el('text', {
      x: x + w / 2, y: y + h / 2 - 4, 'class': 'code',
      'font-size': 13
    });
    code.textContent = s.code;
    g.appendChild(code);

    // State word (so it's not colour-only)
    var word = el('text', {
      x: x + w / 2, y: y + h / 2 + 12, 'class': 'type-label'
    });
    word.textContent = s.status.toUpperCase();
    g.appendChild(word);

    if (state.interactive) {
      g.addEventListener('click', function () { select(s); });
      g.addEventListener('keydown', function (ev) {
        if (ev.key === 'Enter' || ev.key === ' ') {
          ev.preventDefault();
          select(s);
        }
      });
    }
    return g;
  }

  function select(s) {
    if (s.status !== 'available') {
      window.toast(s.code + ' is ' + s.status + '. Pick a green slot.', 'info');
      return;
    }
    state.selectedId = s.id;
    // Redraw highlight
    state.root.querySelectorAll('.fp-slot').forEach(function (n) {
      n.classList.toggle('selected', Number(n.dataset.id) === s.id);
    });
    // Notify listeners (book page)
    document.dispatchEvent(new CustomEvent('slot:selected', { detail: s }));
  }

  function paint() {
    var layer = state.root.querySelector('[data-slot-layer]');
    layer.innerHTML = '';
    state.slots.forEach(function (s) {
      var node = renderSlot(s);
      if (state.selectedId === s.id) node.classList.add('selected');
      if (state.filter !== 'all' && s.slot_type !== state.filter) {
        node.classList.add('dim');
      }
      layer.appendChild(node);
    });
  }

  async function load() {
    if (!state.levelId) return;
    try {
      var r = await fetch('/api/slots?level_id=' + state.levelId, {
        headers: { 'Accept': 'application/json' }
      });
      if (!r.ok) throw new Error('bad status');
      var data = await r.json();
      state.slots = data.slots || [];
      paint();
    } catch (e) {
      // Silent: we'll try again on the next tick.
    }
  }

  function init(container) {
    state.root = container;
    state.interactive = container.dataset.interactive !== '0';

    // Level tabs
    var levelButtons = container.parentElement.querySelectorAll('[data-level]');
    if (levelButtons.length) {
      state.levelId = Number(levelButtons[0].dataset.level);
      levelButtons.forEach(function (btn) {
        btn.addEventListener('click', function () {
          levelButtons.forEach(function (b) {
            b.classList.remove('active');
            b.setAttribute('aria-selected', 'false');
          });
          btn.classList.add('active');
          btn.setAttribute('aria-selected', 'true');
          state.levelId = Number(btn.dataset.level);
          state.selectedId = null;
          load();
        });
      });
    } else {
      state.levelId = Number(container.dataset.level || 1);
    }

    // Filters
    container.parentElement.querySelectorAll('[data-filter]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        container.parentElement.querySelectorAll('[data-filter]').forEach(function (b) {
          b.classList.remove('active');
          b.setAttribute('aria-selected', 'false');
        });
        btn.classList.add('active');
        btn.setAttribute('aria-selected', 'true');
        state.filter = btn.dataset.filter;
        paint();
      });
    });

    // Kick off polling
    load();
    if (state.timer) clearInterval(state.timer);
    state.timer = setInterval(load, 5000);

    document.addEventListener('visibilitychange', function () {
      if (document.hidden) {
        clearInterval(state.timer);
      } else {
        load();
        state.timer = setInterval(load, 5000);
      }
    });
  }

  window.Floorplan = { init: init, refresh: load };
  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.floorplan[data-live="1"]').forEach(init);
  });
})();