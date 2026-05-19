import { create } from 'zustand'

export interface GraphStats {
  total_files: number
  total_classes: number
  total_methods: number
  total_calls: number
  total_components: number
  last_sync_time: string | null
  sync_status: string
}

export interface FileChange {
  id: number
  file_path: string
  change_type: string
  entities_count: number
  duration_ms: number
  created_at: string
}

export interface ParsedClass {
  id: number
  name: string
  file_id: number
  flags: number
  line_number: number
  file_path?: string
  method_count?: number
  methods?: ParsedMethod[]
}

export interface ParsedMethod {
  id: number
  name: string
  class_id: number
  params: string
  return_type: string
  line_number: number
  class_name?: string
  file_path?: string
}

export interface GraphNode {
  id: string
  name: string
  node_type: 'class' | 'method'
  file_path?: string
  val?: number
}

export interface GraphEdge {
  source: string
  target: string
  relation: string
}

interface AppState {
  stats: GraphStats | null
  changes: FileChange[]
  classes: ParsedClass[]
  methods: ParsedMethod[]
  graphNodes: GraphNode[]
  graphEdges: GraphEdge[]
  isConnected: boolean
  isSyncing: boolean

  setStats: (stats: GraphStats) => void
  setChanges: (changes: FileChange[]) => void
  setClasses: (classes: ParsedClass[]) => void
  setMethods: (methods: ParsedMethod[]) => void
  setGraphData: (nodes: GraphNode[], edges: GraphEdge[]) => void
  setIsConnected: (connected: boolean) => void
  setIsSyncing: (syncing: boolean) => void
  addChange: (change: FileChange) => void
}

export const useAppStore = create<AppState>((set) => ({
  stats: null,
  changes: [],
  classes: [],
  methods: [],
  graphNodes: [],
  graphEdges: [],
  isConnected: false,
  isSyncing: false,

  setStats: (stats) => set({ stats }),
  setChanges: (changes) => set({ changes }),
  setClasses: (classes) => set({ classes }),
  setMethods: (methods) => set({ methods }),
  setGraphData: (nodes, edges) => set({ graphNodes: nodes, graphEdges: edges }),
  setIsConnected: (connected) => set({ isConnected: connected }),
  setIsSyncing: (syncing) => set({ isSyncing: syncing }),
  addChange: (change) => set((state) => ({ changes: [change, ...state.changes].slice(0, 50) })),
}))
