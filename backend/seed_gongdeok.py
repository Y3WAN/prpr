"""
공덕역 근처 푸드트럭 1개 + 리뷰 5개 생성
실행: python seed_gongdeok.py
"""
import asyncio
import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import text
from app.database import AsyncSessionLocal
from app.auth.password import hash_password

OWNER = {
    "email": "gongdeok_owner@test.com",
    "password": "Test1234!",
    "nickname": "공덕 마라탕 사장",
    "truck": {
        "name": "공덕역 마라탕",
        "description": "얼얼하고 깊은 국물의 정통 마라탕. 공덕역 직장인들의 점심 성지!",
        "latitude": 37.5449,
        "longitude": 126.9514,
        "keywords": "마라탕,마라,중식,매운맛,점심",
        "account_info": "카카오페이 010-7070-7070",
    },
    "menus": [
        {"name": "마라탕 (소)", "price": 8000},
        {"name": "마라탕 (대)", "price": 12000},
        {"name": "마라샹궈", "price": 13000},
        {"name": "마라탕 + 공기밥", "price": 9000},
    ],
}

CUSTOMERS = [
    {"email": "gongdeok_c1@test.com", "password": "Test1234!", "nickname": "공덕 직장인"},
    {"email": "gongdeok_c2@test.com", "password": "Test1234!", "nickname": "마라탕러버"},
    {"email": "gongdeok_c3@test.com", "password": "Test1234!", "nickname": "점심탐방러"},
    {"email": "gongdeok_c4@test.com", "password": "Test1234!", "nickname": "공덕맛집헌터"},
    {"email": "gongdeok_c5@test.com", "password": "Test1234!", "nickname": "얼큰한게좋아"},
]

REVIEWS = [
    {"rating": 5, "content": "공덕역 근처에서 이런 마라탕을 먹을 수 있다니! 국물이 진짜 얼얼하고 깊어요. 점심마다 찾아오게 될 것 같아요."},
    {"rating": 5, "content": "재료도 신선하고 마라 향이 진짜 제대로예요. 마라샹궈도 시켜봤는데 두 개 다 완벽합니다. 강력 추천!"},
    {"rating": 4, "content": "매운 걸 좋아하는 분들한테 완전 강추. 공기밥이랑 같이 먹으면 한 끼로 딱이에요. 웨이팅이 좀 있긴 한데 그만한 가치!"},
    {"rating": 4, "content": "처음엔 살짝 짤까 걱정했는데 맛 밸런스가 좋아요. 재료 양도 넉넉하고 가성비 최고. 다음에 또 올게요."},
    {"rating": 5, "content": "진짜 오래 기억될 맛이에요. 마라 특유의 향이 중독적이고 면이 쫄깃해서 너무 맛있었어요. 공덕역 필수 방문 코스!"},
]


async def main():
    async with AsyncSessionLocal() as session:
        # 사장 계정 생성
        result = await session.execute(
            text("SELECT id FROM users WHERE email = :email"),
            {"email": OWNER["email"]},
        )
        row = result.fetchone()
        if row:
            owner_id = row[0]
            print(f"기존 사장 계정 사용: {OWNER['email']} (id={owner_id})")
        else:
            res = await session.execute(
                text(
                    "INSERT INTO users (email, password, nickname, role) "
                    "VALUES (:email, :password, :nickname, 'owner') RETURNING id"
                ),
                {
                    "email": OWNER["email"],
                    "password": hash_password(OWNER["password"]),
                    "nickname": OWNER["nickname"],
                },
            )
            owner_id = res.fetchone()[0]
            print(f"사장 계정 생성: {OWNER['email']} (id={owner_id})")

        # 트럭 생성
        result = await session.execute(
            text("SELECT id FROM food_trucks WHERE owner_id = :owner_id"),
            {"owner_id": owner_id},
        )
        existing = result.fetchone()
        if existing:
            truck_id = existing[0]
            print(f"기존 트럭 사용: {OWNER['truck']['name']} (id={truck_id})")
        else:
            t = OWNER["truck"]
            res = await session.execute(
                text(
                    "INSERT INTO food_trucks (owner_id, name, description, latitude, longitude, "
                    "is_open, avg_rating, review_count, account_info, keywords) "
                    "VALUES (:owner_id, :name, :description, :latitude, :longitude, "
                    "true, 0.0, 0, :account_info, :keywords) RETURNING id"
                ),
                {
                    "owner_id": owner_id,
                    "name": t["name"],
                    "description": t["description"],
                    "latitude": t["latitude"],
                    "longitude": t["longitude"],
                    "account_info": t["account_info"],
                    "keywords": json.dumps(t["keywords"].split(","), ensure_ascii=False),
                },
            )
            truck_id = res.fetchone()[0]
            print(f"트럭 생성: {t['name']} (id={truck_id})")

            for m in OWNER["menus"]:
                await session.execute(
                    text("INSERT INTO menus (truck_id, name, price) VALUES (:truck_id, :name, :price)"),
                    {"truck_id": truck_id, "name": m["name"], "price": m["price"]},
                )
                print(f"  메뉴: {m['name']} - {m['price']}원")

        await session.commit()

        # 손님 계정 + 리뷰 생성
        print("\n리뷰 작성 중...")
        for i, (customer, review) in enumerate(zip(CUSTOMERS, REVIEWS)):
            res = await session.execute(
                text("SELECT id FROM users WHERE email = :email"),
                {"email": customer["email"]},
            )
            row = res.fetchone()
            if row:
                customer_id = row[0]
            else:
                res = await session.execute(
                    text(
                        "INSERT INTO users (email, password, nickname, role) "
                        "VALUES (:email, :password, :nickname, 'customer') RETURNING id"
                    ),
                    {
                        "email": customer["email"],
                        "password": hash_password(customer["password"]),
                        "nickname": customer["nickname"],
                    },
                )
                customer_id = res.fetchone()[0]

            dup = await session.execute(
                text("SELECT id FROM reviews WHERE truck_id = :tid AND user_id = :uid"),
                {"tid": truck_id, "uid": customer_id},
            )
            if dup.fetchone():
                print(f"  리뷰 이미 존재, 스킵: {customer['email']}")
                continue

            await session.execute(
                text(
                    "INSERT INTO reviews (truck_id, user_id, rating, content, created_at, updated_at) "
                    "VALUES (:tid, :uid, :rating, :content, NOW(), NOW())"
                ),
                {"tid": truck_id, "uid": customer_id, "rating": review["rating"], "content": review["content"]},
            )
            await session.execute(
                text(
                    "UPDATE food_trucks "
                    "SET review_count = review_count + 1, "
                    "    avg_rating = (avg_rating * review_count + :rating) / (review_count + 1) "
                    "WHERE id = :tid"
                ),
                {"rating": review["rating"], "tid": truck_id},
            )
            print(f"  리뷰 {i+1}: {customer['nickname']} ({review['rating']}점)")

        await session.commit()

    print("\n완료!")
    print(f"  [사장] {OWNER['email']}  /  {OWNER['password']}")
    for c in CUSTOMERS:
        print(f"  [손님] {c['email']}  /  {c['password']}")


if __name__ == "__main__":
    asyncio.run(main())
