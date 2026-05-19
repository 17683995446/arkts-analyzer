import { Routes, Route } from 'react-router-dom'
import { Sidebar } from '@/components/Layout/Sidebar'
import { Dashboard } from '@/pages/Dashboard'
import { GraphView } from '@/pages/GraphView'
import { CallChain } from '@/pages/CallChain'
import { ComponentTree } from '@/pages/ComponentTree'
import { ChangeHistory } from '@/pages/ChangeHistory'
import { Settings } from '@/pages/Settings'

function App() {
  return (
    <div className="min-h-screen bg-[#0a0a0f]">
      <Sidebar />
      <main className="ml-64 p-8 min-h-screen">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/graph" element={<GraphView />} />
          <Route path="/calls" element={<CallChain />} />
          <Route path="/components" element={<ComponentTree />} />
          <Route path="/changes" element={<ChangeHistory />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
