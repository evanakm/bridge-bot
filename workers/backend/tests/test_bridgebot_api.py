import json

from bridgebot_api import handle_request


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
