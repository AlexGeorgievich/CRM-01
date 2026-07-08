"use client";

import { useEffect, useMemo, useState } from "react";
import { BarChart3, Download, LayoutDashboard, LogOut, Settings, Upload, Users } from "lucide-react";
import { addComment, createDictionaryItem, createLead, createUser, deleteLead, loadDictionaries, loadLeads, loadUsers, login, resetPassword, updateDictionaryItem, updateLead, updateUser } from "@/lib/api";
import { buildAnalytics } from "@/lib/analytics";
import { can } from "@/lib/permissions";
import type { Dictionaries, DictionaryInput, Lead, LeadFilters, LeadInput, Session, StatusInput, User, UserCreateInput, UserUpdateInput } from "@/lib/types";
import { LoginCard } from "./login-card";
import { DashboardView } from "./dashboard-view";
import { LeadsView } from "./leads-view";
import { AdminView } from "./admin-view";
import { ImportExportView } from "./import-export-view";
import { Badge, GhostButton } from "./ui";

type View = "dashboard" | "leads" | "import" | "admin";

export function AppShell() {
  const [session, setSession] = useState<Session | null>(null);
  const [view, setView] = useState<View>("dashboard");
  const [leads, setLeads] = useState<Lead[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [dictionaries, setDictionaries] = useState<Dictionaries | null>(null);
  const [filters, setFilters] = useState<LeadFilters>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const analytics = useMemo(() => {
    if (!dictionaries) return null;
    return buildAnalytics(leads, dictionaries, users);
  }, [dictionaries, leads, users]);

  async function refresh(nextFilters = filters) {
    if (!session) return;
    setLoading(true);
    setError("");
    try {
      const [nextDictionaries, nextUsers, nextLeads] = await Promise.all([
        loadDictionaries(session),
        loadUsers(session),
        loadLeads(session, nextFilters)
      ]);
      setDictionaries(nextDictionaries);
      setUsers(nextUsers);
      setLeads(nextLeads.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка загрузки данных");
    } finally {
      setLoading(false);
    }
  }

  async function handleLogin(username: string, password: string) {
    const nextSession = await login(username, password);
    setSession(nextSession);
  }

  useEffect(() => {
    if (session) void refresh({});
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [session]);

  async function handleCreate(payload: LeadInput) {
    if (!session) return;
    await createLead(session, payload);
    await refresh();
  }

  async function handleUpdate(id: number, payload: Partial<LeadInput>) {
    if (!session) return;
    await updateLead(session, id, payload);
    await refresh();
  }

  async function handleDelete(id: number) {
    if (!session || !can(session.user.role, "leads:delete")) return;
    await deleteLead(session, id);
    await refresh();
  }

  async function handleComment(leadId: number, body: string) {
    if (!session) return;
    await addComment(session, leadId, body);
    await refresh();
  }

  async function handleFilter(nextFilters: LeadFilters) {
    setFilters(nextFilters);
    await refresh(nextFilters);
  }

  async function handleCreateUser(payload: UserCreateInput) {
    if (!session) return;
    await createUser(session, payload);
    await refresh();
  }

  async function handleUpdateUser(id: number, payload: UserUpdateInput) {
    if (!session) return;
    await updateUser(session, id, payload);
    await refresh();
  }

  async function handleResetPassword(id: number, password: string) {
    if (!session) return;
    await resetPassword(session, id, password);
    await refresh();
  }

  async function handleCreateDictionary(kind: keyof Dictionaries, payload: DictionaryInput | StatusInput) {
    if (!session) return;
    await createDictionaryItem(session, kind, payload);
    await refresh();
  }

  async function handleUpdateDictionary(kind: keyof Dictionaries, id: number, payload: Partial<DictionaryInput | StatusInput>) {
    if (!session) return;
    await updateDictionaryItem(session, kind, id, payload);
    await refresh();
  }

  if (!session) return <LoginCard onLogin={handleLogin} />;
  if (!dictionaries) {
    return <div className="grid min-h-screen place-items-center bg-panel text-sm text-muted">Загрузка</div>;
  }

  const navigation = [
    { id: "dashboard" as const, label: "Дашборд", icon: LayoutDashboard, permission: "analytics:view" },
    { id: "leads" as const, label: "Заявки", icon: Users, permission: "leads:view" },
    { id: "import" as const, label: "CSV", icon: Upload, permission: "csv:export" },
    { id: "admin" as const, label: "Администрирование", icon: Settings, permission: "admin:view" }
  ].filter((item) => can(session.user.role, item.permission));

  return (
    <div className="min-h-screen bg-panel">
      <aside className="fixed inset-y-0 left-0 z-20 hidden w-64 border-r border-line bg-white px-4 py-5 lg:block">
        <div className="mb-6 px-2">
          <div className="text-lg font-semibold">CRM</div>
          <div className="mt-1 flex items-center gap-2">
            <Badge tone={session.mode === "mock" ? "warning" : "success"}>{session.mode === "mock" ? "Mock" : "API"}</Badge>
            <span className="text-xs text-muted">{session.user.role}</span>
          </div>
        </div>
        <nav className="grid gap-1">
          {navigation.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                className={`flex h-10 items-center gap-3 rounded-md px-3 text-sm font-medium ${view === item.id ? "bg-ink text-white" : "text-ink hover:bg-panel"}`}
                onClick={() => setView(item.id)}
              >
                <Icon size={16} />
                {item.label}
              </button>
            );
          })}
        </nav>
      </aside>

      <div className="lg:pl-64">
        <header className="sticky top-0 z-10 flex min-h-16 items-center justify-between border-b border-line bg-white px-4 lg:px-8">
          <div>
            <div className="text-sm text-muted">{session.user.full_name}</div>
            <h1 className="text-xl font-semibold text-ink">
              {view === "dashboard" && "Дашборд"}
              {view === "leads" && "Заявки"}
              {view === "import" && "CSV"}
              {view === "admin" && "Администрирование"}
            </h1>
          </div>
          <div className="flex items-center gap-2">
            <GhostButton onClick={() => setView("import")} disabled={!can(session.user.role, "csv:export")}>
              <Download size={16} />
              CSV
            </GhostButton>
            <GhostButton onClick={() => setSession(null)}>
              <LogOut size={16} />
              Выйти
            </GhostButton>
          </div>
        </header>

        <main className="px-4 py-5 lg:px-8">
          {error ? <div className="mb-4 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-danger">{error}</div> : null}
          {view === "dashboard" && analytics ? <DashboardView analytics={analytics} loading={loading} /> : null}
          {view === "leads" ? (
            <LeadsView
              canDelete={can(session.user.role, "leads:delete")}
              dictionaries={dictionaries}
              filters={filters}
              leads={leads}
              loading={loading}
              users={users}
              onAddComment={handleComment}
              onCreate={handleCreate}
              onDelete={handleDelete}
              onFilter={handleFilter}
              onUpdate={handleUpdate}
            />
          ) : null}
          {view === "import" ? (
            <ImportExportView
              canImport={can(session.user.role, "csv:import")}
              dictionaries={dictionaries}
              leads={leads}
              users={users}
              onCreate={handleCreate}
            />
          ) : null}
          {view === "admin" && can(session.user.role, "admin:view") ? (
            <AdminView
              dictionaries={dictionaries}
              users={users}
              onCreateDictionary={handleCreateDictionary}
              onCreateUser={handleCreateUser}
              onResetPassword={handleResetPassword}
              onUpdateDictionary={handleUpdateDictionary}
              onUpdateUser={handleUpdateUser}
            />
          ) : null}
        </main>
      </div>
    </div>
  );
}
