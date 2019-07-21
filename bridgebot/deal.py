from enums import Vulnerabilities, Players, Strains, Contracts
from cards import BridgeHand
from cardplay import CardPlay


class Deal:
    @staticmethod
    def deal(cards):
        # Weird python indexing, but it's right
        if not isinstance(cards, list):
            raise Exception("cards must be a list of ints")

        for card in cards:
            if card not in range(52):
                raise Exception("Index must be an integer between 0 and 51 inclusive.")

        return {
            Players.NORTH: BridgeHand(cards[0:13]),
            Players.EAST: BridgeHand(cards[13:26]),
            Players.SOUTH: BridgeHand(cards[26:39]),
            Players.WEST: BridgeHand(cards[39:52]),
        }

    def __init__(self, dealer, vulnerability, cards):
        if not isinstance(dealer, Players):
            raise Exception("Dealer must be a direction")

        if not isinstance(vulnerability, Vulnerabilities):
            raise Exception("Invalid vulnerability")

        self.dealer = dealer
        self.vulnerability = vulnerability
        self.hands = self.deal(cards)

    def play_hand(self):
        auction = Auction()
        if auction.contract['strain'] == Strains.PASSOUT:
            return 0

        strain_index = Strains.strains().index(auction.contract['strain'])
        level_index = int(auction.contract['level']) - 1
        contract = Contracts.contracts()[5*level_index + strain_index]

        cp = CardPlay(self.hands, contract, auction.contract['declarer'])

        bid = int(auction.contract['level'])
        strain = auction.contract['strain']

        if auction.contract['declarer'] in [Players.NORTH, Players.SOUTH]:
            vul = self.vulnerability in [Vulnerabilities.NS, Vulnerabilities.BOTH]
            if cp.ns_tricks < bid + 6:
                return score(bid,strain,cp.ns_tricks-(bid+6),auction.contract['doubled'],vul)
            made = cp.ns_tricks - 6
            return score(bid,strain,made,auction.contract['doubled'],vul)
        else:
            vul = self.vulnerability in [Vulnerabilities.EW, Vulnerabilities.BOTH]
            if cp.ew_tricks < bid + 6:
                return score(bid, strain, cp.ew_tricks-(bid+6),auction.contract['doubled'],vul)
            made = cp.ew_tricks - 6
            return score(bid, strain, made, auction.contract['doubled'], vul)