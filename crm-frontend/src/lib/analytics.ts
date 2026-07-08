import type { Dictionaries, Lead, User } from "./types";

export function isOverdue(lead: Lead, referenceDate = new Date("2026-07-08T00:00:00.000Z")) {
  return Boolean(lead.next_contact_date && new Date(lead.next_contact_date) < referenceDate && !lead.status.is_final);
}

export function buildAnalytics(leads: Lead[], dictionaries: Dictionaries, users: User[]) {
  const activeLeads = leads.filter((lead) => !lead.deleted_at);
  const won = activeLeads.filter((lead) => lead.status.code === "won").length;
  const overdue = activeLeads.filter((lead) => isOverdue(lead)).length;
  const final = activeLeads.filter((lead) => lead.status.is_final).length;
  const conversion = activeLeads.length ? Math.round((won / activeLeads.length) * 100) : 0;

  const byStatus = dictionaries.statuses.map((status) => ({
    name: status.name,
    value: activeLeads.filter((lead) => lead.status_id === status.id).length
  }));

  const bySource = dictionaries.sources.map((source) => {
    const sourceLeads = activeLeads.filter((lead) => lead.source_id === source.id);
    const sourceWon = sourceLeads.filter((lead) => lead.status.code === "won").length;
    return {
      name: source.name,
      leads: sourceLeads.length,
      conversion: sourceLeads.length ? Math.round((sourceWon / sourceLeads.length) * 100) : 0
    };
  });

  const byCourse = dictionaries.courses.map((course) => ({
    name: course.name,
    leads: activeLeads.filter((lead) => lead.course_id === course.id).length
  }));

  const byManager = users
    .filter((user) => user.role === "manager")
    .map((user) => {
      const owned = activeLeads.filter((lead) => lead.assigned_manager_id === user.id);
      return {
        name: user.full_name,
        leads: owned.length,
        overdue: owned.filter((lead) => isOverdue(lead)).length,
        won: owned.filter((lead) => lead.status.code === "won").length
      };
    });

  const timeline = Array.from(
    activeLeads.reduce((acc, lead) => {
      const day = lead.created_at.slice(5, 10);
      acc.set(day, (acc.get(day) ?? 0) + 1);
      return acc;
    }, new Map<string, number>())
  ).map(([date, leads]) => ({ date, leads }));

  return {
    updatedAt: new Date().toISOString(),
    kpi: {
      total: activeLeads.length,
      won,
      final,
      overdue,
      conversion
    },
    byStatus,
    bySource,
    byCourse,
    byManager,
    timeline
  };
}
