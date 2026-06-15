import argparse
import contextlib
import copy
import io
import json
import random
from dataclasses import asdict, dataclass
from pathlib import Path

from bridgebot import bidding
from bridgebot.bots.aiplayers import LinearPolicyBotUser, choose_bid_for_user
from bridgebot.game import cardplay
from bridgebot.game.bridgehand import BridgeHand
from bridgebot.game.deck import Deck
from bridgebot.game.enums import AuctionStatus, Players, Team, Vulnerabilities
from bridgebot.game.scoring import get_score_from_result


DEFAULT_MODEL_PATH = Path("bridgebot/models/linear_policy_selfplay.json")
MODEL_SCHEMA_VERSION = 1

BID_WEIGHT_RANGES = {
    "points": (0.0, 2.5),
    "length": (0.0, 3.0),
    "major": (-1.0, 2.0),
    "balanced_nt": (-1.0, 3.0),
    "level_cost": (-6.0, -0.1),
    "pass_floor": (6.0, 18.0),
    "double_points": (0.0, 1.8),
}

CARD_WEIGHT_RANGES = {
    "rank": (-0.8, 1.2),
    "wins_now": (0.0, 8.0),
    "partner_winning": (-8.0, 1.0),
    "trump": (-1.0, 4.0),
    "conserve_honor": (-1.5, 1.0),
}

IMP_CUTOFFS = [
    (20, 1),
    (50, 2),
    (90, 3),
    (130, 4),
    (170, 5),
    (220, 6),
    (270, 7),
    (320, 8),
    (370, 9),
    (430, 10),
    (500, 11),
    (600, 12),
    (750, 13),
    (900, 14),
    (1100, 15),
    (1300, 16),
    (1500, 17),
    (1750, 18),
    (2000, 19),
    (2250, 20),
    (2500, 21),
    (3000, 22),
    (3500, 23),
    (4000, 24),
]


@dataclass(frozen=True)
class BoardScore:
    ns_score: int
    passed_out: bool
    contract: str
    declarer: str | None


@dataclass(frozen=True)
class MatchScore:
    average_delta: float
    total_delta: int
    boards: int
    passouts: int


@dataclass(frozen=True)
class TrainingConfig:
    seed: int = 20260615
    generations: int = 6
    population: int = 8
    boards_per_generation: int = 10
    validation_boards: int = 12
    mutation_scale: float = 0.45


@dataclass(frozen=True)
class TrainingResult:
    model_path: str
    config: dict
    bid_weights: dict[str, float]
    card_weights: dict[str, float]
    final_score_vs_initial: float
    champion_updates: int
    generations: list[dict]


def train_linear_policy(output_path=DEFAULT_MODEL_PATH, config=None):
    config = config or TrainingConfig()
    rng = random.Random(config.seed)
    initial_weights = linear_policy_weights()
    champion = copy.deepcopy(initial_weights)
    generation_records = []
    champion_updates = 0

    for generation in range(config.generations):
        opponent = copy.deepcopy(champion)
        board_seeds = _board_seeds(config.seed, generation, config.boards_per_generation)
        candidates = _candidate_weights(opponent, rng, config.population, config.mutation_scale, generation)
        best_record = {
            "candidate": "champion",
            "average_delta": 0.0,
            "total_delta": 0,
            "accepted": False,
        }
        best_weights = opponent

        for candidate_id, candidate in candidates:
            match = evaluate_linear_policy(candidate, opponent, board_seeds)
            record = {
                "candidate": candidate_id,
                "average_delta": match.average_delta,
                "total_delta": match.total_delta,
                "boards": match.boards,
                "passouts": match.passouts,
                "accepted": False,
            }
            if match.average_delta > best_record["average_delta"]:
                best_record = record
                best_weights = candidate

        if best_record["candidate"] != "champion":
            best_record["accepted"] = True
            champion = copy.deepcopy(best_weights)
            champion_updates += 1

        validation = evaluate_linear_policy(
            champion,
            initial_weights,
            _board_seeds(config.seed + 97_531, generation, config.validation_boards),
        )
        if validation.average_delta < 0:
            champion = copy.deepcopy(initial_weights)
            champion_updates = 0
            best_record = {
                **best_record,
                "accepted": False,
                "validation_guard": "reverted_to_initial",
            }
            validation = evaluate_linear_policy(
                champion,
                initial_weights,
                _board_seeds(config.seed + 97_531, generation, config.validation_boards),
            )

        generation_records.append({
            "generation": generation,
            "selected": best_record,
            "validation_average_delta_vs_initial": validation.average_delta,
            "validation_total_delta_vs_initial": validation.total_delta,
        })

    final_validation = evaluate_linear_policy(
        champion,
        initial_weights,
        _board_seeds(config.seed + 250_001, 0, config.validation_boards),
    )
    if final_validation.average_delta < 0:
        champion = copy.deepcopy(initial_weights)
        champion_updates = 0
        final_validation = evaluate_linear_policy(
            champion,
            initial_weights,
            _board_seeds(config.seed + 250_001, 0, config.validation_boards),
        )

    result = TrainingResult(
        model_path=str(output_path),
        config=asdict(config),
        bid_weights=champion["bid_weights"],
        card_weights=champion["card_weights"],
        final_score_vs_initial=final_validation.average_delta,
        champion_updates=champion_updates,
        generations=generation_records,
    )
    save_linear_policy_model(output_path, result)
    return result


