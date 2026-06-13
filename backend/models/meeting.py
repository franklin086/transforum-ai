from typing import Optional

from pydantic import BaseModel, Field, field_validator


class Meeting(BaseModel):
    id: str
    name: str
    source_language: str
    target_language: str
    status: str = "created"
    created_at: str
    started_at: Optional[str] = None
    ended_at: Optional[str] = None
    audio_file: Optional[str] = None
    audio_duration: Optional[int] = None
    transcript_file: Optional[str] = None
    transcript_text: Optional[str] = None
    realtime_transcript_text: Optional[str] = None
    english_transcript_text: Optional[str] = None
    translation_provider: str = "mock"
    translation_latency_ms: int = 0
    minutes_summary: Optional[str] = None
    minutes_key_points: Optional[str] = None
    minutes_action_items: Optional[str] = None
    minutes_next_steps: Optional[str] = None
    transcript_status: str = "pending"


class MeetingCreateRequest(BaseModel):
    name: str = Field(min_length=1)
    source_language: str = "zh"
    target_language: str = "en"

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Meeting name is required")
        return stripped
