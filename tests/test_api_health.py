# -*- coding: utf-8 -*-
"""
Health Check Endpoint Testleri
"""
import pytest


class TestHealthEndpoint:
    """Health check endpoint testleri"""
    
    def test_health_check_success(self, client):
        """Health check başarılı durum"""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        assert 'version' in data
        assert 'checks' in data
        assert 'database' in data['checks']
    
    def test_health_check_structure(self, client):
        """Health check response yapısı"""
        response = client.get('/health')
        data = response.get_json()
        
        # Gerekli alanlar
        assert 'status' in data
        assert 'timestamp' in data
        assert 'version' in data
        assert 'checks' in data
        
        # Checks içinde database olmalı
        assert 'database' in data['checks']



















