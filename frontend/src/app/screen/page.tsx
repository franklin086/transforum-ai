"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useMemo, useState } from "react";
import { getMeeting, getRealtimeBilingualTranscript } from "@/services/api";

function extractRecentLines(chinese: string, english: string) {
  return [chinese, english]
    .map((line) => line.trim())
    .filter(Boolean)
    .slice(-5);
}

function ScreenContent() {
  const searchParams = useSearchParams();
  const meetingId = searchParams.get("meeting_id");
  const [meetingName, setMeetingName] = useState("");
  const [chineseCaption, setChineseCaption] = useState("");
  const [englishCaption, setEnglishCaption] = useState("");
  const [translationProvider, setTranslationProvider] = useState("Mock");
  const [translationLatencyMs, setTranslationLatencyMs] = useState(0);
  const [updatedAt, setUpdatedAt] = useState("");
  const [status, setStatus] = useState("Waiting for meeting");
  const recentLines = useMemo(
    () => extractRecentLines(chineseCaption, englishCaption),
    [chineseCaption, englishCaption]
  );

  useEffect(() => {
    if (!meetingId) {
      setStatus("Missing meeting_id");
      return;
    }

    getMeeting(meetingId)
      .then((result) => {
        setMeetingName(result.meeting.name);
      })
      .catch(() => {
        setMeetingName("");
      });
  }, [meetingId]);

  useEffect(() => {
    if (!meetingId) {
      return;
    }

    let isActive = true;
    const activeMeetingId = meetingId;

    async function refreshTranscript() {
      try {
        const result = await getRealtimeBilingualTranscript(activeMeetingId);
        if (!isActive) {
          return;
        }
        setChineseCaption(result.chinese);
        setEnglishCaption(result.english);
        setTranslationProvider(result.provider === "gemini" ? "Gemini" : "Mock");
        setTranslationLatencyMs(result.latency_ms ?? 0);
        setUpdatedAt(result.updated_at ?? "");
        setStatus(result.chinese || result.english ? "Live" : "No bilingual subtitles yet");
      } catch {
        if (isActive) {
          setStatus("Bilingual subtitles unavailable");
        }
      }
    }

    void refreshTranscript();
    const intervalId = window.setInterval(refreshTranscript, 2000);

    return () => {
      isActive = false;
      window.clearInterval(intervalId);
    };
  }, [meetingId]);

  async function handleFullscreen() {
    if (!document.fullscreenElement) {
      await document.documentElement.requestFullscreen();
    } else {
      await document.exitFullscreen();
    }
  }

  return (
    <main className="min-h-screen overflow-hidden bg-[#061225] px-8 py-8 text-white">
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(circle_at_50%_10%,rgba(37,99,235,0.35),transparent_36%),linear-gradient(135deg,rgba(8,47,73,0.95),rgba(2,6,23,0.98))]" />
      <div className="relative mx-auto flex min-h-[calc(100vh-4rem)] max-w-7xl flex-col">
        <header className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold tracking-wide md:text-5xl">
              TransForum AI Live Caption
            </h1>
            <p className="mt-2 text-sm font-semibold uppercase tracking-[0.24em] text-blue-200">
              Alpha 1.1.2 Demo Mode
            </p>
            <p className="mt-3 text-lg text-blue-100 md:text-2xl">
              {meetingName || meetingId || "No meeting selected"}
            </p>
            <p className="mt-2 text-sm font-semibold text-blue-100/80">
              Translation: {translationProvider}
              {translationProvider === "Gemini"
                ? ` · ${translationLatencyMs} ms`
                : ""}
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            {meetingId ? (
              <Link
                className="rounded-lg border border-white/20 bg-white/10 px-4 py-3 text-sm font-semibold text-white hover:bg-white/20"
                href={`/meeting/live?meeting_id=${encodeURIComponent(meetingId)}`}
              >
                Back to Console
              </Link>
            ) : null}
            <button
              className="rounded-lg bg-white px-4 py-3 text-sm font-semibold text-slate-950 hover:bg-blue-100"
              onClick={handleFullscreen}
              type="button"
            >
              Full Screen
            </button>
          </div>
        </header>

        <section className="flex flex-1 flex-col items-center justify-center gap-10 py-10 text-center">
          <p className="text-lg font-semibold uppercase tracking-[0.24em] text-blue-200">
            {status}
          </p>

          <div className="w-full max-w-6xl border-b border-white/20 pb-10">
            <h2 className="mb-5 text-3xl font-semibold text-blue-200 md:text-4xl">
              中文
            </h2>
            <p className="whitespace-pre-wrap break-words text-5xl font-bold leading-tight text-white md:text-7xl lg:text-8xl">
              {chineseCaption || "实时中文字幕将在这里显示"}
            </p>
          </div>

          <div className="w-full max-w-6xl">
            <h2 className="mb-5 text-3xl font-semibold text-blue-200 md:text-4xl">
              English
            </h2>
            <p className="whitespace-pre-wrap break-words text-4xl font-bold leading-tight text-blue-50 md:text-6xl lg:text-7xl">
              {englishCaption || "English subtitles will appear here."}
            </p>
          </div>
        </section>

        <section className="rounded-lg border border-white/15 bg-white/10 p-6 backdrop-blur">
          <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
            <h2 className="text-xl font-semibold text-blue-100">
              Recent Bilingual Captions
            </h2>
            <p className="text-sm text-blue-100/80">
              {updatedAt ? `Updated: ${updatedAt}` : "Auto refresh: 2s"}
            </p>
          </div>
          <div className="space-y-3 text-2xl font-semibold leading-relaxed text-white/90 md:text-3xl">
            {recentLines.length > 0 ? (
              recentLines.map((line) => <p key={line}>{line}</p>)
            ) : (
              <p className="text-white/60">等待会议控制台开始实时双语字幕。</p>
            )}
          </div>
        </section>
      </div>
    </main>
  );
}

export default function ScreenPage() {
  return (
    <Suspense
      fallback={
        <main className="flex min-h-screen items-center justify-center bg-[#061225] px-8 text-center text-white">
          <p className="text-4xl font-bold">Loading live caption...</p>
        </main>
      }
    >
      <ScreenContent />
    </Suspense>
  );
}
