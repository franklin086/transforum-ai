"use client";

import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import {
  endMeeting,
  generateMinutes,
  getMeeting,
  getRealtimeBilingualTranscript,
  getTranscription,
  getWhisperModelStatus,
  startTranscription,
  transcribeRealtimeChunk,
  uploadMeetingAudio
} from "@/services/api";
import { connectRealtimeSocket } from "@/services/realtimeSocket";
import type { Meeting } from "@/types/meeting";

const languageLabels: Record<string, string> = {
  zh: "Chinese zh",
  en: "English en"
};

function formatLanguage(code: string) {
  return languageLabels[code] ?? code;
}

function latestLineWithoutTimestamp(text?: string | null) {
  const lines = (text ?? "")
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);
  const latestLine = lines.at(-1) ?? "";
  return latestLine.replace(/^\[\d{2}:\d{2}:\d{2}\]\s*/, "");
}

function formatTranslationProvider(provider?: string | null, english?: string | null) {
  if (!english?.trim()) {
    return "Waiting";
  }
  if (provider === "gemini") {
    return "Gemini";
  }
  if (provider === "mock") {
    return "Mock Fallback";
  }
  return "Waiting";
}

const SKIPPED_CHUNK_ERRORS = new Set(["INVALID_AUDIO_CHUNK", "CHUNK_TOO_SMALL", "WAITING_FOR_VALID_SPEECH"]);
const REALTIME_CHUNK_MS = 8000;

