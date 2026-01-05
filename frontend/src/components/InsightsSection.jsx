import { Lightbulb } from "lucide-react"

export default function InsightsSection({ insights }) {
  return (
    <div className="bg-surface-light rounded-lg p-6 border border-gray-700">
      <div className="flex items-center space-x-2 mb-6">
        <Lightbulb size={24} className="text-warning" />
        <h3 className="text-xl font-semibold">AI-Generated Insights</h3>
      </div>

      {insights.length === 0 ? (
        <p className="text-gray-400">No insights available yet.</p>
      ) : (
        <ul className="space-y-4">
          {insights.map((insight, index) => (
            <li key={index} className="flex items-start space-x-4 pb-4 border-b border-gray-600 last:border-b-0">
              <span className="text-primary font-bold text-lg flex-shrink-0">{index + 1}.</span>
              <p className="text-gray-300">{insight}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
