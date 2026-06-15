# Limited-Information Bot Adapter Spec

## Status

Implemented by `web/src/game/bot.ts`.

## Goal

Allow bot seats to be attached to external bridge services and physical-card
tables without giving the bot hidden information it would not have at a real
table.

## Threat Model

The process may know more than a player should know, especially when:

- a local game contains all four hands;
- practice mode reveals all cards in the UI;
- one process controls multiple bot seats;
- an external bridge service payload includes full deal state;
- a physical-card adapter has camera or operator data for multiple seats.

Bot strategy code must receive only the information allowed for the active
controller seat.

## Adapter Input

External adapters call `nextExternalBotAction(observation)`.

`observation` must include:

- `source`: `bridge-service` or `physical-table`;
- `botSeats`: 0-4 seats controlled by this bot instance;
- public table state: `phase`, `dealer`, `vulnerability`, `auction`,
  `contract`, `turn`, `leader`, `currentTrick`, `completedTricks`,
  `tricksWon`, and optional `score`;
- `privateHands`: private hands known for controlled seats;
- `publicHands`: public hands, primarily dummy after dummy is visible.

Adapters must not pass full local `GameState` to service strategy code.

## Decision Output

`nextExternalBotAction` returns:

- `wait`: no controlled bot seat is active, required private information is
  missing, or the phase needs no action;
- `call`: auction action for the active seat;
- `play`: card-play action for the active seat.

Returned actions include both `controllerSeat` and `seat`. These differ when
declarer is controlling dummy.

## Privacy Contract

- The active decision view contains the active controller hand.
- Opponent hands are never present.
- Partner hand is absent unless partner is dummy and dummy is public.
- If one process controls multiple seats, non-active controlled hands are absent
  from the active decision view.
- Practice mode does not widen the bot decision view.
- Missing private hand data returns `wait`.
- Physical-table adapters should omit unconfirmed card data.

## Dummy Rules

- Dummy is not public before the opening lead is made.
- After at least one card has been played to the first trick, dummy may be
  included in `publicHands`.
- If the active action seat is dummy, `controllerSeat` is declarer and
  `seat` is dummy.

## Service Adapter Requirements

A service-specific adapter should:

1. Parse service events into `ExternalBotObservation`.
2. Drop hidden data before calling `nextExternalBotAction`.
3. Convert `BotDecision` back into the service's action format.
4. Treat `wait` as a non-action, not an error.
5. Keep service protocol details outside `web/src/game/bot.ts`.

## Physical-Card Adapter Requirements

A physical-card adapter should:

1. Build observations from camera, sensor, operator, or table-device events.
2. Pass only confirmed cards and public facts.
3. Surface `wait` when the bot needs more observed information.
4. Apply returned actions outside the engine, for example by displaying a
   suggestion or controlling an actuator.

## Verification

`web/src/game/bot.test.ts` must cover:

- no hidden hands in local practice bot views;
- 0 controlled bot seats return `wait`;
- 1-4 controlled bot seats sanitize to the active seat;
- missing private active hand returns `wait`;
- physical-table observations hide partner and opponent hands;
- dummy is exposed only after dummy is public.

Run:

```bash
pnpm --dir web test
pnpm --dir web typecheck
pnpm --dir web build
```
