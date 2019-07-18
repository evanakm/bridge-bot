from enum import Enum


class Players(Enum):
    NORTH = "NORTH"
    EAST = "EAST"
    SOUTH = "SOUTH"
    WEST = "WEST"

    def players(self):
        return [self.NORTH, self.EAST, self.SOUTH, self.WEST]

    def next_player(self):
        players = self.players()
        return players[(players.index(self) + 1) % 4]

    def partner(self):
        players = self.players()
        return players[(players.index(self) + 2) % 4]


class Suits(Enum):
    CLUBS = "CLUBS"
    DIAMONDS = "DIAMONDS"
    HEARTS = "HEARTS"
    SPADES = "SPADES"

    def suits(self):
        return [self.CLUBS, self.DIAMONDS, self.HEARTS, self.SPADES]

    def __lt__(self, other):
        suits = self.suits()
        return suits.index(self) < suits.index(other)

suits = [Suits.CLUBS, Suits.DIAMONDS, Suits.HEARTS, Suits.SPADES]

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

    def strains(self):
        return [self.CLUBS, self.DIAMONDS, self.HEARTS, self.SPADES, self.NT, self.PASSOUT]

    def __lt__(self, other):
        strains = self.strains()
        return strains.index(self) < strains.index(other)


PASS = 'PASS'


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

    def __lt__(self, other):
        ranks = [self.TWO, self.THREE, self.FOUR, self.FIVE, self.SIX, self.SEVEN, self.EIGHT, self.NINE,
                 self.TEN, self.JACK, self.QUEEN, self.KING, self.ACE]
        return ranks.index(self) < ranks.index(other)

ranks = [Ranks.TWO, Ranks.THREE, Ranks.FOUR, Ranks.FIVE, Ranks.SIX, Ranks.SEVEN, Ranks.EIGHT, Ranks.NINE, Ranks.TEN,
         Ranks.JACK, Ranks.QUEEN, Ranks.KING, Ranks.ACE]

contracts = ['1C',' 1D', '1H', '1S', '1N',
        '2C', '2D', '2H', '2S', '2N',
        '3C', '3D', '3H', '3S', '3N',
        '4C', '4D', '4H', '4S', '4N',
        '5C', '5D', '5H', '5S', '5N',
        '6C', '6D', '6H', '6S', '6N',
        '7C', '7D', '7H', '7S', '7N']