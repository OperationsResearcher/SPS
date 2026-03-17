/**
 * KPI Panel Modern - Vue app setup for KPI panel page
 */
(function () {
  'use strict';

  if (typeof Vue === 'undefined' || typeof window.vueApp === 'undefined') {
    return;
  }

  var base = window.vueApp;
  var kpiApp = {
    data: base.data,
    computed: base.computed,
    components: { 'kpi-card': window.KpiCard },
    methods: Object.assign({}, base.methods || {}, {
      handleKpiUpdate: async function (data) {
        try {
          await this.updateKpiData(data.kpiId, data.field, data.value);
          await this.loadKpis(this.selectedProcess.id);
        } catch (error) {
          console.error('KPI update failed:', error);
        }
      }
    }),
    async mounted() {
      if (window.loadingManager && window.loadingManager.showSkeleton) {
        window.loadingManager.showSkeleton('#kpi-skeleton', 'kpi-card', 6);
      }
      await this.loadProcesses();
      if (this.processes && this.processes.length > 0) {
        this.selectProcess(this.processes[0]);
      }
    }
  };

  var appEl = document.getElementById('app');
  if (appEl) {
    Vue.createApp(kpiApp).mount('#app');
  }
})();
