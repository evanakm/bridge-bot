# Cloudflare Deployment Spec

## Goals

- Deploy the TanStack Start table as a Cloudflare Worker.
- Keep backend bot decision code in a separate Python Worker so the Python AI
  player work can evolve without coupling it to the web runtime.
- Preserve the limited-information contract for external bridge services and
  physical-card integrations.

## Web Worker

The web app lives in `web/` and deploys with Wrangler.

- `web/vite.config.ts` must include `@cloudflare/vite-plugin` before
  `tanstackStart()`.
- `web/wrangler.jsonc` must use `@tanstack/react-start/server-entry` as `main`.
- `compatibility_flags` must include `nodejs_compat` for TanStack Start SSR.
- The compatibility date should be updated intentionally, with a normal test and
  build pass, not as unrelated churn.

Commands:

```bash
pnpm --dir web dev
pnpm --dir web build
pnpm --dir web cf:dry-run
pnpm --dir web cf:deploy
```

## Python Worker Backend

The backend worker lives in `workers/backend/` and deploys with pywrangler.

- `workers/backend/wrangler.jsonc` must include the `python_workers`
  compatibility flag while Python Workers remain in beta.
- `workers/backend/src/entry.py` is the Cloudflare SDK entrypoint.
- `workers/backend/src/bridgebot_api.py` contains the pure-Python request logic
  that local tests import directly.

Commands:

```bash
cd workers/backend
uv run pywrangler dev
uv run pywrangler deploy
```

## API Contract

`GET /health` returns service health.

`POST /api/bot/action` accepts only a limited public bot view:

- `phase`
- `seat`
- `hand`
- `auction`
- `legalCalls`
- `contract`
- `currentTrick`
- `dummy`
- `dummyHand`
- `legalCards`
- `tricksWon`
- `vulnerability`

The response must not echo `hand` or any complete deal state. Hidden-state keys
such as `hands`, `allHands`, `deal`, and per-seat hand names must be rejected.
Successful responses include `legalMoves.calls` during the auction or
`legalMoves.cards` during play so clients can render only legal choices.

## Verification

Required before changing this setup:

```bash
pytest
pnpm --dir web test
pnpm --dir web typecheck
pnpm --dir web build
```

Cloudflare deploy verification, when credentials are available:

```bash
pnpm --dir web cf:dry-run
cd workers/backend && uv run pywrangler deploy --dry-run
```
