"""
Swagger/OpenAPI Documentation
Sprint 13-15: API ve Entegrasyonlar
"""

from flask_swagger_ui import get_swaggerui_blueprint


def create_swagger_blueprint(base_prefix: str = ""):
    """REST API dokümantasyonu — tek yapı kök URL altında."""
    bp = (base_prefix or "").rstrip("/")
    swagger_url = f"{bp}/api/docs" if bp else "/api/docs"
    api_url = f"{bp}/api/v1/swagger.json" if bp else "/api/v1/swagger.json"
    return get_swaggerui_blueprint(
        swagger_url,
        api_url,
        config={
            "app_name": "Kokpitim API v1",
            "defaultModelsExpandDepth": -1,
        },
    )


# Geriye dönük uyumluluk (tercih: create_swagger_blueprint kullanın)
SWAGGER_URL = "/api/docs"
API_URL = "/api/v1/swagger.json"
swaggerui_blueprint = create_swagger_blueprint("")

# OpenAPI Specification
openapi_spec = {
    "openapi": "3.0.0",
    "info": {
        "title": "Kokpitim API",
        "description": "Kurumsal Performans Yönetim Platformu API",
        "version": "1.0.0",
        "contact": {
            "name": "API Support",
            "email": "support@kokpitim.com"
        }
    },
    "servers": [
        {
            "url": "http://localhost:5001/api/v1",
            "description": "Development server"
        },
        {
            "url": "https://api.kokpitim.com/v1",
            "description": "Production server"
        }
    ],
    "tags": [
        {"name": "Processes", "description": "Süreç yönetimi"},
        {"name": "KPI Data", "description": "KPI veri girişi"},
        {"name": "Analytics", "description": "Analitik ve raporlama"},
        {"name": "Reports", "description": "Rapor oluşturma"},
        # Sprint 43 — yeni tag'ler
        {"name": "Anomalies", "description": "KPI anomali tespit (Z-score)"},
        {"name": "OKR", "description": "Objectives + Key Results"},
        {"name": "Risk", "description": "Risk yönetimi (RAID + heatmap)"},
        {"name": "KVKK", "description": "Veri sahibi hakları (export/delete)"},
        {"name": "Auth", "description": "Kimlik doğrulama + 2FA"},
        {"name": "Webhooks", "description": "Slack/Teams/Discord bildirim"},
        {"name": "Forecasting", "description": "KPI trend tahmini (Sprint 46)"},
    ],
    "paths": {
        "/processes": {
            "get": {
                "tags": ["Processes"],
                "summary": "Süreç listesi",
                "description": "Tenant'a ait tüm süreçleri listeler",
                "parameters": [
                    {
                        "name": "page",
                        "in": "query",
                        "schema": {"type": "integer", "default": 1}
                    },
                    {
                        "name": "per_page",
                        "in": "query",
                        "schema": {"type": "integer", "default": 20}
                    },
                    {
                        "name": "search",
                        "in": "query",
                        "schema": {"type": "string"}
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Başarılı",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "items": {"type": "array"},
                                        "total": {"type": "integer"},
                                        "pages": {"type": "integer"},
                                        "current_page": {"type": "integer"}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "/processes/{process_id}": {
            "get": {
                "tags": ["Processes"],
                "summary": "Süreç detayı",
                "parameters": [
                    {
                        "name": "process_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"}
                    }
                ],
                "responses": {
                    "200": {"description": "Başarılı"},
                    "404": {"description": "Süreç bulunamadı"}
                }
            }
        },
        "/kpi-data": {
            "post": {
                "tags": ["KPI Data"],
                "summary": "KPI veri girişi",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["process_kpi_id", "data_date", "actual_value", "target_value"],
                                "properties": {
                                    "process_kpi_id": {"type": "integer"},
                                    "data_date": {"type": "string", "format": "date"},
                                    "actual_value": {"type": "number"},
                                    "target_value": {"type": "number"},
                                    "notes": {"type": "string"}
                                }
                            }
                        }
                    }
                },
                "responses": {
                    "201": {"description": "Oluşturuldu"},
                    "400": {"description": "Geçersiz veri"}
                }
            }
        },
        "/analytics/trend/{kpi_id}": {
            "get": {
                "tags": ["Analytics"],
                "summary": "KPI trend analizi",
                "parameters": [
                    {
                        "name": "kpi_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"}
                    },
                    {
                        "name": "start_date",
                        "in": "query",
                        "required": True,
                        "schema": {"type": "string", "format": "date"}
                    },
                    {
                        "name": "end_date",
                        "in": "query",
                        "required": True,
                        "schema": {"type": "string", "format": "date"}
                    },
                    {
                        "name": "frequency",
                        "in": "query",
                        "schema": {
                            "type": "string",
                            "enum": ["daily", "weekly", "monthly", "quarterly"],
                            "default": "monthly"
                        }
                    }
                ],
                "responses": {
                    "200": {"description": "Başarılı"}
                }
            }
        },
        # Sprint 14 — Anomali endpoint'leri
        "/k-rapor/api/anomalies": {
            "get": {
                "tags": ["Anomalies"],
                "summary": "KPI anomali tespiti (Z-score)",
                "parameters": [
                    {"name": "threshold", "in": "query",
                     "schema": {"type": "number", "default": 2.0}},
                    {"name": "limit", "in": "query",
                     "schema": {"type": "integer", "default": 50}},
                ],
                "responses": {"200": {"description": "Anomali listesi"}},
            }
        },
        "/k-rapor/api/anomalies/notify-slack": {
            "post": {
                "tags": ["Anomalies", "Webhooks"],
                "summary": "Anomalileri Slack'e gönder",
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"type": "object",
                        "properties": {
                            "webhook_url": {"type": "string"},
                            "severity_min": {"type": "string", "enum": ["low", "medium", "high"]},
                            "limit": {"type": "integer"},
                        }
                    }}}
                },
                "responses": {"200": {"description": "Gönderildi"}},
            }
        },
        # Sprint 13 — OKR
        "/sp/api/okr": {
            "get": {"tags": ["OKR"], "summary": "Aktif plan year için OKR listesi",
                    "responses": {"200": {"description": "Objective + KR'lar"}}}
        },
        "/sp/api/okr/objective": {
            "post": {"tags": ["OKR"], "summary": "Yeni Objective oluştur",
                     "requestBody": {"required": True, "content": {"application/json": {
                         "schema": {"type": "object", "properties": {
                             "title": {"type": "string"},
                             "description": {"type": "string"},
                             "quarter": {"type": "integer"},
                             "owner": {"type": "string"},
                             "linked_strategy_id": {"type": "integer"},
                         }}}}},
                     "responses": {"200": {"description": "OK"}}}
        },
        "/sp/api/okr/sync-kpis": {
            "post": {"tags": ["OKR"], "summary": "Tüm bağlı KR'leri KPI'larından sync et (Sprint 33)",
                     "responses": {"200": {"description": "synced + skipped sayıları"}}}
        },
        # Sprint 34 — Risk
        "/k-radar/api/risk/list": {
            "get": {"tags": ["Risk"], "summary": "Risk listesi + filter (severity/status/source)",
                    "responses": {"200": {"description": "Risk satırları"}}}
        },
        "/k-radar/api/risk/matrix": {
            "get": {"tags": ["Risk"], "summary": "5×5 probability×impact heatmap",
                    "responses": {"200": {"description": "Grid matrisi"}}}
        },
        "/k-radar/api/risk/add": {
            "post": {"tags": ["Risk"], "summary": "Yeni risk ekle",
                     "responses": {"200": {"description": "OK"}}}
        },
        # Sprint 12 — KVKK
        "/api/user/export-my-data": {
            "get": {"tags": ["KVKK"], "summary": "Kullanıcı verisi JSON export (Madde 11)",
                    "responses": {"200": {"description": "JSON dump"}}}
        },
        "/api/user/delete-my-account": {
            "post": {"tags": ["KVKK"], "summary": "Hesap anonimize + sil (Madde 7)",
                     "responses": {"200": {"description": "Silindi"}}}
        },
        # Sprint 26 — 2FA
        "/2fa/setup": {
            "get": {"tags": ["Auth"], "summary": "2FA setup başlat (QR + secret)",
                    "responses": {"200": {"description": "HTML form"}}}
        },
        "/2fa/verify-setup": {
            "post": {"tags": ["Auth"], "summary": "Setup doğrulama + backup codes",
                     "responses": {"200": {"description": "OK + backup_codes"}}}
        },
        # Sprint 25 — SSO
        "/sso/google": {
            "get": {"tags": ["Auth"], "summary": "Google OAuth flow başlat",
                    "responses": {"302": {"description": "Google'a redirect"}}}
        },
        # Sprint 18 — Email digest
        "/k-rapor/api/digest/send": {
            "post": {"tags": ["Reports"], "summary": "Haftalık digest mail tetikle",
                     "responses": {"200": {"description": "Sent count"}}}
        },
        # Sprint 11 — PDF export
        "/k-rapor/api/export-pdf": {
            "get": {"tags": ["Reports"], "summary": "Kurumsal özet PDF",
                    "responses": {"200": {"description": "PDF bytes"}}}
        },
        "/bireysel/api/karne/export-pdf": {
            "get": {"tags": ["Reports"], "summary": "Bireysel karne PDF",
                    "responses": {"200": {"description": "PDF bytes"}}}
        },
        # Sprint 24 — Admin paginated
        "/admin/api/users": {
            "get": {"tags": ["Processes"], "summary": "Paginated user list (search desteği)",
                    "parameters": [
                        {"name": "page", "in": "query", "schema": {"type": "integer"}},
                        {"name": "page_size", "in": "query", "schema": {"type": "integer"}},
                        {"name": "search", "in": "query", "schema": {"type": "string"}},
                    ],
                    "responses": {"200": {"description": "data + pagination"}}}
        },
        # Sprint 46 — Forecasting (eklenecek)
        "/k-rapor/api/forecast/{kpi_id}": {
            "get": {"tags": ["Forecasting"],
                    "summary": "Linear regression trend forecast",
                    "parameters": [
                        {"name": "kpi_id", "in": "path", "required": True,
                         "schema": {"type": "integer"}},
                        {"name": "periods", "in": "query",
                         "schema": {"type": "integer", "default": 3}},
                    ],
                    "responses": {"200": {"description": "tahmin + güven aralığı"}}}
        },
        "/analytics/health/{process_id}": {
            "get": {
                "tags": ["Analytics"],
                "summary": "Süreç sağlık skoru",
                "parameters": [
                    {
                        "name": "process_id",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"}
                    },
                    {
                        "name": "year",
                        "in": "query",
                        "schema": {"type": "integer"}
                    }
                ],
                "responses": {
                    "200": {"description": "Başarılı"}
                }
            }
        }
    },
    "components": {
        "securitySchemes": {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            },
            "cookieAuth": {
                "type": "apiKey",
                "in": "cookie",
                "name": "session"
            }
        }
    },
    "security": [
        {"bearerAuth": []},
        {"cookieAuth": []}
    ]
}
