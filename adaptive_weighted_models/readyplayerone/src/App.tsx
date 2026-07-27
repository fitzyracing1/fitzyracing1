import { useEffect, useState } from 'react'
import './App.css'
import { PlayerCreation } from './PlayerCreation'
import { PlayerProfile } from './PlayerProfile'
import { RaidMatcher } from './RaidMatcher'
import { QuestDetail } from './QuestDetail'
import { RaidBattle } from './RaidBattle'
import { Leaderboard } from './Leaderboard'
import { CosmeticsShop } from './CosmeticsShop'
import { SeasonalDriftDisplay } from './SeasonalDrift'

type Card = { name: string; style: string; summary: string; totalScore?: number; memberCount?: number }
type Signal = { label: string; value: string }
type Quest = { id: string; name: string; desc: string; tier: string; xpReward?: number; goldReward?: number }
type Overview = {
  season: string
  aiServiceStatus: string
  lobbyPopulation: string
  activeRaid: string
  factions: Card[]
  quests: Quest[]
  raidSignals: Signal[]
  leaderboardDrift: string
  rebalanceHint: string
}

type Player = {
  id: string
  username: string
  faction: 'Gunters' | 'Rebels' | 'Sixers'
  level: number
  experience: number
  score: number
  created_at: string
  updated_at: string
}

const fallbackOverview: Overview = {
  season: 'Season Zero',
  aiServiceStatus: 'Booting',
  lobbyPopulation: '0 avatars',
  activeRaid: 'Pending',
  factions: [
    {
      name: 'Gunters',
      style: 'faction-card gold',
      summary: 'Puzzle-first operatives optimized for Halliday clue chains and stable clear rates.',
    },
    {
      name: 'Rebels',
      style: 'faction-card cyan',
      summary: 'Flexible defenders built for escort quests, terrain control, and raid recovery.',
    },
    {
      name: 'Sixers',
      style: 'faction-card crimson',
      summary: 'High-pressure corporate squads with strong tempo but elevated IOI risk signatures.',
    },
  ],
  quests: [
    { id: 'copper-key', name: 'Copper Key', desc: 'Race and route simulation', tier: 'beginner', xpReward: 100, goldReward: 50 },
    { id: 'jade-key', name: 'Jade Key', desc: 'Joust puzzle pathfinding', tier: 'intermediate', xpReward: 250, goldReward: 150 },
    { id: 'crystal-key', name: 'Crystal Key', desc: 'Lore deep dive', tier: 'expert', xpReward: 500, goldReward: 300 },
  ],
  raidSignals: [
    { label: 'Team Sync', value: '86%' },
    { label: 'Faction Drift', value: 'Rising Sixer tempo' },
    { label: 'AI Match Score', value: '0.78' },
  ],
  leaderboardDrift: 'Meta shift pending',
  rebalanceHint: 'Waiting for AI service signal.',
}

