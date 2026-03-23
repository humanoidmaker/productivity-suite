import { NavLink } from "react-router-dom";
import { Home, FolderOpen, Users, Star, Trash2, LayoutTemplate, Settings, FileText } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";

const NAV_ITEMS = [
  { to: "/", icon: Home, label: "Home", exact: true },
  { to: "/files", icon: FolderOpen, label: "My Files" },
  { to: "/shared", icon: Users, label: "Shared with Me" },
  { to: "/starred", icon: Star, label: "Starred" },
  { to: "/trash", icon: Trash2, label: "Trash" },
  { to: "/templates", icon: LayoutTemplate, label: "Templates" },
];

export function Sidebar() {
  const { user } = useAuth();

  const usedPct = user ? Math.round((user.storage_used / user.storage_quota) * 100) : 0;
  const usedMB = user ? Math.round(user.storage_used / 1024 / 1024) : 0;
  const quotaMB = user ? Math.round(user.storage_quota / 1024 / 1024) : 0;

  return (
    <aside className="w-60 h-full bg-gray-50 border-r border-gray-200 flex flex-col shrink-0">
      {/* Logo */}
      <div className="p-4 border-b border-gray-200">
        <NavLink to="/" className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-lg bg-primary-600 flex items-center justify-center">
            <FileText className="h-4 w-4 text-white" />
          </div>
          <span className="font-bold text-lg text-gray-900">Productivity Suite</span>
        </NavLink>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-3 px-3 space-y-0.5 overflow-y-auto">
        {NAV_ITEMS.map(({ to, icon: Icon, label, exact }) => (
          <NavLink
            key={to}
            to={to}
            end={exact}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                isActive ? "bg-primary-100 text-primary-700" : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
              }`
            }
          >
            <Icon className="h-4 w-4 shrink-0" />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* Storage meter */}
      {user && (
        <div className="p-4 border-t border-gray-200">
          <div className="text-xs text-gray-500 mb-1.5">{usedMB} MB of {quotaMB} MB used</div>
          <div className="h-1.5 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-primary-600 rounded-full transition-all"
              style={{ width: `${Math.min(100, usedPct)}%` }}
            />
          </div>
          <NavLink to="/settings" className="flex items-center gap-1 mt-3 text-xs text-gray-500 hover:text-gray-700">
            <Settings className="h-3 w-3" /> Settings
          </NavLink>
        </div>
      )}
    </aside>
  );
}
