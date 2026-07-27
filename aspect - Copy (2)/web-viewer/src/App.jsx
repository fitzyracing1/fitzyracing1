import { useState, useEffect } from 'react'
import './App.css'
import { topics } from './topics'

function App() {
  const [primeGameData, setPrimeGameData] = useState(null)
  const [inventoryData, setInventoryData] = useState(null)
  const [dataSets, setDataSets] = useState([])
  const [activeTab, setActiveTab] = useState('prime')
  const [isSimulating, setIsSimulating] = useState(false)
  const [aiResults, setAiResults] = useState(null)
  const [bingLoading, setBingLoading] = useState(false)
  const [bingResults, setBingResults] = useState({})
  const [searchQuery, setSearchQuery] = useState('')
  const [globalLoading, setGlobalLoading] = useState(false)
  const [globalResults, setGlobalResults] = useState([])

  // Load data from JSON files
  useEffect(() => {
    loadData()
    loadAiResults()
  }, [])

  const loadData = async () => {
    try {
      // Load Prime Game data
      const primeResponse = await fetch('../UnrealExport/PrimeGame_20251124000036.json')
      const primeData = await primeResponse.json()
      setPrimeGameData(primeData)

      // Load Inventory data
      const inventoryResponse = await fetch('../UnrealExport/Inventory_20251124000036.json')
      const inventoryData = await inventoryResponse.json()
      setInventoryData(inventoryData)

      // Load DataSet samples
      const dataSetIds = [
        '66b5e9d0-0162-42a3-a875-4002bede3a1c',
        '1be6b589-4209-469c-8fef-ee7544ebd65a'
      ]
      
      const datasets = []
      for (const id of dataSetIds) {
        try {
          const response = await fetch(`../UnrealExport/DataSet_${id}.json`)
          const data = await response.json()
          datasets.push(data)
        } catch (e) {
          console.log('Could not load dataset:', id)
        }
      }
      setDataSets(datasets)
    } catch (error) {
      console.error('Error loading data:', error)
    }
  }

  const startSimulation = () => {
    setIsSimulating(true)
    setTimeout(() => setIsSimulating(false), 3000)
  }

  const loadAiResults = async () => {
    try {
      const res = await fetch('/algorithm_check_results.json')
      const data = await res.json()
      setAiResults(data)
    } catch (e) {
      console.error('Failed to load AI results:', e)
    }
  }

  const sampleAiResults = () => {
    if (!aiResults?.test_results?.length) return []
    const total = aiResults.test_results.length
    const count = Math.max(1, Math.floor(total * 0.03))
    return aiResults.test_results.slice(0, count)
  }

  const bingKey = import.meta.env.VITE_BING_SEARCH_KEY
  const canSearch = !!bingKey

  const runBingSearch = async (topic) => {
    if (!canSearch) return
    try {
      setBingLoading(true)
      const url = `https://api.bing.microsoft.com/v7.0/search?q=${encodeURIComponent(topic.query)}&responseFilter=Webpages&count=5`
      const resp = await fetch(url, {
        headers: { 'Ocp-Apim-Subscription-Key': bingKey }
      })
      if (!resp.ok) throw new Error(`Bing search failed: ${resp.status}`)
      const json = await resp.json()
      const items = json.webPages?.value?.map(v => ({ name: v.name, url: v.url })) || []
      setBingResults(prev => ({ ...prev, [topic.name]: items }))
    } catch (err) {
      console.error(err)
    } finally {
      setBingLoading(false)
    }
  }

  const runGlobalSearch = async () => {
    const q = searchQuery.trim()
    if (!q) return
    if (!canSearch) {
      // Fallback: filter topics and show their links instead of web results
      const matched = topics
        .filter(t => (
          t.name.toLowerCase().includes(q.toLowerCase()) ||
          t.summary.toLowerCase().includes(q.toLowerCase())
        ))
        .flatMap(t => t.links.map(l => ({ name: `${t.name}: ${l.title}`, url: l.url })))
      setGlobalResults(matched)
      return
    }
    try {
      setGlobalLoading(true)
      const url = `https://api.bing.microsoft.com/v7.0/search?q=${encodeURIComponent(q)}&responseFilter=Webpages&count=8`
      const resp = await fetch(url, { headers: { 'Ocp-Apim-Subscription-Key': bingKey } })
      if (!resp.ok) throw new Error(`Bing search failed: ${resp.status}`)
      const json = await resp.json()
      const items = json.webPages?.value?.map(v => ({ name: v.name, url: v.url })) || []
      setGlobalResults(items)
    } catch (err) {
      console.error(err)
    } finally {
      setGlobalLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="header">
        <h1>🎮 Aspect Control Unit Viewer</h1>
        <p>Real-time Data Pipeline Visualization</p>
      </header>

      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'prime' ? 'active' : ''}`}
          onClick={() => setActiveTab('prime')}
        >
          Prime Game
        </button>
        <button 
          className={`tab ${activeTab === 'inventory' ? 'active' : ''}`}
          onClick={() => setActiveTab('inventory')}
        >
          Inventory
        </button>
        <button 
          className={`tab ${activeTab === 'datasets' ? 'active' : ''}`}
          onClick={() => setActiveTab('datasets')}
        >
          DataSets
        </button>
        <button 
          className={`tab ${activeTab === 'simulation' ? 'active' : ''}`}
          onClick={() => setActiveTab('simulation')}
        >
          Live Simulation
        </button>
        <button 
          className={`tab ${activeTab === 'ai' ? 'active' : ''}`}
          onClick={() => setActiveTab('ai')}
        >
          AI Results & Search
        </button>
      </div>

      <main className="content">
        {activeTab === 'prime' && primeGameData && (
          <div className="panel prime-game">
            <h2>Prime Number Game State</h2>
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-value">{primeGameData.Score}</div>
                <div className="stat-label">Total Score</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{primeGameData.PrimesFound?.length || 0}</div>
                <div className="stat-label">Primes Found</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{primeGameData.CurrentNumber}</div>
                <div className="stat-label">Last Number</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{primeGameData.IsPrime ? '✓' : '✗'}</div>
                <div className="stat-label">Is Prime</div>
              </div>
            </div>
            <div className="primes-list">
              <h3>Prime Numbers Discovered:</h3>
              <div className="primes">
                {primeGameData.PrimesFound?.map((prime, idx) => (
                  <span key={idx} className="prime-badge">{prime}</span>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'inventory' && inventoryData && (
          <div className="panel inventory">
            <h2>Inventory Items ({inventoryData.length})</h2>
            <div className="inventory-grid">
              {inventoryData.map((item, idx) => (
                <div key={idx} className="inventory-item">
                  <div className="item-header">
                    <span className="item-id">{item.Id}</span>
                    <span className={`category-badge ${item.Category.toLowerCase()}`}>
                      {item.Category}
                    </span>
                  </div>
                  <h3>{item.Name}</h3>
                  <div className="item-value">Value: {item.Value}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'datasets' && (
          <div className="panel datasets">
            <h2>Data Sets ({dataSets.length})</h2>
            {dataSets.map((dataset, idx) => (
              <div key={idx} className="dataset-card">
                <h3>{dataset.Source}</h3>
                <p className="dataset-id">ID: {dataset.Id}</p>
                <div className="values-display">
                  <strong>Values:</strong>
                  <div className="values-list">
                    {dataset.Values?.map((val, i) => (
                      <span key={i} className="value-chip">{val}</span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'simulation' && (
          <div className="panel simulation">
            <h2>Live Data Pipeline Simulation</h2>
            <div className="simulation-container">
              <div className="pipeline-flow">
                <div className={`pipeline-step ${isSimulating ? 'active' : ''}`}>
                  <div className="step-icon">📦</div>
                  <div className="step-title">Inventory Manager</div>
                  <div className="step-desc">10 items loaded</div>
                </div>
                <div className="arrow">→</div>
                <div className={`pipeline-step ${isSimulating ? 'active delay-1' : ''}`}>
                  <div className="step-icon">📊</div>
                  <div className="step-title">DataSet Creation</div>
                  <div className="step-desc">2 datasets generated</div>
                </div>
                <div className="arrow">→</div>
                <div className={`pipeline-step ${isSimulating ? 'active delay-2' : ''}`}>
                  <div className="step-icon">🎲</div>
                  <div className="step-title">Prime Game Engine</div>
                  <div className="step-desc">7 primes identified</div>
                </div>
                <div className="arrow">→</div>
                <div className={`pipeline-step ${isSimulating ? 'active delay-3' : ''}`}>
                  <div className="step-icon">🚀</div>
                  <div className="step-title">Unreal Distribution</div>
                  <div className="step-desc">16 files exported</div>
                </div>
              </div>
              
              <button 
                className="simulate-btn"
                onClick={startSimulation}
                disabled={isSimulating}
              >
                {isSimulating ? '⚡ Simulating...' : '▶ Run Simulation'}
              </button>

              {primeGameData && (
                <div className="simulation-results">
                  <h3>Last Pipeline Execution</h3>
                  <div className="result-stats">
                    <p>✓ Score: {primeGameData.Score}</p>
                    <p>✓ Primes: {primeGameData.PrimesFound?.length}</p>
                    <p>✓ Status: Complete</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'ai' && (
          <div className="panel ai-results">
            <h2>AI Results Sample (3%)</h2>
            {!aiResults && <p>Loading AI results…</p>}
            {aiResults && (
              <div>
                <p>Total tests: {aiResults.total_tests} • Passed: {aiResults.passed} • Failed: {aiResults.failed}</p>
                <ul className="ai-sample-list">
                  {sampleAiResults().map((t, i) => (
                    <li key={i} className="ai-sample-item">
                      <strong>{t.test_name}</strong> — expected {String(t.expected)} • actual {String(t.actual)} • {t.passed ? 'Passed' : 'Failed'}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <div className="search-bar">
              <input
                type="text"
                className="search-input"
                placeholder="Search numeric topics or the web…"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
              <button className="search-btn" onClick={runGlobalSearch} disabled={globalLoading}>
                {globalLoading ? 'Searching…' : 'Search'}
              </button>
              {!canSearch && searchQuery.trim() && (
                <a
                  className="open-in-browser"
                  href={`https://www.bing.com/search?q=${encodeURIComponent(searchQuery.trim())}`}
                  target="_blank"
                  rel="noreferrer"
                >Open in browser</a>
              )}
            </div>

            {globalResults.length > 0 && (
              <div className="global-results">
                <h3>Search Results</h3>
                <div className="result-grid">
                  {globalResults.map((r, idx) => (
                    <a key={idx} className="result-card" href={r.url} target="_blank" rel="noreferrer">
                      <div className="result-title">{r.name}</div>
                      <div className="result-url">{r.url}</div>
                    </a>
                  ))}
                </div>
              </div>
            )}

            <h2>Authoritative References</h2>
            <div className="topics">
              {topics.map((topic) => (
                <div key={topic.name} className="topic-card">
                  <div className="topic-header">
                    <h3>{topic.name}</h3>
                    <p className="topic-summary">{topic.summary}</p>
                  </div>
                  <ul className="link-list">
                    {topic.links.map((l) => (
                      <li key={l.url}><a href={l.url} target="_blank" rel="noreferrer">{l.title}</a></li>
                    ))}
                  </ul>
                  <div className="search-actions">
                    <button onClick={() => runBingSearch(topic)} disabled={!canSearch || bingLoading}>
                      {bingLoading ? 'Searching…' : (canSearch ? 'Search Web (Bing)' : 'Search Disabled')}
                    </button>
                    {!canSearch && (
                      <small>Set VITE_BING_SEARCH_KEY to enable live search.</small>
                    )}
                  </div>
                  {bingResults[topic.name] && (
                    <div className="bing-results">
                      <h4>Web Results</h4>
                      <ul>
                        {bingResults[topic.name].map((r, idx) => (
                          <li key={idx}><a href={r.url} target="_blank" rel="noreferrer">{r.name}</a></li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      <footer className="footer">
        <p>Aspect Control Unit • Powered by C# & Unreal Engine Integration</p>
      </footer>
    </div>
  )
}

export default App
