# AI Player Architecture Spec

## Status

Implemented in `bridgebot/bots/aiplayers.py`.

## Goal

Provide several bridge bot architectures so we can compare behavior before
committing to a single ML strategy. The implementations should be deterministic,
testable, and dependency-light.

## Constraints

- Bots must implement the existing `bridgebot.game.interface.User` interface.
- Existing bots with only `bid(current_player, legal_bids, bid_history)` must
  continue to work.
- Serious bidding needs hand context, so new bots may additionally implement
  `bid_with_hand(current_player, hand, legal_bids, bid_history)`.
- No new ML/runtime dependencies are required for these first architectures.
- Card play must choose only from `legal_cards`.
- Policies should not require hidden opponent hands.

## Architectures

### RuleBasedBotUser

Purpose: interpretable baseline.

Behavior:

- Passes weak hands.
- Opens 1NT with balanced 15-count hands.
- Opens the longest suit with opening values.
- Doubles or redoubles with stronger values when legal.
- During play, wins with the lowest sufficient card, ducks when partner is
  winning, and leads from the longest suit.

### RandomBotUser

Purpose: legal-action lower-bound baseline.

Behavior:

- Chooses uniformly from legal bids and legal cards.
- Sorts legal choices before sampling, so seeded runs are reproducible.
- Ignores hidden hands and never chooses outside the legal action set.

### LinearPolicyBotUser

Purpose: simple ML-shaped policy without a training dependency.

Behavior:

- Scores each legal bid using high-card points, suit length, major-suit bonus,
  balanced no-trump bonus, level cost, and double/redouble features.
- Scores each legal card using rank, immediate trick-winning status, trump,
  partner-winning status, and honor-conservation features.
- Accepts custom weight dictionaries for tuning or offline training.
- Can be trained by `bridgebot.training.self_play`.

### RolloutBotUser

Purpose: lightweight search-style card-play architecture.

Behavior:

- Uses the rule-based bidding policy.
- For non-terminal trick positions, samples possible trick completions from
  unseen cards and estimates each legal card's chance to win the trick.
- For fourth hand, plays the lowest card that wins when possible.
- Uses deterministic seeds for repeatable tests and comparisons.

### EnsembleBotUser

Purpose: combine weak policies while we learn which signals matter.

Behavior:

- Runs multiple bot policies.
- Chooses bids/cards by majority vote with deterministic tie-breaking.
- Defaults to rule-based, linear-policy, and rollout members.

## Hand-Aware Bidding Adapter

Use `choose_bid_for_user(user, current_player, hand, legal_bids, bid_history)`.

- If `user` implements `bid_with_hand`, that method is used.
- Otherwise it falls back to the original `bid` method.

This preserves compatibility while allowing new AI players to use the hand for
bidding.

## Verification

Tests live in `bridgebot/test/test_ai_players.py`.

Required coverage:

- feature extraction for HCP and balanced hands;
- rule-based 1NT opening;
- rule-based longest-suit opening;
- linear policy returns a legal non-pass action with strong hands;
- hand-aware adapter fallback;
- rule-based trick tactics;
- random legal-action baseline determinism;
- rollout fourth-hand behavior;
- every architecture returns legal bids and cards;
- rollout bot operates without hidden opponent hands.

Run:

```bash
pytest
```

## Self-Play Training

Training details live in `docs/specs/self-play-training.md`.

Current implemented training target:

- `LinearPolicyBotUser` bid and card weights.

Current training method:

- deterministic duplicate self-play;
- candidate-vs-champion evolutionary mutation;
- standard IMP compression for duplicate score swings;
- validation guard against the initial baseline;
- benchmark reporting against untrained linear, random, rule-based, and
  rollout baselines;
- partnership benchmark reporting for trained+random, trained+trained, and
  random+random team compositions;
- JSON model artifact at `bridgebot/models/linear_policy_selfplay.json`.
