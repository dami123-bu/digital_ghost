const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080'

async function request(path, options = {}) {
  const res = await fetch(`${API_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || `Request failed: ${res.status}`)
  }
  return res.json()
}

// Multipart upload — browser sets Content-Type with boundary automatically
async function upload(path, formData) {
  const res = await fetch(`${API_URL}${path}`, { method: 'POST', body: formData })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || `Upload failed: ${res.status}`)
  }
  return res.json()
}

export const api = {
  health:           ()                    => request('/health'),
  getScores:        ()                    => request('/scores'),
  getMode:          ()                    => request('/mode'),
  setMode:          (mode)                => request('/mode',     { method: 'POST', body: JSON.stringify({ mode }) }),
  getProviders:     ()                    => request('/providers'),
  getProvider:      ()                    => request('/provider'),
  setProvider:      (provider)            => request('/provider', { method: 'POST', body: JSON.stringify({ provider }) }),
  query:            (question, session_id) =>
    request('/query', { method: 'POST', body: JSON.stringify({ question, session_id }) }),
  queryWithDoc:     (question, session_id, file) => {
    const fd = new FormData()
    fd.append('question', question)
    if (session_id) fd.append('session_id', session_id)
    fd.append('file', file)
    return upload('/query/with-doc', fd)
  },
  getLogs:          ()                    => request('/logs'),
  clearLogs:        ()                    => request('/logs', { method: 'DELETE' }),
  ingest:           (formData)            => upload('/ingest', formData),
  ingestDemoPoison: ()                    => request('/ingest/demo-poison', { method: 'POST', headers: {} }),
}
