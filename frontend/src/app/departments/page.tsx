"use client";

import Link from 'next/link'
import { useEffect, useState } from "react";
import Side_Top_Navbar_Layout from "../../components/layout/navbars/navbars";
import { departmentAPI, Department } from "../api/api";
import { 
  Building2, 
  Loader2, 
  AlertCircle, 
  Pencil, 
  Trash2, 
  Plus,
  X,
  AlertTriangle 
} from "lucide-react";

export default function DepartmentsPage() {
  const [departments, setDepartments] = useState<Department[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Modal State
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [selectedDept, setSelectedDept] = useState<Department | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const loadDepartments = async () => {
    try {
      setLoading(true);
      const data = await departmentAPI.get_items();
      setDepartments(data);
    } catch (err) {
      setError("Failed to load departments. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDepartments();
  }, []);

  const openDeleteModal = (dept: Department) => {
    setSelectedDept(dept);
    setIsDeleteModalOpen(true);
  };

  const closeDeleteModal = () => {
    setIsDeleteModalOpen(false);
    setSelectedDept(null);
  };

  const handleDelete = async () => {
    if (!selectedDept) return;
    
    try {
      setIsDeleting(true);
      await departmentAPI.delete_item(selectedDept.id);
      setDepartments(prev => prev.filter(d => d.id !== selectedDept.id));
      closeDeleteModal();
    } catch (err) {
      alert("Critical: Failed to delete department on server.");
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <Side_Top_Navbar_Layout>
      <div className="relative p-8 max-w-7xl mx-auto">
        {/* Page Header */}
        <div className="flex flex-col md:flex-row md:items-center justify-between mb-8 gap-4">
          <div>
            <h1 className="text-2xl font-black text-slate-800 tracking-tight uppercase flex items-center gap-2">
              <Building2 className="text-blue-700" size={24} />
              Departments
            </h1>
            <p className="text-sm text-slate-500 mt-1">
              View and manage organizational structure.
            </p>
          </div>

          <Link href="/departments/create" className="w-full md:w-auto">
            <button className="bg-blue-700 text-white px-5 py-2.5 rounded-xl text-xs font-bold hover:bg-blue-800 transition-all shadow-lg shadow-blue-200 flex items-center justify-center gap-2 w-full">
              <Plus size={18} />
              CREATE NEW
            </button>
          </Link>
        </div>

        {/* Table Section */}
        <div className="bg-white border border-slate-200 rounded-2xl shadow-sm overflow-hidden">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-24 text-slate-400">
              <Loader2 className="animate-spin mb-4 text-blue-600" size={40} />
              <p className="text-xs font-bold uppercase tracking-[0.2em]">Syncing...</p>
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
                    <th className="px-6 py-4 text-[10px] font-black text-slate-400 uppercase tracking-widest text-center w-20">ID</th>
                    <th className="px-6 py-4 text-[10px] font-black text-slate-400 uppercase tracking-widest">Name</th>
                    <th className="px-6 py-4 text-[10px] font-black text-slate-400 uppercase tracking-widest text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {departments.map((dept) => (
                    <tr key={dept.id} className={`hover:bg-slate-50/80 transition-colors ${selectedDept?.id === dept.id ? 'bg-red-50/50' : ''}`}>
                      <td className="px-6 py-4 text-center">
                        <span className="text-xs font-mono font-bold text-slate-400">#{dept.id}</span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center font-bold text-xs uppercase">
                            {dept.name.charAt(0)}
                          </div>
                          <span className="text-sm font-bold text-slate-700">{dept.name}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center justify-end gap-2">
                          <Link href={`/departments/edit/${dept.id}`}>
                            <button className="p-2 text-slate-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-all">
                              <Pencil size={18} />
                            </button>
                          </Link>
                          <button 
                            onClick={() => openDeleteModal(dept)}
                            className={`p-2 rounded-lg transition-all ${selectedDept?.id === dept.id ? 'text-red-600 bg-red-100' : 'text-slate-400 hover:text-red-600 hover:bg-red-50'}`}
                          >
                            <Trash2 size={18} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Floating Side Action Panel (Non-blocking) */}
        {isDeleteModalOpen && (
          <div className="fixed top-24 right-8 z-50 w-80 bg-white border border-red-200 rounded-2xl shadow-[0_20px_50px_rgba(0,0,0,0.15)] overflow-hidden animate-in slide-in-from-right-10 duration-300">
            <div className="p-5 border-b border-slate-100 flex justify-between items-center bg-red-50/30">
              <div className="flex items-center gap-2 text-red-600">
                <AlertTriangle size={18} />
                <span className="text-[10px] font-black uppercase tracking-widest">Critical Action</span>
              </div>
              <button onClick={closeDeleteModal} className="text-slate-400 hover:text-slate-600">
                <X size={18} />
              </button>
            </div>
            
            <div className="p-6">
              <p className="text-xs text-slate-500 mb-1">Delete Department:</p>
              <h3 className="text-lg font-black text-slate-800 leading-tight mb-4 uppercase">
                {selectedDept?.name}
              </h3>
              <p className="text-[11px] text-slate-400 leading-relaxed mb-6">
                Removing this record is irreversible. Ensure you have no dependencies linked to this department.
              </p>

              <div className="flex flex-col gap-2">
                <button 
                  onClick={handleDelete}
                  disabled={isDeleting}
                  className="w-full py-3 rounded-xl text-xs font-bold bg-red-600 text-white hover:bg-red-700 transition-all shadow-lg shadow-red-100 flex items-center justify-center gap-2"
                >
                  {isDeleting ? <Loader2 size={14} className="animate-spin" /> : <Trash2 size={14} />}
                  CONFIRM DELETION
                </button>
                <button 
                  onClick={closeDeleteModal}
                  className="w-full py-3 rounded-xl text-xs font-bold text-slate-500 hover:bg-slate-100 transition-all"
                >
                  KEEP DEPARTMENT
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Footer Info */}
        {!loading && !error && (
          <div className="mt-4 px-2">
            <p className="text-[11px] text-slate-400 font-bold uppercase tracking-wider">
              Items: {departments.length}
            </p>
          </div>
        )}
      </div>
    </Side_Top_Navbar_Layout>
  );
}