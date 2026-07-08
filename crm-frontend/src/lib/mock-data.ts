import type { Comment, Dictionaries, Lead, LeadFilters, LeadInput, User } from "./types";

const now = new Date("2026-07-08T12:00:00.000Z").toISOString();

export const mockUsers: User[] = [
  {
    id: 1,
    username: "admin",
    email: "admin@school.local",
    full_name: "Анна Орлова",
    role: "admin",
    is_active: true,
    created_at: now,
    updated_at: now
  },
  {
    id: 2,
    username: "manager",
    email: "manager@school.local",
    full_name: "Илья Морозов",
    role: "manager",
    is_active: true,
    created_at: now,
    updated_at: now
  },
  {
    id: 3,
    username: "sales",
    email: "sales@school.local",
    full_name: "Мария Ким",
    role: "manager",
    is_active: true,
    created_at: now,
    updated_at: now
  },
  {
    id: 4,
    username: "blocked",
    email: "blocked@school.local",
    full_name: "Олег Серов",
    role: "manager",
    is_active: false,
    created_at: now,
    updated_at: now
  }
];

export const mockDictionaries: Dictionaries = {
  statuses: [
    { id: 1, name: "Новая", code: "new", is_final: false, is_active: true, sort_order: 10, created_at: now, updated_at: now },
    { id: 2, name: "В работе", code: "in_progress", is_final: false, is_active: true, sort_order: 20, created_at: now, updated_at: now },
    { id: 3, name: "Демо назначено", code: "demo", is_final: false, is_active: true, sort_order: 30, created_at: now, updated_at: now },
    { id: 4, name: "Оплата", code: "payment", is_final: false, is_active: true, sort_order: 40, created_at: now, updated_at: now },
    { id: 5, name: "Успешно", code: "won", is_final: true, is_active: true, sort_order: 50, created_at: now, updated_at: now },
    { id: 6, name: "Отказ", code: "lost", is_final: true, is_active: true, sort_order: 60, created_at: now, updated_at: now }
  ],
  courses: [
    { id: 1, name: "Python Start", is_active: true, sort_order: 10, created_at: now, updated_at: now },
    { id: 2, name: "Frontend Pro", is_active: true, sort_order: 20, created_at: now, updated_at: now },
    { id: 3, name: "Data Analytics", is_active: true, sort_order: 30, created_at: now, updated_at: now },
    { id: 4, name: "Product Design", is_active: true, sort_order: 40, created_at: now, updated_at: now }
  ],
  sources: [
    { id: 1, name: "Сайт", is_active: true, sort_order: 10, created_at: now, updated_at: now },
    { id: 2, name: "VK Ads", is_active: true, sort_order: 20, created_at: now, updated_at: now },
    { id: 3, name: "Рекомендация", is_active: true, sort_order: 30, created_at: now, updated_at: now },
    { id: 4, name: "Вебинар", is_active: true, sort_order: 40, created_at: now, updated_at: now }
  ]
};

const leadSeeds: Array<Omit<LeadInput, "status_id"> & { status_id: number; created_at: string }> = [
  ["Екатерина Лебедева", "+7 900 101-20-01", 1, 1, 1, 2, "Хочет утреннюю группу", "2026-07-09"],
  ["Алексей Романов", "+7 900 101-20-02", 2, 2, 2, 2, "Нужно согласовать рассрочку", "2026-07-07"],
  ["Дина Ахметова", "+7 900 101-20-03", 3, 3, 4, 3, "Демо в пятницу", "2026-07-10"],
  ["Павел Сокол", "+7 900 101-20-04", 4, 1, 3, 3, "Ждет счет", "2026-07-08"],
  ["Наталья Фомина", "+7 900 101-20-05", 5, 2, 1, 2, "Оплатила полный курс", null],
  ["Роман Белов", "+7 900 101-20-06", 6, 4, 2, 3, "Выбрал другой центр", null],
  ["Светлана Власова", "+7 900 101-20-07", 1, 3, 1, 2, "Просила перезвонить вечером", "2026-07-06"],
  ["Георгий Волков", "+7 900 101-20-08", 2, 1, 4, 3, "Интересует корпоративный формат", "2026-07-11"],
  ["Юлия Никитина", "+7 900 101-20-09", 3, 2, 3, 2, "Подтвердить демо", "2026-07-09"],
  ["Тимур Громов", "+7 900 101-20-10", 4, 3, 2, 3, "Счет отправлен", "2026-07-08"],
  ["Ольга Захарова", "+7 900 101-20-11", 5, 4, 4, 2, "Пакет Pro", null],
  ["Виктория Ершова", "+7 900 101-20-12", 2, 2, 1, 3, "Сравнивает курсы", "2026-07-05"]
].map((row, index) => ({
  customer_name: row[0] as string,
  contact: row[1] as string,
  status_id: row[2] as number,
  course_id: row[3] as number,
  source_id: row[4] as number,
  assigned_manager_id: row[5] as number,
  notes: row[6] as string,
  next_contact_date: row[7] as string | null,
  created_at: new Date(Date.UTC(2026, 5, 24 + index)).toISOString()
}));

