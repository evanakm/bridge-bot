import pytest
import sys
sys.path.insert(0,'..')
from contextlib import contextmanager

import BridgeBot.cards as cards
from BridgeBot.enums import INVALID, Ranks, Suits

deck = cards.Deck()
seven_of_hearts = cards.Card(Suits.HEARTS, Ranks.SEVEN)
eight_of_clubs = cards.Card(Suits.CLUBS, Ranks.EIGHT)

@contextmanager
def does_not_raise():
    yield


def test_deck():
    print(deck.card_indices) # Will be suppressed unless pytest is called with -s
    assert len(deck.card_indices) == 52

def test_deck_shuffle():
    deck.shuffle()
    print(deck.card_indices)
    assert len(deck.card_indices) == 52


def test_card():
    card = cards.Card(Suits.HEARTS, Suits.HEARTS)
    assert not card.does_not_match(seven_of_hearts)


@pytest.mark.parametrize('suit,rank,expected_result,expected_except', [
    (Suits.HEARTS, Ranks.SEVEN, True, does_not_raise()),
    (Suits.SPADES, Ranks.TEN, False, does_not_raise()),
    (Suits.DIAMONDS, "1", False, pytest.raises(cards.InvalidRankException)),
    ("STARS", Ranks.FIVE, False, pytest.raises(cards.InvalidSuitException)),
])
def test_card(suit, rank, expected_result, expected_except):
    with expected_except:
        card = cards.Card(suit, rank)
        assert card.matches(seven_of_hearts) == expected_result

@pytest.mark.parametrize('index,expected_except', [
    (31, does_not_raise()),
    (55, pytest.raises(Exception))
])
def test_map_index_to_card(index, expected_except):
    with expected_except:
        card = cards.map_index_to_card(index)
        assert card.matches(seven_of_hearts)

