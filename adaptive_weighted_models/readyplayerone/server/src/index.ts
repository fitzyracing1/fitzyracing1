import 'dotenv/config'
import http from 'node:http'
import { WebSocketServer } from 'ws'
import cors from 'cors'
import express from 'express'
import axios from 'axios'
import { v4 as uuidv4 } from 'uuid'
import * as db from './db.js'

const port = Number(process.env.PORT || 4000)
const weightedModelsApi = process.env.WEIGHTED_MODELS_API || 'http://localhost:8000'

const app = express()
app.use(cors())
app.use(express.json())

// Game constants
const QUESTS = [
  { id: 'copper-key', name: 'Copper Key', desc: 'Race and route simulation', tier: 'beginner', xpReward: 100, goldReward: 50 },
  { id: 'jade-key', name: 'Jade Key', desc: 'Joust puzzle pathfinding', tier: 'intermediate', xpReward: 250, goldReward: 150 },
  { id: 'crystal-key', name: 'Crystal Key', desc: 'Lore deep dive and puzzle chains', tier: 'expert', xpReward: 500, goldReward: 300 },
]

const RAIDS = [
  { id: 'anorak', name: 'Castle Anorak', difficulty: 'hard', minLevel: 10 },
  { id: 'OASIS-Core', name: 'OASIS Core', difficulty: 'epic', minLevel: 25 },
]

// Weighted-Models API integration
const callAIService = async (endpoint: string, payload: any) => {
  try {
    const response = await axios.post(`${weightedModelsApi}${endpoint}`, payload, {
      timeout: 5000,
    })
    return response.data
  } catch (error) {
    console.warn(`AI service call failed: ${endpoint}`, error)
    return null
  }
}

// Build overview with dynamic data
const buildOverview = () => {
  const allPlayers = db.getAllPlayers()
  const factionScores = allPlayers.reduce(
    (acc, p) => {
      acc[p.faction] = (acc[p.faction] || 0) + p.score
      return acc
    },
    {} as Record<string, number>,
  )

  return {
    season: 'Season Zero / Halliday Preview',
    aiServiceStatus: `Scoring via ${weightedModelsApi}`,
    lobbyPopulation: `${allPlayers.length} avatars online`,
    activeRaid: 'Castle Anorak',
    factions: [
      {
        name: 'Gunters',
        style: 'faction-card gold',
        summary: 'Puzzle-first operatives optimized for Halliday clue chains and stable clear rates.',
        totalScore: factionScores['Gunters'] || 0,
        memberCount: allPlayers.filter((p) => p.faction === 'Gunters').length,
      },
      {
        name: 'Rebels',
        style: 'faction-card cyan',
        summary: 'Flexible defenders built for escort quests, terrain control, and raid recovery.',
        totalScore: factionScores['Rebels'] || 0,
        memberCount: allPlayers.filter((p) => p.faction === 'Rebels').length,
      },
      {
        name: 'Sixers',
        style: 'faction-card crimson',
        summary: 'High-pressure corporate squads with strong tempo but elevated IOI risk signatures.',
        totalScore: factionScores['Sixers'] || 0,
        memberCount: allPlayers.filter((p) => p.faction === 'Sixers').length,
      },
    ],
    quests: QUESTS.map((q) => ({ ...q })),
    raidSignals: [
      { label: 'Team Sync', value: '86%' },
      { label: 'Faction Drift', value: 'Rising Sixer tempo' },
      { label: 'AI Match Score', value: '0.78' },
    ],
    leaderboardDrift: 'Meta shift detected: Sixer tempo comps +14% over last patch.',
    rebalanceHint: 'Recommended rebalance: +support weight, -IOI aggression bonus.',
  }
}

// HTTP Endpoints
app.get('/api/health', (_req, res) => {
  res.json({ status: 'ok', weightedModelsApi })
})

app.get('/api/overview', (_req, res) => {
  res.json(buildOverview())
})

app.get('/api/leaderboard', (req, res) => {
  const faction = req.query.faction as string | undefined
  const limit = Number(req.query.limit || 10)
  const entries = db.getLeaderboard(limit, faction)

  res.json({
    season: buildOverview().season,
    entries: entries.sort((a, b) => a.rank - b.rank),
  })
})

