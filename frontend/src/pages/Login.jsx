// src/pages/Login.jsx
import React, { useState } from "react";
import { useAuth } from "../hooks/useAuth";

function Login() {
  const { login, loading, error } = useAuth();
  const [form, setForm] = useState({ username: "", password: "" });

  const [tokens, setTokens] = useState(null); // store tokens to show them

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const result = await login(form.name, form.password);

    if (result.success) {
      setTokens({
        access: result.access,
        refresh: result.refresh,
      });
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100 p-4">
      <div className="w-full max-w-sm bg-white p-6 rounded-lg shadow">
        <h2 className="text-2xl font-semibold mb-4 text-center">
          Login to your account
        </h2>

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block font-medium mb-1">Email</label>
            <input
              type="text"
              name="text"
              placeholder="yourname"
              value={form.email}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border rounded-md focus:ring focus:ring-blue-300"
            />
          </div>

          <div className="mb-4">
            <label className="block font-medium mb-1">Password</label>
            <input
              type="password"
              name="password"
              placeholder="******"
              value={form.password}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border rounded-md focus:ring focus:ring-blue-300"
            />
          </div>

          {error && (
            <p className="text-red-600 text-sm mb-3 text-center">{error}</p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 rounded-md 
              hover:bg-blue-700 disabled:bg-gray-400"
          >
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>
         <p className="text-black">Don't have an account? <a href="/Signup" className="text-blue-700">Sign Up</a></p>

        {/* Show tokens after login */}
        {tokens && (
          <div className="mt-6 bg-gray-100 p-3 rounded-lg text-sm break-all">
            <p className="font-bold">Access Token:</p>
            <p className="mb-2">{tokens.access}</p>

            <p className="font-bold">Refresh Token:</p>
            <p>{tokens.refresh}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default Login;
