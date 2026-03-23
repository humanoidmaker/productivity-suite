import { useState, useEffect } from "react";
import { Users, FileText, Table2, Presentation, HardDrive, Radio, Loader2 } from "lucide-react";
import { getDashboardStats } from "@/api/adminApi";
import { StatsCard } from "@/components/StatsCard";
import type { DashboardStats } from "@/types/admin";

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`;
  if (bytes < 1073741824) return `${(bytes / 1048576).toFixed(1)} MB`;
  return `${(bytes / 1073741824).toFixed(1)} GB`;
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getDashboardStats().then(setStats).catch(() => {}).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="flex items-center justify-center h-full"><Loader2 className="h-6 w-6 animate-spin text-gray-500" /></div>;

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-white">Dashboard</h1>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatsCard label="Total Users" value={stats?.total_users ?? 0} icon={<Users className="h-4 w-4" />} color="blue" trend={`${stats?.active_users ?? 0} active`} />
        <StatsCard label="Documents" value={stats?.total_documents ?? 0} icon={<FileText className="h-4 w-4" />} color="blue" />
        <StatsCard label="Spreadsheets" value={stats?.total_spreadsheets ?? 0} icon={<Table2 className="h-4 w-4" />} color="green" />
        <StatsCard label="Presentations" value={stats?.total_presentations ?? 0} icon={<Presentation className="h-4 w-4" />} color="orange" />
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
        <StatsCard label="Total Storage" value={formatBytes(stats?.total_storage_bytes ?? 0)} icon={<HardDrive className="h-4 w-4" />} color="purple" />
        <StatsCard label="Active Collaborations" value={stats?.active_collaborations ?? 0} icon={<Radio className="h-4 w-4" />} color="green" />
        <StatsCard label="Total Files" value={(stats?.total_documents ?? 0) + (stats?.total_spreadsheets ?? 0) + (stats?.total_presentations ?? 0)} icon={<FileText className="h-4 w-4" />} color="blue" />
      </div>
    </div>
  );
}
