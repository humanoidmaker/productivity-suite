import { useState, useEffect } from "react";
import { Loader2 } from "lucide-react";
import { getSettings } from "@/api/adminApi";
import type { SystemSettings } from "@/types/admin";

export default function Settings() {
  const [settings, setSettings] = useState<SystemSettings | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getSettings().then(setSettings).catch(() => {}).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="flex items-center justify-center h-full"><Loader2 className="h-6 w-6 animate-spin text-gray-500" /></div>;

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-white">Settings</h1>

      {settings && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {Object.entries(settings).map(([key, value]) => (
            <div key={key} className="bg-gray-900 border border-gray-800 rounded-xl p-4">
              <label className="text-xs font-medium text-gray-500 uppercase tracking-wider">
                {key.replace(/_/g, " ")}
              </label>
              <div className="mt-1">
                {typeof value === "boolean" ? (
                  <div className={`text-sm font-medium ${value ? "text-green-400" : "text-red-400"}`}>
                    {value ? "Enabled" : "Disabled"}
                  </div>
                ) : (
                  <div className="text-lg font-bold text-white">{value}</div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      <p className="text-xs text-gray-600">Settings are configured via environment variables. Restart the backend to apply changes.</p>
    </div>
  );
}
