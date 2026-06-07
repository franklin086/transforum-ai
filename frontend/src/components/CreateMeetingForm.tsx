"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import { createMeeting } from "@/services/api";

export function CreateMeetingForm() {
  const router = useRouter();
  const [name, setName] = useState("APEC Youth Forum Demo");
  const [sourceLanguage, setSourceLanguage] = useState("zh");
  const [targetLanguage, setTargetLanguage] = useState("en");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    if (!name.trim()) {
      setError("Meeting Name is required.");
      return;
    }

    setIsSubmitting(true);

    try {
      const result = await createMeeting({
        name,
        source_language: sourceLanguage,
        target_language: targetLanguage
      });

      router.push(`/meeting/live?meeting_id=${result.meeting.id}`);
    } catch {
      setError("Could not create meeting. Confirm the backend is running.");
      setIsSubmitting(false);
    }
  }

  return (
    <form
      className="mt-8 rounded-lg border border-slate-200 bg-white p-6 shadow-sm"
      onSubmit={handleSubmit}
    >
      <label className="block">
        <span className="text-sm font-semibold text-slate-700">
          Meeting Name
        </span>
        <input
          className="mt-2 w-full rounded-lg border border-slate-300 px-4 py-3 outline-none focus:border-meeting-blue"
          name="meetingName"
          onChange={(event) => setName(event.target.value)}
          type="text"
          value={name}
        />
      </label>

      <div className="mt-5 grid gap-5 md:grid-cols-2">
        <label className="block">
          <span className="text-sm font-semibold text-slate-700">
            Source Language
          </span>
          <select
            className="mt-2 w-full rounded-lg border border-slate-300 px-4 py-3 outline-none focus:border-meeting-blue"
            name="sourceLanguage"
            onChange={(event) => setSourceLanguage(event.target.value)}
            value={sourceLanguage}
          >
            <option value="zh">中文 zh</option>
          </select>
        </label>

        <label className="block">
          <span className="text-sm font-semibold text-slate-700">
            Target Language
          </span>
          <select
            className="mt-2 w-full rounded-lg border border-slate-300 px-4 py-3 outline-none focus:border-meeting-blue"
            name="targetLanguage"
            onChange={(event) => setTargetLanguage(event.target.value)}
            value={targetLanguage}
          >
            <option value="en">English en</option>
          </select>
        </label>
      </div>

      {error ? <p className="mt-5 text-sm text-red-700">{error}</p> : null}

      <div className="mt-8 flex flex-wrap gap-3">
        <button
          className="inline-flex rounded-lg bg-meeting-blue px-5 py-3 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-400"
          disabled={isSubmitting}
          type="submit"
        >
          {isSubmitting ? "Creating..." : "Create Meeting"}
        </button>
        <Link
          className="inline-flex rounded-lg border border-slate-300 bg-white px-5 py-3 text-sm font-semibold text-slate-700 transition hover:border-meeting-blue hover:text-meeting-blue"
          href="/"
        >
          Cancel
        </Link>
      </div>
    </form>
  );
}
