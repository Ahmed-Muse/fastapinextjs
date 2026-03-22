"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import Link from "next/link";
import { 
  Building2, 
  ArrowLeft, 
  Save, 
  Loader2, 
  AlertCircle,
  Pencil
} from "lucide-react";
import Side_Top_Navbar_Layout from "../../../../components/layout/navbars/navbars";
import { departmentAPI } from "../../../api/api";

export default function EditDepartmentPage() {
  const router = useRouter();
  const params = useParams(); 
  
  // FIX: Safely extract ID and handle the potential null/undefined
  const id = params?.id ? Number(params.id) : null;

  const [formData, setFormData] = useState({ name: "", slug: "" });
  const [loading, setLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // If ID is null or invalid, don't attempt to fetch
    if (!id || isNaN(id)) {
      if (!loading) setError("Invalid Department ID.");
      return;
    }

    const fetchDept = async () => {
      try {
        setLoading(true);
        const data = await departmentAPI.get_item(id);
        setFormData({ name: data.name, slug: data.slug });
      } catch (err: any) {
        setError("Could not find this department record.");
      } finally {
        setLoading(false);
      }
    };

    fetchDept();
  }, [id]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!id) return;

    setIsSubmitting(true);
    setError(null);

    try {
      await departmentAPI.update_item(id, formData);
      router.push("/departments");
      router.refresh();
    } catch (err: any) {
      setError(err.message || "Failed to update department.");
    } finally {
      setIsSubmitting(false);
    }
  };

  // UI for Loading State
  if (loading) {
    return (
      <Side_Top_Navbar_Layout>
        <div className="flex flex-col items-center justify-center min-h-[60vh] text-slate-400">
          <Loader2 className="animate-spin mb-4 text-blue-600" size={40} />
          <p className="text-xs font-bold uppercase tracking-widest">Fetching Record...</p>
        </div>
      </Side_Top_Navbar_Layout>
    );
  }

  return (
    <Side_Top_Navbar_Layout>
      <div className="p-8 max-w-3xl mx-auto">
        <div className="mb-8">
          <Link 
            href="/departments" 
            className="text-slate-500 hover:text-blue-600 flex items-center gap-2 text-sm font-bold transition-colors mb-4"
          >
            <ArrowLeft size={16} /> BACK TO LIST
          </Link>
          <h1 className="text-2xl font-black text-slate-800 tracking-tight uppercase flex items-center gap-2">
            <Pencil className="text-blue-700" size={24} />
            Edit Department: <span className="text-blue-600">#{id}</span>
          </h1>
        </div>

        <div className="bg-white border border-slate-200 rounded-2xl shadow-sm p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <div className="flex items-center gap-3 p-4 bg-red-50 border border-red-100 rounded-xl text-red-700 text-sm font-semibold">
                <AlertCircle size={18} /> {error}
              </div>
            )}

            <div>
              <label className="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">
                Department Name
              </label>
              <input
                required
                type="text"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none transition-all font-medium text-slate-700"
              />
            </div>

            <div>
              <label className="block text-[10px] font-black text-slate-400 uppercase tracking-widest mb-2">
                URL Slug
              </label>
              <input
                required
                type="text"
                value={formData.slug}
                onChange={(e) => setFormData({ ...formData, slug: e.target.value })}
                className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl font-mono text-sm text-slate-500"
              />
            </div>

            <div className="pt-4 flex gap-3">
              <button
                type="submit"
                disabled={isSubmitting}
                className="flex-1 bg-blue-700 text-white px-6 py-3 rounded-xl font-bold hover:bg-blue-800 transition-all shadow-lg shadow-blue-200 flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {isSubmitting ? (
                  <Loader2 className="animate-spin" size={18} />
                ) : (
                  <Save size={18} />
                )}
                UPDATE CHANGES
              </button>
              
              <Link href="/departments" className="flex-1">
                <button 
                  type="button" 
                  className="w-full px-6 py-3 border border-slate-200 text-slate-500 rounded-xl font-bold hover:bg-slate-50 transition-all"
                >
                  CANCEL
                </button>
              </Link>
            </div>
          </form>
        </div>
      </div>
    </Side_Top_Navbar_Layout>
  );
}