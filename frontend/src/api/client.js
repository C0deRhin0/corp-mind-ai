export function askStream({ question, onToken, onSources, onDone, onError }) {
  const url = `/api/ask/stream?question=${encodeURIComponent(question)}`
  const es = new EventSource(url)

  es.onmessage = (e) => {
    if (e.data === '[DONE]') { es.close(); onDone?.(); return }
    try {
      const payload = JSON.parse(e.data)
      if (payload.type === 'token')   onToken?.(payload.text)
      if (payload.type === 'sources') onSources?.(payload.sources)
    } catch {}
  }

  es.onerror = () => { es.close(); onError?.() }
  return () => es.close()
}