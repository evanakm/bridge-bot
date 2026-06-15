import { Bot, Eye, EyeOff, RotateCcw, StepForward, UserRound } from 'lucide-react'
import { useEffect, useMemo, useRef, useState } from 'react'

import { callLabel, contractCalls, isCallLegal } from '../game/auction'
import { cardLabel, seatName, sortCards, suitLabel } from '../game/cards'
import {
  activeControllerSeat,
  advanceBotOnce,
  allLegalCalls,
  applyCall,
  createGame,
  dealerForBoard,
  defaultSeats,
  isCardLegal,
  isHumanTurn,
  handStrengthLabel,
  needsHotseatReady,
  playCard,
  vulnerabilityForBoard,
  visibleSeatCards,
} from '../game/engine'
import type { Call, Card, GameState, Seat, SeatConfig } from '../game/types'

const compassSeats: Seat[] = ['N', 'E', 'S', 'W']
const BOT_DELAY_MS = 420

function nextSeed() {
  return Math.floor(Date.now() % 1_000_000)
}

export function BridgeApp() {
  const [seatConfig, setSeatConfig] = useState<SeatConfig>(defaultSeats)
  const [practice, setPractice] = useState(false)
  const [seed, setSeed] = useState(20260615)
  const [boardIndex, setBoardIndex] = useState(0)
  const [readySeat, setReadySeat] = useState<Seat | null>(null)
  const [thinkingSeat, setThinkingSeat] = useState<Seat | null>(null)
  const [game, setGame] = useState(() => createGame({
    seats: defaultSeats,
    practice: false,
    seed: 20260615,
    dealer: dealerForBoard(0),
    vulnerability: vulnerabilityForBoard(0),
  }))

  const humans = useMemo(() => compassSeats.filter((seat) => seatConfig[seat] === 'human'), [seatConfig])
  const handoffSeat = needsHotseatReady(game, readySeat)
  const humanTurn = isHumanTurn(game) && !handoffSeat

  useEffect(() => {
    if (game.phase === 'complete' || game.phase === 'passedOut' || isHumanTurn(game)) {
      setThinkingSeat(null)
      return
    }
    setThinkingSeat(game.turn)
    const timer = window.setTimeout(() => {
      setGame((current) => advanceBotOnce(current))
      setThinkingSeat(null)
    }, BOT_DELAY_MS)
    return () => window.clearTimeout(timer)
  }, [game])

  useEffect(() => {
    if (humans.length <= 1 || practice) {
      setReadySeat(null)
    }
  }, [humans.length, practice, game.turn])

  function startDeal(next = seed, nextBoardIndex = boardIndex) {
    setSeed(next)
    setBoardIndex(nextBoardIndex)
    setReadySeat(null)
    setThinkingSeat(null)
    setGame(createGame({
      seats: seatConfig,
      practice,
      seed: next,
      dealer: dealerForBoard(nextBoardIndex),
      vulnerability: vulnerabilityForBoard(nextBoardIndex),
    }))
  }

  function toggleSeat(seat: Seat) {
    const nextConfig: SeatConfig = {
      ...seatConfig,
      [seat]: seatConfig[seat] === 'human' ? 'bot' : 'human',
    }
    setSeatConfig(nextConfig)
    setReadySeat(null)
    setThinkingSeat(null)
    setGame((current) => ({
      ...current,
      seats: nextConfig,
    }))
  }

  function setPracticeMode(enabled: boolean) {
    setPractice(enabled)
    setGame((current) => ({
      ...current,
      practice: enabled,
    }))
  }

  function makeCall(call: Call) {
    setGame((current) => applyCall(current, call))
    setReadySeat(null)
  }

  function play(seat: Seat, card: Card) {
    setGame((current) => playCard(current, seat, card.id))
    setReadySeat(null)
  }

  return (
    <main className="bridge-app">
      <section className="table-shell" aria-label="Bridge table">
        <ControlRail
          game={game}
          humans={humans.length}
          practice={practice}
          boardNumber={boardIndex + 1}
          onPractice={setPracticeMode}
          onNewDeal={() => startDeal(nextSeed(), boardIndex + 1)}
          onStep={() => setGame((current) => advanceBotOnce(current))}
        />

        <section className="setup-strip" aria-label="Seat setup">
          <div>
            <span className="eyebrow">Take a seat</span>
            <strong>{humans.length === 0 ? 'Watch mode' : humans.length === 1 ? 'Solo table' : `${humans.length}-seat hotseat`}</strong>
          </div>
          <div className="seat-toggles" role="group" aria-label="Human seats">
            {compassSeats.map((seat) => (
              <button
                key={seat}
                className={`seat-toggle ${seatConfig[seat] === 'human' ? 'active' : ''}`}
                type="button"
                onClick={() => toggleSeat(seat)}
                aria-pressed={seatConfig[seat] === 'human'}
              >
                {seatConfig[seat] === 'human' ? <UserRound aria-hidden="true" /> : <Bot aria-hidden="true" />}
                {seatName(seat)}
              </button>
            ))}
          </div>
          <button className="primary-action" type="button" onClick={() => startDeal(seed, boardIndex)}>
            <RotateCcw aria-hidden="true" />
            Restart deal
          </button>
        </section>

        <div className={`felt-grid phase-${game.phase}`}>
          {compassSeats.map((seat) => (
            <SeatPanel
              key={seat}
              seat={seat}
              game={game}
              visible={visibleSeatCards(game, seat, readySeat)}
              thinking={thinkingSeat === seat}
              canAct={humanTurn && game.turn === seat}
              onPlay={play}
            />
          ))}

          <CenterTable game={game} />

          {game.phase === 'auction' && (
            <BiddingBox
              game={game}
              disabled={!humanTurn}
              onCall={makeCall}
            />
          )}
        </div>

        {handoffSeat && (
          <div className="handoff" role="dialog" aria-label={`Pass to ${seatName(handoffSeat)}`}>
            <div>
              <span className="eyebrow">Hotseat</span>
              <h2>Pass to {seatName(handoffSeat)}</h2>
              <p>Hidden hands stay covered until the next player is ready.</p>
            </div>
            <button type="button" className="primary-action" onClick={() => setReadySeat(handoffSeat)}>
              <Eye aria-hidden="true" />
              Show {seatName(handoffSeat)} hand
            </button>
          </div>
        )}
      </section>
    </main>
  )
}

