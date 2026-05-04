import { useState } from 'react'

// Simple markdown parser for common elements
function parseMarkdown(text) {
  if (!text) return ''
  
  // Escape HTML first for security
  let html = text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  
  // Bold: **text** or __text__
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  html = html.replace(/__(.+?)__/g, '<strong>$1</strong>')
  
  // Italic: *text* or _text_
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>')
  html = html.replace(/_(.+?)_/g, '<em>$1</em>')
  
  // Code blocks: ```code```
  html = html.replace(/```([\s\S]*?)```/g, '<pre class="bg-gray-800 text-gray-100 p-2 rounded my-2 overflow-x-auto text-sm"><code>$1</code></pre>')
  
  // Inline code: `code`
  html = html.replace(/`([^`]+)`/g, '<code class="bg-gray-200 px-1 rounded text-sm">$1</code>')
  
  // Lists: lines starting with - or *
  const lines = html.split('\n')
  const processedLines = lines.map(line => {
    if (line.match(/^[-*]\s+/)) {
      return '<li class="ml-4">' + line.replace(/^[-*]\s+/, '') + '</li>'
    }
    return line
  })
  html = processedLines.join('\n')
  
  // Numbered lists: 1. 2. etc
  const numberedLines = html.split('\n').map(line => {
    if (line.match(/^\d+\.\s+/)) {
      return '<li class="ml-4 list-decimal">' + line.replace(/^\d+\.\s+/, '') + '</li>'
    }
    return line
  })
  html = numberedLines.join('\n')
  
  // Line breaks
  html = html.replace(/\n/g, '<br>')
  
  return html
}

function MessageBubble({ message }) {
  const isUser = message.role === 'assistant'
  const isError = message.error === true
  const [copied, setCopied] = useState(false)
  
  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }
  
  // For user messages, show plain text
  if (message.role === 'user') {
    return (
      <div className="flex justify-end">
        <div className="max-w-[80%] p-3 rounded-lg bg-blue-500 text-white">
          <div className="whitespace-pre-wrap">{message.content}</div>
        </div>
      </div>
    )
  }
  
  // For assistant messages, show markdown
  return (
    <div className="flex justify-start">
      <div 
        className={`max-w-[80%] p-3 rounded-lg ${
          isError
            ? 'bg-red-50 text-red-700 border border-red-200'
            : 'bg-gray-100 text-gray-900'
        }`}
      >
        {/* Copy button for assistant messages */}
        {!isError && message.content && (
          <div className="flex justify-end mb-1">
            <button
              onClick={handleCopy}
              className="text-xs text-gray-400 hover:text-gray-600"
            >
              {copied ? '✓ Copied' : 'Copy'}
            </button>
          </div>
        )}
        
        <div 
          className="whitespace-pre-wrap"
          dangerouslySetInnerHTML={{ __html: parseMarkdown(message.content) }}
        />
        
        {message.isStreaming && (
          <span className="inline-block w-2 h-4 bg-gray-400 animate-pulse ml-1" />
        )}
        
        {!isError && message.sources && message.sources.length > 0 && (
          <div className="mt-2 text-xs text-gray-500">
            View sources ({message.sources.length})
          </div>
        )}
        
        {!isError && !message.sources && !message.isStreaming && (
          <div className="mt-2 text-xs text-gray-400 italic">
            No sources available
          </div>
        )}
      </div>
    </div>
  )
}

export default MessageBubble