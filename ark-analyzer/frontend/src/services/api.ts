const API_BASE_URL = '/api/v1'
const WS_BASE_URL = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}`

export const api = {
  async getStats() {
    const res = await fetch(`${API_BASE_URL}/stats`)
    if (!res.ok) throw new Error('Failed to fetch stats')
    return res.json()
  },

  async getClasses(page = 1, limit = 50, search?: string) {
    const params = new URLSearchParams({ page: String(page), limit: String(limit) })
    if (search) params.append('search', search)
    const res = await fetch(`${API_BASE_URL}/classes?${params}`)
    if (!res.ok) throw new Error('Failed to fetch classes')
    return res.json()
  },

  async getClassDetail(classId: number) {
    const res = await fetch(`${API_BASE_URL}/classes/${classId}`)
    if (!res.ok) throw new Error('Failed to fetch class detail')
    return res.json()
  },

  async getMethods(page = 1, limit = 50, search?: string) {
    const params = new URLSearchParams({ page: String(page), limit: String(limit) })
    if (search) params.append('search', search)
    const res = await fetch(`${API_BASE_URL}/methods?${params}`)
    if (!res.ok) throw new Error('Failed to fetch methods')
    return res.json()
  },

  async getCallChain(fromMethodId: number, toMethodId: number, maxDepth = 10) {
    const params = new URLSearchParams({
      from_method_id: String(fromMethodId),
      to_method_id: String(toMethodId),
      max_depth: String(maxDepth)
    })
    const res = await fetch(`${API_BASE_URL}/call-chain?${params}`)
    if (!res.ok) throw new Error('Failed to fetch call chain')
    return res.json()
  },

  async getComponents() {
    const res = await fetch(`${API_BASE_URL}/components`)
    if (!res.ok) throw new Error('Failed to fetch components')
    return res.json()
  },

  async getChanges(limit = 20) {
    const res = await fetch(`${API_BASE_URL}/changes?limit=${limit}`)
    if (!res.ok) throw new Error('Failed to fetch changes')
    return res.json()
  },

  async search(q: string, type?: string) {
    const params = new URLSearchParams({ q })
    if (type) params.append('type', type)
    const res = await fetch(`${API_BASE_URL}/search?${params}`)
    if (!res.ok) throw new Error('Failed to search')
    return res.json()
  },

  async getGraphNodes(type: 'class' | 'method' = 'class') {
    const res = await fetch(`${API_BASE_URL}/graph/nodes?type=${type}`)
    if (!res.ok) throw new Error('Failed to fetch graph nodes')
    return res.json()
  },

  async getGraphEdges(type: 'extends' | 'calls' | 'components' = 'extends') {
    const res = await fetch(`${API_BASE_URL}/graph/edges?type=${type}`)
    if (!res.ok) throw new Error('Failed to fetch graph edges')
    return res.json()
  }
}

export const websocket = {
  connect(onMessage: (data: any) => void, onConnect?: () => void, onDisconnect?: () => void) {
    const ws = new WebSocket(`${WS_BASE_URL}/ws/updates`)

    ws.onopen = () => {
      console.log('WebSocket connected')
      onConnect?.()
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        onMessage(data)
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e)
      }
    }

    ws.onclose = () => {
      console.log('WebSocket disconnected')
      onDisconnect?.()
      setTimeout(() => this.connect(onMessage, onConnect, onDisconnect), 3000)
    }

    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }

    return ws
  }
}
