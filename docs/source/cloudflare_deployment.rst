Cloudflare deployment
=====================

The project is split into two Cloudflare deployables:

* ``web/``: the TanStack Start table, deployed as a Cloudflare Worker with
  Wrangler.
* ``workers/backend/``: a Python Worker API for server-side bot decisions.

The split keeps the UI runtime and Python AI/runtime experiments independent.
It also reinforces the limited-information boundary: the backend API accepts a
public bot view and rejects complete hidden deal state.

Web Worker
----------

The web app uses ``@cloudflare/vite-plugin`` and ``wrangler``. The Worker config
is ``web/wrangler.jsonc`` and points at the TanStack Start server entrypoint.

Useful commands::

   pnpm --dir web dev
   pnpm --dir web build
   pnpm --dir web cf:dry-run
   pnpm --dir web cf:deploy

Python Worker backend
---------------------

The backend worker is intentionally small for now:

* ``workers/backend/src/entry.py`` adapts Cloudflare's Python Worker request
  object to pure Python request handling.
* ``workers/backend/src/bridgebot_api.py`` implements the testable API contract.
* ``workers/backend/wrangler.jsonc`` enables the ``python_workers``
  compatibility flag.

Useful commands::

   cd workers/backend
   uv run pywrangler dev
   uv run pywrangler deploy

Backend API
-----------

``GET /health``
   Returns the service name and runtime.

``POST /api/bot/action``
   Accepts a limited public bot view and returns a baseline call/play action.

Hidden-state keys such as ``hands``, ``allHands``, ``deal``, or per-seat hand
names are rejected. This is deliberate: integrations with online bridge tables
or physical-card capture should never send the backend more state than the bot
seat is allowed to know.

Verification
------------

Run local verification before changing the Cloudflare setup::

   pytest
   pnpm --dir web test
   pnpm --dir web typecheck
   pnpm --dir web build

See ``docs/specs/cloudflare-deployment.md`` for the deploy contract and
Cloudflare dry-run commands.
