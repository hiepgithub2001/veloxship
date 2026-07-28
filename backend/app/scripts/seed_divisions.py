"""Seed administrative divisions (Provinces and Wards) from Vietnam Provinces online API (2025 v2).

Run: python -m app.scripts.seed_divisions
"""

import asyncio
import json
import urllib.request
from typing import Any

from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.db.session import async_session_factory
from app.models.province import Province
from app.models.ward import Ward

API_URL = "https://provinces.open-api.vn/api/v2/?depth=2"


def fetch_divisions_from_api() -> list[dict[str, Any]]:
    """Fetch provinces and wards data from external API (v2, depth=2)."""
    req = urllib.request.Request(
        API_URL,
        headers={"User-Agent": "VeloxshipSeed/1.0"},
    )
    with urllib.request.urlopen(req, timeout=30) as response:
        if response.status == 200:
            content = response.read().decode("utf-8")
            return json.loads(content)
        raise RuntimeError(f"API request failed with status: {response.status}")


async def seed_divisions() -> tuple[int, int]:
    """Fetch divisions from API as source of truth and upsert into database."""
    print(f"Fetching administrative divisions from {API_URL}...")
    
    # Run synchronous HTTP request in thread pool
    divisions_data = await asyncio.to_thread(fetch_divisions_from_api)
    
    provinces_to_insert = []
    wards_to_insert = []

    for prov in divisions_data:
        prov_code = str(prov["code"])
        prov_name = prov["name"]
        provinces_to_insert.append({
            "code": prov_code,
            "name": prov_name,
            "name_en": prov.get("codename"),
        })

        for ward in prov.get("wards", []):
            ward_code = str(ward["code"])
            ward_name = ward["name"]
            wards_to_insert.append({
                "code": ward_code,
                "name": ward_name,
                "name_en": ward.get("codename"),
                "province_code": prov_code,
            })

    async with async_session_factory() as db:
        # 1. Upsert Provinces
        if provinces_to_insert:
            p_stmt = pg_insert(Province).values(provinces_to_insert)
            p_stmt = p_stmt.on_conflict_do_update(
                index_elements=["code"],
                set_={
                    "name": p_stmt.excluded.name,
                    "name_en": p_stmt.excluded.name_en,
                },
            )
            await db.execute(p_stmt)
            print(f"✓ Upserted {len(provinces_to_insert)} provinces into database.")

        # 2. Upsert Wards in batches
        batch_size = 1000
        total_wards = len(wards_to_insert)
        for i in range(0, total_wards, batch_size):
            batch = wards_to_insert[i : i + batch_size]
            w_stmt = pg_insert(Ward).values(batch)
            w_stmt = w_stmt.on_conflict_do_update(
                index_elements=["code"],
                set_={
                    "name": w_stmt.excluded.name,
                    "name_en": w_stmt.excluded.name_en,
                    "province_code": w_stmt.excluded.province_code,
                },
            )
            await db.execute(w_stmt)

        await db.commit()
        print(f"✓ Upserted {total_wards} wards into database.")

    return len(provinces_to_insert), len(wards_to_insert)


if __name__ == "__main__":
    asyncio.run(seed_divisions())
