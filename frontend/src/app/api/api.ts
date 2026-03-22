const API_BASE = "http://127.0.0.1:8000";

// --- 1. TYPES (Your "Frontend Schemas") ---

export interface Department {
  id: number;
  name: string;
  slug: string;
}

export interface DepartmentCreate {
  name: string;
  slug: string;
}

export interface UserFeedback {
  id: number;
  name: string;
  title: string;
  content: string;
  user_id: number;
  // Add other fields from UserFeedbackOut
}

export interface UserFeedbackCreate {
  title: string;
  content: string;
  user_id: number;
}

// --- 2. THE REUSABLE API CLIENT (The "Engine") ---
// This handles the repetitive fetch logic for high performance and maintenance.

async function request<T>(url: string, config: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${url}`, {
    ...config,
    headers: {
      "Content-Type": "application/json",
      ...config.headers,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP Error: ${response.status}`);
  }

  // For DELETE requests returning {"ok": true} or empty
  if (response.status === 204 || url.includes("delete")) {
     return response.json() as Promise<T>;
  }

  return response.json();
}

// --- 3. THE NAMESPACED SERVICES (The "Routes") ---

export const departmentAPI = {
  get_items: (skip = 0, limit = 100) => 
    request<Department[]>(`/departments/?skip=${skip}&limit=${limit}`),
    
  get_item: (id: number) => 
    request<Department>(`/departments/${id}`),
    
  create_item: (data: DepartmentCreate) => 
    request<Department>(`/departments/`, { method: "POST", body: JSON.stringify(data) }),
    
  update_item: (id: number, data: Partial<DepartmentCreate>) => 
    request<Department>(`/departments/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
    
  delete_item: (id: number) => 
    request<{ ok: boolean }>(`/departments/${id}`, { method: "DELETE" }),
};

export const feedbackAPI = {
  get_items: (skip = 0, limit = 100) => 
    request<UserFeedback[]>(`/feedbacks/?skip=${skip}&limit=${limit}`),
    
  get_item: (id: number) => 
    request<UserFeedback>(`/feedbacks/${id}`),
    
  create_item: (data: UserFeedbackCreate) => 
    request<UserFeedback>(`/feedbacks/`, { method: "POST", body: JSON.stringify(data) }),
    
  update_item: (id: number, data: Partial<UserFeedbackCreate>) => 
    request<UserFeedback>(`/feedbacks/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
    
  delete_item: (id: number) => 
    request<{ ok: boolean }>(`/feedbacks/${id}`, { method: "DELETE" }),
};