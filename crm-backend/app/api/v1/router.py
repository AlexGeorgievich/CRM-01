from fastapi import APIRouter

from app.api.v1 import auth, dictionaries, leads, reports, users

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
router.include_router(leads.router, prefix="/leads", tags=["Leads"])
router.include_router(reports.router, prefix="/reports", tags=["Reports"])
router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(
    dictionaries.router,
    prefix="/dictionaries",
    tags=["Dictionaries"],
)

@router.get("/ping")
async def ping():
    return {"message": "pong"}
