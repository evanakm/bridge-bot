from enum import Enum


class Players(Enum):
    NORTH = "NORTH"
    EAST = "EAST"
    SOUTH = "SOUTH"
    WEST = "WEST"


class Suits(Enum):
    CLUBS = "CLUBS"
    DIAMONDS = "DIAMONDS"
    HEARTS = "HEARTS"
    SPADES = "SPADES"


class Vulnerabilities(Enum):
    NONE = 'NONE'
    NS = 'NS'
    EW = 'EW'
    BOTH = 'BOTH'


INVALID = "INVALID"

players = [Players.NORTH, Players.EAST, Players.SOUTH, Players.WEST]

class Strains(Enum):
    CLUBS = "CLUBS"
    DIAMONDS = "DIAMONDS"
    HEARTS = "HEARTS"
    SPADES = "SPADES"
    NT = "NT"
    PASSOUT = "PASSOUT"


strains = [Strains.CLUBS, Strains.DIAMONDS, Strains.HEARTS, Strains.SPADES, Strains.NT, Strains.PASSOUT]

PASS = 'PASS'

suits = [Suits.CLUBS, Suits.DIAMONDS, Suits.HEARTS, Suits.SPADES]
suits_short = {Suits.CLUBS: "C", Suits.DIAMONDS: "D", Suits.HEARTS: "H", Suits.SPADES: "S"}


class Ranks(Enum):
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "10"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"
    ACE = "A"

ranks = [Ranks.TWO, Ranks.THREE, Ranks.FOUR, Ranks.FIVE, Ranks.SIX, Ranks.SEVEN, Ranks.EIGHT, Ranks.NINE, Ranks.TEN,
         Ranks.JACK, Ranks.QUEEN, Ranks.KING, Ranks.ACE]

contracts = ['1C',' 1D', '1H', '1S', '1N',
        '2C', '2D', '2H', '2S', '2N',
        '3C', '3D', '3H', '3S', '3N',
        '4C', '4D', '4H', '4S', '4N',
        '5C', '5D', '5H', '5S', '5N',
        '6C', '6D', '6H', '6S', '6N',
        '7C', '7D', '7H', '7S', '7N']