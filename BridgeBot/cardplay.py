import cards

contracts = ['1C',' 1D', '1H', '1S', '1N',
        '2C', '2D', '2H', '2S', '2N',
        '3C', '3D', '3H', '3S', '3N',
        '4C', '4D', '4H', '4S', '4N',
        '5C', '5D', '5H', '5S', '5N',
        '6C', '6D', '6H', '6S', '6N',
        '7C', '7D', '7H', '7S', '7N']

players = ['NORTH', 'EAST', 'SOUTH', 'WEST']

suits = cards.suits
strains = ['CLUBS','DIAMONDS','HEARTS','SPADES','NT']

class Cardplay:
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
            x = 0
            while(x != 0):
                suit = input("Enter suit:")
                rank = input("Enter rank:")
                x = self.hands[self.on_lead].lead()

            trick.append(x)

            for i in range(3):
                self.on_lead = (self.on_lead + 1) % 4
                while(x != 0):
                    suit = input("Enter suit:")
                    rank = input("Enter rank:")
                    x = self.hands[self.on_lead].follow()

            self.on_lead = (self.on_lead + trick.append(x)) % 4
            if self.on_lead % 2 == 0:
                self.ns_tricks = self.ns_tricks + 1
            else:
                self.ew_tricks = self.ew_tricks + 1

