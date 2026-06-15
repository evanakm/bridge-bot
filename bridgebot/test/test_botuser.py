import pytest

from bridgebot.bidding import Bids
from bridgebot.bots import botuser
from bridgebot.game.card import Card
from bridgebot.game.deck import Deck
from bridgebot.game.enums import Players, Ranks, Suits


def tensor_value(value):
    if hasattr(value, "numpy"):
        return value.numpy().tolist()
    return value


def test_botuser_imports_with_optional_tensorflow_backend():
    assert hasattr(botuser, "tf")


def test_player_to_tensor_uses_player_order_index_without_tensorflow():
    assert tensor_value(botuser.player_to_tensor(Players.SOUTH)) == 2


def test_cards_to_tensor_encodes_cards_as_one_hot_vector():
    cards = [
        Card(Suits.CLUBS, Ranks.TWO),
        Card(Suits.SPADES, Ranks.ACE),
    ]

    tensor = tensor_value(botuser.cards_to_tensor(cards))

    assert len(tensor) == 52
    assert tensor[0] == 1.0
    assert tensor[51] == 1.0
    assert sum(tensor) == 2.0


def test_cards_to_tensor_accepts_sets():
    tensor = tensor_value(botuser.cards_to_tensor({Deck.generate_card_from_index(13)}))

    assert len(tensor) == 52
    assert tensor[13] == 1.0


@pytest.mark.parametrize("cards", [None, "not cards", 3])
def test_cards_to_tensor_rejects_non_card_collections(cards):
    with pytest.raises(TypeError):
        botuser.cards_to_tensor(cards)


def test_cards_to_tensor_rejects_non_card_values():
    with pytest.raises(TypeError):
        botuser.cards_to_tensor([object()])


def test_card_history_to_tensor_encodes_each_player_history_in_player_order():
    card_history = {
        Players.NORTH: [Deck.generate_card_from_index(0)],
        Players.EAST: [Deck.generate_card_from_index(13)],
        Players.SOUTH: [Deck.generate_card_from_index(26)],
        Players.WEST: [Deck.generate_card_from_index(39)],
    }

    tensor = tensor_value(botuser.card_history_to_tensor(card_history))

    assert len(tensor) == 208
    assert tensor[0] == 1.0
    assert tensor[52 + 13] == 1.0
    assert tensor[104 + 26] == 1.0
    assert tensor[156 + 39] == 1.0
    assert sum(tensor) == 4.0


def test_card_history_to_tensor_requires_all_players():
    with pytest.raises(KeyError):
        botuser.card_history_to_tensor({Players.NORTH: []})


def test_botuser_plays_lowest_legal_card():
    legal_cards = {
        Card(Suits.CLUBS, Ranks.ACE),
        Card(Suits.CLUBS, Ranks.TWO),
    }

    assert botuser.BotUser.play_card(
        Players.NORTH,
        Players.SOUTH,
        set(),
        legal_cards,
        legal_cards,
        None,
        {},
        [],
    ) == Card(Suits.CLUBS, Ranks.TWO)


def test_botuser_bids_pass_when_available():
    assert botuser.BotUser.bid(
        Players.NORTH,
        [Bids.ONE_CLUB, Bids.PASS],
        None,
    ) == Bids.PASS
