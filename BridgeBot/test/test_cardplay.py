import pytest
import sys

sys.path.insert(0,'../BridgeBot')
sys.path.insert(0,'..')

import cardplay
from enums import Suits, Ranks
from cards import Card



def test_determine_trick_winner():
    assert cardplay.CardPlay.determine_trick_winner(
        [
            Card(Suits.SPADES, Ranks.FOUR),
            Card(Suits.HEARTS, Ranks.ACE),
            Card(Suits.CLUBS, Ranks.ACE),
            Card(Suits.DIAMONDS, Ranks.ACE)
        ],
        Suits.SPADES
    ) == 0

    assert cardplay.CardPlay.determine_trick_winner(
        [
            Card(Suits.HEARTS, Ranks.ACE),
            Card(Suits.SPADES, Ranks.FOUR),
            Card(Suits.CLUBS, Ranks.ACE),
            Card(Suits.DIAMONDS, Ranks.ACE)
        ],
        Suits.SPADES
    ) == 1

    assert cardplay.CardPlay.determine_trick_winner(
        [
            Card(Suits.HEARTS, Ranks.ACE),
            Card(Suits.CLUBS, Ranks.ACE),
            Card(Suits.DIAMONDS, Ranks.ACE),
            Card(Suits.SPADES, Ranks.FOUR)
        ],
        Suits.SPADES
    ) == 3

    assert cardplay.CardPlay.determine_trick_winner(
        [
            Card(Suits.SPADES, Ranks.FOUR),
            Card(Suits.HEARTS, Ranks.FIVE),
            Card(Suits.CLUBS, Ranks.ACE),
            Card(Suits.DIAMONDS, Ranks.ACE)
        ],
        Suits.HEARTS
    ) == 1

    assert cardplay.CardPlay.determine_trick_winner(
        [
            Card(Suits.SPADES, Ranks.FOUR),
            Card(Suits.HEARTS, Ranks.FIVE),
            Card(Suits.CLUBS, Ranks.ACE),
            Card(Suits.DIAMONDS, Ranks.ACE)
        ],
        Suits.DIAMONDS
    ) == 3

    assert cardplay.CardPlay.determine_trick_winner(
        [
            Card(Suits.SPADES, Ranks.FOUR),
            Card(Suits.DIAMONDS, Ranks.FIVE),
            Card(Suits.CLUBS, Ranks.ACE),
            Card(Suits.DIAMONDS, Ranks.ACE)
        ],
        Suits.DIAMONDS
    ) == 3

    assert cardplay.CardPlay.determine_trick_winner(
        [
            Card(Suits.DIAMONDS, Ranks.ACE),
            Card(Suits.SPADES, Ranks.FOUR),
            Card(Suits.DIAMONDS, Ranks.FIVE),
            Card(Suits.CLUBS, Ranks.ACE),
        ],
        Suits.DIAMONDS
    ) == 0

    assert cardplay.CardPlay.determine_trick_winner(
        [
            Card(Suits.SPADES, Ranks.FOUR),
            Card(Suits.DIAMONDS, Ranks.ACE),
            Card(Suits.DIAMONDS, Ranks.FIVE),
            Card(Suits.CLUBS, Ranks.ACE),
        ],
        Suits.DIAMONDS
    ) == 1

    assert cardplay.CardPlay.determine_trick_winner(
        [
            Card(Suits.SPADES, Ranks.FOUR),
            Card(Suits.DIAMONDS, Ranks.FIVE),
            Card(Suits.DIAMONDS, Ranks.ACE),
            Card(Suits.CLUBS, Ranks.ACE),
        ],
        Suits.DIAMONDS
    ) == 2

    assert cardplay.CardPlay.determine_trick_winner(
        [
            Card(Suits.CLUBS, Ranks.ACE),
            Card(Suits.SPADES, Ranks.FOUR),
            Card(Suits.DIAMONDS, Ranks.FIVE),
            Card(Suits.DIAMONDS, Ranks.ACE),
        ],
        Suits.DIAMONDS
    ) == 2

    assert cardplay.CardPlay.determine_trick_winner(
        [
            Card(Suits.CLUBS, Ranks.ACE),
            Card(Suits.SPADES, Ranks.FOUR),
            Card(Suits.DIAMONDS, Ranks.ACE),
            Card(Suits.DIAMONDS, Ranks.FIVE),
        ],
        Suits.DIAMONDS
    ) == 2