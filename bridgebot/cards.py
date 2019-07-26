import random

from enums import Suits, Ranks

from card import Card


class CardDoesntFollowSuitException(Exception):
    pass


class WrongSizeHandException(Exception):
    pass


class DeckListNotValid(Exception):
    pass


class BridgeHand:
    def get_cards_of_suit(self, suit):
        if not isinstance(suit, Suits):
            raise TypeError("suit is not of type Suits")

        return set(card for card in self.cards if card.suit == suit)

    @staticmethod
    def __add_cards_to_bridge_hand(bridge_hand, cards):
        if not isinstance(cards, list):
            raise DeckListNotValid("deck_indices is not a list")

        if len(cards) > 13:
            raise WrongSizeHandException("Bridge hands must contain 13 cards.")

        for card in cards:
            bridge_hand.__add_card(card)

        return bridge_hand

    @staticmethod
    def generate_complete_hand(cards):
        if len(cards) != 13:
            raise WrongSizeHandException("cards must contain 13 cards")
        for card in cards:
            if not isinstance(card, Card):
                raise TypeError("card is not of type Card")
        return BridgeHand(cards)

    def __init__(self, cards):
        if not isinstance(cards, list):
            raise DeckListNotValid("cards is not a list")

        self.cards = set(cards)
        if len(cards) > 13:
            raise WrongSizeHandException("cards must contain 13 cards or less")

        BridgeHand.__add_cards_to_bridge_hand(self, cards)

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
        if not isinstance(card, Card):
            raise TypeError("card is not of type Card")

        return card in self.cards

    def __play_card(self, card):
        if not isinstance(card, Card):
            raise TypeError("card is not of type Card")

        if not self.contains_card(card):
            raise CardNotInHandException("Hand does not contain " + card.rank.name + " of " + card.suit.name + ".")
        self.cards.remove(card)

    def __add_card(self, card):
        if not isinstance(card, Card):
            raise TypeError("card is not of type Card")
        self.cards.add(card)

    def lead(self, card):
        """
        Parameters
        ----------
        card: Card
            The Card that was played
        """
        if not isinstance(card, Card):
            raise TypeError("card is not of type Card")

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
            raise TypeError("led_suit is not of type Suits")

        if not isinstance(card_played, Card):
            raise TypeError("card_played is not of type Card")

        if card_played.suit != led_suit:
            if len(self.get_cards_of_suit(led_suit)) != 0:
                raise CardDoesntFollowSuitException("Must follow suit if possible.")
            else:
                self.__play_card(card_played)
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
            raise InvalidSuitException("Invalid Suit")

        if not led_suit:
            return self.cards

        cards_of_lead_suit = self.get_cards_of_suit(led_suit)

        if len(cards_of_lead_suit) is not 0:
            return cards_of_lead_suit
        else:
            return self.cards
