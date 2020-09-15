from game.enums import Strains, Team, NUMBER_OF_TRICKS

from game.bridgehand import Card
from game.gamestate import GameState


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


def card_logic(state: GameState, is_led: bool):
    print(state.current_player.name + "'s turn")
    all_cards = state.hands[state.current_player].cards

    # TODO consider moving this out of this function and passing in `legal_cards` into the function.
    if not is_led:
        legal_cards = state.hands[state.current_player].legal_cards(state.led_card.suit)
    else:
        legal_cards = all_cards

    partner_user = state.users[state.current_player.partner()]
    partners_cards = state.hands[state.current_player.partner()].cards

    # TODO consider creating a function to call on GameState that returns the visible data for each player.
    # The function on GameState would take in a Player and return the items visible to the player.
    # That would allow passing only one argument to the following play_card function.
    card = state.users[state.current_player].play_card(
        partner=partner_user,
        partners_cards=partners_cards,
        current_player=state.current_player,
        dummy=state.dummy,
        dummy_hand=state.hands[state.dummy].cards,
        all_cards=all_cards,
        legal_cards=legal_cards,
        bid_history=state.bid_history,
        card_history=state.card_history,
        leader_history=state.leader_history
    )

    state.card_history[state.current_player].append(card)

    if is_led:
        # TODO consider using follow here instead of lead
        # state.hands[state.current_player].follow(card.suit, card)
        state.hands[state.current_player].lead(card)
    else:
        state.hands[state.current_player].follow(state.led_card.suit, card)

    state.current_trick.append(card)

    print(state.current_player.name + " played " + str(card))
    state.current_player = state.current_player.next_player()


def play(state: GameState):
    print("Declarer is " + str(state.declarer))
    print("Dummy is " + str(state.dummy))
    print("Strain is " + str(state.strain.name))
    print("Contract is " + str(state.contract.name))
    print(state.leading_player.value + " starts")

    while state.trick_count < NUMBER_OF_TRICKS:
        if state.current_player == state.leading_player:
            if len(state.current_trick) == 0:
                card_logic(state, True)
            else:
                # self.play_trick determines the index of the winner relative to the index of the leader
                # it also makes the code re-usable in case we want to use it for another trick-taking game, because
                # they all have the same mechanic, even if they don't have four players.
                winning_player = state.leading_player.determine_nth_player_to_the_right(
                    determine_trick_winner(state.current_trick, state.strain))

                print(state.leading_player.value + " won the trick")

                # Update the number of tricks won
                if Team.NS.is_player_in_team(winning_player):
                    state.ns_tricks += 1
                else:
                    state.ew_tricks += 1

                state.trick_history.append(state.current_trick)
                state.leader_history.append(state.leading_player)

                state.leading_player = winning_player
                state.current_player = winning_player

                state.current_trick = []
        else:
            card_logic(state, False)

    if Team.NS.is_player_in_team(state.declarer):
        return state.ns_tricks
    if Team.EW.is_player_in_team(state.declarer):
        return state.ew_tricks

