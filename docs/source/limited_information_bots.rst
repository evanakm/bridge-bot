Limited-Information Bots
========================

Bots that play on outside bridge services or physical-card tables must not
receive a complete deal state. They should see only public table facts, their
own private hand, and dummy after dummy is public.

The boundary for this is ``web/src/game/bot.ts``.

Core Contract
-------------

External integrations submit an ``ExternalBotObservation`` to
``nextExternalBotAction``. The observation identifies:

* the source, either ``bridge-service`` or ``physical-table``;
* which seats this bot instance controls, from 0-4 seats;
* public table state: phase, dealer, vulnerability, auction, contract, turn,
  leader, current trick, completed tricks, trick counts, and optional score;
* private hands known to the integration for controlled seats;
* public hands, currently used for dummy once dummy is visible.

``nextExternalBotAction`` returns one of:

* ``wait`` when no controlled bot seat is to act, when the hand is missing, or
  when the phase requires no action;
* ``call`` during the auction;
* ``play`` during card play.

Example
-------

.. code-block:: typescript

   import { nextExternalBotAction } from './game/bot'

   const action = nextExternalBotAction({
     source: 'bridge-service',
     botSeats: ['N', 'S'],
     phase: 'auction',
     dealer: 'N',
     vulnerability: 'None',
     auction: [],
     contract: null,
     turn: 'N',
     leader: null,
     currentTrick: [],
     completedTricks: [],
     tricksWon: { NS: 0, EW: 0 },
     privateHands: {
       N: northHand,
     },
   })

   if (action.kind === 'call') {
     // Send action.call to the service for action.seat.
   }

Privacy Rules
-------------

The bot view is intentionally smaller than ``GameState``:

* A seat never receives opponent hands.
* A seat never receives partner hand except when partner is dummy and dummy is
  public.
* Practice mode is a UI reveal only. It must not widen bot decision views.
* If one process controls multiple bot seats, only the active controller seat's
  hand is placed in the current decision view.
* Missing private information results in ``wait`` instead of guessing from
  hidden state.

Physical-Card Tables
--------------------

For real-world cards, an adapter should build observations from camera,
manual-entry, or table-device events. The adapter should pass only confirmed
observations into ``nextExternalBotAction``. If a card or hand is not known, omit
it and allow the bot to return ``wait``.

The adapter is responsible for applying a returned action to the physical
system, for example by displaying the suggested call/card to a human operator or
by driving a robot actuator. The game engine does not assume authority over
real cards.

Service Adapters
----------------

A service-specific adapter should map the service protocol into
``ExternalBotObservation`` and map ``BotDecision`` back to the service action
format. Keep protocol parsing outside ``web/src/game/bot.ts`` so the privacy
boundary stays stable and testable.

Regression Tests
----------------

The leakage contract is covered in ``web/src/game/bot.test.ts``:

* local practice mode does not expose other hands to bot views;
* four co-located controlled seats do not share private hands;
* zero controlled seats waits;
* missing private hands wait;
* physical-table observations hide partner and opponent hands;
* dummy is available only after dummy is public.
