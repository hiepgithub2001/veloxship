"""Seed administrative divisions (provinces and wards) from the Vietnam Provinces API.

The public API (`/api/v2/?depth=2`) returns the post-2025 two-level layout: each
province carries its wards directly (there is no district level any more). Provinces
and wards are upserted by `code`, so re-running this script is safe and refreshes
names when the API changes them.

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
REQUEST_TIMEOUT_SECONDS = 30
WARD_BATCH_SIZE = 1000


def fetch_divisions() -> list[dict[str, Any]]:
    """Download provinces (with their wards) from the external API."""
    request = urllib.request.Request(
        API_URL, headers={"User-Agent": "VeloxshipSeed/1.0"}
    )
    with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        if response.status != 200:
            raise RuntimeError(f"API request failed with status: {response.status}")
        payload = json.loads(response.read().decode("utf-8"))

    if not isinstance(payload, list) or not payload:
        raise RuntimeError(
            "API returned an unexpected payload (expected a non-empty list)"
        )
    return payload


async def seed_divisions() -> tuple[int, int]:
    """Fetch administrative divisions and upsert them into the database."""
    print(f"Fetching administrative divisions from {API_URL}...")
    divisions_data = await asyncio.to_thread(fetch_divisions)

    provinces: list[dict[str, Any]] = []
    wards: list[dict[str, Any]] = []

    for province in divisions_data:
        province_code = str(province["code"])
        provinces.append(
            {
                "code": province_code,
                "name": province["name"],
                "name_en": province.get("codename"),
            }
        )
        for ward in province.get("wards", []):
            wards.append(
                {
                    "code": str(ward["code"]),
                    "name": ward["name"],
                    "name_en": ward.get("codename"),
                    "province_code": province_code,
                }
            )

    async with async_session_factory() as db:
        province_stmt = pg_insert(Province).values(provinces)
        province_stmt = province_stmt.on_conflict_do_update(
            index_elements=["code"],
            set_={
                "name": province_stmt.excluded.name,
                "name_en": province_stmt.excluded.name_en,
            },
        )
        await db.execute(province_stmt)

        for start in range(0, len(wards), WARD_BATCH_SIZE):
            batch = wards[start : start + WARD_BATCH_SIZE]
            ward_stmt = pg_insert(Ward).values(batch)
            ward_stmt = ward_stmt.on_conflict_do_update(
                index_elements=["code"],
                set_={
                    "name": ward_stmt.excluded.name,
                    "name_en": ward_stmt.excluded.name_en,
                    "province_code": ward_stmt.excluded.province_code,
                },
            )
            await db.execute(ward_stmt)

        await db.commit()

    print(f"✓ Upserted {len(provinces)} provinces and {len(wards)} wards.")
    return len(provinces), len(wards)


def main() -> None:
    asyncio.run(seed_divisions())


if __name__ == "__main__":
    main()