def evaluate_linear_policy(candidate_weights, opponent_weights, board_seeds):
    total_delta = 0
    passouts = 0
    board_count = 0
    for seed in board_seeds:
        candidate_ns = play_board(
            _users_for_match(candidate_weights, opponent_weights, candidate_team="NS"),
            seed,
        )
        candidate_ew = play_board(
            _users_for_match(candidate_weights, opponent_weights, candidate_team="EW"),
            seed,
        )
        total_delta += score_to_imps(candidate_ns.ns_score - candidate_ew.ns_score)
        passouts += int(candidate_ns.passed_out) + int(candidate_ew.passed_out)
        board_count += 2

    average = total_delta / board_count if board_count else 0.0
    return MatchScore(
        average_delta=average,
        total_delta=total_delta,
        boards=board_count,
        passouts=passouts,
    )


def play_board(users, seed, dealer=Players.NORTH, vulnerability=Vulnerabilities.BOTH):
    deal = deal_from_seed(seed)
    auction = bidding.Auction(dealer)
    safety_limit = 128

    while not auction.complete() and safety_limit > 0:
        current_player = auction.player
        bid = choose_bid_for_user(
            users[current_player],
            current_player,
            deal[current_player].cards,
            auction.legal_bids(),
            auction.record,
        )
        status = auction.get_new_bid(bid)
        if status == AuctionStatus.DONE:
            break
        safety_limit -= 1
    if safety_limit <= 0:
        raise RuntimeError("auction did not complete")

    full_contract = auction.determine_full_contract()
    if full_contract.passout:
        return BoardScore(0, True, "PASSOUT", None)

    with contextlib.redirect_stdout(io.StringIO()):
        declarer_tricks = cardplay.play(
            users,
            deal,
            full_contract.contract,
            full_contract.declarer,
            auction.record,
        )

    declarer_score = get_score_from_result(
        full_contract.contract,
        full_contract.doubled,
        declarer_tricks,
        vulnerability.is_declarer_vulnerable(full_contract.declarer),
    )
    ns_score = declarer_score if Team.NS.is_player_in_team(full_contract.declarer) else -declarer_score
    return BoardScore(
        ns_score,
        False,
        full_contract.contract.name,
        full_contract.declarer.name,
    )


def score_to_imps(score_delta):
    sign = -1 if score_delta < 0 else 1
    absolute = abs(score_delta)
    if absolute < IMP_CUTOFFS[0][0]:
        return 0
    for cutoff, imps in reversed(IMP_CUTOFFS):
        if absolute >= cutoff:
            return sign * imps
    return 0


def deal_from_seed(seed):
    card_indices = list(range(52))
    random.Random(seed).shuffle(card_indices)
    return {
        Players.NORTH: _hand_from_indices(card_indices[0:13]),
        Players.EAST: _hand_from_indices(card_indices[13:26]),
        Players.SOUTH: _hand_from_indices(card_indices[26:39]),
        Players.WEST: _hand_from_indices(card_indices[39:52]),
    }


def linear_policy_weights(bot=None):
    bot = bot or LinearPolicyBotUser()
    return {
        "bid_weights": copy.deepcopy(bot.bid_weights),
        "card_weights": copy.deepcopy(bot.card_weights),
    }


