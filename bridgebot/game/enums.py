from __future__ import annotations
from enum import Enum

from typing import List, Union, Set


class InvalidPlayerException(Exception):
    pass


# This is a constant. Do not change it! Bridge has 13 tricks!
NUMBER_OF_TRICKS = 13


class Players(Enum):
    NORTH = "NORTH"
    EAST = "EAST"
    SOUTH = "SOUTH"
    WEST = "WEST"

    @staticmethod
    def players() -> List[Players]:
        return [Players.NORTH, Players.EAST, Players.SOUTH, Players.WEST]

    def next_player(self) -> Players:
        players = self.players()
        return players[(players.index(self) + 1) % 4]

    def determine_nth_player_to_the_right(self, steps: int) -> Players:
        """
        Determine the nth player to the right of self

        Parameters
        ----------
        steps: int
            The number of steps to look to the right (0 to 3 inclusive)

        Returns
        -------
        nth_player: Players
            The nth player to the right

        """
        players = self.players()
        return players[(players.index(self) + steps) % 4]

    def partner(self) -> Players:
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
    TWO_CLUBS = "2C"
    TWO_DIAMONDS = "2D"
    TWO_HEARTS = "2H"
    TWO_SPADES = "2S"
    TWO_NO_TRUMP = "2N"
    THREE_CLUBS = "3C"
    THREE_DIAMONDS = "3D"
    THREE_HEARTS = "3H"
    THREE_SPADES = "3S"
    THREE_NO_TRUMP = "3N"
    FOUR_CLUBS = "4C"
    FOUR_DIAMONDS = "4D"
    FOUR_HEARTS = "4H"
    FOUR_SPADES = "4S"
    FOUR_NO_TRUMP = "4N"
    FIVE_CLUBS = "5C"
    FIVE_DIAMONDS = "5D"
    FIVE_HEARTS = "5H"
    FIVE_SPADES = "5S"
    FIVE_NO_TRUMP = "5N"
    SIX_CLUBS = "6C"
    SIX_DIAMONDS = "6D"
    SIX_HEARTS = "6H"
    SIX_SPADES = "6S"
    SIX_NO_TRUMP = "6N"
    SEVEN_CLUBS = "7C"
    SEVEN_DIAMONDS = "7D"
    SEVEN_HEARTS = "7H"
    SEVEN_SPADES = "7S"
    SEVEN_NO_TRUMP = "7N"

    @staticmethod
    def contracts() -> List[Contracts]:
        return [
            Contracts.ONE_CLUB,    Contracts.ONE_DIAMOND,    Contracts.ONE_HEART,    Contracts.ONE_SPADE,    Contracts.ONE_NO_TRUMP,
            Contracts.TWO_CLUBS,   Contracts.TWO_DIAMONDS,   Contracts.TWO_HEARTS,   Contracts.TWO_SPADES,   Contracts.TWO_NO_TRUMP,
            Contracts.THREE_CLUBS, Contracts.THREE_DIAMONDS, Contracts.THREE_HEARTS, Contracts.THREE_SPADES, Contracts.THREE_NO_TRUMP,
            Contracts.FOUR_CLUBS,  Contracts.FOUR_DIAMONDS,  Contracts.FOUR_HEARTS,  Contracts.FOUR_SPADES,  Contracts.FOUR_NO_TRUMP,
            Contracts.FIVE_CLUBS,  Contracts.FIVE_DIAMONDS,  Contracts.FIVE_HEARTS,  Contracts.FIVE_SPADES,  Contracts.FIVE_NO_TRUMP,
            Contracts.SIX_CLUBS,   Contracts.SIX_DIAMONDS,   Contracts.SIX_HEARTS,   Contracts.SIX_SPADES,   Contracts.SIX_NO_TRUMP,
            Contracts.SEVEN_CLUBS, Contracts.SEVEN_DIAMONDS, Contracts.SEVEN_HEARTS, Contracts.SEVEN_SPADES, Contracts.SEVEN_NO_TRUMP,
        ]

    @staticmethod
    def __determine_level_from_contract(contract: Contracts) -> int:
        contracts = Contracts.contracts()
        return 1 + int(contracts.index(contract) / 5) #Add one since indexing starts from zero

    @staticmethod
    def __determine_strain_from_contract(contract: Contracts) -> Strains:
        if not isinstance(contract, Contracts):
            raise TypeError("contract is not of type Contracts")

        contracts = Contracts.contracts()
        strains = Strains.strains()
        return strains[contracts.index(contract) % 5]

    def determine_strain(self) -> Strains:
        return Contracts.__determine_strain_from_contract(self)

    def determine_level(self) -> int:
        return Contracts.__determine_level_from_contract(self)

    def __lt__(self, other: Union[Contracts, None]):
        if other is None:
            return False

        contracts = self.contracts()
        return contracts.index(self) < contracts.index(other)


