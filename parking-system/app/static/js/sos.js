/* ===========================================================================
   SOS button flow: confirm sheet -> POST /sos -> toast.
   Used on the ticket page and on Women's Safety booking pages.
   =========================================================================== */

(function () {
  'use strict';

  document.addEventListener('click', function (e) {
    var trigger = e.target.closest('[data-sos-open]');
    if (trigger) {
      e.preventDefault();
      window.openModal('sos-modal');
      var slotField = document.getElementById('sos-slot-id');
      var bkField   = document.getElementById('sos-booking-id');
      if (slotField) slotField.value = trigger.getAttribute('data-slot-id') || '';
      if (bkField)   bkField.value   = trigger.getAttribute('data-booking-id') || '';
      return;
    }

    var send = e.target.closest('[data-sos-send]');
    if (send) {
      var form = document.getElementById('sos-form');
      if (!form) return;
      send.disabled = true;
      send.textContent = 'Sending\u2026';
      fetch('/sos', {
        method: 'POST',
        body: new FormData(form)
      }).then(function (r) {
        window.closeModal('sos-modal');
        if (r.redirected || r.ok) {
          window.toast('Security has been alerted. Help is on the way.', 'ok');
          // Reload so the flash message and the open-alert state show up.
          setTimeout(function () { window.location.reload(); }, 900);
        } else {
          window.toast('We could not send the alert. Please try again.', 'err');
          send.disabled = false;
          send.textContent = 'Send alert';
        }
      }).catch(function () {
        window.toast('Network problem. Please try again.', 'err');
        send.disabled = false;
        send.textContent = 'Send alert';
      });
    }
  });
})();