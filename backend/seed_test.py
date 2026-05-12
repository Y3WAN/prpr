"""
추천 기능 테스트 환경 세팅 스크립트
실행: python seed_test.py

- 사장 10개 + 트럭 10개 생성 (등록 시 AI 키워드 즉시 생성)
- 테스트 customer 계정 생성 (test@gmail.com / test@gmail.com)
- 일부 트럭에 리뷰를 남겨서 추천 기능이 동작하도록 세팅
"""
import asyncio
import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import httpx
from sqlalchemy import text, select
from app.database import AsyncSessionLocal, engine, Base
from app.models.user import User
from app.models.food_truck import FoodTruck
from app.models.menu import Menu
from app.models.review import Review
from app.auth.password import hash_password
from app.config import settings
from app.services.ai_service import generate_keywords
from seed import TRUCKS


REVIEWS = [
    {"truck_idx": 0, "rating": 5, "content": "떡볶이가 진짜 매콤하고 맛있어요! 국물이 일품입니다."},
    {"truck_idx": 2, "rating": 4, "content": "핫도그 치즈가 엄청 늘어나요. 명동 왔으면 필수!"},
    {"truck_idx": 5, "rating": 5, "content": "점심에 딱 좋아요. BLT 샌드위치 강추합니다."},
]


async def try_generate(name, description, menus, retries=3):
    menu_names = [n for n, _ in menus]
    for attempt in range(retries):
        try:
            kw = await generate_keywords(name, description or "", menu_names, [])
            return kw
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429 and attempt < retries - 1:
                print(f"    429 - 60초 대기 후 재시도...")
                await asyncio.sleep(60)
            else:
                return None
        except Exception:
            return None
    return None


async def seed_test():
    print("[*] DB 초기화 (owner + truck 삭제)...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text("ALTER TABLE food_trucks ADD COLUMN IF NOT EXISTS keywords TEXT"))
        await conn.execute(text("DELETE FROM food_trucks"))
        await conn.execute(text("DELETE FROM users WHERE role = 'owner'"))
        await conn.execute(text("ALTER SEQUENCE food_trucks_id_seq RESTART WITH 1"))
        await conn.execute(text("ALTER SEQUENCE menus_id_seq RESTART WITH 1"))
    print("[OK] 초기화 완료\n")

    truck_ids = []

    async with AsyncSessionLocal() as db:
        print("[*] 트럭 10개 생성 + AI 키워드 즉시 생성 중...")
        for i, t in enumerate(TRUCKS, start=1):
            owner = User(
                email=t["email"],
                password=hash_password(t["email"]),
                nickname=t["nickname"],
                role="owner",
            )
            db.add(owner)
            await db.flush()

            truck = FoodTruck(
                owner_id=owner.id,
                name=t["name"],
                description=t["description"],
                latitude=t["lat"],
                longitude=t["lng"],
                is_open=True,
                account_info=t["account_info"],
            )
            db.add(truck)
            await db.flush()
            truck_ids.append(truck.id)

            for menu_name, price in t["menus"]:
                db.add(Menu(truck_id=truck.id, name=menu_name, price=price))

            await db.commit()

            # 등록 직후 키워드 생성 (새 구조와 동일한 흐름)
            if settings.GEMINI_API_KEY:
                kw = await try_generate(t["name"], t["description"], t["menus"])
                if kw:
                    truck.keywords = json.dumps(kw, ensure_ascii=False)
                    await db.commit()
                    print(f"  [{i:02d}] {t['name']}: {kw}")
                else:
                    print(f"  [{i:02d}] {t['name']}: 키워드 생성 실패 (건너뜀)")
                if i < len(TRUCKS):
                    await asyncio.sleep(5)
            else:
                print(f"  [{i:02d}] {t['name']}: 키워드 없음 (GEMINI_API_KEY 미설정)")

    print(f"\n[OK] 트럭 {len(TRUCKS)}개 생성 완료\n")

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == "test@gmail.com"))
        customer = result.scalar_one_or_none()
        if not customer:
            customer = User(
                email="test@gmail.com",
                password=hash_password("test@gmail.com"),
                nickname="테스트 유저",
                role="customer",
            )
            db.add(customer)
            await db.flush()
            print("[*] customer 계정 생성: test@gmail.com")
        else:
            await db.execute(
                text("DELETE FROM reviews WHERE user_id = :uid").bindparams(uid=customer.id)
            )
            print("[*] 기존 리뷰 삭제 후 재생성")

        print("\n[*] 리뷰 작성 중...")
        for r in REVIEWS:
            truck_id = truck_ids[r["truck_idx"]]
            truck_name = TRUCKS[r["truck_idx"]]["name"]
            db.add(Review(
                truck_id=truck_id,
                user_id=customer.id,
                content=r["content"],
                rating=r["rating"],
            ))
            await db.execute(text("""
                UPDATE food_trucks
                SET review_count = review_count + 1,
                    avg_rating = (avg_rating * review_count + :rating) / (review_count + 1)
                WHERE id = :tid
            """).bindparams(rating=r["rating"], tid=truck_id))
            print(f"  - {truck_name} ({r['rating']}점)")

        await db.commit()

    print("\n[OK] 세팅 완료!")
    print("\n--- 계정 정보 ---")
    print("  [customer] test@gmail.com / test@gmail.com")
    print("  [owner]    boss1~10@gmail.com / (이메일과 동일)")
    print("-----------------")


if __name__ == "__main__":
    asyncio.run(seed_test())