function ControlRail({
  game,
  humans,
  practice,
  boardNumber,
  onPractice,
  onNewDeal,
  onStep,
}: {
  game: GameState
  humans: number
  practice: boolean
  boardNumber: number
  onPractice: (enabled: boolean) => void
  onNewDeal: () => void
  onStep: () => void
}) {
  return (
    <aside className="control-rail" aria-label="Table controls">
      <div>
        <span className="eyebrow">Bridge Bot</span>
        <h1>Table</h1>
      </div>
      <button className={`icon-button ${practice ? 'active' : ''}`} type="button" onClick={() => onPractice(!practice)}>
        {practice ? <Eye aria-hidden="true" /> : <EyeOff aria-hidden="true" />}
        <span>Practice</span>
      </button>
      <button className="icon-button" type="button" onClick={onStep} disabled={isHumanTurn(game) || game.phase === 'complete' || game.phase === 'passedOut'}>
        <StepForward aria-hidden="true" />
        <span>Step</span>
      </button>
      <button className="icon-button" type="button" onClick={onNewDeal}>
        <RotateCcw aria-hidden="true" />
        <span>New</span>
      </button>
      <div className="rail-status">
        <span>Board {boardNumber}</span>
        <span>{humans} human{humans === 1 ? '' : 's'}</span>
        <span>{automationStatus(game)}</span>
        <strong>{game.phase}</strong>
      </div>
      <MoveHistory game={game} />
    </aside>
  )
}

function automationStatus(game: GameState) {
  if (game.phase === 'complete') return 'Board complete'
  if (game.phase === 'passedOut') return 'Board passed out'
  if (isHumanTurn(game)) return `Waiting for ${seatName(activeControllerSeat(game))}`
  return `${seatName(game.turn)} bot thinking`
}

type HistoryItem = {
  id: string
  label: string
  title: string
  detail: string
  tone: 'call' | 'play' | 'trick' | 'result'
}

function moveHistory(game: GameState): HistoryItem[] {
  const history: HistoryItem[] = game.auction.map((entry, index) => ({
    id: `auction-${index}`,
    label: `Bid ${index + 1}`,
    title: `${seatName(entry.seat)} ${callLabel(entry.call)}`,
    detail: `${controllerLabel(game, entry.seat)} call`,
    tone: 'call',
  }))

  game.completedTricks.forEach((trick, trickIndex) => {
    trick.cards.forEach((played, cardIndex) => {
      history.push({
        id: `trick-${trickIndex}-card-${cardIndex}`,
        label: `Trick ${trickIndex + 1}`,
        title: `${seatName(played.seat)} ${cardLabel(played.card)}`,
        detail: `${controllerLabel(game, played.seat)} play`,
        tone: 'play',
      })
    })
    history.push({
      id: `trick-${trickIndex}-winner`,
      label: `Trick ${trickIndex + 1}`,
      title: `${seatName(trick.winner)} wins`,
      detail: `Led by ${seatName(trick.leader)}`,
      tone: 'trick',
    })
  })

  game.currentTrick.forEach((played, index) => {
    history.push({
      id: `current-trick-card-${index}`,
      label: `Trick ${game.completedTricks.length + 1}`,
      title: `${seatName(played.seat)} ${cardLabel(played.card)}`,
      detail: `${controllerLabel(game, played.seat)} play`,
      tone: 'play',
    })
  })

  if (game.phase === 'passedOut') {
    history.push({
      id: 'result-passed-out',
      label: 'Result',
      title: 'Board passed out',
      detail: 'No contract',
      tone: 'result',
    })
  }

  if (game.score) {
    history.push({
      id: 'result-score',
      label: 'Result',
      title: game.score.label,
      detail: `NS ${game.score.nsScore > 0 ? '+' : ''}${game.score.nsScore}`,
      tone: 'result',
    })
  }

  return history
}

