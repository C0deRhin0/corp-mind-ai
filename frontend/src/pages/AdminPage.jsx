import { useEffect, useState } from 'react'

const API_BASE = '/api/admin'

function AdminPage() {
  const [authenticated, setAuthenticated] = useState(false)
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [documents, setDocuments] = useState([])
  const [uploading, setUploading] = useState(false)
  const [resetting, setResetting] = useState(false)

  const handleLogin = async () => {
    setError('')
    try {
      const resp = await fetch(`${API_BASE}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: password }),
      })
      if (!resp.ok) {
        throw new Error('Invalid admin code')
      }
      setAuthenticated(true)
      setPassword('')
    } catch (err) {
      setError(err.message || 'Login failed')
    }
  }

  const fetchDocuments = async () => {
    const resp = await fetch(`${API_BASE}/documents`)
    const data = await resp.json()
    setDocuments(data.documents || [])
  }

  const handleUpload = async (files) => {
    if (!files || files.length === 0) return
    setUploading(true)
    const formData = new FormData()
    for (const file of files) {
      formData.append('files', file)
    }
    const resp = await fetch(`${API_BASE}/documents/upload`, {
      method: 'POST',
      body: formData,
    })
    if (resp.ok) {
      await fetchDocuments()
    }
    setUploading(false)
  }

  const handleDelete = async (filename) => {
    if (!confirm(`Delete ${filename}?`)) return
    await fetch(`${API_BASE}/documents/${encodeURIComponent(filename)}`, { method: 'DELETE' })
    await fetchDocuments()
  }

  const handleReingest = async () => {
    setResetting(true)
    await fetch(`${API_BASE}/documents/reingest`, { method: 'POST' })
    setResetting(false)
  }

  const handleReset = async () => {
    if (!confirm('This will delete all indexed documents. Continue?')) return
    setResetting(true)
    await fetch(`${API_BASE}/documents/reset`, { method: 'POST' })
    setResetting(false)
    await fetchDocuments()
  }

  useEffect(() => {
    if (authenticated) {
      fetchDocuments()
    }
  }, [authenticated])

  if (!authenticated) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-50">
        <div className="bg-white p-6 rounded-lg shadow-md w-96">
          <h2 className="text-lg font-semibold mb-4">Admin Access</h2>
          <input
            type="password"
            placeholder="Enter admin code"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full border rounded px-3 py-2 mb-3"
          />
          {error && <div className="text-red-500 text-sm mb-2">{error}</div>}
          <button
            onClick={handleLogin}
            className="w-full bg-blue-500 text-white py-2 rounded hover:bg-blue-600"
          >
            Enter Admin
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="h-screen bg-gray-50">
      <header className="h-12 border-b flex items-center justify-between px-4 text-sm font-semibold bg-white">
        <div>
          <span style={{ color: '#0096FF', fontWeight: 'bold', fontSize: '18px' }}>NuecAI</span>
          <span style={{ marginLeft: '12px', color: '#666' }}>Admin</span>
        </div>
        <button
          onClick={() => { window.location.hash = '#/chat' }}
          className="text-xs text-gray-500 hover:text-gray-700 px-2 py-1 rounded border border-gray-300 hover:bg-gray-100"
        >
          Back to Chat
        </button>
      </header>

      <div className="p-6">
        <div className="mb-6 flex gap-3">
          <label className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 cursor-pointer">
            {uploading ? 'Uploading...' : 'Upload & Ingest'}
            <input
              type="file"
              multiple
              accept=".pdf,.docx,.txt,.md,.markdown"
              className="hidden"
              onChange={(e) => handleUpload(e.target.files)}
            />
          </label>
          <button
            onClick={handleReingest}
            disabled={resetting}
            className="px-4 py-2 border rounded hover:bg-gray-100"
          >
            Re-ingest All
          </button>
          <button
            onClick={handleReset}
            disabled={resetting}
            className="px-4 py-2 border rounded text-red-600 hover:bg-red-50"
          >
            Reset All
          </button>
        </div>

        <div className="bg-white rounded-lg shadow-sm border">
          <div className="px-4 py-2 border-b text-sm font-semibold">Documents</div>
          {documents.length === 0 ? (
            <div className="p-4 text-gray-500">No documents indexed yet.</div>
          ) : (
            <ul>
              {documents.map((doc, idx) => (
                <li key={idx} className="flex items-center justify-between px-4 py-2 border-b">
                  <span>{doc.filename}</span>
                  <button
                    onClick={() => handleDelete(doc.filename)}
                    className="text-xs text-red-500 hover:text-red-700"
                  >
                    Delete
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  )
}

export default AdminPage
