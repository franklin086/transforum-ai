"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useMemo, useState } from "react";
import { generateMinutes, getMeeting } from "@/services/api";
import type { Meeting } from "@/types/meeting";

function isMockPlaceholder(text?: string | null) {
  return (text ?? "").trim().toLowerCase().startsWith("[" + "mock en" + "]");
}

function splitLines(text?: string | null) {
  return (text ?? "")
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .filter((line) => !isMockPlaceholder(line));
}

function providerLabel(meeting?: Meeting | null, englishLines: string[] = []) {
  if (meeting?.translation_provider === "gemini" && englishLines.length > 0) {
    return "Gemini";
  }
  if (meeting?.translation_provider === "mock" && meeting.translation_fallback_reason) {
    return "Mock Fallback";
  }
  if (meeting?.translation_provider === "error") {
    return "Error";
  }
  return "Waiting";
}

function translationEmptyText(meeting?: Meeting | null) {
  if (meeting?.translation_provider === "mock" && meeting.translation_fallback_reason) {
    return `Gemini unavailable. ${meeting.translation_fallback_reason}`;
  }
  if (meeting?.translation_provider === "error" && meeting.translation_fallback_reason) {
    return `Translation error. ${meeting.translation_fallback_reason}`;
  }
  return "No English translation content yet.";
}

function LinesBlock({ emptyText, lines }: { emptyText: string; lines: string[] }) {
  if (lines.length === 0) {
    return <p className="mt-4 text-slate-500">{emptyText}</p>;
  }

  return (
    <div className="mt-4 max-h-96 overflow-y-auto rounded-lg bg-slate-50 p-4">
      {lines.map((line) => (
        <p className="mb-3 whitespace-pre-wrap text-slate-800 last:mb-0" key={line}>
          {line}
        </p>
      ))}
    </div>
  );
}

