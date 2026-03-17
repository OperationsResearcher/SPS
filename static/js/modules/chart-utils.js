/**
 * CHART UTILITIES
 * Sprint 10-12: Analytics ve Raporlama
 * Chart.js helper fonksiyonları
 */

class ChartUtils {
    /**
     * Trend grafiği oluştur
     */
    static createTrendChart(canvasId, data, options = {}) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        
        const defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value + (options.unit || '');
                        }
                    }
                }
            }
        };
        
        return new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.dates || [],
                datasets: [
                    {
                        label: 'Gerçekleşen',
                        data: data.actual_values || [],
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Hedef',
                        data: data.target_values || [],
                        borderColor: '#10b981',
                        backgroundColor: 'rgba(16, 185, 129, 0.1)',
                        borderDash: [5, 5],
                        tension: 0.4
                    }
                ]
            },
            options: { ...defaultOptions, ...options }
        });
    }
    
    /**
     * Performans bar chart
     */
    static createPerformanceChart(canvasId, data, options = {}) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        
        return new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels || [],
                datasets: [{
                    label: 'Performans (%)',
                    data: data.values || [],
                    backgroundColor: data.values.map(v => 
                        v >= 100 ? '#10b981' : 
                        v >= 90 ? '#3b82f6' : 
                        v >= 80 ? '#f59e0b' : '#ef4444'
                    ),
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 120,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                },
                ...options
            }
        });
    }
    
    /**
     * Karşılaştırma radar chart
     */
    static createComparisonChart(canvasId, data, options = {}) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        
        return new Chart(ctx, {
            type: 'radar',
            data: {
                labels: data.labels || [],
                datasets: data.datasets || []
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100
                    }
                },
                ...options
            }
        });
    }
    
    /**
     * Doughnut chart (süreç dağılımı)
     */
    static createDoughnutChart(canvasId, data, options = {}) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        
        return new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.labels || [],
                datasets: [{
                    data: data.values || [],
                    backgroundColor: [
                        '#3b82f6',
                        '#10b981',
                        '#f59e0b',
                        '#ef4444',
                        '#8b5cf6',
                        '#ec4899'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right'
                    }
                },
                ...options
            }
        });
    }
    
    /**
     * Forecast chart (tahmin grafiği)
     */
    static createForecastChart(canvasId, historicalData, forecastData, options = {}) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        
        return new Chart(ctx, {
            type: 'line',
            data: {
                labels: [...historicalData.dates, ...forecastData.dates],
                datasets: [
                    {
                        label: 'Geçmiş Veri',
                        data: [...historicalData.values, ...Array(forecastData.values.length).fill(null)],
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        tension: 0.4
                    },
                    {
                        label: 'Tahmin',
                        data: [...Array(historicalData.values.length).fill(null), ...forecastData.values],
                        borderColor: '#f59e0b',
                        backgroundColor: 'rgba(245, 158, 11, 0.1)',
                        borderDash: [5, 5],
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true
                    }
                },
                ...options
            }
        });
    }
    
    /**
     * Heatmap (performans ısı haritası)
     */
    static createHeatmap(containerId, data) {
        const container = document.getElementById(containerId);
        
        let html = '<div class="heatmap-grid">';
        
        data.forEach(row => {
            html += '<div class="heatmap-row">';
            row.values.forEach(value => {
                const color = this.getHeatmapColor(value);
                html += `<div class="heatmap-cell" style="background-color: ${color}" title="${value}%">${value}</div>`;
            });
            html += '</div>';
        });
        
        html += '</div>';
        container.innerHTML = html;
    }
    
    static getHeatmapColor(value) {
        if (value >= 100) return '#10b981';
        if (value >= 90) return '#3b82f6';
        if (value >= 80) return '#f59e0b';
        if (value >= 70) return '#f97316';
        return '#ef4444';
    }
    
    /**
     * Sparkline (mini grafik)
     */
    static createSparkline(canvasId, data) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        
        return new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map((_, i) => i),
                datasets: [{
                    data: data,
                    borderColor: '#3b82f6',
                    borderWidth: 2,
                    pointRadius: 0,
                    fill: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false }
                },
                scales: {
                    x: { display: false },
                    y: { display: false }
                }
            }
        });
    }
}

// Export
window.ChartUtils = ChartUtils;