class Suits(Enum):
    CLUBS = "CLUBS"
    DIAMONDS = "DIAMONDS"
    HEARTS = "HEARTS"
    SPADES = "SPADES"

    @staticmethod
    def suits() -> List[Suits]:
        return [Suits.CLUBS, Suits.DIAMONDS, Suits.HEARTS, Suits.SPADES]

    def __lt__(self, other: Suits) -> bool:
        suits = self.suits()
        return suits.index(self) < suits.index(other)

    @staticmethod
    def determine_suit_from_contract(contract: Contracts) -> Suits:
        if not isinstance(contract, Contracts):
            raise ContractNotFound("Invalid Contract")

        return Suits.suits()[Contracts.contracts().index(contract) % 5]


class InvalidTeam(Exception):
    pass


class Team(Enum):
    NS = 'NS'
    EW = 'EW'

    @staticmethod
    def team_to_set_of_players(team: Team) -> Set[Players]:
        if not isinstance(team, Team):
            raise InvalidTeam("Invalid Team")
        if team == Team.NS:
            return {Players.NORTH, Players.SOUTH}
        if team == Team.EW:
            return {Players.EAST, Players.WEST}
        raise InvalidTeam("Invalid Team")

    @staticmethod
    def player_to_team(player: Players) -> Team:
        if not isinstance(player, Players):
            raise InvalidPlayerException("Invalid Player")
        if player == Players.NORTH or player == Players.SOUTH:
            return Team.NS
        else:
            return Team.EW

    def to_set_of_players(self) -> Set[Players]:
        return Team.team_to_set_of_players(self)

    def is_player_in_team(self, player: Players) -> bool:
        if not isinstance(player, Players):
            raise InvalidPlayerException("Invalid Player")
        return player in self.to_set_of_players()


class Vulnerabilities(Enum):
    NONE = 'NONE'
    NS = 'NS'
    EW = 'EW'
    BOTH = 'BOTH'

    def is_declarer_vulnerable(self, declarer: Players) -> bool:
        if not isinstance(declarer, Players):
            raise InvalidPlayerException("Invalid Declarer")

        if self == Vulnerabilities.NONE:
            return False
        elif self == Vulnerabilities.BOTH:
            return True
        elif self == Vulnerabilities.NS:
            return declarer == Players.NORTH or declarer == Players.SOUTH
        else:
            return declarer == Players.EAST or declarer == Players.WEST


class InvalidSuitOrStrainException(Exception):
    pass


class InvalidStrainException(Exception):
    pass


class Strains(Enum):
    CLUBS = "CLUBS"
    DIAMONDS = "DIAMONDS"
    HEARTS = "HEARTS"
    SPADES = "SPADES"
    NT = "NT"
    PASSOUT = "PASSOUT" #Including this as a strain is somewhat of a ninja fix

    @staticmethod
    def strains() -> List[Strains]:
        return [Strains.CLUBS, Strains.DIAMONDS, Strains.HEARTS, Strains.SPADES, Strains.NT, Strains.PASSOUT]

    def __lt__(self, other: Strains) -> bool:
        strains = self.strains()
        return strains.index(self) < strains.index(other)

    def determine_suit(self) -> Suits:
        if self == Strains.CLUBS:
            return Suits.CLUBS
        elif self == Strains.DIAMONDS:
            return Suits.DIAMONDS
        elif self == Strains.HEARTS:
            return Suits.HEARTS
        elif self == Strains.SPADES:
            return Suits.SPADES
        return None

    def compare_to_suit(self, suit: Suits) -> bool:
        if not isinstance(suit, Suits):
            raise InvalidSuitOrStrainException("Invalid Suit")
        else:
            strains = self.strains()
            suits = Suits.suits()
            # If No_Trump, this will be False because strain index will be 4, and suit index will be 0, 1, 2, or 3
            return strains.index(self) == suits.index(suit)


class Pass(Enum):
    PASS = 'P'


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
    def ranks() -> List[Ranks]:
        return [Ranks.TWO, Ranks.THREE, Ranks.FOUR, Ranks.FIVE, Ranks.SIX, Ranks.SEVEN, Ranks.EIGHT, Ranks.NINE,
                Ranks.TEN, Ranks.JACK, Ranks.QUEEN, Ranks.KING, Ranks.ACE]

    def __lt__(self, other: Ranks) -> bool:
        ranks = self.ranks()
        return ranks.index(self) < ranks.index(other)


class InvalidDoublesException(Exception):
    pass


class Doubles(Enum):
    NONE = "NONE"
    DOUBLE = "X"
    REDOUBLE = "XX"


class AuctionStatus(Enum):
    DONE = "DONE"
    CONTINUE = "CONTINUE"
    INVALID = "INVALID"

