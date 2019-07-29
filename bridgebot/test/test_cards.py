import pytest
import sys

sys.path.insert(0,'../bridgebot')
sys.path.insert(0,'..')

from contextlib import contextmanager

from deck import Deck
import cards

from card import InvalidSuitException, InvalidRankException

from enums import Ranks, Suits

deck = Deck()
seven_of_hearts = cards.Card(Suits.HEARTS, Ranks.SEVEN)
eight_of_clubs = cards.Card(Suits.CLUBS, Ranks.EIGHT)

@contextmanager
def does_not_raise():
    yield

def test_deck():
    indices = deck.get_card_indices()
    print(indices) # Will be suppressed unless pytest is called with -s
    assert len(indices) == 52

def test_deck_shuffle():
    deck.shuffle()
    indices = deck.get_card_indices()
    print(indices)
    assert len(indices) == 52

def test_card():
    card = cards.Card(Suits.HEARTS, Ranks.SEVEN)
    assert card == seven_of_hearts

@pytest.mark.parametrize('suit,rank,expected_result,expected_except', [
    (Suits.HEARTS, Ranks.SEVEN, True, does_not_raise()),
    (Suits.SPADES, Ranks.TEN, False, does_not_raise()),
    (Suits.DIAMONDS, "1", False, pytest.raises(InvalidRankException)),
    ("STARS", Ranks.FIVE, False, pytest.raises(InvalidSuitException)),
])
def test_card(suit, rank, expected_result, expected_except):
    with expected_except:
        card = cards.Card(suit, rank)
        assert (card == seven_of_hearts) == expected_result

@pytest.mark.parametrize('index, expected_except', [
    (31, does_not_raise()),
    (55, pytest.raises(Exception))
])
def test_map_index_to_card(index, expected_except):
    with expected_except:
        card = Deck.generate_card_from_index(index)
        assert card == seven_of_hearts


# Generated from a random number generator
test_list = [13, 29, 7, 25, 43, 24]
# Corresponds to 2 of diamonds, 5 of hearts, 8 of clubs, ace of diamonds, 6 of spades, and king of diamonds


@pytest.mark.parametrize('suit, rank, expected', [
    (Suits.DIAMONDS, Ranks.TWO, True),
    (Suits.DIAMONDS, Ranks.KING, True),
    (Suits.SPADES, Ranks.SIX, True),
    (Suits.SPADES, Ranks.TEN, False)
])
def test_partial_hand_fill_and_contains(suit, rank, expected):
    card_list = [ Deck.generate_card_from_index(card_index) for card_index in test_list ]
    hand = cards.BridgeHand.generate_partially_played_hand(card_list)
    assert hand.contains_card(cards.Card(suit, rank)) == expected


def test_lead():
    card_list = [ Deck.generate_card_from_index(card_index) for card_index in test_list ]
    hand = cards.BridgeHand.generate_partially_played_hand(card_list)
    hand.lead(cards.Card(Suits.DIAMONDS, Ranks.KING))
    assert not hand.contains_card(cards.Card(Suits.DIAMONDS, Ranks.KING))


def test_lead_when_card_is_missing():
    card_list = [ Deck.generate_card_from_index(card_index) for card_index in test_list ]
    hand = cards.BridgeHand.generate_partially_played_hand(card_list)
    with pytest.raises(cards.CardNotInHandException):
        hand.lead(cards.Card(Suits.SPADES, Ranks.ACE))
        assert not hand.contains_card(cards.Card(Suits.DIAMONDS, Ranks.KING))


full_test_list = [13, 29, 7, 25, 43, 24, 8, 35, 47, 33, 28, 18, 2]
too_long_test_list = [13, 29, 7, 25, 43, 24, 8, 35, 47, 33, 28, 18, 2, 50]

@pytest.mark.parametrize('list,expected_except', [
    (test_list, pytest.raises(cards.WrongSizeHandException)),
    (full_test_list, does_not_raise())
])
def test_generate_hand(list, expected_except):
    card_list = [ Deck.generate_card_from_index(card_index) for card_index in list ]
    with expected_except:
        hand = cards.BridgeHand.generate_complete_hand(card_list)

@pytest.mark.parametrize('list,expected_except', [
    (test_list, does_not_raise()),
    (full_test_list, does_not_raise()),
    (too_long_test_list, pytest.raises(cards.WrongSizeHandException)),
    ([3,3], pytest.raises(cards.RepeatedCardException))
])
def test_bridge_hand_constructor(list, expected_except):
    card_list = [ Deck.generate_card_from_index(card_index) for card_index in list ]
    with expected_except:
        bridge_hand = cards.BridgeHand(card_list)
