from enum import Enum


class Players(Enum):
    NORTH = "NORTH"
    EAST = "EAST"
    SOUTH = "SOUTH"
    WEST = "WEST"

    @staticmethod
    def players():
        return [Players.NORTH, Players.EAST, Players.SOUTH, Players.WEST]

    def next_player(self):
        players = self.players()
        return players[(players.index(self) + 1) % 4]

    def partner(self):
        players = self.players()
        return players[(players.index(self) + 2) % 4]

class ContractNotFound(Exception):
    pass

class Contracts(Enum):
    ONE_CLUB = "1C"
    ONE_DIAMOND = "1D"
    ONE_HEART = "1H"
    ONE_SPADE = "1S"
    ONE_NO_TRUMP = "1N"

    TWO_CLUBS = "1C"
    TWO_DIAMONDS = "1D"
    TWO_HEARTS = "1H"
    TWO_SPADES = "1S"
    TWO_NO_TRUMP = "1N"

    THREE_CLUBS = "1C"
    THREE_DIAMONDS = "1D"
    THREE_HEARTS = "1H"
    THREE_SPADES = "1S"
    THREE_NO_TRUMP = "1N"

    FOUR_CLUBS = "1C"
    FOUR_DIAMONDS = "1D"
    FOUR_HEARTS = "1H"
    FOUR_SPADES = "1S"
    FOUR_NO_TRUMP = "1N"

    FIVE_CLUBS = "1C"
    FIVE_DIAMONDS = "1D"
    FIVE_HEARTS = "1H"
    FIVE_SPADES = "1S"
    FIVE_NO_TRUMP = "1N"

    SIX_CLUBS = "1C"
    SIX_DIAMONDS = "1D"
    SIX_HEARTS = "1H"
    SIX_SPADES = "1S"
    SIX_NO_TRUMP = "1N"

    SEVEN_CLUBS = "1C"
    SEVEN_DIAMONDS = "1D"
    SEVEN_HEARTS = "1H"
    SEVEN_SPADES = "1S"
    SEVEN_NO_TRUMP = "1N"

    @staticmethod
    def contracts():
        return [
            Contracts.ONE_CLUB,    Contracts.ONE_DIAMOND,    Contracts.ONE_HEART,    Contracts.ONE_SPADE,    Contracts.ONE_NO_TRUMP,
            Contracts.TWO_CLUBS,   Contracts.TWO_DIAMONDS,   Contracts.TWO_HEARTS,   Contracts.TWO_SPADES,   Contracts.TWO_NO_TRUMP,
            Contracts.THREE_CLUBS, Contracts.THREE_DIAMONDS, Contracts.THREE_HEARTS, Contracts.THREE_SPADES, Contracts.THREE_NO_TRUMP,
            Contracts.FOUR_CLUBS,  Contracts.FOUR_DIAMONDS,  Contracts.FOUR_HEARTS,  Contracts.FOUR_SPADES,  Contracts.FOUR_NO_TRUMP,
            Contracts.FIVE_CLUBS,  Contracts.FIVE_DIAMONDS,  Contracts.FIVE_HEARTS,  Contracts.FIVE_SPADES,  Contracts.FIVE_NO_TRUMP,
            Contracts.SIX_CLUBS,   Contracts.SIX_DIAMONDS,   Contracts.SIX_HEARTS,   Contracts.SIX_SPADES,   Contracts.SIX_NO_TRUMP,
            Contracts.SEVEN_CLUBS, Contracts.SEVEN_DIAMONDS, Contracts.SEVEN_HEARTS, Contracts.SEVEN_SPADES, Contracts.SEVEN_NO_TRUMP,
        ]

class Suits(Enum):
    CLUBS = "CLUBS"
    DIAMONDS = "DIAMONDS"
    HEARTS = "HEARTS"
    SPADES = "SPADES"

    @staticmethod
    def suits():
        return [Suits.CLUBS, Suits.DIAMONDS, Suits.HEARTS, Suits.SPADES]

    def __lt__(self, other):
        suits = self.suits()
        return suits.index(self) < suits.index(other)


    @staticmethod
    def determine_suit_from_contract(contract):
        if not isinstance(contract, Contracts):
            raise ContractNotFound("Invalid Contract")

        return Suits.suits()[Contracts.contracts().index(contract) % 5]

class Vulnerabilities(Enum):
    NONE = 'NONE'
    NS = 'NS'
    EW = 'EW'
    BOTH = 'BOTH'


class Status(Enum):
    INVALID = "INVALID"
    VALID = "VALID"


class Strains(Enum):
    CLUBS = "CLUBS"
    DIAMONDS = "DIAMONDS"
    HEARTS = "HEARTS"
    SPADES = "SPADES"
    NT = "NT"
    PASSOUT = "PASSOUT"

    @staticmethod
    def strains():
        return [Strains.CLUBS, Strains.DIAMONDS, Strains.HEARTS, Strains.SPADES, Strains.NT, Strains.PASSOUT]

    def __lt__(self, other):
        strains = self.strains()
        return strains.index(self) < strains.index(other)

    @staticmethod
    def determine_strain_from_contract(contract):
        if not isinstance(contract, Contracts):
            raise ContractNotFound("Invalid Contract")

        return Strains.strains()[Contracts.contracts().index(contract) % 5]



PASS = 'PASS'

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

    @staticmethod
    def ranks():
        return [Ranks.TWO, Ranks.THREE, Ranks.FOUR, Ranks.FIVE, Ranks.SIX, Ranks.SEVEN, Ranks.EIGHT, Ranks.NINE,
                Ranks.TEN, Ranks.JACK, Ranks.QUEEN, Ranks.KING, Ranks.ACE]

    def __lt__(self, other):
        ranks = self.ranks()
        return ranks.index(self) < ranks.index(other)





class Doubles(Enum):
    NONE = "NONE"
    DOUBLE = "X"
    DOUBLE_DOWN = "XX"

class AuctionStatus(Enum):
    DONE = "DONE"
    CONTINUE = "CONTINUE"
    INVALID = "INVALID"

