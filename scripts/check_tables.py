import asyncio, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "backend"))
from sqlalchemy import text
from app.database.connection import engine

async def check():
    async with engine.connect() as conn:
        r = await conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name"))
        print("=== Supabase PostgreSQL Tables ===")
        for row in r:
            print(f"  [OK] {row[0]}")
        r2 = await conn.execute(text("SELECT COUNT(*) FROM users"))
        print(f"\nUsers count: {r2.scalar()}")
        r3 = await conn.execute(text("SELECT COUNT(*) FROM threats"))
        print(f"Threats count: {r3.scalar()}")
        r4 = await conn.execute(text("SELECT COUNT(*) FROM anomalies"))
        print(f"Anomalies count: {r4.scalar()}")
        r5 = await conn.execute(text("SELECT COUNT(*) FROM evidence"))
        print(f"Evidence count: {r5.scalar()}")

asyncio.run(check())
