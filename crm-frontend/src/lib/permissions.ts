import type { Role } from "./types";

const grants: Record<Role, string[]> = {
  admin: ["leads:view", "leads:edit", "leads:delete", "csv:export", "csv:import", "analytics:view", "admin:view"],
  manager: ["leads:view", "leads:edit", "csv:export", "analytics:view"]
};

export function can(role: Role, permission: string) {
  return grants[role].includes(permission);
}
