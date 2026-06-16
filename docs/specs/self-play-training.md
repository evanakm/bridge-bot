# Self-Play Training Spec

## Goal

Train dependency-light bridge bot policies by having candidate models play
duplicate boards against the current champion. Training should produce a
versioned JSON artifact that can be loaded by the Python bot code, plus a
sidecar weight-history file for comparing model snapshots over time.

## Scope

Implemented trainer:

- `bridgebot.training.self_play.train_linear_policy`
- `bridgebot.training.self_play.load_linear_policy_model`
- CLI entrypoint: `python3 -m bridgebot.training.self_play`

The first trained architecture is `LinearPolicyBotUser`, because its bid and
card-play weights are already explicit constructor arguments. Rule-based and
rollout players remain comparison baselines rather than directly trained
models.

The primary baseline is the untrained default `LinearPolicyBotUser`. It uses the
same architecture as the trained policy, but with the hand-written default
weights from `bridgebot/bots/aiplayers.py`.

## Training Loop

For each generation:

1. Treat the current champion weights as the opponent.
2. Generate a population of candidate weights by combining fixed exploratory
   candidates with seeded Gaussian mutations.
3. Evaluate each candidate on deterministic duplicate boards.
4. Seat the candidate as North/South and then East/West on the same board seeds.
5. Score the candidate by converting
   `candidate_as_NS_score - candidate_as_EW_score` through the standard IMP
   table.
6. Accept the best positive candidate as the new champion.
7. Validate the champion against the initial baseline and revert if validation
   drops below zero.
8. Save the best final-validation candidate from the initial baseline, the last
   champion, and the best held-out validation champion seen during training.
9. Benchmark the saved policy against the untrained linear policy, random legal
   play, rule-based play, and a light rollout policy.
10. Benchmark partnership compositions so mixed teams can be compared directly:
    trained+random vs random+random, random+trained vs random+random, the
    averaged mixed orientation, trained+trained vs random+random,
    trained+trained vs both mixed orientations, random+random vs random+random,
    and trained+trained vs trained+trained.
11. Optionally include a mixed training objective. When
    `mixed_training_boards_per_generation` is non-zero, candidates are selected
    by averaging self-play against the current champion with smaller-board
    evaluations against random, rule-based, and rollout partnerships.
12. Benchmark model combinations beyond random pairs by comparing trained pairs
    and averaged trained+baseline mixed pairs against initial-linear, random,
    rule-based, and rollout baselines.

This is evolutionary self-play, not gradient training. It is intentionally small
and deterministic so it can run in CI and on developer machines without heavy ML
dependencies.

## Artifact Format

The model artifact is JSON:

```json
{
  "schema_version": 1,
  "architecture": "LinearPolicyBotUser",
  "bid_weights": {},
  "card_weights": {},
  "training": {
    "algorithm": "evolutionary_self_play",
    "result": {
      "baseline_scores": {},
      "pair_scores": {},
      "combo_scores": {}
    }
  }
}
```

The default output path is:

```text
bridgebot/models/linear_policy_selfplay.json
```

The trainer also writes a sidecar history file:

```text
bridgebot/models/linear_policy_selfplay_history.json
```

The history file stores comparable snapshots of bid weights, card weights,
training config, single-policy baseline scores, pair-composition scores, and
summary validation metrics. Identical deterministic snapshots are deduplicated
by a stable `snapshot_id`.

## Privacy

Training uses the existing `User` bot API. `LinearPolicyBotUser` sees its own
hand, legal calls/cards, dummy when available, and public trick history. It does
not receive full opponent hands.

## Commands

Small local run:

```bash
python3 -m venv .venv
.venv/bin/python -m bridgebot.training.self_play --generations 2 --population 3 --boards 3 --validation-boards 4
```

Default training run:

```bash
.venv/bin/python -m bridgebot.training.self_play
```

Longer mixed-opponent run:

```bash
.venv/bin/python -m bridgebot.training.self_play \
  --generations 12 \
  --population 10 \
  --boards 16 \
  --validation-boards 24 \
  --benchmark-boards 64 \
  --mixed-training-boards 4 \
  --rollout-trials 8
```

## Verification

Run:

```bash
pytest
```

Required test coverage:

- seeded deals are deterministic and contain all 52 cards;
- identical linear policies score zero in duplicate play;
- trained linear policies can be scored against arbitrary bot baselines;
- score deltas use standard IMP cutoffs;
- real board play returns a scored bridge result;
- self-play writes a loadable JSON artifact;
- self-play writes a sidecar weight-history artifact for comparing model
  snapshots over time;
- identical deterministic training snapshots are deduplicated in history;
- self-play artifacts include baseline scores for untrained linear, random,
  rule-based, and rollout players;
- self-play artifacts include pair-composition scores for trained+random,
  random+trained, trained+trained, and random+random partnerships;
- mixed-orientation partnership scores aggregate both trained+random and
  random+trained orderings;
- self-play artifacts include combo scores for trained models paired with
  initial-linear, random, rule-based, and rollout baselines;
- optional mixed training objectives include random, rule-based, and rollout
  partnership pressure;
- identical partnership compositions score zero under duplicate seat-flipped
  comparison;
- the training guard preserves or improves validation score versus the initial
  baseline for deterministic test seeds;
- the saved artifact uses the best validated champion rather than a later
  accepted candidate with weaker held-out validation.
