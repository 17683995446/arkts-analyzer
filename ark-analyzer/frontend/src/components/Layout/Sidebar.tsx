import { NavLink } from 'react-router-dom'
import { Home, GitBranch, Phone, Layers, FileText, Settings } from 'lucide-react'

const navItems = [
  { path: '/', icon: Home, label: '概览' },
  { path: '/graph', icon: GitBranch, label: '类关系图' },
  { path: '/calls', icon: Phone, label: '调用链' },
  { path: '/components', icon: Layers, label: '组件树' },
  { path: '/changes', icon: FileText, label: '变更历史' },
  { path: '/settings', icon: Settings, label: '设置' },
]

export function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-[#0d0d14] border-r border-white/5 z-40">
      <div className="flex items-center gap-3 px-6 py-6 border-b border-white/5">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-purple-600 flex items-center justify-center">
          <GitBranch className="w-6 h-6 text-white" />
        </div>
        <div>
          <h1 className="text-lg font-bold gradient-text">ArkAnalyzer</h1>
          <p className="text-xs text-gray-500">知识图谱系统</p>
        </div>
      </div>

      <nav className="px-3 py-4">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-xl mb-1 transition-all duration-200 ${
                isActive
                  ? 'bg-gradient-to-r from-cyan-500/20 to-purple-500/20 text-cyan-400 border border-cyan-500/30'
                  : 'text-gray-400 hover:text-white hover:bg-white/5'
              }`
            }
          >
            {({ isActive }) => (
              <>
                <item.icon className="w-5 h-5" />
                <span className="font-medium">{item.label}</span>
                {isActive && (
                  <div className="ml-auto w-1.5 h-1.5 rounded-full bg-cyan-400" />
                )}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-white/5">
        <div className="glass-card p-4">
          <p className="text-xs text-gray-500 mb-2">基于第一性原理</p>
          <p className="text-xs text-gray-400">
            增量更新 · 实时同步 · 高性能
          </p>
        </div>
      </div>
    </aside>
  )
}
