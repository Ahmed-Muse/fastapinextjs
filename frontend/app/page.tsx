"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ChevronDown, ChevronRight, Menu, User } from "lucide-react";

const API_BASE = "http://127.0.0.1:8000";

type Department = { id: number; name: string };
type Feedback = { id: number; name: string; description?: string };

export default function HomePage() {
  const router = useRouter();

  const [departments, setDepartments] = useState<Department[]>([]);
  const [feedbacks, setFeedbacks] = useState<Feedback[]>([]);

  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [openMenu, setOpenMenu] = useState<string | null>(null);
  const [openSubMenu, setOpenSubMenu] = useState<string | null>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [deptRes, fbRes] = await Promise.all([
          fetch(`${API_BASE}/departments/`),
          fetch(`${API_BASE}/user/feedbacks/`),
        ]);

        if (!deptRes.ok || !fbRes.ok) throw new Error("Failed to fetch data");

        const deptData = await deptRes.json();
        const fbData = await fbRes.json();

        setDepartments(deptData);
        setFeedbacks(fbData);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const toggleMenu = (menu: string) => {
    setOpenMenu(openMenu === menu ? null : menu);
    setOpenSubMenu(null);
  };

  const toggleSubMenu = (submenu: string) => {
    setOpenSubMenu(openSubMenu === submenu ? null : submenu);
  };

  return (
    <div className="flex flex-col h-screen bg-[#F4F8FD] text-gray-900">
      {/* TOP NAVBAR */}
      <header className="flex items-center justify-between bg-white shadow-lg p-4 sticky top-0 z-50">
        {/* Left: sidebar toggle */}
        <div className="flex items-center gap-4">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 rounded-lg hover:bg-gray-100 transition"
          >
            <Menu size={24} />
          </button>

          <span className="text-xl font-bold text-blue-700">AI Sizing Platform</span>
        </div>

        {/* Center: top navbar dropdowns */}
        <nav className="flex items-center gap-6">
          <div className="relative">
            <button
              onClick={() => toggleMenu("products")}
              className="flex items-center gap-1 font-semibold hover:text-blue-600"
            >
              Products
              {openMenu === "products" ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
            </button>
            {openMenu === "products" && (
              <div className="absolute top-8 left-0 bg-white shadow-lg rounded-lg w-48 p-3 space-y-2">
                <div className="hover:text-blue-600 cursor-pointer" onClick={() => router.push("/departments")}>Departments</div>
                <div className="hover:text-blue-600 cursor-pointer" onClick={() => router.push("/feedbacks")}>Feedbacks</div>
              </div>
            )}
          </div>

          <div className="relative">
            <button
              onClick={() => toggleMenu("reports")}
              className="flex items-center gap-1 font-semibold hover:text-blue-600"
            >
              Reports
              {openMenu === "reports" ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
            </button>
            {openMenu === "reports" && (
              <div className="absolute top-8 left-0 bg-white shadow-lg rounded-lg w-48 p-3 space-y-2">
                <div className="hover:text-blue-600 cursor-pointer">Usage Reports</div>
                <div className="hover:text-blue-600 cursor-pointer">Feedback Analysis</div>
              </div>
            )}
          </div>
        </nav>

        {/* Right: login button */}
        <div>
          <button className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition">
            <User size={18} />
            Login
          </button>
        </div>
      </header>

      {/* MAIN WRAPPER */}
      <div className="flex flex-1 overflow-hidden">
        {/* SIDEBAR */}
        <aside
          className={`fixed top-0 left-0 h-full w-64 bg-white shadow-xl p-5 transform transition-transform duration-300 z-40 ${
            sidebarOpen ? "translate-x-0" : "-translate-x-full"
          }`}
        >
          <h2 className="text-xl font-bold mb-6 text-blue-700">Navigation</h2>

          {/* DEPARTMENTS */}
          <div>
            <button
              className="flex items-center gap-2 py-3 font-semibold hover:text-blue-600 w-full"
              onClick={() => toggleMenu("dept")}
            >
              {openMenu === "dept" ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
              Departments
            </button>
            {openMenu === "dept" && (
              <div className="ml-4">
                <button
                  className="flex items-center gap-2 py-2 text-sm hover:text-blue-500 w-full"
                  onClick={() => toggleSubMenu("deptList")}
                >
                  {openSubMenu === "deptList" ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                  View Departments
                </button>
                {openSubMenu === "deptList" && (
                  <div className="ml-4 space-y-2">
                    {departments.map((dept) => (
                      <div
                        key={dept.id}
                        className="text-sm cursor-pointer hover:text-blue-600"
                        onClick={() => router.push(`/departments/${dept.id}`)}
                      >
                        {dept.name}
                      </div>
                    ))}
                  </div>
                )}
                <button
                  className="py-2 text-sm hover:text-blue-500 w-full"
                  onClick={() => router.push("/departments/create")}
                >
                  Create Department
                </button>
              </div>
            )}
          </div>

          {/* FEEDBACK */}
          <div className="mt-4">
            <button
              className="flex items-center gap-2 py-3 font-semibold hover:text-blue-600 w-full"
              onClick={() => toggleMenu("fb")}
            >
              {openMenu === "fb" ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
              User Feedback
            </button>
            {openMenu === "fb" && (
              <div className="ml-4">
                <button
                  className="flex items-center gap-2 py-2 text-sm hover:text-blue-500 w-full"
                  onClick={() => toggleSubMenu("fbList")}
                >
                  {openSubMenu === "fbList" ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                  View Feedbacks
                </button>
                {openSubMenu === "fbList" && (
                  <div className="ml-4 space-y-2">
                    {feedbacks.map((fb) => (
                      <div key={fb.id} className="text-sm hover:text-blue-600">
                        {fb.name}
                      </div>
                    ))}
                  </div>
                )}
                <button
                  className="py-2 text-sm hover:text-blue-500 w-full"
                  onClick={() => router.push("/feedbacks/create")}
                >
                  Add Feedback
                </button>
              </div>
            )}
          </div>
        </aside>

        {/* MAIN CONTENT */}
        <main className="flex-1 p-10 ml-0 md:ml-0 overflow-y-auto">
          {/* HERO */}
          <section className="bg-gradient-to-r from-blue-600 to-blue-400 text-white p-10 rounded-2xl shadow-lg mb-10">
            <h1 className="text-4xl font-bold mb-4">AI Engineering Product Sizing Platform</h1>
            <p className="mb-6 max-w-2xl text-blue-100">
              Automate engineering calculations, optimize product selection, and generate accurate quotations instantly using AI-powered tools.
            </p>

            <div className="flex gap-4">
              <button
                onClick={() => router.push("/departments")}
                className="bg-white text-blue-700 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition"
              >
                Explore Departments
              </button>

              <button
                onClick={() => router.push("/feedbacks/create")}
                className="border border-white px-6 py-3 rounded-lg hover:bg-white hover:text-blue-700"
              >
                Give Feedback
              </button>
            </div>
          </section>

          {/* STATES */}
          {loading && <p className="text-gray-500">Loading data...</p>}
          {error && <p className="text-red-500">{error}</p>}

          {!loading && !error && (
            <>
              {/* DEPARTMENTS */}
              <section className="mb-12">
                <h2 className="text-2xl font-semibold mb-6 text-blue-700">Departments</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {departments.map((dept) => (
                    <div
                      key={dept.id}
                      className="bg-white p-6 rounded-xl shadow hover:shadow-lg hover:-translate-y-1 transition cursor-pointer"
                      onClick={() => router.push(`/departments/${dept.id}`)}
                    >
                      <h3 className="text-lg font-semibold mb-2">{dept.name}</h3>
                      <p className="text-sm text-gray-500">
                        Access AI tools and sizing modules for this department.
                      </p>
                    </div>
                  ))}
                </div>
              </section>

              {/* FEEDBACK */}
              <section>
                <h2 className="text-2xl font-semibold mb-6 text-blue-700">User Feedback</h2>
                <div className="grid md:grid-cols-2 gap-6">
                  {feedbacks.map((fb) => (
                    <div
                      key={fb.id}
                      className="bg-white p-5 rounded-xl shadow hover:shadow-md transition"
                    >
                      <h4 className="font-semibold mb-1">{fb.name}</h4>
                      <p className="text-gray-600 text-sm">{fb.description}</p>
                    </div>
                  ))}
                </div>
              </section>
            </>
          )}
        </main>
      </div>
    </div>
  );
}