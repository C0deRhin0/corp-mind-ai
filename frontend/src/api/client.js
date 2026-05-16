export function askStream({ question, conversationId, onToken, onSources, onDone, onError }) {
  const params = new URLSearchParams({ question })
  if (conversationId) params.set('conversation_id', conversationId)
  const url = `/api/ask/stream?${params.toString()}`
  const es = new EventSource(url)

  es.onmessage = (e) => {
    if (e.data === '[DONE]') { es.close(); onDone?.(); return }
    try {
      const payload = JSON.parse(e.data)
      if (payload.type === 'token')   onToken?.(payload.text)
      if (payload.type === 'sources') onSources?.(payload.sources)
      if (payload.type === 'error')   onError?.(payload.message)
    } catch {}
  }

  es.onerror = () => { es.close(); onError?.('Connection error') }
  return () => es.close()
}
