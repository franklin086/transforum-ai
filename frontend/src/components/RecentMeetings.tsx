"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { listMeetings } from "@/services/api";
import type { Meeting } from "@/types/meeting";

const languageLabels: Record<string, string> = {
  zh: "中文",
  en: "English"
};

function formatLanguage(code: string) {
  return languageLabels[code] ?? code;
}

export function RecentMeetings() {
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listMeetings()
      .then((result) => {
        setMeetings(result.meetings);
        setError(null);
      })
      .catch(() => {
        setError("Recent meetings are unavailable. Start the backend first.");
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, []);

  return (
    <section className="mx-auto w-full max-w-5xl pb-14">
      <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between gap-4">
          <h2 className="text-2xl font-bold">Recent Meetings</h2>
          <Link
            className="text-sm font-semibold text-meeting-blue"
            href="/meeting/new"
          >
            New meeting
          </Link>
        </div>

        {isLoading ? (
          <p className="mt-5 text-slate-600">Loading recent meetings...</p>
        ) : error ? (
          <p className="mt-5 text-sm text-amber-700">{error}</p>
        ) : meetings.length === 0 ? (
          <p className="mt-5 text-slate-600">
            No meetings yet. Create the first meeting to begin Sprint 1.
          </p>
        ) : (
          <div className="mt-5 divide-y divide-slate-100">
            {meetings.map((meeting) => (
              <Link
                className="block py-4 transition hover:text-meeting-blue"
                href={`/meeting/live?meeting_id=${meeting.id}`}
                key={meeting.id}
              >
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div>
                    <p className="font-semibold">{meeting.name}</p>
                    <p className="mt-1 text-sm text-slate-600">
                      {formatLanguage(meeting.source_language)} →{" "}
                      {formatLanguage(meeting.target_language)}
                    </p>
                  </div>
                  <span className="rounded-full bg-slate-100 px-3 py-1 text-sm font-semibold text-slate-700">
                    {meeting.status}
                  </span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
