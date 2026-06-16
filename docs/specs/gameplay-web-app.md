# Gameplay Web App Spec

## Status

Implemented in `web/`.

## Goal

Provide a small local web app where users can play bridge against bot seats. The
app should be useful for manual play, practice, and regression-testing bot
behavior.

## Users

- Solo player practicing against three bots.
- Multiple local humans using hotseat play.
- Observer watching an all-bot table.
- Developer validating bridge state transitions and UI behavior.

## Functional Requirements

### Seat Control

- The table has four seats: North, East, South, West.
- Each seat can be toggled between human and bot.
- The app supports any number of human seats from 0 through 4.
- Seats not controlled by humans are controlled by bots.
- Seat changes apply to the current deal immediately.

### Practice Mode

- Practice mode reveals all hands in the UI.
- Turning practice mode off restores normal hand hiding.
- Practice mode must not change the information available to bot decision code.

### Hotseat Mode

- If more than one human seat is enabled and practice mode is off, the next
  human hand is hidden until the user confirms handoff.
- A single human seat does not require handoff.
- Bot turns do not require handoff.

### Auction

- The auction starts with the dealer.
- Legal calls include pass, legal contract bids, double, and redouble.
- Contract bids must outrank the current contract.
- Doubles are allowed only by the opposing partnership after a contract bid.
- Redoubles are allowed only by the declaring partnership after a double.
- Four passes with no bid pass the board out.
- Three passes after a bid end the auction.
- The final contract declarer is the first player from the declaring partnership
  to bid the final strain.

### Play

- Opening lead is made by the player to declarer's left.
- Players must follow suit when possible.
- Trump beats led-suit cards.
- No-trump contracts have no trump suit.
- Declarer controls dummy after dummy is public.
- A deal completes after 13 tricks.

### Board Context and Scoring

- New deals advance duplicate-style board number, dealer, and vulnerability.
- Restart preserves the current board context and redeals the same seed.
- Completed contracts are scored for the declaring partnership and mirrored to
  the defending partnership.

### Training Records

- Game sharing is off by default.
- When enabled, only completed or passed-out boards are submitted.
- Submitted records must include consent metadata and the privacy policy
  version.
- Records may include the full final deal, auction, tricks, score, seed,
  dealer, vulnerability, and seat controller types for offline training.
- Records must not include player names, emails, account IDs, visitor IDs,
  session IDs, IP addresses, user agents, browser details, or device details.

### Responsive UI

- Desktop layout keeps seats, center trick area, and bidding controls in
  reserved regions.
- Mobile layout prioritizes the active human hand and bidding controls.
- Gameplay controls must not overlap hands or table status text.

## Non-Goals

- Network multiplayer.
- User-account persistence or multiplayer saved games.
- Expert bridge bidding or card-play strategy.
- Service-specific bridge platform integration. See
  `limited-information-bot-adapter.md` for the generic integration boundary.

## Verification

Primary tests:

- `web/src/game/auction.test.ts`
- `web/src/game/engine.test.ts`
- `web/src/game/bot.test.ts`
- `web/src/components/BridgeApp.test.tsx`

Commands:

```bash
pnpm --dir web test
pnpm --dir web typecheck
pnpm --dir web build
```

For UI-affecting changes, also inspect the app in a browser at desktop and
mobile widths.
