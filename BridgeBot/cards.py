import random
from BridgeBot.enums import INVALID, Suits, Ranks, ranks, suits

class InvalidCardException(Exception):
    pass

class InvalidRankException(InvalidCardException):
    pass

class InvalidSuitException(InvalidCardException):
    pass

class CardNotInHandException(Exception):
    pass

class CardDoesntFollowSuitException(Exception):
    pass

class Deck:
    def __init__(self):
        self.card_indices = list(range(52))

    def shuffle(self):
        for i in range(51, 0, -1):
            j = random.randint(0, i)  # So as not to bias certain permutations
            if j == i:
                continue
            self.card_indices[i], self.card_indices[j] = self.card_indices[j], self.card_indices[i]


class Card:
    def __init__(self, suit, rank):
        if suits.count(suit) == 0:
            raise InvalidSuitException("Suit not found")

        if ranks.count(rank) == 0:
            raise InvalidRankException("Rank not found")

        self.suit = suit
        self.rank = rank

        self.suit_index = suits.index(suit)
        self.rank_index = ranks.index(rank)

    # Mostly for assertions and error checking
    def does_not_match(self, other_card):
        if self.suit_index != other_card.suit_index:
            return False
        elif self.rank_index != other_card.rank_index:
            return False
        else:
            return True

class Card:
    def __init__(self, index):
        self.suit = suits[int(index / 13)]
        self.rank = ranks[index % 13]


class Hand:
    def __init__(self):
        self.hand = {
            Suits.SPADES: set(),
            Suits.HEARTS:  set(),
            Suits.DIAMONDS: set(),
            Suits.CLUBS: set()
        }

    def add_card(self, index):
        card = Card(index)
        if ranks.count(card.rank) == 0:
            raise InvalidCardException("Unknown Rank")
        self.hand[card.suit].add(card.rank)

    def play_card(self, suit, rank):
        if not rank in self.hand[suit]:
            raise CardNotInHandException("Hand does not contain " + rank.value + " of " + suit.value + ".")
        self.hand[suit].difference_update(rank)
        return Card(suit,rank)

    # Take a number from 0 to 51 and map it to suit and rank.
    def add_card_from_deck_index(self, index):
        self.add_card(index)

    # Take a list of numbers from 0 to 51 and map them to suits and ranks.
    def fill_from_list(self, deck_indices):
        for idx in deck_indices:
            self.add_card_from_deck_index(idx)



class BridgeHand(Hand):
    def __init__(self, deck_indices):
        super().__init__()
        if len(deck_indices) != 13:
            raise Exception("Bridge hands must contain 13 cards.")
        self.fill_from_list(deck_indices)

    def __check_input(self, suit, rank):
        if not isinstance(rank, Ranks):
            raise InvalidRankException("Rank not found")

        if not isinstance(suit, Suits):
            raise InvalidSuitException("Suit not found")

    def lead(self, suit, rank):
        self.__check_input(suit, rank)

        return self.play_card(suit,rank)

    def follow(self, led, suit, rank):
        self.__check_input(suit, rank)

        if suit != led[suit]:
            if len(self.hand[suit]) != 0:
                raise CardDoesntFollowSuitException("Must follow suit if possible.")
            else:
                return self.play_card(suit,rank)
