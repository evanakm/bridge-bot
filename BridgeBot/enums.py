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

