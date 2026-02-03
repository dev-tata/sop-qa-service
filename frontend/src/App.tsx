import { useEffect, useMemo, useState } from 'react'
import './App.css'

const API_BASE = '/api'

type HealthResponse = {
  status: string
  ready: boolean
  index_dir: string
}

type SearchHit = {
  score: number
  chunk_id: string
  section_title: string
  page_start: number
  page_end: number
  keywords?: string[]
}

type QAContext = {
  score: number
  chunk_id: string
  section_title: string
  page_start: number
  page_end: number
  excerpt: string
}

type QAResponse = {
  question: string
  contexts: QAContext[]
}

type Chunk = {
  chunk_id: string
  section_title: string
  text: string
  page_start: number
  page_end: number
  keywords?: string[]
  source_file?: string
  section_id?: string
}

async function apiRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
    ...init,
  })

  if (!res.ok) {
    const text = await res.text()
    let message = text
    try {
      const parsed = JSON.parse(text)
      if (typeof parsed?.detail === 'string') {
        message = parsed.detail
      }
    } catch {
      // keep text
    }
    throw new Error(message || `Request failed (${res.status})`)
  }

  const contentType = res.headers.get('content-type') ?? ''
  if (contentType.includes('application/json')) {
    return res.json() as Promise<T>
  }
  return (await res.text()) as unknown as T
}

