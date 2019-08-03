from deck import Deck

from enums import Players, Contracts, Doubles, Vulnerabilities
import cardplay
from scoring import get_score_from_result
from interface import HumanUser
import sys

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
        Players.SOUTH: HumanUser(),
        Players.WEST: HumanUser(),
        Players.EAST: HumanUser()
    }

    for i in range(1, NUMBER_OF_PLAYTHROUGHS):
        deal = deck.deal()

        trick_winners = cardplay.play(users, deal, contract, declarer, bid_history)

        score = get_score_from_result(contract, doubled, trick_winners, vulnerability)

        print(score)


if __name__ == "__main__":
    sys.exit(main())
