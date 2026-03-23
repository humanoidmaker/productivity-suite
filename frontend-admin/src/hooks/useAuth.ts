import { useState, useEffect, useCallback } from "react";
import { getMe } from "@/api/adminApi";
import type { AdminUser } from "@/types/admin";

export function useAdminAuth() {
  const [user, setUser] = useState<AdminUser | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    const token = localStorage.getItem("productivity_access_token");
    if (!token) { setUser(null); setLoading(false); return; }
    try {
      const me = await getMe();
      if (me.role !== "admin" && me.role !== "superadmin") { setUser(null); }
      else setUser(me);
    } catch { setUser(null); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  const logout = useCallback(() => {
    localStorage.removeItem("productivity_access_token");
    localStorage.removeItem("productivity_refresh_token");
    setUser(null);
  }, []);

  return { user, loading, refresh, logout };
}
