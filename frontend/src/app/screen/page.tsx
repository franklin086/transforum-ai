import Link from "next/link";

export default function ScreenPage() {
  return (
    <main className="flex min-h-screen items-center bg-black px-8 py-10 text-white">
      <Link
        className="fixed right-6 top-5 rounded-lg border border-white/20 px-4 py-2 text-sm text-white/80"
        href="/meeting/live"
      >
        Exit Screen
      </Link>
      <section className="mx-auto w-full max-w-7xl">
        <div className="border-b border-white/20 pb-10">
          <p className="text-3xl font-semibold text-blue-300">中文：</p>
          <p className="mt-6 text-6xl font-bold leading-tight md:text-8xl">
            大家好，欢迎参加今天的论坛。
          </p>
        </div>
        <div className="pt-10">
          <p className="text-3xl font-semibold text-blue-300">English:</p>
          <p className="mt-6 text-5xl font-bold leading-tight md:text-7xl">
            Hello everyone, welcome to today’s forum.
          </p>
        </div>
      </section>
    </main>
  );
}
