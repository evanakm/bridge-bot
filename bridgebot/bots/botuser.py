from game.interface import User
import torch
from game.enums import Players
from game.card import Card, Suits, Ranks


def player_to_tensor(player):
    if not isinstance(player, Players):
        raise TypeError("player is not of type Player")

    return torch.tensor(Players.players().index(player))


def cards_to_tensor(cards):
    card_tensor = torch.zeros(
        52,
        dtype=torch.long
    )

    if not isinstance(cards, list) and not isinstance(cards, set):
        raise TypeError("cards must be a list of set")

    for card in cards:
        if not isinstance(card, Card):
            raise TypeError("cards must be a list of set")

        card_tensor[card.to_int()] = 1

    return card_tensor


def card_history_to_tensor(card_history):
    for key, val in card_history.items():
        print(key, val)


class BotUser(User):
    @staticmethod
    def play_card_from_own_hand(current_player, dummy, dummy_hand, all_cards, legal_cards, bid_history, card_history, leader_history):
        pass


if __name__ == "__main__":
    print(player_to_tensor(Players.SOUTH))
    print(cards_to_tensor([Card(Suits.SPADES, Ranks.EIGHT)]))
