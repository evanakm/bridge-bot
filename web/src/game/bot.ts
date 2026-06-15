import { chooseBotCall, legalCalls } from './auction'
import { partner, sortCards } from './cards'
import type {
  AuctionEntry,
  Call,
  Card,
  Contract,
  GameState,
  Phase,
  PlayedCard,
  ScoreResult,
  Seat,
  Trick,
  Vulnerability,
} from './types'

export type BotTableSource = 'local' | 'bridge-service' | 'physical-table'

export type BotDecision =
  | { kind: 'wait'; reason: string }
  | { kind: 'call'; controllerSeat: Seat; seat: Seat; call: Call }
  | { kind: 'play'; controllerSeat: Seat; seat: Seat; card: Card; cardId: string }

export type ExternalBotObservation = {
  source: Exclude<BotTableSource, 'local'>
  botSeats: readonly Seat[]
  phase: Phase
  dealer: Seat
  vulnerability: Vulnerability
  auction: readonly AuctionEntry[]
  contract: Contract | null
  turn: Seat
  leader: Seat | null
  currentTrick: readonly PlayedCard[]
  completedTricks: readonly Trick[]
  tricksWon: Readonly<Record<'NS' | 'EW', number>>
  privateHands: Partial<Record<Seat, readonly Card[]>>
  publicHands?: Partial<Record<Seat, readonly Card[]>>
  score?: ScoreResult | null
}

export type BotSeatView = {
  source: BotTableSource
  controllerSeat: Seat
  actionSeat: Seat
  phase: Phase
  dealer: Seat
  vulnerability: Vulnerability
  auction: readonly AuctionEntry[]
  contract: Contract | null
  turn: Seat
  leader: Seat | null
  currentTrick: readonly PlayedCard[]
  completedTricks: readonly Trick[]
  tricksWon: Readonly<Record<'NS' | 'EW', number>>
  score: ScoreResult | null
  ownHand: readonly Card[]
  actionHand: readonly Card[]
  knownHands: Partial<Record<Seat, readonly Card[]>>
  legalCalls: readonly Call[]
  legalCards: readonly Card[]
  canAct: boolean
  incompleteReason: string | null
}

type BotViewInput = {
  source: BotTableSource
  phase: Phase
  dealer: Seat
  vulnerability: Vulnerability
  auction: readonly AuctionEntry[]
  contract: Contract | null
  turn: Seat
  leader: Seat | null
  currentTrick: readonly PlayedCard[]
  completedTricks: readonly Trick[]
  tricksWon: Readonly<Record<'NS' | 'EW', number>>
  privateHands: Partial<Record<Seat, readonly Card[]>>
  publicHands?: Partial<Record<Seat, readonly Card[]>>
  score?: ScoreResult | null
}

export function createBotViewFromGame(state: GameState, controllerSeat = activeControllerSeatForTable(state)): BotSeatView {
  const dummy = publicDummySeat(state)
  const publicHands = dummy ? { [dummy]: state.hands[dummy] } : undefined
  return createBotView({
    source: 'local',
    phase: state.phase,
    dealer: state.dealer,
    vulnerability: state.vulnerability,
    auction: state.auction,
    contract: state.contract,
    turn: state.turn,
    leader: state.leader,
    currentTrick: state.currentTrick,
    completedTricks: state.completedTricks,
    tricksWon: state.tricksWon,
    privateHands: {
      [controllerSeat]: state.hands[controllerSeat],
      ...(dummy ? { [dummy]: state.hands[dummy] } : {}),
    },
    publicHands,
    score: state.score,
  }, controllerSeat)
}

export function createBotViewFromObservation(observation: ExternalBotObservation, controllerSeat = activeControllerSeatForTable(observation)): BotSeatView {
  return createBotView(observation, controllerSeat)
}

export function chooseBotActionForGame(state: GameState): BotDecision {
  return chooseBotAction(createBotViewFromGame(state))
}

export function nextExternalBotAction(observation: ExternalBotObservation): BotDecision {
  const controllerSeat = activeControllerSeatForTable(observation)
  if (!observation.botSeats.includes(controllerSeat)) {
    return { kind: 'wait', reason: `Seat ${controllerSeat} is not controlled by this bot.` }
  }
  return chooseBotAction(createBotViewFromObservation(observation, controllerSeat))
}

export function chooseBotAction(view: BotSeatView): BotDecision {
  if (!view.canAct) {
    return { kind: 'wait', reason: view.incompleteReason ?? 'This bot does not have enough information to act.' }
  }
  if (view.phase === 'auction') {
    return {
      kind: 'call',
      controllerSeat: view.controllerSeat,
      seat: view.actionSeat,
      call: chooseBotCall([...view.auction], view.actionSeat, [...view.ownHand]),
    }
  }
  if (view.phase === 'play') {
    const card = chooseBotCardFromView(view)
    return {
      kind: 'play',
      controllerSeat: view.controllerSeat,
      seat: view.actionSeat,
      card,
      cardId: card.id,
    }
  }
  return { kind: 'wait', reason: `No bot action is available during ${view.phase}.` }
}

