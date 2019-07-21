from enums import Strains

import json

from enums import Strains, Players, Suits, Ranks, Status, Contracts, ContractNotFound
from get_input import get_input_enum
from cards import Card

players = [Players.NORTH, Players.EAST, Players.SOUTH, Players.WEST]

def get_card_from_user(playable_cards):
    while True:
        suit = get_input_enum(Suits, "suit")
        rank = get_input_enum(Ranks, "rank")
        if suit in playable_cards:
            playable_cards_of_suit = playable_cards[suit]
            if rank in playable_cards_of_suit:
                return suit, rank
            else:
                print("That card is not legal. Please try again.")
        else:
            print("That suit is not legal. Please try again.")

def convert_hand_to_str(hand):
    hand_string = ""
    for key in sorted(hand.keys()):
        hand_string += key.name + ": " + ', '.join(rank.name for rank in sorted(hand[key])) + "   "
    return hand_string


class CardPlay:
    @staticmethod
    def determine_trick_winner(played_cards, trump_suit):
        if not isinstance(played_cards, list):
            raise ValueError("played_cards must be a list of cards")

        highest_card = played_cards[0]
        suit_led = played_cards[0].suit

        for card_counter in range(len(played_cards)):
            if played_cards[card_counter].suit == trump_suit and highest_card != trump_suit:
                highest_card = played_cards[card_counter]
            elif played_cards[card_counter].rank > highest_card.rank and (
                    played_cards[card_counter].suit == suit_led or
                    played_cards[card_counter].rank == trump_suit
            ):
                highest_card = played_cards[card_counter]

        return played_cards.index(highest_card)



    # played_cards must be an ordered structure
    # notrump corresponds to trump_index == 4,
    def play_trick(self, played_cards):

        lead_card = played_cards[0]
        following_cards = played_cards[1:len(played_cards)]

        # Compare suit_index to trump_index so that there's no
        # edge cases with respect to strains. If playing No Trump, trump_index
        # will be 4, and thus never equal to suit_index (in 0, 1, 2, 3)
        trump_played = lead_card.suit == self.trump_suit

        winning_index = 0
        counter = 0
        suit_led = lead_card.suit
        highest = lead_card.rank # Easier to compare indices

        for card in following_cards:

            counter = counter + 1
            if trump_played:
                if card.suit != self.trump:
                    continue #Not following trump. Not winning trick.
                elif card.rank <= highest:
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
                if card.suit == self.trump_suit:
                    if not trump_played:
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

    @staticmethod
    def __determine_trump_rank_from_contract(contract):
        if not isinstance(contract, Contracts):
            raise ContractNotFound("Invalid Contract")

    def __init__(self, hands, contract, declarer):
        if not isinstance(declarer, Players):
            raise Exception("Invalid declarer")

        if not isinstance(contract, Contracts):
            raise ContractNotFound("Invalid Contract")

        self.hands = hands

        self.on_lead = declarer.next_player()
        
        self.strain = Strains.determine_strain_from_contract(contract)

        self.trump_suit = Suits.determine_suit_from_contract(contract)

        self.ns_tricks = 0
        self.ew_tricks = 0

        for trick_count in range(13):
            trick = []
            print(self.on_lead.value + " starts")


            all_cards = self.hands[self.on_lead].hand
            print("All Cards: " +
                  convert_hand_to_str(all_cards)
            )


            led_suit, led_rank = get_card_from_user(all_cards)
            x = self.hands[self.on_lead].lead(led_suit, led_rank)
                # end while loop

            trick.append(Card(led_suit, led_rank))
            led_card_tuple = (led_suit, led_rank)

            for follower_count in range(3):
                self.on_lead = self.on_lead.next_player()
                print(self.on_lead.value + "'s turn")
                print("All Cards: " +
                      convert_hand_to_str(self.hands[self.on_lead].hand)
                )

                legal_cards = self.hands[self.on_lead].legal_cards(self.trump_suit)
                print("Legal Cards: " +
                    convert_hand_to_str(legal_cards)
                )

                suit, rank = get_card_from_user(legal_cards)
                x = self.hands[self.on_lead].follow(led_card_tuple, suit, rank)
                #end while loop

                trick.append(Card(suit, rank))

            # Why do we add self.on_lead here? Should this just be self.play_trick(trick)
            # Answer: self.play_trick determines the index of the winner relative to the index of the leader
            # it also makes the code re-usable in case we want to use it for another trick-taking game, because
            # they all have the same mechanic, even if they don't have four players.
            self.on_lead = (self.on_lead + self.play_trick(trick)) % 4

            # Update the number of tricks won
            if self.on_lead % 2 == 0:
                self.ns_tricks = self.ns_tricks + 1
            else:
                self.ew_tricks = self.ew_tricks + 1

