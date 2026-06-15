Spec Files
==========

Implementation-facing specs live in ``docs/specs/``.

``docs/specs/gameplay-web-app.md``
   Requirements for the TanStack Start table, including seat control, practice
   mode, hotseat behavior, auction, play, scoring, and responsive layout.

``docs/specs/limited-information-bot-adapter.md``
   Privacy contract for attaching bot seats to external bridge services and
   physical-card tables.

``docs/specs/cloudflare-deployment.md``
   Deployment contract for the TanStack Start Cloudflare Worker and Python
   Worker backend.

``docs/specs/ai-player-architectures.md``
   Requirements and comparison points for the Python AI player architectures.

``docs/specs/self-play-training.md``
   Deterministic self-play training contract and model artifact format.

When behavior changes, update the relevant spec and the tests named in that
spec's verification section in the same commit.
