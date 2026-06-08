"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useMemo, useState } from "react";
import { generateMinutes, getMeeting } from "@/services/api";
import type { Meeting } from "@/types/meeting";

function splitLines(text?: string | null) {
  return (text ?? "")
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);
}

function MinutesContent() {
  const searchParams = useSearchParams();
  const meetingId = searchParams.get("meeting_id");
  const [meeting, setMeeting] = useState<Meeting | null>(null);
  const [isLoading, setIsLoading] = useState(Boolean(meetingId));
  const [error, setError] = useState<string | null>(null);

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
        <Link
          className="mt-6 inline-flex rounded-lg bg-meeting-blue px-5 py-3 text-sm font-semibold text-white"
          href="/"
        >
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
          Meeting ID: {meeting.id} · Status: {meeting.status}
        </p>
      </section>

      <section className="rounded-lg border border-slate-200 bg-white p-6">
        <h3 className="text-xl font-bold">会议摘要</h3>
        <p className="mt-4 whitespace-pre-wrap text-lg leading-8 text-slate-800">
          {meeting.minutes_summary || "暂无会议摘要。"}
        </p>
      </section>

      <section className="grid gap-6 lg:grid-cols-3">
        <div className="rounded-lg border border-slate-200 bg-white p-6">
          <h3 className="text-xl font-bold">核心观点</h3>
          <ul className="mt-4 space-y-3 text-slate-800">
            {(keyPoints.length ? keyPoints : ["暂无核心观点。"]).map((item) => (
              <li key={item}>• {item}</li>
            ))}
          </ul>
        </div>
        <div className="rounded-lg border border-slate-200 bg-white p-6">
          <h3 className="text-xl font-bold">待办事项</h3>
          <ul className="mt-4 space-y-3 text-slate-800">
            {(actionItems.length ? actionItems : ["暂无待办事项。"]).map((item) => (
              <li key={item}>• {item}</li>
            ))}
          </ul>
        </div>
        <div className="rounded-lg border border-slate-200 bg-white p-6">
          <h3 className="text-xl font-bold">下一步计划</h3>
          <ul className="mt-4 space-y-3 text-slate-800">
            {(nextSteps.length ? nextSteps : ["暂无下一步计划。"]).map((item) => (
              <li key={item}>• {item}</li>
            ))}
          </ul>
        </div>
      </section>

      <div className="flex flex-wrap gap-3">
        <Link
          className="rounded-lg bg-meeting-blue px-5 py-3 text-sm font-semibold text-white"
          href={`/meeting/live?meeting_id=${encodeURIComponent(meeting.id)}`}
        >
          Back to Console
        </Link>
        <Link
          className="rounded-lg border border-slate-300 bg-white px-5 py-3 text-sm font-semibold text-slate-900"
          href="/"
        >
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
