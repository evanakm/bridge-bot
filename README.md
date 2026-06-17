# bridge-bot
[![Build Status](https://travis-ci.com/evanakm/bridge-bot.svg?branch=master)](https://travis-ci.com/evanakm/bridge-bot)

Building a robot that can play bridge, and training it using ML

## Web table

The TanStack Start web app lives in `web/`. It lets 0-4 human players play a
bridge deal with bots filling the remaining seats. Practice mode reveals all
hands in the UI, while bot decision code still receives only the information a
bot seat is allowed to know.

```bash
pnpm --dir web install
pnpm --dir web dev
```

Open http://127.0.0.1:3000/ after the dev server starts.

Live Cloudflare app: https://bridge.masonbrothers.ca/

Useful verification commands:

```bash
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
pnpm --dir web cf:deploy
pnpm --dir web cf:dry-run
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

## Integration docs

- `docs/source/web_app.rst` describes the web table, gameplay flow, and current
  limits.
- `docs/source/limited_information_bots.rst` describes how to attach bots to
  external bridge services or physical-card tables without leaking hidden state.
- `docs/source/cloudflare_deployment.rst` describes the Cloudflare web and
  Python Worker deployables.
- `docs/specs/gameplay-web-app.md` is the implemented gameplay spec.
- `docs/specs/limited-information-bot-adapter.md` is the privacy and adapter
  contract for outside tables.
- `docs/specs/cloudflare-deployment.md` is the Cloudflare deployment contract.
