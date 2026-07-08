import type { Dictionaries, ImportRow, Lead, User } from "./types";

const columns = [
  "customer_name",
  "contact",
  "status",
  "course",
  "source",
  "assigned_manager",
  "notes",
  "next_contact_date"
];

function escapeCell(value: unknown) {
  const text = String(value ?? "");
  if (/[",\n\r;]/.test(text)) {
    return `"${text.replace(/"/g, '""')}"`;
  }
  return text;
}

export function leadsToCsv(leads: Lead[]) {
  const rows = leads.map((lead) => [
    lead.customer_name,
    lead.contact,
    lead.status.name,
    lead.course?.name ?? "",
    lead.source?.name ?? "",
    lead.assigned_manager?.full_name ?? "",
    lead.notes ?? "",
    lead.next_contact_date ?? ""
  ]);
  return [columns.join(","), ...rows.map((row) => row.map(escapeCell).join(","))].join("\n");
}

export function downloadCsv(filename: string, csv: string) {
  const blob = new Blob([`\uFEFF${csv}`], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

export function parseCsv(text: string, dictionaries: Dictionaries, users: User[]): ImportRow[] {
  const lines = text.split(/\r?\n/).filter(Boolean);
  const header = lines.shift()?.split(",").map((item) => item.trim()) ?? [];

  return lines.map((line) => {
    const cells = line.split(",").map((item) => item.trim());
    const record = Object.fromEntries(header.map((key, index) => [key, cells[index] ?? ""]));
    const row: ImportRow = {
      customer_name: record.customer_name,
      contact: record.contact,
      status: record.status,
      course: record.course,
      source: record.source,
      assigned_manager: record.assigned_manager,
      notes: record.notes,
      next_contact_date: record.next_contact_date,
      errors: []
    };

    if (!row.customer_name) row.errors.push("Нет имени");
    if (!row.contact) row.errors.push("Нет контакта");
    if (!dictionaries.statuses.some((item) => item.name === row.status || item.code === row.status)) row.errors.push("Статус не найден");
    if (row.course && !dictionaries.courses.some((item) => item.name === row.course)) row.errors.push("Курс не найден");
    if (row.source && !dictionaries.sources.some((item) => item.name === row.source)) row.errors.push("Источник не найден");
    if (row.assigned_manager && !users.some((item) => item.full_name === row.assigned_manager || item.username === row.assigned_manager)) {
      row.errors.push("Менеджер не найден");
    }

    return row;
  });
}

export { columns as csvColumns };
