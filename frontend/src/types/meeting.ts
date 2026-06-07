export type MeetingStatus = "created" | "started" | "paused" | "ended";

export type Meeting = {
  id: string;
  name: string;
  source_language: string;
  target_language: string;
  status: MeetingStatus;
  created_at: string;
  started_at?: string | null;
  ended_at?: string | null;
  audio_file?: string | null;
  audio_duration?: number | null;
  transcript_file?: string | null;
  transcript_text?: string | null;
  transcript_status: "pending" | "processing" | "completed" | "failed";
};

export type CreateMeetingPayload = {
  name: string;
  source_language: string;
  target_language: string;
};

export type AudioUploadResult = {
  success: boolean;
  file_name: string;
  duration: number;
};

export type TranscriptionResult = {
  success: boolean;
  status: "pending" | "processing" | "completed" | "failed";
  transcript: string;
  transcript_file?: string | null;
};

export type WhisperModelStatus = {
  installed: boolean;
  model: string;
  path: string;
  model_path?: string;
  message: string;
};
