import { useEffect, useState, useRef } from 'react'
import { RefreshCw, Search, Filter } from 'lucide-react'
import { useAppStore } from '@/stores/appStore'
import { api } from '@/services/api'

interface GraphNode {
  id: string
  name: string
  node_type: 'class' | 'method'
  file_path?: string
  val?: number
  x?: number
  y?: number
}

export function GraphView() {
  const { graphNodes, graphEdges, setGraphData, isSyncing } = useAppStore()
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [relationType, setRelationType] = useState<'extends' | 'calls' | 'components'>('extends')
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    loadGraphData()
  }, [])

  const loadGraphData = async () => {
    try {
      const [nodesData, edgesData] = await Promise.all([
        api.getGraphNodes('class'),
        api.getGraphEdges(relationType)
      ])
      const nodes = nodesData.nodes.map((n: any) => ({
        ...n,
        id: String(n.id),
        val: 1
      }))
      const links = edgesData.edges.map((e: any) => ({
        source: String(e.source),
        target: String(e.target),
        relation: e.relation
      }))
      setGraphData(nodes, links)
    } catch (error) {
      console.error('Failed to load graph data:', error)
    }
  }

  useEffect(() => {
    loadGraphData()
  }, [relationType])

  const filteredNodes = searchTerm
    ? graphNodes.filter(node =>
        node.name.toLowerCase().includes(searchTerm.toLowerCase())
      )
    : graphNodes

  const getNodeColor = (node: GraphNode) => {
    if (selectedNode?.id === node.id) return '#00d4ff'
    if (node.node_type === 'class') return '#7c3aed'
    return '#10b981'
  }

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold mb-2">
            <span className="gradient-text">类关系图谱</span>
          </h1>
          <p className="text-gray-400">可视化展示类之间的继承、实现和调用关系</p>
        </div>
        <button
          onClick={loadGraphData}
          disabled={isSyncing}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 transition-all disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${isSyncing ? 'animate-spin' : ''}`} />
          刷新
        </button>
      </div>

      <div className="flex-1 flex gap-6 min-h-0">
        <div className="w-80 flex flex-col glass-card">
          <div className="p-4 border-b border-white/5">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              <input
                type="text"
                placeholder="搜索类或方法..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 rounded-lg bg-white/5 border border-white/10 text-sm focus:outline-none focus:border-cyan-500/50"
              />
            </div>
          </div>

          <div className="p-4 border-b border-white/5">
            <div className="flex items-center gap-2 mb-3">
              <Filter className="w-4 h-4 text-gray-500" />
              <span className="text-sm text-gray-400">关系类型</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {(['extends', 'calls', 'components'] as const).map(type => (
                <button
                  key={type}
                  onClick={() => setRelationType(type)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                    relationType === type
                      ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                      : 'bg-white/5 text-gray-400 border border-white/10 hover:bg-white/10'
                  }`}
                >
                  {type === 'extends' ? '继承' : type === 'calls' ? '调用' : '组合'}
                </button>
              ))}
            </div>
          </div>

          <div className="flex-1 overflow-y-auto p-4">
            <p className="text-xs text-gray-500 mb-3">
              {filteredNodes.length} 个节点
            </p>
            <div className="space-y-2">
              {filteredNodes.slice(0, 50).map(node => (
                <button
                  key={node.id}
                  onClick={() => setSelectedNode(node)}
                  className={`w-full text-left p-3 rounded-lg transition-all ${
                    selectedNode?.id === node.id
                      ? 'bg-cyan-500/20 border border-cyan-500/30'
                      : 'bg-white/5 hover:bg-white/10 border border-transparent'
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <div
                      className="w-2 h-2 rounded-full"
                      style={{ backgroundColor: getNodeColor(node) }}
                    />
                    <span className="text-sm font-medium truncate">{node.name}</span>
                  </div>
                  <p className="text-xs text-gray-500 mt-1 truncate">
                    {node.node_type === 'class' ? '类' : '方法'}
                  </p>
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="flex-1 glass-card overflow-hidden">
          <div className="h-full flex flex-col">
            <div
              ref={containerRef}
              className="flex-1 relative bg-gradient-to-br from-[#0a0a0f] to-[#12121a] flex items-center justify-center"
            >
              {filteredNodes.length > 0 ? (
                <div className="text-center">
                  <p className="text-gray-400 text-lg mb-2">
                    📊 图谱可视化
                  </p>
                  <p className="text-gray-500 text-sm">
                    {filteredNodes.length} 个节点, {graphEdges.length} 个关系
                  </p>
                </div>
              ) : (
                <div className="text-gray-500">加载中...</div>
              )}
            </div>
          </div>
        </div>

        {selectedNode && (
          <div className="w-80 glass-card p-4">
            <h3 className="font-semibold mb-4">节点详情</h3>
            <div className="space-y-3">
              <div>
                <p className="text-xs text-gray-500">名称</p>
                <p className="text-sm font-mono">{selectedNode.name}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500">类型</p>
                <p className="text-sm">{selectedNode.node_type === 'class' ? '类' : '方法'}</p>
              </div>
              {selectedNode.file_path && (
                <div>
                  <p className="text-xs text-gray-500">文件路径</p>
                  <p className="text-sm font-mono truncate">{selectedNode.file_path}</p>
                </div>
              )}
            </div>
            <button
              onClick={() => setSelectedNode(null)}
              className="w-full mt-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 text-sm transition-colors"
            >
              关闭
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
