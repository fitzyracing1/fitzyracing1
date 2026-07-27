import './style.css'
import { World3D } from './3dWorld'
import { SentinelB } from './sentinelB'

// Create main layout
const app = document.querySelector<HTMLDivElement>('#app')!
app.innerHTML = `
  <div class="main-layout">
    <div class="left-panel">
      <div id="canvas-container"></div>
      <div id="info-panel">
        <h1>Methane Emissions 3D Visualization</h1>
        <div class="stats">
          <div class="stat-item">
            <label>Average Reading:</label>
            <span id="avg-reading">0.00 PPM</span>
          </div>
          <div class="stat-item">
            <label>Max Reading:</label>
            <span id="max-reading">0.00 PPM</span>
          </div>
          <div class="stat-item">
            <label>Min Reading:</label>
            <span id="min-reading">0.00 PPM</span>
          </div>
          <div class="stat-item">
            <label>Last Updated:</label>
            <span id="last-updated">--:--:--</span>
          </div>
        </div>
        <button id="refresh-btn">Refresh Data</button>
      </div>
    </div>
    <div class="right-panel" id="sentinel-container"></div>
  </div>
`

// Initialize 3D world
const container = document.querySelector<HTMLDivElement>('#canvas-container')!
const world = new World3D(container)

// Initialize Sentinel B
const sentinelContainer = document.querySelector<HTMLDivElement>('#sentinel-container')!
new SentinelB(sentinelContainer)

// Initial data update
world.updateMethaneData()

// Update UI stats
function updateStats() {
  const stats = world.getStats()
  document.querySelector('#avg-reading')!.textContent = stats.avgReading.toFixed(2) + ' PPM'
  document.querySelector('#max-reading')!.textContent = stats.maxReading.toFixed(2) + ' PPM'
  document.querySelector('#min-reading')!.textContent = stats.minReading.toFixed(2) + ' PPM'
  document.querySelector('#last-updated')!.textContent = stats.lastUpdated
}

updateStats()

// Refresh data button
document.querySelector('#refresh-btn')!.addEventListener('click', () => {
  world.updateMethaneData()
  updateStats()
})

// Update data every 3 seconds
setInterval(() => {
  world.updateMethaneData()
  updateStats()
}, 3000)
