"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { MessageSquare, Plus, Save, Search, Trash2 } from "lucide-react";
import { isOverdue } from "@/lib/analytics";
import type { Dictionaries, Lead, LeadFilters, LeadInput, User } from "@/lib/types";
import { Badge, Button, Field, GhostButton, IconButton, Input, Panel, Select, Textarea } from "./ui";

type Props = {
  canDelete: boolean;
  dictionaries: Dictionaries;
  filters: LeadFilters;
  leads: Lead[];
  loading: boolean;
  users: User[];
  onAddComment: (leadId: number, body: string) => Promise<void>;
  onCreate: (payload: LeadInput) => Promise<void>;
  onDelete: (id: number) => Promise<void>;
  onFilter: (filters: LeadFilters) => Promise<void>;
  onUpdate: (id: number, payload: Partial<LeadInput>) => Promise<void>;
};

const blankLead: LeadInput = {
  customer_name: "",
  contact: "",
  notes: "",
  status_id: 1,
  course_id: null,
  source_id: null,
  assigned_manager_id: null,
  next_contact_date: ""
};

export function LeadsView({ canDelete, dictionaries, filters, leads, loading, users, onAddComment, onCreate, onDelete, onFilter, onUpdate }: Props) {
  const [draft, setDraft] = useState<LeadInput>({ ...blankLead, status_id: dictionaries.statuses[0]?.id ?? 1 });
  const [selectedId, setSelectedId] = useState<number | null>(leads[0]?.id ?? null);
  const [comment, setComment] = useState("");
  const selected = useMemo(() => leads.find((lead) => lead.id === selectedId) ?? leads[0], [leads, selectedId]);

  async function create(event: FormEvent) {
    event.preventDefault();
    await onCreate(normalizeLead(draft));
    setDraft({ ...blankLead, status_id: dictionaries.statuses[0]?.id ?? 1 });
  }

  async function submitComment(event: FormEvent) {
    event.preventDefault();
    if (!selected || !comment.trim()) return;
    await onAddComment(selected.id, comment.trim());
    setComment("");
  }

  return (
    <div className="grid items-start gap-5 xl:grid-cols-[minmax(0,1fr)_420px]">
      <div className="grid auto-rows-max content-start gap-5">
        <Panel className="p-4">
          <div className="grid gap-3 md:grid-cols-6">
            <Field label="Поиск">
              <div className="relative">
                <Search className="pointer-events-none absolute left-3 top-2.5 text-muted" size={15} />
                <Input className="w-full pl-9" value={filters.search ?? ""} onChange={(event) => onFilter({ ...filters, search: event.target.value })} />
              </div>
            </Field>
            <Field label="Статус">
              <Select value={filters.status_id ?? ""} onChange={(event) => onFilter({ ...filters, status_id: event.target.value ? Number(event.target.value) : "" })}>
                <option value="">Все</option>
                {dictionaries.statuses.map((status) => <option key={status.id} value={status.id}>{status.name}</option>)}
              </Select>
            </Field>
            <Field label="Курс">
              <Select value={filters.course_id ?? ""} onChange={(event) => onFilter({ ...filters, course_id: event.target.value ? Number(event.target.value) : "" })}>
                <option value="">Все</option>
                {dictionaries.courses.map((course) => <option key={course.id} value={course.id}>{course.name}</option>)}
              </Select>
            </Field>
            <Field label="Источник">
              <Select value={filters.source_id ?? ""} onChange={(event) => onFilter({ ...filters, source_id: event.target.value ? Number(event.target.value) : "" })}>
                <option value="">Все</option>
                {dictionaries.sources.map((source) => <option key={source.id} value={source.id}>{source.name}</option>)}
              </Select>
            </Field>
            <Field label="Менеджер">
              <Select value={filters.assigned_manager_id ?? ""} onChange={(event) => onFilter({ ...filters, assigned_manager_id: event.target.value ? Number(event.target.value) : "" })}>
                <option value="">Все</option>
                {users.filter((user) => user.role === "manager").map((user) => <option key={user.id} value={user.id}>{user.full_name}</option>)}
              </Select>
            </Field>
            <label className="mt-5 inline-flex h-9 items-center gap-2 rounded-md border border-line bg-white px-3 text-sm">
              <input type="checkbox" checked={Boolean(filters.overdue)} onChange={(event) => onFilter({ ...filters, overdue: event.target.checked })} />
              Просрочки
            </label>
          </div>
        </Panel>

        <Panel className="overflow-hidden">
          <div className="flex items-center justify-between border-b border-line px-4 py-3">
            <div className="text-sm font-semibold">Заявки</div>
            <Badge>{loading ? "Загрузка" : leads.length}</Badge>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[920px] border-collapse text-sm">
              <thead className="bg-panel text-left text-xs uppercase text-muted">
                <tr>
                  <th className="px-4 py-3">Клиент</th>
                  <th className="px-4 py-3">Статус</th>
                  <th className="px-4 py-3">Курс</th>
                  <th className="px-4 py-3">Источник</th>
                  <th className="px-4 py-3">Менеджер</th>
                  <th className="px-4 py-3">Контакт</th>
                  <th className="px-4 py-3">Следующий контакт</th>
                </tr>
              </thead>
              <tbody>
                {leads.map((lead) => (
                  <tr
                    key={lead.id}
                    className={`cursor-pointer border-t border-line hover:bg-panel ${selected?.id === lead.id ? "bg-blue-50" : ""}`}
                    onClick={() => setSelectedId(lead.id)}
                  >
                    <td className="px-4 py-3 font-medium">{lead.customer_name}</td>
                    <td className="px-4 py-3"><Badge tone={lead.status.is_final ? "success" : "neutral"}>{lead.status.name}</Badge></td>
                    <td className="px-4 py-3">{lead.course?.name ?? "-"}</td>
                    <td className="px-4 py-3">{lead.source?.name ?? "-"}</td>
                    <td className="px-4 py-3">{lead.assigned_manager?.full_name ?? "-"}</td>
                    <td className="px-4 py-3">{lead.contact}</td>
                    <td className="px-4 py-3">
                      {lead.next_contact_date ? <Badge tone={isOverdue(lead) ? "danger" : "warning"}>{lead.next_contact_date}</Badge> : "-"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>
      </div>

      <div className="grid content-start gap-5">
        <Panel className="p-4">
          <div className="mb-3 flex items-center gap-2 text-sm font-semibold">
            <Plus size={16} />
            Новая заявка
          </div>
          <LeadForm
            dictionaries={dictionaries}
            lead={draft}
            users={users}
            onChange={setDraft}
            onSubmit={create}
            submitLabel="Создать"
          />
        </Panel>

        {selected ? (
          <Panel className="p-4">
            <LeadEditor
              canDelete={canDelete}
              dictionaries={dictionaries}
              lead={selected}
              users={users}
              onDelete={onDelete}
              onUpdate={onUpdate}
            />
            <div className="mt-5 border-t border-line pt-4">
              <div className="mb-3 flex items-center gap-2 text-sm font-semibold">
                <MessageSquare size={16} />
                Комментарии
              </div>
              <div className="grid max-h-44 gap-2 overflow-auto">
                {(selected.comments ?? []).map((item) => (
                  <div key={item.id} className="rounded-md bg-panel px-3 py-2 text-sm">
                    <div>{item.body}</div>
                    <div className="mt-1 text-xs text-muted">{new Date(item.created_at).toLocaleString("ru-RU")}</div>
                  </div>
                ))}
              </div>
              <form className="mt-3 grid gap-2" onSubmit={submitComment}>
                <Textarea value={comment} onChange={(event) => setComment(event.target.value)} placeholder="Комментарий" />
                <GhostButton type="submit">
                  <Save size={16} />
                  Добавить
                </GhostButton>
              </form>
            </div>
          </Panel>
        ) : null}
      </div>
    </div>
  );
}

function LeadEditor({
  canDelete,
  dictionaries,
  lead,
  users,
  onDelete,
  onUpdate
}: {
  canDelete: boolean;
  dictionaries: Dictionaries;
  lead: Lead;
  users: User[];
  onDelete: (id: number) => Promise<void>;
  onUpdate: (id: number, payload: Partial<LeadInput>) => Promise<void>;
}) {
  const [edit, setEdit] = useState<LeadInput>(leadToInput(lead));

  useEffect(() => {
    setEdit(leadToInput(lead));
  }, [lead]);

  async function save(event: FormEvent) {
    event.preventDefault();
    await onUpdate(lead.id, normalizeLead(edit));
  }

  return (
    <>
      <div className="mb-3 flex items-center justify-between gap-3">
        <div className="text-sm font-semibold">Карточка #{lead.id}</div>
        {canDelete ? (
          <IconButton label="Архивировать" onClick={() => onDelete(lead.id)}>
            <Trash2 size={16} />
          </IconButton>
        ) : null}
      </div>
      <LeadForm
        dictionaries={dictionaries}
        lead={edit}
        users={users}
        onChange={setEdit}
        onSubmit={save}
        submitLabel="Сохранить"
      />
    </>
  );
}

function LeadForm({
  dictionaries,
  lead,
  users,
  onChange,
  onSubmit,
  submitLabel
}: {
  dictionaries: Dictionaries;
  lead: LeadInput;
  users: User[];
  onChange: (lead: LeadInput) => void;
  onSubmit: (event: FormEvent) => void;
  submitLabel: string;
}) {
  const update = (patch: Partial<LeadInput>) => onChange({ ...lead, ...patch });
  return (
    <form className="grid gap-3" onSubmit={onSubmit}>
      <Field label="Клиент">
        <Input value={lead.customer_name} onChange={(event) => update({ customer_name: event.target.value })} required />
      </Field>
      <Field label="Контакт">
        <Input value={lead.contact} onChange={(event) => update({ contact: event.target.value })} required />
      </Field>
      <div className="grid gap-3 md:grid-cols-2">
        <Field label="Статус">
          <Select value={lead.status_id} onChange={(event) => update({ status_id: Number(event.target.value) })}>
            {dictionaries.statuses.map((status) => <option key={status.id} value={status.id}>{status.name}</option>)}
          </Select>
        </Field>
        <Field label="Менеджер">
          <Select value={lead.assigned_manager_id ?? ""} onChange={(event) => update({ assigned_manager_id: event.target.value ? Number(event.target.value) : null })}>
            <option value="">Не назначен</option>
            {users.filter((user) => user.role === "manager").map((user) => <option key={user.id} value={user.id}>{user.full_name}</option>)}
          </Select>
        </Field>
        <Field label="Курс">
          <Select value={lead.course_id ?? ""} onChange={(event) => update({ course_id: event.target.value ? Number(event.target.value) : null })}>
            <option value="">Не выбран</option>
            {dictionaries.courses.map((course) => <option key={course.id} value={course.id}>{course.name}</option>)}
          </Select>
        </Field>
        <Field label="Источник">
          <Select value={lead.source_id ?? ""} onChange={(event) => update({ source_id: event.target.value ? Number(event.target.value) : null })}>
            <option value="">Не выбран</option>
            {dictionaries.sources.map((source) => <option key={source.id} value={source.id}>{source.name}</option>)}
          </Select>
        </Field>
      </div>
      <Field label="Следующий контакт">
        <Input type="date" value={lead.next_contact_date ?? ""} onChange={(event) => update({ next_contact_date: event.target.value })} />
      </Field>
      <Field label="Заметки">
        <Textarea value={lead.notes ?? ""} onChange={(event) => update({ notes: event.target.value })} />
      </Field>
      <Button type="submit">
        <Save size={16} />
        {submitLabel}
      </Button>
    </form>
  );
}

function normalizeLead(lead: LeadInput): LeadInput {
  return {
    customer_name: lead.customer_name,
    contact: lead.contact,
    notes: lead.notes || null,
    course_id: lead.course_id || null,
    source_id: lead.source_id || null,
    status_id: Number(lead.status_id),
    assigned_manager_id: lead.assigned_manager_id || null,
    next_contact_date: lead.next_contact_date || null
  };
}

function leadToInput(lead: Lead): LeadInput {
  return {
    customer_name: lead.customer_name,
    contact: lead.contact,
    notes: lead.notes ?? "",
    course_id: lead.course_id ?? null,
    source_id: lead.source_id ?? null,
    status_id: lead.status_id,
    assigned_manager_id: lead.assigned_manager_id ?? null,
    next_contact_date: lead.next_contact_date ?? ""
  };
}
