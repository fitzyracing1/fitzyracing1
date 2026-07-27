import './PlayerProfile.css'

interface Player {
  id: string
  username: string
  faction: 'Gunters' | 'Rebels' | 'Sixers'
  level: number
  experience: number
  score: number
  created_at: string
  updated_at: string
}

interface PlayerProfileProps {
  player: Player
  onBack: () => void
}

export function PlayerProfile({ player, onBack }: PlayerProfileProps) {
  return (
    <div className="player-profile">
      <button className="back-btn" onClick={onBack}>
        ← Back
      </button>

      <div className="profile-header">
        <div
          className="avatar"
          style={{
            backgroundColor: '#00ffff',
          }}
        >
          {player.username.charAt(0).toUpperCase()}
        </div>
        <div className="profile-info">
          <h2>{player.username}</h2>
          <p className="faction-tag">{player.faction}</p>
          <p className="level">Level {player.level}</p>
        </div>
      </div>

      <div className="profile-stats">
        <div className="stat">
          <span className="stat-label">Experience</span>
          <span className="stat-value">{player.experience.toLocaleString()}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Score</span>
          <span className="stat-value">{player.score.toLocaleString()}</span>
        </div>
        <div className="stat">
          <span className="stat-label">Member Since</span>
          <span className="stat-value">{new Date(player.created_at).toLocaleDateString()}</span>
        </div>
      </div>

      <div className="profile-section">
        <h3>Active Quests</h3>
        <div className="quest-list">
          <div className="quest-item in-progress">
            <span className="quest-name">Copper Key</span>
            <span className="quest-progress">45%</span>
          </div>
          <div className="quest-item available">
            <span className="quest-name">Jade Key</span>
            <span className="quest-status">Available</span>
          </div>
          <div className="quest-item locked">
            <span className="quest-name">Crystal Key</span>
            <span className="quest-status">Level 10+</span>
          </div>
        </div>
      </div>
    </div>
  )
}
