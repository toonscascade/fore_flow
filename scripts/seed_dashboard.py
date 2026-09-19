import asyncio
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))

from app.core.auth import hash_password
from app.core.constants import EvidenceStatus, ThreatSeverity
from app.database.connection import AsyncSessionLocal
from app.models.anomaly import Anomaly
from app.models.evidence import Evidence
from app.models.threat import Threat
from app.models.user import User
from app.services.blockchain_service import BlockchainService
from sqlalchemy import select


async def seed():
    print("--> Seeding database with initial platform data...")
    async with AsyncSessionLocal() as session:
        # 1. Admin User
        admin_email = "admin@foreflow.security"
        existing = await session.execute(select(User).where(User.email == admin_email))
        if existing.scalar_one_or_none() is None:
            admin = User(
                email=admin_email,
                password_hash=hash_password("SecureAdmin!2026"),
                full_name="Chief SOC Analyst",
                role="ADMIN",
            )
            session.add(admin)
            print(f"    [+] Created Admin User: {admin_email} (password: SecureAdmin!2026)")

        # 2. Realistic Threats
        threat_defs = [
            {
                "title": "Credential Spraying Campaign",
                "description": "Distributed authentication brute force targeting Microsoft 365 and VPN endpoints",
                "severity": ThreatSeverity.CRITICAL.value,
                "confidence_score": 0.96,
                "src_ip": "45.33.12.9",
                "dst_ip": "10.24.8.14",
                "mitre_technique_id": "T1110",
                "mitre_tactic": "INITIAL_ACCESS",
                "iocs": ["45.33.12.9", "185.220.101.14"],
            },
            {
                "title": "Suspicious PowerShell Execution Chain",
                "description": "Obfuscated encoded command invocation spawning child cmd.exe process",
                "severity": ThreatSeverity.HIGH.value,
                "confidence_score": 0.91,
                "src_ip": "10.24.8.51",
                "dst_ip": "10.24.4.22",
                "mitre_technique_id": "T1059.001",
                "mitre_tactic": "EXECUTION",
                "iocs": ["powershell.exe -enc JAB..."],
            },
            {
                "title": "Lateral SMB Enumeration & Pipe Hijack",
                "description": "Rapid IPC$ enumeration across internal 10.24.4.0/24 subnet",
                "severity": ThreatSeverity.HIGH.value,
                "confidence_score": 0.88,
                "src_ip": "10.24.8.51",
                "dst_ip": "10.24.4.0/24",
                "mitre_technique_id": "T1021.002",
                "mitre_tactic": "LATERAL_MOVEMENT",
                "iocs": ["\\10.24.4.22\IPC$"],
            },
            {
                "title": "DNS Beaconing to Dynamic Domain",
                "description": "Regular interval 30-second jitter outbound DNS TXT requests",
                "severity": ThreatSeverity.MEDIUM.value,
                "confidence_score": 0.82,
                "src_ip": "10.24.5.77",
                "dst_ip": "8.8.8.8",
                "mitre_technique_id": "T1071.004",
                "mitre_tactic": "COMMAND_AND_CONTROL",
                "iocs": ["cdn-sync[.]net"],
            },
        ]

        created_threats = []
        for td in threat_defs:
            t = Threat(**td)
            session.add(t)
            created_threats.append(t)

        await session.flush()
        print(f"    [+] Created {len(created_threats)} threats")

        # 3. Anomalies
        now = datetime.now(timezone.utc)
        anomalies_defs = [
            {"flow_id": "flow-auth-01", "src_ip": "45.33.12.9", "dst_ip": "10.24.8.14", "src_port": 51234, "dst_port": 443, "protocol": "TCP", "anomaly_score": 0.94, "is_anomalous": True, "status": "confirmed", "detected_at": now - timedelta(minutes=15)},
            {"flow_id": "flow-psh-02", "src_ip": "10.24.8.51", "dst_ip": "10.24.4.22", "src_port": 49811, "dst_port": 445, "protocol": "TCP", "anomaly_score": 0.89, "is_anomalous": True, "status": "confirmed", "detected_at": now - timedelta(minutes=30)},
            {"flow_id": "flow-dns-03", "src_ip": "10.24.5.77", "dst_ip": "8.8.8.8", "src_port": 55102, "dst_port": 53, "protocol": "UDP", "anomaly_score": 0.78, "is_anomalous": True, "status": "pending", "detected_at": now - timedelta(minutes=45)},
            {"flow_id": "flow-norm-04", "src_ip": "10.24.1.20", "dst_ip": "10.24.1.1", "src_port": 52100, "dst_port": 80, "protocol": "TCP", "anomaly_score": 0.12, "is_anomalous": False, "status": "resolved", "detected_at": now - timedelta(hours=1)},
            {"flow_id": "flow-norm-05", "src_ip": "10.24.2.14", "dst_ip": "142.250.190.46", "src_port": 53210, "dst_port": 443, "protocol": "TCP", "anomaly_score": 0.08, "is_anomalous": False, "status": "resolved", "detected_at": now - timedelta(hours=2)},
        ]
        for ad in anomalies_defs:
            a = Anomaly(**ad)
            session.add(a)

        print(f"    [+] Created {len(anomalies_defs)} flow anomalies")

        # 4. Evidence anchored on-chain
        blockchain = BlockchainService()
        if blockchain.is_connected() and blockchain.contract is not None:
            ev_payload = {
                "campaign": "Credential Spray 2026-09",
                "attack_vector": "T1110",
                "origin_ips": ["45.33.12.9", "185.220.101.14"],
                "target_account": "admin@foreflow.security",
                "timestamp": now.isoformat(),
            }
            c_hash = blockchain.compute_evidence_hash(ev_payload)
            anchor_res = blockchain.anchor_evidence(c_hash)

            ev = Evidence(
                threat_id=created_threats[0].id,
                title="Credential Spray Telemetry & Forensics",
                description="Correlated authentication telemetry anchored on Ethereum testnet",
                payload=ev_payload,
                content_hash=c_hash,
                status=EvidenceStatus.ANCHORED.value,
                blockchain_tx_hash=anchor_res["tx_hash"],
                blockchain_block_number=anchor_res["block_number"],
                anchored_at=anchor_res["anchored_at"],
            )
            session.add(ev)
            print(f"    [+] Anchored evidence record on blockchain: {anchor_res['tx_hash'][:16]}...")

        await session.commit()
        print("--> Seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed())
