import { PrimaryButton } from "@/components/PrimaryButton";
import { RecentMeetings } from "@/components/RecentMeetings";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-slate-50 px-6 py-10 text-ink">
      <section className="mx-auto flex min-h-[80vh] max-w-5xl flex-col justify-center">
        <p className="mb-4 text-sm font-semibold uppercase tracking-[0.22em] text-meeting-blue">
          Alpha 1.1.2
        </p>
        <h1 className="max-w-3xl text-5xl font-bold leading-tight md:text-7xl">
          TransForum AI
        </h1>
        <p className="mt-6 max-w-2xl text-2xl font-semibold text-slate-700">
          First Real Meeting Demo
        </p>
        <p className="mt-4 max-w-2xl text-lg leading-8 text-slate-600">
          一个人、一台电脑、一个麦克风、一台投影仪，5 分钟开启一场中英双语 AI 同传会议，并生成会议纪要。
        </p>
        <div className="mt-8 rounded-lg border border-blue-100 bg-white p-5 shadow-sm">
          <h2 className="text-lg font-bold">First Real Meeting Demo Flow</h2>
          <ol className="mt-3 grid gap-2 text-sm font-semibold text-slate-700 md:grid-cols-4">
            <li>1. Create Meeting</li>
            <li>2. Start Realtime Caption</li>
            <li>3. Open Screen Mode</li>
            <li>4. End Meeting & Generate Minutes</li>
          </ol>
        </div>
        <div className="mt-10 flex flex-wrap gap-4">
          <PrimaryButton href="/meeting/new">
            Start First Real Meeting Demo
          </PrimaryButton>
          <PrimaryButton href="/meeting/new" variant="secondary">
            Create Meeting
          </PrimaryButton>
        </div>
      </section>
      <RecentMeetings />
    </main>
  );
}
