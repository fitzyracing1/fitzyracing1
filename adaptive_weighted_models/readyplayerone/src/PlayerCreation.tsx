import { useState } from 'react'
import './PlayerCreation.css'

interface PlayerCreationProps {
  onCreate: (username: string, faction: string) => Promise<void>
}

export function PlayerCreation({ onCreate }: PlayerCreationProps) {
  const [username, setUsername] = useState('')
  const [faction, setFaction] = useState('Gunters')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!username.trim()) {
      setError('Username is required')
      return
    }

    setLoading(true)
    setError('')

    try {
      await onCreate(username, faction)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create player')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="player-creation-overlay">
      <div className="player-creation-modal">
        <h2>Welcome to the OASIS</h2>
        <p>Enter your details to begin your adventure</p>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username">Avatar Name</label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="e.g., Parzival"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label>Faction</label>
            <div className="faction-choices">
              {[
                { id: 'Gunters', color: '#ffd700', desc: 'Puzzle solvers' },
                { id: 'Rebels', color: '#00ffff', desc: 'Defenders' },
                { id: 'Sixers', color: '#ff1744', desc: 'Aggressive tactics' },
              ].map((f) => (
                <label key={f.id} className={`faction-option ${faction === f.id ? 'selected' : ''}`}>
                  <input type="radio" name="faction" value={f.id} checked={faction === f.id} onChange={(e) => setFaction(e.target.value)} disabled={loading} />
                  <div
                    className="faction-badge"
                    style={{ backgroundColor: f.color }}
                  >
                    {f.id}
                  </div>
                  <span>{f.desc}</span>
                </label>
              ))}
            </div>
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? 'Creating...' : 'Enter OASIS'}
          </button>
        </form>
      </div>
    </div>
  )
}
