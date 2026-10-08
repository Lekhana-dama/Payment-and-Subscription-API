from app.models.plans import Plan
from app.repositories.plan_repo import PlanRepo
from app.schemes.plan_model import PlanCreate,PlanResponse
from app.database import get_db
from app.services.plan_service import PlanService
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter,Depends,status

router=APIRouter(prefix="/plans",tags=["Plans"])

@router.post("/",response_model=PlanResponse)
async def create_plan(paln:PlanCreate,db:AsyncSession=Depends(get_db)):
    return await PlanService.create_plan(db,plan_data=paln)

@router.get("",response_model=list[PlanResponse])
async def get_active_plans(db:AsyncSession=Depends(get_db)):
    return await PlanService.get_active_plans(db)

@router.get("/{id}",response_model=PlanResponse)
async def get_plan_by_id(id:int,db:AsyncSession=Depends(get_db)):
    return await PlanService.get_plan_by_id(db,id)


