"""Custom Dashboard Widget Registry (Sprint 50).

Önceden tanımlanmış widget'lardan oluşan registry. Kullanıcı dashboard'ına
widget ekler — frontend bu metadata ile uygun komponenti seçer.

Mimari:
    Widget tanımı (bu modül) ──[data fetcher]──> JSON
                            ──[frontend type]──> render component

Production'da user_dashboards tablosuna user-bazlı dashboard config saklanır
(şu an iskelet — JSON config + endpoint).
"""
from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Callable, Optional


@dataclass
class WidgetDefinition:
    """Widget metadata + data fetcher."""
    key: str  # "kpi_card", "anomaly_count", "process_health" gibi
    title: str
    description: str
    category: str  # "kpi", "risk", "strategy", "okr", "esg"
    component: str  # frontend component adı (Vue/React)
    data_endpoint: Optional[str] = None  # data fetch URL
    default_size: str = "1x1"  # grid boyut: 1x1, 2x1, 2x2
    config_schema: dict = field(default_factory=dict)  # widget config (kpi_id, period vb.)
    icon: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


# ─── Built-in widget'lar ─────────────────────────────────────────────────────

_REGISTRY: dict[str, WidgetDefinition] = {}


def register(widget: WidgetDefinition) -> None:
    _REGISTRY[widget.key] = widget


# KPI category
register(WidgetDefinition(
    key="kpi_card", title="KPI Kartı",
    description="Tek KPI'nın son değeri + hedef + trend ok",
    category="kpi", component="KpiCard",
    data_endpoint="/k-rapor/api/forecast/{kpi_id}?periods=1",
    default_size="1x1",
    config_schema={"kpi_id": {"type": "integer", "required": True}},
    icon="bi-graph-up",
))
register(WidgetDefinition(
    key="kpi_trend_chart", title="KPI Trend Grafiği",
    description="Son 12 dönem + 3 forecast line chart",
    category="kpi", component="KpiTrendChart",
    data_endpoint="/k-rapor/api/forecast/{kpi_id}?periods=3",
    default_size="2x2",
    config_schema={"kpi_id": {"type": "integer", "required": True}},
    icon="bi-graph-up-arrow",
))

# Risk category
register(WidgetDefinition(
    key="risk_heatmap", title="Risk Isı Haritası 5×5",
    description="Probability × Impact matrisi",
    category="risk", component="RiskHeatmap",
    data_endpoint="/k-radar/api/risk/matrix",
    default_size="2x2",
    icon="bi-shield-exclamation",
))
register(WidgetDefinition(
    key="critical_risks", title="Kritik Riskler",
    description="severity=critical olanlar (top 10)",
    category="risk", component="RiskList",
    data_endpoint="/k-radar/api/risk/list?severity=critical&limit=10",
    default_size="2x1",
    icon="bi-exclamation-triangle",
))

# Strategy
register(WidgetDefinition(
    key="strategy_progress", title="Stratejik İlerleme",
    description="Aktif plan year ana strateji yüzdeleri",
    category="strategy", component="StrategyProgress",
    data_endpoint="/k-rapor/api/kurumsal",
    default_size="2x1",
    icon="bi-bullseye",
))

# OKR
register(WidgetDefinition(
    key="okr_summary", title="OKR Özeti",
    description="Aktif yıl Objective + ortalama ilerleme",
    category="okr", component="OkrSummary",
    data_endpoint="/sp/api/okr",
    default_size="2x1",
    icon="bi-flag",
))

# Anomalies
register(WidgetDefinition(
    key="anomaly_alert", title="KPI Anomali Uyarısı",
    description="Son 24 saat severity ≥ medium",
    category="kpi", component="AnomalyList",
    data_endpoint="/k-rapor/api/anomalies?threshold=2.0&limit=5",
    default_size="2x1",
    icon="bi-broadcast",
))

# ESG (Sprint 49)
register(WidgetDefinition(
    key="esg_scorecard", title="ESG Skor Kartı",
    description="E/S/G kategori bazlı performans (yakında)",
    category="esg", component="EsgScorecard",
    data_endpoint=None,  # API gelecek (Sprint 53+)
    default_size="2x2",
    icon="bi-tree",
))

# Stakeholder
register(WidgetDefinition(
    key="stakeholder_map", title="Paydaş Haritası",
    description="Influence × Interest matrix",
    category="strategy", component="StakeholderMap",
    data_endpoint="/k-rapor/api/paydas",
    default_size="2x2",
    icon="bi-people",
))


# ─── Public API ──────────────────────────────────────────────────────────────

def list_widgets(category: Optional[str] = None) -> list[dict]:
    """Tüm widget'ları (veya kategoriye göre) döndür."""
    items = _REGISTRY.values()
    if category:
        items = [w for w in items if w.category == category]
    return [w.to_dict() for w in items]


def get_widget(key: str) -> Optional[dict]:
    w = _REGISTRY.get(key)
    return w.to_dict() if w else None


def categories() -> list[str]:
    return sorted({w.category for w in _REGISTRY.values()})
