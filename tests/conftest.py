# -*- coding: utf-8 -*-
"""
Pytest configuration ve fixtures
"""
import pytest
import os
import sys
from datetime import datetime

# Proje root'unu path'e ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from __init__ import create_app
from extensions import db
from models import User, Kurum, Project, Task, TaskImpact, BireyselPerformansGostergesi


@pytest.fixture(scope='session')
def app():
    """Test uygulaması oluştur"""
    app = create_app('testing')
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """CLI test runner"""
    return app.test_cli_runner()


@pytest.fixture
def auth_client(client, app):
    """Authenticated test client"""
    with app.app_context():
        # Test kullanıcısı oluştur
        kurum = Kurum(
            ad='Test Kurum',
            kisa_ad='TEST',
            email='test@test.com'
        )
        db.session.add(kurum)
        db.session.flush()
        
        user = User(
            username='testuser',
            email='test@test.com',
            first_name='Test',
            last_name='User',
            sistem_rol='kurum_yoneticisi',
            kurum_id=kurum.id
        )
        user.set_password('testpass123')
        db.session.add(user)
        db.session.commit()
        
        # Login yap
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
        
        yield client


@pytest.fixture
def test_kurum(app):
    """Test kurumu"""
    with app.app_context():
        kurum = Kurum(
            ad='Test Kurum',
            kisa_ad='TEST',
            email='test@test.com'
        )
        db.session.add(kurum)
        db.session.commit()
        return kurum


@pytest.fixture
def test_user(app, test_kurum):
    """Test kullanıcısı"""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@test.com',
            first_name='Test',
            last_name='User',
            sistem_rol='kurum_yoneticisi',
            kurum_id=test_kurum.id
        )
        user.set_password('testpass123')
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def test_project(app, test_kurum, test_user):
    """Test projesi"""
    with app.app_context():
        project = Project(
            name='Test Proje',
            description='Test açıklama',
            manager_id=test_user.id,
            kurum_id=test_kurum.id,
            start_date=datetime(2025, 1, 1).date(),
            end_date=datetime(2025, 12, 31).date(),
            priority='Yüksek'
        )
        db.session.add(project)
        db.session.commit()
        return project


@pytest.fixture
def test_task(app, test_project, test_user):
    """Test görevi"""
    with app.app_context():
        task = Task(
            project_id=test_project.id,
            title='Test Görev',
            description='Test görev açıklaması',
            assigned_to_id=test_user.id,
            status='Yapılacak',
            priority='Yüksek',
            due_date=datetime(2025, 12, 31).date()
        )
        db.session.add(task)
        db.session.commit()
        return task




















