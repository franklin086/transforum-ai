export type RealtimeSocketStatus =
  | "Connected"
  | "Disconnected"
  | "Fallback Polling"
  | "Error";

export type SubtitleUpdateMessage = {
  type: "subtitle_update";
  meeting_id: string;
  chinese: string;
  english: string;
  provider: "gemini" | "mock" | string;
  translation_latency_ms: number;
  translation_text?: string;
  translation_fallback_reason?: string | null;
  fallback_reason?: string | null;
  translation_status?: string;
  gemini_configured?: boolean;
  audio_mode?: string;
  chunk_duration_ms?: number;
  asr_latency_ms?: number;
  end_to_end_latency_ms?: number;
  timestamp: string;
};

export type ChunkStatusMessage = {
  type: "chunk_status";
  meeting_id: string;
  chunk_index: number;
  error: "INVALID_AUDIO_CHUNK" | "CHUNK_TOO_SMALL" | "WAITING_FOR_VALID_SPEECH" | string;
  message: string;
  timestamp: string;
};

type RealtimeMessage = SubtitleUpdateMessage | ChunkStatusMessage;

const WS_BASE_URL =
  process.env.NEXT_PUBLIC_WS_BASE_URL ?? "ws://localhost:8000";

export function connectRealtimeSocket(
  meetingId: string,
  onMessage: (message: RealtimeMessage) => void,
  onStatus: (status: RealtimeSocketStatus) => void
) {
  let socket: WebSocket | null = null;
  let reconnectAttempted = false;
  let closedByClient = false;
  let reconnectTimer: number | null = null;

  function openSocket() {
    socket = new WebSocket(
      `${WS_BASE_URL}/ws/realtime/${encodeURIComponent(meetingId)}`
    );

    socket.onopen = () => {
      onStatus("Connected");
    };

    socket.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data) as RealtimeMessage;
        if (message.type === "subtitle_update" || message.type === "chunk_status") {
          onMessage(message);
        }
      } catch {
        onStatus("Error");
      }
    };

    socket.onerror = () => {
      onStatus("Error");
    };

    socket.onclose = () => {
      if (closedByClient) {
        onStatus("Disconnected");
        return;
      }

      if (!reconnectAttempted) {
        reconnectAttempted = true;
        onStatus("Disconnected");
        reconnectTimer = window.setTimeout(openSocket, 1000);
        return;
      }

      onStatus("Fallback Polling");
    };
  }

  openSocket();

  return () => {
    closedByClient = true;
    if (reconnectTimer !== null) {
      window.clearTimeout(reconnectTimer);
    }
    socket?.close();
  };
}
