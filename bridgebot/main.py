from deck import Deck

from enums import Players, Contracts
import cardplay
from get_input import get_input_enum

if __name__ == "__main__":
    deck = Deck()
    deck.shuffle()

    contract = get_input_enum(Contracts, "contract")

    declarer = get_input_enum(Players, "declarer")

    trick_winners = cardplay.play(deck.deal(), contract, declarer)
