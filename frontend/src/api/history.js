const STORAGE_KEY = 'nuecai_history_v1'

function getStoredHistory() {
  const raw = localStorage.getItem(STORAGE_KEY)
  if (!raw) return { conversations: [], searches: [] }
  try {
    return JSON.parse(raw)
  } catch (e) {
    return { conversations: [], searches: [] }
  }
}

function setStoredHistory(data) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
}

export async function createConversationIfNeeded(currentId, question) {
  if (currentId) {
    return currentId
  }

  const history = getStoredHistory()
  const id = `conv_${Date.now()}`
  const newConversation = {
    id,
    title: question.slice(0, 60),
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    messages: [],
  }
  history.conversations.unshift(newConversation)
  setStoredHistory(history)
  return id
}

export async function recordMessage(conversationId, message) {
  const history = getStoredHistory()
  const convo = history.conversations.find((c) => c.id === conversationId)
  if (!convo) return
  convo.messages.push(message)
  convo.updatedAt = new Date().toISOString()
  setStoredHistory(history)
}

export async function recordSearch(query) {
  const history = getStoredHistory()
  const exists = history.searches.find((q) => q.query === query)
  if (!exists) {
    history.searches.unshift({
      query,
      lastUsedAt: new Date().toISOString(),
    })
  } else {
    exists.lastUsedAt = new Date().toISOString()
    history.searches = [exists, ...history.searches.filter((q) => q.query !== query)]
  }
  history.searches = history.searches.slice(0, 20)
  setStoredHistory(history)
}

export async function getHistory() {
  return getStoredHistory()
}

export async function clearHistory() {
  setStoredHistory({ conversations: [], searches: [] })
}
