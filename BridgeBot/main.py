from cards import Deck, Card, BridgeHand, suits, ranks
from bidding import Auction, strains
from cardplay import Cardplay, contracts
from scoring import score
from deal import Deal

from enums import Players, Vulnerabilities

hand_names = [Players.NORTH, Players.SOUTH, Players.EAST, Players.WEST]


if __name__ == "__main__":
    deck = Deck()
    deal = Deal(Players.NORTH, Vulnerabilities.NONE)
