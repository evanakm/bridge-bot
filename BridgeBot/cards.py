import random

suits = ['CLUBS','DIAMONDS','HEARTS','SPADES']
ranks = ['2','3','4','5','6','7','8','9','T','J','Q','K','A']


class Deck:
    def __init__(self):
        self.card_indices = list(range(52))

    def shuffle(self):
        for i in range(51, 0, -1):
            j = random.randint(0, i)  # So as not to bias certain permutations
            if j == i:
                continue
            self.card_indices[i], self.card_indices[j] = self.card_indices[j], self.card_indices[i]


class Card:
    def __init__(self, suit, rank):
        if suits.count(suit) == 0:
            raise Exception("Unknown Suit")

        if ranks.count(rank) == 0:
            raise Exception("Unknown Rank")

        self.suit = suit
        self.rank = rank

        self.suit_index = suits.index(suit)
        self.rank_index = ranks.index(rank)

    # Mostly for assertions and error checking
    def does_not_match(self, other_card):
        if self.suit_index != other_card.suit_index:
            return False
        elif self.rank_index != other_card.rank_index:
            return False
        else:
            return True


# played_cards must be an ordered structure
# notrump corresponds to trump_index == 4,
def trick(played_cards, trump_index):

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


class Hand:
    hand = {
        'spades': set(),
        'hearts':  set(),
        'diamonds': set(),
        'clubs': set()
    }

    def add_card(self,suit,rank):
        if ranks.count(rank) == 0:
            raise Exception("Unknown Rank")
        self.hand[suit].add(rank)

    def play_card(self,suit,rank):
        if not rank in self.hand[suit]:
            raise Exception("Hand does not contain " + rank + " of " + suit + ".")
        self.hand[suit].difference_update(rank)
        return Card(suit,rank)

    # Take a number from 0 to 51 and map it to suit and rank.
    def add_card_from_deck_index(self,index):
        self.add_card(suits[int(index / 13)], ranks[index % 13])

    # Take a list of numbers from 0 to 51 and map them to suits and ranks.
    def fill_from_list(self,deck_indices):
        for idx in deck_indices:
            self.add_card_from_deck_index(idx)


class BridgeHand(Hand):
    def __init__(self,deck_indices):
        if len(deck_indices) != 13:
            raise Exception("Bridge hands must contain 13 cards.")
        self.fill_from_list(deck_indices)

    def lead(self,suit,rank):
        return self.play_card(suit,rank)

    def follow(self,led,suit,rank):
        if suit != led[suit]:
            if len(self.hand[suit]) != 0:
                print("Must follow suit if possible.")
                return 0
            else:
                return self.play_card(suit,rank)
