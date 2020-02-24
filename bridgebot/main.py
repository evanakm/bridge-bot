from game.deck import Deck

from game.enums import Players, Vulnerabilities
from game import cardplay
from game.scoring import get_score_from_result
import sys
from bots.randombotuser import RandomBotUser
from game.interface import HumanUser
from game.bidding import auction

NUMBER_OF_PLAYTHROUGHS = 1


def main():
    if sys.version_info < (3, 6):
        print('bridgebot only works with python 3.6 and higher')
        return 1

    deck = Deck()
    deck.shuffle()

    users = {
        Players.NORTH: HumanUser(),
        Players.SOUTH: RandomBotUser(),
        Players.WEST: RandomBotUser(),
        Players.EAST: RandomBotUser()
    }

    record = auction(users, Players.NORTH)
    full_contract = record.determine_full_contract()

    contract = full_contract.contract
    doubled = full_contract.doubled
    declarer = full_contract.declarer
    vulnerability = Vulnerabilities.BOTH
    declarer_vulnerable = vulnerability.is_declarer_vulnerable(declarer)

    for i in range(0, NUMBER_OF_PLAYTHROUGHS):
        deal = deck.deal()

        trick_winners = cardplay.play(users, deal, contract, declarer, record.record)

        score = get_score_from_result(contract, doubled, trick_winners, declarer_vulnerable)

        print("The declarer " + declarer.name + " has a score of " + str(score))

    return 0


if __name__ == "__main__":
    sys.exit(main())
