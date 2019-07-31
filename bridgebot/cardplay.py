from enums import Strains, Players, Contracts, ContractNotFound, Team
from get_input import get_input_card
from cards import Card


def __convert_hand_to_str(cards):
    card_string = ""
    for card in sorted(cards):
        card_string += str(card) + " "
    return card_string


def determine_trick_winner(played_cards, strain):
    if not isinstance(played_cards, list):
        raise TypeError("played_cards must be a list of cards")

    for card in played_cards:
        if not isinstance(card, Card):
            raise TypeError("played_cards must be a list of cards")

    if not len(played_cards) == 4:
        raise ValueError("played_cards must contain 4 cards")

    if not isinstance(strain, Strains):
        raise TypeError("strain must be of type Strains")

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

        all_cards = hands[leading_player].cards
        print("All Cards: " +
              __convert_hand_to_str(all_cards)
              )

        led_card = get_input_card(all_cards)

        hands[leading_player].lead(led_card)

        trick.append(led_card)

        current_player = leading_player

        for follower_count in range(3):
            current_player = current_player.next_player()
            print(current_player.name + "'s turn")
            print("All Cards: " +
                  __convert_hand_to_str(hands[current_player].cards)
                  )

            legal_cards = hands[current_player].legal_cards(led_card.suit)
            print("Legal Cards: " +
                  __convert_hand_to_str(legal_cards)
                  )

            card = get_input_card(legal_cards)
            hands[current_player].follow(led_card.suit, card)
            trick.append(card)

        trick_winner = determine_trick_winner(trick, strain)

        # self.play_trick determines the index of the winner relative to the index of the leader
        # it also makes the code re-usable in case we want to use it for another trick-taking game, because
        # they all have the same mechanic, even if they don't have four players.
        winning_player = leading_player.determine_nth_player_to_the_right(trick_winner)

        print(winning_player.name + " won the trick")

        # Update the number of tricks won
        if leading_player in Team.team_to_set_of_players(Team.NS):
            ns_tricks = ns_tricks + 1
        else:
            ew_tricks = ew_tricks + 1

        leading_player = winning_player

    if declarer in [Players.NORTH, Players.SOUTH]:
        return ns_tricks
    if declarer in [Players.EAST, Players.WEST]:
        return ew_tricks

