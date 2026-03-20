const API_BASE = "http://127.0.0.1:8000"; // Adjust to your actual backend URL/port if needed

// Match these to your FastAPI schemas (DepartmentOut, DepartmentCreate, DepartmentUpdate)
export interface Department {
  id: number;
  name: string;
  // Add other fields defined in your FastAPI DepartmentOut schema here
}

export interface DepartmentCreate {
  name: string;
  // Add other required fields
}

export const departmentAPI = {
  // GET /departments/
  getAll: async (skip = 0, limit = 100): Promise<Department[]> => {
    const res = await fetch(`${API_BASE}/departments/?skip=${skip}&limit=${limit}`);
    if (!res.ok) throw new Error("Failed to fetch departments");
    return res.json();
  },

  // GET /departments/{id}
  getOne: async (id: number): Promise<Department> => {
    const res = await fetch(`${API_BASE}/departments/${id}`);
    if (!res.ok) throw new Error("Failed to fetch department");
    return res.json();
  },

  // POST /departments/
  create: async (data: DepartmentCreate): Promise<Department> => {
    const res = await fetch(`${API_BASE}/departments/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Failed to create department");
    return res.json();
  },

  // PATCH /departments/{id}
  update: async (id: number, data: Partial<DepartmentCreate>): Promise<Department> => {
    const res = await fetch(`${API_BASE}/departments/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Failed to update department");
    return res.json();
  },

  // DELETE /departments/{id}
  delete: async (id: number): Promise<boolean> => {
    const res = await fetch(`${API_BASE}/departments/${id}`, {
      method: "DELETE",
    });
    if (!res.ok) throw new Error("Failed to delete department");
    return true;
  },
};