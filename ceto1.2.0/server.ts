import express from 'express';
import cors from 'cors';
import axios from 'axios';
import dotenv from 'dotenv';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());

// Interfaces
interface SearchResult {
  title: string;
  link: string;
  snippet: string;
  source: string;
}

interface SearchResponse {
  success: boolean;
  query: string;
  results: SearchResult[];
  resultCount: number;
  searchTime: number;
}

// Search endpoint using Google Custom Search API
app.post('/api/search', async (req, res) => {
  try {
    const { query, limit = 10 } = req.body;

    if (!query || query.trim().length === 0) {
      return res.status(400).json({ 
        success: false, 
        error: 'Search query is required' 
      });
    }

    const startTime = Date.now();
    const results = await performWebSearch(query, limit);
    const searchTime = Date.now() - startTime;

    res.json({
      success: true,
      query,
      results,
      resultCount: results.length,
      searchTime
    } as SearchResponse);
  } catch (error) {
    console.error('Search error:', error);
    res.status(500).json({ 
      success: false, 
      error: 'Failed to perform search' 
    });
  }
});

// DuckDuckGo API fallback (no API key needed)
async function performWebSearch(query: string, limit: number): Promise<SearchResult[]> {
  try {
    // Using DuckDuckGo's public API as fallback (no key needed)
    const response = await axios.get('https://api.duckduckgo.com/', {
      params: {
        q: query,
        format: 'json',
        t: 'sentinel-b',
        no_redirect: 1,
        no_html: 1,
        skip_disambig: 1
      },
      timeout: 5000
    });

    const results: SearchResult[] = [];

    // Parse DuckDuckGo results
    if (response.data.Results && response.data.Results.length > 0) {
      response.data.Results.slice(0, limit).forEach((item: any) => {
        results.push({
          title: item.Text,
          link: item.FirstURL,
          snippet: item.Icon?.URL || '',
          source: 'DuckDuckGo'
        });
      });
    }

    // Add related searches
    if (response.data.RelatedTopics && results.length < limit) {
      response.data.RelatedTopics.slice(0, limit - results.length).forEach((item: any) => {
        if (item.FirstURL) {
          results.push({
            title: item.Text,
            link: item.FirstURL,
            snippet: item.Icon?.URL || '',
            source: 'DuckDuckGo Related'
          });
        }
      });
    }

    return results.slice(0, limit);
  } catch (error) {
    console.error('Web search error:', error);
    
    // Return mock results for demo if API fails
    return [
      {
        title: `Results for "${query}"`,
        link: `https://duckduckgo.com/?q=${encodeURIComponent(query)}`,
        snippet: 'Search unavailable - offline mode',
        source: 'Sentinel B (Offline)'
      }
    ];
  }
}

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    message: 'Sentinel B is running',
    timestamp: new Date().toISOString()
  });
});

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    name: 'Sentinel B',
    description: 'Local search engine with internet capabilities',
    version: '1.0.0',
    endpoints: {
      'POST /api/search': 'Search the web',
      'GET /api/health': 'Health check'
    }
  });
});

app.listen(PORT, () => {
  console.log(`
╔════════════════════════════════════════╗
║        🛰️  SENTINEL B ACTIVATED 🛰️       ║
║    Local Search Engine - Internet Mode │
╚════════════════════════════════════════╝

Server running at: http://localhost:${PORT}
API Documentation: http://localhost:${PORT}

Endpoints:
  POST   /api/search  - Search the web
  GET    /api/health  - Health check

Status: Ready for queries ✓
  `);
});

export default app;
