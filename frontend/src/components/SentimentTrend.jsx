import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts"
import { TrendingUp } from "lucide-react"

export default function SentimentTrend({ data }) {
  return (
    <div className="bg-surface-light rounded-lg p-6 border border-gray-700">
      <div className="flex items-center space-x-2 mb-6">
        <TrendingUp size={24} className="text-primary" />
        <h3 className="text-xl font-semibold">Sentiment Trends (7 Days)</h3>
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis dataKey="date" stroke="#9CA3AF" />
          <YAxis stroke="#9CA3AF" />
          <Tooltip
            contentStyle={{ backgroundColor: "#1F2937", border: "1px solid #374151" }}
            labelStyle={{ color: "#E5E7EB" }}
          />
          <Legend />
          <Line type="monotone" dataKey="positive" stroke="#10B981" strokeWidth={2} dot={{ fill: "#10B981" }} />
          <Line type="monotone" dataKey="neutral" stroke="#6B7280" strokeWidth={2} dot={{ fill: "#6B7280" }} />
          <Line type="monotone" dataKey="negative" stroke="#EF4444" strokeWidth={2} dot={{ fill: "#EF4444" }} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
