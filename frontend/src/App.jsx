import { useState } from 'react'
import ChatPanel from './components/ChatPanel'
import SourcePanel from './components/SourcePanel'

function App() {
  const [messages, setMessages] = useState([])
  const [activeSources, setActiveSources] = useState(null)
  const [isLoading, setIsLoading] = useState(false)

  const handleAsk = async (question) => {
    const userMsg = { id: Date.now(), role: 'user', content: question }
    const assistantMsg = { id: Date.now() + 1, role: 'assistant', content: '', isStreaming: true, error: false }
    
    setMessages(prev => [...prev, userMsg, assistantMsg])
    setActiveSources(null)
    setIsLoading(true)

    const { askStream } = await import('./api/client')
    
    askStream({
      question,
      onToken: (token) => {
        setMessages(prev => prev.map(m => 
          m.id === assistantMsg.id 
            ? { ...m, content: m.content + token }
            : m
        ))
      },
      onSources: (sources) => {
        setActiveSources(sources)
        setMessages(prev => prev.map(m => 
          m.id === assistantMsg.id 
            ? { ...m, sources }
            : m
        ))
      },
      onDone: () => {
        setMessages(prev => prev.map(m => 
          m.id === assistantMsg.id 
            ? { ...m, isStreaming: false }
            : m
        ))
        setIsLoading(false)
      },
      onError: () => {
        setMessages(prev => prev.map(m => 
          m.id === assistantMsg.id 
            ? { ...m, content: 'I apologize, but I encountered an error while processing your request. Please try again.', isStreaming: false, error: true }
            : m
        ))
        setIsLoading(false)
      }
    })
  }

  const handleClearChat = () => {
    setMessages([])
    setActiveSources(null)
  }

  return (
    <div className="h-screen flex overflow-hidden">
      <div className="flex-[6] flex flex-col border-r">
        <header className="h-12 border-b flex items-center justify-between px-4 text-sm font-semibold">
          <div>
            <span style={{ color: '#0096FF', fontWeight: 'bold', fontSize: '18px' }}>NuecAI</span>
            <span style={{ marginLeft: '12px', color: '#666' }}>Corporate Mind</span>
          </div>
          {messages.length > 0 && (
            <button 
              onClick={handleClearChat}
              className="text-xs text-gray-500 hover:text-gray-700 px-2 py-1 rounded border border-gray-300 hover:bg-gray-100"
            >
              Clear Chat
            </button>
          )}
        </header>
        <ChatPanel 
          messages={messages} 
          onAsk={handleAsk} 
          isLoading={isLoading}
        />
      </div>
      <div className="flex-[4] overflow-y-auto bg-gray-50">
        <header className="h-12 border-b flex items-center px-4 text-sm font-semibold" style={{ background: '#f8f9fa' }}>
          Sources
        </header>
        <SourcePanel sources={activeSources} />
      </div>
    </div>
  )
}

export default App