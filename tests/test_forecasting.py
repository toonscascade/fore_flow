import pytest
from uuid import uuid4
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.core.auth import create_session_token, hash_password, token_digest
from app.database.connection import AsyncSessionLocal
from app.models.user import User, UserSession


@pytest.mark.asyncio
async def test_ai_forecast_generation_and_retrieval():
    email = f"forecaster-{uuid4().hex[:8]}@foreflow.security"
    password = "Forecaster!Pass2026"

    async with AsyncSessionLocal() as session:
        user = User(
            email=email,
            password_hash=hash_password(password),
            full_name="Forecaster Analyst",
            role="DATA_SCIENTIST",
        )
        session.add(user)
        await session.flush()
        token, jti, expires = create_session_token(user.id)
        session.add(UserSession(user_id=user.id, jti=jti, token_hash=token_digest(token), expires_at=expires))
        await session.commit()

    transport = ASGITransport(app=app)
    cookies = {"foreflow_session": token}
    async with AsyncClient(transport=transport, base_url="http://test", cookies=cookies) as client:
        payload = {
            "network_segment": "DMZ-Internal",
            "horizon_hours": 24,
            "sequence_length": 48,
        }

        res = await client.post("/api/v1/forecast/generate", json=payload)
        assert res.status_code == 201
        forecast = res.json()
        assert forecast["horizon_hours"] == 24
        assert len(forecast["points"]) == 24
        assert forecast["confidence"] in ["low", "medium", "high"]
        assert "model_version" in forecast
        assert 0.0 <= forecast["points"][0]["predicted_threat_level"] <= 1.0

        # Retrieve latest forecast
        latest_res = await client.get("/api/v1/forecast/latest?network_segment=DMZ-Internal")
        assert latest_res.status_code == 200
        latest = latest_res.json()
        assert latest["id"] == forecast["id"]
