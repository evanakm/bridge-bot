Privacy Policy
==============

Effective June 16, 2026.

Bridge Bot runs a local bridge table in the browser and can optionally share
completed game records for bot training.

Game Recording
--------------

Game sharing is off by default. If a player turns on Share games, the web app
sends completed or passed-out boards to the backend. The backend accepts only
records that include explicit training consent metadata.

Data Stored
-----------

Training records may include:

* board number, seed, dealer, vulnerability, and final phase;
* seat controller types;
* final hands, auction, contract, tricks, trick counts, and score;
* the privacy policy version attached to the consented record.

Training records do not include:

* names, email addresses, account IDs, session IDs, or visitor IDs;
* IP addresses, user agents, browser details, or device details;
* chat messages or profile text, because the table has no chat or profile
  fields.

Use
---

Shared games may be used to compare bot policies, train future bridge models,
test scoring and bidding behavior, and improve gameplay quality. Records are
anonymous table data, not user profiles.

Control
-------

Players can turn off Share games at any time to stop sending future boards.
Boards already accepted by the backend may remain in the training dataset.
