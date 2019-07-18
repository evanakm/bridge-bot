import pytest
from .. import cards as Cards

def test_deck():
    deck = Cards.Deck()
    pytest.assume(len(deck) == 52)
    print(deck)

    deck.shuffle()
    pytest.assume(len(deck) == 52)
    print(deck)

