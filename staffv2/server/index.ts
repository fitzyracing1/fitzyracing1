import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import OpenAI from 'openai';
import { loadAIConfig } from './aiConfigLoader.js';

dotenv.config();

// Initialize OpenAI client
const openai = process.env.OPENAI_API_KEY 
  ? new OpenAI({ apiKey: process.env.OPENAI_API_KEY })
  : null;

const app = express();
app.use(cors());
app.use(express.json());

app.get('/api/config', (_req, res) => {
  const cfg = loadAIConfig();
  res.json(cfg);
});

app.post('/api/ask', async (req, res) => {
  const { prompt } = req.body || {};
  const cfg = loadAIConfig();
  
  // Use real OpenAI if API key is configured
  if (openai && cfg.enableGpt5) {
    try {
      const completion = await openai.chat.completions.create({
        model: 'gpt-4o', // Using GPT-4o as GPT-5 isn't released yet
        messages: [
          { 
            role: 'system', 
            content: 'You are a Staff Bot managing nanobot build simulations. Respond in a technical, futuristic manner about nanobot assembly, quantum coherence, and AI systems. Keep responses concise (2-3 sentences).'
          },
          { role: 'user', content: prompt }
        ],
        max_tokens: 150,
        temperature: 0.8,
      });
      
      const reply = completion.choices[0]?.message?.content || 'No response generated.';
      return res.json({ 
        model: 'gpt-4o (simulating gpt-5)', 
        reply 
      });
    } catch (error) {
      console.error('[OpenAI Error]', error);
      // Fall through to stub responses on error
    }
  }
  
  // Fallback: Generate AI-like stub responses
  const responses = [
    `Analyzing nanobot assembly patterns for: "${prompt}". The GPT-5 neural matrix suggests optimizing quantum coherence by 23.7% through adaptive self-replication protocols.`,
    `Processing request through ${cfg.gptVersion} architecture... Result: Nanobot swarm configuration updated. Efficiency increased. Recommended action: Deploy to sector 7-G.`,
    `Your query "${prompt}" has been processed by 47 active nanobots. Conclusion: Molecular assembly complete. Self-healing protocols engaged.`,
    `GPT-5 Staff Bot Analysis: The optimal solution involves restructuring the nanobot lattice framework. Estimated completion: 3.2 microseconds. All systems nominal.`,
    `Nanobot intelligence report for "${prompt}": Detected anomalous patterns. Initiating adaptive learning sequence. Current swarm intelligence: EVOLVING.`,
  ];
  
  const randomResponse = responses[Math.floor(Math.random() * responses.length)];
  
  res.json({ 
    model: `${cfg.gptVersion} (stub mode)`, 
    reply: randomResponse
  });
});

const PORT = process.env.PORT ? Number(process.env.PORT) : 3001;
const server = app.listen(PORT, () => {
  const cfg = loadAIConfig();
  console.log(`[server] listening on ${PORT} | model=${cfg.gptVersion} enableGpt5=${cfg.enableGpt5}`);
});

// Keep server alive
setInterval(() => {
  console.log('[server] heartbeat');
}, 10000);

server.on('error', (err) => {
  console.error('[server] error:', err);
  process.exit(1);
});
