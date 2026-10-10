"""Password reset flow tests."""
from unittest.mock import patch

from werkzeug.security import check_password_hash

from app.models import db
from app.routes import password_reset as pr
from app.routes.password_reset import generate_reset_token

SEND = "micro.services.email_service.send_notification_email"


def test_request_existing_and_missing_same_response(client, test_user):
    with patch(SEND, return_value=(True, "")) as m:
        r1 = client.post("/forgot-password", data={"email": test_user.email})
        r2 = client.post("/forgot-password", data={"email": "nobody@example.com"})
    assert r1.status_code == r2.status_code == 302
    assert r1.headers["Location"] == r2.headers["Location"]
    assert m.call_count == 1


def test_inactive_user_gets_no_mail(client, test_user):
    test_user.is_active = False
    db.session.commit()
    with patch(SEND, return_value=(True, "")) as m:
        client.post("/forgot-password", data={"email": test_user.email})
    assert m.call_count == 0


def test_valid_token_resets_password(client, test_user):
    token = generate_reset_token(test_user)
    r = client.post(f"/reset-password/{token}",
                    data={"password": "NewStrong123", "password_confirm": "NewStrong123"})
    assert r.status_code == 302
    db.session.refresh(test_user)
    assert check_password_hash(test_user.password_hash, "NewStrong123")


def test_token_single_use(client, test_user):
    token = generate_reset_token(test_user)
    data = {"password": "NewStrong123", "password_confirm": "NewStrong123"}
    client.post(f"/reset-password/{token}", data=data)
    r = client.post(f"/reset-password/{token}",
                    data={"password": "Other12345x", "password_confirm": "Other12345x"})
    assert r.status_code == 302 and "forgot-password" in r.headers["Location"]
    db.session.refresh(test_user)
    assert check_password_hash(test_user.password_hash, "NewStrong123")


def test_expired_and_garbage_token_rejected(client, test_user):
    token = generate_reset_token(test_user)
    assert pr.load_user_from_token(token) is not None
    assert pr.load_user_from_token(token, max_age=-1) is None
    r = client.get("/reset-password/garbage")
    assert r.status_code == 302 and "forgot-password" in r.headers["Location"]


def test_weak_password_rejected(client, test_user):
    token = generate_reset_token(test_user)
    client.post(f"/reset-password/{token}", data={"password": "abc", "password_confirm": "abc"})
    db.session.refresh(test_user)
    assert check_password_hash(test_user.password_hash, "TestPassword123")
