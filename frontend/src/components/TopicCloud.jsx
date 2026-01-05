import { Cloud } from "lucide-react"

export default function TopicCloud({ topics }) {
  if (!topics || topics.length === 0) {
    return (
      <div className="bg-surface-light rounded-lg p-6 border border-gray-700">
        <div className="flex items-center space-x-2 mb-6">
          <Cloud size={24} className="text-primary" />
          <h3 className="text-xl font-semibold">Top Topics</h3>
        </div>
        <p className="text-gray-400">No topics found</p>
      </div>
    )
  }

  const maxMentions = Math.max(...topics.map((t) => t.mentions))

  return (
    <div className="bg-surface-light rounded-lg p-6 border border-gray-700">
      <div className="flex items-center space-x-2 mb-6">
        <Cloud size={24} className="text-primary" />
        <h3 className="text-xl font-semibold">Top Topics</h3>
      </div>

      <div className="flex flex-wrap gap-4">
        {topics.map((topic, index) => {
          const sizeRatio = topic.mentions / maxMentions
          const sentimentColor =
            topic.sentiment > 70 ? "text-success" : topic.sentiment > 40 ? "text-warning" : "text-danger"
          const size = Math.floor(sizeRatio * 4) + 1

          return (
            <div key={index} className="text-center">
              <div
                className={`text-${size * 4}xl font-bold ${sentimentColor} mb-2 cursor-pointer hover:scale-110 transition-transform`}
              >
                {topic.name}
              </div>
              <p className="text-xs text-gray-400">{topic.mentions} mentions</p>
            </div>
          )
        })}
      </div>
    </div>
  )
}
