import { describe, expect, it } from 'vitest'

import {
  createBotViewFromGame,
  createBotViewFromObservation,
  type ExternalBotObservation,
  nextExternalBotAction,
} from './bot'
import { createGame } from './engine'
import type { Card, Contract } from './types'

function card(id: string): Card {
  const suit = id[0] as Card['suit']
  const label = id.slice(1)
  const rank = ({ J: 11, Q: 12, K: 13, A: 14 } as Record<string, number>)[label] ?? Number(label)
  return { id, suit, rank: rank as Card['rank'] }
}

function baseObservation(overrides: Partial<ExternalBotObservation> = {}): ExternalBotObservation {
  return {
    source: 'bridge-service',
    botSeats: ['N'],
    phase: 'auction',
    dealer: 'N',
    vulnerability: 'None',
    auction: [],
    contract: null,
    turn: 'N',
    leader: null,
    currentTrick: [],
    completedTricks: [],
    tricksWon: { NS: 0, EW: 0 },
    privateHands: {
      N: [card('SA'), card('HK'), card('DQ'), card('CJ')],
    },
    publicHands: {},
    score: null,
    ...overrides,
  }
}

describe('limited-information bot views', () => {
  it('does not expose other local hands even when practice mode reveals them in the UI', () => {
    const state = createGame({
      seats: { N: 'bot', E: 'bot', S: 'bot', W: 'bot' },
      practice: true,
      seed: 21,
    })

    const view = createBotViewFromGame(state, 'N')

    expect(Object.keys(view.knownHands)).toEqual(['N'])
    expect(JSON.stringify(view)).not.toContain(state.hands.E[0]!.id)
    expect(JSON.stringify(view)).not.toContain(state.hands.S[0]!.id)
    expect(JSON.stringify(view)).not.toContain(state.hands.W[0]!.id)
  })

  it('sanitizes four controlled external bot seats to the active seat only', () => {
    const observation = baseObservation({
      botSeats: ['N', 'E', 'S', 'W'],
      turn: 'E',
      privateHands: {
        N: [card('SA')],
        E: [card('HK')],
        S: [card('DQ')],
        W: [card('CJ')],
      },
    })

    const view = createBotViewFromObservation(observation)
    const action = nextExternalBotAction(observation)

    expect(view.controllerSeat).toBe('E')
    expect(view.knownHands.E?.map((knownCard) => knownCard.id)).toEqual(['HK'])
    expect(view.knownHands.N).toBeUndefined()
    expect(view.knownHands.S).toBeUndefined()
    expect(view.knownHands.W).toBeUndefined()
    expect(JSON.stringify(view)).not.toContain('SA')
    expect(JSON.stringify(view)).not.toContain('DQ')
    expect(JSON.stringify(view)).not.toContain('CJ')
    expect(action.kind).toBe('call')
  })

  it('waits when no bot seat is controlled or the active bot hand is missing', () => {
    expect(nextExternalBotAction(baseObservation({ botSeats: [] }))).toMatchObject({
      kind: 'wait',
      reason: 'Seat N is not controlled by this bot.',
    })

    expect(nextExternalBotAction(baseObservation({ privateHands: {} }))).toMatchObject({
      kind: 'wait',
      reason: 'Missing private hand for N.',
    })
  })

  it('keeps partner and opponent hands hidden from physical-table bot observations', () => {
    const observation = baseObservation({
      source: 'physical-table',
      botSeats: ['S'],
      turn: 'S',
      privateHands: {
        N: [card('SA')],
        E: [card('HK')],
        S: [card('DQ')],
        W: [card('CJ')],
      },
    })

    const view = createBotViewFromObservation(observation)

    expect(view.source).toBe('physical-table')
    expect(Object.keys(view.knownHands)).toEqual(['S'])
    expect(JSON.stringify(view)).not.toContain('SA')
    expect(JSON.stringify(view)).not.toContain('HK')
    expect(JSON.stringify(view)).not.toContain('CJ')
  })

  it('allows declarer to act from dummy only after dummy is public', () => {
    const contract: Contract = { level: 1, strain: 'S', declarer: 'S', bidder: 'S', doubled: 'none' }
    const beforeDummy = baseObservation({
      botSeats: ['S', 'N'],
      phase: 'play',
      contract,
      turn: 'N',
      leader: 'W',
      privateHands: {
        N: [card('SA')],
        S: [card('S2')],
        W: [card('C2')],
      },
    })
    const afterDummy = baseObservation({
      ...beforeDummy,
      currentTrick: [{ seat: 'W', card: card('C2') }],
    })

    const hiddenView = createBotViewFromObservation(beforeDummy, 'S')
    const publicView = createBotViewFromObservation(afterDummy, 'S')

    expect(hiddenView.knownHands.N).toBeUndefined()
    expect(hiddenView.canAct).toBe(false)
    expect(publicView.knownHands.N?.map((knownCard) => knownCard.id)).toEqual(['SA'])
    expect(publicView.actionHand.map((knownCard) => knownCard.id)).toEqual(['SA'])
    expect(publicView.canAct).toBe(true)
  })
})