export function chooseBotCardFromView(view: BotSeatView): Card {
  const card = sortCards([...view.legalCards]).at(-1)
  if (!card) throw new Error('No legal card is available from the bot view.')
  return card
}

export function legalCardsFromKnownHand(hand: readonly Card[], currentTrick: readonly PlayedCard[]): Card[] {
  if (currentTrick.length === 0) return cloneCards(hand)
  const ledSuit = currentTrick[0]!.card.suit
  const followingSuit = hand.filter((card) => card.suit === ledSuit)
  return cloneCards(followingSuit.length > 0 ? followingSuit : hand)
}

export function activeControllerSeatForTable(table: Pick<BotViewInput, 'phase' | 'contract' | 'turn'>): Seat {
  if (table.phase === 'play' && table.contract && table.turn === partner(table.contract.declarer)) {
    return table.contract.declarer
  }
  return table.turn
}

function createBotView(input: BotViewInput, controllerSeat: Seat): BotSeatView {
  const actionSeat = input.turn
  const ownHand = cloneCards(input.privateHands[controllerSeat] ?? [])
  const dummy = publicDummySeat(input)
  const dummyHand = dummy
    ? cloneCards(input.publicHands?.[dummy] ?? input.privateHands[dummy] ?? [])
    : []
  const actionHand = actionSeat === controllerSeat
    ? ownHand
    : actionSeat === dummy
      ? dummyHand
      : []
  const knownHands: Partial<Record<Seat, readonly Card[]>> = {}

  if (ownHand.length > 0) {
    knownHands[controllerSeat] = ownHand
  }
  if (dummy && dummyHand.length > 0) {
    knownHands[dummy] = dummyHand
  }

  const legalCards = input.phase === 'play' ? legalCardsFromKnownHand(actionHand, input.currentTrick) : []
  const availableCalls = input.phase === 'auction' ? legalCalls([...input.auction], actionSeat) : []
  const incompleteReason = missingInformationReason(input.phase, controllerSeat, actionSeat, ownHand, actionHand)

  return {
    source: input.source,
    controllerSeat,
    actionSeat,
    phase: input.phase,
    dealer: input.dealer,
    vulnerability: input.vulnerability,
    auction: cloneAuction(input.auction),
    contract: input.contract ? { ...input.contract } : null,
    turn: input.turn,
    leader: input.leader,
    currentTrick: clonePlayedCards(input.currentTrick),
    completedTricks: input.completedTricks.map((trick) => ({
      leader: trick.leader,
      winner: trick.winner,
      cards: clonePlayedCards(trick.cards),
    })),
    tricksWon: { ...input.tricksWon },
    score: input.score ? { ...input.score, contract: { ...input.score.contract } } : null,
    ownHand,
    actionHand,
    knownHands,
    legalCalls: availableCalls,
    legalCards,
    canAct: incompleteReason === null,
    incompleteReason,
  }
}

function publicDummySeat(input: Pick<BotViewInput, 'phase' | 'contract' | 'currentTrick' | 'completedTricks'>): Seat | null {
  if (input.phase !== 'play' || !input.contract) return null
  const dummy = partner(input.contract.declarer)
  return input.currentTrick.length + input.completedTricks.length > 0 ? dummy : null
}

function missingInformationReason(
  phase: Phase,
  controllerSeat: Seat,
  actionSeat: Seat,
  ownHand: readonly Card[],
  actionHand: readonly Card[],
) {
  if (phase === 'auction' && ownHand.length === 0) {
    return `Missing private hand for ${controllerSeat}.`
  }
  if (phase === 'play' && ownHand.length === 0) {
    return `Missing private hand for ${controllerSeat}.`
  }
  if (phase === 'play' && actionHand.length === 0) {
    return `Missing playable hand for ${actionSeat}.`
  }
  if (phase !== 'auction' && phase !== 'play') {
    return `No decision is needed during ${phase}.`
  }
  return null
}

function cloneAuction(auction: readonly AuctionEntry[]): AuctionEntry[] {
  return auction.map((entry) => ({
    seat: entry.seat,
    call: { ...entry.call },
  }))
}

function clonePlayedCards(cards: readonly PlayedCard[]): PlayedCard[] {
  return cards.map((played) => ({
    seat: played.seat,
    card: { ...played.card },
  }))
}

function cloneCards(cards: readonly Card[]): Card[] {
  return cards.map((card) => ({ ...card }))
}
