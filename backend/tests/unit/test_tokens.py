"""Tests for JWT tokens."""
import uuid
import pytest
import jwt as pyjwt
from app.utils.tokens import create_access_token, create_refresh_token, decode_access_token, decode_refresh_token


def test_access_token_roundtrip():
    uid = uuid.uuid4()
    token = create_access_token(uid, "user")
    payload = decode_access_token(token)
    assert payload["sub"] == str(uid)
    assert payload["role"] == "user"
    assert payload["type"] == "access"

def test_refresh_token_roundtrip():
    uid = uuid.uuid4()
    token = create_refresh_token(uid)
    payload = decode_refresh_token(token)
    assert payload["sub"] == str(uid)
    assert payload["type"] == "refresh"

def test_access_token_has_exp():
    token = create_access_token(uuid.uuid4(), "admin")
    payload = decode_access_token(token)
    assert "exp" in payload

def test_refresh_token_rejected_as_access():
    token = create_refresh_token(uuid.uuid4())
    with pytest.raises(pyjwt.InvalidTokenError):
        decode_access_token(token)

def test_access_token_rejected_as_refresh():
    token = create_access_token(uuid.uuid4(), "user")
    with pytest.raises(pyjwt.InvalidTokenError):
        decode_refresh_token(token)

def test_invalid_token_raises():
    with pytest.raises(pyjwt.PyJWTError):
        decode_access_token("invalid.token.here")

def test_expired_token_raises():
    from datetime import datetime, timezone, timedelta
    uid = uuid.uuid4()
    payload = {"sub": str(uid), "type": "access", "role": "user", "exp": datetime.now(timezone.utc) - timedelta(hours=1)}
    from app.config import get_settings
    s = get_settings()
    token = pyjwt.encode(payload, s.jwt_secret, algorithm=s.jwt_algorithm)
    with pytest.raises(pyjwt.ExpiredSignatureError):
        decode_access_token(token)

def test_different_users_different_tokens():
    t1 = create_access_token(uuid.uuid4(), "user")
    t2 = create_access_token(uuid.uuid4(), "user")
    assert t1 != t2