export function MeetingConsole() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const meetingId = searchParams.get("meeting_id");
  const [meeting, setMeeting] = useState<Meeting | null>(null);
  const [isLoading, setIsLoading] = useState(Boolean(meetingId));
  const [error, setError] = useState<string | null>(null);
  const [microphoneStatus, setMicrophoneStatus] = useState(
    "Microphone Disconnected"
  );
  const [audioUploadStatus, setAudioUploadStatus] = useState("Not Uploaded");
  const [recordingDuration, setRecordingDuration] = useState(0);
  const [uploadedFileName, setUploadedFileName] = useState<string | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [transcriptStatus, setTranscriptStatus] = useState("pending");
  const [transcriptPreview, setTranscriptPreview] = useState("");
  const [transcriptFile, setTranscriptFile] = useState<string | null>(null);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [whisperStatus, setWhisperStatus] = useState("Checking...");
  const [isWhisperReady, setIsWhisperReady] = useState(false);
  const [realtimeStatus, setRealtimeStatus] = useState("Stopped");
  const [currentRealtimeChunk, setCurrentRealtimeChunk] = useState(0);
  const [latestRealtimeText, setLatestRealtimeText] = useState("");
  const [currentTranslation, setCurrentTranslation] = useState("");
  const [translationProvider, setTranslationProvider] = useState("Waiting");
  const [translationLatencyMs, setTranslationLatencyMs] = useState(0);
  const [translationFallbackReason, setTranslationFallbackReason] = useState<string | null>(null);
  const [webSocketStatus, setWebSocketStatus] = useState("Disconnected");
  const [realtimeTranscript, setRealtimeTranscript] = useState("");
  const [isRealtimeCaptioning, setIsRealtimeCaptioning] = useState(false);
  const [isEndingMeeting, setIsEndingMeeting] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const realtimeRecorderRef = useRef<MediaRecorder | null>(null);
  const realtimeStreamRef = useRef<MediaStream | null>(null);
  const realtimeChunkIndexRef = useRef(0);
  const invalidChunkCountRef = useRef(0);
  const realtimeActiveRef = useRef(false);
  const chunksRef = useRef<BlobPart[]>([]);
  const timerRef = useRef<number | null>(null);
  const startedAtRef = useRef<number | null>(null);

  useEffect(() => {
    if (!meetingId) {
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    getMeeting(meetingId)
      .then((result) => {
        setMeeting(result.meeting);
        setTranscriptStatus(result.meeting.transcript_status);
        setTranscriptPreview(result.meeting.transcript_text?.slice(0, 500) ?? "");
        setTranscriptFile(result.meeting.transcript_file ?? null);
        setRealtimeTranscript(result.meeting.realtime_transcript_text ?? "");
        const latestEnglish = latestLineWithoutTimestamp(
          result.meeting.english_transcript_text
        );
        setCurrentTranslation(latestEnglish);
        setTranslationProvider(
          formatTranslationProvider(result.meeting.translation_provider, latestEnglish)
        );
        setTranslationLatencyMs(result.meeting.translation_latency_ms ?? 0);
        setTranslationFallbackReason(null);
        setError(null);
      })
      .catch(() => {
        setError("Meeting not found or backend is unavailable.");
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [meetingId]);

  useEffect(() => {
    getWhisperModelStatus()
      .then((result) => {
        setIsWhisperReady(result.installed);
        setWhisperStatus(result.installed ? "Ready" : "Model Not Installed");
      })
      .catch(() => {
        setIsWhisperReady(false);
        setWhisperStatus("Model Status Unavailable");
      });
  }, []);

  useEffect(() => {
    return () => {
      if (timerRef.current) {
        window.clearInterval(timerRef.current);
      }
      mediaStreamRef.current?.getTracks().forEach((track) => track.stop());
      realtimeActiveRef.current = false;
      if (realtimeRecorderRef.current?.state === "recording") {
        realtimeRecorderRef.current.stop();
      }
      realtimeStreamRef.current?.getTracks().forEach((track) => track.stop());
    };
  }, []);

  useEffect(() => {
    if (!meetingId) {
      return;
    }

    return connectRealtimeSocket(
      meetingId,
      (message) => {
        if (message.type === "chunk_status") {
          if (SKIPPED_CHUNK_ERRORS.has(message.error)) {
            invalidChunkCountRef.current += 1;
            setCurrentRealtimeChunk(message.chunk_index);
            setRealtimeStatus("Waiting for valid speech input...");
            setTranslationProvider((current) =>
              current === "Mock Fallback" ? "Waiting" : current
            );
            setTranslationFallbackReason(null);
          }
          return;
        }

        setLatestRealtimeText(message.chinese);
        setCurrentTranslation(message.english);
        setTranslationProvider(
          formatTranslationProvider(message.provider, message.english)
        );
        setTranslationLatencyMs(message.translation_latency_ms ?? 0);
        setTranslationFallbackReason(message.translation_fallback_reason ?? null);
        invalidChunkCountRef.current = 0;
        setRealtimeStatus("Captioning");
      },
      setWebSocketStatus
    );
  }, [meetingId]);

  useEffect(() => {
    if (!meetingId || webSocketStatus !== "Fallback Polling") {
      return;
    }

    let isActive = true;
    const activeMeetingId = meetingId;

    async function refreshBilingualTranscript() {
      try {
        const result = await getRealtimeBilingualTranscript(activeMeetingId);
        if (!isActive) {
          return;
        }
        setLatestRealtimeText(result.chinese);
        setCurrentTranslation(result.english);
        setTranslationProvider(
          formatTranslationProvider(result.provider, result.english)
        );
        setTranslationLatencyMs(result.latency_ms ?? 0);
        setTranslationFallbackReason(null);
      } catch {
        setWebSocketStatus("Error");
      }
    }

    void refreshBilingualTranscript();
    const intervalId = window.setInterval(refreshBilingualTranscript, 2000);

    return () => {
      isActive = false;
      window.clearInterval(intervalId);
    };
  }, [meetingId, webSocketStatus]);

  function formatDuration(seconds: number) {
    const minutes = Math.floor(seconds / 60)
      .toString()
      .padStart(2, "0");
    const remainingSeconds = Math.floor(seconds % 60)
      .toString()
      .padStart(2, "0");
    return `${minutes}:${remainingSeconds}`;
  }

  function getSupportedMimeType() {
    if (
      typeof MediaRecorder !== "undefined" &&
      MediaRecorder.isTypeSupported("audio/webm")
    ) {
      return "audio/webm";
    }
    return "";
  }

  function formatRealtimeTimestamp(chunkIndex: number) {
    const totalSeconds = Math.max(chunkIndex, 1) * (REALTIME_CHUNK_MS / 1000);
    const hours = Math.floor(totalSeconds / 3600)
      .toString()
      .padStart(2, "0");
    const minutes = Math.floor((totalSeconds % 3600) / 60)
      .toString()
      .padStart(2, "0");
    const seconds = Math.floor(totalSeconds % 60)
      .toString()
      .padStart(2, "0");
    return `[${hours}:${minutes}:${seconds}]`;
  }

  function getCurrentStep() {
    if (isEndingMeeting) {
      return "Generating minutes";
    }
    if (meeting?.minutes_summary) {
      return "Minutes generated";
    }
    if (meeting?.status === "ended") {
      return "Meeting ended";
    }
    if (latestRealtimeText || currentTranslation) {
      return "Captioning";
    }
    if (isRealtimeCaptioning) {
      return "Listening";
    }
    return "Ready to start";
  }

  async function uploadRealtimeAudioChunk(audioBlob: Blob, chunkIndex: number) {
    if (!meetingId || audioBlob.size === 0) {
      return;
    }

    setRealtimeStatus("Recording and Processing...");
    setCurrentRealtimeChunk(chunkIndex);

    try {
      const result = await transcribeRealtimeChunk(
        meetingId,
        chunkIndex,
        audioBlob
      );
      if (!result.success) {
        if (SKIPPED_CHUNK_ERRORS.has(result.error)) {
          invalidChunkCountRef.current += 1;
          setRealtimeStatus("Waiting for valid speech input...");
          if (!currentTranslation) {
            setTranslationProvider("Waiting");
          }
          setTranslationFallbackReason(null);
          return;
        }

        setRealtimeStatus("Transcription Failed");
        setError(result.message);
        return;
      }

      const text = result.text.trim();
      if (text) {
        const line = `${formatRealtimeTimestamp(result.chunk_index)} ${text}`;
        const englishText =
          result.translation_text?.trim() || result.english_text?.trim() || "";
        setLatestRealtimeText(text);
        setCurrentTranslation(englishText);
        setTranslationProvider(
          formatTranslationProvider(result.translation_provider, englishText)
        );
        setTranslationLatencyMs(result.translation_latency_ms ?? 0);
        setTranslationFallbackReason(
          result.translation_fallback_reason ?? result.translation?.fallback_reason ?? null
        );
        invalidChunkCountRef.current = 0;
        setRealtimeTranscript((current) =>
          current ? `${current}\n${line}` : line
        );
      } else {
        setRealtimeStatus("Waiting for valid speech input...");
        if (!currentTranslation) {
          setTranslationProvider("Waiting");
        }
        setTranslationFallbackReason(null);
        return;
      }
      setRealtimeStatus(realtimeActiveRef.current ? "Listening..." : "Stopped");
    } catch {
      setRealtimeStatus("Upload Failed");
      setError("Realtime chunk upload failed. Confirm the backend is running.");
    }
  }

  async function handleStartRealtimeCaption() {
    if (!meetingId) {
      setError("Please create a meeting before starting realtime captions.");
      return;
    }

    setError(null);
    setRealtimeStatus("Requesting Microphone...");

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: true,
        video: false
      });
      const mimeType = getSupportedMimeType();
      const recorder = new MediaRecorder(
        stream,
        mimeType ? { mimeType } : undefined
      );

      realtimeChunkIndexRef.current = 0;
      invalidChunkCountRef.current = 0;
      realtimeActiveRef.current = true;
      realtimeStreamRef.current = stream;
      realtimeRecorderRef.current = recorder;

      recorder.ondataavailable = (event) => {
        if (!realtimeActiveRef.current || event.data.size === 0) {
          return;
        }
        realtimeChunkIndexRef.current += 1;
        void uploadRealtimeAudioChunk(
          new Blob([event.data], { type: recorder.mimeType || "audio/webm" }),
          realtimeChunkIndexRef.current
        );
      };

      recorder.onstop = () => {
        realtimeActiveRef.current = false;
        setIsRealtimeCaptioning(false);
        setRealtimeStatus("Stopped");
        stream.getTracks().forEach((track) => track.stop());
        realtimeRecorderRef.current = null;
        realtimeStreamRef.current = null;
      };

      recorder.start(REALTIME_CHUNK_MS);
      setIsRealtimeCaptioning(true);
      setRealtimeStatus("Listening...");
      setCurrentRealtimeChunk(0);
      setLatestRealtimeText("");
      setCurrentTranslation("");
      setTranslationProvider("Waiting");
      setTranslationFallbackReason(null);
    } catch {
      setRealtimeStatus("Microphone Permission Denied");
      setError("Could not access microphone for realtime captions.");
    }
  }

  function handleStopRealtimeCaption() {
    realtimeActiveRef.current = false;
    if (realtimeRecorderRef.current?.state === "recording") {
      realtimeRecorderRef.current.stop();
    }
    realtimeStreamRef.current?.getTracks().forEach((track) => track.stop());
    setIsRealtimeCaptioning(false);
    setRealtimeStatus("Stopped");
  }

  async function handleStartMeeting() {
    if (!meetingId) {
      setError("Please create a meeting before recording audio.");
      return;
    }

    setError(null);
    setAudioUploadStatus("Not Uploaded");
    setUploadedFileName(null);
    setRecordingDuration(0);

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: true,
        video: false
      });
      const mimeType = getSupportedMimeType();
      const recorder = new MediaRecorder(
        stream,
        mimeType ? { mimeType } : undefined
      );

      chunksRef.current = [];
      mediaStreamRef.current = stream;
      mediaRecorderRef.current = recorder;
      startedAtRef.current = Date.now();

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      recorder.onstop = async () => {
        if (timerRef.current) {
          window.clearInterval(timerRef.current);
          timerRef.current = null;
        }

        const duration = startedAtRef.current
          ? Math.max(1, Math.round((Date.now() - startedAtRef.current) / 1000))
          : recordingDuration;
        const audioBlob = new Blob(chunksRef.current, {
          type: recorder.mimeType || "audio/webm"
        });

        setRecordingDuration(duration);
        setMicrophoneStatus("Microphone Disconnected");
        setAudioUploadStatus("Uploading Audio...");
        stream.getTracks().forEach((track) => track.stop());

        try {
          const result = await uploadMeetingAudio(meetingId, audioBlob, duration);
          setAudioUploadStatus("Audio Uploaded Successfully");
          setUploadedFileName(result.file_name);
          const refreshed = await getMeeting(meetingId);
          setMeeting(refreshed.meeting);
        } catch {
          setAudioUploadStatus("Audio Upload Failed");
          setError("Audio upload failed. Confirm the backend is running.");
        } finally {
          chunksRef.current = [];
          mediaRecorderRef.current = null;
          mediaStreamRef.current = null;
          startedAtRef.current = null;
        }
      };

      recorder.start();
      setIsRecording(true);
      setMicrophoneStatus("Microphone Connected");
      timerRef.current = window.setInterval(() => {
        if (startedAtRef.current) {
          setRecordingDuration(
            Math.floor((Date.now() - startedAtRef.current) / 1000)
          );
        }
      }, 1000);
    } catch {
      setMicrophoneStatus("Microphone Permission Denied");
      setError("Could not access microphone. Check browser permission.");
    }
  }

  function handleStopMeeting() {
    if (mediaRecorderRef.current?.state === "recording") {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  }

  async function pollTranscriptionStatus(currentMeetingId: string) {
    for (let attempt = 0; attempt < 60; attempt += 1) {
      const result = await getTranscription(currentMeetingId);
      setTranscriptStatus(result.status);
      setTranscriptPreview(result.transcript.slice(0, 500));
      setTranscriptFile(result.transcript_file ?? null);

      if (result.status === "completed" || result.status === "failed") {
        setIsTranscribing(false);
        const refreshed = await getMeeting(currentMeetingId);
        setMeeting(refreshed.meeting);
        return;
      }

      await new Promise((resolve) => window.setTimeout(resolve, 2000));
    }

    setIsTranscribing(false);
  }

  async function handleGenerateTranscript() {
    if (!meetingId) {
      setError("Please create a meeting before generating a transcript.");
      return;
    }

    setError(null);
    setIsTranscribing(true);
    setTranscriptStatus("processing");

    try {
      const startResult = await startTranscription(meetingId);
      if (!startResult.success) {
        setTranscriptStatus("failed");
        setIsTranscribing(false);
        setError(startResult.message);
        return;
      }
      if (startResult.status === "completed") {
        setTranscriptStatus("completed");
        setTranscriptPreview(startResult.transcript?.slice(0, 500) ?? "");
        setTranscriptFile(startResult.transcript_file ?? null);
        setIsTranscribing(false);
        const refreshed = await getMeeting(meetingId);
        setMeeting(refreshed.meeting);
        return;
      }
      await pollTranscriptionStatus(meetingId);
    } catch {
      setTranscriptStatus("failed");
      setIsTranscribing(false);
      setError("Transcription failed. Confirm the backend and Whisper model are ready.");
    }
  }

  async function handleEndMeeting() {
    if (!meetingId) {
      setError("Please create a meeting before ending it.");
      return;
    }

    setError(null);
    setIsEndingMeeting(true);
    handleStopRealtimeCaption();

    try {
      await endMeeting(meetingId);
      await generateMinutes(meetingId);
      router.push(`/meeting/minutes?meeting_id=${encodeURIComponent(meetingId)}`);
    } catch {
      setIsEndingMeeting(false);
      setError("End Meeting failed. Confirm the backend is running.");
    }
  }

  if (!meetingId) {
    return (
      <section className="mt-8 rounded-lg border border-slate-200 bg-white p-8">
        <h2 className="text-2xl font-bold">No meeting selected.</h2>
        <p className="mt-3 text-slate-600">
          Please create a meeting first.
        </p>
        <Link
          className="mt-6 inline-flex rounded-lg bg-meeting-blue px-5 py-3 text-sm font-semibold text-white"
          href="/meeting/new"
        >
          Create Meeting
        </Link>
      </section>
    );
  }

  if (isLoading) {
    return (
      <section className="mt-8 rounded-lg border border-slate-200 bg-white p-8">
        <p className="text-slate-600">Loading meeting...</p>
      </section>
    );
  }

  if (!meeting) {
    return (
      <section className="mt-8 rounded-lg border border-slate-200 bg-white p-8">
        <h2 className="text-2xl font-bold">Meeting unavailable</h2>
        <p className="mt-3 text-red-700">{error ?? "Meeting not found."}</p>
        <Link
          className="mt-6 inline-flex rounded-lg bg-meeting-blue px-5 py-3 text-sm font-semibold text-white"
          href="/meeting/new"
        >
          Create Meeting
        </Link>
      </section>
    );
  }

  return (
    <>
      <div className="mt-8 grid gap-4 md:grid-cols-2">
        <section className="rounded-lg border border-slate-200 bg-white p-5">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            Meeting Name
          </h2>
          <p className="mt-3 text-2xl font-bold">{meeting.name}</p>
        </section>
        <section className="rounded-lg border border-slate-200 bg-white p-5">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            Meeting Status
          </h2>
          <p className="mt-3 text-2xl font-bold text-green-700">
            {meeting.status}
          </p>
        </section>
        <section className="rounded-lg border border-slate-200 bg-white p-5">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            Microphone Status
          </h2>
          <p className="mt-3 text-2xl font-bold text-amber-700">
            {microphoneStatus}
          </p>
        </section>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-3">
        <section className="rounded-lg border border-slate-200 bg-white p-5">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            Source Language
          </h2>
          <p className="mt-3 text-xl font-bold">
            {formatLanguage(meeting.source_language)}
          </p>
        </section>
        <section className="rounded-lg border border-slate-200 bg-white p-5">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            Target Language
          </h2>
          <p className="mt-3 text-xl font-bold">
            {formatLanguage(meeting.target_language)}
          </p>
        </section>
        <section className="rounded-lg border border-slate-200 bg-white p-5">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            Created Time
          </h2>
          <p className="mt-3 text-xl font-bold">{meeting.created_at}</p>
        </section>
      </div>

      <div className="mt-6 grid gap-4 md:grid-cols-3">
        <section className="rounded-lg border border-slate-200 bg-white p-5">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            Recording Duration
          </h2>
          <p className="mt-3 text-xl font-bold">
            {formatDuration(recordingDuration)}
          </p>
        </section>
        <section className="rounded-lg border border-slate-200 bg-white p-5">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            Audio Upload Status
          </h2>
          <p className="mt-3 text-xl font-bold">{audioUploadStatus}</p>
        </section>
        <section className="rounded-lg border border-slate-200 bg-white p-5">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            Audio File
          </h2>
          <p className="mt-3 break-all text-sm font-semibold">
            {uploadedFileName ?? meeting.audio_file ?? "No audio uploaded"}
          </p>
          {meeting.audio_duration ? (
            <p className="mt-2 text-sm text-slate-600">
              Duration: {meeting.audio_duration}s
            </p>
          ) : null}
        </section>
      </div>

      {error ? <p className="mt-5 text-sm text-red-700">{error}</p> : null}

      <section className="mt-6 rounded-lg border border-slate-200 bg-white p-5">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
              Real-time Chinese Subtitles
            </h2>
            <p className="mt-3 text-xl font-bold">
              Realtime Status: {realtimeStatus}
            </p>
            <p className="mt-2 text-sm font-semibold text-meeting-blue">
              Current Step: {getCurrentStep()}
            </p>
            <p className="mt-2 text-sm font-semibold text-slate-700">
              Current Chunk: {currentRealtimeChunk}
            </p>
            <p className="mt-2 text-sm font-semibold text-slate-700">
              WebSocket Status: {webSocketStatus}
            </p>
            <p className="mt-2 text-sm text-slate-600">
              Latest Text: {latestRealtimeText || "No realtime text yet."}
            </p>
            <p className="mt-2 text-sm text-slate-600">
              Current Translation: {currentTranslation || "No English subtitle yet."}
            </p>
            <p className="mt-2 text-sm font-semibold text-slate-700">
              Translation: {translationProvider}
            </p>
            {translationProvider === "Mock Fallback" && translationFallbackReason ? (
              <p className="mt-2 text-sm text-amber-700">
                Mock Fallback Reason: {translationFallbackReason}
              </p>
            ) : null}
            <p className="mt-2 text-sm font-semibold text-slate-700">
              Latency: {translationLatencyMs} ms
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <button
              className="rounded-lg bg-meeting-blue px-5 py-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-slate-400"
              disabled={isRealtimeCaptioning || !isWhisperReady}
              onClick={handleStartRealtimeCaption}
              type="button"
            >
              Start Realtime Caption
            </button>
            <Link
              className="rounded-lg border border-meeting-blue px-5 py-3 text-sm font-semibold text-meeting-blue hover:bg-blue-50"
              href={`/screen?meeting_id=${encodeURIComponent(meetingId)}`}
              target="_blank"
            >
              Open Screen Mode
            </Link>
            <button
              className="rounded-lg bg-red-700 px-5 py-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-slate-400"
              disabled={isEndingMeeting}
              onClick={handleEndMeeting}
              type="button"
            >
              {isEndingMeeting ? "Generating Minutes..." : "End Meeting & Generate Minutes"}
            </button>
            <button
              className="rounded-lg bg-slate-900 px-5 py-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-slate-400"
              disabled={!isRealtimeCaptioning}
              onClick={handleStopRealtimeCaption}
              type="button"
            >
              Stop Realtime Caption
            </button>
          </div>
        </div>
        <div className="mt-5 rounded-lg bg-slate-50 p-4">
          <h3 className="text-sm font-semibold text-slate-500">
            Full Realtime Transcript
          </h3>
          <p className="mt-3 max-h-72 overflow-y-auto whitespace-pre-wrap text-slate-800">
            {realtimeTranscript || "Realtime Chinese subtitles will appear here."}
          </p>
        </div>
      </section>

      <section className="mt-6 rounded-lg border border-slate-200 bg-white p-5">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
              Speech Recognition
            </h2>
            <p className="mt-3 text-xl font-bold">
              Transcript Status: {transcriptStatus}
            </p>
            <p className="mt-2 text-sm font-semibold text-slate-700">
              Whisper Status: {whisperStatus}
            </p>
            {!isWhisperReady ? (
              <p className="mt-2 text-sm text-amber-700">
                Please install Whisper model first.
              </p>
            ) : null}
            {transcriptFile ? (
              <p className="mt-2 break-all text-sm text-slate-600">
                Transcript File: {transcriptFile}
              </p>
            ) : null}
          </div>
          <button
            className="rounded-lg bg-meeting-blue px-5 py-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-slate-400"
            disabled={isTranscribing || !meeting.audio_file || !isWhisperReady}
            onClick={handleGenerateTranscript}
            type="button"
          >
            {isTranscribing ? "Processing..." : "Optional: Generate Full Transcript"}
          </button>
        </div>
        <div className="mt-5 rounded-lg bg-slate-50 p-4">
          <h3 className="text-sm font-semibold text-slate-500">
            Transcript Preview
          </h3>
          <p className="mt-3 whitespace-pre-wrap text-slate-800">
            {transcriptPreview || "No transcript generated yet."}
          </p>
        </div>
      </section>

      <div className="mt-8 flex flex-wrap gap-3">
        <button
          className="rounded-lg bg-meeting-blue px-5 py-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-slate-400"
          disabled={isRecording}
          onClick={handleStartMeeting}
          type="button"
        >
          Start Meeting
        </button>
        <button
          className="rounded-lg bg-slate-900 px-5 py-3 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:bg-slate-400"
          disabled={!isRecording}
          onClick={handleStopMeeting}
          type="button"
        >
          Stop Meeting
        </button>
      </div>
    </>
  );
}

