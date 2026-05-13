"""테스트 사장 계정 5개 생성"""
import asyncio
import bcrypt
from sqlalchemy import text
from app.database import AsyncSessionLocal

OWNERS = [
    {"email": "owner1@test.com", "password": "Test1234!", "nickname": "사장님1"},
    {"email": "owner2@test.com", "password": "Test1234!", "nickname": "사장님2"},
    {"email": "owner3@test.com", "password": "Test1234!", "nickname": "사장님3"},
    {"email": "owner4@test.com", "password": "Test1234!", "nickname": "사장님4"},
    {"email": "owner5@test.com", "password": "Test1234!", "nickname": "사장님5"},
]


def hash_pw(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt(rounds=12)).decode()


async def main():
    async with AsyncSessionLocal() as session:
        for o in OWNERS:
            hashed = hash_pw(o["password"])
            result = await session.execute(
                text("SELECT id FROM users WHERE email = :email"),
                {"email": o["email"]},
            )
            if result.fetchone():
                print(f"이미 존재: {o['email']}")
                continue
            await session.execute(
                text(
                    "INSERT INTO users (email, password, nickname, role) "
                    "VALUES (:email, :password, :nickname, 'owner')"
                ),
                {"email": o["email"], "password": hashed, "nickname": o["nickname"]},
            )
            print(f"생성 완료: {o['email']}  (비밀번호: {o['password']})")
        await session.commit()
    print("done.")


asyncio.run(main())
