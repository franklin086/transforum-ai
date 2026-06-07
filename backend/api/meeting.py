from fastapi import APIRouter, HTTPException

from models.meeting import MeetingCreateRequest
from services.export_service import create_docx_export_placeholder
from services.meeting_repository import (
    create_meeting as create_meeting_record,
    get_meeting as get_meeting_record,
    list_recent_meetings,
)

router = APIRouter()


@router.post("/create")
def create_meeting(request: MeetingCreateRequest):
    meeting = create_meeting_record(request)
    return {
        "success": True,
        "meeting": meeting.model_dump(),
    }


@router.get("/list")
def list_meetings():
    return {
        "success": True,
        "meetings": [meeting.model_dump() for meeting in list_recent_meetings()],
    }


@router.post("/start")
def start_meeting():
    return {
        "success": True,
        "status": "started",
    }


@router.post("/end")
def end_meeting():
    return {
        "success": True,
        "status": "ended",
    }


@router.post("/export")
def export_meeting():
    return create_docx_export_placeholder()


@router.get("/{meeting_id}")
def get_meeting(meeting_id: str):
    meeting = get_meeting_record(meeting_id)
    if meeting is None:
        raise HTTPException(status_code=404, detail="Meeting not found")

    return {
        "success": True,
        "meeting": meeting.model_dump(),
    }