function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [healthLoading, setHealthLoading] = useState(false)
  const [message, setMessage] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const [pdfPath, setPdfPath] = useState('backend/data/pdfs/my_doc.pdf')
  const [persist, setPersist] = useState(true)
  const [buildLoading, setBuildLoading] = useState(false)
  const [loadLoading, setLoadLoading] = useState(false)

  const [searchQuery, setSearchQuery] = useState('')
  const [searchKeywords, setSearchKeywords] = useState('')
  const [searchTopK, setSearchTopK] = useState(5)
  const [searchPoolK, setSearchPoolK] = useState(25)
  const [searchLoading, setSearchLoading] = useState(false)
  const [searchResults, setSearchResults] = useState<SearchHit[]>([])

  const [question, setQuestion] = useState('')
  const [qaTopK, setQaTopK] = useState(5)
  const [qaLoading, setQaLoading] = useState(false)
  const [qaResult, setQaResult] = useState<QAResponse | null>(null)

  const [chunkLoading, setChunkLoading] = useState(false)
  const [selectedChunk, setSelectedChunk] = useState<Chunk | null>(null)

  const keywordsList = useMemo(
    () =>
      searchKeywords
        .split(',')
        .map((item) => item.trim())
        .filter(Boolean),
    [searchKeywords],
  )

  const refreshHealth = async () => {
    setHealthLoading(true)
    try {
      const data = await apiRequest<HealthResponse>('/health')
      setHealth(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load health status.')
    } finally {
      setHealthLoading(false)
    }
  }

  useEffect(() => {
    refreshHealth()
  }, [])

  const handleBuild = async () => {
    setError(null)
    setMessage(null)
    setBuildLoading(true)
    setSelectedChunk(null)
    try {
      const result = await apiRequest<{ status: string; chunks: number; index_dir: string }>('/build', {
        method: 'POST',
        body: JSON.stringify({ pdf_path: pdfPath, persist }),
      })
      setMessage(`Index ${result.status}. Chunks: ${result.chunks}`)
      await refreshHealth()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Build failed.')
    } finally {
      setBuildLoading(false)
    }
  }

  const handleLoad = async () => {
    setError(null)
    setMessage(null)
    setLoadLoading(true)
    setSelectedChunk(null)
    try {
      const result = await apiRequest<{ status: string; chunks: number; index_dir: string }>('/load', {
        method: 'POST',
      })
      setMessage(`Index ${result.status}. Chunks: ${result.chunks}`)
      await refreshHealth()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Load failed.')
    } finally {
      setLoadLoading(false)
    }
  }

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      setError('Enter a search query first.')
      return
    }
    setError(null)
    setMessage(null)
    setSearchLoading(true)
    setSelectedChunk(null)
    try {
      const result = await apiRequest<SearchHit[]>('/search', {
        method: 'POST',
        body: JSON.stringify({
          query: searchQuery,
          keywords: keywordsList.length ? keywordsList : null,
          top_k: searchTopK,
          pool_k: searchPoolK,
        }),
      })
      setSearchResults(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed.')
    } finally {
      setSearchLoading(false)
    }
  }

  const handleQA = async () => {
    if (!question.trim()) {
      setError('Enter a question first.')
      return
    }
    setError(null)
    setMessage(null)
    setQaLoading(true)
    setSelectedChunk(null)
    try {
      const result = await apiRequest<QAResponse>('/qa', {
        method: 'POST',
        body: JSON.stringify({ question, top_k: qaTopK }),
      })
      setQaResult(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'QA failed.')
    } finally {
      setQaLoading(false)
    }
  }

  const handleChunk = async (chunkId: string) => {
    setError(null)
    setMessage(null)
    setChunkLoading(true)
    try {
      const result = await apiRequest<Chunk>(`/chunks/${chunkId}`)
      setSelectedChunk(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load chunk.')
    } finally {
      setChunkLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="hero">
        <div>
          <p className="eyebrow">PDF FAISS QA Service</p>
          <h1>Search SOPs and extract answers :)</h1>
          <p className="subtitle">
            Type a document path and extract answers with full chunk context.
          </p>
        </div>
        <div className="status-card">
          <div className="status-row">
            <span className="status-label">Service</span>
            <span className={`status-pill ${health?.ready ? 'ok' : 'warn'}`}>
              {healthLoading ? 'Checking…' : health?.ready ? 'Ready' : 'Not Ready'}
            </span>
          </div>
          <div className="status-row">
            <span className="status-label">Index Dir</span>
            <span className="status-value">{health?.index_dir ?? '—'}</span>
          </div>
          <button className="ghost" onClick={refreshHealth} disabled={healthLoading}>
            Refresh
          </button>
        </div>
      </header>

      <section className="grid">
        <div className="panel">
          <h2>Index Controls</h2>
          <label className="field">
            PDF path (server-side)
            <input
              value={pdfPath}
              onChange={(event) => setPdfPath(event.target.value)}
              placeholder="backend/data/pdfs/my_doc.pdf"
            />
            <span className="hint">Path is resolved on the backend host, not your browser.</span>
          </label>
          <label className="check">
            <input type="checkbox" checked={persist} onChange={(event) => setPersist(event.target.checked)} />
            Persist index artifacts to disk
          </label>
          <div className="button-row">
            <button onClick={handleBuild} disabled={buildLoading}>
              {buildLoading ? 'Building…' : 'Build Index'}
            </button>
            <button className="ghost" onClick={handleLoad} disabled={loadLoading}>
              {loadLoading ? 'Loading…' : 'Load Existing'}
            </button>
          </div>
        </div>

        <div className="panel">
          <h2>Semantic Search</h2>
          <label className="field">
            Query
            <input
              value={searchQuery}
              onChange={(event) => setSearchQuery(event.target.value)}
              placeholder="How do we handle customer complaints?"
            />
          </label>
          <label className="field">
            Keywords (comma-separated)
            <input
              value={searchKeywords}
              onChange={(event) => setSearchKeywords(event.target.value)}
              placeholder="billing, escalation, tier 2"
            />
          </label>
          <div className="field-row">
            <label className="field small">
              Top K
              <input
                type="number"
                min={1}
                value={searchTopK}
                onChange={(event) => setSearchTopK(Number(event.target.value))}
              />
            </label>
            <label className="field small">
              Pool K
              <input
                type="number"
                min={1}
                value={searchPoolK}
                onChange={(event) => setSearchPoolK(Number(event.target.value))}
              />
            </label>
          </div>
          <div className="button-row">
            <button onClick={handleSearch} disabled={searchLoading}>
              {searchLoading ? 'Searching…' : 'Search'}
            </button>
            <button className="ghost" onClick={() => setSearchResults([])} disabled={searchLoading}>
              Clear Results
            </button>
          </div>
        </div>

        <div className="panel">
          <h2>Ask a Question</h2>
          <label className="field">
            Question
            <input
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="What is the SLA for priority incidents?"
            />
          </label>
          <label className="field small">
            Top K
            <input type="number" min={1} value={qaTopK} onChange={(event) => setQaTopK(Number(event.target.value))} />
          </label>
          <div className="button-row">
            <button onClick={handleQA} disabled={qaLoading}>
              {qaLoading ? 'Analyzing…' : 'Get Answer Context'}
            </button>
            <button className="ghost" onClick={() => setQaResult(null)} disabled={qaLoading}>
              Clear
            </button>
          </div>
        </div>

        <div className="panel results">
          <h2>Results</h2>
          {error && <div className="notice error">Error: {error}</div>}
          {message && <div className="notice success">{message}</div>}

          <div className="results-grid">
            <div>
              <h3>Search Hits</h3>
              {searchResults.length === 0 ? (
                <p className="muted">No search results yet.</p>
              ) : (
                <ul className="list">
                  {searchResults.map((hit) => (
                    <li key={hit.chunk_id} className="list-item">
                      <div>
                        <p className="title">{hit.section_title || 'Untitled section'}</p>
                        <p className="meta">
                          Score {hit.score.toFixed(3)} · Pages {hit.page_start}-{hit.page_end}
                        </p>
                        {hit.keywords?.length ? (
                          <div className="tag-row">
                            {hit.keywords.map((kw) => (
                              <span key={kw} className="tag">
                                {kw}
                              </span>
                            ))}
                          </div>
                        ) : null}
                      </div>
                      <button className="ghost small" onClick={() => handleChunk(hit.chunk_id)} disabled={chunkLoading}>
                        {chunkLoading ? 'Loading…' : 'View Chunk'}
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>

            <div>
              <h3>QA Context</h3>
              {qaResult?.contexts?.length ? (
                <ul className="list">
                  {qaResult.contexts.map((context) => (
                    <li key={context.chunk_id} className="list-item">
                      <div>
                        <p className="title">{context.section_title || 'Untitled section'}</p>
                        <p className="meta">
                          Score {context.score.toFixed(3)} · Pages {context.page_start}-{context.page_end}
                        </p>
                        <p className="excerpt">{context.excerpt}</p>
                      </div>
                      <button className="ghost small" onClick={() => handleChunk(context.chunk_id)} disabled={chunkLoading}>
                        {chunkLoading ? 'Loading…' : 'View Chunk'}
                      </button>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="muted">No QA context yet.</p>
              )}
            </div>
          </div>
        </div>

        <div className="panel">
          <h2>Chunk Detail</h2>
          {selectedChunk ? (
            <div className="chunk">
              <div className="chunk-header">
                <div>
                  <p className="title">{selectedChunk.section_title || 'Untitled section'}</p>
                  <p className="meta">
                    {selectedChunk.chunk_id} · Pages {selectedChunk.page_start}-{selectedChunk.page_end}
                  </p>
                </div>
              </div>
              <p className="chunk-text">{selectedChunk.text}</p>
              {selectedChunk.keywords?.length ? (
                <div className="tag-row">
                  {selectedChunk.keywords.map((kw) => (
                    <span key={kw} className="tag">
                      {kw}
                    </span>
                  ))}
                </div>
              ) : null}
            </div>
          ) : (
            <p className="muted">Select a search hit or QA context to view full text.</p>
          )}
        </div>
      </section>
    </div>
  )
}

export default App
