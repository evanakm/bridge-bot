from bridgebot.game.card import Card
from bridgebot.game.enums import Players
from bridgebot.game.interface import User

try:
    import tensorflow as tf
except ModuleNotFoundError:
    tf = None


def player_to_tensor(player):
    if not isinstance(player, Players):
        raise TypeError("player is not of type Player")

    player_index = Players.players().index(player)
    if tf is None:
        return player_index
    return tf.constant(player_index, dtype=tf.dtypes.int32)


def _to_tensor(values):
    if tf is None:
        return values
    return tf.constant(values, dtype=tf.dtypes.float32)


def _cards_to_values(cards):
    values = [0.0] * 52
    for card in cards:
        if not isinstance(card, Card):
            raise TypeError("cards must contain only Card values")
        values[card.to_int()] = 1.0
    return values


def cards_to_tensor(cards):
    if not isinstance(cards, (list, set, tuple)):
        raise TypeError("cards must be a list, set, or tuple")

    return _to_tensor(_cards_to_values(cards))


def card_history_to_tensor(card_history):
    if not isinstance(card_history, dict):
        raise TypeError("card_history must be a dict")

    values = []
    for player in Players.players():
        if player not in card_history:
            raise KeyError(player)
        values.extend(_cards_to_values(card_history[player]))

    return _to_tensor(values)


class BotUser(User):
    @staticmethod
    def play_card(current_player, dummy, dummy_hand, all_cards, legal_cards, bid_history, card_history, leader_history):
        if len(legal_cards) == 0:
            raise ValueError("legal_cards must not be empty")
        return sorted(legal_cards)[0]

    @staticmethod
    def bid(current_player, legal_bids, bid_history):
        if len(legal_bids) == 0:
            raise ValueError("legal_bids must not be empty")

        for bid in legal_bids:
            if bid.name == "PASS":
                return bid

        return legal_bids[0]
