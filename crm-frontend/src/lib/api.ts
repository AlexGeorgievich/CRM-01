import {
  mockAddComment,
  mockCreateLead,
  mockDeleteLead,
  mockGetDictionaries,
  mockGetUsers,
  mockListLeads,
  mockLogin,
  mockUpdateLead
} from "./mock-data";
import type { Dictionaries, Lead, LeadFilters, LeadInput, LeadList, Session, User } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8001/api/v1";
const USE_MOCKS = process.env.NEXT_PUBLIC_USE_MOCKS !== "false";

async function request<T>(path: string, token: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...(init.headers ?? {})
    }
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail ?? "Ошибка запроса");
  }

  return response.json();
}

function filterParams(filters: LeadFilters) {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== "" && typeof value !== "boolean") {
      params.set(key, String(value));
    }
  });
  params.set("limit", "200");
  return params.toString();
}

export async function login(username: string, password: string): Promise<Session> {
  if (USE_MOCKS) return mockLogin(username, password);

  const form = new URLSearchParams();
  form.set("username", username);
  form.set("password", password);

  const tokenResponse = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: form
  });
  if (!tokenResponse.ok) throw new Error("Неверный логин или пароль");
  const token = await tokenResponse.json();
  const user = await request<User>("/auth/me", token.access_token);
  return { token: token.access_token, user, mode: "api" };
}

export async function loadDictionaries(session: Session): Promise<Dictionaries> {
  if (session.mode === "mock") return mockGetDictionaries();
  const [statuses, courses, sources] = await Promise.all([
    request<Dictionaries["statuses"]>("/dictionaries/statuses", session.token),
    request<Dictionaries["courses"]>("/dictionaries/courses", session.token),
    request<Dictionaries["sources"]>("/dictionaries/sources", session.token)
  ]);
  return { statuses, courses, sources };
}

export async function loadUsers(session: Session) {
  if (session.mode === "mock") return mockGetUsers();
  if (session.user.role !== "admin") return [session.user];
  return request<User[]>("/users", session.token);
}

export async function loadLeads(session: Session, filters: LeadFilters = {}): Promise<LeadList> {
  if (session.mode === "mock") return mockListLeads(session.user, filters);
  return request<LeadList>(`/leads?${filterParams(filters)}`, session.token);
}

export async function createLead(session: Session, payload: LeadInput): Promise<Lead> {
  if (session.mode === "mock") return mockCreateLead(session.user, payload);
  return request<Lead>("/leads", session.token, { method: "POST", body: JSON.stringify(payload) });
}

export async function updateLead(session: Session, id: number, payload: Partial<LeadInput>): Promise<Lead> {
  if (session.mode === "mock") return mockUpdateLead(id, payload);
  return request<Lead>(`/leads/${id}`, session.token, { method: "PATCH", body: JSON.stringify(payload) });
}

export async function deleteLead(session: Session, id: number) {
  if (session.mode === "mock") return mockDeleteLead(id);
  return request(`/leads/${id}`, session.token, { method: "DELETE" });
}

export async function addComment(session: Session, leadId: number, body: string) {
  if (session.mode === "mock") return mockAddComment(session.user, leadId, body);
  return request(`/leads/${leadId}/comments`, session.token, { method: "POST", body: JSON.stringify({ body }) });
}
