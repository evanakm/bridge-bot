# Self-Play Training Spec

## Goal

Train dependency-light bridge bot policies by having candidate models play
duplicate boards against the current champion. Training should produce a
versioned JSON artifact that can be loaded by the Python bot code.

## Scope

Implemented trainer:

- `bridgebot.training.self_play.train_linear_policy`
- `bridgebot.training.self_play.load_linear_policy_model`
- CLI entrypoint: `python3 -m bridgebot.training.self_play`

The first trained architecture is `LinearPolicyBotUser`, because its bid and
card-play weights are already explicit constructor arguments. Rule-based and
rollout players remain comparison baselines rather than directly trained
models.

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
    "result": {}
  }
}
```

The default output path is:

```text
bridgebot/models/linear_policy_selfplay.json
```

## Privacy

Training uses the existing `User` bot API. `LinearPolicyBotUser` sees its own
hand, legal calls/cards, dummy when available, and public trick history. It does
not receive full opponent hands.

## Commands

Small local run:

```bash
python3 -m bridgebot.training.self_play --generations 2 --population 3 --boards 3 --validation-boards 4
```

Default training run:

```bash
python3 -m bridgebot.training.self_play
```

## Verification

Run:

```bash
pytest
```

Required test coverage:

- seeded deals are deterministic and contain all 52 cards;
- identical linear policies score zero in duplicate play;
- score deltas use standard IMP cutoffs;
- real board play returns a scored bridge result;
- self-play writes a loadable JSON artifact;
- the training guard preserves or improves validation score versus the initial
  baseline for deterministic test seeds.
