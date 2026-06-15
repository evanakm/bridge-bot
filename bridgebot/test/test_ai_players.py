from bridgebot.bidding import Auction, Bids
from bridgebot.bots.aiplayers import (
    EnsembleBotUser,
    LinearPolicyBotUser,
    RolloutBotUser,
    RuleBasedBotUser,
    choose_bid_for_user,
    high_card_points,
    is_balanced,
)
from bridgebot.bots.botuser import BotUser
from bridgebot.game.card import Card
from bridgebot.game.enums import Players, Ranks, Suits


def card(suit, rank):
    return Card(suit, rank)


def balanced_15_count_hand():
    return {
        card(Suits.SPADES, Ranks.ACE),
        card(Suits.SPADES, Ranks.KING),
        card(Suits.SPADES, Ranks.THREE),
        card(Suits.SPADES, Ranks.TWO),
        card(Suits.HEARTS, Ranks.QUEEN),
        card(Suits.HEARTS, Ranks.JACK),
        card(Suits.HEARTS, Ranks.TWO),
        card(Suits.DIAMONDS, Ranks.KING),
        card(Suits.DIAMONDS, Ranks.THREE),
        card(Suits.DIAMONDS, Ranks.TWO),
        card(Suits.CLUBS, Ranks.QUEEN),
        card(Suits.CLUBS, Ranks.THREE),
        card(Suits.CLUBS, Ranks.TWO),
    }


def spade_opening_hand():
    return {
        card(Suits.SPADES, Ranks.ACE),
        card(Suits.SPADES, Ranks.KING),
        card(Suits.SPADES, Ranks.QUEEN),
        card(Suits.SPADES, Ranks.FOUR),
        card(Suits.SPADES, Ranks.THREE),
        card(Suits.HEARTS, Ranks.JACK),
        card(Suits.HEARTS, Ranks.KING),
        card(Suits.DIAMONDS, Ranks.THREE),
        card(Suits.DIAMONDS, Ranks.TWO),
        card(Suits.CLUBS, Ranks.FIVE),
        card(Suits.CLUBS, Ranks.FOUR),
        card(Suits.CLUBS, Ranks.THREE),
        card(Suits.CLUBS, Ranks.TWO),
    }


def empty_card_history():
    return {
        Players.NORTH: [],
        Players.EAST: [],
        Players.SOUTH: [],
        Players.WEST: [],
    }


def legal_opening_bids():
    return Auction(Players.NORTH).legal_bids()


def test_hand_features_score_high_card_points_and_balance():
    hand = balanced_15_count_hand()

    assert high_card_points(hand) == 15
    assert is_balanced(hand)


def test_rule_based_bot_opens_one_no_trump_with_balanced_15_count():
    bid = RuleBasedBotUser.bid_with_hand(
        Players.NORTH,
        balanced_15_count_hand(),
        legal_opening_bids(),
        Auction(Players.NORTH).record,
    )

    assert bid == Bids.ONE_NO_TRUMP


def test_rule_based_bot_opens_longest_suit_with_opening_values():
    bid = RuleBasedBotUser.bid_with_hand(
        Players.NORTH,
        spade_opening_hand(),
        legal_opening_bids(),
        Auction(Players.NORTH).record,
    )

    assert bid == Bids.ONE_SPADE


def test_linear_policy_bot_chooses_a_legal_non_pass_call_with_strong_hand():
    legal_bids = legal_opening_bids()
    bid = LinearPolicyBotUser().bid_with_hand(
        Players.NORTH,
        balanced_15_count_hand(),
        legal_bids,
        Auction(Players.NORTH).record,
    )

    assert bid in legal_bids
    assert bid != Bids.PASS


def test_choose_bid_for_user_uses_hand_aware_extension_when_available():
    legal_bids = legal_opening_bids()

    assert choose_bid_for_user(
        RuleBasedBotUser(),
        Players.NORTH,
        balanced_15_count_hand(),
        legal_bids,
        Auction(Players.NORTH).record,
    ) == Bids.ONE_NO_TRUMP
    assert choose_bid_for_user(
        BotUser(),
        Players.NORTH,
        balanced_15_count_hand(),
        legal_bids,
        Auction(Players.NORTH).record,
    ) == Bids.PASS


