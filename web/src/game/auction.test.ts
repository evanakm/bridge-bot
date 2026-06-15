import { describe, expect, it } from 'vitest'

import { callLabel, deriveContract, isAuctionComplete, isCallLegal, legalCalls } from './auction'
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
