import json

from bridgebot.bidding import Bids
from bridgebot.bots.aiplayers import LinearPolicyBotUser, RandomBotUser
from bridgebot.game.enums import Players
from bridgebot.game.interface import User
from bridgebot.training import self_play
from bridgebot.training.self_play import (
    MatchScore,
    TrainingConfig,
    benchmark_team_compositions,
    deal_from_seed,
    evaluate_linear_policy,
    evaluate_linear_policy_against_bot,
    evaluate_team_factories,
    linear_policy_weights,
    load_linear_policy_model,
    play_board,
    score_to_imps,
    train_linear_policy,
)


class AlwaysPassBot(User):
    @staticmethod
    def bid(_current_player, legal_bids, _bid_history):
        assert Bids.PASS in legal_bids
        return Bids.PASS

    @staticmethod
    def play_card(_current_player, _dummy, _dummy_hand, _all_cards, legal_cards, _bid_history, _card_history, _leader_history):
        return sorted(legal_cards, key=lambda card: card.to_int())[0]


class RecordingLinearPolicyBot(LinearPolicyBotUser):
    def __init__(self):
        super().__init__()
        self.play_view_sizes = []

    def play_card(self, current_player, dummy, dummy_hand, all_cards, legal_cards, bid_history, card_history, leader_history):
        self.play_view_sizes.append(len(all_cards))
        assert len(all_cards) <= 13
        return super().play_card(current_player, dummy, dummy_hand, all_cards, legal_cards, bid_history, card_history, leader_history)


def test_seeded_deals_are_deterministic_and_complete():
    first = deal_from_seed(17)
    second = deal_from_seed(17)

    assert {
        player: sorted(card.to_int() for card in hand.cards)
        for player, hand in first.items()
    } == {
        player: sorted(card.to_int() for card in hand.cards)
        for player, hand in second.items()
    }

    all_cards = [card.to_int() for hand in first.values() for card in hand.cards]
    assert len(all_cards) == 52
    assert len(set(all_cards)) == 52


def test_identical_linear_policies_score_zero_in_duplicate_match():
    weights = linear_policy_weights()

    match = evaluate_linear_policy(weights, weights, [101, 202])

    assert match.boards == 4
    assert match.total_delta == 0
    assert match.average_delta == 0


def test_play_board_handles_passout_without_card_play():
    board = play_board({
        Players.NORTH: AlwaysPassBot(),
        Players.EAST: AlwaysPassBot(),
        Players.SOUTH: AlwaysPassBot(),
        Players.WEST: AlwaysPassBot(),
    }, seed=909)

    assert board.passed_out
    assert board.ns_score == 0
    assert board.contract == "PASSOUT"


def test_score_to_imps_uses_standard_cutoffs():
    assert score_to_imps(0) == 0
    assert score_to_imps(10) == 0
    assert score_to_imps(20) == 1
    assert score_to_imps(50) == 2
    assert score_to_imps(1_000) == 14
    assert score_to_imps(4_000) == 24
    assert score_to_imps(-750) == -13


def test_play_board_returns_score_from_real_gameplay():
    bot = LinearPolicyBotUser()
    board = play_board({
        Players.NORTH: bot,
        Players.EAST: bot,
        Players.SOUTH: bot,
        Players.WEST: bot,
    }, seed=404)

    assert isinstance(board.ns_score, int)
    assert board.contract
    assert board.declarer is None or board.declarer in {"NORTH", "EAST", "SOUTH", "WEST"}


def test_play_board_only_passes_current_hand_view_to_bots():
    bots = {
        Players.NORTH: RecordingLinearPolicyBot(),
        Players.EAST: RecordingLinearPolicyBot(),
        Players.SOUTH: RecordingLinearPolicyBot(),
        Players.WEST: RecordingLinearPolicyBot(),
    }

    board = play_board(bots, seed=404)

    assert not board.passed_out
    assert sum(len(bot.play_view_sizes) for bot in bots.values()) == 52
    assert all(size <= 13 for bot in bots.values() for size in bot.play_view_sizes)


def test_self_play_training_writes_loadable_non_regressing_model(tmp_path):
    output = tmp_path / "linear_policy_selfplay.json"

    result = train_linear_policy(
        output_path=output,
        config=TrainingConfig(
            seed=101,
            generations=2,
            population=3,
            boards_per_generation=3,
            validation_boards=4,
        ),
    )

    payload = json.loads(output.read_text())
    loaded = load_linear_policy_model(output)

    assert payload["schema_version"] == 1
    assert payload["architecture"] == "LinearPolicyBotUser"
    assert payload["bid_weights"] == result.bid_weights
    assert payload["card_weights"] == result.card_weights
    assert set(payload["training"]["result"]["baseline_scores"]) == {
        "initial_linear",
        "random",
        "rule_based",
        "rollout_8",
    }
    assert set(payload["training"]["result"]["pair_scores"]) == {
        "trained_random_vs_random_random",
        "trained_trained_vs_random_random",
        "trained_trained_vs_trained_random",
        "random_random_vs_random_random",
        "trained_trained_vs_trained_trained",
    }
    assert loaded.bid_weights == result.bid_weights
    assert loaded.card_weights == result.card_weights
    assert result.final_score_vs_initial >= 0
    assert result.champion_updates >= 1


