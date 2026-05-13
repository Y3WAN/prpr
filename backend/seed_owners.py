"""테스트 사장 계정 5개 + 푸드트럭 + 메뉴 생성"""
import asyncio
import json
import bcrypt
from sqlalchemy import text
from app.database import AsyncSessionLocal

OWNERS = [
    {
        "email": "owner1@test.com", "password": "Test1234!", "nickname": "사장님1",
        "truck": {
            "name": "맛있는 타코야키",
            "description": "바삭바삭한 타코야키 전문점입니다.",
            "latitude": 37.5665, "longitude": 126.9780,
            "keywords": "타코야키,일식,간식",
            "account_info": "카카오페이 010-1111-1111",
        },
        "menus": [
            {"name": "타코야키 6개", "price": 4000},
            {"name": "타코야키 12개", "price": 7500},
            {"name": "치즈 타코야키 6개", "price": 5000},
        ],
    },
    {
        "email": "owner2@test.com", "password": "Test1234!", "nickname": "사장님2",
        "truck": {
            "name": "길거리 토스트",
            "description": "계란 듬뿍 달걀 토스트 전문점.",
            "latitude": 37.5700, "longitude": 126.9820,
            "keywords": "토스트,아침,브런치",
            "account_info": "카카오페이 010-2222-2222",
        },
        "menus": [
            {"name": "기본 토스트", "price": 3000},
            {"name": "햄치즈 토스트", "price": 4000},
            {"name": "에그 토스트", "price": 3500},
        ],
    },
    {
        "email": "owner3@test.com", "password": "Test1234!", "nickname": "사장님3",
        "truck": {
            "name": "매콤 떡볶이",
            "description": "쫄깃하고 매콤한 국물 떡볶이.",
            "latitude": 37.5630, "longitude": 126.9750,
            "keywords": "떡볶이,분식,매운맛",
            "account_info": "카카오페이 010-3333-3333",
        },
        "menus": [
            {"name": "떡볶이 (1인)", "price": 4500},
            {"name": "떡볶이 + 순대 세트", "price": 7000},
            {"name": "치즈 떡볶이", "price": 5500},
        ],
    },
    {
        "email": "owner4@test.com", "password": "Test1234!", "nickname": "사장님4",
        "truck": {
            "name": "수제버거 가게",
            "description": "직접 구운 패티가 들어간 수제버거.",
            "latitude": 37.5590, "longitude": 126.9700,
            "keywords": "버거,수제,점심",
            "account_info": "카카오페이 010-4444-4444",
        },
        "menus": [
            {"name": "클래식 버거", "price": 6000},
            {"name": "치즈버거", "price": 7000},
            {"name": "더블 패티 버거", "price": 9000},
        ],
    },
    {
        "email": "owner5@test.com", "password": "Test1234!", "nickname": "사장님5",
        "truck": {
            "name": "달콤 붕어빵",
            "description": "팥, 슈크림, 피자 붕어빵 판매.",
            "latitude": 37.5720, "longitude": 126.9850,
            "keywords": "붕어빵,디저트,간식",
            "account_info": "카카오페이 010-5555-5555",
        },
        "menus": [
            {"name": "팥 붕어빵 5개", "price": 3000},
            {"name": "슈크림 붕어빵 5개", "price": 3500},
            {"name": "피자 붕어빵 3개", "price": 3000},
        ],
    },
]


def hash_pw(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt(rounds=12)).decode()


async def main():
    async with AsyncSessionLocal() as session:
        for o in OWNERS:
            # 사용자 생성 또는 조회
            result = await session.execute(
                text("SELECT id FROM users WHERE email = :email"),
                {"email": o["email"]},
            )
            row = result.fetchone()
            if row:
                user_id = row[0]
                print(f"기존 계정 사용: {o['email']} (id={user_id})")
            else:
                res = await session.execute(
                    text(
                        "INSERT INTO users (email, password, nickname, role) "
                        "VALUES (:email, :password, :nickname, 'owner') RETURNING id"
                    ),
                    {"email": o["email"], "password": hash_pw(o["password"]), "nickname": o["nickname"]},
                )
                user_id = res.fetchone()[0]
                print(f"계정 생성: {o['email']} (id={user_id})")

            # 트럭 생성 (이미 있으면 스킵)
            result = await session.execute(
                text("SELECT id FROM food_trucks WHERE owner_id = :owner_id"),
                {"owner_id": user_id},
            )
            if result.fetchone():
                print(f"  트럭 이미 존재, 스킵: {o['truck']['name']}")
                continue

            t = o["truck"]
            res = await session.execute(
                text(
                    "INSERT INTO food_trucks (owner_id, name, description, latitude, longitude, "
                    "is_open, avg_rating, review_count, account_info, keywords) "
                    "VALUES (:owner_id, :name, :description, :latitude, :longitude, "
                    "true, 0.0, 0, :account_info, :keywords) RETURNING id"
                ),
                {
                    "owner_id": user_id,
                    "name": t["name"],
                    "description": t["description"],
                    "latitude": t["latitude"],
                    "longitude": t["longitude"],
                    "account_info": t["account_info"],
                    "keywords": json.dumps(t["keywords"].split(","), ensure_ascii=False),
                },
            )
            truck_id = res.fetchone()[0]
            print(f"  트럭 생성: {t['name']} (id={truck_id})")

            # 메뉴 생성
            for m in o["menus"]:
                await session.execute(
                    text(
                        "INSERT INTO menus (truck_id, name, price) "
                        "VALUES (:truck_id, :name, :price)"
                    ),
                    {"truck_id": truck_id, "name": m["name"], "price": m["price"]},
                )
                print(f"    메뉴: {m['name']} - {m['price']}원")

        await session.commit()
    print("\n완료!")


asyncio.run(main())