function controllerLabel(game: GameState, seat: Seat) {
  return game.seats[seat] === 'human' ? 'Human' : 'Bot'
}

function MoveHistory({ game }: { game: GameState }) {
  const history = moveHistory(game)
  const latest = history.at(-1)
  const endRef = useRef<HTMLLIElement | null>(null)

  useEffect(() => {
    endRef.current?.scrollIntoView?.({ block: 'end' })
  }, [history.length])

  return (
    <section className="move-history" aria-label="Move history">
      <header>
        <div>
          <span className="eyebrow">History</span>
          <strong>Moves</strong>
        </div>
        <span>{history.length}</span>
      </header>
      {latest && (
        <div className={`latest-move history-${latest.tone}`} aria-label="Latest move">
          <span>Last move</span>
          <strong>{latest.title}</strong>
          <small>{latest.detail}</small>
        </div>
      )}
      {history.length === 0 ? (
        <p className="history-empty">Waiting for the first call.</p>
      ) : (
        <ol>
          {history.map((item) => (
            <li key={item.id} className={`history-item history-${item.tone}`}>
              <span>{item.label}</span>
              <strong>{item.title}</strong>
              <small>{item.detail}</small>
            </li>
          ))}
          <li className="history-end" ref={endRef} aria-hidden="true" />
        </ol>
      )}
    </section>
  )
}

function SeatPanel({
  seat,
  game,
  visible,
  thinking,
  canAct,
  onPlay,
}: {
  seat: Seat
  game: GameState
  visible: boolean
  thinking: boolean
  canAct: boolean
  onPlay: (seat: Seat, card: Card) => void
}) {
  const hand = game.hands[seat]
  const isTurn = game.turn === seat
  const turnBadge = game.phase === 'auction' ? 'to bid' : game.phase === 'play' ? 'to play' : null

  return (
    <section className={`seat-panel seat-${seat} ${isTurn ? 'turn' : ''} ${visible ? 'visible' : 'hidden'}`} aria-label={`${seatName(seat)} seat`}>
      <header>
        <div>
          <span className="seat-code">{seat}</span>
          <strong>{seatName(seat)}</strong>
        </div>
        <span className={`controller ${game.seats[seat]}`}>{game.seats[seat]}</span>
      </header>
      <div className="seat-meta">
        <span>{visible ? handStrengthLabel(hand) : `${hand.length} cards`}</span>
        {isTurn && turnBadge && <span className="turn-badge">{turnBadge}</span>}
        {thinking && <span className="thinking">thinking</span>}
        {game.contract && seat === partnerOfContract(game) && game.completedTricks.length + game.currentTrick.length > 0 && <span>dummy</span>}
      </div>
      <div className="hand" aria-label={`${seatName(seat)} hand`}>
        {visible
          ? sortCards(hand).map((card) => (
            <button
              key={card.id}
              className={`playing-card suit-${card.suit} ${canAct && isCardLegal(game, seat, card.id) ? 'legal' : ''}`}
              type="button"
              disabled={!canAct || !isCardLegal(game, seat, card.id)}
              onClick={() => onPlay(seat, card)}
              aria-label={`Play ${cardLabel(card)}`}
            >
              <span>{cardLabel(card)}</span>
            </button>
          ))
          : Array.from({ length: Math.min(hand.length, 13) }).map((_, index) => (
            <span key={index} className="card-back" aria-hidden="true" />
          ))}
      </div>
    </section>
  )
}

function partnerOfContract(game: GameState) {
  if (!game.contract) return null
  return ({ N: 'S', E: 'W', S: 'N', W: 'E' } as Record<Seat, Seat>)[game.contract.declarer]
}

