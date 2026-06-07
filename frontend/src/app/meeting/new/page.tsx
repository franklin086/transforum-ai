import Link from "next/link";
import { CreateMeetingForm } from "@/components/CreateMeetingForm";

export default function NewMeetingPage() {
  return (
    <main className="min-h-screen bg-slate-50 px-6 py-10 text-ink">
      <section className="mx-auto max-w-3xl">
        <Link className="text-sm font-semibold text-meeting-blue" href="/">
          Back to Home
        </Link>
        <h1 className="mt-8 text-4xl font-bold">Create Meeting</h1>
        <p className="mt-3 text-slate-600">
          Configure the minimum fields required for First Real Meeting.
        </p>

        <CreateMeetingForm />
      </section>
    </main>
  );
}
