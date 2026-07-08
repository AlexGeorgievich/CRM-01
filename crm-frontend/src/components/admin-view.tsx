"use client";

import { FormEvent, ReactNode, useState } from "react";
import { BookOpen, CircleDot, Database, KeyRound, Plus, UserCog } from "lucide-react";
import type { Dictionaries, DictionaryInput, DictionaryItem, Role, Status, StatusInput, User, UserCreateInput, UserUpdateInput } from "@/lib/types";
import { Badge, Button, Field, GhostButton, Input, Panel, Select } from "./ui";

type Props = {
  dictionaries: Dictionaries;
  users: User[];
  onCreateDictionary: (kind: keyof Dictionaries, payload: DictionaryInput | StatusInput) => Promise<void>;
  onCreateUser: (payload: UserCreateInput) => Promise<void>;
  onResetPassword: (id: number, password: string) => Promise<void>;
  onUpdateDictionary: (kind: keyof Dictionaries, id: number, payload: Partial<DictionaryInput | StatusInput>) => Promise<void>;
  onUpdateUser: (id: number, payload: UserUpdateInput) => Promise<void>;
};

const defaultUser: UserCreateInput = {
  username: "",
  password: "manager12345",
  email: "",
  full_name: "",
  role: "manager",
  is_active: true
};

export function AdminView({ dictionaries, users, onCreateDictionary, onCreateUser, onResetPassword, onUpdateDictionary, onUpdateUser }: Props) {
  const [userDraft, setUserDraft] = useState<UserCreateInput>(defaultUser);
  const [passwords, setPasswords] = useState<Record<number, string>>({});

  async function createUser(event: FormEvent) {
    event.preventDefault();
    await onCreateUser({ ...userDraft, email: userDraft.email || null });
    setUserDraft(defaultUser);
  }

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
        <form className="grid gap-3 border-b border-line p-4 lg:grid-cols-6" onSubmit={createUser}>
          <Field label="Логин">
            <Input value={userDraft.username} onChange={(event) => setUserDraft({ ...userDraft, username: event.target.value })} required />
          </Field>
          <Field label="Имя">
            <Input value={userDraft.full_name} onChange={(event) => setUserDraft({ ...userDraft, full_name: event.target.value })} required />
          </Field>
          <Field label="Email">
            <Input value={userDraft.email ?? ""} onChange={(event) => setUserDraft({ ...userDraft, email: event.target.value })} />
          </Field>
          <Field label="Роль">
            <Select value={userDraft.role} onChange={(event) => setUserDraft({ ...userDraft, role: event.target.value as Role })}>
              <option value="manager">manager</option>
              <option value="admin">admin</option>
            </Select>
          </Field>
          <Field label="Пароль">
            <Input value={userDraft.password} onChange={(event) => setUserDraft({ ...userDraft, password: event.target.value })} minLength={8} required />
          </Field>
          <div className="flex items-end">
            <Button className="w-full" type="submit">
              <Plus size={16} />
              Создать
            </Button>
          </div>
        </form>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[980px] border-collapse text-sm">
            <thead className="bg-panel text-left text-xs uppercase text-muted">
              <tr>
                <th className="px-4 py-3">Имя</th>
                <th className="px-4 py-3">Логин</th>
                <th className="px-4 py-3">Email</th>
                <th className="px-4 py-3">Роль</th>
                <th className="px-4 py-3">Статус</th>
                <th className="px-4 py-3">Новый пароль</th>
                <th className="px-4 py-3">Действия</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.id} className="border-t border-line">
                  <td className="px-4 py-3 font-medium">{user.full_name}</td>
                  <td className="px-4 py-3">{user.username}</td>
                  <td className="px-4 py-3">{user.email ?? "-"}</td>
                  <td className="px-4 py-3">
                    <Select className="w-32" value={user.role} onChange={(event) => onUpdateUser(user.id, { role: event.target.value as Role })}>
                      <option value="manager">manager</option>
                      <option value="admin">admin</option>
                    </Select>
                  </td>
                  <td className="px-4 py-3">
                    <Badge tone={user.is_active ? "success" : "danger"}>{user.is_active ? "Активен" : "Заблокирован"}</Badge>
                  </td>
                  <td className="px-4 py-3">
                    <Input
                      className="w-40"
                      minLength={8}
                      placeholder="Новый пароль"
                      value={passwords[user.id] ?? ""}
                      onChange={(event) => setPasswords({ ...passwords, [user.id]: event.target.value })}
                    />
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex gap-2">
                      <GhostButton onClick={() => onUpdateUser(user.id, { is_active: !user.is_active })}>
                        {user.is_active ? "Блокировать" : "Активировать"}
                      </GhostButton>
                      <GhostButton
                        disabled={(passwords[user.id] ?? "").length < 8}
                        onClick={() => onResetPassword(user.id, passwords[user.id])}
                      >
                        <KeyRound size={16} />
                        Сбросить
                      </GhostButton>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>

      <div className="grid gap-5 lg:grid-cols-3">
        <DictionaryPanel
          icon={<CircleDot size={16} />}
          items={dictionaries.statuses}
          kind="statuses"
          title="Статусы"
          onCreate={onCreateDictionary}
          onUpdate={onUpdateDictionary}
        />
        <DictionaryPanel
          icon={<BookOpen size={16} />}
          items={dictionaries.courses}
          kind="courses"
          title="Курсы"
          onCreate={onCreateDictionary}
          onUpdate={onUpdateDictionary}
        />
        <DictionaryPanel
          icon={<Database size={16} />}
          items={dictionaries.sources}
          kind="sources"
          title="Источники"
          onCreate={onCreateDictionary}
          onUpdate={onUpdateDictionary}
        />
      </div>
    </div>
  );
}

