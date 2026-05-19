import { useEffect } from 'react'
import { Database, Code2, GitBranch, Layers, Clock, Activity } from 'lucide-react'
import { useAppStore } from '@/stores/appStore'
import { api, websocket } from '@/services/api'

const statCards = [
  { key: 'total_files', label: '文件总数', icon: Database, color: 'from-blue-500 to-cyan-500' },
  { key: 'total_classes', label: '类总数', icon: Code2, color: 'from-purple-500 to-pink-500' },
  { key: 'total_methods', label: '方法总数', icon: GitBranch, color: 'from-green-500 to-emerald-500' },
  { key: 'total_calls', label: '调用关系', icon: Layers, color: 'from-orange-500 to-red-500' },
]

export function Dashboard() {
  const { stats, changes, isConnected, setStats, setChanges, setIsConnected, addChange } = useAppStore()

  useEffect(() => {
    loadData()
    const ws = websocket.connect(
      (data) => {
        if (data.type === 'file_changed') {
          addChange(data.data)
        }
        if (data.type === 'sync_complete') {
          loadData()
        }
      },
      () => setIsConnected(true),
      () => setIsConnected(false)
    )
    return () => ws.close()
  }, [])

  const loadData = async () => {
    try {
      const [statsData, changesData] = await Promise.all([
        api.getStats(),
        api.getChanges(10)
      ])
      setStats(statsData)
      setChanges(changesData.items || [])
    } catch (error) {
      console.error('Failed to load data:', error)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2">
            <span className="gradient-text">ArkTS 知识图谱</span>
          </h1>
          <p className="text-gray-400">实时追踪代码结构与依赖关系</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10">
            <Activity className={`w-4 h-4 ${isConnected ? 'text-green-400' : 'text-gray-500'}`} />
            <span className={`text-sm ${isConnected ? 'text-green-400' : 'text-gray-500'}`}>
              {isConnected ? '实时监控中' : '连接中...'}
            </span>
            {isConnected && (
              <div className="w-2 h-2 rounded-full bg-green-400" />
            )}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((card) => (
          <div
            key={card.key}
            className="glass-card p-6"
          >
            <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${card.color} flex items-center justify-center mb-4`}>
              <card.icon className="w-6 h-6 text-white" />
            </div>
            <p className="text-3xl font-bold mb-1">
              {(stats as any)?.[card.key]?.toLocaleString() || '0'}
            </p>
            <p className="text-gray-400 text-sm">{card.label}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass-card p-6">
          <div className="flex items-center gap-3 mb-6">
            <Clock className="w-5 h-5 text-cyan-400" />
            <h2 className="text-lg font-semibold">最近变更</h2>
          </div>
          <div className="space-y-3">
            {changes.length === 0 ? (
              <p className="text-gray-500 text-center py-8">暂无变更记录</p>
            ) : (
              changes.slice(0, 8).map((change) => (
                <div
                  key={change.id}
                  className="flex items-center justify-between p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-2 h-2 rounded-full ${
                      change.change_type === 'created' ? 'bg-green-400' :
                      change.change_type === 'modified' ? 'bg-yellow-400' : 'bg-red-400'
                    }`} />
                    <span className="text-sm font-mono text-gray-300 truncate max-w-md">
                      {change.file_path.split('/').pop()}
                    </span>
                  </div>
                  <div className="flex items-center gap-4 text-xs text-gray-500">
                    <span>{change.entities_count} 实体</span>
                    <span>{change.duration_ms}ms</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="glass-card p-6">
          <div className="flex items-center gap-3 mb-6">
            <GitBranch className="w-5 h-5 text-purple-400" />
            <h2 className="text-lg font-semibold">系统状态</h2>
          </div>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-400">同步状态</span>
              <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                (stats as any)?.sync_status === 'idle'
                  ? 'bg-green-500/20 text-green-400'
                  : 'bg-yellow-500/20 text-yellow-400'
              }`}>
                {(stats as any)?.sync_status || 'idle'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400">最后同步</span>
              <span className="text-sm text-gray-300">
                {(stats as any)?.last_sync_time
                  ? new Date((stats as any).last_sync_time).toLocaleString('zh-CN')
                  : '从未同步'}
              </span>
            </div>
            <div className="h-px bg-white/10 my-4" />
            <div className="text-center py-4">
              <p className="text-xs text-gray-500 mb-2">基于第一性原理</p>
              <p className="text-sm text-gray-400">
                增量更新 · 单文件变更 &lt;500ms
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="glass-card p-6">
        <h2 className="text-lg font-semibold mb-4">架构说明</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 rounded-xl bg-gradient-to-br from-cyan-500/10 to-blue-500/10 border border-cyan-500/20">
            <h3 className="font-semibold text-cyan-400 mb-2">文件监控系统</h3>
            <p className="text-sm text-gray-400">
              使用 watchdog 监控 ArkTS 文件变化，支持创建、修改、删除事件
            </p>
          </div>
          <div className="p-4 rounded-xl bg-gradient-to-br from-purple-500/10 to-pink-500/10 border border-purple-500/20">
            <h3 className="font-semibold text-purple-400 mb-2">增量更新引擎</h3>
            <p className="text-sm text-gray-400">
              基于哈希对比实现精准增量，只更新变化的文件
            </p>
          </div>
          <div className="p-4 rounded-xl bg-gradient-to-br from-green-500/10 to-emerald-500/10 border border-green-500/20">
            <h3 className="font-semibold text-green-400 mb-2">SQLite 图数据库</h3>
            <p className="text-sm text-gray-400">
              轻量级嵌入式数据库，支持复杂图查询和关系追踪
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
