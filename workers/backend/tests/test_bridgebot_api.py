import json

from bridgebot_api import TRAINING_RECORD_SCHEMA, handle_request


def response_json(response):
    return json.loads(response.body)


def test_health_endpoint_reports_cloudflare_worker_runtime():
    response = handle_request("GET", "https://bridgebot-api.example/health")

    assert response.status == 200
    assert response.headers["Content-Type"] == "application/json"
    assert response_json(response) == {
        "ok": True,
        "service": "bridgebot-api",
        "runtime": "cloudflare-python-worker",
    }


def test_auction_action_uses_limited_view_and_prefers_pass():
    response = handle_request(
        "POST",
        "https://bridgebot-api.example/api/bot/action",
        json.dumps({
            "phase": "auction",
            "seat": "N",
            "hand": [{"id": "AS", "suit": "S", "rank": 14}],
            "auction": [],
            "legalCalls": [
                {"kind": "contract", "level": 1, "strain": "S"},
                {"kind": "pass"},
            ],
        }),
    )

    body = response_json(response)

    assert response.status == 200
    assert body["action"] == {"kind": "call", "call": {"kind": "pass"}}
    assert body["legalMoves"] == {
        "calls": [
            {"kind": "contract", "level": 1, "strain": "S"},
            {"kind": "pass"},
        ],
    }
    assert body["view"] == {"phase": "auction", "seat": "N"}
    assert "hand" not in body


def test_play_action_selects_lowest_legal_card_without_echoing_hand():
    response = handle_request(
        "POST",
        "https://bridgebot-api.example/api/bot/action",
        json.dumps({
            "phase": "play",
            "seat": "W",
            "hand": [{"id": "AS", "suit": "S", "rank": 14}],
            "currentTrick": [{"seat": "N", "card": {"id": "2C", "suit": "C", "rank": 2}}],
            "legalCards": [
                {"id": "AS", "suit": "S", "rank": 14},
                {"id": "3C", "suit": "C", "rank": 3},
            ],
        }),
    )

    body = response_json(response)

    assert response.status == 200
    assert body["action"] == {"kind": "play", "cardId": "3C"}
    assert body["legalMoves"] == {
        "cards": [
            {"id": "AS", "suit": "S", "rank": 14},
            {"id": "3C", "suit": "C", "rank": 3},
        ],
    }
    assert body["view"] == {"phase": "play", "seat": "W"}
    assert "hand" not in body


def test_bot_action_rejects_hidden_state_payloads():
    response = handle_request(
        "POST",
        "https://bridgebot-api.example/api/bot/action",
        json.dumps({
            "phase": "auction",
            "seat": "E",
            "legalCalls": [{"kind": "pass"}],
            "hands": {
                "N": [{"id": "AS", "suit": "S", "rank": 14}],
                "E": [{"id": "2C", "suit": "C", "rank": 2}],
            },
        }),
    )

    body = response_json(response)

    assert response.status == 400
    assert body["error"] == "hidden_state_rejected"
    assert "hands" in body["message"]


def test_bot_action_rejects_unknown_view_keys():
    response = handle_request(
        "POST",
        "https://bridgebot-api.example/api/bot/action",
        json.dumps({
            "phase": "auction",
            "seat": "S",
            "legalCalls": [{"kind": "pass"}],
            "opponentModel": "too much information",
        }),
    )

    body = response_json(response)

    assert response.status == 400
    assert body == {"error": "unknown_view_keys", "keys": ["opponentModel"]}


def test_training_game_record_accepts_completed_anonymous_game():
    response = handle_request(
        "POST",
        "https://bridgebot-api.example/api/training/games",
        json.dumps(training_game_payload()),
    )

    body = response_json(response)

    assert response.status == 202
    assert body["ok"] is True
    assert len(body["recordId"]) == 24
    assert body["storage"] == "not_configured"
    assert body["policyVersion"] == "2026-06-16"


def test_training_game_record_requires_explicit_consent():
    payload = training_game_payload()
    payload["consent"]["shareForTraining"] = False

    response = handle_request(
        "POST",
        "https://bridgebot-api.example/api/training/games",
        json.dumps(payload),
    )

    body = response_json(response)

    assert response.status == 422
    assert body["error"] == "training_consent_required"


def test_training_game_record_rejects_unfinished_games():
    payload = training_game_payload()
    payload["game"]["phase"] = "play"

    response = handle_request(
        "POST",
        "https://bridgebot-api.example/api/training/games",
        json.dumps(payload),
    )

    body = response_json(response)

    assert response.status == 422
    assert body["error"] == "unfinished_training_game"


def test_training_game_record_rejects_personal_data_keys():
    payload = training_game_payload()
    payload["game"]["playerName"] = "North Player"

    response = handle_request(
        "POST",
        "https://bridgebot-api.example/api/training/games",
        json.dumps(payload),
    )

    body = response_json(response)

    assert response.status == 400
    assert body["error"] == "personal_data_rejected"
    assert "playerName" in body["message"]


def training_game_payload():
    return {
        "schema": TRAINING_RECORD_SCHEMA,
        "source": "bridgebot-web",
        "recordedAt": "2026-06-16T00:00:00.000Z",
        "consent": {
            "shareForTraining": True,
            "privacyPolicyVersion": "2026-06-16",
        },
        "game": {
            "boardNumber": 1,
            "seed": 20260615,
            "dealer": "N",
            "vulnerability": "None",
            "phase": "passedOut",
            "seats": {"N": "bot", "E": "bot", "S": "human", "W": "bot"},
            "hands": {
                "N": [{"id": "AS", "suit": "S", "rank": 14}],
                "E": [{"id": "2C", "suit": "C", "rank": 2}],
                "S": [{"id": "3D", "suit": "D", "rank": 3}],
                "W": [{"id": "4H", "suit": "H", "rank": 4}],
            },
            "auction": [
                {"seat": "N", "call": {"kind": "pass"}},
                {"seat": "E", "call": {"kind": "pass"}},
                {"seat": "S", "call": {"kind": "pass"}},
                {"seat": "W", "call": {"kind": "pass"}},
            ],
            "contract": None,
            "currentTrick": [],
            "completedTricks": [],
            "tricksWon": {"NS": 0, "EW": 0},
            "score": None,
        },
    }
