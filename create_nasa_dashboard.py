# -*- coding: utf-8 -*-
"""
KURUM PANELİ - NASA SEVİYESİ GÖRSEL ŞOV
Apache ECharts ile interaktif, canlı, WOW faktörlü dashboard
"""

content = r'''{% extends "base.html" %}

{% block title %}Stratejik Yönetim Şovu - {{ kurum.kisa_ad if kurum else 'Kurum Paneli' }}{% endblock %}

{% block breadcrumb %}
<a href="{{ url_for('main.dashboard') }}" class="text-decoration-none text-muted">
    <i class="fas fa-home"></i> Ana Sayfa
</a>
<span class="mx-2">/</span>
<span class="text-dark">Stratejik Yönetim Şovu</span>
{% endblock %}

{% block content %}
<!-- SweetAlert2 -->
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/sweetalert2@11/dist/sweetalert2.min.css">
<script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>

<style>
    /* NASA Teması */
    body {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }

    .dashboard-container {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    }

    /* V3 Card Styles - Enhanced */
    .card-v3 {
        border: none;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
        border-radius: 16px;
        transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        overflow: hidden;
        position: relative;
    }

    .card-v3::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2, #f093fb, #4facfe);
        background-size: 300% 100%;
        animation: gradientShift 3s ease infinite;
    }

    @keyframes gradientShift {
        0%, 100% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
    }

    .card-v3:hover {
        transform: translateY(-8px) scale(1.02);
        box-shadow: 0 16px 48px rgba(102, 126, 234, 0.4);
    }

    .card-header-v3 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: 700;
        cursor: move;
        border-top-left-radius: 16px !important;
        border-top-right-radius: 16px !important;
        padding: 1.25rem 1.5rem;
        border: none;
        position: relative;
        overflow: hidden;
    }

    .card-header-v3::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 300%;
        height: 300%;
        background: radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 70%);
        transform: translate(-50%, -50%);
        opacity: 0;
        transition: opacity 0.3s;
    }

    .card-header-v3:hover::after {
        opacity: 1;
    }

    .card-header-v3 h5 {
        color: white !important;
        font-size: 1.1rem;
        margin-bottom: 0;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        letter-spacing: 0.5px;
    }

    .card-header-v3 .close-widget-btn {
        background-color: rgba(255, 255, 255, 0.2);
        color: white;
        border: 2px solid rgba(255, 255, 255, 0.3);
        width: 36px;
        height: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s;
        border-radius: 50%;
        backdrop-filter: blur(10px);
    }

    .card-header-v3 .close-widget-btn:hover {
        background-color: #e74c3c;
        border-color: #e74c3c;
        transform: rotate(180deg) scale(1.1);
    }

    .widget-id-badge {
        font-size: 0.75rem;
        font-weight: 800;
        padding: 0.4rem 0.8rem;
        border-radius: 12px;
        letter-spacing: 1px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border: 2px solid rgba(255, 255, 255, 0.5);
    }

    .chart-container {
        min-height: 450px;
        position: relative;
        padding: 1rem;
    }

    .sortable-ghost {
        opacity: 0.5;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: 3px dashed #ffffff;
        border-radius: 16px;
    }

    /* Glow Effect */
    .glow {
        animation: glow 2s ease-in-out infinite alternate;
    }

    @keyframes glow {
        from {
            box-shadow: 0 0 10px #667eea, 0 0 20px #667eea, 0 0 30px #667eea;
        }
        to {
            box-shadow: 0 0 20px #764ba2, 0 0 30px #764ba2, 0 0 40px #764ba2;
        }
    }

    /* Loading Animation */
    .loading-spinner {
        border: 4px solid rgba(102, 126, 234, 0.1);
        border-top: 4px solid #667eea;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        animation: spin 1s linear infinite;
        margin: 2rem auto;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    /* Mobil Responsive */
    @media (max-width: 768px) {
        .card-header-v3 h5 {
            font-size: 0.95rem;
        }
        
        .widget-id-badge {
            font-size: 0.65rem;
            padding: 0.3rem 0.6rem;
        }
        
        .chart-container {
            min-height: 300px;
        }
    }
</style>

<div class="dashboard-container">
    <!-- Header -->
    <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
            <h1 class="fw-bold mb-1" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                🚀 Stratejik Yönetim Şovu
            </h1>
            <p class="text-muted">NASA seviyesi görselleştirme - Sürükle, bırak, keşfet!</p>
        </div>
        <div class="dropdown">
            <button class="btn btn-lg glow" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border: none; border-radius: 12px; padding: 0.75rem 1.5rem;" type="button" id="widgetManagementBtn" data-bs-toggle="dropdown" aria-expanded="false">
                <i class="fas fa-rocket me-2"></i> Widget Kontrol
            </button>
            <ul class="dropdown-menu dropdown-menu-end shadow-lg" style="border-radius: 12px; border: none;" aria-labelledby="widgetManagementBtn">
                <li><h6 class="dropdown-header" style="color: #667eea;">Widget Görünürlüğü</h6></li>
                <li><a class="dropdown-item" href="javascript:void(0)" onclick="toggleWidget('widget-a')">
                    <i class="fas fa-sun me-2 text-warning"></i> Stratejik Güneş
                </a></li>
                <li><a class="dropdown-item" href="javascript:void(0)" onclick="toggleWidget('widget-b')">
                    <i class="fas fa-stream me-2 text-info"></i> Değer Akışı
                </a></li>
                <li><a class="dropdown-item" href="javascript:void(0)" onclick="toggleWidget('widget-c')">
                    <i class="fas fa-chart-line me-2 text-success"></i> Gelecek Simülasyonu
                </a></li>
                <li><a class="dropdown-item" href="javascript:void(0)" onclick="toggleWidget('widget-d')">
                    <i class="fas fa-globe me-2 text-primary"></i> Proje Galaksisi
                </a></li>
                <li><hr class="dropdown-divider"></li>
                <li><a class="dropdown-item text-primary fw-bold" href="javascript:void(0)" onclick="showAllWidgets()">
                    <i class="fas fa-eye me-2"></i> Tümünü Göster
                </a></li>
                <li><hr class="dropdown-divider"></li>
                <li><a class="dropdown-item text-danger fw-bold" href="javascript:void(0)" onclick="resetLayout()">
                    <i class="fas fa-undo me-2"></i> Sıfırla
                </a></li>
            </ul>
        </div>
    </div>

    <!-- Dashboard Grid -->
    <div id="dashboard-grid" class="row g-4">
        
        <!-- WIDGET A: STRATEJİK GÜNEŞ (Sunburst) -->
        <div class="col-lg-6 widget-wrapper" data-id="widget-a" id="widget-a-wrapper">
            <div class="card card-v3 h-100">
                <div class="card-header card-header-v3 d-flex justify-content-between align-items-center handle">
                    <h5><i class="fas fa-sun me-2"></i> Stratejik Güneş</h5>
                    <div class="d-flex align-items-center gap-2">
                        <span class="widget-id-badge">WIDGET-A</span>
                        <button class="btn btn-sm btn-light close-widget-btn" onclick="hideWidget('widget-a')">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
                <div class="card-body p-0">
                    <div id="sunburstChart" class="chart-container"></div>
                </div>
            </div>
        </div>

        <!-- WIDGET B: DEĞER AKIŞI (Sankey) -->
        <div class="col-lg-6 widget-wrapper" data-id="widget-b" id="widget-b-wrapper">
            <div class="card card-v3 h-100">
                <div class="card-header card-header-v3 d-flex justify-content-between align-items-center handle">
                    <h5><i class="fas fa-stream me-2"></i> Değer Akışı</h5>
                    <div class="d-flex align-items-center gap-2">
                        <span class="widget-id-badge">WIDGET-B</span>
                        <button class="btn btn-sm btn-light close-widget-btn" onclick="hideWidget('widget-b')">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
                <div class="card-body p-0">
                    <div id="sankeyChart" class="chart-container"></div>
                </div>
            </div>
        </div>

        <!-- WIDGET C: GELECEK SİMÜLASYONU (Predictive Line) -->
        <div class="col-lg-6 widget-wrapper" data-id="widget-c" id="widget-c-wrapper">
            <div class="card card-v3 h-100">
                <div class="card-header card-header-v3 d-flex justify-content-between align-items-center handle">
                    <h5><i class="fas fa-chart-line me-2"></i> Gelecek Simülasyonu</h5>
                    <div class="d-flex align-items-center gap-2">
                        <span class="widget-id-badge">WIDGET-C</span>
                        <button class="btn btn-sm btn-light close-widget-btn" onclick="hideWidget('widget-c')">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
                <div class="card-body p-0">
                    <div id="predictiveChart" class="chart-container"></div>
                </div>
            </div>
        </div>

        <!-- WIDGET D: PROJE GALAKSİSİ (Bubble/Scatter) -->
        <div class="col-lg-6 widget-wrapper" data-id="widget-d" id="widget-d-wrapper">
            <div class="card card-v3 h-100">
                <div class="card-header card-header-v3 d-flex justify-content-between align-items-center handle">
                    <h5><i class="fas fa-globe me-2"></i> Proje Galaksisi</h5>
                    <div class="d-flex align-items-center gap-2">
                        <span class="widget-id-badge">WIDGET-D</span>
                        <button class="btn btn-sm btn-light close-widget-btn" onclick="hideWidget('widget-d')">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                </div>
                <div class="card-body p-0">
                    <div id="galaxyChart" class="chart-container"></div>
                </div>
            </div>
        </div>

    </div>
</div>

<!-- Sortable.js CDN -->
<script src="https://cdn.jsdelivr.net/npm/sortablejs@latest/Sortable.min.js"></script>
<!-- Apache ECharts CDN -->
<script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>

<script>
// LocalStorage Keys
const STORAGE_KEYS = {
    visibility: 'kurum_panel_nasa_visibility',
    order: 'kurum_panel_nasa_order'
};

const ALL_WIDGETS = ['widget-a', 'widget-b', 'widget-c', 'widget-d'];

// Backend Data
const backendData = {
    globalScore: {{ global_score|default(0)|int }},
    bscDistribution: {{ bsc_distribution | tojson | safe }},
    strategicProgress: {{ strategic_progress | tojson | safe }},
    topProcesses: {{ top_processes | tojson | safe }},
    riskyProcesses: {{ risky_processes | tojson | safe }},
    projectImpact: {{ project_impact | tojson | safe }}
};

document.addEventListener("DOMContentLoaded", function() {
    console.log("🚀 NASA Seviyesi Dashboard Yükleniyor...");
    
    loadWidgetState();
    initSortable();
    initAllCharts();
});

// ============================================================
// DUMMY DATA GENERATORS
// ============================================================

function generateSunburstData() {
    const perspectives = ['Finansal', 'Müşteri', 'Süreç', 'Öğrenme'];
    const colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe'];
    
    const data = {
        name: 'VİZYON',
        children: perspectives.map((persp, idx) => ({
            name: persp,
            value: Math.floor(Math.random() * 50) + 30,
            itemStyle: { color: colors[idx] },
            children: Array.from({length: 4}, (_, i) => ({
                name: `Süreç ${idx+1}.${i+1}`,
                value: Math.floor(Math.random() * 20) + 10,
                itemStyle: { 
                    color: colors[idx],
                    opacity: 0.7 - (i * 0.1)
                }
            }))
        }))
    };
    
    return data;
}

function generateSankeyData() {
    const nodes = [
        {name: 'İnsan Gücü'},
        {name: 'Bütçe'},
        {name: 'Teknoloji'},
        {name: 'Proje A'},
        {name: 'Proje B'},
        {name: 'Proje C'},
        {name: 'Finansal Hedef'},
        {name: 'Müşteri Hedefi'},
        {name: 'Süreç İyileştirme'}
    ];
    
    const links = [
        {source: 'İnsan Gücü', target: 'Proje A', value: 30},
        {source: 'İnsan Gücü', target: 'Proje B', value: 25},
        {source: 'Bütçe', target: 'Proje A', value: 40},
        {source: 'Bütçe', target: 'Proje C', value: 35},
        {source: 'Teknoloji', target: 'Proje B', value: 20},
        {source: 'Teknoloji', target: 'Proje C', value: 15},
        {source: 'Proje A', target: 'Finansal Hedef', value: 50},
        {source: 'Proje A', target: 'Müşteri Hedefi', value: 20},
        {source: 'Proje B', target: 'Müşteri Hedefi', value: 30},
        {source: 'Proje B', target: 'Süreç İyileştirme', value: 15},
        {source: 'Proje C', target: 'Süreç İyileştirme', value: 35},
        {source: 'Proje C', target: 'Finansal Hedef', value: 15}
    ];
    
    return {nodes, links};
}

function generatePredictiveData() {
    const months = ['Tem', 'Ağu', 'Eyl', 'Eki', 'Kas', 'Ara', 'Oca', 'Şub', 'Mar', 'Nis', 'May', 'Haz'];
    const historical = [65, 68, 72, 70, 75, 78];
    const predicted = [80, 83, 85, 88, 90, 92];
    const upperBound = predicted.map(v => v + 5);
    const lowerBound = predicted.map(v => v - 5);
    
    return {
        months,
        historical,
        predicted,
        upperBound,
        lowerBound
    };
}

function generateGalaxyData() {
    const healthColors = {
        'Mükemmel': '#28a745',
        'İyi': '#17a2b8',
        'Dikkat': '#ffc107',
        'Kritik': '#dc3545'
    };
    
    const projects = [];
    const healthStates = Object.keys(healthColors);
    
    for (let i = 0; i < 20; i++) {
        const health = healthStates[Math.floor(Math.random() * healthStates.length)];
        projects.push({
            name: `Proje ${i+1}`,
            value: [
                Math.floor(Math.random() * 100), // Tamamlanma %
                Math.floor(Math.random() * 100), // Stratejik Önem
                Math.floor(Math.random() * 50) + 10, // Bütçe (baloncuk boyutu)
                health
            ]
        });
    }
    
    return {projects, healthColors};
}

// ============================================================
// ECHARTS INITIALIZATION
// ============================================================

function initAllCharts() {
    initSunburstChart();
    initSankeyChart();
    initPredictiveChart();
    initGalaxyChart();
}

function initSunburstChart() {
    const chart = echarts.init(document.getElementById('sunburstChart'));
    const data = generateSunburstData();
    
    const option = {
        tooltip: {
            trigger: 'item',
            formatter: '{b}: {c}'
        },
        series: [{
            type: 'sunburst',
            data: [data],
            radius: ['15%', '90%'],
            label: {
                rotate: 'radial',
                fontSize: 12,
                fontWeight: 'bold'
            },
            itemStyle: {
                borderWidth: 2,
                borderColor: '#fff'
            },
            emphasis: {
                focus: 'ancestor',
                itemStyle: {
                    shadowBlur: 20,
                    shadowColor: 'rgba(0, 0, 0, 0.5)'
                }
            },
            levels: [{}, {
                r0: '15%',
                r: '40%',
                label: {
                    rotate: 0,
                    fontSize: 14
                }
            }, {
                r0: '40%',
                r: '75%',
                label: {
                    fontSize: 10
                }
            }]
        }]
    };
    
    chart.setOption(option);
    window.addEventListener('resize', () => chart.resize());
}

function initSankeyChart() {
    const chart = echarts.init(document.getElementById('sankeyChart'));
    const {nodes, links} = generateSankeyData();
    
    const option = {
        tooltip: {
            trigger: 'item',
            triggerOn: 'mousemove'
        },
        series: [{
            type: 'sankey',
            layout: 'none',
            emphasis: {
                focus: 'adjacency'
            },
            data: nodes,
            links: links,
            lineStyle: {
                color: 'gradient',
                curveness: 0.5,
                opacity: 0.6
            },
            itemStyle: {
                borderWidth: 2,
                borderColor: '#fff'
            },
            label: {
                fontSize: 12,
                fontWeight: 'bold'
            }
        }]
    };
    
    chart.setOption(option);
    window.addEventListener('resize', () => chart.resize());
}

function initPredictiveChart() {
    const chart = echarts.init(document.getElementById('predictiveChart'));
    const {months, historical, predicted, upperBound, lowerBound} = generatePredictiveData();
    
    const option = {
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'cross'
            }
        },
        legend: {
            data: ['Geçmiş Veri', 'Tahmin', 'Güven Aralığı'],
            top: 10
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis: {
            type: 'category',
            data: months,
            boundaryGap: false
        },
        yAxis: {
            type: 'value',
            min: 50,
            max: 100
        },
        series: [
            {
                name: 'Geçmiş Veri',
                type: 'line',
                data: [...historical, null, null, null, null, null, null],
                lineStyle: {
                    width: 3,
                    color: '#667eea'
                },
                itemStyle: {
                    color: '#667eea'
                },
                smooth: true,
                animation: true,
                animationDuration: 2000
            },
            {
                name: 'Tahmin',
                type: 'line',
                data: [null, null, null, null, null, null, ...predicted],
                lineStyle: {
                    width: 3,
                    type: 'dashed',
                    color: '#f093fb'
                },
                itemStyle: {
                    color: '#f093fb'
                },
                smooth: true,
                animation: true,
                animationDuration: 2000,
                animationDelay: 500
            },
            {
                name: 'Güven Aralığı',
                type: 'line',
                data: [null, null, null, null, null, null, ...upperBound],
                lineStyle: {
                    opacity: 0
                },
                stack: 'confidence',
                symbol: 'none',
                areaStyle: {
                    color: 'rgba(240, 147, 251, 0.2)'
                }
            },
            {
                name: 'Güven Aralığı Alt',
                type: 'line',
                data: [null, null, null, null, null, null, ...lowerBound],
                lineStyle: {
                    opacity: 0
                },
                areaStyle: {
                    color: 'rgba(240, 147, 251, 0.2)'
                },
                stack: 'confidence',
                symbol: 'none'
            }
        ]
    };
    
    chart.setOption(option);
    window.addEventListener('resize', () => chart.resize());
}

function initGalaxyChart() {
    const chart = echarts.init(document.getElementById('galaxyChart'));
    const {projects, healthColors} = generateGalaxyData();
    
    const series = Object.keys(healthColors).map(health => ({
        name: health,
        type: 'scatter',
        data: projects.filter(p => p.value[3] === health).map(p => p.value.slice(0, 3)),
        symbolSize: function(val) {
            return val[2];
        },
        itemStyle: {
            color: healthColors[health],
            shadowBlur: 10,
            shadowColor: healthColors[health],
            shadowOffsetY: 5,
            opacity: 0.8
        },
        emphasis: {
            focus: 'series',
            itemStyle: {
                shadowBlur: 20,
                shadowColor: healthColors[health]
            }
        }
    }));
    
    const option = {
        backgroundColor: 'transparent',
        tooltip: {
            trigger: 'item',
            formatter: function(params) {
                return `<strong>${params.seriesName}</strong><br/>
                        Tamamlanma: ${params.value[0]}%<br/>
                        Stratejik Önem: ${params.value[1]}<br/>
                        Bütçe: ${params.value[2]}M`;
            }
        },
        legend: {
            data: Object.keys(healthColors),
            top: 10
        },
        grid: {
            left: '8%',
            right: '8%',
            bottom: '8%',
            top: '15%'
        },
        xAxis: {
            name: 'Tamamlanma %',
            nameLocation: 'middle',
            nameGap: 30,
            splitLine: {
                lineStyle: {
                    type: 'dashed',
                    opacity: 0.2
                }
            }
        },
        yAxis: {
            name: 'Stratejik Önem',
            nameLocation: 'middle',
            nameGap: 40,
            splitLine: {
                lineStyle: {
                    type: 'dashed',
                    opacity: 0.2
                }
            }
        },
        series: series
    };
    
    chart.setOption(option);
    window.addEventListener('resize', () => chart.resize());
}

// ============================================================
// WIDGET MANAGEMENT
// ============================================================

function saveWidgetVisibility() {
    const visibility = {};
    ALL_WIDGETS.forEach(widgetId => {
        const wrapper = document.getElementById(widgetId + '-wrapper');
        if (wrapper) {
            visibility[widgetId] = !wrapper.classList.contains('d-none');
        }
    });
    localStorage.setItem(STORAGE_KEYS.visibility, JSON.stringify(visibility));
}

function saveWidgetOrder() {
    const grid = document.getElementById('dashboard-grid');
    const widgets = grid.querySelectorAll('.widget-wrapper');
    const order = Array.from(widgets).map(w => w.getAttribute('data-id'));
    localStorage.setItem(STORAGE_KEYS.order, JSON.stringify(order));
}

function loadWidgetState() {
    try {
        const savedVisibility = localStorage.getItem(STORAGE_KEYS.visibility);
        if (savedVisibility) {
            const visibility = JSON.parse(savedVisibility);
            ALL_WIDGETS.forEach(widgetId => {
                const wrapper = document.getElementById(widgetId + '-wrapper');
                if (wrapper && visibility.hasOwnProperty(widgetId)) {
                    if (visibility[widgetId]) {
                        wrapper.classList.remove('d-none');
                        wrapper.style.display = '';
                    } else {
                        wrapper.classList.add('d-none');
                        wrapper.style.display = 'none';
                    }
                }
            });
        }
        
        const savedOrder = localStorage.getItem(STORAGE_KEYS.order);
        if (savedOrder) {
            const order = JSON.parse(savedOrder);
            const grid = document.getElementById('dashboard-grid');
            const widgets = {};
            
            grid.querySelectorAll('.widget-wrapper').forEach(w => {
                widgets[w.getAttribute('data-id')] = w;
            });
            
            order.forEach(widgetId => {
                if (widgets[widgetId]) {
                    grid.appendChild(widgets[widgetId]);
                }
            });
        }
    } catch (e) {
        console.error('Widget durumu yüklenirken hata:', e);
    }
}

function initSortable() {
    const grid = document.getElementById('dashboard-grid');
    new Sortable(grid, {
        animation: 300,
        handle: '.handle',
        ghostClass: 'sortable-ghost',
        onEnd: function (evt) {
            saveWidgetOrder();
            Swal.fire({
                icon: 'success',
                title: '🚀 Düzen Kaydedildi',
                toast: true,
                position: 'top-end',
                showConfirmButton: false,
                timer: 1500,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: '#fff'
            });
        }
    });
}

function toggleWidget(widgetId) {
    const wrapper = document.getElementById(widgetId + '-wrapper');
    if (wrapper) {
        const isHidden = wrapper.classList.contains('d-none');
        
        if (isHidden) {
            wrapper.classList.remove('d-none');
            wrapper.style.display = '';
        } else {
            wrapper.classList.add('d-none');
        }
        
        saveWidgetVisibility();
        
        Swal.fire({
            icon: isHidden ? 'success' : 'info',
            title: isHidden ? 'Widget Açıldı' : 'Widget Gizlendi',
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 1500
        });
    }
}

function hideWidget(widgetId) {
    const wrapper = document.getElementById(widgetId + '-wrapper');
    if (wrapper) {
        wrapper.classList.add('d-none');
        wrapper.style.display = 'none';
        saveWidgetVisibility();
        
        Swal.fire({
            icon: 'info',
            title: 'Widget Gizlendi',
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 2000
        });
    }
}

function showAllWidgets() {
    let shownCount = 0;
    
    ALL_WIDGETS.forEach(widgetId => {
        const wrapper = document.getElementById(widgetId + '-wrapper');
        if (wrapper) {
            const isHidden = wrapper.classList.contains('d-none');
            if (isHidden) {
                wrapper.classList.remove('d-none');
                wrapper.style.display = '';
                shownCount++;
            }
        }
    });
    
    saveWidgetVisibility();
    
    Swal.fire({
        icon: shownCount > 0 ? 'success' : 'info',
        title: shownCount > 0 ? `${shownCount} Widget Açıldı` : 'Tüm Widgetlar Zaten Açık',
        toast: true,
        position: 'top-end',
        showConfirmButton: false,
        timer: 2000
    });
}

function resetLayout() {
    Swal.fire({
        title: 'Varsayılan Düzeni Geri Yükle?',
        text: 'Tüm özelleştirmeleriniz silinecek.',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#dc3545',
        cancelButtonColor: '#6c757d',
        confirmButtonText: 'Evet, Sıfırla',
        cancelButtonText: 'İptal'
    }).then((result) => {
        if (result.isConfirmed) {
            localStorage.removeItem(STORAGE_KEYS.visibility);
            localStorage.removeItem(STORAGE_KEYS.order);
            
            Swal.fire({
                icon: 'success',
                title: 'Düzen Sıfırlandı',
                text: 'Sayfa yenileniyor...',
                timer: 1500,
                showConfirmButton: false
            }).then(() => {
                location.reload();
            });
        }
    });
}

console.log("✅ 🚀 NASA Seviyesi Dashboard Hazır!");
</script>
{% endblock %}'''

try:
    with open('templates/kurum_panel.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ SUCCESS: NASA SEVİYESİ DASHBOARD OLUŞTURULDU! ({len(content)} karakter)")
    print("🚀 Özellikler:")
    print("   ✓ Apache ECharts 5.4.3")
    print("   ✓ Sunburst Chart (Stratejik Güneş)")
    print("   ✓ Sankey Diagram (Değer Akışı)")
    print("   ✓ Predictive Line (Gelecek Simülasyonu)")
    print("   ✓ Bubble/Scatter (Proje Galaksisi)")
    print("   ✓ Gradient & Glow efektleri")
    print("   ✓ Animasyonlu çizimler")
    print("   ✓ LocalStorage persistence")
    print("   ✓ Dummy data generators")
    print("")
    print("🌟 BURASI NASA MI? - EVET!")
except Exception as e:
    print(f"❌ ERROR: {e}")
