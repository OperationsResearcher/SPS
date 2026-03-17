/**
 * DASHBOARD BUILDER COMPONENT
 * Sprint 10-12: Analytics ve Raporlama
 * Özelleştirilebilir dashboard oluşturucu
 */

const DashboardBuilder = {
    data() {
        return {
            widgets: [],
            availableWidgets: [
                { type: 'kpi-card', name: 'KPI Kartı', icon: '📊' },
                { type: 'trend-chart', name: 'Trend Grafiği', icon: '📈' },
                { type: 'performance-table', name: 'Performans Tablosu', icon: '📋' },
                { type: 'process-health', name: 'Süreç Sağlık Skoru', icon: '❤️' },
                { type: 'comparison-chart', name: 'Karşılaştırma Grafiği', icon: '📊' },
                { type: 'forecast-chart', name: 'Tahmin Grafiği', icon: '🔮' }
            ],
            editMode: false,
            selectedWidget: null
        };
    },
    
    mounted() {
        this.loadDashboard();
        this.initGridster();
    },
    
    methods: {
        async loadDashboard() {
            try {
                const response = await fetch('/api/dashboard/layout');
                const data = await response.json();
                this.widgets = data.widgets || [];
            } catch (error) {
                console.error('Load dashboard error:', error);
            }
        },
        
        initGridster() {
            // Gridster.js ile drag & drop grid
            this.$nextTick(() => {
                $('.gridster ul').gridster({
                    widget_margins: [10, 10],
                    widget_base_dimensions: [140, 140],
                    draggable: {
                        enabled: this.editMode,
                        handle: '.widget-header'
                    },
                    resize: {
                        enabled: this.editMode
                    },
                    serialize_params: ($w, wgd) => {
                        return {
                            id: $w.attr('data-widget-id'),
                            col: wgd.col,
                            row: wgd.row,
                            size_x: wgd.size_x,
                            size_y: wgd.size_y
                        };
                    }
                });
            });
        },
        
        toggleEditMode() {
            this.editMode = !this.editMode;
            
            if (this.editMode) {
                $('.gridster ul').data('gridster').enable();
            } else {
                $('.gridster ul').data('gridster').disable();
                this.saveDashboard();
            }
        },
        
        addWidget(widgetType) {
            const widget = {
                id: Date.now(),
                type: widgetType.type,
                name: widgetType.name,
                config: {},
                col: 1,
                row: 1,
                size_x: 2,
                size_y: 2
            };
            
            this.widgets.push(widget);
            this.selectedWidget = widget;
            this.showWidgetConfig();
        },
        
        removeWidget(widgetId) {
            this.widgets = this.widgets.filter(w => w.id !== widgetId);
            this.saveDashboard();
        },
        
        showWidgetConfig() {
            // Widget konfigürasyon modal'ını göster
            $('#widgetConfigModal').modal('show');
        },
        
        async saveDashboard() {
            try {
                const layout = $('.gridster ul').data('gridster').serialize();
                
                const response = await fetch('/api/dashboard/layout', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.content
                    },
                    body: JSON.stringify({
                        widgets: this.widgets,
                        layout: layout
                    })
                });
                
                if (response.ok) {
                    this.showSuccess('Dashboard kaydedildi');
                }
            } catch (error) {
                console.error('Save dashboard error:', error);
                this.showError('Dashboard kaydedilemedi');
            }
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
    
    template: `
        <div class="dashboard-builder">
            <div class="dashboard-toolbar">
                <button @click="toggleEditMode" class="btn btn-primary">
                    <i class="fas" :class="editMode ? 'fa-save' : 'fa-edit'"></i>
                    {{ editMode ? 'Kaydet' : 'Düzenle' }}
                </button>
                
                <div v-if="editMode" class="widget-palette">
                    <button 
                        v-for="widget in availableWidgets" 
                        :key="widget.type"
                        @click="addWidget(widget)"
                        class="btn btn-outline-secondary btn-sm">
                        {{ widget.icon }} {{ widget.name }}
                    </button>
                </div>
            </div>
            
            <div class="gridster">
                <ul>
                    <li v-for="widget in widgets" 
                        :key="widget.id"
                        :data-widget-id="widget.id"
                        :data-row="widget.row"
                        :data-col="widget.col"
                        :data-sizex="widget.size_x"
                        :data-sizey="widget.size_y">
                        
                        <div class="widget-container">
                            <div class="widget-header">
                                <span class="widget-title">{{ widget.name }}</span>
                                <button v-if="editMode" 
                                        @click="removeWidget(widget.id)"
                                        class="btn-remove">
                                    <i class="fas fa-times"></i>
                                </button>
                            </div>
                            
                            <div class="widget-content">
                                <component 
                                    :is="widget.type" 
                                    :config="widget.config">
                                </component>
                            </div>
                        </div>
                    </li>
                </ul>
            </div>
        </div>
    `
};

// Widget Components
const KpiCardWidget = {
    props: ['config'],
    template: `
        <div class="kpi-widget">
            <div class="kpi-value">{{ config.value || '0' }}</div>
            <div class="kpi-label">{{ config.label || 'KPI' }}</div>
        </div>
    `
};

const TrendChartWidget = {
    props: ['config'],
    mounted() {
        this.renderChart();
    },
    methods: {
        renderChart() {
            // Chart.js ile grafik çiz
            const ctx = this.$refs.canvas.getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: this.config.data || { labels: [], datasets: [] },
                options: {
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        }
    },
    template: `
        <div class="chart-widget">
            <canvas ref="canvas"></canvas>
        </div>
    `
};

// Export
window.DashboardBuilder = DashboardBuilder;
window.KpiCardWidget = KpiCardWidget;
window.TrendChartWidget = TrendChartWidget;
