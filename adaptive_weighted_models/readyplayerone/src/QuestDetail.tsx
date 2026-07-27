import './QuestDetail.css'

interface Quest {
  id: string
  name: string
  desc: string
  tier: string
  xpReward: number
  goldReward: number
  progress?: number
  completed?: boolean
}

interface QuestDetailProps {
  quest: Quest
  playerLevel: number
  onStart: () => void
  onComplete: () => void
  onBack: () => void
}

export function QuestDetail({ quest, playerLevel, onStart, onComplete: _onComplete, onBack }: QuestDetailProps) {
  const canStart = playerLevel >= (quest.tier === 'expert' ? 10 : quest.tier === 'intermediate' ? 5 : 1)

  return (
    <div className="quest-detail-overlay">
      <div className="quest-detail-modal">
        <button className="close-btn" onClick={onBack}>
          ✕
        </button>

        <div className="quest-header">
          <h2>{quest.name}</h2>
          <span className={`tier-badge tier-${quest.tier}`}>{quest.tier.toUpperCase()}</span>
        </div>

        <p className="quest-description">{quest.desc}</p>

        <div className="quest-rewards">
          <div className="reward-item">
            <span className="reward-label">Experience</span>
            <span className="reward-value xp">{quest.xpReward}</span>
          </div>
          <div className="reward-item">
            <span className="reward-label">Gold</span>
            <span className="reward-value gold">{quest.goldReward}</span>
          </div>
        </div>

        {quest.progress !== undefined && (
          <div className="quest-progress">
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${quest.progress}%` }}></div>
            </div>
            <p className="progress-text">{quest.progress}% Complete</p>
          </div>
        )}

        <div className="quest-lore">
          <h3>Story</h3>
          <p>
            {quest.id === 'copper-key' &&
              'Wade\'s first trial: solve Halliday\'s copper key riddle. A test of wit and persistence through the OASIS archives.'}
            {quest.id === 'jade-key' &&
              'The green key awaits in a joust competition. Prove your reflexes and tactical positioning in the game arena.'}
            {quest.id === 'crystal-key' &&
              'The final trial demands deep knowledge of OASIS lore. Uncover Halliday\'s secrets hidden across sectors.'}
          </p>
        </div>

        <div className="quest-actions">
          <button className="action-btn secondary" onClick={onBack}>
            Back
          </button>
          {!quest.completed ? (
            <button
              className="action-btn primary"
              onClick={onStart}
              disabled={!canStart}
              title={!canStart ? `Requires Level ${quest.tier === 'expert' ? 10 : 5}` : ''}
            >
              {quest.progress ? 'Continue' : 'Start Quest'}
            </button>
          ) : (
            <button className="action-btn success" disabled>
              ✓ Completed
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
