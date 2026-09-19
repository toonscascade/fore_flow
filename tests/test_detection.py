import pytest
from uuid import uuid4
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.core.auth import create_session_token, hash_password, token_digest
from app.database.connection import AsyncSessionLocal
from app.models.user import User, UserSession


@pytest.mark.asyncio
async def test_ai_anomaly_detection_pipeline():
    admin_email = f"analyst-{uuid4().hex[:8]}@foreflow.security"
    password = "Analyst!Password2026"

    async with AsyncSessionLocal() as session:
        analyst = User(
            email=admin_email,
            password_hash=hash_password(password),
            full_name="AI Detection Analyst",
            role="DATA_SCIENTIST",
        )
        session.add(analyst)
        await session.flush()
        token, jti, expires = create_session_token(analyst.id)
        session.add(UserSession(user_id=analyst.id, jti=jti, token_hash=token_digest(token), expires_at=expires))
        await session.commit()

    transport = ASGITransport(app=app)
    cookies = {"foreflow_session": token}
    async with AsyncClient(transport=transport, base_url="http://test", cookies=cookies) as client:
        # 25-dimensional network flow feature vector
        feature_vector = [
            12.4, 450, 68000, 36.2, 5480.0, 151.1, 45.2, 40, 1500,
            0.65, 0.35, 0.70, 0.30, 1, 448, 2, 0, 15, 0, 0.027, 0.005,
            49152, 443, 1.0, 0.0
        ]

        payload = {
            "flow_id": f"flow-{uuid4().hex[:8]}",
            "src_ip": "10.0.1.45",
            "dst_ip": "172.16.0.8",
            "src_port": 49152,
            "dst_port": 443,
            "protocol": "TCP",
            "feature_vector": feature_vector,
            "raw_features": {"service": "https", "bytes": 68000},
        }

        res = await client.post("/api/v1/detection/analyze", json=payload)
        assert res.status_code == 201
        anomaly = res.json()
        assert anomaly["flow_id"] == payload["flow_id"]
        assert "anomaly_score" in anomaly
        assert isinstance(anomaly["is_anomalous"], bool)
        assert anomaly["status"] == "pending"

        # Verify listing
        list_res = await client.get("/api/v1/detection/anomalies?page=1&page_size=10")
        assert list_res.status_code == 200
        assert list_res.json()["total"] >= 1
