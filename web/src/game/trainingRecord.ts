import type { GameState } from './types'

export const TRAINING_RECORD_SCHEMA = 'bridgebot.training_game.v1'
export const PRIVACY_POLICY_VERSION = '2026-06-16'

export type TrainingRecord = {
  schema: typeof TRAINING_RECORD_SCHEMA
  source: 'bridgebot-web'
  recordedAt: string
  consent: {
    shareForTraining: true
    privacyPolicyVersion: typeof PRIVACY_POLICY_VERSION
  }
  game: {
    boardNumber: number
    seed: number
    dealer: GameState['dealer']
    vulnerability: GameState['vulnerability']
    phase: 'complete' | 'passedOut'
    seats: GameState['seats']
    hands: GameState['hands']
    auction: GameState['auction']
    contract: GameState['contract']
    currentTrick: GameState['currentTrick']
    completedTricks: GameState['completedTricks']
    tricksWon: GameState['tricksWon']
    score: GameState['score']
  }
}

export type TrainingSubmitResult =
  | { ok: true; recordId: string; storage: string; policyVersion: string }
  | { ok: false; reason: 'network' | 'server'; status?: number }

export function isRecordableTrainingGame(game: GameState): game is GameState & { phase: 'complete' | 'passedOut' } {
  return game.phase === 'complete' || game.phase === 'passedOut'
}

export function trainingRecordFromGame(
  game: GameState,
  boardNumber: number,
  recordedAt = new Date().toISOString(),
): TrainingRecord {
  if (!isRecordableTrainingGame(game)) {
    throw new Error('Only completed or passed-out games can be recorded for training.')
  }

  return {
    schema: TRAINING_RECORD_SCHEMA,
    source: 'bridgebot-web',
    recordedAt,
    consent: {
      shareForTraining: true,
      privacyPolicyVersion: PRIVACY_POLICY_VERSION,
    },
    game: {
      boardNumber,
      seed: game.seed,
      dealer: game.dealer,
      vulnerability: game.vulnerability,
      phase: game.phase,
      seats: game.seats,
      hands: game.hands,
      auction: game.auction,
      contract: game.contract,
      currentTrick: game.currentTrick,
      completedTricks: game.completedTricks,
      tricksWon: game.tricksWon,
      score: game.score,
    },
  }
}

export async function submitTrainingRecord(
  record: TrainingRecord,
  fetcher: typeof fetch = fetch,
): Promise<TrainingSubmitResult> {
  try {
    const response = await fetcher(trainingEndpoint(), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(record),
    })

    if (!response.ok) {
      return { ok: false, reason: 'server', status: response.status }
    }

    return await response.json() as TrainingSubmitResult
  } catch {
    return { ok: false, reason: 'network' }
  }
}

function trainingEndpoint() {
  const configuredBase = import.meta.env.VITE_BRIDGEBOT_API_URL?.trim()
  if (!configuredBase) return '/api/training/games'
  return `${configuredBase.replace(/\/+$/, '')}/api/training/games`
}
