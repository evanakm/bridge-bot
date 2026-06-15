# bridge-bot
[![Build Status](https://travis-ci.com/evanakm/bridge-bot.svg?branch=master)](https://travis-ci.com/evanakm/bridge-bot)

Building a robot that can play bridge, and training it using ML

## AI players

The Python bot package includes random, rule-based, rollout-search, and
linear-policy player architectures. The goal is to compare simple AI strategies
without changing the bot user API used by the bridge table.

Useful verification commands:

```bash
pytest bridgebot/test/test_ai_players.py
```

## Integration docs

- `docs/source/ai_players.rst` describes the Python AI player architectures.
- `docs/specs/ai-player-architectures.md` is the implemented AI-player spec.
