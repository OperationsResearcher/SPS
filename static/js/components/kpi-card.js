/**
 * KPI CARD COMPONENT
 * Sprint 1-2: Frontend Modernizasyonu
 * Modern KPI kartı Vue component'i
 */

const KpiCard = {
    props: {
        kpi: {
            type: Object,
            required: true
        },
        editable: {
            type: Boolean,
            default: false
        }
    },
    
    data() {
        return {
            editing: false,
            localValue: this.kpi.actual_value
        };
    },
    
    computed: {
        performance() {
            if (!this.kpi.target_value || this.kpi.target_value === 0) return 0;
            return (this.kpi.actual_value / this.kpi.target_value) * 100;
        },
        
        statusClass() {
            if (this.performance >= 100) return 'success';
            if (this.performance >= 80) return 'warning';
            return 'danger';
        },
        
        statusIcon() {
            if (this.performance >= 100) return '✅';
            if (this.performance >= 80) return '⚠️';
            return '❌';
        },
        
        trend() {
            // Basit trend hesaplama (gerçek implementasyonda geçmiş verilerle karşılaştırılmalı)
            const diff = this.kpi.actual_value - (this.kpi.previous_value || 0);
            if (diff > 0) return { direction: 'up', value: diff, class: 'trend-up' };
            if (diff < 0) return { direction: 'down', value: Math.abs(diff), class: 'trend-down' };
            return { direction: 'neutral', value: 0, class: 'trend-neutral' };
        }
    },

    
    methods: {
        async updateValue() {
            if (!this.editable) return;
            
            try {
                await this.$emit('update', {
                    kpiId: this.kpi.id,
                    field: 'actual_value',
                    value: this.localValue
                });
                this.editing = false;
            } catch (error) {
                this.localValue = this.kpi.actual_value;
            }
        },
        
        startEdit() {
            if (this.editable) {
                this.editing = true;
                this.$nextTick(() => {
                    this.$refs.valueInput?.focus();
                });
            }
        },
        
        cancelEdit() {
            this.editing = false;
            this.localValue = this.kpi.actual_value;
        }
    },
    
    template: `
        <div class="kpi-card">
            <div class="kpi-header">
                <span class="kpi-code">{{ kpi.code }}</span>
                <span class="kpi-status" :class="'status-' + statusClass">{{ statusIcon }}</span>
            </div>
            
            <h3 class="kpi-title">{{ kpi.name }}</h3>
            
            <div class="kpi-metrics">
                <div class="metric-primary">
                    <div class="metric-value" @click="startEdit" :class="{ 'editable': editable }">
                        <template v-if="!editing">
                            {{ kpi.actual_value }}<span class="unit">{{ kpi.unit }}</span>
                        </template>
                        <input 
                            v-else
                            ref="valueInput"
                            v-model.number="localValue"
                            @blur="updateValue"
                            @keyup.enter="updateValue"
                            @keyup.esc="cancelEdit"
                            type="number"
                            class="form-control"
                        />
                    </div>
                    <div class="metric-label">Gerçekleşen</div>
                </div>
                
                <div class="metric-secondary">
                    <div class="metric-value">
                        {{ kpi.target_value }}<span class="unit">{{ kpi.unit }}</span>
                    </div>
                    <div class="metric-label">Hedef</div>
                </div>
            </div>
            
            <div class="kpi-progress">
                <div class="progress-bar" 
                     :class="statusClass" 
                     :style="{ width: Math.min(performance, 100) + '%' }">
                </div>
            </div>
            
            <div class="kpi-footer">
                <span class="trend" :class="trend.class">
                    {{ trend.value > 0 ? '+' : '' }}{{ trend.value }}{{ kpi.unit }}
                    {{ trend.direction === 'up' ? '↗' : trend.direction === 'down' ? '↘' : '→' }}
                </span>
                <span class="last-update">{{ formatDate(kpi.last_update) }}</span>
            </div>
        </div>
    `
};

// Export
window.KpiCard = KpiCard;
