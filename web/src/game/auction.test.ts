import { describe, expect, it } from 'vitest'

import {
  callLabel,
  deriveContract,
  doubledStatusAfterHighestBid,
  isAuctionComplete,
  isCallLegal,
  legalCalls,
  nextAuctionSeat,
} from './auction'
import type { AuctionEntry, Call } from './types'

const pass: Call = { kind: 'pass' }
const double: Call = { kind: 'double' }
const redouble: Call = { kind: 'redouble' }
const oneClub: Call = { kind: 'contract', level: 1, strain: 'C' }
const oneHeart: Call = { kind: 'contract', level: 1, strain: 'H' }
const twoClub: Call = { kind: 'contract', level: 2, strain: 'C' }
const fourHeart: Call = { kind: 'contract', level: 4, strain: 'H' }

describe('auction rules', () => {
  it('allows only higher contract bids over the current contract', () => {
    const auction: AuctionEntry[] = [{ seat: 'N', call: oneHeart }]

    expect(isCallLegal(auction, 'E', oneClub)).toBe(false)
    expect(isCallLegal(auction, 'E', twoClub)).toBe(true)
  })

  it('allows opponents to double and the declaring side to redouble', () => {
    const doubledAuction: AuctionEntry[] = [
      { seat: 'N', call: oneHeart },
      { seat: 'E', call: double },
    ]

    expect(isCallLegal([{ seat: 'N', call: oneHeart }], 'E', double)).toBe(true)
    expect(isCallLegal([{ seat: 'N', call: oneHeart }], 'S', double)).toBe(false)
    expect(isCallLegal(doubledAuction, 'S', redouble)).toBe(true)
    expect(isCallLegal(doubledAuction, 'W', redouble)).toBe(false)
  })

  it('rotates clockwise from the dealer and passes out after four passes', () => {
    const auction: AuctionEntry[] = [
      { seat: 'E', call: pass },
      { seat: 'S', call: pass },
      { seat: 'W', call: pass },
      { seat: 'N', call: pass },
    ]

    expect(nextAuctionSeat('E', [])).toBe('E')
    expect(nextAuctionSeat('E', auction.slice(0, 1))).toBe('S')
    expect(nextAuctionSeat('E', auction.slice(0, 2))).toBe('W')
    expect(nextAuctionSeat('E', auction.slice(0, 3))).toBe('N')
    expect(isAuctionComplete(auction)).toBe(true)
    expect(deriveContract(auction)).toBeNull()
  })

  it('allows a balancing double after two passes by the opening side', () => {
    const auction: AuctionEntry[] = [
      { seat: 'N', call: oneHeart },
      { seat: 'E', call: pass },
      { seat: 'S', call: pass },
    ]
    const doubledAuction: AuctionEntry[] = [
      ...auction,
      { seat: 'W', call: double },
      { seat: 'N', call: pass },
      { seat: 'E', call: pass },
      { seat: 'S', call: pass },
    ]

    expect(isCallLegal(auction, 'W', double)).toBe(true)
    expect(isCallLegal(auction, 'N', double)).toBe(false)
    expect(isAuctionComplete(doubledAuction)).toBe(true)
    expect(deriveContract(doubledAuction)).toMatchObject({
      level: 1,
      strain: 'H',
      bidder: 'N',
      declarer: 'N',
      doubled: 'double',
    })
  })

  it('resets double and redouble state when a higher contract is bid', () => {
    const auction: AuctionEntry[] = [
      { seat: 'N', call: oneHeart },
      { seat: 'E', call: double },
      { seat: 'S', call: redouble },
      { seat: 'W', call: twoClub },
    ]
    const finalAuction: AuctionEntry[] = [
      ...auction,
      { seat: 'N', call: pass },
      { seat: 'E', call: pass },
      { seat: 'S', call: pass },
    ]

    expect(doubledStatusAfterHighestBid(auction)).toBe('none')
    expect(isCallLegal(auction, 'N', double)).toBe(true)
    expect(isCallLegal(auction, 'E', redouble)).toBe(false)
    expect(isAuctionComplete(finalAuction)).toBe(true)
    expect(deriveContract(finalAuction)).toMatchObject({
      level: 2,
      strain: 'C',
      bidder: 'W',
      declarer: 'W',
      doubled: 'none',
    })
  })

  it('derives declarer as first partnership player to bid the final strain', () => {
    const auction: AuctionEntry[] = [
      { seat: 'N', call: oneHeart },
      { seat: 'E', call: pass },
      { seat: 'S', call: fourHeart },
      { seat: 'W', call: pass },
      { seat: 'N', call: pass },
      { seat: 'E', call: pass },
    ]

    expect(isAuctionComplete(auction)).toBe(true)
    expect(deriveContract(auction)).toMatchObject({
      level: 4,
      strain: 'H',
      bidder: 'S',
      declarer: 'N',
      doubled: 'none',
    })
  })

  it('lists pass, double, and redouble with readable labels', () => {
    const calls = legalCalls([{ seat: 'N', call: oneClub }], 'E')

    expect(calls.map(callLabel)).toContain('Pass')
    expect(calls.map(callLabel)).toContain('Double')
    expect(callLabel({ kind: 'redouble' })).toBe('Redouble')
  })
})
