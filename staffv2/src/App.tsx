import { useState, useEffect } from 'react'
import './App.css'
import { fetchAIConfig, askModel, type AIConfig } from './lib/apiClient'

interface Nanobot {
  id: number;
  name: string;
  status: 'idle' | 'building' | 'complete' | 'error';
  progress: number;
  model: string;
}

function App() {
  const [config, setConfig] = useState<AIConfig | null>(null)
  const [nanobots, setNanobots] = useState<Nanobot[]>([])
  const [isBuilding, setIsBuilding] = useState(false)
  const [prompt, setPrompt] = useState('')
  const [response, setResponse] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadConfig()
  }, [])

  const loadConfig = async () => {
    try {
      const cfg = await fetchAIConfig()
      setConfig(cfg)
    } catch (err) {
      console.error('Failed to load config:', err)
      setConfig({ gptVersion: 'gpt-5', enableGpt5: false })
    }
  }

  const buildNanobot = () => {
    if (isBuilding) return
    
    const id = Date.now()
    const newBot: Nanobot = {
      id,
      name: `Bot-${nanobots.length + 1}`,
      status: 'building',
      progress: 0,
      model: config?.gptVersion || 'gpt-5'
    }
    
    setNanobots(prev => [...prev, newBot])
    setIsBuilding(true)
    
    // Simulate build progress
    const interval = setInterval(() => {
      setNanobots(prev => prev.map(bot => {
        if (bot.id === id && bot.progress < 100) {
          const newProgress = bot.progress + Math.random() * 15
          if (newProgress >= 100) {
            clearInterval(interval)
            setIsBuilding(false)
            return { ...bot, progress: 100, status: 'complete' }
          }
          return { ...bot, progress: newProgress }
        }
        return bot
      }))
    }, 200)
  }

  const handleAsk = async () => {
    if (!prompt.trim() || loading) return
    
    setLoading(true)
    setResponse('')
    
    try {
      const result = await askModel(prompt)
      setResponse(`[${result.model}] ${result.reply}`)
    } catch (err) {
      setResponse(`Error: ${err instanceof Error ? err.message : 'Failed to get response'}`)
    } finally {
      setLoading(false)
    }
  }

  const clearBots = () => {
    setNanobots([])
  }

  return (
    <div className="app">
      <header className="header">
        <h1>🤖 Staff Bot Nanobot Simulation</h1>
        <div className="config-badge">
          {config ? (
            <>
              <span className={`model-badge ${config.enableGpt5 ? 'enabled' : 'disabled'}`}>
                {config.gptVersion.toUpperCase()}
              </span>
              <span className="status-text">
                {config.enableGpt5 ? '✓ Enabled' : '✗ Disabled'}
              </span>
            </>
          ) : (
            <span>Loading...</span>
          )}
        </div>
      </header>

      <main className="main">
        <section className="build-section">
          <h2>Build Nanobots</h2>
          <div className="controls">
            <button 
              onClick={buildNanobot} 
              disabled={isBuilding}
              className="btn btn-primary"
            >
              {isBuilding ? 'Building...' : 'Build Nanobot'}
            </button>
            <button 
              onClick={clearBots} 
              disabled={nanobots.length === 0}
              className="btn btn-secondary"
            >
              Clear All
            </button>
          </div>
          
          <div className="nanobots-grid">
            {nanobots.map(bot => (
              <div key={bot.id} className={`nanobot-card status-${bot.status}`}>
                <div className="nanobot-header">
                  <h3>{bot.name}</h3>
                  <span className="model-tag">{bot.model}</span>
                </div>
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{ width: `${bot.progress}%` }}
                  />
                </div>
                <div className="nanobot-status">
                  {bot.status === 'building' && `Building... ${Math.round(bot.progress)}%`}
                  {bot.status === 'complete' && '✓ Complete'}
                  {bot.status === 'error' && '✗ Error'}
                  {bot.status === 'idle' && 'Idle'}
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="ask-section">
          <h2>Ask Staff Bot</h2>
          <div className="ask-controls">
            <input
              type="text"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleAsk()}
              placeholder="Enter your prompt..."
              className="prompt-input"
            />
            <button 
              onClick={handleAsk} 
              disabled={loading || !prompt.trim()}
              className="btn btn-primary"
            >
              {loading ? 'Asking...' : 'Ask'}
            </button>
          </div>
          {response && (
            <div className="response-box">
              <pre>{response}</pre>
            </div>
          )}
        </section>
      </main>
    </div>
  )
}

export default App
