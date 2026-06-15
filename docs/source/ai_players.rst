AI Players
==========

The Python package now includes several dependency-light AI player
architectures in ``bridgebot/bots/aiplayers.py``. They all implement the existing
``User`` interface and can be used by the legacy Python game runner.

Architectures
-------------

``RuleBasedBotUser``
   A transparent baseline. It opens 1NT with balanced 15-count hands, opens the
   longest suit with opening values, doubles with stronger hands, and uses simple
   trick tactics during card play.

``LinearPolicyBotUser``
   A feature-weighted policy. It scores legal bids and legal cards using hand
   features, strain/level features, immediate trick-winning features, and
   honor-conservation features. The weights are constructor arguments, so this
   can be tuned or trained later without changing the public bot API.

``RolloutBotUser``
   A lightweight search-style player. Bidding delegates to the rule-based
   baseline, while card play samples possible completions of the current trick
   from unseen cards and chooses the card with the best estimated chance to win
   the trick.

``EnsembleBotUser``
   A voting wrapper over multiple bot architectures. It is useful when comparing
   weak signals from different policies before a stronger model is available.

Hand-Aware Bidding
------------------

The original ``User.bid`` interface receives only ``current_player``,
``legal_bids``, and ``bid_history``. That is not enough for serious bidding. The
new AI bots therefore support ``bid_with_hand``. The helper
``choose_bid_for_user`` calls ``bid_with_hand`` when available and falls back to
the original ``bid`` method for older bots.

The demo runner in ``bridgebot/main.py`` now uses ``choose_bid_for_user``.

Usage
-----

.. code-block:: python

   from bridgebot.bots.aiplayers import EnsembleBotUser, RuleBasedBotUser
   from bridgebot.game.enums import Players

   users = {
       Players.NORTH: RuleBasedBotUser(),
       Players.EAST: EnsembleBotUser(),
       Players.SOUTH: RuleBasedBotUser(),
       Players.WEST: EnsembleBotUser(),
   }

Verification
------------

The AI players are covered by ``bridgebot/test/test_ai_players.py``. The tests
check feature extraction, opening bids, legal bid/card output, hand-aware
bidding fallback, immediate trick tactics, rollout behavior, and operation
without hidden opponent hands.

Run:

.. code-block:: bash

   pytest