function AdminMetric({ label, value, icon }: { label: string; value: number; icon: ReactNode }) {
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

function DictionaryPanel({
  icon,
  items,
  kind,
  title,
  onCreate,
  onUpdate
}: {
  icon: ReactNode;
  items: Array<DictionaryItem | Status>;
  kind: keyof Dictionaries;
  title: string;
  onCreate: (kind: keyof Dictionaries, payload: DictionaryInput | StatusInput) => Promise<void>;
  onUpdate: (kind: keyof Dictionaries, id: number, payload: Partial<DictionaryInput | StatusInput>) => Promise<void>;
}) {
  const isStatus = kind === "statuses";
  const [draft, setDraft] = useState<DictionaryInput | StatusInput>(
    isStatus
      ? { name: "", code: "", is_final: false, is_active: true, sort_order: 100 }
      : { name: "", is_active: true, sort_order: 100 }
  );

  async function create(event: FormEvent) {
    event.preventDefault();
    await onCreate(kind, draft);
    setDraft(isStatus ? { name: "", code: "", is_final: false, is_active: true, sort_order: 100 } : { name: "", is_active: true, sort_order: 100 });
  }

  return (
    <Panel className="overflow-hidden">
      <div className="flex items-center gap-2 border-b border-line px-4 py-3 text-sm font-semibold">
        {icon}
        {title}
      </div>
      <form className="grid gap-3 border-b border-line p-4" onSubmit={create}>
        <Field label="Название">
          <Input value={draft.name} onChange={(event) => setDraft({ ...draft, name: event.target.value })} required />
        </Field>
        {isStatus ? (
          <Field label="Код">
            <Input value={(draft as StatusInput).code} onChange={(event) => setDraft({ ...(draft as StatusInput), code: event.target.value })} required />
          </Field>
        ) : null}
        <div className="grid grid-cols-2 gap-3">
          <Field label="Порядок">
            <Input type="number" value={draft.sort_order} onChange={(event) => setDraft({ ...draft, sort_order: Number(event.target.value) })} />
          </Field>
          {isStatus ? (
            <label className="mt-5 inline-flex h-9 items-center gap-2 rounded-md border border-line bg-white px-3 text-sm">
              <input
                type="checkbox"
                checked={(draft as StatusInput).is_final}
                onChange={(event) => setDraft({ ...(draft as StatusInput), is_final: event.target.checked })}
              />
              Финальный
            </label>
          ) : null}
        </div>
        <Button type="submit">
          <Plus size={16} />
          Добавить
        </Button>
      </form>
      <div className="grid gap-2 p-4">
        {items.map((item) => (
          <div key={item.id} className="grid gap-2 rounded-md border border-line bg-panel px-3 py-2 text-sm">
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="font-medium">{item.name}</div>
                {"code" in item ? <div className="text-xs text-muted">{item.code}</div> : null}
              </div>
              <Badge tone={item.is_active ? "success" : "danger"}>{item.is_active ? "Активен" : "Архив"}</Badge>
            </div>
            <div className="flex items-center justify-between gap-2">
              <span className="text-xs text-muted">Порядок: {item.sort_order}</span>
              <GhostButton onClick={() => onUpdate(kind, item.id, { is_active: !item.is_active })}>
                {item.is_active ? "Архивировать" : "Активировать"}
              </GhostButton>
            </div>
          </div>
        ))}
      </div>
    </Panel>
  );
}
