"use client";

import { ChangeEvent, useState } from "react";
import { Download, Upload } from "lucide-react";
import { downloadCsv, leadsToCsv, parseCsv } from "@/lib/csv";
import type { Dictionaries, ImportRow, Lead, LeadInput, User } from "@/lib/types";
import { Badge, Button, GhostButton, Panel } from "./ui";

type Props = {
  canImport: boolean;
  dictionaries: Dictionaries;
  leads: Lead[];
  users: User[];
  onCreate: (payload: LeadInput) => Promise<void>;
};

export function ImportExportView({ canImport, dictionaries, leads, users, onCreate }: Props) {
  const [rows, setRows] = useState<ImportRow[]>([]);
  const [importing, setImporting] = useState(false);
  const validRows = rows.filter((row) => row.errors.length === 0);

  async function readFile(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    const text = await file.text();
    setRows(parseCsv(text, dictionaries, users));
  }

  async function importRows() {
    setImporting(true);
    try {
      for (const row of validRows) {
        await onCreate({
          customer_name: row.customer_name,
          contact: row.contact,
          notes: row.notes ?? null,
          next_contact_date: row.next_contact_date || null,
          status_id: dictionaries.statuses.find((item) => item.name === row.status || item.code === row.status)?.id ?? dictionaries.statuses[0].id,
          course_id: dictionaries.courses.find((item) => item.name === row.course)?.id ?? null,
          source_id: dictionaries.sources.find((item) => item.name === row.source)?.id ?? null,
          assigned_manager_id: users.find((item) => item.full_name === row.assigned_manager || item.username === row.assigned_manager)?.id ?? null
        });
      }
      setRows([]);
    } finally {
      setImporting(false);
    }
  }

  return (
    <div className="grid gap-5">
      <div className="grid gap-5 lg:grid-cols-2">
        <Panel className="p-4">
          <div className="mb-3 flex items-center gap-2 text-sm font-semibold">
            <Download size={16} />
            Экспорт
          </div>
          <div className="mb-4 grid grid-cols-3 gap-3">
            <Metric label="Строк" value={leads.length} />
            <Metric label="Активных" value={leads.filter((lead) => !lead.deleted_at).length} />
            <Metric label="Архив" value={leads.filter((lead) => lead.deleted_at).length} />
          </div>
          <Button onClick={() => downloadCsv(`crm-leads-${new Date().toISOString().slice(0, 10)}.csv`, leadsToCsv(leads))}>
            <Download size={16} />
            Скачать CSV
          </Button>
        </Panel>

        <Panel className="p-4">
          <div className="mb-3 flex items-center gap-2 text-sm font-semibold">
            <Upload size={16} />
            Импорт
          </div>
          <label className="flex min-h-28 cursor-pointer items-center justify-center rounded-lg border border-dashed border-line bg-panel px-4 text-center text-sm text-muted">
            <input className="sr-only" type="file" accept=".csv,text/csv" disabled={!canImport} onChange={readFile} />
            {canImport ? "Выберите CSV-файл" : "Импорт доступен администратору"}
          </label>
        </Panel>
      </div>

      {rows.length ? (
        <Panel className="overflow-hidden">
          <div className="flex items-center justify-between border-b border-line px-4 py-3">
            <div className="text-sm font-semibold">Предпросмотр</div>
            <div className="flex items-center gap-2">
              <Badge tone={validRows.length === rows.length ? "success" : "warning"}>{validRows.length}/{rows.length}</Badge>
              <GhostButton disabled={!canImport || importing || validRows.length === 0} onClick={importRows}>
                <Upload size={16} />
                Импортировать
              </GhostButton>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[900px] border-collapse text-sm">
              <thead className="bg-panel text-left text-xs uppercase text-muted">
                <tr>
                  <th className="px-4 py-3">Клиент</th>
                  <th className="px-4 py-3">Контакт</th>
                  <th className="px-4 py-3">Статус</th>
                  <th className="px-4 py-3">Курс</th>
                  <th className="px-4 py-3">Источник</th>
                  <th className="px-4 py-3">Менеджер</th>
                  <th className="px-4 py-3">Ошибки</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row, index) => (
                  <tr key={`${row.customer_name}-${index}`} className="border-t border-line">
                    <td className="px-4 py-3 font-medium">{row.customer_name}</td>
                    <td className="px-4 py-3">{row.contact}</td>
                    <td className="px-4 py-3">{row.status}</td>
                    <td className="px-4 py-3">{row.course}</td>
                    <td className="px-4 py-3">{row.source}</td>
                    <td className="px-4 py-3">{row.assigned_manager}</td>
                    <td className="px-4 py-3">
                      {row.errors.length ? <Badge tone="danger">{row.errors.join(", ")}</Badge> : <Badge tone="success">OK</Badge>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>
      ) : null}
    </div>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-md border border-line bg-panel px-3 py-2">
      <div className="text-xs text-muted">{label}</div>
      <div className="text-lg font-semibold">{value}</div>
    </div>
  );
}