// Player endpoints
app.post('/api/player/create', (req, res) => {
  const { username, faction } = req.body

  if (!username || !faction || !['Gunters', 'Rebels', 'Sixers'].includes(faction)) {
    return res.status(400).json({ error: 'Invalid username or faction' })
  }

  const existing = db.getPlayerByUsername(username)
  if (existing) {
    return res.status(409).json({ error: 'Username already taken' })
  }

  const playerId = uuidv4()
  const player = db.createPlayer(playerId, username, faction)

  // Initialize quests
  for (const quest of QUESTS) {
    // Could use a quests table or embed in player, but for MVP just return in player profile
  }

  res.json({ player, message: 'Player created successfully' })
})

app.get('/api/player/:id', (req, res) => {
  const player = db.getPlayer(req.params.id)
  if (!player) {
    return res.status(404).json({ error: 'Player not found' })
  }

  res.json({
    player,
    quests: QUESTS.map((q) => ({
      ...q,
      status: 'available',
      progress: 0,
    })),
    raids: db.getAllRaids().filter((r) => r.roster?.some((m) => m.player_id === req.params.id)),
  })
})

// Quest endpoints
app.post('/api/quest/complete', (req, res) => {
  const { playerId, questId } = req.body

  const player = db.getPlayer(playerId)
  if (!player) {
    return res.status(404).json({ error: 'Player not found' })
  }

  const quest = QUESTS.find((q) => q.id === questId)
  if (!quest) {
    return res.status(400).json({ error: 'Quest not found' })
  }

  // Award XP and gold
  db.updatePlayerScore(playerId, quest.xpReward || 0)

  // Broadcast event
  for (const client of wss.clients) {
    if (client.readyState === 1) {
      client.send(
        JSON.stringify({
          type: 'quest-completed',
          playerId,
          questId,
          rewards: { xp: quest.xpReward, gold: quest.goldReward },
          timestamp: Date.now(),
        }),
      )
    }
  }

  res.json({ message: 'Quest completed', rewards: { xp: quest.xpReward, gold: quest.goldReward } })
})

// Raid endpoints
app.post('/api/raid/create', (req, res) => {
  const { raidId, difficulty } = req.body

  const raid = RAIDS.find((r) => r.id === raidId)
  if (!raid) {
    return res.status(400).json({ error: 'Invalid raid ID' })
  }

  const session = db.createRaidSession(raidId, difficulty || 'normal')
  res.json(session)
})

app.post('/api/raid/join', (req, res) => {
  const { raidSessionId, playerId, role } = req.body

  const player = db.getPlayer(playerId)
  if (!player) {
    return res.status(404).json({ error: 'Player not found' })
  }

  const session = db.getRaidSession(raidSessionId)
  if (!session) {
    return res.status(404).json({ error: 'Raid session not found' })
  }

  db.addPlayerToRaid(raidSessionId, playerId, role)

  // Broadcast to WebSocket clients
  for (const client of wss.clients) {
    if (client.readyState === 1) {
      client.send(
        JSON.stringify({
          type: 'raid-update',
          raidSessionId,
          action: 'player-joined',
          playerId,
          rosterSize: session.roster?.length || 0,
        }),
      )
    }
  }

  res.json({ message: 'Joined raid', session: db.getRaidSession(raidSessionId) })
})

app.post('/api/raid/complete', (req, res) => {
  const { raidSessionId, roster } = req.body

  db.completeRaidSession(raidSessionId, roster)

  // Broadcast event
  for (const client of wss.clients) {
    if (client.readyState === 1) {
      client.send(
        JSON.stringify({
          type: 'raid-completed',
          raidSessionId,
          timestamp: Date.now(),
        }),
      )
    }
  }

  res.json({ message: 'Raid completed and rewards distributed' })
})

// WebSocket
const server = http.createServer(app)
const wss = new WebSocketServer({ server, path: '/ws' })

wss.on('connection', (socket) => {
  socket.send(JSON.stringify({ type: 'welcome', season: buildOverview().season }))
})

// Broadcast heartbeat and game state
setInterval(() => {
  const overview = buildOverview()
  const payload = JSON.stringify({
    type: 'heartbeat',
    activeRaid: overview.activeRaid,
    leaderboardDrift: overview.leaderboardDrift,
    playerCount: overview.lobbyPopulation,
    timestamp: Date.now(),
  })

  for (const client of wss.clients) {
    if (client.readyState === 1) {
      client.send(payload)
    }
  }
}, 5000)

server.listen(port, () => {
  console.log(`Ready Player One server listening on http://localhost:${port}`)
})
