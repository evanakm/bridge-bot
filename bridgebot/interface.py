from get_input import get_input_enum, get_input_card
from abc import abstractmethod


class User:
    @staticmethod
    @abstractmethod
    def play_card(all_cards, legal_cards, bid_history, card_history, leader_history):
        pass

    @staticmethod
    def _convert_hand_to_str(cards):
        card_string = ""
        for card in sorted(cards):
            card_string += str(card) + " "
        return card_string


class HumanUser(User):
    @staticmethod
    def play_card(all_cards, legal_cards, bid_history, card_history, leader_history):
        print("All Cards: " +
              User._convert_hand_to_str(all_cards)
              )
        if set(all_cards) != set(legal_cards):
            print("Legal Cards: " +
                  User._convert_hand_to_str(legal_cards)
                  )

        return get_input_card(legal_cards)



