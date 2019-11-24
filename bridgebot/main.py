from game.deck import Deck

from game.enums import Players, Contracts, Doubles, Vulnerabilities
from game import cardplay
from game.scoring import get_score_from_result
import sys
from bots.randombotuser import RandomBotUser
from game.interface import HumanUser

NUMBER_OF_PLAYTHROUGHS = 1


def main():
    if sys.version_info[0] < 3:
        print('bridgebot only works with python 3')
        return 1

    deck = Deck()
    deck.shuffle()

    # Todo add in bid getting
    contract = Contracts.FIVE_CLUBS # get_input_enum(Contracts, "contract")
    doubled = Doubles.DOUBLE # get_input_enum(Doubles, "doubled status")
    declarer = Players.EAST # get_input_enum(Players, "declarer")
    vulnerability = Vulnerabilities.BOTH # get_input_enum(Vulnerabilities, "vulnerability")
    vulnerability = vulnerability.is_declarer_vulnerable(declarer)

    # Todo, link in bid history
    bid_history = None

    users = {
        Players.NORTH: HumanUser(),
        Players.SOUTH: RandomBotUser(),
        Players.WEST: RandomBotUser(),
        Players.EAST: RandomBotUser()
    }

    for i in range(0, NUMBER_OF_PLAYTHROUGHS):
        deal = deck.deal()

        trick_winners = cardplay.play(users, deal, contract, declarer, bid_history)

        score = get_score_from_result(contract, doubled, trick_winners, vulnerability)

        print(score)


if __name__ == "__main__":
    sys.exit(main())
