import { useState } from 'react'
import './RaidBattle.css'

interface PartyMember {
  id: string
  name: string
  role: 'tank' | 'dps' | 'healer'
  hp: number
  maxHp: number
  mana: number
  maxMana: number
  damage: number
  defense: number
}

interface Enemy {
  id: string
  name: string
  hp: number
  maxHp: number
  damage: number
  attacks: string[]
}

interface RaidBattleProps {
  raidSessionId: string
  playerName: string
  playerRole: string
  onVictory: (loot: { xp: number; gold: number }) => void
  onDefeat: () => void
  onLeave: () => void
}

export function RaidBattle({ raidSessionId: _raidSessionId, playerName, playerRole, onVictory, onDefeat, onLeave }: RaidBattleProps) {
  const [battleLog, setBattleLog] = useState<string[]>(['Battle with Castle Anorak begins!'])
  const [party, setParty] = useState<PartyMember[]>([
    { id: playerName, name: playerName, role: playerRole as any, hp: 100, maxHp: 100, mana: 100, maxMana: 100, damage: 15, defense: 10 },
    { id: 'ally1', name: 'Ally One', role: 'dps', hp: 80, maxHp: 80, mana: 50, maxMana: 50, damage: 20, defense: 5 },
    { id: 'ally2', name: 'Ally Two', role: 'healer', hp: 60, maxHp: 60, mana: 120, maxMana: 120, damage: 5, defense: 8 },
  ])
  const [enemy, setEnemy] = useState<Enemy>({
    id: 'anorak-keeper',
    name: 'Keeper of Castle Anorak',
    hp: 300,
    maxHp: 300,
    damage: 25,
    attacks: ['Fireball', 'Dark Curse', 'Laser Beam'],
  })
  const [gameState, setGameState] = useState<'combat' | 'victory' | 'defeat'>('combat')
  const [turn, setTurn] = useState(0)

  const addLog = (message: string) => {
    setBattleLog((prev) => [...prev, `[Turn ${turn}] ${message}`])
  }

  const handleAttack = () => {
    const player = party[0]
    const damage = player.damage + Math.random() * 10 - 5
    const newEnemyHp = Math.max(0, enemy.hp - damage)

    addLog(`${player.name} attacks ${enemy.name} for ${Math.round(damage)} damage!`)

    setEnemy((prev) => ({ ...prev, hp: newEnemyHp }))

    if (newEnemyHp <= 0) {
      setTimeout(() => {
        setGameState('victory')
        setBattleLog((prev) => [...prev, `Victory! ${enemy.name} has been defeated!`])
      }, 500)
    } else {
      handleEnemyAttack()
    }
  }

  const handleHeal = () => {
    const healer = party.find((m) => m.role === 'healer')
    if (!healer || healer.mana < 30) {
      addLog('Insufficient mana for healing!')
      return
    }

    const target = party[0]
    const healAmount = 50
    const newHp = Math.min(target.maxHp, target.hp + healAmount)

    addLog(`${healer.name} casts Healing Light on ${target.name} for ${healAmount} HP!`)

    setParty((prev) =>
      prev.map((m) => (m.id === target.id ? { ...m, hp: newHp } : m.id === healer.id ? { ...m, mana: m.mana - 30 } : m)),
    )

    handleEnemyAttack()
  }

  const handleDefend = () => {
    const player = party[0]
    addLog(`${player.name} takes a defensive stance, reducing incoming damage!`)

    setParty((prev) => prev.map((m) => (m.id === player.id ? { ...m, defense: m.defense + 5 } : m)))

    setTimeout(() => {
      setParty((prev) => prev.map((m) => (m.id === player.id ? { ...m, defense: m.defense - 5 } : m)))
      handleEnemyAttack()
    }, 500)
  }

  const handleEnemyAttack = () => {
    setTimeout(() => {
      const attack = enemy.attacks[Math.floor(Math.random() * enemy.attacks.length)]
      const target = party[0]
      const damage = Math.max(1, enemy.damage - target.defense / 2 + Math.random() * 10 - 5)
      const newHp = Math.max(0, target.hp - damage)

      addLog(`${enemy.name} uses ${attack} on ${target.name} for ${Math.round(damage)} damage!`)

      setParty((prev) => prev.map((m) => (m.id === target.id ? { ...m, hp: newHp } : m)))

      if (newHp <= 0) {
        setGameState('defeat')
        setBattleLog((prev) => [...prev, `Defeat! ${target.name} has fallen!`])
      } else {
        setTurn((prev) => prev + 1)
      }
    }, 800)
  }

  if (gameState === 'victory') {
    return (
      <div className="raid-battle-overlay">
        <div className="raid-battle-container">
          <div className="victory-screen">
            <h2>Victory!</h2>
            <p>You have defeated the Keeper of Castle Anorak!</p>
            <div className="victory-rewards">
              <div className="reward">
                <span>Experience</span>
                <strong>500 XP</strong>
              </div>
              <div className="reward">
                <span>Gold</span>
                <strong>250 Gold</strong>
              </div>
            </div>
            <button
              className="victory-btn"
              onClick={() => {
                onVictory({ xp: 500, gold: 250 })
              }}
            >
              Continue
            </button>
          </div>
        </div>
      </div>
    )
  }

  if (gameState === 'defeat') {
    return (
      <div className="raid-battle-overlay">
        <div className="raid-battle-container">
          <div className="defeat-screen">
            <h2>Defeat</h2>
            <p>Your party has fallen. Better luck next time!</p>
            <button className="continue-btn" onClick={onDefeat}>
              Return to Lobby
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="raid-battle-overlay">
      <div className="raid-battle-container">
        <div className="battle-header">
          <h2>Castle Anorak</h2>
          <button className="leave-btn" onClick={onLeave}>
            Leave Raid
          </button>
        </div>

        <div className="battle-area">
          <div className="enemy-section">
            <div className="enemy-card">
              <h3>{enemy.name}</h3>
              <div className="hp-bar">
                <div className="hp-fill" style={{ width: `${(enemy.hp / enemy.maxHp) * 100}%` }}></div>
              </div>
              <p className="hp-text">
                {Math.round(enemy.hp)} / {enemy.maxHp}
              </p>
            </div>
          </div>

          <div className="party-section">
            <h3>Your Party</h3>
            <div className="party-roster">
              {party.map((member) => (
                <div key={member.id} className="party-member">
                  <div className="member-info">
                    <span className="member-name">{member.name}</span>
                    <span className={`member-role role-${member.role}`}>{member.role.toUpperCase()}</span>
                  </div>
                  <div className="member-hp">
                    <div className="hp-bar small">
                      <div className="hp-fill" style={{ width: `${(member.hp / member.maxHp) * 100}%` }}></div>
                    </div>
                    <span className="hp-text">{Math.round(member.hp)}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="battle-log-section">
          <h3>Battle Log</h3>
          <div className="battle-log">
            {battleLog.slice(-5).map((log, i) => (
              <p key={i}>{log}</p>
            ))}
          </div>
        </div>

        <div className="battle-actions">
          <button className="action-btn attack" onClick={handleAttack}>
            ⚔ Attack
          </button>
          <button className="action-btn defend" onClick={handleDefend}>
            🛡 Defend
          </button>
          <button className="action-btn heal" onClick={handleHeal}>
            💚 Heal
          </button>
        </div>
      </div>
    </div>
  )
}
