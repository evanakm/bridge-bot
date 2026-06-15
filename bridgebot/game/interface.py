from bridgebot.game.get_input import get_input_card
from abc import abstractmethod


class User:
    @staticmethod
    @abstractmethod
    def play_card(current_player, dummy, dummy_hand, all_cards, legal_cards, bid_history, card_history, leader_history):
        pass

    @staticmethod
    @abstractmethod
    def bid(current_player, legal_bids, bid_history):
        pass

    @staticmethod
    def _convert_hand_to_str(cards):
        card_string = ""
        for card in sorted(cards):
            card_string += str(card) + " "
        return card_string


class HumanUser(User):
    @staticmethod
    def play_card(current_player, dummy, dummy_hand, all_cards, legal_cards, bid_history, card_history, leader_history):
        print("Dummy: " + User._convert_hand_to_str(dummy_hand))
        print("All Cards: " +
              User._convert_hand_to_str(all_cards)
              )
        if set(all_cards) != set(legal_cards):
            print("Legal Cards: " +
                  User._convert_hand_to_str(legal_cards)
                  )

        return get_input_card(legal_cards)

    @staticmethod
    def bid(current_player, legal_bids, bid_history):
        from bridgebot.game.get_input import get_input_list

        return get_input_list(legal_bids, "bid")


