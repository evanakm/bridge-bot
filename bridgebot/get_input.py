from enum import Enum

import readline

def get_input_enum(enum, name):
    # This assumes that the enum values are all upper case

    valid_input_list = [e.name for e in enum]

    def completer(text, state):
        options = [option for option in valid_input_list if option.startswith(text)]
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
            print(message)
            value = enum[str(input(message)).upper()]
        except KeyError:
            pass
    return value


def get_input(values, name):
    if isinstance(values, Enum):
        return get_input_enum(values, name)
    else:
        raise TypeError("Input Error")