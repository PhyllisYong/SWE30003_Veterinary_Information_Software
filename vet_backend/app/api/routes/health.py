from fastapi import APIRouter
from app.core.database import checkDbConnection

router = APIRouter()


@router.get("/health")
def healthCheck():
    dbOk = checkDbConnection()
    return {
        "status": "ok" if dbOk else "degraded",
        "database": "connected" if dbOk else "unreachable",
    }
