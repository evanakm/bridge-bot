from enum import Enum

import readline # in windows, need to install pyreadline
import re


def get_input_list(valid_input_list, name):
    # This assumes that the enum values are all upper case

    if not (isinstance(valid_input_list, list) or isinstance(valid_input_list, set)):
        raise TypeError("valid_input_list is not of type list or set")

    def completer(text, state):
        options = [str(option) for option in valid_input_list if bool(re.match(text, str(option), re.I))]

        if state < len(options):
            return options[state]
        else:
            return None

    readline.parse_and_bind("tab: complete")
    readline.set_completer(completer)

    value = None
    first_time = True
    while value not in valid_input_list:
        if first_time:
            message = "Please enter the " + name + ": "
            first_time = False
        else:
            all_valid_inputs = ', '.join([str(e) for e in valid_input_list])
            message = "That was not a valid input. Here are all valid inputs: " + all_valid_inputs + "\n" + \
                      "Please enter the " + name + ": "
        try:
            value_str = input(message)
            value_list = [v for v in valid_input_list if bool(str(v) == value_str)]
            value = value_list[0]
        except KeyError and IndexError:
            pass
    return value


def get_input_enum(enum, name):
    # This assumes that the enum values are all upper case

    if not issubclass(enum, Enum):
        raise TypeError("enum is not a subclass of Enum")

    if not isinstance(name, str):
        raise TypeError("name is not of type str")

    valid_input_list = [e.name for e in enum]

    def completer(text, state):
        options = [option for option in valid_input_list if bool(re.match(text, option, re.I))]
        if state < len(options):
            return options[state]
        else:
            return None

    readline.parse_and_bind("tab: complete")
    readline.set_completer(completer)

    value = None
    first_time = True
    while not isinstance(value, enum):
        if first_time:
            message = "Please enter the " + name + ": "
            first_time = False
        else:
            all_valid_inputs = ', '.join(valid_input_list)
            message = "That was not a valid input. Here are all valid inputs: " + all_valid_inputs + "\n" + \
                      "Please enter the " + name + ": "
        try:
            value = enum[str(input(message)).upper()]
        except KeyError:
            pass
    return value


def get_input_card(playable_cards):
    return get_input_list(playable_cards, "card")
