/**
 * Offline page - Auto-retry when online
 */
(function () {
  'use strict';

  function retry() {
    window.location.reload();
  }

  window.addEventListener('online', retry);

  setInterval(function () {
    if (navigator.onLine) {
      retry();
    }
  }, 5000);

  var btn = document.getElementById('retryBtn');
  if (btn) {
    btn.addEventListener('click', retry);
  }
})();
