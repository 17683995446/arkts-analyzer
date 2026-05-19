import { useEffect, useState } from 'react'
import { FileText, Clock, Zap, RefreshCw, Filter } from 'lucide-react'
import { api } from '@/services/api'
import { useAppStore } from '@/stores/appStore'

export function ChangeHistory() {
  const { changes, setChanges, isConnected } = useAppStore()
  const [filter, setFilter] = useState<string>('all')
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    loadChanges()
  }, [])

  const loadChanges = async () => {
    setIsLoading(true)
    try {
      const data = await api.getChanges(50)
      setChanges(data.items || [])
    } catch (error) {
      console.error('Failed to load changes:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const filteredChanges = filter === 'all' 
    ? changes 
    : changes.filter(c => c.change_type === filter)

  const getChangeTypeColor = (type: string) => {
    switch (type) {
      case 'created':
        return 'bg-green-500/20 text-green-400 border-green-500/30'
      case 'modified':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
      case 'deleted':
        return 'bg-red-500/20 text-red-400 border-red-500/30'
      default:
        return 'bg-white/5 text-gray-400 border-white/10'
    }
  }

  const getChangeTypeName = (type: string) => {
    switch (type) {
      case 'created':
        return '新增'
      case 'modified':
        return '修改'
      case 'deleted':
        return '删除'
      default:
        return '其他'
    }
  }

  const formatTime = (timeStr: string) => {
    try {
      return new Date(timeStr).toLocaleString('zh-CN')
    } catch {
      return timeStr
    }
  }

  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold mb-2">
            <span className="gradient-text">变更历史</span>
          </h1>
          <p className="text-gray-400">文件变更记录</p>
        </div>
        <div className="flex items-center gap-3">
          <div className={`flex items-center gap-2 px-3 py-1 rounded-full border ${
            isConnected ? 'bg-green-500/10 border-green-500/30' : 'bg-yellow-500/10 border-yellow-500/30'
          }`}>
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500 animate-pulse' : 'bg-yellow-500'}`} />
            <span className="text-xs font-medium">{isConnected ? '实时监控中' : '连接中...'}</span>
          </div>
          <button
            onClick={loadChanges}
            disabled={isLoading}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 text-sm hover:bg-white/10 transition-all"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            刷新
          </button>
        </div>
      </div>

      <div className="flex items-center gap-2 mb-4">
        <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-white/5 border border-white/10">
          <Filter className="w-4 h-4 text-gray-500" />
          {['all', 'created', 'modified', 'deleted'].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1 rounded-md text-xs font-medium transition-all ${
                f === filter
                  ? 'bg-cyan-500/20 text-cyan-400'
                  : 'text-gray-400 hover:bg-white/5'
              }`}
            >
              {f === 'all' ? '全部' :
               f === 'created' ? '新增' :
               f === 'modified' ? '修改' : '删除'
              }
            </button>
          ))}
        </div>
      </div>

      <div className="flex-1 glass-card overflow-hidden">
        <div className="p-4 border-b border-white/5 flex items-center gap-3">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-cyan-500/20 to-blue-500/20 flex items-center justify-center">
            <FileText className="w-4 h-4 text-cyan-400" />
          </div>
          <div>
            <h2 className="font-semibold">变更记录</h2>
          </div>
        </div>
        <div className="p-4 overflow-y-auto h-[calc(100%-72px)]">
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <RefreshCw className="w-5 h-5 text-gray-500 animate-spin mr-2" />
              <span className="text-gray-500 text-sm">加载中...</span>
            </div>
          ) : filteredChanges.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12">
              <Zap className="w-12 h-12 text-gray-600 mb-3" />
              <p className="text-gray-500 text-sm">暂无变更记录</p>
            </div>
          ) : (
            <div className="space-y-2">
              {filteredChanges.map((change, idx) => (
                <div
                  key={change.id || idx}
                  className="p-3 rounded-lg bg-white/5 border border-white/5 flex items-center justify-between"
                >
                  <div className="flex items-center gap-3">
                    <div className={`px-2 py-1 rounded-md text-xs font-medium border ${getChangeTypeColor(change.change_type)}`}>
                      {getChangeTypeName(change.change_type)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium truncate">
                        {change.file_path}
                      </div>
                      <div className="text-xs text-gray-500 flex items-center gap-1">
                        <Clock className="w-3 h-3 inline" />
                        {formatTime(change.created_at || '')}
                      </div>
                    </div>
                  </div>
                  {change.entities_count && (
                    <div className="text-xs text-gray-500 bg-white/5 px-2 py-1 rounded">
                      {change.entities_count} 个实体
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
