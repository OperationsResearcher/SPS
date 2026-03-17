/**
 * Stratejik Planlama Akışı - Statik sayfa
 * Son güncelleme zamanı ve otomatik yenileme (30 sn)
 */
(function () {
  'use strict';

  function byId(id) {
    return document.getElementById(id);
  }

  function formatTime(date) {
    return date.toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  }

  function init() {
    var lastUpdateEl = byId('lastUpdateTime');
    if (lastUpdateEl) {
      lastUpdateEl.textContent = formatTime(new Date());
    }

    var updateManual = byId('updateManual');
    var updateAuto = byId('updateAuto');
    var configEl = document.getElementById('strategyFlowConfig');
    var refreshUrl = configEl ? configEl.getAttribute('data-strategy-flow-config') : null;

    var refreshInterval = null;

    function startAutoRefresh() {
      if (refreshInterval) return;
      refreshInterval = setInterval(function () {
        if (refreshUrl) {
          window.location.reload();
        }
      }, 30000);
    }

    function stopAutoRefresh() {
      if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
      }
    }

    if (updateManual) {
      updateManual.addEventListener('change', function () {
        if (updateManual.checked) {
          stopAutoRefresh();
          if (lastUpdateEl) lastUpdateEl.textContent = formatTime(new Date());
        }
      });
    }

    if (updateAuto) {
      updateAuto.addEventListener('change', function () {
        if (updateAuto.checked) {
          startAutoRefresh();
        } else {
          stopAutoRefresh();
        }
      });
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
