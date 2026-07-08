import { cn } from "@/lib/utils";

type LogoProps = {
  variant?: "full" | "icon";
  className?: string;
  size?: number;
};

export function Logo({ variant = "full", className, size = 32 }: LogoProps) {
  const padding = Math.max(4, Math.round(size * 0.2));

  const mark = (
    <span
      className="inline-flex items-center justify-center rounded-xl shadow-sm ring-1 ring-black/5 text-slate-900"
      style={{ padding }}
    >
      <svg
        width={size}
        height={size}
        viewBox="0 0 64 64"
        fill="none"
        aria-hidden="true"
      >
        <path
          d="M32 6 C20.4 6 12 14.4 12 26 C12 40.5 32 58 32 58 C32 58 52 40.5 52 26 C52 14.4 43.6 6 32 6 Z"
          stroke="white"
          strokeWidth="3"
          fill="none"
        />
        <rect x="22" y="26" width="4.6" height="8" rx="1.4" className="fill-blue-600" />
        <rect x="29.7" y="20" width="4.6" height="14" rx="1.4" className="fill-blue-600" />
        <rect x="37.4" y="14" width="4.6" height="20" rx="1.4" className="fill-blue-600" />
      </svg>
    </span>
  );

  if (variant === "icon") {
    return <span className={cn(className)}>{mark}</span>;
  }

  return (
    <span className={cn("inline-flex items-center gap-2 text-slate-900 dark:text-white", className)}>
      <span className="inline-flex items-center gap-0">
        {mark}
        <span data-slot="wordmark" className="inline-flex items-center gap-0.5 -ml-1.5 text-2xl tracking-tight font-normal">
          Market<span className="font-extrabold">Scout</span>
        </span>
      </span>
      <span className="text-[11px] font-semibold leading-none tracking-normal px-1.5 py-1 rounded-md border border-slate-900/20 dark:border-white/50 text-slate-900/70 dark:text-white/80">
          AI
      </span>
    </span>
  );
}
