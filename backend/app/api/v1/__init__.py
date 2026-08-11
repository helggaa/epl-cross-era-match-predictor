from fastapi import APIRouter
from app.api.v1.teams import router as teams_router
from app.api.v1.predict import router as predict_router
from app.api.v1.explanation import router as explanation_router

api_v1_router = APIRouter()
api_v1_router.include_router(teams_router, tags=["Teams"])
api_v1_router.include_router(predict_router, tags=["Prediction"])
api_v1_router.include_router(explanation_router, tags=["Explanation"])
