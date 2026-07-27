// Network speed monitoring with buffering
export class SpeedMonitor {
  constructor(bufferSize = 60) {
    this.bufferSize = bufferSize // seconds of history
    this.downloadBuffer = []
    this.uploadBuffer = []
    this.lastTestTime = null
    this.isMonitoring = false
  }

  async measureDownloadSpeed() {
    // Test download speed using a small image or API call
    const fileSize = 500000 // ~500KB test file
    const testUrl = 'https://via.placeholder.com/500x500.png'
    
    try {
      const startTime = performance.now()
      const response = await fetch(testUrl + '?cache=' + Date.now())
      await response.blob()
      const endTime = performance.now()
      
      const durationSeconds = (endTime - startTime) / 1000
      const speedMbps = (fileSize * 8) / (durationSeconds * 1000000)
      
      return speedMbps
    } catch (err) {
      console.error('Download test failed:', err)
      return 0
    }
  }

  async measureUploadSpeed() {
    // Simulate upload test - in production, use actual upload endpoint
    const testData = new Blob([new ArrayBuffer(100000)]) // 100KB
    
    try {
      const startTime = performance.now()
      // For demo, we'll simulate - replace with actual upload endpoint
      await new Promise(resolve => setTimeout(resolve, Math.random() * 500 + 200))
      const endTime = performance.now()
      
      const durationSeconds = (endTime - startTime) / 1000
      const speedMbps = (testData.size * 8) / (durationSeconds * 1000000)
      
      return Math.max(0.5, speedMbps * 0.8) // Simulated with variance
    } catch (err) {
      console.error('Upload test failed:', err)
      return 0
    }
  }

  addToBuffer(downloadSpeed, uploadSpeed) {
    const timestamp = new Date()
    
    this.downloadBuffer.push({ timestamp, speed: downloadSpeed })
    this.uploadBuffer.push({ timestamp, speed: uploadSpeed })
    
    // Keep only last N entries
    if (this.downloadBuffer.length > this.bufferSize) {
      this.downloadBuffer.shift()
    }
    if (this.uploadBuffer.length > this.bufferSize) {
      this.uploadBuffer.shift()
    }
  }

  getBufferStats() {
    const calcStats = (buffer) => {
      if (buffer.length === 0) return { avg: 0, min: 0, max: 0, current: 0 }
      
      const speeds = buffer.map(b => b.speed)
      const avg = speeds.reduce((a, b) => a + b, 0) / speeds.length
      const min = Math.min(...speeds)
      const max = Math.max(...speeds)
      const current = speeds[speeds.length - 1]
      
      return { avg, min, max, current }
    }
    
    return {
      download: calcStats(this.downloadBuffer),
      upload: calcStats(this.uploadBuffer),
      bufferSize: this.downloadBuffer.length,
      maxBuffer: this.bufferSize
    }
  }

  getBufferData() {
    return {
      download: [...this.downloadBuffer],
      upload: [...this.uploadBuffer]
    }
  }

  async runTest() {
    const download = await this.measureDownloadSpeed()
    const upload = await this.measureUploadSpeed()
    this.addToBuffer(download, upload)
    this.lastTestTime = new Date()
    return { download, upload }
  }

  clearBuffer() {
    this.downloadBuffer = []
    this.uploadBuffer = []
  }
}
