import pytest
import sys

sys.path.insert(0,'../bridgebot')
sys.path.insert(0,'..')

from contextlib import contextmanager

from game.deck import Deck
from game.bridgehand import Card, BridgeHand, CardDoesntFollowSuitException, CardNotInHandException, RepeatedCardException, WrongSizeHandException

from game.card import InvalidSuitException, InvalidRankException

from game.enums import Ranks, Suits

deck = Deck()
seven_of_hearts = Card(Suits.HEARTS, Ranks.SEVEN)
eight_of_clubs = Card(Suits.CLUBS, Ranks.EIGHT)

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
    card = Card(Suits.HEARTS, Ranks.SEVEN)
    assert card == seven_of_hearts

def test_card_str():
    card = Card(Suits.HEARTS, Ranks.SEVEN)
    assert str(card) == "SEVEN_HEARTS"

@pytest.mark.parametrize('suit,rank,expected_result,expected_except', [
    (Suits.HEARTS, Ranks.SEVEN, True, does_not_raise()),
    (Suits.SPADES, Ranks.TEN, False, does_not_raise()),
    (Suits.DIAMONDS, "1", False, pytest.raises(InvalidRankException)),
    ("STARS", Ranks.FIVE, False, pytest.raises(InvalidSuitException)),
])
def test_card(suit, rank, expected_result, expected_except):
    with expected_except:
        card = Card(suit, rank)
        assert (card == seven_of_hearts) == expected_result

@pytest.mark.parametrize('index, expected_except', [
    (31, does_not_raise()),
    (55, pytest.raises(Exception))
])
def test_map_index_to_card(index, expected_except):
    with expected_except:
        card = Deck.generate_card_from_index(index)
        assert card == seven_of_hearts

#-------- TESTING HANDS --------#
# Generated from a random number generator
test_list = [13, 29, 7, 25, 24]
# Corresponds to 2 of diamonds, 5 of hearts, 8 of clubs, ace of diamonds, and king of diamonds


@pytest.mark.parametrize('suit, rank, expected', [
    (Suits.DIAMONDS, Ranks.TWO, True),
    (Suits.DIAMONDS, Ranks.KING, True),
    (Suits.HEARTS, Ranks.FIVE, True),
    (Suits.SPADES, Ranks.TEN, False)
])
def test_partial_hand_fill_and_contains(suit, rank, expected):
    card_list = [ Deck.generate_card_from_index(card_index) for card_index in test_list ]
    hand = BridgeHand.generate_partially_played_hand(card_list)
    assert hand.contains_card(Card(suit, rank)) == expected


def test_lead():
    card_list = [ Deck.generate_card_from_index(card_index) for card_index in test_list ]
    hand = BridgeHand.generate_partially_played_hand(card_list)
    hand.lead(Card(Suits.DIAMONDS, Ranks.KING))
    assert not hand.contains_card(Card(Suits.DIAMONDS, Ranks.KING))


def test_lead_when_card_is_missing():
    card_list = [ Deck.generate_card_from_index(card_index) for card_index in test_list ]
    hand = BridgeHand.generate_partially_played_hand(card_list)
    with pytest.raises(CardNotInHandException):
        hand.lead(Card(Suits.SPADES, Ranks.ACE))


# The hand contains no spades, so arbitrarily playing a card when following spades doesn't fail
@pytest.mark.parametrize('led_suit,card', [
    (Suits.DIAMONDS, Card(Suits.DIAMONDS, Ranks.ACE)),
    (Suits.SPADES, Card(Suits.DIAMONDS, Ranks.ACE))
])
def test_follow(led_suit, card):
    card_list = [ Deck.generate_card_from_index(card_index) for card_index in test_list ]
    hand = BridgeHand.generate_partially_played_hand(card_list)
    hand.follow(led_suit, card)
    assert not hand.contains_card(card)

@pytest.mark.parametrize('led_suit,card,expected_except', [
    (Suits.DIAMONDS, Card(Suits.DIAMONDS, Ranks.QUEEN), pytest.raises(CardNotInHandException)),
    (Suits.DIAMONDS, Card(Suits.CLUBS, Ranks.EIGHT), pytest.raises(CardDoesntFollowSuitException))
])
def test_follow_raises(led_suit, card, expected_except):
    card_list = [ Deck.generate_card_from_index(card_index) for card_index in test_list ]
    hand = BridgeHand.generate_partially_played_hand(card_list)
    with expected_except:
        hand.follow(led_suit, card)


full_test_list = [13, 29, 7, 25, 43, 24, 8, 35, 47, 33, 28, 18, 2]
too_long_test_list = [13, 29, 7, 25, 43, 24, 8, 35, 47, 33, 28, 18, 2, 50]

@pytest.mark.parametrize('list,expected_except', [
    (test_list, pytest.raises(WrongSizeHandException)),
    (full_test_list, does_not_raise())
])
def test_generate_hand(list, expected_except):
    card_list = [ Deck.generate_card_from_index(card_index) for card_index in list ]
    with expected_except:
        hand = BridgeHand.generate_complete_hand(card_list)

@pytest.mark.parametrize('list,expected_except', [
    (test_list, does_not_raise()),
    (full_test_list, does_not_raise()),
    (too_long_test_list, pytest.raises(WrongSizeHandException)),
    ([3,3], pytest.raises(RepeatedCardException))
])
def test_bridge_hand_constructor(list, expected_except):
    card_list = [ Deck.generate_card_from_index(card_index) for card_index in list ]
    with expected_except:
        bridge_hand = BridgeHand(card_list)

def test_legal_cards():
    card_list = [Deck.generate_card_from_index(card_index) for card_index in test_list]
    hand = BridgeHand.generate_partially_played_hand(card_list)
    legal = hand.legal_cards(Suits.DIAMONDS)
    assert Card(Suits.DIAMONDS, Ranks.ACE) in legal

