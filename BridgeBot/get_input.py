def get_input_enum(enum, name):
    # This assumes that the enum values are all upper case
    value = None
    first_time = True
    while not isinstance(value, enum):
        if first_time:
            message = "Please enter the " + name + ": "
            first_time = False
        else:
            all_valid_inputs = ', '.join([e.name for e in enum])
            message = "That was not a valid input. Here are all valid inputs: " + all_valid_inputs + "\nPlease enter the " + name + ": "
        try:
            value = enum[str(input(message)).upper()]
        except KeyError:
            pass
    return value