import { useEffect, useState } from 'react'
import './Leaderboard.css'

interface LeaderboardEntry {
  rank: number
  player_id?: string
  username?: string
  player?: string
  faction: string
  level?: number
  score: number
}

interface LeaderboardProps {
  onBack: () => void
}

export function Leaderboard({ onBack }: LeaderboardProps) {
  const [entries, setEntries] = useState<LeaderboardEntry[]>([])
  const [selectedFaction, setSelectedFaction] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchLeaderboard = async () => {
      try {
        const url = selectedFaction ? `/api/leaderboard?faction=${selectedFaction}&limit=20` : '/api/leaderboard?limit=20'
        const response = await fetch(url)
        if (response.ok) {
          const data = await response.json()
          setEntries(data.entries)
        }
      } catch (err) {
        console.error('Failed to fetch leaderboard:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchLeaderboard()
    const interval = setInterval(fetchLeaderboard, 5000)
    return () => clearInterval(interval)
  }, [selectedFaction])

  return (
    <div className="leaderboard-container">
      <div className="leaderboard-header">
        <h2>Seasonal Leaderboard</h2>
        <button className="back-btn" onClick={onBack}>
          ← Back
        </button>
      </div>

      <div className="faction-filters">
        <button
          className={`filter-btn ${!selectedFaction ? 'active' : ''}`}
          onClick={() => setSelectedFaction(null)}
        >
          All Factions
        </button>
        <button
          className={`filter-btn gunters ${selectedFaction === 'Gunters' ? 'active' : ''}`}
          onClick={() => setSelectedFaction('Gunters')}
        >
          Gunters
        </button>
        <button
          className={`filter-btn rebels ${selectedFaction === 'Rebels' ? 'active' : ''}`}
          onClick={() => setSelectedFaction('Rebels')}
        >
          Rebels
        </button>
        <button
          className={`filter-btn sixers ${selectedFaction === 'Sixers' ? 'active' : ''}`}
          onClick={() => setSelectedFaction('Sixers')}
        >
          Sixers
        </button>
      </div>

      {loading ? (
        <div className="loading">Fetching rankings...</div>
      ) : entries.length === 0 ? (
        <div className="empty-state">No players yet. Be the first!</div>
      ) : (
        <div className="leaderboard-table">
          <div className="table-header">
            <div className="rank">Rank</div>
            <div className="name">Player</div>
            <div className="faction">Faction</div>
            <div className="level">Level</div>
            <div className="score">Score</div>
          </div>

          <div className="table-body">
            {entries.map((entry, idx) => (
              <div key={`${entry.rank}-${idx}`} className={`table-row rank-${Math.min(entry.rank, 3)}`}>
                <div className="rank">
                  {entry.rank === 1 && '🥇'}
                  {entry.rank === 2 && '🥈'}
                  {entry.rank === 3 && '🥉'}
                  {entry.rank > 3 && `#${entry.rank}`}
                </div>
                <div className="name">{entry.username || entry.player}</div>
                <div className={`faction faction-${entry.faction.toLowerCase()}`}>{entry.faction}</div>
                <div className="level">{entry.level || '-'}</div>
                <div className="score">{entry.score.toLocaleString()}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
