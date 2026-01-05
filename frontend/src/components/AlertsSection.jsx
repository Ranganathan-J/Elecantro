"use client"

import React from "react"
import { AlertCircle, AlertTriangle, Info, Trash2 } from "lucide-react"

export default function AlertsSection({ alerts }) {
  const [dismissedAlerts, setDismissedAlerts] = React.useState([])

  const dismissAlert = (id) => {
    setDismissedAlerts([...dismissedAlerts, id])
  }

  const activeAlerts = alerts.filter((alert) => !dismissedAlerts.includes(alert.id))

  const getAlertIcon = (type) => {
    switch (type) {
      case "critical":
        return <AlertCircle size={20} className="text-danger" />
      case "warning":
        return <AlertTriangle size={20} className="text-warning" />
      default:
        return <Info size={20} className="text-primary" />
    }
  }

  const getAlertBgColor = (type) => {
    switch (type) {
      case "critical":
        return "bg-red-900/20 border-red-700/50"
      case "warning":
        return "bg-yellow-900/20 border-yellow-700/50"
      default:
        return "bg-blue-900/20 border-blue-700/50"
    }
  }

  return (
    <div className="bg-surface-light rounded-lg p-6 border border-gray-700">
      <div className="flex items-center space-x-2 mb-6">
        <AlertCircle size={24} className="text-danger" />
        <h3 className="text-xl font-semibold">Critical Alerts</h3>
        <span className="ml-auto bg-danger text-white text-xs px-3 py-1 rounded-full">{activeAlerts.length}</span>
      </div>

      {activeAlerts.length === 0 ? (
        <p className="text-gray-400 text-center py-8">All clear! No critical alerts.</p>
      ) : (
        <div className="space-y-3">
          {activeAlerts.map((alert) => (
            <div
              key={alert.id}
              className={`rounded-lg p-4 border ${getAlertBgColor(alert.type)} flex justify-between items-start`}
            >
              <div className="flex space-x-4 flex-1">
                <div className="mt-1">{getAlertIcon(alert.type)}</div>
                <div className="flex-1">
                  <h4 className="font-semibold text-white">{alert.title}</h4>
                  <p className="text-gray-300 text-sm mt-1">{alert.message}</p>
                  <p className="text-gray-500 text-xs mt-2">{new Date(alert.timestamp).toLocaleString()}</p>
                </div>
              </div>
              <button
                onClick={() => dismissAlert(alert.id)}
                className="text-gray-400 hover:text-gray-200 transition-colors ml-4"
              >
                <Trash2 size={18} />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
