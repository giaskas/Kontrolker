# src/app/routers/test_config.py
from fastapi import APIRouter


router = APIRouter(prefix="/services")

@router.get("")
def health():
    return {"status": "ok"}