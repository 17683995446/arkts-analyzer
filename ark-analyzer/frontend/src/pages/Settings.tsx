import { useState, useEffect } from 'react'
import { FolderOpen, Key, Clock, Brain, Save, CheckCircle } from 'lucide-react'

export function Settings() {
  const [watchPath, setWatchPath] = useState('')
  const [apiKey, setApiKey] = useState('')
  const [debounceSeconds, setDebounceSeconds] = useState(1.0)
  const [enableLlMAnalysis, setEnableLlMAnalysis] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [saveSuccess, setSaveSuccess] = useState(false)

  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = () => {
    const savedConfig = localStorage.getItem('ark-analyzer-config')
    if (savedConfig) {
      const config = JSON.parse(savedConfig)
      setWatchPath(config.watchPath || '')
      setApiKey(config.apiKey || '')
      setDebounceSeconds(config.debounceSeconds || 1.0)
      setEnableLlMAnalysis(config.enableLlMAnalysis !== false)
    }
  }

  const handleSave = async () => {
    setIsSaving(true)
    try {
      localStorage.setItem('ark-analyzer-config', JSON.stringify({
        watchPath,
        apiKey,
        debounceSeconds,
        enableLlMAnalysis
      }))
      
      setSaveSuccess(true)
      setTimeout(() => setSaveSuccess(false), 3000)
    } catch (error) {
      console.error('Failed to save settings:', error)
    } finally {
      setIsSaving(false)
    }
  }

  return (
    <div className="h-full flex flex-col">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">
          <span className="gradient-text">系统设置</span>
        </h1>
        <p className="text-gray-400">配置ArkAnalyzer的各项参数</p>
      </div>

      <div className="flex-1 overflow-y-auto space-y-6">
        <div className="glass-card p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center">
              <FolderOpen className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="font-semibold">监控路径</h2>
              <p className="text-xs text-gray-500">设置要监控的代码目录</p>
            </div>
          </div>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-2">项目路径</label>
              <input
                type="text"
                value={watchPath}
                onChange={(e) => setWatchPath(e.target.value)}
                placeholder="/path/to/your/arkts/project"
                className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-sm focus:outline-none focus:border-cyan-500/50"
              />
            </div>
          </div>
        </div>

        <div className="glass-card p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
              <Key className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="font-semibold">API 配置</h2>
              <p className="text-xs text-gray-500">配置LLM服务认证信息</p>
            </div>
          </div>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-2">硅基流动 API Key</label>
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                placeholder="sk-xxxxxxxxxxxxxxxx"
                className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-sm focus:outline-none focus:border-cyan-500/50 font-mono"
              />
              <p className="text-xs text-gray-500 mt-2">
                用于调用硅基流动的免费LLM模型进行语义分析
              </p>
            </div>
          </div>
        </div>

        <div className="glass-card p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-orange-500 to-red-500 flex items-center justify-center">
              <Clock className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="font-semibold">更新策略</h2>
              <p className="text-xs text-gray-500">配置增量更新的行为</p>
            </div>
          </div>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-2">
                防抖延迟 (秒)
              </label>
              <input
                type="number"
                step="0.1"
                min="0.1"
                max="10"
                value={debounceSeconds}
                onChange={(e) => setDebounceSeconds(parseFloat(e.target.value))}
                className="w-full px-4 py-3 rounded-xl bg-white/5 border border-white/10 text-sm focus:outline-none focus:border-cyan-500/50"
              />
              <p className="text-xs text-gray-500 mt-2">
                连续修改同一文件时，等待 {debounceSeconds} 秒后再更新
              </p>
            </div>
          </div>
        </div>

        <div className="glass-card p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-green-500 to-emerald-500 flex items-center justify-center">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="font-semibold">LLM 语义分析</h2>
              <p className="text-xs text-gray-500">启用后使用LLM增强代码理解</p>
            </div>
          </div>
          <div className="space-y-4">
            <label className="flex items-center gap-3 cursor-pointer">
              <div className={`w-12 h-6 rounded-full transition-colors relative ${
                enableLlMAnalysis ? 'bg-cyan-500' : 'bg-white/10'
              }`}>
                <div className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-transform ${
                  enableLlMAnalysis ? 'left-7' : 'left-1'
                }`} />
              </div>
              <span className="text-sm">
                {enableLlMAnalysis ? '已启用' : '已禁用'}
              </span>
            </label>
            <p className="text-xs text-gray-500">
              启用LLM分析可以获得更准确的类关系和调用链理解，但会增加处理时间
            </p>
          </div>
        </div>

        <div className="flex justify-end">
          <button
            onClick={handleSave}
            disabled={isSaving}
            className={`flex items-center gap-2 px-6 py-3 rounded-xl font-medium transition-all ${
              saveSuccess
                ? 'bg-green-500 text-white'
                : 'bg-gradient-to-r from-cyan-500 to-purple-500 text-white hover:shadow-lg hover:shadow-cyan-500/20'
            } disabled:opacity-50`}
          >
            {saveSuccess ? (
              <>
                <CheckCircle className="w-5 h-5" />
                保存成功
              </>
            ) : (
              <>
                <Save className="w-5 h-5" />
                {isSaving ? '保存中...' : '保存设置'}
              </>
            )}
          </button>
        </div>

        <div className="glass-card p-6">
          <h2 className="font-semibold mb-4">系统信息</h2>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">版本</span>
              <span>1.0.0</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">前端框架</span>
              <span>React 18 + TypeScript</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">后端框架</span>
              <span>FastAPI + Python</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">数据库</span>
              <span>SQLite</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">LLM服务</span>
              <span>硅基流动</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
