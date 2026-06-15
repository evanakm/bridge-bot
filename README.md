# bridge-bot
[![Build Status](https://travis-ci.com/evanakm/bridge-bot.svg?branch=master)](https://travis-ci.com/evanakm/bridge-bot)

Building a robot that can play bridge, and training it using ML

## Web table

The TanStack Start web app lives in `web/`. It lets 0-4 human players play a
bridge deal with bots filling the remaining seats. Practice mode reveals all
hands in the UI, while bot decision code still receives only the information a
bot seat is allowed to know. The table can also opt in to sharing completed
anonymous boards for training.

```bash
pnpm --dir web install
pnpm --dir web dev
```

Open http://127.0.0.1:3000/ after the dev server starts.

Live Cloudflare app: https://bridge.masonbrothers.ca/

## AI players

The Python bot package includes random, rule-based, rollout-search, and
linear-policy player architectures. The goal is to compare simple AI strategies
without changing the bot user API used by the bridge table.

Useful verification commands:

```bash
pytest
pytest bridgebot/test/test_ai_players.py
pnpm --dir web test
pnpm --dir web e2e
pnpm --dir web typecheck
pnpm --dir web build
```

`pnpm --dir web e2e` starts the local Vite server and runs Playwright browser
checks for the bridge table, mobile layout, move-history scrolling, and social
card/install metadata. On a fresh machine or CI runner, install Chromium first:

```bash
pnpm --dir web exec playwright install chromium
```

Cloudflare web deployment:

```bash
VITE_BRIDGEBOT_API_URL=https://bridgebot-api.<your-account>.workers.dev pnpm --dir web cf:dry-run
VITE_BRIDGEBOT_API_URL=https://bridgebot-api.<your-account>.workers.dev pnpm --dir web cf:deploy
```

## Cloudflare Python Worker backend

The Python Worker backend lives in `workers/backend/`. It exposes a small
limited-information bot API that can later host stronger Python AI policies
without sending hidden hands to the server.

```bash
cd workers/backend
uv run pywrangler dev
uv run pywrangler deploy
```

Local backend contract tests are included in the root pytest suite:

```bash
pytest
```

Create the R2 buckets before deploying game recording:

```bash
pnpm --dir web exec wrangler r2 bucket create bridgebot-training-games
pnpm --dir web exec wrangler r2 bucket create bridgebot-training-games-preview
```

Backend endpoints:

- `GET /health`
- `POST /api/bot/action` for limited-information bot decisions
- `POST /api/training/games` for consented completed-game records

## Privacy and training records

Game sharing is off by default in the web UI. When enabled, the app submits only
completed or passed-out boards. The record includes board context, final hands,
auction, tricks, score, seed, and seat controller types so it can be used for
offline training and evaluation.

The training endpoint rejects personal-data keys such as names, email
addresses, account IDs, session IDs, visitor IDs, IP addresses, user agents,
browser details, and device details. The in-app privacy policy is available at
`/privacy`, with a documentation copy in `docs/source/privacy.rst`.

## Self-play training

The first trainable model is the dependency-light `LinearPolicyBotUser`. It can
iteratively play duplicate boards against the current champion, mutate its bid
and card-play weights, and write a versioned JSON artifact.

```bash
python3 -m bridgebot.training.self_play
```

The default model artifact is
`bridgebot/models/linear_policy_selfplay.json`.

## Integration docs

- `docs/source/web_app.rst` describes the web table, gameplay flow, and current
  limits.
- `docs/source/limited_information_bots.rst` describes how to attach bots to
  external bridge services or physical-card tables without leaking hidden state.
- `docs/source/cloudflare_deployment.rst` describes the Cloudflare web and
  Python Worker deployables.
- `docs/source/privacy.rst` describes what optional training records include and
  exclude.
- `docs/source/ai_players.md` describes the Python AI player architectures.
- `docs/specs/gameplay-web-app.md` is the implemented gameplay spec.
- `docs/specs/limited-information-bot-adapter.md` is the privacy and adapter
  contract for outside tables.
- `docs/specs/cloudflare-deployment.md` is the Cloudflare deployment contract.
- `docs/specs/ai-player-architectures.md` is the implemented AI-player spec.
- `docs/specs/self-play-training.md` is the self-play training spec.
