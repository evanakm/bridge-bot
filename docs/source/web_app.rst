Web Table
=========

The web table is a small TanStack Start app in ``web/``. It provides a playable
single-table bridge experience for local use and for exercising the bot engine.

Run it with:

.. code-block:: bash

   pnpm --dir web install
   pnpm --dir web dev

Then open ``http://127.0.0.1:3000/``.

Gameplay Scope
--------------

The app supports:

* 0-4 human seats.
* Bot control for every non-human seat.
* Hotseat handoff when multiple human seats are enabled and practice mode is
  off.
* Practice mode, which reveals all cards in the UI.
* Duplicate-style board progression for dealer and vulnerability.
* Legal auction calls, passout detection, double/redouble legality, contract
  derivation, declarer and dummy assignment.
* Legal play, including follow-suit enforcement, trump trick winners, trick
  counts, and rubber-independent duplicate-style scoring for the deal.

The current bot strategy is intentionally simple. It is suitable for integration
plumbing and gameplay validation, not expert bidding or expert card play.

Primary Files
-------------

``web/src/components/BridgeApp.tsx``
   React UI for the table, controls, hands, auction box, hotseat handoff, and
   score display.

``web/src/game/engine.ts``
   State transitions for local deals: create deal, apply calls, play cards,
   advance local bots, and score completed contracts.

``web/src/game/auction.ts``
   Auction legality and contract derivation.

``web/src/game/bot.ts``
   Limited-information bot decision boundary used by local bots and external
   table adapters.

``web/src/game/*.test.ts`` and ``web/src/components/*.test.tsx``
   Regression tests for gameplay rules, UI behavior, and hidden-state privacy.

Verification
------------

Use these commands before changing gameplay behavior:

.. code-block:: bash

   pnpm --dir web test
   pnpm --dir web typecheck
   pnpm --dir web build

When changing layout or table interaction, also inspect the app in a browser at
desktop and mobile viewport sizes. The table has fixed gameplay regions so
hands, bidding controls, and the center trick area should not overlap.

Known Limits
------------

* Bot bidding and card play are heuristic.
* There is no persistence or multiplayer network transport.
* External service adapters are not service-specific yet; they should be built
  on top of the limited-information observation contract described in
  :doc:`limited_information_bots`.
