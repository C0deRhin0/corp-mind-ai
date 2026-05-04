import { useState, useRef, useEffect } from 'react'
import MessageBubble from './MessageBubble'

function ChatPanel({ messages, onAsk, isLoading }) {
  const [input, setInput] = useState('')
  const messagesEndRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return
    onAsk(input.trim())
    setInput('')
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
      
      <div className="p-4 border-t bg-white">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your question..."
            className="flex-1 p-2 border rounded resize-none"
            rows={2}
            disabled={isLoading}
          />
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