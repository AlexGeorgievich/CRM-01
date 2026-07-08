import { clsx } from "clsx";
import type { ButtonHTMLAttributes, InputHTMLAttributes, ReactNode, SelectHTMLAttributes, TextareaHTMLAttributes } from "react";

export function Button({ className, ...props }: ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      className={clsx(
        "inline-flex h-9 items-center justify-center gap-2 rounded-md border border-ink bg-ink px-3 text-sm font-medium text-white transition hover:bg-black",
        className
      )}
      {...props}
    />
  );
}

export function GhostButton({ className, ...props }: ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      className={clsx(
        "inline-flex h-9 items-center justify-center gap-2 rounded-md border border-line bg-white px-3 text-sm font-medium text-ink transition hover:bg-panel",
        className
      )}
      {...props}
    />
  );
}

export function IconButton({ label, className, ...props }: ButtonHTMLAttributes<HTMLButtonElement> & { label: string }) {
  return (
    <button
      aria-label={label}
      title={label}
      className={clsx(
        "inline-flex h-9 w-9 items-center justify-center rounded-md border border-line bg-white text-ink transition hover:bg-panel",
        className
      )}
      {...props}
    />
  );
}

export function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className="grid gap-1 text-xs font-medium text-muted">
      <span>{label}</span>
      {children}
    </label>
  );
}

export function Input({ className, ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return <input className={clsx("h-9 rounded-md border border-line bg-white px-3 text-sm text-ink outline-none focus:border-brand", className)} {...props} />;
}

export function Select({ className, ...props }: SelectHTMLAttributes<HTMLSelectElement>) {
  return <select className={clsx("h-9 rounded-md border border-line bg-white px-3 text-sm text-ink outline-none focus:border-brand", className)} {...props} />;
}

export function Textarea({ className, ...props }: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return <textarea className={clsx("min-h-20 rounded-md border border-line bg-white px-3 py-2 text-sm text-ink outline-none focus:border-brand", className)} {...props} />;
}

export function Panel({ children, className }: { children: ReactNode; className?: string }) {
  return <section className={clsx("rounded-lg border border-line bg-white shadow-soft", className)}>{children}</section>;
}

export function Badge({ children, tone = "neutral" }: { children: ReactNode; tone?: "neutral" | "success" | "warning" | "danger" }) {
  const tones = {
    neutral: "border-line bg-panel text-muted",
    success: "border-emerald-200 bg-emerald-50 text-success",
    warning: "border-amber-200 bg-amber-50 text-warning",
    danger: "border-red-200 bg-red-50 text-danger"
  };
  return <span className={clsx("inline-flex items-center rounded-md border px-2 py-1 text-xs font-medium", tones[tone])}>{children}</span>;
}
