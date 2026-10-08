from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import hash_password, verify_password, create_access_token
from app.models.user import User


class AuthService:

    @staticmethod
    async def register(
        db: AsyncSession,
        username: str,
        email: str,
        password: str
    ):
        result = await db.execute(
            select(User).where(User.email == email)
        )

        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise ValueError("User already exists")

        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password)
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        return user

    @staticmethod
    async def login(
        db: AsyncSession,
        email: str,
        password: str
    ):
        result = await db.execute(
            select(User).where(User.email == email)
        )

        user = result.scalar_one_or_none()

        if not user:
            raise ValueError("Invalid credentials")

        if not verify_password(password, user.password_hash):
            raise ValueError("Invalid credentials")

        access_token = create_access_token(
            data={"sub": str(user.id)}
        )

        return access_token