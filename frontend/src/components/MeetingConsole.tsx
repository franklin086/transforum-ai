"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import {
  getMeeting,
  getTranscription,
  getWhisperModelStatus,
  startTranscription,
  uploadMeetingAudio
} from "@/services/api";
import type { Meeting } from "@/types/meeting";

const languageLabels: Record<string, string> = {
  zh: "中文 zh",
  en: "English en"
};

function formatLanguage(code: string) {
  return languageLabels[code] ?? code;
}

export function MeetingConsole() {
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
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
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
    };
  }, []);

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

  if (error || !meeting) {
    return (
      <section className="mt-8 rounded-lg border border-slate-200 bg-white p-8">
        <h2 className="text-2xl font-bold">Meeting unavailable</h2>
        <p className="mt-3 text-red-700">{error}</p>
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
            {isTranscribing ? "Processing..." : "Generate Transcript"}
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
