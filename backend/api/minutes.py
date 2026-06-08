from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from services.minutes_service import generate_minutes

router = APIRouter()


class MinutesGenerateRequest(BaseModel):
    meeting_id: str


@router.post("/generate")
def generate_meeting_minutes(request: MinutesGenerateRequest):
    result = generate_minutes(request.meeting_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return result
