import { chooseBotCall, deriveContract, isAuctionComplete, isCallLegal, isPassout, legalCalls, nextAuctionSeat } from './auction'
import { deal, findCard, highCardPoints, nextSeat, partner, removeCard, sortCards, teamOf } from './cards'
import { scoreContract } from './scoring'
import type { AuctionEntry, Call, Card, GameState, NewGameOptions, PlayedCard, Seat, SeatConfig, Strain, Trick } from './types'

export const defaultSeats: SeatConfig = {
  N: 'bot',
  E: 'bot',
  S: 'human',
  W: 'bot',
}

export function createGame(options: NewGameOptions): GameState {
  const dealer = options.dealer ?? 'N'
  return {
    phase: 'auction',
    seats: options.seats,
    practice: options.practice,
    seed: options.seed,
    dealer,
    vulnerability: options.vulnerability ?? 'Both',
    hands: deal(options.seed),
    auction: [],
    contract: null,
    turn: dealer,
    leader: null,
    currentTrick: [],
    completedTricks: [],
    tricksWon: { NS: 0, EW: 0 },
    score: null,
  }
}

export function humanSeats(seats: SeatConfig): Seat[] {
  return (Object.entries(seats) as Array<[Seat, 'human' | 'bot']>)
    .filter(([, controller]) => controller === 'human')
    .map(([seat]) => seat)
}

export function activeControllerSeat(state: GameState): Seat {
  if (state.phase === 'play' && state.contract && state.turn === partner(state.contract.declarer)) {
    return state.contract.declarer
  }
  return state.turn
}

export function isHumanTurn(state: GameState) {
  return state.seats[activeControllerSeat(state)] === 'human'
}

export function applyCall(state: GameState, call: Call): GameState {
  if (state.phase !== 'auction') {
    throw new Error('Calls are only allowed during the auction.')
  }
  if (!isCallLegal(state.auction, state.turn, call)) {
    throw new Error('Illegal call.')
  }
  const auction: AuctionEntry[] = [...state.auction, { seat: state.turn, call }]
  if (isAuctionComplete(auction)) {
    if (isPassout(auction)) {
      return {
        ...state,
        phase: 'passedOut',
        auction,
        contract: null,
      }
    }
    const contract = deriveContract(auction)
    if (!contract) throw new Error('Could not derive contract.')
    const leader = nextSeat(contract.declarer)
    return {
      ...state,
      phase: 'play',
      auction,
      contract,
      leader,
      turn: leader,
    }
  }
  return {
    ...state,
    auction,
    turn: nextAuctionSeat(state.dealer, auction),
  }
}

export function legalCards(state: GameState, seat: Seat): Card[] {
  const hand = state.hands[seat]
  if (state.currentTrick.length === 0) return hand
  const ledSuit = state.currentTrick[0]!.card.suit
  const followingSuit = hand.filter((card) => card.suit === ledSuit)
  return followingSuit.length > 0 ? followingSuit : hand
}

export function isCardLegal(state: GameState, seat: Seat, cardId: string) {
  return legalCards(state, seat).some((card) => card.id === cardId)
}

export function playCard(state: GameState, seat: Seat, cardId: string): GameState {
  if (state.phase !== 'play') {
    throw new Error('Cards are only played after the auction.')
  }
  if (seat !== state.turn) {
    throw new Error('It is not that seat\'s turn.')
  }
  const card = findCard(state.hands[seat], cardId)
  if (!card) throw new Error('Card is not in hand.')
  if (!isCardLegal(state, seat, cardId)) throw new Error('Illegal card.')

  const hands = {
    ...state.hands,
    [seat]: removeCard(state.hands[seat], cardId),
  }
  const currentTrick = [...state.currentTrick, { seat, card }]
  if (currentTrick.length < 4) {
    return {
      ...state,
      hands,
      currentTrick,
      turn: nextSeat(seat),
    }
  }

  const winner = determineTrickWinner(currentTrick, state.contract!.strain, state.leader!)
  const trick: Trick = {
    leader: state.leader!,
    cards: currentTrick,
    winner,
  }
  const tricksWon = {
    ...state.tricksWon,
    [teamOf(winner)]: state.tricksWon[teamOf(winner)] + 1,
  }
  const completedTricks = [...state.completedTricks, trick]
  if (completedTricks.length === 13) {
    const contract = state.contract!
    const declarerTeam = teamOf(contract.declarer)
    const score = scoreContract(contract, tricksWon[declarerTeam], state.vulnerability)
    return {
      ...state,
      phase: 'complete',
      hands,
      currentTrick: [],
      completedTricks,
      tricksWon,
      score,
      turn: winner,
      leader: winner,
    }
  }
  return {
    ...state,
    hands,
    currentTrick: [],
    completedTricks,
    tricksWon,
    turn: winner,
    leader: winner,
  }
}

export function determineTrickWinner(cards: PlayedCard[], strain: Strain, leader: Seat): Seat {
  const ledSuit = cards[0]!.card.suit
  const trumpCards = strain === 'NT' ? [] : cards.filter((played) => played.card.suit === strain)
  const candidates = trumpCards.length > 0 ? trumpCards : cards.filter((played) => played.card.suit === ledSuit)
  const winner = candidates.reduce((best, played) => played.card.rank > best.card.rank ? played : best)
  return winner.seat ?? leader
}

export function chooseBotCard(state: GameState, seat: Seat): Card {
  const legal = legalCards(state, seat)
  return sortCards(legal).at(-1)!
}

export function advanceBotOnce(state: GameState): GameState {
  if (state.phase === 'auction' && !isHumanTurn(state)) {
    return applyCall(state, chooseBotCall(state.auction, state.turn, state.hands[state.turn]))
  }
  if (state.phase === 'play' && !isHumanTurn(state)) {
    const card = chooseBotCard(state, state.turn)
    return playCard(state, state.turn, card.id)
  }
  return state
}

export function advanceBots(state: GameState, limit = 256): GameState {
  let next = state
  for (let index = 0; index < limit; index += 1) {
    if (isHumanTurn(next) || next.phase === 'complete' || next.phase === 'passedOut') return next
    next = advanceBotOnce(next)
  }
  throw new Error('Bot advancement did not settle.')
}

export function visibleSeatCards(state: GameState, seat: Seat, readySeat: Seat | null): boolean {
  if (state.practice) return true
  if (state.phase === 'play' && state.contract && seat === partner(state.contract.declarer) && state.completedTricks.length + state.currentTrick.length > 0) {
    return true
  }
  if (state.seats[seat] === 'human') {
    if (humanSeats(state.seats).length <= 1) return true
    return readySeat === seat
  }
  return false
}

export function needsHotseatReady(state: GameState, readySeat: Seat | null): Seat | null {
  if (state.practice || !isHumanTurn(state)) return null
  const controller = activeControllerSeat(state)
  if (humanSeats(state.seats).length <= 1) return null
  return readySeat === controller ? null : controller
}

export function handStrengthLabel(cards: Card[]) {
  return `${highCardPoints(cards)} HCP`
}

export function allLegalCalls(state: GameState) {
  return legalCalls(state.auction, state.turn)
}
