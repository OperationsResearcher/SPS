"""
Swagger/OpenAPI Documentation
Sprint 13-15: API ve Entegrasyonlar
"""

from flask_swagger_ui import get_swaggerui_blueprint


def create_swagger_blueprint(legacy_prefix: str = "/kok"):
    """Klasik REST API dokümantasyonu — yollar LEGACY_URL_PREFIX altında (örn. /kok/api/docs)."""
    lp = (legacy_prefix or "/kok").rstrip("/") or "/kok"
    swagger_url = f"{lp}/api/docs"
    api_url = f"{lp}/api/v1/swagger.json"
    return get_swaggerui_blueprint(
        swagger_url,
        api_url,
        config={
            "app_name": "Kokpitim API v1",
            "defaultModelsExpandDepth": -1,
        },
    )


# Geriye dönük uyumluluk (tercih: create_swagger_blueprint kullanın)
SWAGGER_URL = "/kok/api/docs"
API_URL = "/kok/api/v1/swagger.json"
swaggerui_blueprint = create_swagger_blueprint("/kok")

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
        {"name": "Reports", "description": "Rapor oluşturma"}
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
