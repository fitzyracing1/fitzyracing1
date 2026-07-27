import { useState } from 'react'
import './RaidMatcher.css'

interface RaidMatcherProps {
  raidId: string
  raidName: string
  onJoinRaid: (role: string) => Promise<void>
  onClose: () => void
}

const ROLES = [
  { id: 'tank', name: 'Tank', desc: 'High defense, lead the team' },
  { id: 'dps', name: 'DPS', desc: 'High damage output' },
  { id: 'healer', name: 'Healer', desc: 'Support and recovery' },
]

export function RaidMatcher({ raidName, onJoinRaid, onClose }: RaidMatcherProps) {
  const [selectedRole, setSelectedRole] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleJoin = async () => {
    if (!selectedRole) return

    setLoading(true)
    try {
      await onJoinRaid(selectedRole)
      onClose()
    } catch (err) {
      console.error('Failed to join raid:', err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="raid-matcher-overlay">
      <div className="raid-matcher-modal">
        <h3>Join {raidName}</h3>
        <p>Select your role and match with other players</p>

        <div className="role-selection">
          {ROLES.map((role) => (
            <div
              key={role.id}
              className={`role-card ${selectedRole === role.id ? 'selected' : ''}`}
              onClick={() => setSelectedRole(role.id)}
            >
              <div className="role-icon">{role.name.charAt(0)}</div>
              <h4>{role.name}</h4>
              <p>{role.desc}</p>
            </div>
          ))}
        </div>

        <div className="raid-matcher-actions">
          <button className="cancel-btn" onClick={onClose} disabled={loading}>
            Cancel
          </button>
          <button className="join-btn" onClick={handleJoin} disabled={!selectedRole || loading}>
            {loading ? 'Joining...' : 'Join Raid'}
          </button>
        </div>
      </div>
    </div>
  )
}
