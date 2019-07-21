from enums import Strains, Players, Suits, Ranks, Contracts, ContractNotFound, Team
from get_input import get_input_enum
from cards import Card


def __get_card_from_user(playable_cards):
    while True:
        suit = get_input_enum(Suits, "suit")
        rank = get_input_enum(Ranks, "rank")
        if suit in playable_cards:
            playable_cards_of_suit = playable_cards[suit]
            if rank in playable_cards_of_suit:
                return Card(suit, rank)
            else:
                print("That card is not legal. Please try again.")
        else:
            print("That suit is not legal. Please try again.")


def __convert_hand_to_str(hand):
    hand_string = ""
    for key in sorted(hand.keys()):
        hand_string += key.name + ": " + ', '.join(rank.name for rank in sorted(hand[key])) + "   "
    return hand_string


def determine_trick_winner(played_cards, strain):
    if not isinstance(played_cards, list):
        raise TypeError("played_cards must be a list of cards")

    for card in played_cards:
        if not isinstance(card, Card):
            raise TypeError("played_cards must be a list of cards")

    if not len(played_cards) == 4:
        raise ValueError("played_cards must contain 4 cards")

    highest_card = played_cards[0]
    suit_led = played_cards[0].suit

    for card_counter in range(len(played_cards)):
        if strain.compare_to_suit(played_cards[card_counter].suit) and not strain.compare_to_suit(highest_card.suit):
            highest_card = played_cards[card_counter]
        elif played_cards[card_counter].rank > highest_card.rank and (
                played_cards[card_counter].suit == suit_led or
                strain.compare_to_suit(played_cards[card_counter].suit)
        ):
            highest_card = played_cards[card_counter]

    return played_cards.index(highest_card)


def play(hands, contract, declarer):
    if not isinstance(declarer, Players):
        raise Exception("Invalid declarer")

    if not isinstance(contract, Contracts):
        raise ContractNotFound("Invalid Contract")

    leading_player = declarer.next_player()

    strain = Strains.determine_strain_from_contract(contract)

    ns_tricks = 0
    ew_tricks = 0

    for trick_count in range(13):
        trick = []
        print(leading_player.value + " starts")


        all_cards = hands[leading_player].hand
        print("All Cards: " +
              __convert_hand_to_str(all_cards)
              )

        led_card = __get_card_from_user(all_cards)

        hands[leading_player].lead(led_card)

        trick.append(led_card)

        current_player = leading_player

        for follower_count in range(3):
            current_player = current_player.next_player()
            print(current_player.name + "'s turn")
            print("All Cards: " +
                  __convert_hand_to_str(hands[current_player].hand)
                  )

            legal_cards = hands[current_player].legal_cards(led_card.suit)
            print("Legal Cards: " +
                  __convert_hand_to_str(legal_cards)
                  )

            card = __get_card_from_user(legal_cards)
            hands[current_player].follow(led_card.suit, card)
            trick.append(card)

        # self.play_trick determines the index of the winner relative to the index of the leader
        # it also makes the code re-usable in case we want to use it for another trick-taking game, because
        # they all have the same mechanic, even if they don't have four players.
        winning_player = leading_player.increment_by(determine_trick_winner(trick, strain))

        # Update the number of tricks won
        if leading_player in Team.team_to_set_of_players(Team.NS):
            ns_tricks = ns_tricks + 1
        else:
            ew_tricks = ew_tricks + 1

        leading_player = winning_player

    return {Team.NS: ns_tricks, Team.EW: ew_tricks}
