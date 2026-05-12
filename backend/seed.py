"""
테스트 데이터 초기화 + 시드 스크립트
실행: python seed.py
"""
import asyncio
import sys
import os
import json

sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import text
from app.database import AsyncSessionLocal, engine, Base
from app.models.user import User
from app.models.food_truck import FoodTruck
from app.models.menu import Menu
from app.auth.password import hash_password
from app.config import settings
from app.services.ai_service import generate_keywords

TRUCKS = [
    {
        "email": "boss1@gmail.com",
        "nickname": "강남 떡볶이 사장",
        "name": "강남 매콤 떡볶이",
        "description": "30년 전통 할머니 비법 떡볶이. 매콤달콤한 국물이 일품입니다.",
        "lat": 37.4979, "lng": 127.0276,
        "account_info": "카카오페이 010-1111-0001",
        "menus": [("떡볶이", 4000), ("순대", 3500), ("튀김 세트", 4500), ("쫄면", 5000)],
    },
    {
        "email": "boss2@gmail.com",
        "nickname": "홍대 타코야끼 사장",
        "name": "홍대 타코야끼 본점",
        "description": "오사카 직전수! 바삭한 겉면과 촉촉한 속살. 줄 서는 맛집.",
        "lat": 37.5563, "lng": 126.9227,
        "account_info": "토스 010-2222-0002",
        "menus": [("타코야끼 6개", 3500), ("타코야끼 12개", 6500), ("오코노미야끼", 7000)],
    },
    {
        "email": "boss3@gmail.com",
        "nickname": "명동 핫도그 사장",
        "name": "명동 길거리 핫도그",
        "description": "관광객도 인정한 명동 명물 핫도그. 치즈가 쭉쭉 늘어납니다.",
        "lat": 37.5636, "lng": 126.9857,
        "account_info": "국민 010-3333-0003",
        "menus": [("치즈 핫도그", 2500), ("감자 핫도그", 3000), ("소시지 핫도그", 2000), ("할라피뇨 핫도그", 3000)],
    },
    {
        "email": "boss4@gmail.com",
        "nickname": "신촌 붕어빵 사장",
        "name": "신촌역 붕어빵 & 계란빵",
        "description": "겨울엔 역시 붕어빵! 팥·슈크림 두 가지 맛. 따뜻하게 드세요.",
        "lat": 37.5555, "lng": 126.9360,
        "account_info": "현금만 가능",
        "menus": [("팥 붕어빵 3개", 2000), ("슈크림 붕어빵 3개", 2000), ("계란빵", 1500), ("호떡", 1500)],
    },
    {
        "email": "boss5@gmail.com",
        "nickname": "이태원 케밥 사장",
        "name": "이태원 정통 터키 케밥",
        "description": "이태원 20년 터키인 셰프가 직접 만드는 정통 되너 케밥.",
        "lat": 37.5340, "lng": 126.9944,
        "account_info": "카드·현금 모두 가능",
        "menus": [("되너 케밥", 7000), ("치킨 케밥", 7500), ("야채 케밥", 6000), ("케밥 플레이트", 12000)],
    },
    {
        "email": "boss6@gmail.com",
        "nickname": "여의도 샌드위치 사장",
        "name": "여의도 직장인 샌드위치",
        "description": "점심시간 직장인을 위한 든든한 샌드위치. 매일 신선한 재료로 준비합니다.",
        "lat": 37.5215, "lng": 126.9248,
        "account_info": "토스·카카오페이 010-6666-0006",
        "menus": [("BLT 샌드위치", 5500), ("에그 샌드위치", 5000), ("클럽 샌드위치", 6500), ("아메리카노", 2000)],
    },
    {
        "email": "boss7@gmail.com",
        "nickname": "건대 닭꼬치 사장",
        "name": "건대 야키토리 닭꼬치",
        "description": "숯불향 가득한 닭꼬치. 야식으로도 최고! 맥주 한 캔이랑 함께하세요.",
        "lat": 37.5406, "lng": 127.0696,
        "account_info": "신한 010-7777-0007",
        "menus": [("닭꼬치 2개", 3000), ("닭꼬치 5개", 7000), ("닭근위 꼬치", 3500), ("파닭 꼬치", 4000)],
    },
    {
        "email": "boss8@gmail.com",
        "nickname": "신림 순대볶음 사장",
        "name": "신림동 순대볶음 트럭",
        "description": "신림동 포장마차 감성 그대로! 매콤한 순대볶음 한 접시.",
        "lat": 37.4841, "lng": 126.9294,
        "account_info": "현금 010-8888-0008",
        "menus": [("순대볶음 (소)", 6000), ("순대볶음 (대)", 9000), ("순대국밥", 7000)],
    },
    {
        "email": "boss9@gmail.com",
        "nickname": "잠실 와플 사장",
        "name": "잠실 벨기에 와플",
        "description": "겉바속촉 벨기에 정통 와플. 생크림·딸기·누텔라 토핑 다양.",
        "lat": 37.5133, "lng": 127.1001,
        "account_info": "카카오페이 010-9999-0009",
        "menus": [("플레인 와플", 3500), ("딸기크림 와플", 5000), ("누텔라 와플", 4500), ("아이스크림 와플", 5500)],
    },
    {
        "email": "boss10@gmail.com",
        "nickname": "마포 곱창 사장",
        "name": "마포 소곱창 구이 트럭",
        "description": "연탄불에 직접 굽는 소곱창. 깊은 불향과 쫄깃한 식감이 예술입니다.",
        "lat": 37.5490, "lng": 126.9119,
        "account_info": "카드 가능 010-1010-0010",
        "menus": [("소곱창 구이", 12000), ("대창 구이", 13000), ("막창 구이", 11000), ("소주", 4000)],
    },
]


