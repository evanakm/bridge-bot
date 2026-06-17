import hashlib
import json
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlparse


PRIVACY_POLICY_VERSION = "2026-06-16"
TRAINING_RECORD_SCHEMA = "bridgebot.training_game.v1"
MAX_TRAINING_GAME_BYTES = 128_000

FORBIDDEN_STATE_KEYS = {
    "all_hands",
    "allHands",
    "deal",
    "hands",
    "hiddenCards",
    "northHand",
    "eastHand",
    "southHand",
    "westHand",
}

FORBIDDEN_PERSONAL_KEYS = {
    "account",
    "accountId",
    "browser",
    "device",
    "email",
    "ip",
    "ipAddress",
    "name",
    "playerId",
    "playerName",
    "rawRequest",
    "session",
    "sessionId",
    "user",
    "userAgent",
    "username",
    "visitor",
    "visitorId",
}

PUBLIC_VIEW_KEYS = {
    "auction",
    "contract",
    "currentTrick",
    "dummy",
    "dummyHand",
    "hand",
    "legalCalls",
    "legalCards",
    "phase",
    "seat",
    "tricksWon",
    "vulnerability",
}


@dataclass(frozen=True)
class ApiResponse:
    status: int
    headers: dict[str, str]
    body: str


@dataclass(frozen=True)
class PreparedTrainingRecord:
    record_id: str
    storage_key: str
    body: str
    payload: dict[str, Any]


def handle_request(method: str, url: str, body: str | None = None) -> ApiResponse:
    path = urlparse(url).path
    normalized_method = method.upper()

    if normalized_method == "OPTIONS":
        return _json_response({}, status=204)

    if normalized_method == "GET" and path == "/health":
        return _json_response({
            "ok": True,
            "service": "bridgebot-api",
            "runtime": "cloudflare-python-worker",
        })

    if normalized_method == "POST" and path == "/api/bot/action":
        return _bot_action(body)

    if normalized_method == "POST" and path == "/api/training/games":
        record = prepare_training_game_record(body)
        if isinstance(record, ApiResponse):
            return record
        return training_game_response(record)

    return _json_response({"error": "not_found"}, status=404)


def prepare_training_game_record(body: str | None) -> PreparedTrainingRecord | ApiResponse:
    if body is not None and len(body.encode("utf-8")) > MAX_TRAINING_GAME_BYTES:
        return _json_response({
            "error": "training_game_too_large",
            "maxBytes": MAX_TRAINING_GAME_BYTES,
        }, status=413)

    payload = _load_json_object(body)
    if isinstance(payload, ApiResponse):
        return payload

    personal_key = _first_forbidden_key(payload, forbidden_keys=FORBIDDEN_PERSONAL_KEYS)
    if personal_key is not None:
        return _json_response({
            "error": "personal_data_rejected",
            "message": f"Payload includes personal-data key: {personal_key}",
        }, status=400)

    if payload.get("schema") != TRAINING_RECORD_SCHEMA:
        return _json_response({
            "error": "invalid_training_schema",
            "message": f"schema must be {TRAINING_RECORD_SCHEMA}",
        }, status=422)

    consent = payload.get("consent")
    if not isinstance(consent, dict) or consent.get("shareForTraining") is not True:
        return _json_response({
            "error": "training_consent_required",
            "message": "shareForTraining consent must be true before storing a game.",
        }, status=422)

    game = payload.get("game")
    if not isinstance(game, dict):
        return _json_response({"error": "invalid_training_game"}, status=422)

    if game.get("phase") not in {"complete", "passedOut"}:
        return _json_response({
            "error": "unfinished_training_game",
            "message": "Only completed or passed-out games may be recorded for training.",
        }, status=422)

    required_game_keys = {
        "auction",
        "boardNumber",
        "dealer",
        "hands",
        "phase",
        "seed",
        "seats",
        "tricksWon",
        "vulnerability",
    }
    missing_game_keys = sorted(required_game_keys - set(game))
    if missing_game_keys:
        return _json_response({
            "error": "training_game_missing_keys",
            "keys": missing_game_keys,
        }, status=422)

    normalized = {
        "schema": TRAINING_RECORD_SCHEMA,
        "source": payload.get("source", "bridgebot-web"),
        "policyVersion": PRIVACY_POLICY_VERSION,
        "consent": {
            "shareForTraining": True,
            "privacyPolicyVersion": consent.get("privacyPolicyVersion", PRIVACY_POLICY_VERSION),
        },
        "game": game,
    }

    if "recordedAt" in payload:
        normalized["recordedAt"] = payload["recordedAt"]

    record_body = json.dumps(normalized, sort_keys=True, separators=(",", ":"))
    record_id = hashlib.sha256(record_body.encode("utf-8")).hexdigest()[:24]
    return PreparedTrainingRecord(
        record_id=record_id,
        storage_key=f"training-games/v1/{record_id}.json",
        body=record_body,
        payload=normalized,
    )


