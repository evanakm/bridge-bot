import pytest
from bridgebot.game import cardplay
from bridgebot.game.enums import Strains, Suits, Ranks
from bridgebot.game.bridgehand import Card


@pytest.mark.parametrize('played_cards, trump_strain, expected', [
    (
            [
                Card(Suits.SPADES, Ranks.FOUR),
                Card(Suits.HEARTS, Ranks.ACE),
                Card(Suits.CLUBS, Ranks.ACE),
                Card(Suits.DIAMONDS, Ranks.ACE)
            ],
            Strains.SPADES,
            0
    ),
    (
            [
                Card(Suits.HEARTS, Ranks.ACE),
                Card(Suits.SPADES, Ranks.FOUR),
                Card(Suits.CLUBS, Ranks.ACE),
                Card(Suits.DIAMONDS, Ranks.ACE)
            ],
            Strains.SPADES,
            1
    ),
    (
            [
                Card(Suits.HEARTS, Ranks.ACE),
                Card(Suits.CLUBS, Ranks.ACE),
                Card(Suits.DIAMONDS, Ranks.ACE),
                Card(Suits.SPADES, Ranks.FOUR)
            ],
            Strains.SPADES,
            3
    ),
    (
            [
                Card(Suits.SPADES, Ranks.FOUR),
                Card(Suits.HEARTS, Ranks.FIVE),
                Card(Suits.CLUBS, Ranks.ACE),
                Card(Suits.DIAMONDS, Ranks.ACE)
            ],
            Strains.HEARTS,
            1
    ),
    (
            [
                Card(Suits.SPADES, Ranks.FOUR),
                Card(Suits.HEARTS, Ranks.FIVE),
                Card(Suits.CLUBS, Ranks.ACE),
                Card(Suits.DIAMONDS, Ranks.ACE)
            ],
            Strains.DIAMONDS,
            3
    ),
    (
            [
                Card(Suits.SPADES, Ranks.FOUR),
                Card(Suits.DIAMONDS, Ranks.FIVE),
                Card(Suits.CLUBS, Ranks.ACE),
                Card(Suits.DIAMONDS, Ranks.ACE)
            ],
            Strains.DIAMONDS,
            3
    ),
    (
            [
                Card(Suits.DIAMONDS, Ranks.ACE),
                Card(Suits.SPADES, Ranks.FOUR),
                Card(Suits.DIAMONDS, Ranks.FIVE),
                Card(Suits.CLUBS, Ranks.ACE),
            ],
            Strains.DIAMONDS,
            0
    ),
    (
            [
                Card(Suits.SPADES, Ranks.FOUR),
                Card(Suits.DIAMONDS, Ranks.ACE),
                Card(Suits.DIAMONDS, Ranks.FIVE),
                Card(Suits.CLUBS, Ranks.ACE),
            ],
            Strains.DIAMONDS,
            1
    ),
    (
            [
                Card(Suits.SPADES, Ranks.FOUR),
                Card(Suits.DIAMONDS, Ranks.FIVE),
                Card(Suits.DIAMONDS, Ranks.ACE),
                Card(Suits.CLUBS, Ranks.ACE),
            ],
            Strains.DIAMONDS,
            2
    ),
    (
            [
                Card(Suits.CLUBS, Ranks.ACE),
                Card(Suits.SPADES, Ranks.FOUR),
                Card(Suits.DIAMONDS, Ranks.FIVE),
                Card(Suits.DIAMONDS, Ranks.ACE),
            ],
            Strains.DIAMONDS,
            3
    ),
    (
            [
                Card(Suits.CLUBS, Ranks.ACE),
                Card(Suits.SPADES, Ranks.FOUR),
                Card(Suits.DIAMONDS, Ranks.ACE),
                Card(Suits.DIAMONDS, Ranks.FIVE),
            ],
            Strains.DIAMONDS,
            2
    )
])
def test_determine_trick_winner(played_cards, trump_strain, expected):
    assert cardplay.determine_trick_winner(played_cards, trump_strain) == expected
