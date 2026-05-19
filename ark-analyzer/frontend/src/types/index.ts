export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

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
  change_type: 'created' | 'modified' | 'deleted'
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
  extends?: ParsedClass[]
  called_by?: ParsedMethod[]
  calls?: ParsedMethod[]
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
  x?: number
  y?: number
  fx?: number
  fy?: number
}

export interface GraphEdge {
  source: string
  target: string
  relation: string
}

export interface ComponentNode {
  id: number
  name: string
  file_path?: string
  children?: ComponentNode[]
}

export interface CallChain {
  paths: number[][]
  total_paths: number
  depth: number
}

export interface SearchResult {
  type: 'class' | 'method'
  id: number
  name: string
  file_path?: string
  class_name?: string
}

export interface WebSocketMessage {
  type: string
  data: any
}

export interface Config {
  watch_path: string
  api_key: string
  base_url: string
  model_name: string
  debounce_seconds: number
  enable_llm_analysis: boolean
  database_path: string
}
