# -*- coding: utf-8 -*-
"""
Swagger/OpenAPI Dokümantasyonu
flask-restx ile otomatik API dokümantasyonu
"""
from flask_restx import Api, Resource, fields, Namespace
from flask import Blueprint

# API Blueprint
swagger_bp = Blueprint('swagger', __name__, url_prefix='/api')

# RestX API instance
api = Api(
    swagger_bp,
    version='2.0.0',
    title='SPSV2 API Dokümantasyonu',
    description='Stratejik Planlama ve Performans Yönetim Sistemi REST API',
    doc='/docs',
    default='SPSV2 API',
    default_label='Ana API Endpoint\'leri'
)

# Namespace'ler
projects_ns = Namespace('projects', description='Proje yönetimi işlemleri')
tasks_ns = Namespace('tasks', description='Görev yönetimi işlemleri')
dashboard_ns = Namespace('dashboard', description='Dashboard verileri')
simulation_ns = Namespace('simulation', description='What-If simülasyon işlemleri')
webhook_ns = Namespace('webhooks', description='Webhook yönetimi')

api.add_namespace(projects_ns)
api.add_namespace(tasks_ns)
api.add_namespace(dashboard_ns)
api.add_namespace(simulation_ns)
api.add_namespace(webhook_ns)

# Model tanımları
project_model = api.model('Project', {
    'id': fields.Integer(description='Proje ID'),
    'name': fields.String(required=True, description='Proje adı'),
    'description': fields.String(description='Proje açıklaması'),
    'start_date': fields.Date(description='Başlangıç tarihi'),
    'end_date': fields.Date(description='Bitiş tarihi'),
    'priority': fields.String(description='Öncelik (Düşük/Orta/Yüksek/Acil)'),
    'manager_id': fields.Integer(description='Proje yöneticisi ID')
})

task_model = api.model('Task', {
    'id': fields.Integer(description='Görev ID'),
    'title': fields.String(required=True, description='Görev başlığı'),
    'description': fields.String(description='Görev açıklaması'),
    'status': fields.String(description='Durum (Yapılacak/Devam Ediyor/Beklemede/Tamamlandı)'),
    'priority': fields.String(description='Öncelik'),
    'due_date': fields.Date(description='Bitiş tarihi'),
    'assigned_to_id': fields.Integer(description='Atanan kullanıcı ID')
})

simulation_request_model = api.model('SimulationRequest', {
    'type': fields.String(required=True, description='Simülasyon tipi (project_end_date/pg_value/risk_probability)'),
    'project_id': fields.Integer(description='Proje ID (project_end_date için)'),
    'pg_id': fields.Integer(description='PG ID (pg_value için)'),
    'risk_id': fields.Integer(description='Risk ID (risk_probability için)'),
    'new_value': fields.Raw(description='Yeni değer (tarih/float/int)'),
    'new_probability': fields.Integer(description='Yeni olasılık (risk_probability için)')
})

simulation_response_model = api.model('SimulationResponse', {
    'original_score': fields.Float(description='Orijinal skor'),
    'simulated_score': fields.Float(description='Simüle edilmiş skor'),
    'impact': fields.Float(description='Etki miktarı'),
    'impact_percentage': fields.Float(description='Yüzde değişim'),
    'affected_processes': fields.List(fields.Raw, description='Etkilenen süreçler'),
    'recommendations': fields.List(fields.Raw, description='Öneriler')
})

# Endpoint tanımları (örnek - gerçek endpoint'ler api/routes.py'de)
@simulation_ns.route('/what-if')
class WhatIfSimulation(Resource):
    @api.doc('what_if_simulation', description='What-If simülasyonu çalıştır')
    @api.expect(simulation_request_model)
    @api.marshal_with(simulation_response_model, code=200)
    def post(self):
        """What-If simülasyonu çalıştır"""
        # Gerçek implementasyon api/routes.py'de olacak
        pass

@dashboard_ns.route('/executive')
class ExecutiveDashboard(Resource):
    @api.doc('get_executive_dashboard', description='Executive Dashboard verilerini getir')
    def get(self):
        """Executive Dashboard verilerini getir"""
        # Gerçek implementasyon api/routes.py'de olacak
        pass



















