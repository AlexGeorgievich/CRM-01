from app.core.security import create_access_token, decode_access_token
from app.core.security import get_password_hash, verify_password


def test_password_hashing_roundtrip() -> None:
    password = "strong-password-123"
    hashed = get_password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong-password", hashed)


def test_access_token_roundtrip() -> None:
    token = create_access_token("42")

    assert decode_access_token(token) == "42"
    assert decode_access_token("not-a-token") is None
