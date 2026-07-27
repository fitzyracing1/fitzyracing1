# CETO 1.2.0 - Methane Emissions 3D Visualization + Sentinel B Search

An integrated platform combining:
1. **Interactive 3D methane emissions visualization** using Three.js
2. **Sentinel B** - A local search engine with internet search capabilities

## Features

### 3D World Visualization
- **3D Scene**: Dynamic 3D visualization with methane emission data points
- **Real-time Data Updates**: Simulated methane readings update every 3 seconds
- **Interactive Statistics Panel**: Live metrics showing average, max, and min readings
- **Color-Coded Particles**: Red indicates high methane levels, green indicates low levels
- **Orbital Camera**: Automatically rotating camera for better data visibility

### Sentinel B Search Engine
- **Local Operation**: Runs entirely on your machine
- **Internet Search**: Integrated web search using DuckDuckGo API
- **Search History**: Keeps track of recent searches
- **Real-time Results**: Fast, responsive search with performance metrics
- **Secure & Private**: No tracking, all processing local

## Project Structure

```
├── src/
│   ├── main.ts              # Application entry point
│   ├── 3dWorld.ts           # 3D scene and visualization logic
│   ├── methaneData.ts       # Data generation and simulation
│   ├── sentinelB.ts         # Sentinel B search interface
│   └── style.css            # Styling for the UI
├── server.ts                # Backend server for search
├── package.json             # Dependencies and scripts
└── README.md                # This file
```

## Getting Started

### Installation

```bash
npm install
```

### Development

Run both the frontend dev server and backend API server:

**Terminal 1 - Frontend (Vite dev server):**
```bash
npm run dev
```
The app will be available at `http://localhost:5173`

**Terminal 2 - Backend (Sentinel B API):**
```bash
npm run server
```
The API will be available at `http://localhost:3001`

Or run both together:
```bash
npm run dev:all
```

### Build for Production

```bash
npm run build
```

The optimized build will be output to the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## How It Works

### 3D World (`src/3dWorld.ts`)
- Initializes a Three.js scene with WebGL rendering
- Creates particles around methane reading points
- Colors particles based on methane concentration levels
- Orbits the camera around the scene for continuous visualization
- Updates the statistics panel with current readings

### Methane Data Generator (`src/methaneData.ts`)
- Simulates realistic methane readings using mathematical functions
- Generates 10 circular readings and 5 random isolated readings
- Uses time-based sine waves to create natural variations
- Returns readings with XYZ coordinates and PPM (parts per million) values

### Sentinel B (`src/sentinelB.ts` + `server.ts`)
- **Frontend Component**: Handles search UI, input, and result display
- **Backend API**: Express.js server providing web search endpoints
- **Search Integration**: Uses DuckDuckGo API for internet searches
- **Privacy-First**: No tracking, no API keys required for DuckDuckGo

### API Endpoints

#### Search
```
POST /api/search
Content-Type: application/json

Request:
{
  "query": "climate change methane",
  "limit": 10
}

Response:
{
  "success": true,
  "query": "climate change methane",
  "results": [
    {
      "title": "Result title",
      "link": "https://example.com",
      "snippet": "Result snippet",
      "source": "DuckDuckGo"
    }
  ],
  "resultCount": 10,
  "searchTime": 245
}
```

#### Health Check
```
GET /api/health

Response:
{
  "status": "ok",
  "message": "Sentinel B is running",
  "timestamp": "2024-01-02T12:00:00Z"
}
```

## Technologies Used

- **Three.js**: 3D graphics rendering
- **TypeScript**: Type-safe JavaScript
- **Vite**: Modern build tool and dev server
- **Express.js**: Backend API server
- **Axios**: HTTP client for web requests
- **CSS**: Styling with glassmorphism effects
- **DuckDuckGo API**: Web search integration

## Browser Compatibility

Requires a modern browser with WebGL support:
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## Configuration

### Methane Update Interval
Change the data refresh rate in `src/main.ts` (currently 3 seconds):
```typescript
setInterval(() => {
  world.updateMethaneData()
  updateStats()
}, 3000) // 3000ms = 3 seconds
```

### Camera Settings
Modify camera behavior in `src/3dWorld.ts`:
```typescript
// Adjust orbit speed
const time = Date.now() * 0.0001; // Change multiplier for rotation speed
```

### Server Port
Change the API server port in `server.ts`:
```typescript
const PORT = process.env.PORT || 3001;
```

Or use environment variable:
```bash
PORT=8080 npm run server
```

## Running in Production

### Build the application:
```bash
npm run build
```

### Serve the frontend:
```bash
# Using a static server (e.g., Python)
python -m http.server 8000 --directory dist

# Or using Node.js
npx serve dist
```

### Run the backend:
```bash
npm run server
```

Or use PM2 for process management:
```bash
npm install -g pm2
pm2 start server.ts
pm2 start "vite preview" --name "frontend"
```

## Environment Variables

Create a `.env` file for configuration:
```env
PORT=3001
NODE_ENV=production
```

## API Integration Examples

### Search from the command line:
```bash
curl -X POST http://localhost:3001/api/search \
  -H "Content-Type: application/json" \
  -d '{"query": "renewable energy", "limit": 5}'
```

### Check server health:
```bash
curl http://localhost:3001/api/health
```

## Troubleshooting

### "Failed to connect to Sentinel B server"
- Ensure the backend server is running: `npm run server`
- Check that port 3001 is not in use
- Verify CORS is properly configured in `server.ts`

### 3D visualization not loading
- Check browser console for WebGL errors
- Ensure you're using a compatible browser
- Try disabling browser extensions that might block WebGL

### Search results are empty
- Check your internet connection
- Verify DuckDuckGo API is accessible
- Check server logs for error messages

## Future Enhancements

- [ ] Real methane data integration from APIs
- [ ] Multiple search providers (Google, Bing, etc.)
- [ ] Search filters and advanced operators
- [ ] Data visualization for search results
- [ ] Heat map visualization for methane data
- [ ] Historical data playback
- [ ] Export capabilities
- [ ] Multi-region monitoring
- [ ] Real-time alerts

## License

MIT
