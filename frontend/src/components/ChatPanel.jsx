import { useState, useRef, useEffect } from 'react'
import MessageBubble from './MessageBubble'
import { getHistory, recordSearch, clearHistory } from '../api/history'

function ChatPanel({ messages, onAsk, isLoading, onClearChat }) {
  const [input, setInput] = useState('')
  const messagesEndRef = useRef(null)
  const [searchHistory, setSearchHistory] = useState([])
  const [showHistory, setShowHistory] = useState(false)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useEffect(() => {
    const loadHistory = async () => {
      const history = await getHistory()
      setSearchHistory(history.searches || [])
    }
    loadHistory()
  }, [])

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return
    const query = input.trim()
    onAsk(query)
    recordSearch(query)
    setSearchHistory((prev) => {
      const exists = prev.find((p) => p.query === query)
      const updated = exists ? [exists, ...prev.filter((p) => p.query !== query)] : [{ query }, ...prev]
      return updated.slice(0, 20)
    })
    setInput('')
    setShowHistory(false)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  const exampleQuestions = [
    "What is our remote work policy?",
    "How do I submit a travel reimbursement?",
    "What are the IT security requirements for contractors?"
  ]

  const handleClearHistory = async () => {
    await clearHistory()
    setSearchHistory([])
  }

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <div className="flex-1 overflow-y-auto p-4">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-gray-400">
            <p className="mb-4">Ask a question about your company documents</p>
            <div className="flex flex-col gap-2">
              {exampleQuestions.map((q, i) => (
                <button
                  key={i}
                  onClick={() => onAsk(q)}
                  className="text-sm text-blue-500 hover:underline"
                >
                  "{q}"
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map(msg => (
              <MessageBubble key={msg.id} message={msg} />
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>
      
      <div className="p-4 border-t bg-white relative">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <div className="flex-1 relative">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              onFocus={() => setShowHistory(true)}
              placeholder="Type your question..."
              className="w-full p-2 border rounded resize-none"
              rows={2}
              disabled={isLoading}
            />
            {showHistory && searchHistory.length > 0 && (
              <div className="absolute bottom-full left-0 right-0 mb-2 bg-white border rounded shadow-lg max-h-40 overflow-y-auto z-50">
                <div className="flex items-center justify-between px-3 py-2 border-b">
                  <span className="text-xs text-gray-500">Search History</span>
                  <button
                    type="button"
                    onClick={handleClearHistory}
                    className="text-xs text-gray-400 hover:text-gray-600"
                  >
                    Clear
                  </button>
                </div>
                {searchHistory.map((item, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => { setInput(item.query); setShowHistory(false) }}
                    className="w-full text-left px-3 py-2 text-sm hover:bg-gray-100"
                  >
                    {item.query}
                  </button>
                ))}
              </div>
            )}
          </div>
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
          >
            Ask
          </button>
        </form>
      </div>
    </div>
  )
}

export default ChatPanel
