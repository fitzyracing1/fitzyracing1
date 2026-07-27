import { useState, useEffect } from 'react'
import './App.css'
import { topics } from './topics'

function App() {
  const [primeGameData, setPrimeGameData] = useState(null)
  const [inventoryData, setInventoryData] = useState(null)
  const [dataSets, setDataSets] = useState([])
  const [activeTab, setActiveTab] = useState('prime')
  const [isSimulating, setIsSimulating] = useState(false)
  const [algorithmMeta, setAlgorithmMeta] = useState(null)
  const [sampledResults, setSampledResults] = useState([])
  const [searchResults, setSearchResults] = useState({})
  const [searchingTopic, setSearchingTopic] = useState(null)
  const [searchError, setSearchError] = useState(null)
  const bingKey = import.meta.env.VITE_BING_SEARCH_KEY || null

  // Load data from JSON files
  useEffect(() => {
    loadData()
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

      // Load algorithm check results for AI tab
      const algoResponse = await fetch('/algorithm_check_results.json')
      const algoData = await algoResponse.json()
      const results = algoData.test_results || []
      const sampleSize = Math.max(1, Math.ceil(results.length * 0.03))
      setAlgorithmMeta({
        generatedAt: algoData.generated_at,
        total: algoData.total_tests,
        passed: algoData.passed,
        failed: algoData.failed
      })
      setSampledResults(results.slice(0, sampleSize))
    } catch (error) {
      console.error('Error loading data:', error)
    }
  }

  const performSearch = async (topic) => {
    setSearchError(null)
    setSearchingTopic(topic.name)

    if (!bingKey) {
      setSearchResults(prev => ({
        ...prev,
        [topic.name]: {
          source: 'static',
          items: topic.links
        }
      }))
      setSearchingTopic(null)
      return
    }

    try {
      const response = await fetch(
        `https://api.bing.microsoft.com/v7.0/search?q=${encodeURIComponent(topic.query)}&count=5`,
        {
          headers: {
            'Ocp-Apim-Subscription-Key': bingKey
          }
        }
      )

      if (!response.ok) {
        throw new Error(`Search failed (${response.status})`)
      }

      const data = await response.json()
      const items = (data.webPages?.value || []).map(entry => ({
        title: entry.name,
        url: entry.url,
        snippet: entry.snippet
      }))

      setSearchResults(prev => ({
        ...prev,
        [topic.name]: {
          source: items.length ? 'bing' : 'static',
          items: items.length ? items : topic.links
        }
      }))
    } catch (err) {
      setSearchError(err.message)
      setSearchResults(prev => ({
        ...prev,
        [topic.name]: {
          source: 'static',
          items: topic.links
        }
      }))
    } finally {
      setSearchingTopic(null)
    }
  }

  const runAllSearches = async () => {
    for (const topic of topics) {
      await performSearch(topic)
    }
  }

  const startSimulation = () => {
    setIsSimulating(true)
    setTimeout(() => setIsSimulating(false), 3000)
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
          AI Results
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
            <div className="ai-header">
              <div>
                <h2>AI Results & References</h2>
                <p>Shows 3% sample of algorithm checks and curated references. Add a Bing key to enable live search.</p>
              </div>
              <div className="ai-actions">
                <button className="simulate-btn" onClick={runAllSearches} disabled={searchingTopic !== null}>
                  {searchingTopic ? `Searching ${searchingTopic}...` : 'Run search for all topics'}
                </button>
                {!bingKey && <span className="inline-hint">Set VITE_BING_SEARCH_KEY to enable live web search.</span>}
              </div>
            </div>

            {algorithmMeta && (
              <div className="ai-metrics">
                <div className="metric-card">
                  <div className="metric-label">Generated</div>
                  <div className="metric-value">{new Date(algorithmMeta.generatedAt).toLocaleString()}</div>
                </div>
                <div className="metric-card">
                  <div className="metric-label">Total Tests</div>
                  <div className="metric-value">{algorithmMeta.total}</div>
                </div>
                <div className="metric-card success">
                  <div className="metric-label">Passed</div>
                  <div className="metric-value">{algorithmMeta.passed}</div>
                </div>
                <div className="metric-card muted">
                  <div className="metric-label">Failed</div>
                  <div className="metric-value">{algorithmMeta.failed}</div>
                </div>
              </div>
            )}

            <div className="sample-section">
              <h3>3% Sample (min 1) from algorithm_check_results.json</h3>
              <div className="sample-grid">
                {sampledResults.map((result, idx) => (
                  <div key={idx} className="sample-card">
                    <div className="sample-name">{result.test_name}</div>
                    <div className={`sample-status ${result.passed ? 'pass' : 'fail'}`}>{result.passed ? 'PASS' : 'FAIL'}</div>
                    <div className="sample-values">
                      <span>A: {String(result.value_a)}</span>
                      <span>B: {String(result.value_b)}</span>
                    </div>
                    <div className="sample-expected">Expected: {String(result.expected)}</div>
                    <div className="sample-actual">Actual: {String(result.actual)}</div>
                  </div>
                ))}
              </div>
            </div>

            {searchError && <div className="error-banner">Search error: {searchError}</div>}

            <div className="topics-section">
              <h3>Topics & References</h3>
              <div className="topics-grid">
                {topics.map(topic => (
                  <div key={topic.name} className="topic-card">
                    <div className="topic-header">
                      <div>
                        <h4>{topic.name}</h4>
                        <p>{topic.summary}</p>
                      </div>
                      <button
                        className="simulate-btn"
                        onClick={() => performSearch(topic)}
                        disabled={searchingTopic === topic.name}
                      >
                        {searchingTopic === topic.name ? 'Searching...' : 'Search'}
                      </button>
                    </div>

                    <div className="links">
                      {(searchResults[topic.name]?.items || topic.links).map((link, idx) => (
                        <a key={idx} href={link.url} target="_blank" rel="noreferrer" className="link-item">
                          <div className="link-title">{link.title || link.url}</div>
                          {link.snippet && <div className="link-snippet">{link.snippet}</div>}
                        </a>
                      ))}
                    </div>

                    <div className="source-label">
                      Source: {searchResults[topic.name]?.source === 'bing' ? 'Bing Web Search' : 'Curated references'}
                    </div>
                  </div>
                ))}
              </div>
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