function App() {
  const [overview, setOverview] = useState<Overview>(fallbackOverview)
  const [socketState, setSocketState] = useState('Disconnected')
  const [currentPlayer, setCurrentPlayer] = useState<Player | null>(null)
  const [showCreation, setShowCreation] = useState(false)
  const [showRaidMatcher, setShowRaidMatcher] = useState(false)
  const [selectedQuest, setSelectedQuest] = useState<string | null>(null)
  const [showLeaderboard, setShowLeaderboard] = useState(false)
  const [inBattle, setInBattle] = useState(false)
  const [currentRaidRole, setCurrentRaidRole] = useState<string | null>(null)
  const [showCosmeticsShop, setShowCosmeticsShop] = useState(false)

  // Load player from localStorage on mount
  useEffect(() => {
    const storedPlayerId = localStorage.getItem('playerid')
    if (storedPlayerId) {
      const loadPlayer = async () => {
        try {
          const response = await fetch(`/api/player/${storedPlayerId}`)
          if (response.ok) {
            const data = await response.json()
            setCurrentPlayer(data.player)
          } else {
            localStorage.removeItem('playerid')
            setShowCreation(true)
          }
        } catch {
          localStorage.removeItem('playerid')
          setShowCreation(true)
        }
      }
      loadPlayer()
    } else {
      setShowCreation(true)
    }
  }, [])

  // Load overview
  useEffect(() => {
    const loadOverview = async () => {
      try {
        const response = await fetch('/api/overview')
        if (response.ok) {
          const payload = (await response.json()) as Overview
          setOverview(payload)
        }
      } catch (err) {
        console.error('Failed to load overview:', err)
      }
    }

    loadOverview()
    const interval = setInterval(loadOverview, 10000)
    return () => clearInterval(interval)
  }, [])

  // WebSocket
  useEffect(() => {
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
    const socket = new WebSocket(`${protocol}://${window.location.host}/ws`)

    socket.addEventListener('open', () => setSocketState('Live'))
    socket.addEventListener('close', () => setSocketState('Disconnected'))
    socket.addEventListener('error', () => setSocketState('Unavailable'))
    socket.addEventListener('message', (event) => {
      const data = JSON.parse(event.data)
      if (data.type === 'heartbeat') {
        // Update with live data
      }
    })

    return () => socket.close()
  }, [])

  const handleCreatePlayer = async (username: string, faction: string) => {
    try {
      const response = await fetch('/api/player/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, faction }),
      })

      if (!response.ok) {
        throw new Error('Failed to create player')
      }

      const data = await response.json()
      const player = data.player as Player
      localStorage.setItem('playerid', player.id)
      setCurrentPlayer(player)
      setShowCreation(false)
    } catch (err) {
      throw new Error(err instanceof Error ? err.message : 'Failed to create player')
    }
  }

  const handleJoinRaid = async (role: string) => {
    if (!currentPlayer) return

    try {
      // Create a new raid session
      const createResponse = await fetch('/api/raid/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ raidId: 'anorak', difficulty: 'normal' }),
      })

      if (!createResponse.ok) {
        throw new Error('Failed to create raid')
      }

      const raidData = await createResponse.json()

      // Join the raid
      const joinResponse = await fetch('/api/raid/join', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          raidSessionId: raidData.id,
          playerId: currentPlayer.id,
          role,
        }),
      })

      if (!joinResponse.ok) {
        throw new Error('Failed to join raid')
      }

      // Enter battle
      setCurrentRaidRole(role)
      setInBattle(true)
      setShowRaidMatcher(false)
    } catch (err) {
      console.error('Raid join failed:', err)
    }
  }

  const handleBattleVictory = (loot: { xp: number; gold: number }) => {
    if (currentPlayer) {
      setCurrentPlayer((prev) => (prev ? { ...prev, score: prev.score + loot.xp, experience: prev.experience + loot.xp } : null))
    }
    setInBattle(false)
    setCurrentRaidRole(null)
  }

  // Show player creation modal if needed
  if (showCreation) {
    return <PlayerCreation onCreate={handleCreatePlayer} />
  }

  // Show cosmetics shop
  if (showCosmeticsShop && currentPlayer) {
    return (
      <>
        <LobbyView
          overview={overview}
          socketState={socketState}
          currentPlayer={currentPlayer}
          onQuestClick={setSelectedQuest}
          onLeaderboardClick={() => setShowLeaderboard(true)}
          onRaidClick={() => setShowRaidMatcher(true)}
          onCosmeticsClick={() => setShowCosmeticsShop(true)}
        />
        <CosmeticsShop
          playerGold={currentPlayer.score}
          onBuy={(cosmeticId) => {
            console.log('Bought cosmetic:', cosmeticId)
            setShowCosmeticsShop(false)
          }}
          onClose={() => setShowCosmeticsShop(false)}
        />
      </>
    )
  }

  // Show leaderboard
  if (showLeaderboard && currentPlayer) {
    return <Leaderboard onBack={() => setShowLeaderboard(false)} />
  }

  // Show quest detail
  if (selectedQuest && currentPlayer) {
    const quest = overview.quests.find((q) => q.id === selectedQuest)
    if (quest) {
      return (
        <>
          <LobbyView
            overview={overview}
            socketState={socketState}
            currentPlayer={currentPlayer}
            onQuestClick={setSelectedQuest}
            onLeaderboardClick={() => setShowLeaderboard(true)}
            onRaidClick={() => setShowRaidMatcher(true)}
          />
          <QuestDetail
            quest={{ ...quest, progress: 45 }}
            playerLevel={currentPlayer.level}
            onStart={() => {
              // Quest started
            }}
            onComplete={() => {
              setSelectedQuest(null)
              setCurrentPlayer((prev) => (prev ? { ...prev, experience: prev.experience + (quest.xpReward || 0), score: prev.score + (quest.xpReward || 0) } : null))
            }}
            onBack={() => setSelectedQuest(null)}
          />
        </>
      )
    }
  }

  // Show raid battle
  if (inBattle && currentPlayer && currentRaidRole) {
    return (
      <RaidBattle
        raidSessionId=""
        playerName={currentPlayer.username}
        playerRole={currentRaidRole}
        onVictory={handleBattleVictory}
        onDefeat={() => {
          setInBattle(false)
          setCurrentRaidRole(null)
        }}
        onLeave={() => {
          setInBattle(false)
          setCurrentRaidRole(null)
        }}
      />
    )
  }

  // Raid matcher modal
  if (showRaidMatcher && currentPlayer) {
    return (
      <>
        <LobbyView
          overview={overview}
          socketState={socketState}
          currentPlayer={currentPlayer}
          onQuestClick={setSelectedQuest}
          onLeaderboardClick={() => setShowLeaderboard(true)}
          onRaidClick={() => setShowRaidMatcher(true)}
          onCosmeticsClick={() => setShowCosmeticsShop(true)}
        />
        <RaidMatcher
          raidId="anorak"
          raidName="Castle Anorak"
          onJoinRaid={handleJoinRaid}
          onClose={() => setShowRaidMatcher(false)}
        />
      </>
    )
  }

  // Default: Lobby view
  return (
    <LobbyView
      overview={overview}
      socketState={socketState}
      currentPlayer={currentPlayer}
      onQuestClick={setSelectedQuest}
      onLeaderboardClick={() => setShowLeaderboard(true)}
      onRaidClick={() => setShowRaidMatcher(true)}
      onCosmeticsClick={() => setShowCosmeticsShop(true)}
    />
  )
}

