from game.get_input import get_input_card, get_input_list
from abc import abstractmethod
from game.enums import Suits

class User:
    @staticmethod
    @abstractmethod
    def play_card(current_player, dummy, dummy_hand, all_cards, legal_cards, bid_history, card_history, leader_history):
        pass

    @staticmethod
    @abstractmethod
    def make_bid(record, legal_bids):
        pass

    @staticmethod
    def _convert_hand_to_str(cards):
        card_string = ""
        for card in sorted(cards):
            card_string += str(card) + " "
        return card_string

    @staticmethod
    def _beautify_hand(cards):
        res = ""

        for suit in Suits.suits():
            cards_in_suit = [card for card in cards if card.suit == suit]

            if len(cards_in_suit) ==  0:
                res = res + "--"
            else:
                for card in cards_in_suit:
                    res = res + str(card).ljust(20)

            res = res + "\n"

        return res


class HumanUser(User):
    @staticmethod
    def play_card(current_player, dummy, dummy_hand, all_cards, legal_cards, bid_history, card_history, leader_history):
        #print("Dummy: \n" + User._convert_hand_to_str(dummy_hand))
        print("Dummy: \n" + User._beautify_hand(dummy_hand))
        print("All Cards: \n" +
              #User._convert_hand_to_str(all_cards)
              User._beautify_hand(all_cards)
              )
        print("Legal Cards: \n" +
              #User._convert_hand_to_str(legal_cards)
              User._beautify_hand(legal_cards)
              )

        return get_input_card(legal_cards)

    @staticmethod
    def make_bid(record, legal_bids):
        print("Record: " + str(record)) # TODO stringify record
        print("Legal Bids: " + str(legal_bids))
        return get_input_list(legal_bids, "bid")

