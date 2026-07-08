"use client";

import { FormEvent, useState } from "react";
import { LogIn } from "lucide-react";
import { Button, Field, Input, Panel } from "./ui";

export function LoginCard({ onLogin }: { onLogin: (username: string, password: string) => Promise<void> }) {
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("admin12345");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError("");
    try {
      await onLogin(username, password);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка входа");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="grid min-h-screen place-items-center bg-panel px-4">
      <Panel className="w-full max-w-sm p-6">
        <div className="mb-6">
          <div className="text-xl font-semibold text-ink">CRM</div>
          <div className="mt-1 text-sm text-muted">Вход в рабочую область</div>
        </div>
        <form className="grid gap-4" onSubmit={submit}>
          <Field label="Логин">
            <Input value={username} onChange={(event) => setUsername(event.target.value)} autoComplete="username" />
          </Field>
          <Field label="Пароль">
            <Input value={password} onChange={(event) => setPassword(event.target.value)} type="password" autoComplete="current-password" />
          </Field>
          {error ? <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-danger">{error}</div> : null}
          <Button disabled={loading} type="submit">
            <LogIn size={16} />
            Войти
          </Button>
        </form>
      </Panel>
    </main>
  );
}
