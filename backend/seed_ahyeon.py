"""
아현역 근처 테스트용 사장 계정 10개 + 푸드트럭 + 메뉴 생성
실행: python seed_ahyeon.py

- 기존 데이터 삭제 없이 추가만 수행
- 아현역(37.5564, 126.9561) 반경 300m 이내에 분산 배치
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import text
from app.database import AsyncSessionLocal
from app.auth.password import hash_password

OWNERS = [
    {
        "email": "ahyeon1@test.com", "password": "Test1234!", "nickname": "아현 떡볶이 사장",
        "truck": {
            "name": "아현역 매콤 떡볶이",
            "description": "쫄깃하고 매콤한 국물 떡볶이. 아현역 대표 분식.",
            "latitude": 37.5564, "longitude": 126.9561,
            "keywords": "떡볶이,분식,매운맛,국물",
            "account_info": "카카오페이 010-1001-1001",
        },
        "menus": [
            {"name": "떡볶이 (1인)", "price": 4500},
            {"name": "떡볶이 + 순대 세트", "price": 7000},
            {"name": "치즈 떡볶이", "price": 5500},
            {"name": "라볶이", "price": 5000},
        ],
    },
    {
        "email": "ahyeon2@test.com", "password": "Test1234!", "nickname": "아현 핫도그 사장",
        "truck": {
            "name": "아현 길거리 핫도그",
            "description": "치즈가 쭉쭉 늘어나는 황금 핫도그. 아현역 명물!",
            "latitude": 37.5570, "longitude": 126.9553,
            "keywords": "핫도그,치즈,간식,길거리",
            "account_info": "토스 010-2002-2002",
        },
        "menus": [
            {"name": "치즈 핫도그", "price": 2500},
            {"name": "감자 핫도그", "price": 3000},
            {"name": "할라피뇨 핫도그", "price": 3000},
            {"name": "소시지 핫도그", "price": 2000},
        ],
    },
    {
        "email": "ahyeon3@test.com", "password": "Test1234!", "nickname": "아현 타코야키 사장",
        "truck": {
            "name": "아현 타코야키",
            "description": "오사카식 바삭 촉촉 타코야키. 갓 구운 따뜻한 맛.",
            "latitude": 37.5558, "longitude": 126.9572,
            "keywords": "타코야키,일식,간식,오사카",
            "account_info": "카카오페이 010-3003-3003",
        },
        "menus": [
            {"name": "타코야키 6개", "price": 4000},
            {"name": "타코야키 12개", "price": 7500},
            {"name": "치즈 타코야키 6개", "price": 5000},
        ],
    },
    {
        "email": "ahyeon4@test.com", "password": "Test1234!", "nickname": "아현 닭꼬치 사장",
        "truck": {
            "name": "아현 숯불 닭꼬치",
            "description": "숯불향 가득한 야키토리 스타일 닭꼬치. 야식으로 최고!",
            "latitude": 37.5575, "longitude": 126.9565,
            "keywords": "닭꼬치,야키토리,숯불,야식",
            "account_info": "신한 010-4004-4004",
        },
        "menus": [
            {"name": "닭꼬치 2개", "price": 3000},
            {"name": "닭꼬치 5개", "price": 7000},
            {"name": "파닭 꼬치", "price": 4000},
            {"name": "닭껍질 꼬치", "price": 3500},
        ],
    },
    {
        "email": "ahyeon5@test.com", "password": "Test1234!", "nickname": "아현 수제버거 사장",
        "truck": {
            "name": "아현 수제버거",
            "description": "직접 구운 두툼한 패티가 들어간 수제버거. 점심 특선!",
            "latitude": 37.5551, "longitude": 126.9548,
            "keywords": "버거,수제,점심,패티",
            "account_info": "카드 가능 010-5005-5005",
        },
        "menus": [
            {"name": "클래식 버거", "price": 6000},
            {"name": "치즈버거", "price": 7000},
            {"name": "더블 패티 버거", "price": 9000},
            {"name": "콜라 세트 추가", "price": 2000},
        ],
    },
    {
        "email": "ahyeon6@test.com", "password": "Test1234!", "nickname": "아현 붕어빵 사장",
        "truck": {
            "name": "아현역 붕어빵",
            "description": "팥·슈크림·피자 세 가지 맛 붕어빵. 따끈따끈 갓 구워 드려요.",
            "latitude": 37.5560, "longitude": 126.9580,
            "keywords": "붕어빵,디저트,간식,팥",
            "account_info": "현금만 가능",
        },
        "menus": [
            {"name": "팥 붕어빵 5개", "price": 3000},
            {"name": "슈크림 붕어빵 5개", "price": 3500},
            {"name": "피자 붕어빵 3개", "price": 3000},
            {"name": "계란빵", "price": 1500},
        ],
    },
    {
        "email": "ahyeon7@test.com", "password": "Test1234!", "nickname": "아현 케밥 사장",
        "truck": {
            "name": "아현 터키 케밥",
            "description": "이태원 출신 터키 셰프의 정통 되너 케밥. 든든한 한 끼!",
            "latitude": 37.5568, "longitude": 126.9545,
            "keywords": "케밥,터키,이태원,할랄",
            "account_info": "카드·현금 모두 가능",
        },
        "menus": [
            {"name": "되너 케밥", "price": 7000},
            {"name": "치킨 케밥", "price": 7500},
            {"name": "야채 케밥", "price": 6000},
            {"name": "케밥 플레이트", "price": 12000},
        ],
    },
    {
        "email": "ahyeon8@test.com", "password": "Test1234!", "nickname": "아현 와플 사장",
        "truck": {
            "name": "아현 벨기에 와플",
            "description": "겉은 바삭 속은 촉촉한 벨기에 정통 와플. 다양한 토핑 선택!",
            "latitude": 37.5545, "longitude": 126.9558,
            "keywords": "와플,디저트,벨기에,카페",
            "account_info": "카카오페이 010-8008-8008",
        },
        "menus": [
            {"name": "플레인 와플", "price": 3500},
            {"name": "딸기크림 와플", "price": 5000},
            {"name": "누텔라 와플", "price": 4500},
            {"name": "아이스크림 와플", "price": 5500},
        ],
    },
    {
        "email": "ahyeon9@test.com", "password": "Test1234!", "nickname": "아현 샌드위치 사장",
        "truck": {
            "name": "아현 직장인 샌드위치",
            "description": "매일 신선한 재료로 만드는 든든한 샌드위치. 점심 픽업 가능!",
            "latitude": 37.5580, "longitude": 126.9570,
            "keywords": "샌드위치,점심,브런치,직장인",
            "account_info": "토스 010-9009-9009",
        },
        "menus": [
            {"name": "BLT 샌드위치", "price": 5500},
            {"name": "에그 샌드위치", "price": 5000},
            {"name": "클럽 샌드위치", "price": 6500},
            {"name": "아메리카노", "price": 2000},
        ],
    },
    {
        "email": "ahyeon10@test.com", "password": "Test1234!", "nickname": "아현 순대 사장",
        "truck": {
            "name": "아현 전통 순대국",
            "description": "진한 국물의 순대국과 매콤한 순대볶음. 아현 포장마차 감성!",
            "latitude": 37.5555, "longitude": 126.9540,
            "keywords": "순대,분식,국물,포장마차",
            "account_info": "현금 010-1010-0010",
        },
        "menus": [
            {"name": "순대국밥", "price": 7000},
            {"name": "순대볶음 (소)", "price": 6000},
            {"name": "순대볶음 (대)", "price": 9000},
            {"name": "순대 (단품)", "price": 4000},
        ],
    },
]


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
                    {
                        "email": o["email"],
                        "password": hash_password(o["password"]),
                        "nickname": o["nickname"],
                    },
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
                    "keywords": t["keywords"],
                },
            )
            truck_id = res.fetchone()[0]
            print(f"  트럭 생성: {t['name']} (id={truck_id})")

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
    print("\n--- 계정 정보 (아현역 테스트) ---")
    for o in OWNERS:
        print(f"  {o['email']}  /  {o['password']}")
    print("----------------------------------")


if __name__ == "__main__":
    asyncio.run(main())
