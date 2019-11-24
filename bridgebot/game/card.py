from game.enums import Suits, Ranks


class InvalidCardException(Exception):
    pass


class InvalidRankException(InvalidCardException):
    pass


class InvalidSuitException(InvalidCardException):
    pass


class Card:
    def __init__(self, suit, rank):
        if not isinstance(suit, Suits):
            raise InvalidSuitException

        if not isinstance(rank, Ranks):
            raise InvalidRankException

        self.suit = suit
        self.rank = rank

    def __eq__(self, other):
        if other is None:
            return False
        return self.suit == other.suit and self.rank == other.rank

    # Makes suit and rank a unique identifier
    def __hash__(self):
        return hash(self.suit.name + " " + self.rank.name)

    def __lt__(self, other):
        if self.suit != other.suit:
            return Suits.suits().index(self.suit) < Suits.suits().index(other.suit)
        return Ranks.ranks().index(self.rank) < Ranks.ranks().index(other.rank)

    def __str__(self):
        return self.rank.name + "_" + self.suit.name

    def to_int(self):
        return Ranks.ranks().index(self.rank) + Suits.suits().index(self.suit) * 13