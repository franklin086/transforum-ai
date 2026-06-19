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
  translation_provider?: string | null;
  translation_status?: string | null;
  translation_fallback_reason?: string | null;
  translation_latency_ms?: number | null;
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
  current_model?: string;
  path: string;
  model_path?: string;
  active_model_path?: string;
  available_models?: Record<string, { installed: boolean; path: string }>;
  recommended_for_field_test?: string;
  message: string;
};

export type RealtimeTranscriptionResult =
  | {
      success: true;
      text: string;
      caption_text?: string;
      accepted_caption?: boolean;
      translation_attempted?: boolean;
      saved_to_minutes?: boolean;
      english_text?: string;
      translation_text?: string;
      translation_provider?: string;
      translation_status?: string;
      translation_latency_ms?: number;
      latency_ms?: number;
      translation_fallback_reason?: string | null;
      fallback_reason?: string | null;
      gemini_configured?: boolean;
      audio_mode?: string;
      chunk_duration_ms?: number;
      audio_size_bytes?: number;
      asr_latency_ms?: number;
      end_to_end_latency_ms?: number;
      translation?: {
        success: boolean;
        provider: string;
        translation_status?: string;
        source_text?: string;
        translated_text?: string;
        error?: string | null;
        fallback_reason?: string | null;
        latency_ms?: number;
      };
      chunk_index: number;
      chunk_file?: string;
      transcript_file?: string;
    }
  | {
      success: false;
      error: string;
      message: string;
      chunk_index?: number;
      caption_text?: string;
      accepted_caption?: boolean;
      translation_attempted?: boolean;
      translation_provider?: string;
      translation_status?: string;
      translation_fallback_reason?: string | null;
      fallback_reason?: string | null;
      saved_to_minutes?: boolean;
      audio_mode?: string;
      chunk_duration_ms?: number;
      audio_size_bytes?: number;
      asr_latency_ms?: number;
      translation_latency_ms?: number;
      end_to_end_latency_ms?: number;
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
  provider?: string;
  translation_provider?: string;
  translation_status?: string;
  translation_text?: string;
  fallback_reason?: string | null;
  latency_ms?: number;
  audio_mode?: string;
  chunk_duration_ms?: number;
  asr_latency_ms?: number;
  end_to_end_latency_ms?: number;
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


export type TranslationStatus = {
  gemini_api_key_configured: boolean;
  provider: "gemini" | "mock" | string;
  model?: string | null;
};
