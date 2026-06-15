import json

from bridgebot.bidding import Bids
from bridgebot.bots.aiplayers import LinearPolicyBotUser
from bridgebot.game.enums import Players
from bridgebot.training.self_play import (
    TrainingConfig,
    deal_from_seed,
    evaluate_linear_policy,
    linear_policy_weights,
    load_linear_policy_model,
    play_board,
    score_to_imps,
    train_linear_policy,
)


class AlwaysPassBot:
    @staticmethod
    def bid(_current_player, legal_bids, _bid_history):
        assert Bids.PASS in legal_bids
        return Bids.PASS


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
    assert loaded.bid_weights == result.bid_weights
    assert loaded.card_weights == result.card_weights
    assert result.final_score_vs_initial >= 0
    assert result.champion_updates >= 1
