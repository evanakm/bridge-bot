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

@pytest.mark.parametrize('suit,rank,expected_result,expected_except', [
    ("HEARTS", "7", True, does_not_raise()),
    ("SPADES", "10", False, does_not_raise()),
    ("DIAMONDS", "1", ),
    (0, pytest.raises(ZeroDivisionError)),
])
def test_card(suit, rank):
    with pytest.raises(Exception, match="Unknown Suit"):
        card = cards.Card("STARS", "SEVEN")
