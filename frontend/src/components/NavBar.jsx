"use client"

import { useState, useMemo } from "react"
import { Link, useNavigate, useLocation } from "react-router-dom"
import { Menu, X, LogOut, BarChart3, User, Users } from "lucide-react"
import { useAuth } from "../context/AuthContext"

export default function NavBar() {
  const { user, logout, isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [isOpen, setIsOpen] = useState(false)

  const handleLogout = () => {
    logout()
    navigate("/")
  }

  const isActive = (path) => location.pathname === path

  // Check if user is admin - use useMemo to ensure reactivity
  const isAdmin = useMemo(() => {
    if (!user) return false
    const role = user.role || (user.user && user.user.role)
    console.log('NavBar - user:', user)
    console.log('NavBar - role:', role, 'isAdmin:', role === 'admin')
    return role === 'admin'
  }, [user])

  // Debug: Log user data to help troubleshoot
  console.log('NavBar Render - user:', user?.username, 'isAdmin:', isAdmin, 'isAuthenticated:', isAuthenticated)

  // TEMP: Force isAdmin for testing
  const debugIsAdmin = true // Change this to false to test non-admin view

  if (location.pathname === "/" && !isAuthenticated) {
    return null
  }

  return (
    <nav className="bg-surface-light border-b border-gray-700 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2 text-xl font-bold gradient-text">
            <BarChart3 size={28} className="text-primary" />
            <span>SentimentHub</span>
          </Link>

          {/* Desktop Menu */}
          <div className="hidden md:flex items-center space-x-8">
            {isAuthenticated && (
              <>
                <Link
                  to="/dashboard"
                  className={`flex items-center space-x-1 transition-colors ${
                    isActive("/dashboard") ? "text-primary" : "text-gray-300 hover:text-primary"
                  }`}
                >
                  <BarChart3 size={18} />
                  <span>Dashboard</span>
                </Link>
                {(isAdmin || debugIsAdmin) && (
                  <Link
                    to="/users"
                    className={`flex items-center space-x-1 transition-colors ${
                      isActive("/users") ? "text-primary" : "text-gray-300 hover:text-primary"
                    }`}
                  >
                    <Users size={18} />
                    <span>Users</span>
                  </Link>
                )}
                <Link
                  to="/profile"
                  className={`flex items-center space-x-1 transition-colors ${
                    isActive("/profile") ? "text-primary" : "text-gray-300 hover:text-primary"
                  }`}
                >
                  <User size={18} />
                  <span>Profile</span>
                </Link>
              </>
            )}
          </div>

          {/* Auth Buttons */}
          <div className="hidden md:flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                <span className="text-sm text-gray-400">Welcome, {user?.username || user?.email || user?.first_name}</span>
                <button
                  onClick={handleLogout}
                  className="flex items-center space-x-2 bg-danger hover:bg-red-600 text-white px-4 py-2 rounded-lg transition-colors"
                >
                  <LogOut size={18} />
                  <span>Logout</span>
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="text-primary hover:text-blue-400 transition-colors">
                  Login
                </Link>
                <Link
                  to="/signup"
                  className="bg-primary hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition-colors"
                >
                  Sign Up
                </Link>
              </>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="md:hidden text-gray-300 hover:text-primary transition-colors"
          >
            {isOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Mobile Menu */}
        {isOpen && (
          <div className="md:hidden pb-4 border-t border-gray-700 space-y-4 pt-4">
            {isAuthenticated && (
              <>
                <Link
                  to="/dashboard"
                  className="block text-gray-300 hover:text-primary transition-colors py-2"
                  onClick={() => setIsOpen(false)}
                >
                  Dashboard
                </Link>
                {(isAdmin || debugIsAdmin) && (
                  <Link
                    to="/users"
                    className="block text-gray-300 hover:text-primary transition-colors py-2"
                    onClick={() => setIsOpen(false)}
                  >
                    Users
                  </Link>
                )}
                <Link
                  to="/profile"
                  className="block text-gray-300 hover:text-primary transition-colors py-2"
                  onClick={() => setIsOpen(false)}
                >
                  Profile
                </Link>
              </>
            )}
            {isAuthenticated ? (
              <button
                onClick={() => {
                  handleLogout()
                  setIsOpen(false)
                }}
                className="w-full text-left text-danger hover:text-red-400 transition-colors py-2"
              >
                Logout
              </button>
            ) : (
              <>
                <Link
                  to="/login"
                  className="block text-primary hover:text-blue-400 transition-colors py-2"
                  onClick={() => setIsOpen(false)}
                >
                  Login
                </Link>
                <Link
                  to="/signup"
                  className="block bg-primary hover:bg-blue-600 text-white px-4 py-2 rounded-lg transition-colors"
                  onClick={() => setIsOpen(false)}
                >
                  Sign Up
                </Link>
              </>
            )}
          </div>
        )}
      </div>
    </nav>
  )
}
