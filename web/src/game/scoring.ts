import { teamOf } from './cards'
import type { Contract, Doubled, ScoreResult, Vulnerability } from './types'

function isVulnerable(contract: Contract, vulnerability: Vulnerability) {
  const team = teamOf(contract.declarer)
  return vulnerability === 'Both' || vulnerability === team
}

function contractBonus(bidTrickScore: number, vulnerable: boolean) {
  if (bidTrickScore < 100) return 50
  return vulnerable ? 500 : 300
}

function doubledBonus(doubled: Doubled) {
  if (doubled === 'double') return 50
  if (doubled === 'redouble') return 100
  return 0
}

function slamBonus(level: number, vulnerable: boolean) {
  if (level === 6) return vulnerable ? 750 : 500
  if (level === 7) return vulnerable ? 1500 : 1000
  return 0
}

function penalty(down: number, doubled: Doubled, vulnerable: boolean) {
  if (doubled === 'none') return vulnerable ? down * 100 : down * 50
  if (doubled === 'double') {
    if (down === 1) return vulnerable ? 200 : 100
    if (down === 2) return vulnerable ? 500 : 300
    if (down === 3) return vulnerable ? 800 : 500
    return (vulnerable ? 800 : 500) + (down - 3) * 300
  }
  if (down === 1) return vulnerable ? 400 : 200
  if (down === 2) return vulnerable ? 1000 : 600
  if (down === 3) return vulnerable ? 1600 : 1000
  return (vulnerable ? 1600 : 1000) + (down - 3) * 600
}

function madeScore(contract: Contract, madeLevel: number, vulnerable: boolean) {
  const multiplier = contract.doubled === 'redouble' ? 4 : contract.doubled === 'double' ? 2 : 1
  const overtrickValue = contract.doubled === 'redouble'
    ? vulnerable ? 400 : 200
    : contract.doubled === 'double'
      ? vulnerable ? 200 : 100
      : contract.strain === 'C' || contract.strain === 'D'
        ? 20
        : 30
  const basePerTrick = contract.strain === 'C' || contract.strain === 'D' ? 20 : 30
  const noTrumpBonus = contract.strain === 'NT' ? 10 : 0
  const bidTrickScore = (basePerTrick * contract.level + noTrumpBonus) * multiplier
  const overtrickScore = (madeLevel - contract.level) * overtrickValue
  return bidTrickScore + overtrickScore + contractBonus(bidTrickScore, vulnerable) + doubledBonus(contract.doubled) + slamBonus(contract.level, vulnerable)
}

export function scoreContract(contract: Contract, declarerTricks: number, vulnerability: Vulnerability): ScoreResult {
  const vulnerable = isVulnerable(contract, vulnerability)
  const requiredTricks = contract.level + 6
  const result = declarerTricks >= requiredTricks
    ? declarerTricks - 6
    : declarerTricks - requiredTricks
  const declarerScore = result > 0
    ? madeScore(contract, result, vulnerable)
    : -penalty(Math.abs(result), contract.doubled, vulnerable)
  const declarerTeam = teamOf(contract.declarer)
  const nsScore = declarerTeam === 'NS' ? declarerScore : -declarerScore
  const ewScore = -nsScore
  const label = result > 0
    ? `Made ${contract.level}${contract.strain}${result > contract.level ? ` +${result - contract.level}` : ''}`
    : `Down ${Math.abs(result)}`

  return {
    contract,
    tricksTaken: declarerTricks,
    result,
    declarerScore,
    nsScore,
    ewScore,
    label,
  }
}
