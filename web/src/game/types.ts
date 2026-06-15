export const seats = ['N', 'E', 'S', 'W'] as const
export type Seat = (typeof seats)[number]

export const suits = ['C', 'D', 'H', 'S'] as const
export type Suit = (typeof suits)[number]

export const strains = ['C', 'D', 'H', 'S', 'NT'] as const
export type Strain = (typeof strains)[number]

export const ranks = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14] as const
export type Rank = (typeof ranks)[number]

export type Controller = 'human' | 'bot'
export type Vulnerability = 'None' | 'NS' | 'EW' | 'Both'
export type Phase = 'auction' | 'play' | 'passedOut' | 'complete'
export type Doubled = 'none' | 'double' | 'redouble'

export type Card = {
  id: string
  suit: Suit
  rank: Rank
}

export type ContractCall = {
  kind: 'contract'
  level: number
  strain: Strain
}

export type NonContractCall = {
  kind: 'pass' | 'double' | 'redouble'
}

export type Call = ContractCall | NonContractCall

export type AuctionEntry = {
  seat: Seat
  call: Call
}

export type Contract = {
  level: number
  strain: Strain
  declarer: Seat
  bidder: Seat
  doubled: Doubled
}

export type PlayedCard = {
  seat: Seat
  card: Card
}

export type Trick = {
  leader: Seat
  cards: PlayedCard[]
  winner: Seat
}

export type SeatConfig = Record<Seat, Controller>
export type Hands = Record<Seat, Card[]>

export type GameState = {
  phase: Phase
  seats: SeatConfig
  practice: boolean
  seed: number
  dealer: Seat
  vulnerability: Vulnerability
  hands: Hands
  auction: AuctionEntry[]
  contract: Contract | null
  turn: Seat
  leader: Seat | null
  currentTrick: PlayedCard[]
  completedTricks: Trick[]
  tricksWon: Record<'NS' | 'EW', number>
  score: ScoreResult | null
}

export type ScoreResult = {
  contract: Contract
  tricksTaken: number
  result: number
  declarerScore: number
  nsScore: number
  ewScore: number
  label: string
}

export type NewGameOptions = {
  seats: SeatConfig
  practice: boolean
  seed: number
  dealer?: Seat
  vulnerability?: Vulnerability
}
