// src/hooks/useAuth.js
import { useState } from "react";
import api from "../services/api";

export function useAuth() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const login = async (username, password) => {
    setLoading(true);
    setError(null);

    try {
      const res = await api.post("/api/users/login/", { username, password });

      return {
        success: true,
        user: res.data.user,
        access: res.data.tokens.access,
        refresh: res.data.tokens.refresh,
      };
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed");
      return { success: false };
    } finally {
      setLoading(false);
    }
  };

  return { login, loading, error };
}
