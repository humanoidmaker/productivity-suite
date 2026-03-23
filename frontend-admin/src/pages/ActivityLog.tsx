import { useState, useEffect } from "react";
import { Loader2 } from "lucide-react";
import { getActivityLog } from "@/api/adminApi";
import type { ActivityEntry } from "@/types/admin";

export default function ActivityLog() {
  const [entries, setEntries] = useState<ActivityEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getActivityLog(0, 100).then(setEntries).catch(() => {}).finally(() => setLoading(false));
  }, []);

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-2xl font-bold text-white">Activity Log</h1>
      {loading ? (
        <div className="flex justify-center py-12"><Loader2 className="h-6 w-6 animate-spin text-gray-500" /></div>
      ) : (
        <div className="border border-gray-800 rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead><tr className="bg-gray-900/50">
              <th className="text-left px-4 py-3 text-xs font-medium text-gray-500">Time</th>
              <th className="text-left px-4 py-3 text-xs font-medium text-gray-500">Action</th>
              <th className="text-left px-4 py-3 text-xs font-medium text-gray-500">File Type</th>
              <th className="text-left px-4 py-3 text-xs font-medium text-gray-500">IP</th>
            </tr></thead>
            <tbody className="divide-y divide-gray-800/50">
              {entries.map(e => (
                <tr key={e.id}>
                  <td className="px-4 py-2.5 text-gray-400 text-xs">{new Date(e.created_at).toLocaleString()}</td>
                  <td className="px-4 py-2.5 text-gray-300">{e.action}</td>
                  <td className="px-4 py-2.5 text-gray-400">{e.file_type || "—"}</td>
                  <td className="px-4 py-2.5 text-gray-500 font-mono text-xs">{e.ip_address || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
