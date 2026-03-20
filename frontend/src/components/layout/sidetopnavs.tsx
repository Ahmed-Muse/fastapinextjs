"use client";

import { useEffect, useState, useRef } from "react";
import Link from "next/link";
import { 
  ChevronDown, 
  ChevronRight, 
  Menu, 
  User, 
  Settings, 
  X,
  Droplets,
  Search,
  ShoppingCart,
  ClipboardList,
} from "lucide-react";

export default function DashboardShell({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [openMenu, setOpenMenu] = useState<string | null>(null);
  const [openSubMenu, setOpenSubMenu] = useState<string | null>(null);
  const [activeNavDropdown, setActiveNavDropdown] = useState<string | null>(null);
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const searchInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isSearchOpen && searchInputRef.current) {
      searchInputRef.current.focus();
    }
  }, [isSearchOpen]);

  const toggleMenu = (menu: string) => {
    setOpenMenu(openMenu === menu ? null : menu);
    setOpenSubMenu(null);
  };

  return (
    <div className="flex flex-col h-screen bg-white text-slate-900 font-sans overflow-hidden">
      {/* TOP NAVBAR */}
      <header className="flex items-center justify-between bg-slate-100 border-b border-slate-300 px-6 h-16 sticky top-0 z-50">
        <div className="flex items-center gap-4">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 rounded-lg hover:bg-slate-200 transition text-slate-700 border border-slate-300"
          >
            {sidebarOpen ? <X size={22} /> : <Menu size={22} />}
          </button>
          <div className="flex items-center gap-3 select-none">
            <div className="w-8 h-8 bg-blue-700 rounded-md flex items-center justify-center text-white font-bold text-sm shadow-sm">D&S</div>
            <span className="hidden sm:block text-lg font-black text-slate-800 tracking-tight uppercase">AI Product Sizing Engine</span>
          </div>
        </div>

        <div className="flex items-center gap-6">
          <nav className="hidden xl:flex items-center gap-6">
             <div className="relative">
                <button onClick={() => setActiveNavDropdown(activeNavDropdown === 'dept' ? null : 'dept')} className="flex items-center gap-1 text-xs font-bold uppercase tracking-widest text-slate-600 hover:text-blue-700 transition">
                  Company<ChevronDown size={14} />
                </button>
                {activeNavDropdown === 'dept' && (
                  <div className="absolute top-full left-0 w-48 bg-white border border-slate-200 shadow-xl rounded-md p-2 mt-2 z-50">
                    <Link href="/departments" className="block p-2 text-[11px] hover:bg-slate-50 cursor-pointer rounded font-bold text-slate-800">Departments</Link>
                    <div className="p-2 text-[11px] hover:bg-slate-50 cursor-pointer rounded font-bold">Branches</div>
                  </div>
                )}
             </div>
          </nav>

          {/* Search & Login (Condensed for brevity) */}
          <div className="relative flex items-center">
            <button onClick={() => setIsSearchOpen(!isSearchOpen)} className="p-2 text-slate-500 hover:text-blue-700 transition rounded-full hover:bg-slate-200">
              <Search size={20} />
            </button>
          </div>
          <button className="flex items-center gap-2 bg-slate-800 text-white px-4 py-2 rounded-lg text-xs font-bold hover:bg-slate-900 transition shadow-md">
            <User size={16} /> Login
          </button>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden relative">
        {/* SIDEBAR */}
        <aside className={`fixed top-16 left-0 h-[calc(100vh-4rem)] w-64 bg-slate-100 shadow-2xl transform transition-transform duration-300 ease-in-out z-40 border-r border-slate-300 ${sidebarOpen ? "translate-x-0" : "-translate-x-full"}`}>
          <div className="p-4 overflow-y-auto h-full">
            <p className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-6 px-2">Core Operations</p>
            <div className="space-y-2">
              <button onClick={() => toggleMenu("sales")} className={`flex items-center justify-between w-full p-3 rounded-xl transition text-sm font-bold ${openMenu === "sales" ? 'bg-white text-blue-700' : 'text-slate-600'}`}>
                <div className="flex items-center gap-3"><ShoppingCart size={20} /><span>Sales & Quotes</span></div>
                {openMenu === "sales" ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
              </button>
              <button className="flex items-center gap-3 w-full p-3 rounded-xl text-sm font-bold text-slate-600 hover:bg-slate-200"><Settings size={20} /><span>System Config</span></button>
            </div>
          </div>
        </aside>

        {/* MAIN CONTENT: This is where the page content will inject */}
        <main className={`flex-1 transition-all duration-300 p-8 overflow-y-auto bg-white ${sidebarOpen ? "ml-64" : "ml-0"}`}>
            {children}
        </main>
      </div>
    </div>
  );
}