interface LobbyViewProps {
  overview: Overview
  socketState: string
  currentPlayer: Player | null
  onQuestClick?: (questId: string) => void
  onLeaderboardClick?: () => void
  onRaidClick?: () => void
  onCosmeticsClick?: () => void
}

function LobbyView({ overview, socketState, currentPlayer, onQuestClick, onLeaderboardClick, onRaidClick, onCosmeticsClick }: LobbyViewProps) {
  return (
    <main className="shell">
      <section className="hero-panel">
        <div>
          <p className="eyebrow">{overview.season}</p>
          <h1>Ready Player One MVP</h1>
          <p className="lede">
            Browser-first lobby, faction board, quest orchestration, raid balancing, and leaderboard
            intelligence backed by the weighted-models service.
          </p>
          {currentPlayer && (
            <p style={{ color: '#00ffff' }}>
              Logged in as {currentPlayer.username} (Level {currentPlayer.level}) | 💰 {currentPlayer.score.toLocaleString()}
            </p>
          )}
        </div>
        <div className="status-grid">
          <article>
            <span>AI Service</span>
            <strong>{overview.aiServiceStatus}</strong>
          </article>
          <article>
            <span>Lobby Population</span>
            <strong>{overview.lobbyPopulation}</strong>
          </article>
          <article>
            <span>Active Raid</span>
            <strong>{overview.activeRaid}</strong>
          </article>
          <article>
            <span>WebSocket</span>
            <strong>{socketState}</strong>
          </article>
        </div>
        {onCosmeticsClick && (
          <button
            onClick={onCosmeticsClick}
            style={{
              position: 'absolute',
              top: '2rem',
              right: '2rem',
              padding: '0.5rem 1rem',
              background: 'rgba(255, 215, 0, 0.2)',
              border: '1px solid #ffd700',
              color: '#ffd700',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '0.9rem',
              fontWeight: '600',
            }}
            title="Cosmetics Shop"
          >
            🎨 Shop
          </button>
        )}
      </section>

      <section className="panel-grid">
        <section className="panel">
          <header>
            <p className="eyebrow">Lobby</p>
            <h2>Faction Lineup</h2>
          </header>
          <div className="faction-grid">
            {overview.factions.map((card) => (
              <article key={card.name} className={card.style}>
                <h3>{card.name}</h3>
                <p>{card.summary}</p>
                {card.memberCount !== undefined && (
                  <p style={{ fontSize: '0.85rem', color: '#aaa', marginTop: '0.5rem' }}>
                    {card.memberCount} members
                  </p>
                )}
              </article>
            ))}
          </div>
        </section>

        <section className="panel">
          <header>
            <p className="eyebrow">Quest Flow</p>
            <h2>Progression Tracks</h2>
          </header>
          <ul className="quest-list">
            {overview.quests.map((track) => (
              <li
                key={track.id}
                onClick={() => onQuestClick?.(track.id)}
                style={{
                  cursor: 'pointer',
                  padding: '0.5rem',
                  borderRadius: '4px',
                  transition: 'all 0.2s',
                }}
                onMouseEnter={(e) => {
                  const el = e.currentTarget
                  el.style.background = 'rgba(0, 255, 255, 0.1)'
                }}
                onMouseLeave={(e) => {
                  const el = e.currentTarget
                  el.style.background = 'transparent'
                }}
              >
                <strong>{track.name}</strong> - {track.desc} <em>({track.tier})</em>
              </li>
            ))}
          </ul>
          {onRaidClick && (
            <button
              onClick={onRaidClick}
              style={{
                width: '100%',
                padding: '0.75rem',
                marginTop: '1rem',
                background: 'rgba(255, 215, 0, 0.2)',
                border: '1px solid #ffd700',
                color: '#ffd700',
                borderRadius: '4px',
                cursor: 'pointer',
                fontWeight: '600',
                transition: 'all 0.2s',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'rgba(255, 215, 0, 0.3)'
                e.currentTarget.style.boxShadow = '0 0 10px rgba(255, 215, 0, 0.4)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'rgba(255, 215, 0, 0.2)'
                e.currentTarget.style.boxShadow = 'none'
              }}
            >
              Join Raid
            </button>
          )}
        </section>

        <section className="panel wide">
          <header>
            <p className="eyebrow">Raid Ops</p>
            <h2>Balancing Signals</h2>
          </header>
          <div className="signal-row">
            {overview.raidSignals.map((signal) => (
              <article key={signal.label} className="signal-card">
                <span>{signal.label}</span>
                <strong>{signal.value}</strong>
              </article>
            ))}
          </div>
        </section>

        <section className="panel">
          <header>
            <p className="eyebrow">Leaderboard</p>
            <h2>Seasonal Drift Monitor</h2>
          </header>
          <p className="mono-line">{overview.leaderboardDrift}</p>
          <p className="mono-line">{overview.rebalanceHint}</p>
          <SeasonalDriftDisplay
            factions={overview.factions.map((f) => ({
              faction: f.name,
              totalScore: f.totalScore || 0,
              memberCount: f.memberCount || 0,
            }))}
          />
          {onLeaderboardClick && (
            <button
              onClick={onLeaderboardClick}
              style={{
                width: '100%',
                padding: '0.75rem',
                marginTop: '1rem',
                background: 'rgba(0, 255, 255, 0.2)',
                border: '1px solid #00ffff',
                color: '#00ffff',
                borderRadius: '4px',
                cursor: 'pointer',
                fontWeight: '600',
                transition: 'all 0.2s',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'rgba(0, 255, 255, 0.3)'
                e.currentTarget.style.boxShadow = '0 0 10px rgba(0, 255, 255, 0.4)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'rgba(0, 255, 255, 0.2)'
                e.currentTarget.style.boxShadow = 'none'
              }}
            >
              View Full Leaderboard
            </button>
          )}
        </section>
      </section>
    </main>
  )
}

export default App
