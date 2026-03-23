import { NavLink, Outlet, Navigate } from "react-router-dom";
import { LayoutDashboard, Users, FolderOpen, LayoutTemplate, Activity, Server, Settings, LogOut, FileText } from "lucide-react";
import { useAdminAuth } from "@/hooks/useAuth";

const NAV = [
  { to: "/", icon: LayoutDashboard, label: "Dashboard", exact: true },
  { to: "/users", icon: Users, label: "Users" },
  { to: "/files", icon: FolderOpen, label: "Files" },
  { to: "/templates", icon: LayoutTemplate, label: "Templates" },
  { to: "/activity", icon: Activity, label: "Activity" },
  { to: "/system", icon: Server, label: "System" },
  { to: "/settings", icon: Settings, label: "Settings" },
];

export function AdminLayout() {
  const { user, loading, logout } = useAdminAuth();

  if (loading) return <div className="h-screen flex items-center justify-center bg-gray-950 text-white">Loading...</div>;
  if (!user) return <Navigate to="/login" replace />;

  return (
    <div className="h-screen flex bg-gray-950 text-gray-100">
      {/* Sidebar */}
      <aside className="w-56 bg-gray-900 border-r border-gray-800 flex flex-col shrink-0">
        <div className="p-4 border-b border-gray-800">
          <div className="flex items-center gap-2">
            <div className="h-7 w-7 rounded bg-blue-600 flex items-center justify-center"><FileText className="h-3.5 w-3.5 text-white" /></div>
            <div>
              <div className="text-sm font-bold">Productivity Suite</div>
              <div className="text-[10px] text-gray-500">Admin Panel</div>
            </div>
          </div>
        </div>

        <nav className="flex-1 py-3 px-2 space-y-0.5">
          {NAV.map(({ to, icon: Icon, label, exact }) => (
            <NavLink key={to} to={to} end={exact}
              className={({ isActive }) => `flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors ${isActive ? "bg-blue-600/20 text-blue-400" : "text-gray-400 hover:text-gray-200 hover:bg-gray-800"}`}>
              <Icon className="h-4 w-4 shrink-0" />{label}
            </NavLink>
          ))}
        </nav>

        <div className="p-3 border-t border-gray-800">
          <div className="text-xs text-gray-500 mb-2 truncate">{user.email}</div>
          <button onClick={() => { logout(); window.location.href = "/login"; }}
            className="flex items-center gap-2 text-xs text-gray-500 hover:text-red-400 transition-colors">
            <LogOut className="h-3.5 w-3.5" /> Sign out
          </button>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 overflow-auto">
        <Outlet />
      </main>
    </div>
  );
}