function MinutesContent() {
  const searchParams = useSearchParams();
  const meetingId = searchParams.get("meeting_id");
  const [meeting, setMeeting] = useState<Meeting | null>(null);
  const [isLoading, setIsLoading] = useState(Boolean(meetingId));
  const [error, setError] = useState<string | null>(null);

  const realtimeChineseLines = useMemo(
    () => splitLines(meeting?.realtime_transcript_text),
    [meeting?.realtime_transcript_text]
  );
  const englishLines = useMemo(
    () => splitLines(meeting?.english_transcript_text),
    [meeting?.english_transcript_text]
  );
  const keyPoints = useMemo(
    () => splitLines(meeting?.minutes_key_points),
    [meeting?.minutes_key_points]
  );
  const actionItems = useMemo(
    () => splitLines(meeting?.minutes_action_items),
    [meeting?.minutes_action_items]
  );
  const nextSteps = useMemo(
    () => splitLines(meeting?.minutes_next_steps),
    [meeting?.minutes_next_steps]
  );

  useEffect(() => {
    if (!meetingId) {
      setIsLoading(false);
      setError("Missing meeting_id.");
      return;
    }

    const activeMeetingId = meetingId;

    async function loadMinutes() {
      try {
        const meetingResult = await getMeeting(activeMeetingId);
        if (!meetingResult.meeting.minutes_summary) {
          await generateMinutes(activeMeetingId);
        }
        const refreshed = await getMeeting(activeMeetingId);
        setMeeting(refreshed.meeting);
        setError(null);
      } catch {
        setError("Minutes unavailable. Confirm the backend is running.");
      } finally {
        setIsLoading(false);
      }
    }

    void loadMinutes();
  }, [meetingId]);

  if (isLoading) {
    return (
      <section className="mt-8 rounded-lg border border-slate-200 bg-white p-8">
        <p className="text-slate-600">Loading meeting minutes...</p>
      </section>
    );
  }

  if (error || !meeting) {
    return (
      <section className="mt-8 rounded-lg border border-slate-200 bg-white p-8">
        <h2 className="text-2xl font-bold">Minutes unavailable</h2>
        <p className="mt-3 text-red-700">{error}</p>
        <Link className="mt-6 inline-flex rounded-lg bg-meeting-blue px-5 py-3 text-sm font-semibold text-white" href="/">
          Back to Home
        </Link>
      </section>
    );
  }

  return (
    <div className="mt-8 space-y-6">
      <section className="rounded-lg border border-slate-200 bg-white p-6">
        <p className="text-sm font-semibold uppercase tracking-wide text-slate-500">
          Meeting Minutes
        </p>
        <h2 className="mt-3 text-3xl font-bold">{meeting.name}</h2>
        <p className="mt-2 text-sm text-slate-600">
          Meeting ID: {meeting.id} | Status: {meeting.status}
        </p>
        <p className="mt-2 text-sm font-semibold text-slate-700">
          Translation Provider: {providerLabel(meeting, englishLines)}
        </p>
        <p className="mt-2 text-sm font-semibold text-slate-700">
          Translation Status: {meeting.translation_status || "waiting"}
        </p>
        {meeting.translation_fallback_reason ? (
          <p className="mt-2 text-sm text-amber-700">
            Fallback Reason: {meeting.translation_fallback_reason}
          </p>
        ) : null}
      </section>

      <section className="rounded-lg border border-slate-200 bg-white p-6">
        <h3 className="text-xl font-bold">Meeting Summary</h3>
        <p className="mt-4 whitespace-pre-wrap text-lg leading-8 text-slate-800">
          {meeting.minutes_summary || "No meeting summary generated yet."}
        </p>
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-lg border border-slate-200 bg-white p-6">
          <h3 className="text-xl font-bold">Realtime Chinese Captions</h3>
          <LinesBlock emptyText="No realtime Chinese captions yet." lines={realtimeChineseLines} />
        </div>
        <div className="rounded-lg border border-slate-200 bg-white p-6">
          <h3 className="text-xl font-bold">English Translation</h3>
          <LinesBlock emptyText={translationEmptyText(meeting)} lines={englishLines} />
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-3">
        <div className="rounded-lg border border-slate-200 bg-white p-6">
          <h3 className="text-xl font-bold">Key Points</h3>
          <LinesBlock emptyText="No key points yet." lines={keyPoints} />
        </div>
        <div className="rounded-lg border border-slate-200 bg-white p-6">
          <h3 className="text-xl font-bold">Action Items</h3>
          <LinesBlock emptyText="No action items yet." lines={actionItems} />
        </div>
        <div className="rounded-lg border border-slate-200 bg-white p-6">
          <h3 className="text-xl font-bold">Next Steps</h3>
          <LinesBlock emptyText="No next steps yet." lines={nextSteps} />
        </div>
      </section>

      <div className="flex flex-wrap gap-3">
        <Link className="rounded-lg bg-meeting-blue px-5 py-3 text-sm font-semibold text-white" href={`/meeting/live?meeting_id=${encodeURIComponent(meeting.id)}`}>
          Back to Console
        </Link>
        <Link className="rounded-lg border border-meeting-blue bg-white px-5 py-3 text-sm font-semibold text-meeting-blue" href={`/screen?meeting_id=${encodeURIComponent(meeting.id)}`} target="_blank">
          Open Screen Mode
        </Link>
        <Link className="rounded-lg border border-slate-300 bg-white px-5 py-3 text-sm font-semibold text-slate-900" href="/">
          Back to Home
        </Link>
      </div>
    </div>
  );
}

export default function MeetingMinutesPage() {
  return (
    <main className="min-h-screen bg-slate-100 px-6 py-8 text-ink">
      <section className="mx-auto max-w-6xl">
        <Link className="text-sm font-semibold text-meeting-blue" href="/">
          Back to Home
        </Link>
        <h1 className="mt-4 text-4xl font-bold">Meeting Minutes</h1>
        <Suspense
          fallback={
            <section className="mt-8 rounded-lg border border-slate-200 bg-white p-8">
              Loading meeting minutes...
            </section>
          }
        >
          <MinutesContent />
        </Suspense>
      </section>
    </main>
  );
}
