import Link from "next/link";
import { Suspense } from "react";
import { MeetingConsole } from "@/components/MeetingConsole";

export default function LiveMeetingPage() {
  return (
    <main className="min-h-screen bg-slate-100 px-6 py-8 text-ink">
      <section className="mx-auto max-w-6xl">
        <div>
          <div>
            <Link className="text-sm font-semibold text-meeting-blue" href="/">
              Back to Home
            </Link>
            <h1 className="mt-4 text-4xl font-bold">Meeting Console</h1>
          </div>
        </div>

        <Suspense
          fallback={
            <section className="mt-8 rounded-lg border border-slate-200 bg-white p-8">
              Loading meeting...
            </section>
          }
        >
          <MeetingConsole />
        </Suspense>
      </section>
    </main>
  );
}
