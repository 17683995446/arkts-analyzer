import { useEffect, useState } from 'react'
import { Layers, Search, ChevronRight } from 'lucide-react'
import { api } from '@/services/api'
import { useAppStore } from '@/stores/appStore'

export function ComponentTree() {
  const { classes: components } = useAppStore()
  const [searchTerm, setSearchTerm] = useState('')
  const [expandedNodes, setExpandedNodes] = useState<Set<number>>(new Set())

  useEffect(() => {
    loadComponents()
  }, [])

  const loadComponents = async () => {
    try {
      const data = await api.getClasses(1, 100)
      useAppStore.getState().setClasses(data.items || [])
    } catch (error) {
      console.error('Failed to load components:', error)
    }
  }

  const toggleNode = (id: number) => {
    const newExpanded = new Set(expandedNodes)
    if (newExpanded.has(id)) {
      newExpanded.delete(id)
    } else {
      newExpanded.add(id)
    }
    setExpandedNodes(newExpanded)
  }

  const filteredComponents = searchTerm
    ? components.filter(c =>
        c.name.toLowerCase().includes(searchTerm.toLowerCase())
      )
    : components

  return (
    <div className="h-full flex flex-col">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">
          <span className="gradient-text">组件树</span>
        </h1>
        <p className="text-gray-400">浏览ArkTS组件结构</p>
      </div>

      <div className="flex-1 glass-card overflow-hidden">
        <div className="p-4 border-b border-white/5">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="搜索组件..."
              className="w-full pl-10 pr-4 py-2 rounded-lg bg-white/5 border border-white/10 text-sm focus:outline-none focus:border-cyan-500/50"
            />
          </div>
        </div>
        <div className="p-4 overflow-y-auto h-[calc(100%-80px)]">
          {filteredComponents.length === 0 ? (
            <p className="text-gray-500 text-sm text-center py-8">暂无组件数据</p>
          ) : (
            <div className="space-y-1">
              {filteredComponents.map(component => (
                <div key={component.id} className="text-sm">
                  <div
                    className="flex items-center gap-2 px-2 py-1 rounded-lg hover:bg-white/5 cursor-pointer"
                    onClick={() => toggleNode(component.id)}
                  >
                    <div className="flex items-center gap-2">
                      <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-purple-500/20 to-pink-500/20 flex items-center justify-center">
                        <Layers className="w-3 h-3 text-purple-400" />
                      </div>
                      <span className="font-medium text-gray-200">{component.name}</span>
                    </div>
                    <ChevronRight className={`w-4 h-4 text-gray-500 transition-transform ${expandedNodes.has(component.id) ? 'rotate-90' : ''}`} />
                  </div>
                  {expandedNodes.has(component.id) && component.methods && component.methods.length > 0 && (
                    <div className="ml-6 mt-1 space-y-1">
                      {component.methods.map((method: any) => (
                        <div
                          key={method.id}
                          className="flex items-center gap-2 px-2 py-1 rounded-lg text-gray-400 text-xs"
                        >
                          <div className="w-1 h-1 rounded-full bg-cyan-500/50" />
                          <span>{method.name}()</span>
                        </div>
                      ))}
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
