import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [primeGameData, setPrimeGameData] = useState(null)
  const [inventoryData, setInventoryData] = useState(null)
  const [dataSets, setDataSets] = useState([])
  const [activeTab, setActiveTab] = useState('prime')
  const [isSimulating, setIsSimulating] = useState(false)

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
    } catch (error) {
      console.error('Error loading data:', error)
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
      </main>

      <footer className="footer">
        <p>Aspect Control Unit • Powered by C# & Unreal Engine Integration</p>
      </footer>
    </div>
  )
}

export default App
