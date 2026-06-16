import { describe, expect, it, vi } from 'vitest'

import { createGame, defaultSeats } from './engine'
import { PRIVACY_POLICY_VERSION, TRAINING_RECORD_SCHEMA, submitTrainingRecord, trainingRecordFromGame } from './trainingRecord'

describe('training records', () => {
  it('serializes completed games without browser or player identifiers', () => {
    const game = {
      ...createGame({ seats: defaultSeats, practice: false, seed: 20260615, dealer: 'N', vulnerability: 'None' }),
      phase: 'passedOut' as const,
    }

    const record = trainingRecordFromGame(game, 1, '2026-06-16T00:00:00.000Z')
    const serialized = JSON.stringify(record)

    expect(record.schema).toBe(TRAINING_RECORD_SCHEMA)
    expect(record.consent).toEqual({
      shareForTraining: true,
      privacyPolicyVersion: PRIVACY_POLICY_VERSION,
    })
    expect(record.game.boardNumber).toBe(1)
    expect(record.game.hands.N).toHaveLength(13)
    expect(serialized).not.toMatch(/userAgent|playerName|sessionId|visitorId|email/i)
  })

  it('rejects unfinished games', () => {
    const game = createGame({ seats: defaultSeats, practice: false, seed: 20260615 })

    expect(() => trainingRecordFromGame(game, 1)).toThrow(/completed or passed-out/i)
  })

  it('submits records to the same-origin training endpoint by default', async () => {
    const game = {
      ...createGame({ seats: defaultSeats, practice: false, seed: 20260615, dealer: 'N', vulnerability: 'None' }),
      phase: 'passedOut' as const,
    }
    const record = trainingRecordFromGame(game, 1, '2026-06-16T00:00:00.000Z')
    const fetcher = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        ok: true,
        recordId: '0123456789abcdef01234567',
        storage: 'r2',
        policyVersion: PRIVACY_POLICY_VERSION,
      }),
    })

    const result = await submitTrainingRecord(record, fetcher)
    expect(fetcher.mock.calls[0]).toBeDefined()
    const [url, options] = fetcher.mock.calls[0]!
    const body = JSON.parse(options.body)

    expect(result).toEqual({
      ok: true,
      recordId: '0123456789abcdef01234567',
      storage: 'r2',
      policyVersion: PRIVACY_POLICY_VERSION,
    })
    expect(url).toBe('/api/training/games')
    expect(options.method).toBe('POST')
    expect(options.headers).toEqual({ 'Content-Type': 'application/json' })
    expect(body.schema).toBe(TRAINING_RECORD_SCHEMA)
    expect(body.consent.shareForTraining).toBe(true)
  })
})
