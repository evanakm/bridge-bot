from enums import Suits, Ranks


class InvalidCardException(Exception):
    pass


class InvalidRankException(InvalidCardException):
    pass


class InvalidSuitException(InvalidCardException):
    pass


class Card:
    def __init__(self, suit, rank):
        if not isinstance(suit, Suits):
            raise TypeError("suit is not of type Suits")

        if not isinstance(rank, Ranks):
            raise TypeError("rank is not of type Ranks")

        self.suit = suit
        self.rank = rank

    def __eq__(self, other):
        return self.suit == other.suit and self.rank == other.rank
