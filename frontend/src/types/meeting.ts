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
  realtime_transcript_text?: string | null;
  english_transcript_text?: string | null;
  minutes_summary?: string | null;
  minutes_key_points?: string | null;
  minutes_action_items?: string | null;
  minutes_next_steps?: string | null;
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

export type RealtimeTranscriptionResult =
  | {
      success: true;
      text: string;
      english_text?: string;
      chunk_index: number;
      chunk_file?: string;
      transcript_file?: string;
    }
  | {
      success: false;
      error: string;
      message: string;
      chunk_index?: number;
    };

export type RealtimeTranscriptResult = {
  success: boolean;
  meeting_id: string;
  transcript: string;
  latest_text: string;
  updated_at?: string;
  message?: string;
};

export type RealtimeBilingualResult = {
  success: boolean;
  meeting_id: string;
  chinese: string;
  english: string;
  updated_at: string;
};

export type MinutesResult = {
  success: boolean;
  meeting_id: string;
  summary: string;
  key_points: string[];
  action_items: string[];
  next_steps: string[];
};
