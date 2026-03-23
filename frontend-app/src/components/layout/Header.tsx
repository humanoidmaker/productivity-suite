import { useState } from "react";
import { Search, Plus, LogOut, User as UserIcon } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "@/hooks/useAuth";
import { createDocument } from "@/api/documentsApi";

export function Header() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState("");
  const [showNewMenu, setShowNewMenu] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) navigate(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
  };

  const handleNewDocument = async () => {
    setShowNewMenu(false);
    const doc = await createDocument({});
    navigate(`/document/${doc.id}`);
  };

  return (
    <header className="h-14 bg-white border-b border-gray-200 flex items-center gap-4 px-4 shrink-0">
      {/* Search */}
      <form onSubmit={handleSearch} className="flex-1 max-w-xl">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            placeholder="Search files..."
            className="w-full h-9 pl-10 pr-4 rounded-lg border border-gray-200 bg-gray-50 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          />
        </div>
      </form>

      {/* New button */}
      <div className="relative">
        <button
          onClick={() => setShowNewMenu(v => !v)}
          className="flex items-center gap-1.5 h-9 px-4 bg-primary-600 text-white text-sm font-medium rounded-lg hover:bg-primary-700 transition-colors"
        >
          <Plus className="h-4 w-4" /> New
        </button>
        {showNewMenu && (
          <div className="absolute right-0 top-full mt-1 w-52 bg-white border border-gray-200 rounded-lg shadow-xl py-1 z-50">
            <button onClick={handleNewDocument} className="w-full text-left px-4 py-2 text-sm hover:bg-gray-50 flex items-center gap-2">
              <div className="w-5 h-5 rounded bg-doc/10 flex items-center justify-center"><span className="text-doc text-[10px] font-bold">D</span></div>
              New Document
            </button>
            <button onClick={() => { setShowNewMenu(false); navigate("/spreadsheet/new"); }} className="w-full text-left px-4 py-2 text-sm hover:bg-gray-50 flex items-center gap-2">
              <div className="w-5 h-5 rounded bg-sheet/10 flex items-center justify-center"><span className="text-sheet text-[10px] font-bold">S</span></div>
              New Spreadsheet
            </button>
            <button onClick={() => { setShowNewMenu(false); navigate("/presentation/new"); }} className="w-full text-left px-4 py-2 text-sm hover:bg-gray-50 flex items-center gap-2">
              <div className="w-5 h-5 rounded bg-pres/10 flex items-center justify-center"><span className="text-pres text-[10px] font-bold">P</span></div>
              New Presentation
            </button>
            <hr className="my-1 border-gray-100" />
            <button onClick={() => setShowNewMenu(false)} className="w-full text-left px-4 py-2 text-sm hover:bg-gray-50 text-gray-500">
              New Folder
            </button>
          </div>
        )}
      </div>

      {/* User menu */}
      <div className="relative">
        <button onClick={() => setShowUserMenu(v => !v)} className="h-8 w-8 rounded-full bg-primary-100 flex items-center justify-center text-primary-700 font-medium text-sm">
          {user?.name?.[0]?.toUpperCase() || <UserIcon className="h-4 w-4" />}
        </button>
        {showUserMenu && (
          <div className="absolute right-0 top-full mt-1 w-48 bg-white border border-gray-200 rounded-lg shadow-xl py-1 z-50">
            <div className="px-4 py-2 border-b border-gray-100">
              <p className="text-sm font-medium truncate">{user?.name}</p>
              <p className="text-xs text-gray-500 truncate">{user?.email}</p>
            </div>
            <button onClick={() => { setShowUserMenu(false); navigate("/settings"); }} className="w-full text-left px-4 py-2 text-sm hover:bg-gray-50">Settings</button>
            <button onClick={() => { setShowUserMenu(false); logout(); navigate("/login"); }} className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center gap-2">
              <LogOut className="h-3.5 w-3.5" /> Sign out
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