def test_self_play_training_is_reproducible_for_same_seed(tmp_path):
    config = TrainingConfig(
        seed=303,
        generations=1,
        population=2,
        boards_per_generation=2,
        validation_boards=2,
    )

    first = train_linear_policy(output_path=tmp_path / "first.json", config=config)
    second = train_linear_policy(output_path=tmp_path / "second.json", config=config)

    assert first.bid_weights == second.bid_weights
    assert first.card_weights == second.card_weights
    assert first.baseline_scores == second.baseline_scores
    assert first.pair_scores == second.pair_scores
    assert first.generations == second.generations


def test_identical_team_compositions_score_zero_in_duplicate_match():
    random_factory = lambda player: RandomBotUser(seed=Players.players().index(player))
    random_pair = (random_factory, random_factory)

    match = evaluate_team_factories(random_pair, random_pair, [101, 202])

    assert match.boards == 4
    assert match.total_delta == 0
    assert match.average_delta == 0


def test_team_composition_benchmark_reports_requested_pairs():
    pair_scores = benchmark_team_compositions(
        linear_policy_weights(),
        [101, 202],
        seed=55,
    )

    assert set(pair_scores) == {
        "trained_random_vs_random_random",
        "trained_trained_vs_random_random",
        "trained_trained_vs_trained_random",
        "random_random_vs_random_random",
        "trained_trained_vs_trained_trained",
    }
    assert pair_scores["random_random_vs_random_random"]["average_delta"] == 0
    assert pair_scores["trained_trained_vs_trained_trained"]["average_delta"] == 0


def test_linear_policy_can_be_scored_against_arbitrary_bot_baseline():
    weights = linear_policy_weights()

    match = evaluate_linear_policy_against_bot(
        weights,
        lambda _player: AlwaysPassBot(),
        [101, 202],
    )

    assert match.boards == 4
    assert match.passouts >= 0


def test_self_play_saves_best_validated_champion(monkeypatch, tmp_path):
    first_candidate = linear_policy_weights()
    first_candidate["bid_weights"]["pass_floor"] = 15.0
    later_candidate = linear_policy_weights()
    later_candidate["bid_weights"]["pass_floor"] = 14.0

    def fake_candidates(_champion, _rng, _population, _mutation_scale, generation):
        if generation == 0:
            return [("first-candidate", first_candidate)]
        return [("later-candidate", later_candidate)]

    def fake_evaluate(candidate, _opponent, board_seeds):
        if board_seeds[0] < 50_000:
            return MatchScore(1.0, 1, 2, 0)

        pass_floor = candidate["bid_weights"]["pass_floor"]
        if pass_floor == 15.0:
            return MatchScore(8.0, 8, 2, 0)
        if pass_floor == 14.0:
            return MatchScore(2.0, 2, 2, 0)
        return MatchScore(0.0, 0, 2, 0)

    monkeypatch.setattr(self_play, "_candidate_weights", fake_candidates)
    monkeypatch.setattr(self_play, "evaluate_linear_policy", fake_evaluate)
    monkeypatch.setattr(
        self_play,
        "benchmark_linear_policy",
        lambda *_args: {
            "initial_linear": {"average_delta": 8.0, "total_delta": 8, "boards": 2, "passouts": 0},
            "random": {"average_delta": 9.0, "total_delta": 9, "boards": 2, "passouts": 0},
            "rule_based": {"average_delta": 1.0, "total_delta": 1, "boards": 2, "passouts": 0},
            "rollout_8": {"average_delta": 0.0, "total_delta": 0, "boards": 2, "passouts": 0},
        },
    )
    monkeypatch.setattr(
        self_play,
        "benchmark_team_compositions",
        lambda *_args: {
            "trained_random_vs_random_random": {"average_delta": 2.0, "total_delta": 2, "boards": 2, "passouts": 0},
            "trained_trained_vs_random_random": {"average_delta": 8.0, "total_delta": 8, "boards": 2, "passouts": 0},
            "trained_trained_vs_trained_random": {"average_delta": 1.0, "total_delta": 1, "boards": 2, "passouts": 0},
            "random_random_vs_random_random": {"average_delta": 0.0, "total_delta": 0, "boards": 2, "passouts": 0},
            "trained_trained_vs_trained_trained": {"average_delta": 0.0, "total_delta": 0, "boards": 2, "passouts": 0},
        },
    )

    result = train_linear_policy(
        output_path=tmp_path / "linear_policy_selfplay.json",
        config=TrainingConfig(
            seed=7,
            generations=2,
            population=1,
            boards_per_generation=1,
            validation_boards=1,
        ),
    )

    assert result.bid_weights["pass_floor"] == 15.0
    assert result.final_selection == "best_validated"
