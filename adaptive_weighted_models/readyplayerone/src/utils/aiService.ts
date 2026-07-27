/**
 * Weighted-Models AI Service Integration
 * Connects to the adaptive_weighted_models service for:
 * - Quest recommendations based on player profile
 * - Raid difficulty suggestions
 * - Meta balance analysis
 * - Seasonal drift detection
 */

const AI_API_URL = import.meta.env.VITE_WEIGHTED_MODELS_API || 'http://localhost:8000/v1'

export interface AIQuestRecommendation {
  quest_id: string
  match_score: number
  difficulty_adjustment: string
  narrative_hook: string
}

export interface AIRaidAnalysis {
  recommended_difficulty: string
  team_composition_score: number
  meta_recommendation: string
  balance_factor: number
}

export interface SeasonalDrift {
  dominant_faction: string
  meta_shift: string
  recommended_rebalance: string
  power_factor: number
}

/**
 * Get quest recommendations from AI service
 */
export async function getQuestRecommendations(
  playerProfile: {
    level: number
    faction: string
    recentScores: number[]
  },
): Promise<AIQuestRecommendation[]> {
  try {
    const response = await fetch(`${AI_API_URL}/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: `Given a ${playerProfile.faction} player level ${playerProfile.level} with recent performance scores of ${playerProfile.recentScores.join(', ')}, recommend the next quest they should attempt. Return: quest_id, match_score (0-1), difficulty_adjustment (easy/medium/hard), and a one-sentence narrative hook.`,
        context: playerProfile,
      }),
      signal: AbortSignal.timeout(5000),
    })

    if (!response.ok) {
      console.warn('AI quest recommendation failed')
      return []
    }

    return await response.json()
  } catch (error) {
    console.error('Error fetching quest recommendations:', error)
    return []
  }
}

/**
 * Get raid difficulty analysis from AI service
 */
export async function getRaidAnalysis(
  partyComposition: {
    tanks: number
    dps: number
    healers: number
  },
  playerLevels: number[],
): Promise<AIRaidAnalysis | null> {
  try {
    const response = await fetch(`${AI_API_URL}/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: `Analyze raid readiness for party composition: ${partyComposition.tanks} tanks, ${partyComposition.dps} DPS, ${partyComposition.healers} healers with player levels: ${playerLevels.join(', ')}. Return: recommended_difficulty, team_composition_score (0-1), meta recommendation, balance_factor.`,
        context: { partyComposition, playerLevels },
      }),
      signal: AbortSignal.timeout(5000),
    })

    if (!response.ok) {
      console.warn('AI raid analysis failed')
      return null
    }

    return await response.json()
  } catch (error) {
    console.error('Error fetching raid analysis:', error)
    return null
  }
}

/**
 * Get seasonal drift and meta analysis
 */
export async function getSeasonalDrift(
  factionStats: {
    faction: string
    totalScore: number
    memberCount: number
    avgLevel: number
  }[],
): Promise<SeasonalDrift | null> {
  try {
    const statsString = factionStats
      .map((f) => `${f.faction}: ${f.totalScore} points, ${f.memberCount} players, avg level ${f.avgLevel}`)
      .join('; ')

    const response = await fetch(`${AI_API_URL}/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: `Analyze faction meta balance based on: ${statsString}. Identify dominant faction, meta shift trend, and recommended rebalancing changes. Return: dominant_faction, meta_shift (description), recommended_rebalance, power_factor (1.0=balanced).`,
        context: { factionStats },
      }),
      signal: AbortSignal.timeout(5000),
    })

    if (!response.ok) {
      console.warn('AI drift analysis failed')
      return null
    }

    return await response.json()
  } catch (error) {
    console.error('Error fetching seasonal drift:', error)
    return null
  }
}

/**
 * Generate quest lore using AI
 */
export async function generateQuestLore(questId: string, questName: string): Promise<string> {
  try {
    const response = await fetch(`${AI_API_URL}/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: `Write a two-sentence quest narrative for "${questName}" (quest ID: ${questId}) in the OASIS universe inspired by "Ready Player One". Should be immersive and game-like. Keep it brief and suspenseful.`,
      }),
      signal: AbortSignal.timeout(5000),
    })

    if (!response.ok) {
      return `${questName} awaits in the OASIS. Can you complete this challenge?`
    }

    const data = await response.json()
    return data.narrative || `${questName} awaits in the OASIS. Can you complete this challenge?`
  } catch (error) {
    console.error('Error generating quest lore:', error)
    return `${questName} awaits in the OASIS. Can you complete this challenge?`
  }
}

/**
 * Suggest raid team composition balancing
 */
export async function suggestTeamBalance(
  playerRoles: { role: string; level: number; faction: string }[],
): Promise<{ suggestion: string; synergy_score: number }> {
  try {
    const rolesString = playerRoles
      .map((p) => `${p.role} (${p.faction}, Lvl ${p.level})`)
      .join(', ')

    const response = await fetch(`${AI_API_URL}/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: `Analyze raid team synergy for: ${rolesString}. Provide tactical suggestion for optimal play and synergy_score (0-1). Keep suggestion to one sentence.`,
        context: { playerRoles },
      }),
      signal: AbortSignal.timeout(5000),
    })

    if (!response.ok) {
      return { suggestion: 'Your team is ready. Coordinate role abilities for maximum effectiveness.', synergy_score: 0.75 }
    }

    return await response.json()
  } catch (error) {
    console.error('Error suggesting team balance:', error)
    return { suggestion: 'Your team is ready. Coordinate role abilities for maximum effectiveness.', synergy_score: 0.75 }
  }
}
