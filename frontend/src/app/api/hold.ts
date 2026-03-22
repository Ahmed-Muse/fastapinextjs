const API_BASE = "http://127.0.0.1:8000"; // Adjust to your actual backend URL/port if needed

// Match these to your FastAPI schemas (DepartmentOut, DepartmentCreate, DepartmentUpdate)...
//this is like the pydantic of converting model into into acceptable schema for frontend
export interface Department {
  id: number;
  name: string;
  slug: string;
  // Add other fields defined in your FastAPI DepartmentOut schema here.
}
//
export interface DepartmentCreate {
  name: string;
  slug: string;
  // Add other required fields
}
//this is ts obect literal type for department update, which is partial of department create
export const departmentAPI = {
  // GET /departments/
  //get_items is the property while the async function is the value of that property, which is a function that returns a promise of an array of departments
  get_items: async (skip = 0, limit = 100): Promise<Department[]> => {
    const res = await fetch(`${API_BASE}/departments/?skip=${skip}&limit=${limit}`);//this is the fetch api to make a get request to the backend, and it returns a promise of a response object
    if (!res.ok) throw new Error("Failed to fetch departments");
    else {
      return res.json();
    }
  },

  // GET /departments/{id}
  get_item: async (id: number): Promise<Department> => {
    const res = await fetch(`${API_BASE}/departments/${id}`);
    
    if (!res.ok) throw new Error("Failed to fetch department");
    return res.json();
  },

  // POST /departments/
  create_item: async (data: DepartmentCreate): Promise<Department> => {
    const res = await fetch(`${API_BASE}/departments/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Failed to create department");
    return res.json();
  },

  // PATCH /departments/{id}
  update_item: async (id: number, data: Partial<DepartmentCreate>): Promise<Department> => {
    const res = await fetch(`${API_BASE}/departments/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Failed to update department");
    return res.json();
  },

  // DELETE /departments/{id}
  delete_item: async (id: number): Promise<boolean> => {
    const res = await fetch(`${API_BASE}/departments/${id}`, {
      method: "DELETE",
    });
    if (!res.ok) throw new Error("Failed to delete department");
    return true;
  },
};