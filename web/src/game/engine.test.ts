import { describe, expect, it } from 'vitest'

import { callLabel } from './auction'
import { cardLabel, deal, partner, teamOf } from './cards'
import {
  activeControllerSeat,
  advanceBots,
  allLegalCalls,
  createGame,
  defaultSeats,
  determineTrickWinner,
  isHumanTurn,
  legalCards,
  needsHotseatReady,
  playCard,
  visibleSeatCards,
} from './engine'
import { scoreContract } from './scoring'
import type { Card, Contract, PlayedCard, SeatConfig } from './types'

function card(id: string): Card {
  const suit = id[0] as Card['suit']
  const label = id.slice(1)
  const rank = ({ J: 11, Q: 12, K: 13, A: 14 } as Record<string, number>)[label] ?? Number(label)
  return { id, suit, rank: rank as Card['rank'] }
}

describe('game engine', () => {
  it('deals deterministically from a seed', () => {
    expect(deal(42)).toEqual(deal(42))
    expect(deal(42)).not.toEqual(deal(43))
  })

  it('starts with legal auction calls for the dealer', () => {
    const state = createGame({ seats: defaultSeats, practice: false, seed: 7 })

    expect(state.phase).toBe('auction')
    expect(state.turn).toBe('N')
    expect(allLegalCalls(state).map(callLabel)).toContain('Pass')
    expect(allLegalCalls(state).map(callLabel)).toContain('1C')
  })

  it('recognizes bot-only games and advances them to a terminal state', () => {
    const seats: SeatConfig = { N: 'bot', E: 'bot', S: 'bot', W: 'bot' }
    const state = createGame({ seats, practice: true, seed: 13 })

    const finalState = advanceBots(state)

    expect(['passedOut', 'complete']).toContain(finalState.phase)
  })

  it('enforces follow suit when possible', () => {
    const state = createGame({ seats: defaultSeats, practice: false, seed: 1 })
    const contract: Contract = { level: 1, strain: 'S', declarer: 'S', bidder: 'S', doubled: 'none' }
    const playState = {
      ...state,
      phase: 'play' as const,
      contract,
      leader: 'N' as const,
      turn: 'E' as const,
      currentTrick: [{ seat: 'N' as const, card: card('H2') }],
      hands: {
        ...state.hands,
        E: [card('H3'), card('C4')],
      },
    }

    expect(legalCards(playState, 'E').map(cardLabel)).toEqual(['3♥'])
  })

  it('lets trump beat later high led-suit cards', () => {
    const played: PlayedCard[] = [
      { seat: 'N', card: card('S2') },
      { seat: 'E', card: card('H3') },
      { seat: 'S', card: card('SA') },
      { seat: 'W', card: card('C2') },
    ]

    expect(determineTrickWinner(played, 'H', 'N')).toBe('E')
  })

  it('makes declarer control dummy during play', () => {
    const state = createGame({ seats: { N: 'bot', E: 'bot', S: 'human', W: 'bot' }, practice: false, seed: 4 })
    const contract: Contract = { level: 1, strain: 'C', declarer: 'S', bidder: 'S', doubled: 'none' }
    const playState = {
      ...state,
      phase: 'play' as const,
      contract,
      turn: partner('S'),
    }

    expect(activeControllerSeat(playState)).toBe('S')
    expect(isHumanTurn(playState)).toBe(true)
  })

  it('scores vulnerable doubled contracts and assigns partnership scores', () => {
    const contract: Contract = {
      level: 4,
      strain: 'H',
      declarer: 'S',
      bidder: 'S',
      doubled: 'double',
    }

    const score = scoreContract(contract, 10, 'Both')

    expect(score.declarerScore).toBe(790)
    expect(score.nsScore).toBe(790)
    expect(score.ewScore).toBe(-790)
  })

  it('hides non-practice human hotseat hands until that seat is ready', () => {
    const state = createGame({
      seats: { N: 'human', E: 'bot', S: 'human', W: 'bot' },
      practice: false,
      seed: 9,
    })

    expect(needsHotseatReady(state, null)).toBe('N')
    expect(visibleSeatCards(state, 'N', null)).toBe(false)
    expect(visibleSeatCards(state, 'N', 'N')).toBe(true)
    expect(visibleSeatCards({ ...state, practice: true }, 'S', null)).toBe(true)
  })

  it('shows the only human player hand without a handoff gate', () => {
    const state = createGame({
      seats: { N: 'bot', E: 'bot', S: 'human', W: 'bot' },
      practice: false,
      seed: 11,
    })

    expect(visibleSeatCards(state, 'S', null)).toBe(true)
  })

  it('plays a card through the same state path humans and bots use', () => {
    const state = createGame({ seats: defaultSeats, practice: false, seed: 1 })
    const contract: Contract = { level: 1, strain: 'NT', declarer: 'S', bidder: 'S', doubled: 'none' }
    const playState = {
      ...state,
      phase: 'play' as const,
      contract,
      leader: 'N' as const,
      turn: 'N' as const,
      hands: {
        ...state.hands,
        N: [card('C2')],
      },
    }

    const next = playCard(playState, 'N', 'C2')

    expect(next.currentTrick).toHaveLength(1)
    expect(next.turn).toBe('E')
    expect(next.hands.N).toHaveLength(0)
  })

  it('uses bridge partnerships for trick counts', () => {
    expect(teamOf('N')).toBe('NS')
    expect(teamOf('E')).toBe('EW')
  })
})
