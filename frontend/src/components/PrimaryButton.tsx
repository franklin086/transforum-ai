import Link from "next/link";

type PrimaryButtonProps = {
  href: string;
  children: React.ReactNode;
  variant?: "primary" | "secondary";
};

export function PrimaryButton({
  href,
  children,
  variant = "primary"
}: PrimaryButtonProps) {
  const classes =
    variant === "primary"
      ? "bg-meeting-blue text-white hover:bg-blue-700"
      : "border border-slate-300 bg-white text-ink hover:border-meeting-blue hover:text-meeting-blue";

  return (
    <Link
      className={`inline-flex items-center justify-center rounded-lg px-5 py-3 text-sm font-semibold transition ${classes}`}
      href={href}
    >
      {children}
    </Link>
  );
}
