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

Useful verification commands:

```bash
pnpm --dir web test
pnpm --dir web typecheck
pnpm --dir web build
```

## Integration docs

- `docs/source/web_app.rst` describes the web table, gameplay flow, and current
  limits.
- `docs/source/limited_information_bots.rst` describes how to attach bots to
  external bridge services or physical-card tables without leaking hidden state.
- `docs/specs/gameplay-web-app.md` is the implemented gameplay spec.
- `docs/specs/limited-information-bot-adapter.md` is the privacy and adapter
  contract for outside tables.