async def reset_and_seed():
    print("[*] DB 초기화 중 (owner + truck 데이터만 삭제)...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text("ALTER TABLE food_trucks ADD COLUMN IF NOT EXISTS keywords TEXT"))
        # food_trucks 삭제 시 reviews, menus도 CASCADE 삭제됨
        await conn.execute(text("DELETE FROM food_trucks"))
        await conn.execute(text("DELETE FROM users WHERE role = 'owner'"))
        # 시퀀스 리셋 (선택)
        await conn.execute(text("ALTER SEQUENCE food_trucks_id_seq RESTART WITH 1"))
        await conn.execute(text("ALTER SEQUENCE menus_id_seq RESTART WITH 1"))
    print("[OK] 사장/가게 데이터 삭제 완료\n")

    async with AsyncSessionLocal() as db:
        for i, t in enumerate(TRUCKS, start=1):
            user = User(
                email=t["email"],
                password=hash_password(t["email"]),
                nickname=t["nickname"],
                role="owner",
            )
            db.add(user)
            await db.flush()

            truck = FoodTruck(
                owner_id=user.id,
                name=t["name"],
                description=t["description"],
                latitude=t["lat"],
                longitude=t["lng"],
                is_open=True,
                account_info=t["account_info"],
            )
            db.add(truck)
            await db.flush()

            for menu_name, price in t["menus"]:
                db.add(Menu(truck_id=truck.id, name=menu_name, price=price))

            print(f"  [{i:02d}] {t['email']} -> {t['name']}")

        await db.commit()

    print(f"\n[OK] 시드 완료! 가게 {len(TRUCKS)}개 생성됨")

    if settings.GEMINI_API_KEY:
        import httpx
        print("\n[*] AI 키워드 생성 중 (가게당 5초 간격, 429시 60초 대기 재시도)...")
        async with AsyncSessionLocal() as db:
            from sqlalchemy import select as sa_select
            result = await db.execute(
                sa_select(FoodTruck).order_by(FoodTruck.id)
            )
            trucks_db = result.scalars().all()

            for i, truck_db in enumerate(trucks_db):
                menus_in_db = TRUCKS[i]["menus"]
                menu_names = [n for n, _ in menus_in_db]
                for attempt in range(5):
                    try:
                        keywords = await generate_keywords(truck_db.name, truck_db.description or "", menu_names, [])
                        truck_db.keywords = json.dumps(keywords, ensure_ascii=False)
                        await db.commit()
                        print(f"  [{i+1:02d}] {truck_db.name}: {keywords}")
                        break
                    except httpx.HTTPStatusError as e:
                        if e.response.status_code == 429 and attempt < 4:
                            print(f"  [{i+1:02d}] 429 - 60초 대기 후 재시도 ({attempt+1}/5)...")
                            await asyncio.sleep(60)
                        else:
                            print(f"  [{i+1:02d}] {truck_db.name}: 키워드 생성 실패 - {e}")
                            break
                    except Exception as e:
                        print(f"  [{i+1:02d}] {truck_db.name}: 키워드 생성 실패 - {e}")
                        break
                if i < len(trucks_db) - 1:
                    await asyncio.sleep(5)
        print("[OK] 키워드 생성 완료")
    else:
        print("[!] GEMINI_API_KEY 없음 - 키워드 생성 건너뜀")

    print("\n--- 계정 정보 ---")
    for t in TRUCKS:
        print(f"  ID: {t['email']}  /  PW: {t['email']}")
    print("-----------------")


if __name__ == "__main__":
    asyncio.run(reset_and_seed())
