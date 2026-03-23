import { useState, useEffect } from "react";
import { Search, Plus, Loader2, Shield, ShieldOff } from "lucide-react";
import { listUsers, updateUser, createUser } from "@/api/adminApi";
import { DataTable } from "@/components/DataTable";
import type { AdminUser } from "@/types/admin";

export default function UserManagement() {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [newUser, setNewUser] = useState({ email: "", name: "", password: "", role: "user" });

  const load = () => {
    setLoading(true);
    listUsers(page, 20, search || undefined)
      .then(res => { setUsers(res.items); setTotal(res.total); })
      .catch(() => {})
      .finally(() => setLoading(false));
  };

  useEffect(load, [page, search]);

  const handleToggleActive = async (user: AdminUser) => {
    await updateUser(user.id, { is_active: !user.is_active });
    load();
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    await createUser(newUser);
    setShowCreate(false);
    setNewUser({ email: "", name: "", password: "", role: "user" });
    load();
  };

  const columns = [
    { key: "name", label: "Name", render: (u: AdminUser) => (
      <div>
        <div className="font-medium text-white">{u.name}</div>
        <div className="text-xs text-gray-500">{u.email}</div>
      </div>
    )},
    { key: "role", label: "Role", render: (u: AdminUser) => (
      <span className={`px-2 py-0.5 rounded text-[10px] font-medium ${u.role === "admin" || u.role === "superadmin" ? "bg-blue-500/20 text-blue-400" : "bg-gray-800 text-gray-400"}`}>
        {u.role}
      </span>
    )},
    { key: "storage", label: "Storage", render: (u: AdminUser) => `${Math.round(u.storage_used / 1024 / 1024)}/${Math.round(u.storage_quota / 1024 / 1024)} MB` },
    { key: "is_active", label: "Status", render: (u: AdminUser) => (
      <button onClick={() => handleToggleActive(u)} className={`text-xs ${u.is_active ? "text-green-400" : "text-red-400"}`}>
        {u.is_active ? "Active" : "Disabled"}
      </button>
    )},
    { key: "created_at", label: "Joined", render: (u: AdminUser) => new Date(u.created_at).toLocaleDateString() },
  ];

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">Users</h1>
        <button onClick={() => setShowCreate(true)} className="flex items-center gap-1.5 px-4 h-9 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700">
          <Plus className="h-4 w-4" /> Add User
        </button>
      </div>

      {/* Search */}
      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500" />
        <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search users..."
          className="w-full h-9 pl-10 pr-4 rounded-lg bg-gray-900 border border-gray-800 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500" />
      </div>

      {loading ? (
        <div className="flex justify-center py-12"><Loader2 className="h-6 w-6 animate-spin text-gray-500" /></div>
      ) : (
        <DataTable columns={columns} data={users} keyField="id" />
      )}

      <div className="flex items-center justify-between text-xs text-gray-500">
        <span>{total} users total</span>
        <div className="flex gap-2">
          <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page <= 1} className="px-3 py-1 rounded bg-gray-800 disabled:opacity-50">Prev</button>
          <span className="px-3 py-1">Page {page}</span>
          <button onClick={() => setPage(p => p + 1)} disabled={users.length < 20} className="px-3 py-1 rounded bg-gray-800 disabled:opacity-50">Next</button>
        </div>
      </div>

      {/* Create dialog */}
      {showCreate && (
        <div className="fixed inset-0 z-50 bg-black/70 flex items-center justify-center p-4">
          <form onSubmit={handleCreate} className="bg-gray-900 border border-gray-800 rounded-xl p-6 w-full max-w-sm space-y-4">
            <h2 className="text-lg font-bold text-white">Create User</h2>
            <input value={newUser.name} onChange={e => setNewUser(p => ({ ...p, name: e.target.value }))} placeholder="Name" required
              className="w-full h-9 px-3 rounded-lg bg-gray-800 border border-gray-700 text-sm text-white" />
            <input type="email" value={newUser.email} onChange={e => setNewUser(p => ({ ...p, email: e.target.value }))} placeholder="Email" required
              className="w-full h-9 px-3 rounded-lg bg-gray-800 border border-gray-700 text-sm text-white" />
            <input type="password" value={newUser.password} onChange={e => setNewUser(p => ({ ...p, password: e.target.value }))} placeholder="Password" required minLength={8}
              className="w-full h-9 px-3 rounded-lg bg-gray-800 border border-gray-700 text-sm text-white" />
            <select value={newUser.role} onChange={e => setNewUser(p => ({ ...p, role: e.target.value }))}
              className="w-full h-9 px-3 rounded-lg bg-gray-800 border border-gray-700 text-sm text-white">
              <option value="user">User</option>
              <option value="admin">Admin</option>
            </select>
            <div className="flex gap-3">
              <button type="button" onClick={() => setShowCreate(false)} className="flex-1 h-9 bg-gray-800 text-gray-300 text-sm rounded-lg">Cancel</button>
              <button type="submit" className="flex-1 h-9 bg-blue-600 text-white text-sm rounded-lg">Create</button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
