"use client";

import { Bar, BarChart, CartesianGrid, Funnel, FunnelChart, Line, LineChart, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Badge, Panel } from "./ui";

type Analytics = ReturnType<typeof import("@/lib/analytics").buildAnalytics>;

export function DashboardView({ analytics, loading }: { analytics: Analytics; loading: boolean }) {
  const kpi = [
    { label: "Заявки", value: analytics.kpi.total, tone: "neutral" as const },
    { label: "Успешно", value: analytics.kpi.won, tone: "success" as const },
    { label: "Просрочено", value: analytics.kpi.overdue, tone: "danger" as const },
    { label: "Конверсия", value: `${analytics.kpi.conversion}%`, tone: "warning" as const }
  ];

  return (
    <div className="grid gap-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="text-sm text-muted">Обновлено {new Date(analytics.updatedAt).toLocaleString("ru-RU")}</div>
        {loading ? <Badge tone="warning">Обновление</Badge> : <Badge tone="success">Актуально</Badge>}
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        {kpi.map((item) => (
          <Panel key={item.label} className="p-4">
            <div className="text-sm text-muted">{item.label}</div>
            <div className="mt-2 flex items-end justify-between gap-2">
              <div className="text-3xl font-semibold text-ink">{item.value}</div>
              <Badge tone={item.tone}>{item.label}</Badge>
            </div>
          </Panel>
        ))}
      </div>

      <div className="grid gap-5 xl:grid-cols-2">
        <ChartPanel title="Воронка по статусам">
          <ResponsiveContainer width="100%" height={280}>
            <FunnelChart>
              <Tooltip />
              <Funnel dataKey="value" data={analytics.byStatus} nameKey="name" fill="#1F6FEB" />
            </FunnelChart>
          </ResponsiveContainer>
        </ChartPanel>

        <ChartPanel title="Динамика заявок">
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={analytics.timeline}>
              <CartesianGrid stroke="#E5E7EB" />
              <XAxis dataKey="date" />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Line type="monotone" dataKey="leads" stroke="#11845B" strokeWidth={2} dot={{ r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        </ChartPanel>

        <ChartPanel title="Источники">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={analytics.bySource}>
              <CartesianGrid stroke="#E5E7EB" />
              <XAxis dataKey="name" />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="leads" fill="#1F6FEB" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartPanel>

        <ChartPanel title="Курсы">
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Tooltip />
              <Pie data={analytics.byCourse} dataKey="leads" nameKey="name" outerRadius={95} fill="#11845B" label />
            </PieChart>
          </ResponsiveContainer>
        </ChartPanel>
      </div>

      <Panel className="overflow-hidden">
        <div className="border-b border-line px-4 py-3 text-sm font-semibold">Менеджеры</div>
        <div className="overflow-x-auto">
          <table className="w-full min-w-[680px] border-collapse text-sm">
            <thead className="bg-panel text-left text-xs uppercase text-muted">
              <tr>
                <th className="px-4 py-3">Менеджер</th>
                <th className="px-4 py-3">Заявки</th>
                <th className="px-4 py-3">Просрочки</th>
                <th className="px-4 py-3">Успешно</th>
              </tr>
            </thead>
            <tbody>
              {analytics.byManager.map((row) => (
                <tr key={row.name} className="border-t border-line">
                  <td className="px-4 py-3 font-medium">{row.name}</td>
                  <td className="px-4 py-3">{row.leads}</td>
                  <td className="px-4 py-3">{row.overdue}</td>
                  <td className="px-4 py-3">{row.won}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>
    </div>
  );
}

function ChartPanel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <Panel className="p-4">
      <div className="mb-3 text-sm font-semibold">{title}</div>
      {children}
    </Panel>
  );
}
