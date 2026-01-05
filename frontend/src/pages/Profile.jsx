"use client"

import { useState, useEffect } from "react"
import { User, Mail, Save, AlertCircle } from "lucide-react"
import Navbar from "../components/NavBar"
import { useAuth } from "../context/AuthContext"

export default function Profile() {
  const { user, updateProfile, loading: authLoading } = useAuth()
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    company: "",
    role: "",
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")

  useEffect(() => {
    if (user) {
      setFormData({
        name: user.name || "",
        email: user.email || "",
        company: user.company || "",
        role: user.role || "",
      })
    }
  }, [user])

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError("")
    setSuccess("")
    setLoading(true)

    try {
      await updateProfile(formData)
      setSuccess("Profile updated successfully!")
      setTimeout(() => setSuccess(""), 3000)
    } catch (err) {
      setError(err.response?.data?.message || "Failed to update profile")
    } finally {
      setLoading(false)
    }
  }

  if (authLoading) {
    return (
      <div className="min-h-screen bg-surface">
        <Navbar />
        <div className="flex items-center justify-center min-h-[calc(100vh-64px)]">
          <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-surface">
      <Navbar />

      <main className="max-w-2xl mx-auto px-4 py-16 page-transition">
        <div className="bg-surface-light rounded-lg p-8 border border-gray-700">
          <div className="flex items-center space-x-4 mb-8">
            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary to-accent flex items-center justify-center">
              <User size={32} className="text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold">{user?.name || "User"}</h1>
              <p className="text-gray-400">{user?.email || "No email"}</p>
            </div>
          </div>

          {error && (
            <div className="bg-red-900/20 border border-red-700/50 rounded-lg p-4 mb-6 flex items-start space-x-3">
              <AlertCircle size={20} className="text-danger flex-shrink-0 mt-0.5" />
              <p className="text-red-200">{error}</p>
            </div>
          )}

          {success && (
            <div className="bg-green-900/20 border border-green-700/50 rounded-lg p-4 mb-6 flex items-start space-x-3">
              <User size={20} className="text-success flex-shrink-0 mt-0.5" />
              <p className="text-green-200">{success}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Full Name</label>
              <div className="relative">
                <User size={18} className="absolute left-3 top-3 text-gray-500" />
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  className="w-full bg-surface border border-gray-600 rounded-lg pl-10 pr-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Email</label>
              <div className="relative">
                <Mail size={18} className="absolute left-3 top-3 text-gray-500" />
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  disabled
                  className="w-full bg-surface border border-gray-600 rounded-lg pl-10 pr-4 py-2 text-gray-500 placeholder-gray-500 focus:outline-none transition-colors cursor-not-allowed"
                />
              </div>
              <p className="text-xs text-gray-500 mt-1">Email cannot be changed</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Company</label>
              <input
                type="text"
                name="company"
                value={formData.company}
                onChange={handleChange}
                placeholder="Your company name"
                className="w-full bg-surface border border-gray-600 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">Role</label>
              <select
                name="role"
                value={formData.role}
                onChange={handleChange}
                className="w-full bg-surface border border-gray-600 rounded-lg px-4 py-2 text-white placeholder-gray-500 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors"
              >
                <option value="">Select a role</option>
                <option value="admin">Admin</option>
                <option value="analyst">Analyst</option>
                <option value="manager">Manager</option>
                <option value="viewer">Viewer</option>
              </select>
            </div>

            <div className="pt-4 border-t border-gray-600">
              <button
                type="submit"
                disabled={loading}
                className="flex items-center space-x-2 bg-primary hover:bg-blue-600 disabled:bg-gray-600 text-white font-semibold py-2 px-6 rounded-lg transition-colors"
              >
                <Save size={18} />
                <span>{loading ? "Saving..." : "Save Changes"}</span>
              </button>
            </div>
          </form>

          {/* Additional Info */}
          <div className="mt-8 pt-8 border-t border-gray-600">
            <h3 className="text-lg font-semibold mb-4">Account Information</h3>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-400">Member Since</span>
                <span className="text-gray-300">
                  {user?.createdAt ? new Date(user.createdAt).toLocaleDateString() : "Unknown"}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Account Status</span>
                <span className="text-success font-semibold">Active</span>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
