from BridgeBot.enums import Strains, strains

from BridgeBot.enums import Strains, strains, Players, contracts

players = [Players.NORTH, Players.EAST, Players.SOUTH, Players.WEST]

INVALID = "INVALID"

def play_card():
    suit = input("Enter suit: ")
    rank = input("Enter rank: ")
    return suit, rank

class Cardplay:
    # played_cards must be an ordered structure
    # notrump corresponds to trump_index == 4,
    def play_trick(self, played_cards):

        lead_card = played_cards[0]
        following_cards = played_cards[1:len(played_cards)]

        # Compare suit_index to trump_index so that there's no
        # edge cases w.r.t. strains. If playing No Trump, trump_index
        # will be 4, and thus never equal to suit_index (in 0, 1, 2, 3)
        trump_played = lead_card.suit_index == self.trump_index

        winning_index = 0
        counter = 0
        suit_led = lead_card.suit
        highest = lead_card.rank_index # Easier to compare indices

        for card in following_cards:
            counter = counter + 1
            if trump_played:
                if card.suit_index != self.trump_index:
                    continue #Not following trump. Not winning trick.
                elif card.rank_index <= highest:
                    continue #Following low.
                else:
                    winning_index = counter
                    highest = card.rank_index
            elif card.suit_index == suit_led:
                if card.rank_index <= highest:
                    continue
                else:
                    winning_index = counter
                    highest = card.rank_index
            else:
                if card.suit_index == self.trump_index:
                    if (not trump_played):
                        # first time the lead is trumped
                        trump_played = True
                        winning_index = counter
                        highest = card.rank_index
                    elif card.rank_index <= highest:
                        continue
                    else:
                        winning_index = counter
                        highest = card.rank_index
                else:
                    # Not following suit, not trumping
                    continue

        return winning_index

    def __init__(self, hands, contract, declarer):
        if not isinstance(declarer, Players):
            raise Exception("Invalid declarer")

        if contract not in contracts:
            raise Exception("Invalid contract")

        self.hands = hands

        self.on_lead = (players.index(declarer) + 1) % 4
        self.strain = strains[contracts.index(contract) % 5]
        self.trump_index = contracts.index(contract) % 5

        self.ns_tricks = 0
        self.ew_tricks = 0

        for i in range(13):
            trick = []
            x = INVALID
            while x == INVALID:
                suit, rank = play_card()
                x = self.hands[self.on_lead].lead()

            trick.append(x)

            for i in range(3):
                self.on_lead = (self.on_lead + 1) % 4
                x = INVALID
                while x == INVALID:
                    suit, rank = play_card()
                    x = self.hands[self.on_lead].follow()

                trick.append(x)

            self.on_lead = (self.on_lead + self.play_trick(trick)) % 4
            if self.on_lead % 2 == 0:
                self.ns_tricks = self.ns_tricks + 1
            else:
                self.ew_tricks = self.ew_tricks + 1

