import pytest
from uuid import uuid4
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.core.auth import create_session_token, hash_password, token_digest
from app.database.connection import AsyncSessionLocal
from app.models.user import User, UserSession
from app.models.threat import Threat


@pytest.mark.asyncio
async def test_blockchain_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/health/blockchain")
        assert res.status_code == 200
        assert res.json()["blockchain"] == "connected"


@pytest.mark.asyncio
async def test_evidence_creation_anchoring_and_on_chain_verification():
    admin_email = f"admin-{uuid4().hex[:8]}@foreflow.security"
    password = "Admin!Password2026"

    async with AsyncSessionLocal() as session:
        admin = User(
            email=admin_email,
            password_hash=hash_password(password),
            full_name="Admin Blockchain Tester",
            role="ADMIN",
        )
        session.add(admin)
        await session.flush()
        token, jti, expires = create_session_token(admin.id)
        session.add(UserSession(user_id=admin.id, jti=jti, token_hash=token_digest(token), expires_at=expires))

        threat = Threat(
            title="Ransomware Exfiltration Attempt",
            description="Detected high outbound volume to suspicious external IP",
            severity="critical",
            confidence_score=0.95,
        )
        session.add(threat)
        await session.commit()
        threat_id = threat.id

    transport = ASGITransport(app=app)
    cookies = {"foreflow_session": token}
    async with AsyncClient(transport=transport, base_url="http://test", cookies=cookies) as client:
        # 1. Create evidence
        payload = {
            "threat_id": threat_id,
            "title": "Malware PCAP Exfiltration Segment",
            "description": "Captured suspicious flow payload for on-chain anchoring",
            "payload": {
                "src_ip": "192.168.1.100",
                "dst_ip": "45.33.32.156",
                "bytes_transferred": 1420500,
                "signature": "WIN32.TROJAN.EMOTET",
                "nonce": uuid4().hex,
            },
        }
        create_res = await client.post("/api/v1/evidence", json=payload)
        assert create_res.status_code == 201
        evidence = create_res.json()
        evidence_id = evidence["id"]
        assert evidence["status"] == "hashed"
        assert len(evidence["content_hash"]) == 64

        # 2. Anchor evidence on-chain
        anchor_res = await client.post(f"/api/v1/evidence/{evidence_id}/anchor")
        assert anchor_res.status_code == 200
        anchored = anchor_res.json()
        assert anchored["status"] == "anchored"
        assert anchored["blockchain_tx_hash"] is not None
        assert anchored["blockchain_block_number"] is not None
        assert anchored["anchored_at"] is not None

        # 3. Verify on-chain tamper proofing
        verify_res = await client.get(f"/api/v1/evidence/{evidence_id}/verify")
        assert verify_res.status_code == 200
        verification = verify_res.json()
        assert verification["is_valid"] is True
        assert verification["on_chain_hash"] == evidence["content_hash"]
        assert "Verified on-chain" in verification["message"]
