"use client"
import { Link } from "react-router-dom"
import { BarChart3, TrendingUp, AlertCircle, Zap } from "lucide-react"
import Navbar from "../components/NavBar"
import { useAuth } from "../context/AuthContext"

export default function Home() {
  const { isAuthenticated } = useAuth()

  return (
    <div className="min-h-screen bg-gradient-to-br from-surface via-surface to-surface-light">
      <Navbar />

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 py-20 text-center page-transition">
        <h1 className="text-5xl md:text-6xl font-bold mb-6 gradient-text">Sentiment Analysis Dashboard</h1>
        <p className="text-xl text-gray-400 mb-8 max-w-2xl mx-auto">
          Real-time feedback analysis, sentiment tracking, and AI-powered insights to drive better business decisions
        </p>

        {isAuthenticated ? (
          <Link
            to="/dashboard"
            className="inline-block bg-primary hover:bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold transition-colors"
          >
            Go to Dashboard
          </Link>
        ) : (
          <div className="space-x-4">
            <Link
              to="/login"
              className="inline-block bg-primary hover:bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold transition-colors"
            >
              Login
            </Link>
            <Link
              to="/signup"
              className="inline-block border border-primary text-primary hover:bg-primary hover:text-white px-8 py-3 rounded-lg font-semibold transition-colors"
            >
              Sign Up
            </Link>
          </div>
        )}
      </section>

      {/* Features Section */}
      <section className="max-w-7xl mx-auto px-4 py-16">
        <h2 className="text-3xl font-bold text-center mb-12">Key Features</h2>
        <div className="grid md:grid-cols-3 gap-8">
          <div className="bg-surface-light rounded-lg p-8 border border-gray-700 card-hover">
            <TrendingUp size={32} className="text-primary mb-4" />
            <h3 className="text-xl font-semibold mb-3">Sentiment Trends</h3>
            <p className="text-gray-400">
              Track sentiment changes over time with beautiful visualization charts and detailed analytics
            </p>
          </div>

          <div className="bg-surface-light rounded-lg p-8 border border-gray-700 card-hover">
            <BarChart3 size={32} className="text-accent mb-4" />
            <h3 className="text-xl font-semibold mb-3">Topic Analysis</h3>
            <p className="text-gray-400">
              Identify trending topics and understand what customers are talking about most
            </p>
          </div>

          <div className="bg-surface-light rounded-lg p-8 border border-gray-700 card-hover">
            <AlertCircle size={32} className="text-danger mb-4" />
            <h3 className="text-xl font-semibold mb-3">Smart Alerts</h3>
            <p className="text-gray-400">Get notified immediately when critical feedback emerges or sentiment drops</p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="max-w-4xl mx-auto px-4 py-16 text-center">
        <div className="bg-surface-light rounded-lg p-12 border border-gray-700">
          <Zap size={40} className="text-warning mx-auto mb-4" />
          <h2 className="text-3xl font-bold mb-4">Ready to Get Started?</h2>
          <p className="text-gray-400 mb-8">
            Join thousands of companies using SentimentHub to understand their customers better
          </p>
          {!isAuthenticated && (
            <Link
              to="/signup"
              className="inline-block bg-primary hover:bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold transition-colors"
            >
              Create Free Account
            </Link>
          )}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-700 mt-20 py-8 text-center text-gray-400">
        <p>&copy; 2025 SentimentHub. All rights reserved.</p>
      </footer>
    </div>
  )
}
