# Specs

These files describe the implemented web bridge table and the integration
contracts that should remain stable as the project grows.

- `gameplay-web-app.md`: playable TanStack Start table requirements, including
  consented completed-game records for training.
- `limited-information-bot-adapter.md`: privacy-preserving adapter contract for
  external bridge services and physical-card tables.
- `cloudflare-deployment.md`: Cloudflare Worker deployment contract for the web
  app and Python backend worker.
- `ai-player-architectures.md`: implemented Python AI player architectures and
  verification expectations.
- `self-play-training.md`: deterministic self-play training contract and model
  artifact format.

Specs are written to be testable. When changing behavior, update the relevant
spec and the tests named in its verification section in the same commit.