def save_linear_policy_model(path, result):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": MODEL_SCHEMA_VERSION,
        "architecture": "LinearPolicyBotUser",
        "training": {
            "algorithm": "evolutionary_self_play",
            "result": asdict(result),
        },
        "bid_weights": result.bid_weights,
        "card_weights": result.card_weights,
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def load_linear_policy_model(path=DEFAULT_MODEL_PATH):
    payload = json.loads(Path(path).read_text())
    if payload.get("schema_version") != MODEL_SCHEMA_VERSION:
        raise ValueError("unsupported model schema version")
    if payload.get("architecture") != "LinearPolicyBotUser":
        raise ValueError("unsupported model architecture")
    return LinearPolicyBotUser(
        bid_weights=payload["bid_weights"],
        card_weights=payload["card_weights"],
    )


def _candidate_weights(champion, rng, population, mutation_scale, generation):
    candidates = []
    if generation == 0:
        candidates.extend([
            ("conservative-openings", _conservative_opening_weights(champion)),
            ("trick-taking-cardplay", _trick_taking_card_weights(champion)),
        ])
    while len(candidates) < population:
        candidates.append((
            f"mutation-{generation}-{len(candidates)}",
            _mutate_weights(champion, rng, mutation_scale),
        ))
    return candidates[:population]


def _conservative_opening_weights(weights):
    candidate = copy.deepcopy(weights)
    candidate["bid_weights"].update({
        "level_cost": -4.2,
        "pass_floor": 12.0,
        "double_points": 0.5,
    })
    return candidate


def _trick_taking_card_weights(weights):
    candidate = copy.deepcopy(weights)
    candidate["card_weights"].update({
        "wins_now": 5.4,
        "partner_winning": -4.6,
        "conserve_honor": -0.2,
    })
    return candidate


def _mutate_weights(weights, rng, mutation_scale):
    candidate = copy.deepcopy(weights)
    _mutate_group(candidate["bid_weights"], BID_WEIGHT_RANGES, rng, mutation_scale)
    _mutate_group(candidate["card_weights"], CARD_WEIGHT_RANGES, rng, mutation_scale)
    return candidate


def _mutate_group(weights, ranges, rng, mutation_scale):
    for key, value in list(weights.items()):
        low, high = ranges[key]
        span = high - low
        step = max(abs(value), span * 0.08) * mutation_scale
        mutated = value + rng.gauss(0, step)
        weights[key] = round(min(high, max(low, mutated)), 4)


def _users_for_match(candidate_weights, opponent_weights, candidate_team):
    candidate = lambda: LinearPolicyBotUser(**copy.deepcopy(candidate_weights))
    opponent = lambda: LinearPolicyBotUser(**copy.deepcopy(opponent_weights))
    if candidate_team == "NS":
        return {
            Players.NORTH: candidate(),
            Players.SOUTH: candidate(),
            Players.EAST: opponent(),
            Players.WEST: opponent(),
        }
    return {
        Players.NORTH: opponent(),
        Players.SOUTH: opponent(),
        Players.EAST: candidate(),
        Players.WEST: candidate(),
    }


def _hand_from_indices(indices):
    return BridgeHand.generate_complete_hand([
        Deck.generate_card_from_index(index)
        for index in indices
    ])


def _board_seeds(seed, generation, boards):
    return [seed + generation * 1_009 + board * 37 for board in range(boards)]


def main(argv=None):
    parser = argparse.ArgumentParser(description="Train a linear bridge policy through deterministic self-play.")
    parser.add_argument("--output", default=str(DEFAULT_MODEL_PATH), help="Path to write trained model JSON.")
    parser.add_argument("--seed", type=int, default=TrainingConfig.seed)
    parser.add_argument("--generations", type=int, default=TrainingConfig.generations)
    parser.add_argument("--population", type=int, default=TrainingConfig.population)
    parser.add_argument("--boards", type=int, default=TrainingConfig.boards_per_generation)
    parser.add_argument("--validation-boards", type=int, default=TrainingConfig.validation_boards)
    parser.add_argument("--mutation-scale", type=float, default=TrainingConfig.mutation_scale)
    args = parser.parse_args(argv)

    result = train_linear_policy(
        output_path=args.output,
        config=TrainingConfig(
            seed=args.seed,
            generations=args.generations,
            population=args.population,
            boards_per_generation=args.boards,
            validation_boards=args.validation_boards,
            mutation_scale=args.mutation_scale,
        ),
    )
    print(json.dumps({
        "model_path": result.model_path,
        "final_score_vs_initial": result.final_score_vs_initial,
        "champion_updates": result.champion_updates,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
