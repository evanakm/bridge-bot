from game import cardplay
from game.bidding import Auction
from game.enums import Vulnerabilities, Players, Strains, Contracts
from game.scoring import score


def play(dealer, vulnerability, hands):
    if not isinstance(dealer, Players):
        raise Exception("Dealer must be a direction")

    if not isinstance(vulnerability, Vulnerabilities):
        raise Exception("Invalid vulnerability")

    auction = Auction()
    if auction.contract['strain'] == Strains.PASSOUT:
        return 0

    strain_index = Strains.strains().index(auction.contract['strain'])
    level_index = int(auction.contract['level']) - 1
    contract = Contracts.contracts()[5*level_index + strain_index]

    cp = cardplay.play(hands, contract, auction.contract['declarer'])

    bid = int(auction.contract['level'])
    strain = auction.contract['strain']

    if auction.contract['declarer'] in [Players.NORTH, Players.SOUTH]:
        vul = vulnerability in [Vulnerabilities.NS, Vulnerabilities.BOTH]
        if cp.ns_tricks < bid + 6:
            return score(bid,strain,cp.ns_tricks-(bid+6),auction.contract['doubled'],vul)
        made = cp.ns_tricks - 6
        return score(bid,strain,made,auction.contract['doubled'],vul)
    else:
        vul = vulnerability in [Vulnerabilities.EW, Vulnerabilities.BOTH]
        if cp.ew_tricks < bid + 6:
            return score(bid, strain, cp.ew_tricks-(bid+6),auction.contract['doubled'],vul)
        made = cp.ew_tricks - 6
        return score(bid, strain, made, auction.contract['doubled'], vul)