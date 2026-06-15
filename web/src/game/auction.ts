import { longestSuit, nextSeat, partner, teamOf } from './cards'
import { strains, type AuctionEntry, type Call, type Card, type Contract, type ContractCall, type Doubled, type Seat, type Strain } from './types'

export function callLabel(call: Call): string {
  if (call.kind === 'pass') return 'Pass'
  if (call.kind === 'double') return 'Double'
  if (call.kind === 'redouble') return 'Redouble'
  if (call.kind === 'contract') return `${call.level}${call.strain}`
  return ''
}

export function contractCalls(): ContractCall[] {
  const calls: ContractCall[] = []
  for (let level = 1; level <= 7; level += 1) {
    for (const strain of strains) {
      calls.push({ kind: 'contract', level, strain })
    }
  }
  return calls
}

export function compareContracts(left: ContractCall, right: ContractCall) {
  if (left.level !== right.level) return left.level - right.level
  return strains.indexOf(left.strain) - strains.indexOf(right.strain)
}

export function highestContract(auction: AuctionEntry[]) {
  const entries = auction.filter((entry): entry is AuctionEntry & { call: ContractCall } => entry.call.kind === 'contract')
  if (entries.length === 0) return null
  return entries.reduce((highest, entry) => compareContracts(entry.call, highest.call) > 0 ? entry : highest)
}

export function currentContractBid(auction: AuctionEntry[]) {
  return highestContract(auction)
}

export function doubledStatusAfterHighestBid(auction: AuctionEntry[]): Doubled {
  const highest = highestContract(auction)
  if (!highest) return 'none'
  const highestIndex = auction.indexOf(highest)
  const laterCalls = auction.slice(highestIndex + 1)
  if (laterCalls.some((entry) => entry.call.kind === 'redouble')) return 'redouble'
  if (laterCalls.some((entry) => entry.call.kind === 'double')) return 'double'
  return 'none'
}

export function isCallLegal(auction: AuctionEntry[], seat: Seat, call: Call) {
  if (call.kind === 'pass') return true
  const currentBid = currentContractBid(auction)
  if (call.kind === 'contract') {
    return currentBid === null || compareContracts(call, currentBid.call) > 0
  }
  if (!currentBid) return false
  const doubled = doubledStatusAfterHighestBid(auction)
  if (call.kind === 'double') {
    return doubled === 'none' && teamOf(seat) !== teamOf(currentBid.seat)
  }
  return doubled === 'double' && teamOf(seat) === teamOf(currentBid.seat)
}

export function legalCalls(auction: AuctionEntry[], seat: Seat): Call[] {
  return [
    ...contractCalls(),
    { kind: 'pass' } as Call,
    { kind: 'double' } as Call,
    { kind: 'redouble' } as Call,
  ].filter((call) => isCallLegal(auction, seat, call))
}

export function isPassout(auction: AuctionEntry[]) {
  return auction.length === 4 && auction.every((entry) => entry.call.kind === 'pass')
}

export function isAuctionComplete(auction: AuctionEntry[]) {
  if (isPassout(auction)) return true
  if (auction.length < 4 || !highestContract(auction)) return false
  return auction.slice(-3).every((entry) => entry.call.kind === 'pass')
}

export function deriveContract(auction: AuctionEntry[]): Contract | null {
  const highest = highestContract(auction)
  if (!highest) return null
  const strain = highest.call.strain
  const contractTeam = teamOf(highest.seat)
  const partnership = [highest.seat, partner(highest.seat)]
  const declarer = auction.find((entry) =>
    partnership.includes(entry.seat) &&
    entry.call.kind === 'contract' &&
    entry.call.strain === strain &&
    teamOf(entry.seat) === contractTeam,
  )?.seat
  if (!declarer) return null
  return {
    level: highest.call.level,
    strain,
    bidder: highest.seat,
    declarer,
    doubled: doubledStatusAfterHighestBid(auction),
  }
}

export function nextAuctionSeat(dealer: Seat, auction: AuctionEntry[]): Seat {
  let seat = dealer
  for (let index = 0; index < auction.length; index += 1) {
    seat = nextSeat(seat)
  }
  return seat
}

export function chooseBotCall(auction: AuctionEntry[], seat: Seat, hand: Card[]): Call {
  const legal = legalCalls(auction, seat)
  const currentBid = currentContractBid(auction)
  if (!currentBid) {
    const points = hand.reduce((total, card) => {
      if (card.rank === 14) return total + 4
      if (card.rank === 13) return total + 3
      if (card.rank === 12) return total + 2
      if (card.rank === 11) return total + 1
      return total
    }, 0)
    if (points >= 12) {
      const strain = longestSuit(hand) as Strain
      return legal.find((call) => call.kind === 'contract' && call.level === 1 && call.strain === strain) ?? { kind: 'pass' }
    }
  }
  return { kind: 'pass' }
}
