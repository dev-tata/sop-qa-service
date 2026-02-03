import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { vi } from 'vitest'
import App from '../App'

type MockResponse = {
  ok: boolean
  status: number
  headers: { get: (key: string) => string | null }
  json: () => Promise<unknown>
  text: () => Promise<string>
}

const jsonResponse = (data: unknown, status = 200): MockResponse => ({
  ok: status >= 200 && status < 300,
  status,
  headers: { get: () => 'application/json' },
  json: async () => data,
  text: async () => JSON.stringify(data),
})

const createFetchMock = (routes: Record<string, unknown>) =>
  vi.fn(async (input: RequestInfo) => {
    const url = typeof input === 'string' ? input : input.url
    const path = url.replace(/^https?:\/\/[^/]+/, '')
    if (path in routes) {
      return jsonResponse(routes[path])
    }
    return jsonResponse({ detail: `No mock for ${path}` }, 404)
  })

describe('App', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
    vi.resetAllMocks()
  })

  it('renders key panels', async () => {
    const fetchMock = createFetchMock({
      '/api/health': { status: 'ok', ready: false, index_dir: 'data/index' },
    })
    vi.stubGlobal('fetch', fetchMock)

    render(<App />)

    expect(await screen.findByText('Index Controls')).toBeInTheDocument()
    expect(screen.getByText('Semantic Search')).toBeInTheDocument()
    expect(screen.getByText('Ask a Question')).toBeInTheDocument()
  })

  it('searches and loads a chunk', async () => {
    const fetchMock = createFetchMock({
      '/api/health': { status: 'ok', ready: true, index_dir: 'data/index' },
      '/api/search': [
        {
          score: 0.91,
          chunk_id: 'chunk-1',
          section_title: 'Validation Steps',
          page_start: 2,
          page_end: 3,
          keywords: ['validation'],
        },
      ],
      '/api/chunks/chunk-1': {
        chunk_id: 'chunk-1',
        section_title: 'Validation Steps',
        text: 'Step 1: Gather requirements.\nStep 2: Verify outputs.',
        page_start: 2,
        page_end: 3,
        keywords: ['validation'],
      },
    })
    vi.stubGlobal('fetch', fetchMock)

    render(<App />)

    await screen.findByText('Semantic Search')

    await userEvent.type(screen.getByLabelText('Query'), 'validation')
    await userEvent.click(screen.getByRole('button', { name: 'Search' }))

    expect(await screen.findByText('Validation Steps')).toBeInTheDocument()

    await userEvent.click(screen.getByRole('button', { name: 'View Chunk' }))
    expect(await screen.findByText(/Step 1: Gather requirements\./)).toBeInTheDocument()
  })
})
