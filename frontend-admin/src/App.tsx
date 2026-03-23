import { Routes, Route, Navigate } from "react-router-dom";
import { AdminLayout } from "./components/AdminLayout";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import UserManagement from "./pages/UserManagement";
import ActivityLog from "./pages/ActivityLog";
import SystemHealth from "./pages/SystemHealth";
import Settings from "./pages/Settings";

function Placeholder({ name }: { name: string }) {
  return (
    <div className="flex items-center justify-center h-full">
      <div className="text-center">
        <h1 className="text-xl font-bold text-white">{name}</h1>
        <p className="text-gray-500 text-sm mt-1">Coming soon</p>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route element={<AdminLayout />}>
        <Route index element={<Dashboard />} />
        <Route path="/users" element={<UserManagement />} />
        <Route path="/files" element={<Placeholder name="File Explorer" />} />
        <Route path="/templates" element={<Placeholder name="Template Management" />} />
        <Route path="/activity" element={<ActivityLog />} />
        <Route path="/system" element={<SystemHealth />} />
        <Route path="/settings" element={<Settings />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
