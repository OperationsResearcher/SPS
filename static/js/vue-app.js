/**
 * VUE.JS APPLICATION
 * Sprint 1-2: Frontend Modernizasyonu
 * Vue.js temel altyapı ve component'ler
 */

// Vue.js CDN üzerinden yüklenecek (base.html'de)

// Global Vue instance
const app = {
    data() {
        return {
            loading: false,
            processes: [],
            kpis: [],
            selectedProcess: null,
            filters: {
                search: '',
                status: 'all',
                strategy: 'all'
            }
        };
    },
    
    computed: {
        filteredProcesses() {
            let filtered = this.processes;
            
            if (this.filters.search) {
                const search = this.filters.search.toLowerCase();
                filtered = filtered.filter(p => 
                    p.name.toLowerCase().includes(search) ||
                    p.code.toLowerCase().includes(search)
                );
            }
            
            if (this.filters.status !== 'all') {
                filtered = filtered.filter(p => p.status === this.filters.status);
            }
            
            if (this.filters.strategy !== 'all') {
                filtered = filtered.filter(p => 
                    p.sub_strategies.some(s => s.id === parseInt(this.filters.strategy))
                );
            }
            
            return filtered;
        },
        
        filteredKpis() {
            if (!this.selectedProcess) return [];
            return this.kpis.filter(k => k.process_id === this.selectedProcess.id);
        }
    },
    
    methods: {
        async loadProcesses() {
            this.loading = true;
            try {
                const response = await fetch('/api/processes');
                const data = await response.json();
                this.processes = data.items || data;
            } catch (error) {
                console.error('Process yükleme hatası:', error);
                this.showError('Süreçler yüklenemedi');
            } finally {
                this.loading = false;
            }
        },

        
        async loadKpis(processId) {
            this.loading = true;
            try {
                const response = await fetch(`/api/processes/${processId}/kpis`);
                const data = await response.json();
                this.kpis = data.items || data;
            } catch (error) {
                console.error('KPI yükleme hatası:', error);
                this.showError('KPI\'lar yüklenemedi');
            } finally {
                this.loading = false;
            }
        },
        
        async updateKpiData(kpiId, field, value) {
            try {
                const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
                const response = await fetch(`/api/kpi-data/${kpiId}`, {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    body: JSON.stringify({ [field]: value })
                });
                
                if (!response.ok) throw new Error('Güncelleme başarısız');
                
                const data = await response.json();
                this.showSuccess('Kaydedildi');
                return data;
            } catch (error) {
                console.error('KPI güncelleme hatası:', error);
                this.showError('Kaydetme başarısız');
                throw error;
            }
        },
        
        selectProcess(process) {
            this.selectedProcess = process;
            this.loadKpis(process.id);
        },
        
        getStatusIcon(status) {
            const icons = {
                'success': '✅',
                'warning': '⚠️',
                'danger': '❌',
                'info': 'ℹ️'
            };
            return icons[status] || 'ℹ️';
        },
        
        getStatusClass(performance) {
            if (performance >= 100) return 'success';
            if (performance >= 80) return 'warning';
            return 'danger';
        },
        
        formatNumber(value, decimals = 2) {
            if (value === null || value === undefined) return '-';
            return parseFloat(value).toFixed(decimals);
        },
        
        formatDate(date) {
            if (!date) return '-';
            const d = new Date(date);
            const now = new Date();
            const diff = Math.floor((now - d) / (1000 * 60 * 60 * 24));
            
            if (diff === 0) return 'Bugün';
            if (diff === 1) return 'Dün';
            if (diff < 7) return `${diff} gün önce`;
            if (diff < 30) return `${Math.floor(diff / 7)} hafta önce`;
            return d.toLocaleDateString('tr-TR');
        },
        
        showSuccess(message) {
            if (window.Swal) {
                Swal.fire({
                    icon: 'success',
                    title: 'Başarılı',
                    text: message,
                    timer: 2000,
                    showConfirmButton: false
                });
            }
        },
        
        showError(message) {
            if (window.Swal) {
                Swal.fire({
                    icon: 'error',
                    title: 'Hata',
                    text: message
                });
            }
        }
    },
    
    mounted() {
        // Component mount olduğunda
        console.log('Vue app mounted');
    }
};

// Export
window.vueApp = app;
