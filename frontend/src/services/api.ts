import type {
  AudioUploadResult,
  CreateMeetingPayload,
  Meeting,
  MinutesResult,
  RealtimeBilingualResult,
  RealtimeTranscriptionResult,
  RealtimeTranscriptResult,
  TranscriptionResult,
  TranslationStatus,
  WhisperModelStatus
} from "@/types/meeting";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const isFormData = init?.body instanceof FormData;
  const response = await fetch(`${API_BASE_URL}${path}`, {
    cache: "no-store",
    ...init,
    headers: isFormData
      ? init?.headers
      : {
          "Content-Type": "application/json",
          ...(init?.headers ?? {})
        }
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed with ${response.status}`);
  }

  return response.json();
}

export async function getHealth() {
  return requestJson<{
    status: string;
    project: string;
    version: string;
  }>("/api/health");
}

export async function createMeeting(payload: CreateMeetingPayload) {
  return requestJson<{
    success: boolean;
    meeting: Meeting;
  }>("/api/meeting/create", {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export async function getMeeting(meetingId: string) {
  return requestJson<{
    success: boolean;
    meeting: Meeting;
  }>(`/api/meeting/${meetingId}`);
}

export async function listMeetings() {
  return requestJson<{
    success: boolean;
    meetings: Meeting[];
  }>("/api/meeting/list");
}

export async function uploadMeetingAudio(
  meetingId: string,
  audioBlob: Blob,
  duration: number
) {
  const extension = audioBlob.type.includes("wav") ? "wav" : "webm";
  const formData = new FormData();
  formData.append("meeting_id", meetingId);
  formData.append("duration", String(Math.round(duration)));
  formData.append("audio", audioBlob, `${meetingId}.${extension}`);

  return requestJson<AudioUploadResult>("/api/audio/upload", {
    method: "POST",
    body: formData
  });
}

export async function startTranscription(meetingId: string) {
  return requestJson<
    | {
        success: true;
        status: "processing" | "completed";
        transcript?: string;
        transcript_file?: string | null;
      }
    | {
        success: false;
        error: string;
        message: string;
        status: "failed";
        model?: string;
        path?: string;
      }
  >("/api/transcription/start", {
    method: "POST",
    body: JSON.stringify({ meeting_id: meetingId })
  });
}

export async function getTranscription(meetingId: string) {
  return requestJson<TranscriptionResult>(`/api/transcription/${meetingId}`);
}

export async function getWhisperModelStatus() {
  return requestJson<WhisperModelStatus>("/api/transcription/model-status");
}

export async function getTranslationStatus() {
  return requestJson<TranslationStatus>("/api/translation/status");
}

export async function transcribeRealtimeChunk(
  meetingId: string,
  chunkIndex: number,
  audioBlob: Blob
) {
  const formData = new FormData();
  formData.append("meeting_id", meetingId);
  formData.append("chunk_index", String(chunkIndex));
  formData.append("audio", audioBlob, `${meetingId}_chunk_${chunkIndex}.webm`);

  return requestJson<RealtimeTranscriptionResult>(
    "/api/realtime/transcribe-chunk",
    {
      method: "POST",
      body: formData
    }
  );
}

export async function getRealtimeTranscript(meetingId: string) {
  return requestJson<RealtimeTranscriptResult>(
    `/api/realtime/transcript/${meetingId}`
  );
}

export async function getRealtimeBilingualTranscript(meetingId: string) {
  return requestJson<RealtimeBilingualResult>(
    `/api/realtime/bilingual/${meetingId}`
  );
}

export async function endMeeting(meetingId: string) {
  return requestJson<{
    success: boolean;
    status: "ended";
    meeting: Meeting;
  }>("/api/meeting/end", {
    method: "POST",
    body: JSON.stringify({ meeting_id: meetingId })
  });
}

export async function generateMinutes(meetingId: string) {
  return requestJson<MinutesResult>("/api/minutes/generate", {
    method: "POST",
    body: JSON.stringify({ meeting_id: meetingId })
  });
}
