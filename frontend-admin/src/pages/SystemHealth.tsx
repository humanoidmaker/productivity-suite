import { useState, useEffect } from "react";
import { CheckCircle, XCircle, Loader2, RefreshCw } from "lucide-react";
import { getSystemHealth } from "@/api/adminApi";
import type { SystemHealth as SystemHealthType } from "@/types/admin";

export default function SystemHealth() {
  const [health, setHealth] = useState<SystemHealthType | null>(null);
  const [loading, setLoading] = useState(true);

  const load = () => {
    setLoading(true);
    getSystemHealth().then(setHealth).catch(() => {}).finally(() => setLoading(false));
  };

  useEffect(load, []);

  const StatusBadge = ({ ok }: { ok: boolean }) => ok
    ? <div className="flex items-center gap-1.5 text-green-400 text-sm"><CheckCircle className="h-4 w-4" /> Healthy</div>
    : <div className="flex items-center gap-1.5 text-red-400 text-sm"><XCircle className="h-4 w-4" /> Down</div>;

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">System Health</h1>
        <button onClick={load} className="flex items-center gap-1.5 px-3 h-8 text-sm text-gray-400 hover:text-white border border-gray-800 rounded-lg">
          <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} /> Refresh
        </button>
      </div>

      {health && (
        <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
          {[
            { name: "PostgreSQL", ok: health.postgres },
            { name: "Redis", ok: health.redis },
            { name: "MinIO Storage", ok: health.minio },
          ].map(svc => (
            <div key={svc.name} className="bg-gray-900 border border-gray-800 rounded-xl p-5">
              <div className="text-sm font-medium text-gray-300 mb-2">{svc.name}</div>
              <StatusBadge ok={svc.ok} />
            </div>
          ))}

          <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
            <div className="text-sm font-medium text-gray-300 mb-2">Celery Workers</div>
            <div className="text-2xl font-bold text-white">{health.celery_workers}</div>
          </div>

          <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
            <div className="text-sm font-medium text-gray-300 mb-2">WebSocket Connections</div>
            <div className="text-2xl font-bold text-white">{health.websocket_connections}</div>
          </div>

          <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
            <div className="text-sm font-medium text-gray-300 mb-2">Active Sessions</div>
            <div className="text-2xl font-bold text-white">{health.active_sessions}</div>
          </div>
        </div>
      )}
    </div>
  );
}
