import random

from enums import Suits, Ranks


class InvalidCardException(Exception):
    pass


class InvalidRankException(InvalidCardException):
    pass


class InvalidSuitException(InvalidCardException):
    pass


class InvalidIndexException(Exception):
    pass


class CardNotInHandException(Exception):
    pass


class CardDoesntFollowSuitException(Exception):
    pass


class WrongSizeHandException(Exception):
    pass


class Card:
    @staticmethod
    def generate_card_from_index(index):
        if index not in range(52):
            raise InvalidIndexException("Index must be an integer between 0 and 51 inclusive.")
        return Card(Suits.suits()[int(index / 13)], Ranks.ranks()[index % 13])

    def __init__(self, suit, rank):
        if not isinstance(suit, Suits):
            raise InvalidSuitException("Suit not found")

        if not isinstance(rank, Ranks):
            raise InvalidRankException("Rank not found")

        self.suit = suit
        self.rank = rank

    def __eq__(self, other):
        return self.suit == other.suit and self.rank == other.rank


class DeckListNotValid(Exception):
    pass


class BridgeHand:
    def __init__(self, deck_indices):
        self.hand = {
            Suits.SPADES: set(),
            Suits.HEARTS:  set(),
            Suits.DIAMONDS: set(),
            Suits.CLUBS: set()
        }

        if len(deck_indices) != 13:
            raise WrongSizeHandException("Bridge hands must contain 13 cards.")

        if not isinstance(deck_indices, list):
            raise DeckListNotValid("deck_indices is not a list")

        for index in deck_indices:
            card = Card.generate_card_from_index(index)
            self.__add_card(card)

    @staticmethod
    def __check_input(card):
        if not isinstance(card.suit, Suits):
            raise InvalidSuitException("Suit not found")

        if not isinstance(card.rank, Ranks):
            raise InvalidRankException("Rank not found")

    def contains_card(self, card):
        """
        Returns if a card is in the hand or not

        Parameters
        ----------
        card: Card
            The card to be checked

        Returns
        -------
        card_in_hand: bool
            Whether the card is in the hand or not

        """
        self.__check_input(card)
        return card.rank in self.hand[card.suit]

    def __play_card(self, card):
        self.__check_input(card)
        if not self.contains_card(card):
            raise CardNotInHandException("Hand does not contain " + card.rank.name + " of " + card.suit.name + ".")
        self.hand[card.suit].difference_update([card.rank])

    def __add_card(self, card):
        if not isinstance(card, Card):
            raise InvalidCardException("Invalid Card")
        self.hand[card.suit].add(card.rank)

    def lead(self, card):
        """
        Parameters
        ----------
        card: Card
            The Card that was played
        """
        self.__check_input(card)

        if not self.contains_card(card):
            raise CardNotInHandException("Hand does not contain " + card.rank.name + " of " + card.suit.name + ".")

        self.__play_card(card)

    def follow(self, led_suit, card_played):
        """
        Parameters
        ----------
        led_suit: Suits
            A suit representing the first card played to the trick
        card_played: Card
            The Card that was played
        """

        if not isinstance(led_suit, Suits):
            raise InvalidSuitException("Invalid trump_suit")

        self.__check_input(card_played)

        if card_played.suit != led_suit:
            if len(self.hand[led_suit]) != 0:
                raise CardDoesntFollowSuitException("Must follow suit if possible.")
            else:
                self.__play_card(card_played)

    def legal_cards(self, led_suit=None):
        """
        Get a list of all of a players playable cards.

        Parameters
        ----------
        led_suit: Suits or None
            The suit lead

        Returns
        -------
        playable_cards: list of Card
            A list of all of the playable cards
        """
        print(led_suit)
        if not (led_suit is None or isinstance(led_suit, Suits)):
            raise InvalidRankException("Invalid Rank")

        if not led_suit and len(self.hand[led_suit]) is not 0:
            return {led_suit: self.hand[led_suit]}
        else:
            return self.hand
