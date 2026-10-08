from app.database import get_db
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.plans import Plan
from app.repositories.plan_repo import PlanRepo
from app.schemes.plan_model import PlanCreate

class PlanService:

    @staticmethod
    async def create_plan(db:AsyncSession,plan_data:PlanCreate):
        plan=Plan(name=plan_data.name,description=plan_data.description,price=plan_data.price,
                  billing_interval=plan_data.billing_interval,is_active=plan_data.is_active)
        return await PlanRepo.create_plan(db,plan)

    @staticmethod
    async def get_active_plans(db:AsyncSession)->list[Plan]:
        return await PlanRepo.get_active_plans(db)

    @staticmethod
    async def get_plan_by_id(db:AsyncSession,id:int)->Plan|None:
        return await PlanRepo.get_by_id(db,id)