def test_rule_based_card_play_wins_with_lowest_sufficient_card():
    legal_cards = {
        card(Suits.HEARTS, Ranks.QUEEN),
        card(Suits.HEARTS, Ranks.ACE),
    }
    card_history = empty_card_history()
    card_history[Players.NORTH].append(card(Suits.HEARTS, Ranks.TEN))
    card_history[Players.EAST].append(card(Suits.HEARTS, Ranks.JACK))

    assert RuleBasedBotUser.play_card(
        Players.SOUTH,
        Players.NORTH,
        set(),
        legal_cards,
        legal_cards,
        Auction(Players.NORTH).record,
        card_history,
        [Players.NORTH],
    ) == card(Suits.HEARTS, Ranks.QUEEN)


def test_rule_based_card_play_ducks_when_partner_is_winning():
    legal_cards = {
        card(Suits.HEARTS, Ranks.QUEEN),
        card(Suits.HEARTS, Ranks.TWO),
    }
    card_history = empty_card_history()
    card_history[Players.NORTH].append(card(Suits.HEARTS, Ranks.TEN))
    card_history[Players.EAST].append(card(Suits.HEARTS, Ranks.ACE))

    assert RuleBasedBotUser.play_card(
        Players.SOUTH,
        Players.NORTH,
        set(),
        legal_cards,
        legal_cards,
        Auction(Players.NORTH).record,
        card_history,
        [Players.NORTH],
    ) == card(Suits.HEARTS, Ranks.TWO)


def test_rollout_bot_takes_last_seat_trick_with_lowest_winner():
    legal_cards = {
        card(Suits.HEARTS, Ranks.THREE),
        card(Suits.HEARTS, Ranks.QUEEN),
        card(Suits.HEARTS, Ranks.ACE),
    }
    card_history = empty_card_history()
    card_history[Players.NORTH].append(card(Suits.HEARTS, Ranks.TEN))
    card_history[Players.EAST].append(card(Suits.HEARTS, Ranks.JACK))
    card_history[Players.SOUTH].append(card(Suits.HEARTS, Ranks.TWO))

    assert RolloutBotUser().play_card(
        Players.WEST,
        Players.SOUTH,
        set(),
        legal_cards,
        legal_cards,
        Auction(Players.NORTH).record,
        card_history,
        [Players.NORTH],
    ) == card(Suits.HEARTS, Ranks.QUEEN)


def test_every_ai_architecture_returns_legal_bid_and_card():
    legal_bids = legal_opening_bids()
    legal_cards = {
        card(Suits.CLUBS, Ranks.TWO),
        card(Suits.CLUBS, Ranks.ACE),
    }

    for bot in [
        RuleBasedBotUser(),
        LinearPolicyBotUser(),
        RolloutBotUser(trials=8),
        EnsembleBotUser(),
    ]:
        bid = choose_bid_for_user(
            bot,
            Players.NORTH,
            balanced_15_count_hand(),
            legal_bids,
            Auction(Players.NORTH).record,
        )
        played = bot.play_card(
            Players.NORTH,
            Players.SOUTH,
            set(),
            legal_cards,
            legal_cards,
            Auction(Players.NORTH).record,
            empty_card_history(),
            [],
        )

        assert bid in legal_bids
        assert played in legal_cards


def test_rollout_bot_does_not_require_hidden_opponent_hands():
    legal_cards = {
        card(Suits.SPADES, Ranks.TWO),
        card(Suits.HEARTS, Ranks.ACE),
    }

    played = RolloutBotUser(trials=4, seed=9).play_card(
        Players.NORTH,
        Players.SOUTH,
        set(),
        legal_cards,
        legal_cards,
        Auction(Players.NORTH).record,
        empty_card_history(),
        [],
    )

    assert played in legal_cards
