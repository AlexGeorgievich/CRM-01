export type Role = "admin" | "manager";

export type User = {
  id: number;
  username: string;
  email?: string | null;
  full_name: string;
  role: Role;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type UserCreateInput = {
  username: string;
  password: string;
  email?: string | null;
  full_name: string;
  role: Role;
  is_active: boolean;
};

export type UserUpdateInput = {
  email?: string | null;
  full_name?: string;
  role?: Role;
  is_active?: boolean;
};

export type DictionaryItem = {
  id: number;
  name: string;
  is_active: boolean;
  sort_order: number;
  created_at: string;
  updated_at: string;
};

export type Status = DictionaryItem & {
  code: string;
  is_final: boolean;
};

export type DictionaryInput = {
  name: string;
  is_active: boolean;
  sort_order: number;
};

export type StatusInput = DictionaryInput & {
  code: string;
  is_final: boolean;
};

export type Comment = {
  id: number;
  lead_id: number;
  author_id: number | null;
  body: string;
  created_at: string;
};

export type Lead = {
  id: number;
  customer_name: string;
  contact: string;
  email?: string | null;
  notes?: string | null;
  course_id?: number | null;
  source_id?: number | null;
  status_id: number;
  assigned_manager_id?: number | null;
  created_by_id?: number | null;
  deleted_at?: string | null;
  created_at: string;
  updated_at: string;
  next_contact_date?: string | null;
  course?: DictionaryItem | null;
  source?: DictionaryItem | null;
  status: Status;
  assigned_manager?: User | null;
  created_by?: User | null;
  comments?: Comment[];
};

export type LeadInput = {
  customer_name: string;
  contact: string;
  email?: string | null;
  notes?: string | null;
  course_id?: number | null;
  source_id?: number | null;
  status_id: number;
  assigned_manager_id?: number | null;
  next_contact_date?: string | null;
};

export type LeadFilters = {
  search?: string;
  status_id?: number | "";
  course_id?: number | "";
  source_id?: number | "";
  assigned_manager_id?: number | "";
  overdue?: boolean;
  include_archived?: boolean;
};

export type LeadList = {
  items: Lead[];
  total: number;
  skip: number;
  limit: number;
};

export type Dictionaries = {
  statuses: Status[];
  courses: DictionaryItem[];
  sources: DictionaryItem[];
};

export type Session = {
  token: string;
  user: User;
  mode: "mock" | "api";
};

export type ImportRow = {
  customer_name: string;
  contact: string;
  email?: string;
  status: string;
  course: string;
  source: string;
  assigned_manager: string;
  notes?: string;
  next_contact_date?: string;
  errors: string[];
};
