"use client";
import Link from 'next/link'
import { useEffect, useState } from "react";
// Assuming AppLayout is in the components folder two directories up
//import AppLayout from "../../components/AppLayout"; 
import Side_Top_Navbar_Layout from "../../components/layout/navbars/navbars";
import { departmentAPI, Department } from "../api/api";
import { 
  Building2, 
  Loader2, 
  AlertCircle, 
  Pencil, 
  Trash2, 
  Plus,
  MoreVertical 
} from "lucide-react";

export default function DepartmentsPage() {
  const [departments, setDepartments] = useState<Department[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadDepartments = async () => {
    try {
      setLoading(true);
      const data = await departmentAPI.getAll();
      setDepartments(data);
    } catch (err) {
      setError("Failed to load departments. Is the backend running?");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDepartments();
  }, []);

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this department?")) return;
    
    try {
      await departmentAPI.delete(id);
      // Optimistic update: remove from UI immediately
      setDepartments(departments.filter(d => d.id !== id));
    } catch (err) {
      alert("Failed to delete department");
    }
  };

  return (
    <Side_Top_Navbar_Layout>
      <div className="p-8 max-w-7xl mx-auto">
        {/* Page Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
          <div>
            <h1 className="text-2xl font-black text-slate-800 tracking-tight uppercase flex items-center gap-2">
              <Building2 className="text-blue-700" size={24} />
              Departments
            </h1>
            <p className="text-sm text-slate-500 mt-1">
              View and manage organizational structure and unit details.
            </p>
          </div>
          <button className="bg-blue-700 text-white px-5 py-2.5 rounded-xl text-xs font-bold hover:bg-blue-800 transition-all shadow-lg shadow-blue-200 flex items-center justify-center gap-2 w-full md:w-auto">
            <Plus size={18} />
            CREATE NEW
          </button>
        </div>

        {/* Table Section */}
        <div className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-24 text-slate-400">
              <Loader2 className="animate-spin mb-4 text-blue-600" size={40} />
              <p className="text-xs font-bold uppercase tracking-[0.2em]">Syncing with Database...</p>
            </div>
          ) : error ? (
            <div className="m-6 flex items-center gap-3 p-4 bg-red-50 border border-red-100 rounded-xl text-red-700">
              <AlertCircle size={20} />
              <p className="text-sm font-semibold">{error}</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-slate-50/50 border-b border-slate-200">
                    <th className="px-6 py-4 text-[10px] font-black text-slate-400 uppercase tracking-widest">ID</th>
                    <th className="px-6 py-4 text-[10px] font-black text-slate-400 uppercase tracking-widest">Department Name</th>
                    <th className="px-6 py-4 text-[10px] font-black text-slate-400 uppercase tracking-widest text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {departments.map((dept) => (
                    <tr key={dept.id} className="hover:bg-slate-50/80 transition-colors group">
                      <td className="px-6 py-4">
                        <span className="text-xs font-mono font-bold text-slate-400">#{dept.id}</span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center font-bold text-xs">
                            {dept.name.charAt(0).toUpperCase()}
                          </div>
                          <span className="text-sm font-bold text-slate-700">{dept.name}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center justify-end gap-2">
                          <button 
                            onClick={() => console.log("Edit", dept.id)}
                            className="p-2 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all"
                            title="Edit Department"
                          >
                            <Pencil size={18} />
                          </button>
                          <button 
                            onClick={() => handleDelete(dept.id)}
                            className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all"
                            title="Delete Department"
                          >
                            <Trash2 size={18} />
                          </button>
                        </div>
                      </td>
                      <td>
                        
       
          <Link href={`/departments/${dept.name}-${dept.id}-${dept.slug}`}>{dept.id} - Details</Link>

                      </td>



                      
     
       
  

                    </tr>
                  ))}
                </tbody>
              </table>

              {departments.length === 0 && (
                <div className="py-20 flex flex-col items-center justify-center text-slate-400">
                  <div className="p-4 bg-slate-50 rounded-full mb-4">
                    <Building2 size={32} className="text-slate-300" />
                  </div>
                  <p className="text-sm font-medium">No departments found in the system</p>
                  <button 
                    onClick={loadDepartments}
                    className="mt-2 text-xs font-bold text-blue-600 hover:underline"
                  >
                    Refresh data
                  </button>
                </div>
              )}
            </div>

            
          )}
        </div>
        
        {/* Footer Info */}
        {!loading && !error && (
          <div className="mt-4 flex justify-between items-center px-2">
            <p className="text-[11px] text-slate-400 font-bold uppercase tracking-wider">
              Total Results: {departments.length}
            </p>
          </div>
        )}
      </div>
    </Side_Top_Navbar_Layout>
  );
}