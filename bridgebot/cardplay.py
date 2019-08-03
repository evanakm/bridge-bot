from enums import Strains, Players, Contracts, ContractNotFound, Team

from bridgehand import Card
from interface import User


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


def play(users, hands, contract, declarer, bid_history):
    if not isinstance(users, dict):
        raise TypeError("users is not of type dict")

    for key, val in users.items():
        if not isinstance(key, Players):
            raise TypeError("users key is not of type Players")

        if not isinstance(val, User):
            raise TypeError("users value is not of type User")

    card_history = {
        Players.NORTH: [],
        Players.EAST: [],
        Players.WEST: [],
        Players.SOUTH: []
    }

    leader_history = []

    if not isinstance(declarer, Players):
        raise TypeError("Invalid declarer")

    if not isinstance(contract, Contracts):
        raise ContractNotFound("Invalid Contract")

    dummy = declarer.partner()

    leading_player = declarer.next_player()

    strain = Strains.determine_strain_from_contract(contract)

    ns_tricks = 0
    ew_tricks = 0

    for trick_count in range(13):
        trick = []

        leader_history.append(leading_player)
        print(leading_player.value + " starts")

        all_cards = hands[leading_player].cards

        led_card = users[leading_player].play_card(
            leading_player, dummy, hands[dummy].cards, all_cards, all_cards, bid_history, card_history, leader_history
        )
        card_history[leading_player].append(led_card)

        hands[leading_player].lead(led_card)

        trick.append(led_card)

        print(leading_player.name + " played " + str(led_card))

        current_player = leading_player

        for follower_count in range(3):
            current_player = current_player.next_player()
            print(current_player.name + "'s turn")
            all_cards = hands[current_player].cards
            legal_cards = hands[current_player].legal_cards(led_card.suit)
            card = users[current_player].play_card(
                current_player, dummy, hands[dummy].cards, all_cards, legal_cards, bid_history, card_history,
                leader_history
            )
            card_history[current_player].append(card)

            hands[current_player].follow(led_card.suit, card)
            trick.append(card)
            print(current_player.name + " played " + str(card))

        # self.play_trick determines the index of the winner relative to the index of the leader
        # it also makes the code re-usable in case we want to use it for another trick-taking game, because
        # they all have the same mechanic, even if they don't have four players.
        winning_player = leading_player.determine_nth_player_to_the_right(determine_trick_winner(trick, strain))

        # Update the number of tricks won
        if Team.NS.is_player_in_team(winning_player):
            ns_tricks = ns_tricks + 1
        else:
            ew_tricks = ew_tricks + 1

        leading_player = winning_player

    if Team.NS.is_player_in_team(declarer):
        return ns_tricks
    if Team.EW.is_player_in_team(declarer):
        return ew_tricks

