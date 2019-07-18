import pytest
import sys
sys.path.insert(0,'..')

import BridgeBot.cards as Cards

def test_deck():
    deck = Cards.Deck()
    print(deck.card_indices)
    assert len(deck.card_indices) == 52

    deck.shuffle()
    print(deck.card_indices)
    assert len(deck.card_indices) == 52

