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
        if other is None:
            return False
        return self.suit == other.suit and self.rank == other.rank

    def __hash__(self):
        return hash(self.suit.name + " " + self.rank.name)

    def __lt__(self, other):
        if self.suit != other.suit:
            return Suits.suits().index(self.suit) < Suits.suits().index(other.suit)
        return Ranks.ranks().index(self.rank) < Ranks.ranks().index(other.rank)

    def __str__(self):
        return self.rank.name + "_" + self.suit.name
