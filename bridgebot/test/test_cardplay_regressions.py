from bridgebot.game import cardplay
from bridgebot.game.bridgehand import Card
from bridgebot.game.enums import Ranks, Strains, Suits


def test_trump_cannot_be_beaten_by_later_led_suit_card():
    played_cards = [
        Card(Suits.SPADES, Ranks.TWO),
        Card(Suits.HEARTS, Ranks.THREE),
        Card(Suits.SPADES, Ranks.ACE),
        Card(Suits.CLUBS, Ranks.TWO),
    ]

    assert cardplay.determine_trick_winner(played_cards, Strains.HEARTS) == 1


def test_no_trump_highest_led_suit_card_wins():
    played_cards = [
        Card(Suits.SPADES, Ranks.TWO),
        Card(Suits.HEARTS, Ranks.ACE),
        Card(Suits.SPADES, Ranks.ACE),
        Card(Suits.CLUBS, Ranks.KING),
    ]

    assert cardplay.determine_trick_winner(played_cards, Strains.NT) == 2
