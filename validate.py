"""This module performs all the validation functions for the automotive serivce application."""

import string


def is_valid_phone_number(phone_number):
    """This function will validate a passed phone number."""

    valid_numbers = string.digits
    numbers = []
    numbers[:0] = phone_number
    is_valid = True

    if len(numbers) != 12:
        is_valid = False

        return is_valid

    if numbers[3] != "-" or numbers[7] != "-":
        is_valid = False

        return is_valid

    for number in numbers:
        if number in (numbers[3], numbers[7]):
            continue

        if number not in valid_numbers:
            is_valid = False

    return is_valid


def is_valid_address(address):
    """This function will validate a passed address."""

    valid_characters = string.ascii_letters + " " + "," + "." + string.digits
    characters = []
    characters[:0] = address
    is_valid = True

    if len(characters) > 500:
        is_valid = False

        return is_valid

    for character in characters:
        if character not in valid_characters:
            is_valid = False

            return is_valid

    return is_valid


def is_valid_name(name):
    """This function will validate a passed name."""

    valid_characters = string.ascii_letters + " " + string.digits
    is_valid = True

    if len(name) > 50:
        is_valid = False

        return is_valid

    for character in name:
        if character not in valid_characters:
            is_valid = False

    return is_valid


def is_valid_id(passed_id):
    """This function will validate a passed id."""

    valid_characters = string.ascii_letters + string.digits

    if (
        not passed_id
        or isinstance(passed_id, bool)
        or len(passed_id) > 100000000
        or len(passed_id) < 1
    ):
        return False

    for character in passed_id:
        if character not in valid_characters:
            return False

    return True


def is_valid_vin(vin):
    """This function will validate a passed vin number."""

    valid_characters = string.ascii_letters + string.digits

    if not vin or isinstance(vin, bool) or len(vin) != 17:
        return False

    for character in vin:
        if character not in valid_characters:
            return False

    return True


def is_valid_team(team):
    """This function will validate a passed team."""

    valid_teams = string.ascii_uppercase
    is_valid = True

    if len(team) > 1:
        is_valid = False

        return is_valid

    if team not in valid_teams:
        is_valid = False

    return is_valid


def is_valid_lane(lane):
    """This function will validate a passed lane."""

    valid_lanes = string.digits
    is_valid = True

    try:
        lane = int(lane)

    except ValueError:
        is_valid = False

        return is_valid

    if lane < 0:
        is_valid = False

        return is_valid

    if str(lane) not in valid_lanes:
        is_valid = False

    return is_valid


def is_valid_description(description):
    """This function will validate a passed description."""

    valid_characters = string.ascii_letters + "?" + " " + "," + "." + string.digits
    is_valid = True

    if len(description) > 5000:
        is_valid = False

        return is_valid

    for character in description:
        if character not in valid_characters:
            is_valid = False

    return is_valid


def is_valid_dollar_amount(value):
    """This function will validate a passed value to check if it is a valid
    dollar amount."""

    try:
        value = float(value)

    except ValueError:
        return False

    if not value or value < 0:
        return False

    return True


def is_valid_password(password):
    """This function will validate a passed password."""

    valid_characters = string.ascii_letters + string.digits + string.punctuation
    is_valid = True

    if not password or len(password) > 20 or len(password) < 4:
        is_valid = False

        return is_valid

    for character in password:
        if character not in valid_characters:
            is_valid = False

    return is_valid


def is_valid_username(username):
    """This function will validate a passed username."""

    valid_characters = string.ascii_letters + string.digits
    is_valid = True

    if len(username) > 20 or len(username) < 4:
        is_valid = False

        return is_valid

    for character in username:
        if character not in valid_characters:
            is_valid = False

    return is_valid


def is_valid_year(year):
    """Validates that the passed year is 4 digits, returns boolean."""

    valid_digits = string.digits

    is_valid = True

    if len(year) != 4:
        is_valid = False

    for digit in year:
        if digit not in valid_digits:
            is_valid = False

    return is_valid
