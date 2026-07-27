import { useEffect, useState } from 'react'
import { getSeasonalDrift } from './utils/aiService.ts'
import './SeasonalDrift.css'

interface FactionStats {
  faction: string
  totalScore: number
  memberCount: number
}

interface SeasonalDriftProps {
  factions: FactionStats[]
}

export function SeasonalDriftDisplay({ factions }: SeasonalDriftProps) {
  const [drift, setDrift] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const analyzeDrift = async () => {
      const stats = factions.map((f) => ({
        ...f,
        avgLevel: Math.ceil(f.totalScore / 100),
      }))
      const analysis = await getSeasonalDrift(stats)
      setDrift(analysis)
      setLoading(false)
    }

    analyzeDrift()
  }, [factions])

  if (loading) {
    return <div className="drift-loading">Analyzing meta...</div>
  }

  if (!drift) {
    return null
  }

  return (
    <div className="seasonal-drift">
      <h3>Meta Analysis</h3>
      <div className="drift-content">
        <p className="drift-dominant">
          <strong>Dominant Force:</strong> {drift.dominant_faction || 'Balanced'}
        </p>
        <p className="drift-shift">{drift.meta_shift || 'Meta remains stable'}</p>
        <p className="drift-recommendation">
          <em>Rebalance: {drift.recommended_rebalance || 'No changes needed'}</em>
        </p>
      </div>
    </div>
  )
}