function CenterTable({ game }: { game: GameState }) {
  const contract = game.contract
  return (
    <section className="center-table" aria-label="Current deal">
      <div className="contract-panel">
        <div className="turn-panel" aria-live="polite">
          <span className={`phase-pill phase-${game.phase}`}>{phaseLabel(game.phase)}</span>
          <strong>{turnSummary(game)}</strong>
          <span>{turnDetail(game)}</span>
        </div>
        <span className="eyebrow">Contract</span>
        <div className="deal-info">
          <span>Dealer {seatName(game.dealer)}</span>
          <span>Vul {game.vulnerability}</span>
        </div>
        {contract ? (
          <strong>{contract.level}{contract.strain} by {seatName(contract.declarer)} {contract.doubled !== 'none' ? contract.doubled : ''}</strong>
        ) : game.phase === 'passedOut' ? (
          <strong>Passed out</strong>
        ) : (
          <strong>Auction open</strong>
        )}
      </div>
      <div className="trick-zone">
        {game.currentTrick.length === 0 && <span className="empty-trick">Current trick</span>}
        {game.currentTrick.map((played) => (
          <div key={`${played.seat}-${played.card.id}`} className={`trick-card trick-${played.seat} suit-${played.card.suit}`}>
            <small>{played.seat}</small>
            <strong>{cardLabel(played.card)}</strong>
          </div>
        ))}
      </div>
      <div className="score-row">
        <span>NS {game.tricksWon.NS}</span>
        <span>EW {game.tricksWon.EW}</span>
      </div>
      {game.score && (
        <div className="result-panel">
          <strong>{game.score.label}</strong>
          <span>NS {game.score.nsScore > 0 ? '+' : ''}{game.score.nsScore}</span>
        </div>
      )}
      <AuctionRecord game={game} />
    </section>
  )
}

function phaseLabel(phase: GameState['phase']) {
  if (phase === 'passedOut') return 'Passed out'
  if (phase === 'complete') return 'Complete'
  return phase === 'auction' ? 'Auction' : 'Play'
}

function turnSummary(game: GameState) {
  if (game.phase === 'passedOut') return 'Board passed out'
  if (game.phase === 'complete') return game.score?.label ?? 'Board complete'
  if (game.phase === 'auction') return `${seatName(game.turn)} to bid`
  const controller = activeControllerSeat(game)
  if (controller !== game.turn) {
    return `${seatName(controller)} controls ${seatName(game.turn)}`
  }
  return `${seatName(game.turn)} to play`
}

function turnDetail(game: GameState) {
  if (game.phase === 'complete') {
    return game.score ? `NS ${game.score.nsScore > 0 ? '+' : ''}${game.score.nsScore}` : 'Score settled'
  }
  if (game.phase === 'passedOut') return 'No contract'
  const controller = activeControllerSeat(game)
  return game.seats[controller] === 'human' ? 'Human action' : 'Bot action'
}

function AuctionRecord({ game }: { game: GameState }) {
  return (
    <div className="auction-record" aria-label="Auction record">
      {compassSeats.map((seat) => <strong key={seat}>{seat}</strong>)}
      {game.auction.map((entry, index) => (
        <span key={`${entry.seat}-${index}`} className={`auction-call seat-call-${entry.seat}`}>
          {callLabel(entry.call)}
        </span>
      ))}
    </div>
  )
}

function BiddingBox({ game, disabled, onCall }: { game: GameState; disabled: boolean; onCall: (call: Call) => void }) {
  const legal = allLegalCalls(game)
  const actionCalls: Call[] = [{ kind: 'pass' }, { kind: 'double' }, { kind: 'redouble' }]
  return (
    <section className="bidding-box" aria-label="Bidding box">
      <header className="bid-header">
        <div>
          <span className="eyebrow">Bidding</span>
          <strong>{seatName(game.turn)}</strong>
        </div>
        <span>{disabled ? 'Waiting' : 'Your call'}</span>
      </header>
      <div className="bid-grid">
        {contractCalls().map((call) => (
          <button
            key={`${call.level}-${call.strain}`}
            type="button"
            disabled={disabled || !isCallLegal(game.auction, game.turn, call)}
            onClick={() => onCall(call)}
          >
            {call.level}{call.strain === 'NT' ? 'NT' : suitLabel(call.strain)}
          </button>
        ))}
      </div>
      <div className="bid-actions">
        {actionCalls.map((call) => (
          <button
            key={call.kind}
            type="button"
            disabled={disabled || !legal.some((legalCall) => callLabel(legalCall) === callLabel(call))}
            onClick={() => onCall(call)}
          >
            {callLabel(call)}
          </button>
        ))}
      </div>
    </section>
  )
}
