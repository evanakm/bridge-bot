import { ranks, seats, suits, type Card, type Hands, type Rank, type Seat, type Suit } from './types'

const rankLabels: Record<Rank, string> = {
  2: '2',
  3: '3',
  4: '4',
  5: '5',
  6: '6',
  7: '7',
  8: '8',
  9: '9',
  10: '10',
  11: 'J',
  12: 'Q',
  13: 'K',
  14: 'A',
}

const suitLabels: Record<Suit, string> = {
  C: '♣',
  D: '♦',
  H: '♥',
  S: '♠',
}

export function makeDeck(): Card[] {
  return suits.flatMap((suit) =>
    ranks.map((rank) => ({
      id: `${suit}${rank}`,
      suit,
      rank,
    })),
  )
}

export function seededRandom(seed: number) {
  let state = seed >>> 0
  return () => {
    state += 0x6D2B79F5
    let value = state
    value = Math.imul(value ^ (value >>> 15), value | 1)
    value ^= value + Math.imul(value ^ (value >>> 7), value | 61)
    return ((value ^ (value >>> 14)) >>> 0) / 4294967296
  }
}

export function shuffleDeck(seed: number): Card[] {
  const random = seededRandom(seed)
  const deck = makeDeck()
  for (let index = deck.length - 1; index > 0; index -= 1) {
    const swapIndex = Math.floor(random() * (index + 1))
    const current = deck[index]!
    deck[index] = deck[swapIndex]!
    deck[swapIndex] = current
  }
  return deck
}

export function deal(seed: number): Hands {
  const deck = shuffleDeck(seed)
  return seats.reduce((hands, seat, seatIndex) => {
    hands[seat] = sortCards(deck.slice(seatIndex * 13, seatIndex * 13 + 13))
    return hands
  }, {} as Hands)
}

export function sortCards(cards: Card[]): Card[] {
  const suitOrder: Record<Suit, number> = { S: 0, H: 1, D: 2, C: 3 }
  return [...cards].sort((left, right) => {
    if (left.suit !== right.suit) {
      return suitOrder[left.suit] - suitOrder[right.suit]
    }
    return right.rank - left.rank
  })
}

export function cardLabel(card: Card) {
  return `${rankLabels[card.rank]}${suitLabels[card.suit]}`
}

export function rankLabel(rank: Rank) {
  return rankLabels[rank]
}

export function suitLabel(suit: Suit) {
  return suitLabels[suit]
}

export function removeCard(cards: Card[], cardId: string) {
  return cards.filter((card) => card.id !== cardId)
}

export function findCard(cards: Card[], cardId: string) {
  return cards.find((card) => card.id === cardId)
}

export function highCardPoints(cards: Card[]) {
  return cards.reduce((total, card) => {
    if (card.rank === 14) return total + 4
    if (card.rank === 13) return total + 3
    if (card.rank === 12) return total + 2
    if (card.rank === 11) return total + 1
    return total
  }, 0)
}

export function longestSuit(cards: Card[]): Suit {
  const counts = suits.map((suit) => ({
    suit,
    count: cards.filter((card) => card.suit === suit).length,
  }))
  return counts.sort((left, right) => right.count - left.count || suits.indexOf(right.suit) - suits.indexOf(left.suit))[0]!.suit
}

export function nextSeat(seat: Seat): Seat {
  return seats[(seats.indexOf(seat) + 1) % seats.length]!
}

export function partner(seat: Seat): Seat {
  return seats[(seats.indexOf(seat) + 2) % seats.length]!
}

export function teamOf(seat: Seat): 'NS' | 'EW' {
  return seat === 'N' || seat === 'S' ? 'NS' : 'EW'
}

export function seatName(seat: Seat) {
  return ({ N: 'North', E: 'East', S: 'South', W: 'West' } satisfies Record<Seat, string>)[seat]
}
