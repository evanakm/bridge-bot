import pytest
import sys

sys.path.insert(0,'../BridgeBot')
sys.path.insert(0,'..')

import cardplay
from enums import Suits, Ranks
from cards import Card


@pytest.mark.parametrize('played_cards, trump_suit, expected', [
    (
            [
                Card(Suits.SPADES, Ranks.FOUR),
                Card(Suits.HEARTS, Ranks.ACE),
                Card(Suits.CLUBS, Ranks.ACE),
                Card(Suits.DIAMONDS, Ranks.ACE)
            ],
            Suits.SPADES,
            0
    ),
    (
            [
                Card(Suits.HEARTS, Ranks.ACE),
                Card(Suits.SPADES, Ranks.FOUR),
                Card(Suits.CLUBS, Ranks.ACE),
                Card(Suits.DIAMONDS, Ranks.ACE)
            ],
            Suits.SPADES,
            1
    ),
    (
            [
                Card(Suits.HEARTS, Ranks.ACE),
                Card(Suits.CLUBS, Ranks.ACE),
                Card(Suits.DIAMONDS, Ranks.ACE),
                Card(Suits.SPADES, Ranks.FOUR)
            ],
            Suits.SPADES,
            3
    ),
    (
            [
                Card(Suits.SPADES, Ranks.FOUR),
                Card(Suits.HEARTS, Ranks.FIVE),
                Card(Suits.CLUBS, Ranks.ACE),
                Card(Suits.DIAMONDS, Ranks.ACE)
            ],
            Suits.HEARTS,
            1
    ),
    (
            [
                Card(Suits.SPADES, Ranks.FOUR),
                Card(Suits.HEARTS, Ranks.FIVE),
                Card(Suits.CLUBS, Ranks.ACE),
                Card(Suits.DIAMONDS, Ranks.ACE)
            ],
            Suits.DIAMONDS,
            3
    ),
    (
            [
                Card(Suits.SPADES, Ranks.FOUR),
                Card(Suits.DIAMONDS, Ranks.FIVE),
                Card(Suits.CLUBS, Ranks.ACE),
                Card(Suits.DIAMONDS, Ranks.ACE)
            ],
            Suits.DIAMONDS,
            3
    ),
    (
            [
                Card(Suits.DIAMONDS, Ranks.ACE),
                Card(Suits.SPADES, Ranks.FOUR),
                Card(Suits.DIAMONDS, Ranks.FIVE),
                Card(Suits.CLUBS, Ranks.ACE),
            ],
            Suits.DIAMONDS,
            0
    ),
    (
            [
                Card(Suits.SPADES, Ranks.FOUR),
                Card(Suits.DIAMONDS, Ranks.ACE),
                Card(Suits.DIAMONDS, Ranks.FIVE),
                Card(Suits.CLUBS, Ranks.ACE),
            ],
            Suits.DIAMONDS,
            1
    ),
    (
            [
                Card(Suits.SPADES, Ranks.FOUR),
                Card(Suits.DIAMONDS, Ranks.FIVE),
                Card(Suits.DIAMONDS, Ranks.ACE),
                Card(Suits.CLUBS, Ranks.ACE),
            ],
            Suits.DIAMONDS,
            2
    ),
    (
            [
                Card(Suits.CLUBS, Ranks.ACE),
                Card(Suits.SPADES, Ranks.FOUR),
                Card(Suits.DIAMONDS, Ranks.FIVE),
                Card(Suits.DIAMONDS, Ranks.ACE),
            ],
            Suits.DIAMONDS,
            3
    ),
    (
            [
                Card(Suits.CLUBS, Ranks.ACE),
                Card(Suits.SPADES, Ranks.FOUR),
                Card(Suits.DIAMONDS, Ranks.ACE),
                Card(Suits.DIAMONDS, Ranks.FIVE),
            ],
            Suits.DIAMONDS,
            2
    )
])
def test_determine_trick_winner(played_cards, trump_suit, expected):
    assert cardplay.CardPlay.determine_trick_winner(played_cards, trump_suit) == expected