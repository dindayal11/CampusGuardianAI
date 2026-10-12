from fastapi import APIRouter
router = APIRouter(prefix="/public", tags=["Public"])

@router.get("/platform")
def platform_info():
    return {
        "name":"Campus Guardian AI",
        "description":"Campus safety, complaint management and institute communication platform.",
        "roles":["Student","Institute Admin","Platform Admin"]
    }
