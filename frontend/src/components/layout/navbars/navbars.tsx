"use client";

import { useEffect, useState, useRef } from "react";
import Link from "next/link";
import { ChevronDown, ChevronRight,Menu,User,Settings,X,Droplets,Search,ShoppingCart,ClipboardList} from "lucide-react";

export default function Side_Top_Navbar_Layout({ children }: { children: React.ReactNode }) {
  // Sidebar State
  const [sidebarOpen, setSidebarOpen] = useState(false);
  
  // Menu States (Click-based)
  const [openMenu, setOpenMenu] = useState<string | null>(null);
  const [openSubMenu, setOpenSubMenu] = useState<string | null>(null);
  const [activeNavDropdown, setActiveNavDropdown] = useState<string | null>(null);

  // Search States
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const searchInputRef = useRef<HTMLInputElement>(null);

  // Focus search input when opened
  useEffect(() => {
    if (isSearchOpen && searchInputRef.current) {
      searchInputRef.current.focus();
    }
  }, [isSearchOpen]);

  // Toggle Handlers
  const toggleMenu = (menu: string) => {
    {/*this asks, is the clicked menu the open one? if yes, (null), then close it, otherwise open it*/}
    setOpenMenu(openMenu === menu ? null : menu);
    setOpenSubMenu(null); {/* Close any open submenus when toggling main menu.... in other words,
         This is a State Cleanup. By calling setOpenSubMenu(null), you are ensuring that if a user had a sub-menu open (like "Invoices") and then switches to a different main menu, the old sub-menu doesn't stay "stuck" open in the background. It resets the nested state to a clean slate. */}
  };

  const toggleSubMenu = (sub: string) => {
    setOpenSubMenu(openSubMenu === sub ? null : sub);
  };

  const toggleNavDropdown = (name: string) => {
    setActiveNavDropdown(activeNavDropdown === name ? null : name);
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
          {/* condition ? run_if_true : run_if_false...? is the ternary operator */}

          {/* HOME LINK / LOGO SECTION */}
          <Link href="/" className="flex items-center gap-3 select-none group cursor-pointer">
         
            <span className="hidden sm:block text-lg font-black text-slate-800 tracking-tight uppercase group-hover:text-blue-700 transition-colors">
             Home
            </span>
          </Link>
        </div>

        {/* RIGHT SIDE: Nav Links & Compact Search */}
        <div className="flex items-center gap-6">
          <nav className="hidden xl:flex items-center gap-6">
             {/* Departments Dropdown */}
             <div className="relative">
                <button 
                  onClick={() => toggleNavDropdown('dept')}
                  className="flex items-center gap-1 text-xs font-bold uppercase tracking-widest text-slate-600 hover:text-blue-700 transition"
                >
                  Company<ChevronDown size={14} />
                </button>
                {activeNavDropdown === 'dept' && (
                  <div className="absolute top-full left-0 w-48 bg-white border border-slate-200 shadow-xl rounded-md p-2 mt-2 z-50">
                    <Link href="/departments" className="block p-2 text-[11px] hover:bg-slate-50 cursor-pointer rounded font-bold text-slate-800">
                      Departments
                    </Link>

                      <Link href="/feedbacks" className="block p-2 text-[11px] hover:bg-slate-50 cursor-pointer rounded font-bold text-slate-800">
                      User Feedbacks
                    </Link>

                    
                  



                  </div>
                )}
             </div>

             {/* Projects Dropdown */}
             <div className="relative">
                <button 
                  onClick={() => toggleNavDropdown('projects')}
                  className="flex items-center gap-1 text-xs font-bold uppercase tracking-widest text-slate-600 hover:text-blue-700 transition"
                >
                  HRM <ChevronDown size={14} />
                </button>
                {activeNavDropdown === 'projects' && (
                  <div className="absolute top-full left-0 w-48 bg-white border border-slate-200 shadow-xl rounded-md p-2 mt-2 z-50">
                     <div className="p-2 text-[11px] hover:bg-slate-50 cursor-pointer rounded font-bold">Salaries</div>
                     <div className="p-2 text-[11px] hover:bg-slate-50 cursor-pointer rounded font-bold">Leave</div>
                  </div>
                )}
             </div>
          </nav>

          {/* Compact Search */}
          <div className="relative flex items-center">
            {!isSearchOpen ? (
              <button 
                onClick={() => setIsSearchOpen(true)}
                className="p-2 text-slate-500 hover:text-blue-700 transition rounded-full hover:bg-slate-200"
              >
                <Search size={20} />
              </button>
            ) : (
              <div className="animate-in fade-in slide-in-from-right-4 duration-200 flex items-center relative">
                <input 
                  ref={searchInputRef}
                  type="text" 
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search..." 
                  className="w-48 lg:w-64 bg-white border border-blue-600 rounded-lg py-1.5 pl-8 pr-8 text-xs focus:outline-none shadow-sm"
                />
                <Search className="absolute left-2.5 text-blue-600" size={14} />
                <button 
                  onClick={() => { setIsSearchOpen(false); setSearchQuery(""); }}
                  className="absolute right-2 text-slate-400 hover:text-slate-900"
                >
                  <X size={14} />
                </button>

                {/* Compact Results Area */}
                {searchQuery.length > 0 && (
                  <div className="absolute top-full right-0 w-64 mt-2 bg-white border border-slate-200 rounded-lg shadow-2xl overflow-hidden z-[60]">
                    <div className="max-h-[200px] overflow-y-auto">
                      <div className="p-2 hover:bg-blue-50 cursor-pointer flex items-center gap-2 border-b border-slate-50">
                        <Droplets size={12} className="text-blue-600"/>
                        <span className="text-[11px] font-bold">Sample Result goes here</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          <button className="flex items-center gap-2 bg-slate-800 text-white px-4 py-2 rounded-lg text-xs font-bold hover:bg-slate-900 transition shadow-md">
            <User size={16} />
            Login
          </button>
        </div>
      </header>

      {/* MAIN WRAPPER */}
      <div className="flex flex-1 overflow-hidden relative">
        
        {/* SIDEBAR */}
        <aside
          className={`fixed top-16 left-0 h-[calc(100vh-4rem)] w-64 bg-slate-100 shadow-2xl 
            transform transition-transform duration-300 ease-in-out z-40 border-r border-slate-300
             ${sidebarOpen ? "translate-x-0" : "-translate-x-full"}`}
        >
          <div className="p-4 overflow-y-auto h-full scrollbar-thin">
            <p className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-6 px-2">Core Operations</p>
            <div className="space-y-2">
              <div>
                <button
                  className={`flex items-center justify-between w-full p-3 rounded-xl transition text-sm font-bold
                ${openMenu === "sales" ? 'bg-white text-blue-700 shadow-sm border border-slate-200' : 'text-slate-600 hover:bg-slate-200'}`}
                  onClick={() => toggleMenu("sales")}
                >
                  <div className="flex items-center gap-3">
                    <ShoppingCart size={20} />
                    <span>Sales & Quotes</span>
                  </div>
                  {openMenu === "sales" ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                </button>
                
                {openMenu === "sales" && (
                  <div className="mt-2 ml-4 border-l-2 border-blue-200 pl-4 space-y-1">
                    <button 
                      onClick={() => toggleSubMenu("invoices")}
                      className="flex items-center justify-between w-full py-2 text-xs font-bold text-slate-500 hover:text-blue-700"
                    >
                      Invoices {openSubMenu === "invoices" ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
                    </button>
                    {openSubMenu === "invoices" && (
                       <div className="ml-2 space-y-1 pb-2">
                          <div className="p-2 text-[10px] text-slate-400 hover:bg-white rounded cursor-pointer">Drafts</div>
                          <div className="p-2 text-[10px] text-slate-400 hover:bg-white rounded cursor-pointer">Paid</div>
                       </div>
                    )}
                  </div>
                )}
              </div>

              <button className="flex items-center gap-3 w-full p-3 rounded-xl text-sm font-bold text-slate-600 hover:bg-slate-200 transition">
                <ClipboardList size={20} />
                <span>Settings</span>
              </button>

              <button className="flex items-center gap-3 w-full p-3 rounded-xl text-sm font-bold text-slate-600 hover:bg-slate-200 transition">
                <Settings size={20} />
                <span>System Config</span>
              </button>
            </div>
          </div>
        </aside>

        {/* INJECTED MAIN CONTENT AREA */}
        <main className={`flex-1 transition-all duration-300 p-8 overflow-y-auto bg-white ${sidebarOpen ? "ml-64" : "ml-0"}`}>
           <div className="max-w-5xl mx-auto">
              {children}
           </div>
        </main>
      </div>
    </div>
  );
}