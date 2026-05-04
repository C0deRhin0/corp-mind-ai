import { useState } from 'react'

function SourcePanel({ sources }) {
  const [expandedIndex, setExpandedIndex] = useState(null)

  if (!sources) {
    return (
      <div className="p-4 text-gray-400 text-center">
        Ask a question to see sources here
      </div>
    )
  }

  // Helper to remove file extension
  const getNameWithoutExtension = (filename) => {
    return filename.replace(/\.(pdf|docx|txt|md|markdown)$/i, '')
  }

  const getConfidenceColor = (confidence) => {
    if (confidence >= 90) return 'bg-green-500'
    if (confidence >= 60) return 'bg-amber-500'
    return 'bg-orange-500'
  }

  const toggleExpand = (index) => {
    setExpandedIndex(expandedIndex === index ? null : index)
  }

  return (
    <div className="p-4">
      {sources.map((source, i) => {
        const isExpanded = expandedIndex === i
        // Use the isTruncated flag from backend to determine if "Show more" is needed
        const isTruncated = source.isTruncated === true
        // Show full text when expanded, otherwise show excerpt
        const displayText = isExpanded ? source.text : source.excerpt
        
        return (
          <div key={i} className="rounded-lg border bg-white p-4 mb-3 shadow-sm">
            <div className="font-medium text-sm text-gray-800 mb-2">
              {getNameWithoutExtension(source.filename)}
            </div>
            
            <div className="mb-2">
              <div className="text-xs text-gray-500 mb-1">
                Confidence: {source.confidence}%
              </div>
              <div className="h-2 bg-gray-200 rounded overflow-hidden">
                <div 
                  className={`h-full ${getConfidenceColor(source.confidence)}`}
                  style={{ width: `${source.confidence}%` }}
                />
              </div>
            </div>
            
            <div className="text-sm text-gray-600 italic whitespace-pre-wrap">
              "{displayText}"
            </div>
            
            {isTruncated && (
              <button
                onClick={() => toggleExpand(i)}
                className="mt-2 text-xs text-blue-500 hover:text-blue-700 font-medium"
              >
                {isExpanded ? 'Show less' : 'Show more'}
              </button>
            )}
          </div>
        )
      })}
    </div>
  )
}

export default SourcePanel