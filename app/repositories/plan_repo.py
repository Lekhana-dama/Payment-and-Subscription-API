from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.plans  import Plan

class PlanRepo:
    @staticmethod
    async def create_plan(db:AsyncSession,plan:Plan):
        db.add(plan)
        await db.commit()
        await db.refresh(plan)

        return plan

    @staticmethod
    async def get_active_plans(db:AsyncSession)->list[Plan]:
        result = await db.execute(select(Plan).where(Plan.is_active==True))
        return result.scalars().all()

    @staticmethod
    async def get_by_id(db:AsyncSession,id:int)->Plan|None:
        result=await db.execute(
            select(Plan).where(Plan.id==id)
        )
        return result.scalar_one_or_none()