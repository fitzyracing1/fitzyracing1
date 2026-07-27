import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const dbPath = path.join(__dirname, '..', 'game.json')

interface GameDB {
  players: Record<string, Player>
  quests: Record<string, QuestProgress[]>
  raids: Record<string, RaidSession>
}

let db: GameDB = { players: {}, quests: {}, raids: {} }

// Load from disk
const loadDB = () => {
  if (fs.existsSync(dbPath)) {
    const content = fs.readFileSync(dbPath, 'utf-8')
    db = JSON.parse(content)
  }
}

// Save to disk
const saveDB = () => {
  fs.writeFileSync(dbPath, JSON.stringify(db, null, 2))
}

loadDB()

export interface Player {
  id: string
  username: string
  faction: 'Gunters' | 'Rebels' | 'Sixers'
  avatar_color?: string
  level: number
  experience: number
  score: number
  created_at: string
  updated_at: string
}

export interface QuestProgress {
  id: string
  player_id: string
  quest_id: string
  status: 'available' | 'in_progress' | 'completed'
  progress: number
  completed_at?: string
}

export interface RaidSession {
  id: string
  raid_id: string
  difficulty: string
  status: 'forming' | 'active' | 'completed'
  reward_xp: number
  created_at: string
  started_at?: string
  ended_at?: string
  roster?: RaidRoster[]
}

export interface RaidRoster {
  id: string
  raid_session_id: string
  player_id: string
  role: 'tank' | 'dps' | 'healer'
  contribution_score: number
}

// Helper functions
export const createPlayer = (id: string, username: string, faction: 'Gunters' | 'Rebels' | 'Sixers'): Player => {
  const player: Player = {
    id,
    username,
    faction,
    level: 1,
    experience: 0,
    score: 0,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  }
  db.players[id] = player
  saveDB()
  return player
}

export const getPlayer = (id: string): Player | undefined => {
  return db.players[id]
}

export const getPlayerByUsername = (username: string): Player | undefined => {
  return Object.values(db.players).find((p) => p.username === username)
}

export const updatePlayerScore = (playerId: string, xp: number): void => {
  const player = db.players[playerId]
  if (player) {
    player.experience += xp
    player.score += xp
    player.level = Math.floor(player.experience / 1000) + 1
    player.updated_at = new Date().toISOString()
    saveDB()
  }
}

export const getLeaderboard = (limit: number = 10, faction?: string): Array<Player & { rank: number }> => {
  let players = Object.values(db.players)
  if (faction) {
    players = players.filter((p) => p.faction === faction)
  }
  return players
    .sort((a, b) => b.score - a.score)
    .slice(0, limit)
    .map((p, i) => ({ ...p, rank: i + 1 }))
}

export const createRaidSession = (raidId: string, difficulty: string = 'normal'): RaidSession => {
  const id = `raid_${Date.now()}_${Math.random().toString(36).substring(7)}`
  const session: RaidSession = {
    id,
    raid_id: raidId,
    difficulty,
    status: 'forming',
    reward_xp: 500,
    created_at: new Date().toISOString(),
    roster: [],
  }
  db.raids[id] = session
  saveDB()
  return session
}

export const getRaidSession = (id: string): RaidSession | undefined => {
  return db.raids[id]
}

export const addPlayerToRaid = (raidSessionId: string, playerId: string, role: 'tank' | 'dps' | 'healer'): void => {
  const session = db.raids[raidSessionId]
  if (session && session.roster) {
    // Prevent duplicates
    if (!session.roster.find((r) => r.player_id === playerId)) {
      session.roster.push({
        id: `roster_${Date.now()}_${Math.random().toString(36).substring(7)}`,
        raid_session_id: raidSessionId,
        player_id: playerId,
        role,
        contribution_score: 0,
      })
      saveDB()
    }
  }
}

export const startRaidSession = (raidSessionId: string): void => {
  const session = db.raids[raidSessionId]
  if (session) {
    session.status = 'active'
    session.started_at = new Date().toISOString()
    saveDB()
  }
}

export const completeRaidSession = (
  raidSessionId: string,
  roster: Array<{ playerId: string; contribution: number }>,
): void => {
  const session = db.raids[raidSessionId]
  if (session) {
    session.status = 'completed'
    session.ended_at = new Date().toISOString()

    // Award XP to participants
    for (const r of roster) {
      const xpAwarded = Math.floor(r.contribution * 100)
      updatePlayerScore(r.playerId, xpAwarded)

      // Update raid roster contribution
      if (session.roster) {
        const rosterEntry = session.roster.find((e) => e.player_id === r.playerId)
        if (rosterEntry) {
          rosterEntry.contribution_score = r.contribution
        }
      }
    }
    saveDB()
  }
}

export const getAllPlayers = (): Player[] => {
  return Object.values(db.players)
}

export const getAllRaids = (): RaidSession[] => {
  return Object.values(db.raids)
}
