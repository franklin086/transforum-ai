import { PrimaryButton } from "@/components/PrimaryButton";
import { RecentMeetings } from "@/components/RecentMeetings";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-slate-50 px-6 py-10 text-ink">
      <section className="mx-auto flex min-h-[80vh] max-w-5xl flex-col justify-center">
        <p className="mb-4 text-sm font-semibold uppercase tracking-[0.22em] text-meeting-blue">
          Alpha 0.5.1
        </p>
        <h1 className="max-w-3xl text-5xl font-bold leading-tight md:text-7xl">
          TransForum AI
        </h1>
        <p className="mt-6 max-w-2xl text-2xl font-semibold text-slate-700">
          First Real Meeting
        </p>
        <p className="mt-4 max-w-2xl text-lg leading-8 text-slate-600">
          让任何人都能在 5 分钟内开启一场专业的双语国际会议，并在会议结束时获得完整的会议成果。
        </p>
        <div className="mt-10 flex flex-wrap gap-4">
          <PrimaryButton href="/meeting/new">Create Meeting</PrimaryButton>
          <PrimaryButton href="/screen" variant="secondary">
            Open Screen Mode
          </PrimaryButton>
        </div>
      </section>
      <RecentMeetings />
    </main>
  );
}
