from enums import Vulnerabilities

class Deal:
    def __init__(self, dealer, vuln, cards=None):

        if hand_names.count(dealer) == 0:
            raise Exception("Dealer must be a direction")

        if not isinstance(vuln, Vulnerabilities):
            raise Exception("Invalid vulnerability")

        self.dealer = dealer

        if vuln == Vulnerabilities.NONE:
            self.ns_vuln = False
            self.ew_vuln = False
        elif vuln == Vulnerabilities.NS:
            self.ns_vuln = True
            self.ew_vuln = False
        if vuln == Vulnerabilities.EW:
            self.ns_vuln = False
            self.ew_vuln = True
        if vuln == Vulnerabilities.BOTH:
            self.ns_vuln = True
            self.ew_vuln = True

        if not cards:
            deck.shuffle()
            cards = deck.cards
        elif set(cards) != set(range(52)):
            print("'cards' must be a list of integers from 0 to 51 with each number appearing once.")
            print("Generating a random deal.")
            deck.shuffle()
            cards = deck.cards

        # Weird python indexing, but it's right
        self.hands = {
            'NORTH': BridgeHand(cards[0:13]),
            'EAST': BridgeHand(cards[13:26]),
            'SOUTH': BridgeHand(cards[26:39]),
            'WEST': BridgeHand(cards[39:52]),
        }

        self.dealer_ix = hand_names.index(dealer)

    def play_hand(self):
        auction = Auction()
        if auction.contract['strain'] == 'PASSOUT':
            return 0

        strain_index = strains.index(auction.contract['strain'])
        level_index = int(auction.contract['level']) - 1
        contract = contracts[5*level_index + strain_index]

        cp = Cardplay(self.hands['NORTH'],self.hands['EAST'], self.hands['SOUTH'], self.hands['WEST'],
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