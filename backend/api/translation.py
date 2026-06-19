from fastapi import APIRouter

from services.translation_service import get_translation_status


router = APIRouter()


@router.get("/status")
def translation_status():
    return get_translation_status()
