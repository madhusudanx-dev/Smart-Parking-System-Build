/* ===========================================================================
   Inline Lucide-style icons.
   Each entry is an SVG string with the standard 24x24 viewBox.
   app.js replaces <i data-lucide="name"></i> with the matching SVG.
   Only icons actually used in the project are included, to keep the bundle
   small enough for a mid-range phone.
   =========================================================================== */

(function () {
  'use strict';

  var S = function (paths) {
    return '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" ' +
           'viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
           'stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">' +
           paths + '</svg>';
  };

  window.__LUCIDE_INLINE__ = {
    'square-parking':  S('<rect x="3" y="3" width="18" height="18" rx="3"/><path d="M9 17V7h4a3 3 0 0 1 0 6H9"/>'),
    'car':             S('<path d="M19 17h2v-4l-2-5H5L3 13v4h2"/><circle cx="7" cy="17" r="2"/><circle cx="17" cy="17" r="2"/>'),
    'zap':             S('<polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>'),
    'shield-check':    S('<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 11 14 15 10"/>'),
    'check-circle-2':  S('<circle cx="12" cy="12" r="9"/><path d="m8 12 3 3 5-6"/>'),
    'clock-4':         S('<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>'),
    'ban':             S('<circle cx="12" cy="12" r="9"/><path d="m5.5 5.5 13 13"/>'),
    'calendar':        S('<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 11h18"/>'),
    'map-pin':         S('<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/>'),
    'wallet':          S('<path d="M20 7H5a2 2 0 0 1 0-4h13v4"/><path d="M3 7v12a2 2 0 0 0 2 2h16v-9H8"/><circle cx="17" cy="15" r="1.2"/>'),
    'ticket':          S('<path d="M4 8a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v2a2 2 0 0 0 0 4v2a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-2a2 2 0 0 0 0-4V8z"/><path d="M13 6v12" stroke-dasharray="2 2"/>'),
    'user':            S('<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>'),
    'log-out':         S('<path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/><polyline points="10 17 15 12 10 7"/><line x1="15" y1="12" x2="3" y2="12"/>'),
    'log-in':          S('<path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/><polyline points="10 17 15 12 10 7"/><line x1="3" y1="12" x2="15" y2="12"/>'),
    'menu':            S('<line x1="4" y1="7" x2="20" y2="7"/><line x1="4" y1="12" x2="20" y2="12"/><line x1="4" y1="17" x2="20" y2="17"/>'),
    'info':            S('<circle cx="12" cy="12" r="9"/><line x1="12" y1="11" x2="12" y2="16"/><circle cx="12" cy="8" r="0.6" fill="currentColor"/>'),
    'alert-circle':    S('<circle cx="12" cy="12" r="9"/><line x1="12" y1="8" x2="12" y2="13"/><circle cx="12" cy="16.5" r="0.7" fill="currentColor"/>'),
    'alert-triangle':  S('<path d="M10.3 3.9 2.4 18a2 2 0 0 0 1.7 3h15.8a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/><line x1="12" y1="9" x2="12" y2="14"/><circle cx="12" cy="17" r="0.7" fill="currentColor"/>'),
    'siren':           S('<path d="M7 18v-5a5 5 0 0 1 10 0v5"/><path d="M5 18h14a1 1 0 0 1 1 1v1H4v-1a1 1 0 0 1 1-1z"/><path d="M12 3v2M4.5 6.5l1.4 1.4M19.5 6.5l-1.4 1.4"/>'),
    'battery-charging':S('<rect x="2" y="7" width="16" height="10" rx="2"/><path d="M22 10v4"/><polyline points="11 9 8 13 11 13 9 17 13 12 10 12 11 9"/>'),
    'arrow-right':     S('<line x1="4" y1="12" x2="20" y2="12"/><polyline points="14 6 20 12 14 18"/>'),
    'arrow-left':      S('<line x1="20" y1="12" x2="4" y2="12"/><polyline points="10 6 4 12 10 18"/>'),
    'plus':            S('<line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>'),
    'pencil':          S('<path d="m4 20 4-1 11-11-3-3L5 16l-1 4z"/>'),
    'trash-2':         S('<polyline points="4 7 20 7"/><path d="M9 7V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2"/><path d="M6 7l1 12a2 2 0 0 0 2 2h6a2 2 0 0 0 2-2l1-12"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/>'),
    'download':        S('<path d="M12 3v12"/><polyline points="7 10 12 15 17 10"/><path d="M5 21h14"/>'),
    'printer':         S('<path d="M7 8V3h10v5"/><rect x="3" y="8" width="18" height="8" rx="2"/><path d="M7 16h10v5H7z"/>'),
    'filter':          S('<polygon points="3 4 21 4 14 12 14 20 10 18 10 12 3 4"/>'),
    'search':          S('<circle cx="11" cy="11" r="7"/><line x1="20" y1="20" x2="16.5" y2="16.5"/>'),
    'chevron-right':   S('<polyline points="9 6 15 12 9 18"/>'),
    'chevron-down':    S('<polyline points="6 9 12 15 18 9"/>'),
    'x':               S('<line x1="6" y1="6" x2="18" y2="18"/><line x1="18" y1="6" x2="6" y2="18"/>'),
    'check':           S('<polyline points="4 12 10 18 20 6"/>'),
    'external-link':   S('<path d="M14 4h6v6"/><path d="M20 4 10 14"/><path d="M20 14v4a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h4"/>'),
    'layout-dashboard':S('<rect x="3" y="3" width="8" height="8" rx="2"/><rect x="13" y="3" width="8" height="5" rx="2"/><rect x="13" y="10" width="8" height="11" rx="2"/><rect x="3" y="13" width="8" height="8" rx="2"/>'),
    'bar-chart':       S('<line x1="4" y1="20" x2="20" y2="20"/><rect x="6"  y="12" width="3" height="8"/><rect x="11" y="7"  width="3" height="13"/><rect x="16" y="4"  width="3" height="16"/>'),
    'list':            S('<line x1="8" y1="6" x2="20" y2="6"/><line x1="8" y1="12" x2="20" y2="12"/><line x1="8" y1="18" x2="20" y2="18"/><circle cx="4" cy="6" r="1"/><circle cx="4" cy="12" r="1"/><circle cx="4" cy="18" r="1"/>'),
    'settings':        S('<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.9l.1.1a2 2 0 0 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.9-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 0 1-4 0v-.1A1.7 1.7 0 0 0 9 19.4a1.7 1.7 0 0 0-1.9.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.9 1.7 1.7 0 0 0-1.5-1H3a2 2 0 0 1 0-4h.1A1.7 1.7 0 0 0 4.6 9a1.7 1.7 0 0 0-.3-1.9l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.9.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 0 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.9-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.9V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 0 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/>'),
    'door-open':       S('<path d="M4 21V5a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v16"/><line x1="3" y1="21" x2="21" y2="21"/><path d="M17 21V9l3 2v10"/>'),
    'refresh-cw':      S('<polyline points="21 4 21 10 15 10"/><polyline points="3 20 3 14 9 14"/><path d="M20.5 15A8 8 0 0 1 5 20l-2-2M3.5 9A8 8 0 0 1 19 4l2 2"/>'),
    'qr-code':         S('<rect x="3" y="3" width="6" height="6" rx="1"/><rect x="15" y="3" width="6" height="6" rx="1"/><rect x="3" y="15" width="6" height="6" rx="1"/><line x1="15" y1="15" x2="21" y2="21"/><line x1="15" y1="21" x2="21" y2="15"/>'),
    'bell':            S('<path d="M6 8a6 6 0 1 1 12 0v5l2 3H4l2-3V8z"/><path d="M10 19a2 2 0 0 0 4 0"/>'),
    'credit-card':     S('<rect x="3" y="6" width="18" height="12" rx="2"/><line x1="3" y1="10" x2="21" y2="10"/>'),
    'smartphone':      S('<rect x="7" y="2" width="10" height="20" rx="2"/><circle cx="12" cy="18" r="0.8" fill="currentColor"/>'),
    'history':         S('<path d="M3 12a9 9 0 1 0 3-6.7"/><polyline points="3 4 3 10 9 10"/><line x1="12" y1="7" x2="12" y2="12"/><line x1="12" y1="12" x2="15" y2="14"/>'),
    'shield-alert':    S('<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><line x1="12" y1="8" x2="12" y2="13"/><circle cx="12" cy="16" r="0.7" fill="currentColor"/>'),
    'eye':             S('<path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12z"/><circle cx="12" cy="12" r="3"/>'),
    'arrow-up-right':  S('<line x1="7" y1="17" x2="17" y2="7"/><polyline points="8 7 17 7 17 16"/>'),
    'arrow-down-right':S('<line x1="7" y1="7" x2="17" y2="17"/><polyline points="17 8 17 17 8 17"/>')
  };
})();