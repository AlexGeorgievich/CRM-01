"use client";

import { BookOpen, CircleDot, Database, UserCog } from "lucide-react";
import type { Dictionaries, User } from "@/lib/types";
import { Badge, Panel } from "./ui";

export function AdminView({ dictionaries, users }: { dictionaries: Dictionaries; users: User[] }) {
  return (
    <div className="grid gap-5">
      <div className="grid gap-4 md:grid-cols-4">
        <AdminMetric label="Пользователи" value={users.length} icon={<UserCog size={18} />} />
        <AdminMetric label="Статусы" value={dictionaries.statuses.length} icon={<CircleDot size={18} />} />
        <AdminMetric label="Курсы" value={dictionaries.courses.length} icon={<BookOpen size={18} />} />
        <AdminMetric label="Источники" value={dictionaries.sources.length} icon={<Database size={18} />} />
      </div>

      <Panel className="overflow-hidden">
        <div className="border-b border-line px-4 py-3 text-sm font-semibold">Пользователи</div>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[760px] border-collapse text-sm">
            <thead className="bg-panel text-left text-xs uppercase text-muted">
              <tr>
                <th className="px-4 py-3">Имя</th>
                <th className="px-4 py-3">Логин</th>
                <th className="px-4 py-3">Email</th>
                <th className="px-4 py-3">Роль</th>
                <th className="px-4 py-3">Статус</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.id} className="border-t border-line">
                  <td className="px-4 py-3 font-medium">{user.full_name}</td>
                  <td className="px-4 py-3">{user.username}</td>
                  <td className="px-4 py-3">{user.email ?? "-"}</td>
                  <td className="px-4 py-3"><Badge>{user.role}</Badge></td>
                  <td className="px-4 py-3"><Badge tone={user.is_active ? "success" : "danger"}>{user.is_active ? "Активен" : "Заблокирован"}</Badge></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>

      <div className="grid gap-5 lg:grid-cols-3">
        <DictionaryPanel title="Статусы" items={dictionaries.statuses.map((item) => `${item.name} · ${item.code}`)} />
        <DictionaryPanel title="Курсы" items={dictionaries.courses.map((item) => item.name)} />
        <DictionaryPanel title="Источники" items={dictionaries.sources.map((item) => item.name)} />
      </div>
    </div>
  );
}

function AdminMetric({ label, value, icon }: { label: string; value: number; icon: React.ReactNode }) {
  return (
    <Panel className="p-4">
      <div className="flex items-center justify-between">
        <div className="text-sm text-muted">{label}</div>
        <div className="text-brand">{icon}</div>
      </div>
      <div className="mt-2 text-2xl font-semibold">{value}</div>
    </Panel>
  );
}

function DictionaryPanel({ title, items }: { title: string; items: string[] }) {
  return (
    <Panel className="p-4">
      <div className="mb-3 text-sm font-semibold">{title}</div>
      <div className="grid gap-2">
        {items.map((item) => (
          <div key={item} className="rounded-md border border-line bg-panel px-3 py-2 text-sm">{item}</div>
        ))}
      </div>
    </Panel>
  );
}
