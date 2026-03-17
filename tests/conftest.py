"""
Pytest Configuration
Sprint 5-6: Güvenlik ve Stabilite
Test fixtures ve setup
"""

import pytest
from werkzeug.security import generate_password_hash

from app import create_app
from app.models import db
from app.models.core import User, Tenant, Role
from config import TestingConfig


@pytest.fixture(scope='function')
def app():
    """Flask app fixture - function scope for test isolation."""
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Test client fixture"""
    return app.test_client()


@pytest.fixture(scope='function')
def db_session(app):
    """Database session fixture"""
    with app.app_context():
        db.session.begin_nested()
        yield db.session
        db.session.rollback()


@pytest.fixture
def test_tenant(db_session):
    """Test tenant fixture"""
    tenant = Tenant(
        name='Test Tenant',
        short_name='test',
        is_active=True
    )
    db_session.add(tenant)
    db_session.commit()
    return tenant


@pytest.fixture
def test_role(db_session):
    """Test role fixture"""
    role = Role(
        name='test_user',
        description='Test User Role'
    )
    db_session.add(role)
    db_session.commit()
    return role


@pytest.fixture
def test_user(db_session, test_tenant, test_role):
    """Test user fixture"""
    user = User(
        email='test@example.com',
        first_name='Test',
        last_name='User',
        tenant_id=test_tenant.id,
        role_id=test_role.id,
        password_hash=generate_password_hash('TestPassword123'),
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    return user
