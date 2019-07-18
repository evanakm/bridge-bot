from BridgeBot.enums import Vulnerabilities, players, Players
from BridgeBot.cards import BridgeHand


class Deal:
    def __init__(self, dealer, vuln, cards):

        if not isinstance(dealer, Players):
            raise Exception("Dealer must be a direction")

        if not isinstance(vuln, Vulnerabilities):
            raise Exception("Invalid vulnerability")

        self.dealer = dealer

        self.vuln = vuln

        # Weird python indexing, but it's right
        self.hands = {
            Players.NORTH: BridgeHand(cards[0:13]),
            Players.EAST: BridgeHand(cards[13:26]),
            Players.SOUTH: BridgeHand(cards[26:39]),
            Players.WEST: BridgeHand(cards[39:52]),
        }

        print(self.hands)

        self.dealer_ix = players.index(dealer)

    def play_hand(self):
        auction = Auction()
        if auction.contract['strain'] == Strains.PASSOUT:
            return 0

        strain_index = strains.index(auction.contract['strain'])
        level_index = int(auction.contract['level']) - 1
        contract = contracts[5*level_index + strain_index]

        cp = Cardplay(self.hands[Players.NORTH],self.hands[Players.EAST], self.hands[Players.SOUTH], self.hands[Players.WEST],
                      contract, auction.contract['declarer'])

        bid = int(auction.contract['level'])
        strain = auction.contract['strain']

        if auction.contract['declarer'] in [Players.NORTH, Players.SOUTH]:
            vul = self.vuln in [Vulnerabilities.NS, Vulnerabilities.BOTH]
            if cp.ns_tricks < bid + 6:
                return score(bid,strain,cp.ns_tricks-(bid+6),auction.contract['doubled'],vul)
            made = cp.ns_tricks - 6
            return score(bid,strain,made,auction.contract['doubled'],vul)
        else:
            vul = self.vuln in [Vulnerabilities.EW, Vulnerabilities.BOTH]
            if cp.ew_tricks < bid + 6:
                return score(bid, strain, cp.ew_tricks-(bid+6),auction.contract['doubled'],vul)
            made = cp.ew_tricks - 6
            return score(bid, strain, made, auction.contract['doubled'], vul)