let mockLeads: Lead[] = leadSeeds.map((lead, index) => hydrateLead({
  id: index + 1,
  ...lead,
  created_by_id: 1,
  deleted_at: null,
  updated_at: lead.created_at,
  comments: [
    {
      id: index + 1,
      lead_id: index + 1,
      author_id: lead.assigned_manager_id ?? 1,
      body: index % 3 === 0 ? "Системное событие: статус обновлен" : "Первичный контакт зафиксирован",
      created_at: lead.created_at
    }
  ]
}));

function hydrateLead(lead: Omit<Lead, "status"> & { status?: Lead["status"] }): Lead {
  const status = mockDictionaries.statuses.find((item) => item.id === lead.status_id) ?? mockDictionaries.statuses[0];
  return {
    ...lead,
    status,
    course: mockDictionaries.courses.find((item) => item.id === lead.course_id) ?? null,
    source: mockDictionaries.sources.find((item) => item.id === lead.source_id) ?? null,
    assigned_manager: mockUsers.find((item) => item.id === lead.assigned_manager_id) ?? null,
    created_by: mockUsers.find((item) => item.id === lead.created_by_id) ?? null
  };
}

function canSeeLead(user: User, lead: Lead) {
  return user.role === "admin" || lead.assigned_manager_id === user.id;
}

export function mockLogin(username: string, password: string) {
  const user = mockUsers.find((item) => item.username === username && item.is_active);
  if (!user || password.length < 1) {
    throw new Error("Неверный логин или пароль");
  }
  return { token: `mock-token-${user.id}`, user, mode: "mock" as const };
}

export function mockGetDictionaries() {
  return structuredClone(mockDictionaries);
}

export function mockGetUsers() {
  return structuredClone(mockUsers);
}

export function mockListLeads(user: User, filters: LeadFilters = {}) {
  const search = filters.search?.trim().toLowerCase();
  const today = new Date("2026-07-08T00:00:00.000Z");
  const items = mockLeads
    .filter((lead) => canSeeLead(user, lead))
    .filter((lead) => filters.include_archived || !lead.deleted_at)
    .filter((lead) => !filters.status_id || lead.status_id === Number(filters.status_id))
    .filter((lead) => !filters.course_id || lead.course_id === Number(filters.course_id))
    .filter((lead) => !filters.source_id || lead.source_id === Number(filters.source_id))
    .filter((lead) => !filters.assigned_manager_id || lead.assigned_manager_id === Number(filters.assigned_manager_id))
    .filter((lead) => {
      if (!filters.overdue) return true;
      return Boolean(lead.next_contact_date && new Date(lead.next_contact_date) < today && !lead.status.is_final);
    })
    .filter((lead) => {
      if (!search) return true;
      return `${lead.customer_name} ${lead.contact} ${lead.notes ?? ""}`.toLowerCase().includes(search);
    })
    .sort((a, b) => b.updated_at.localeCompare(a.updated_at));

  return { items: structuredClone(items), total: items.length, skip: 0, limit: 200 };
}

export function mockCreateLead(user: User, payload: LeadInput) {
  const created = hydrateLead({
    id: Math.max(...mockLeads.map((item) => item.id)) + 1,
    ...payload,
    created_by_id: user.id,
    deleted_at: null,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    comments: []
  });
  mockLeads = [created, ...mockLeads];
  return structuredClone(created);
}

export function mockUpdateLead(id: number, payload: Partial<LeadInput>) {
  const index = mockLeads.findIndex((item) => item.id === id);
  if (index < 0) throw new Error("Заявка не найдена");
  mockLeads[index] = hydrateLead({ ...mockLeads[index], ...payload, updated_at: new Date().toISOString() });
  return structuredClone(mockLeads[index]);
}

export function mockDeleteLead(id: number) {
  mockLeads = mockLeads.map((lead) => lead.id === id ? { ...lead, deleted_at: new Date().toISOString() } : lead);
}

export function mockAddComment(user: User, leadId: number, body: string) {
  const lead = mockLeads.find((item) => item.id === leadId);
  if (!lead) throw new Error("Заявка не найдена");
  const comment: Comment = {
    id: Date.now(),
    lead_id: leadId,
    author_id: user.id,
    body,
    created_at: new Date().toISOString()
  };
  lead.comments = [...(lead.comments ?? []), comment];
  lead.updated_at = comment.created_at;
  return structuredClone(comment);
}
