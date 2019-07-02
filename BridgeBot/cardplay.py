import cards
from bidding import strains
from cards import suits, ranks

contracts = ['1C',' 1D', '1H', '1S', '1N',
        '2C', '2D', '2H', '2S', '2N',
        '3C', '3D', '3H', '3S', '3N',
        '4C', '4D', '4H', '4S', '4N',
        '5C', '5D', '5H', '5S', '5N',
        '6C', '6D', '6H', '6S', '6N',
        '7C', '7D', '7H', '7S', '7N']

players = ['NORTH', 'EAST', 'SOUTH', 'WEST']


class Cardplay:
    # played_cards must be an ordered structure
    # notrump corresponds to trump_index == 4,
    def play_trick(self, played_cards, trump_index):

        lead_card = played_cards[0]
        following_cards = played_cards[1:len(played_cards)]

        winning_index = 0
        counter = 0
        suit_led = lead_card.suit_index
        trump_played = lead_card.suit_index == trump_index
        highest = lead_card.rank_index

        for card in following_cards:
            counter = counter + 1
            if trump_played:
                if card.suit_index != trump_index:
                    continue
                elif card.rank_index <= highest:
                    continue
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
                if card.suit_index == trump_index:
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

    def __init__(self,north,east,south,west,contract,declarer):
        if not declarer in players:
            raise Exception("Invalid declarer")

        if not contract in contracts:
            raise Exception("Invalid contract")

        self.hands = {
            'NORTH':north,
            'EAST':east,
            'SOUTH':south,
            'WEST':west
        }

        self.on_lead = (players.index(declarer) + 1) % 4
        self.strain = strains[contracts.index(contract) % 5]

        self.ns_tricks = 0
        self.ew_tricks = 0

        for i in range(13):
            trick = []
            x = None
            while x is None:
                suit = input("Enter suit:")
                rank = input("Enter rank:")
                x = self.hands[self.on_lead].lead()

            trick.append(x)

            for i in range(3):
                self.on_lead = (self.on_lead + 1) % 4
                x = None
                while x is None:
                    suit = input("Enter suit:")
                    rank = input("Enter rank:")
                    x = self.hands[self.on_lead].follow()

                trick.append(x)

            self.on_lead = (self.on_lead + self.play_trick(trick,self.strain)) % 4
            if self.on_lead % 2 == 0:
                self.ns_tricks = self.ns_tricks + 1
            else:
                self.ew_tricks = self.ew_tricks + 1