def training_game_response(record: PreparedTrainingRecord, storage: str = "not_configured") -> ApiResponse:
    return _json_response({
        "ok": True,
        "recordId": record.record_id,
        "storage": storage,
        "policyVersion": PRIVACY_POLICY_VERSION,
    }, status=202)


def _bot_action(body: str | None) -> ApiResponse:
    payload = _load_json_object(body)
    if isinstance(payload, ApiResponse):
        return payload

    leak_path = _first_forbidden_key(payload, forbidden_keys=FORBIDDEN_STATE_KEYS)
    if leak_path is not None:
        return _json_response({
            "error": "hidden_state_rejected",
            "message": f"Payload includes forbidden hidden-state key: {leak_path}",
        }, status=400)

    unknown_keys = sorted(set(payload) - PUBLIC_VIEW_KEYS)
    if unknown_keys:
        return _json_response({
            "error": "unknown_view_keys",
            "keys": unknown_keys,
        }, status=400)

    phase = payload.get("phase")
    if phase == "auction":
        return _auction_action(payload)
    if phase == "play":
        return _play_action(payload)

    return _json_response({
        "error": "invalid_phase",
        "message": "phase must be either 'auction' or 'play'",
    }, status=422)


def _auction_action(payload: dict[str, Any]) -> ApiResponse:
    legal_calls = payload.get("legalCalls")
    if not isinstance(legal_calls, list) or len(legal_calls) == 0:
        return _json_response({
            "error": "invalid_legal_calls",
            "message": "auction decisions require a non-empty legalCalls list",
        }, status=422)

    call = next((candidate for candidate in legal_calls if _call_kind(candidate) == "pass"), legal_calls[0])
    return _json_response({
        "action": {
            "kind": "call",
            "call": call,
        },
        "legalMoves": {
            "calls": legal_calls,
        },
        "policy": "safe-baseline",
        "view": _view_summary(payload),
    })


def _play_action(payload: dict[str, Any]) -> ApiResponse:
    legal_cards = payload.get("legalCards")
    if not isinstance(legal_cards, list) or len(legal_cards) == 0:
        return _json_response({
            "error": "invalid_legal_cards",
            "message": "play decisions require a non-empty legalCards list",
        }, status=422)

    card = min(legal_cards, key=_card_sort_key)
    card_id = card.get("id") if isinstance(card, dict) else card
    return _json_response({
        "action": {
            "kind": "play",
            "cardId": card_id,
        },
        "legalMoves": {
            "cards": legal_cards,
        },
        "policy": "safe-baseline",
        "view": _view_summary(payload),
    })


def _load_json_object(body: str | None) -> dict[str, Any] | ApiResponse:
    if body is None or body.strip() == "":
        return _json_response({"error": "missing_json_body"}, status=400)
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return _json_response({"error": "invalid_json"}, status=400)
    if not isinstance(payload, dict):
        return _json_response({"error": "invalid_json_object"}, status=400)
    return payload


def _first_forbidden_key(value: Any, prefix: str = "", forbidden_keys: set[str] | None = None) -> str | None:
    forbidden = forbidden_keys or FORBIDDEN_STATE_KEYS
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            if key in forbidden:
                return path
            nested = _first_forbidden_key(child, path, forbidden)
            if nested is not None:
                return nested
    elif isinstance(value, list):
        for index, child in enumerate(value):
            nested = _first_forbidden_key(child, f"{prefix}[{index}]", forbidden)
            if nested is not None:
                return nested
    return None


def _call_kind(call: Any) -> str | None:
    if isinstance(call, dict):
        return call.get("kind")
    if isinstance(call, str):
        return call.lower()
    return None


def _card_sort_key(card: Any) -> tuple[int, str]:
    if not isinstance(card, dict):
        return (0, str(card))
    rank = card.get("rank")
    numeric_rank = rank if isinstance(rank, int) else 0
    return (numeric_rank, str(card.get("id", "")))


def _view_summary(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "phase": payload.get("phase"),
        "seat": payload.get("seat"),
    }


def _json_response(payload: dict[str, Any], status: int = 200) -> ApiResponse:
    return ApiResponse(
        status=status,
        headers={
            "Access-Control-Allow-Headers": "content-type",
            "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
            "Access-Control-Allow-Origin": "*",
            "Content-Type": "application/json",
        },
        body=json.dumps(payload, separators=(",", ":")),
    )
