from interface import User
import tensorflow as tf
from enums import Players
from card import Card


def player_to_tensor(player):
    if not isinstance(player, Players):
        raise TypeError("player is not of type Player")

    return tf.Variable(Players.players().index(player))


def cards_to_tensor(cards):
    card_tensor = tf.zeros(
        [52],
        dtype=tf.dtypes.float32,
        name=None
    )

    if not isinstance(cards, list) or not isinstance(cards, set):
        raise TypeError("cards must be a list of set")

    for card in cards:
        if not isinstance(card, Card):
            raise TypeError("cards must be a list of set")

        card_tensor[card.to_int()] = 1

    return card_tensor


def card_history_to_tensor(card_history):
    for key, val in card_history.items():
        card_history

def leader_history_to_tensor(leader_history):



class BotUser(User):
    @staticmethod
    def play_card(current_player, dummy, dummy_hand, all_cards, legal_cards, bid_history, card_history, leader_history):
            current_player
        pass