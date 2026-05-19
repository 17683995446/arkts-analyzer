import { useEffect, useState } from 'react'
import { Phone, Search, ArrowRight, RefreshCw } from 'lucide-react'
import { api } from '@/services/api'
import { useAppStore } from '@/stores/appStore'

export function CallChain() {
  const { methods } = useAppStore()
  const [fromMethod, setFromMethod] = useState<number | null>(null)
  const [toMethod, setToMethod] = useState<number | null>(null)
  const [callChain, setCallChain] = useState<any>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    loadMethods()
  }, [])

  const loadMethods = async () => {
    try {
      const data = await api.getMethods(1, 100)
      useAppStore.getState().setMethods(data.items || [])
    } catch (error) {
      console.error('Failed to load methods:', error)
    }
  }

  const handleTrace = async () => {
    if (!fromMethod || !toMethod) return
    setIsLoading(true)
    try {
      const chain = await api.getCallChain(fromMethod, toMethod)
      setCallChain(chain)
    } catch (error) {
      console.error('Failed to trace call chain:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const filteredMethods = searchTerm
    ? methods.filter(m => m.name.toLowerCase().includes(searchTerm.toLowerCase()))
    : methods

  return (
    <div className="h-full flex flex-col">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">
          <span className="gradient-text">调用链追踪</span>
        </h1>
        <p className="text-gray-400">追踪方法之间的调用关系</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <div className="glass-card p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-500 flex items-center justify-center">
              <Phone className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="font-semibold">方法选择</h2>
            </div>
          </div>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-2">源方法</label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="搜索方法..."
                  className="w-full pl-10 pr-4 py-2 rounded-lg bg-white/5 border border-white/10 text-sm focus:outline-none focus:border-cyan-500/50 mb-3"
                />
              </div>
              <select
                value={fromMethod || ''}
                onChange={(e) => setFromMethod(Number(e.target.value) || null)}
                className="w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-sm focus:outline-none focus:border-cyan-500/50"
              >
                <option value="">选择源方法</option>
                {filteredMethods.map(m => (
                  <option key={m.id} value={m.id}>{m.name}</option>
                ))}
              </select>
            </div>
            <div className="flex items-center justify-center">
              <ArrowRight className="w-6 h-6 text-gray-500" />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-2">目标方法</label>
              <select
                value={toMethod || ''}
                onChange={(e) => setToMethod(Number(e.target.value) || null)}
                className="w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-sm focus:outline-none focus:border-cyan-500/50"
              >
                <option value="">选择目标方法</option>
                {filteredMethods.map(m => (
                  <option key={m.id} value={m.id}>{m.name}</option>
                ))}
              </select>
            </div>
            <button
              onClick={handleTrace}
              disabled={isLoading || !fromMethod || !toMethod}
              className="w-full py-2 rounded-lg bg-gradient-to-r from-cyan-500 to-purple-500 text-white font-medium disabled:opacity-50 flex items-center justify-center gap-2"
            >
              <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
              {isLoading ? '追踪中...' : '追踪调用链'}
            </button>
          </div>
        </div>
        <div className="glass-card p-6">
          <h2 className="font-semibold mb-4">调用链结果</h2>
          {callChain ? (
            <div className="space-y-2">
              {callChain.map((item: any, idx: number) => (
                <div key={idx} className="flex items-center gap-2 px-3 py-2 rounded-lg bg-white/5">
                  <div className="w-6 h-6 rounded-full bg-cyan-500/20 text-cyan-400 flex items-center justify-center text-xs font-bold">
                    {idx + 1}
                  </div>
                  <span className="font-mono text-sm">{item.name}</span>
                  {idx < callChain.length - 1 && <ArrowRight className="w-4 h-4 text-gray-500" />}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-sm text-center py-8">选择方法并点击“追踪调用链”开始</p>
          )}
        </div>
      </div>
    </div>
  )
}
