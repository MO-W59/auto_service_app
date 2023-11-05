"""This module performs all the validation functions for the automotive serivce application."""

import string


def is_valid_phone_number(phone_number):
    """Validates a passed phone number."""

    valid_numbers = string.digits
    numbers = []
    numbers[:0] = phone_number

    if len(numbers) != 12:
        return False

    # check for xxx-xxx-xxxx format
    if numbers[3] != "-" or numbers[7] != "-":
        return False

    for number in numbers:
        if number in (numbers[3], numbers[7]):  # skip "-" locations
            continue

        if number not in valid_numbers:
            return False

    return True


def is_valid_address(address):
    """Validates a passed address."""

    valid_characters = string.ascii_letters + " " + "," + "." + string.digits
    characters = []
    characters[:0] = address

    if len(characters) > 500:
        return False

    for character in characters:
        if character not in valid_characters:
            return False

    return True


def is_valid_name(name):
    """Validates a passed name."""

    valid_characters = string.ascii_letters + " " + string.digits

    if len(name) > 50 or len(name) < 1:
        return False

    for character in name:
        if character not in valid_characters:
            return False

    return True


def is_valid_id(passed_id):
    """Validates a passed id."""

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
    """Validates a passed vin number."""

    valid_characters = string.ascii_letters + string.digits

    if not vin or isinstance(vin, bool) or len(vin) != 17:
        return False

    for character in vin:
        if character not in valid_characters:
            return False

    return True


def is_valid_team(team):
    """Validates a passed team."""

    valid_teams = string.ascii_uppercase

    if len(team) != 1:
        return False

    if team not in valid_teams:
        return False

    return True


def is_valid_lane(lane):
    """Validates a passed lane."""

    valid_lanes = string.digits

    try:
        lane = int(lane)

    except ValueError:
        return False

    if lane < 0:
        return False

    if str(lane) not in valid_lanes:
        return False

    return True


def is_valid_description(description):
    """Validates a passed description."""

    valid_characters = string.ascii_letters + "?" + " " + "," + "." + string.digits

    if len(description) > 5000:
        return False

    for character in description:
        if character not in valid_characters:
            return False

    return True


def is_valid_dollar_amount(value):
    """Validates a passed value to check if it is a valid dollar amount."""

    try:
        value = float(value)

    except ValueError:
        return False

    if not value or value < 0:
        return False

    return True


def is_valid_password(password):
    """Validates a passed password."""

    valid_characters = string.ascii_letters + string.digits + string.punctuation

    if not password or len(password) > 20 or len(password) < 4:
        return False

    for character in password:
        if character not in valid_characters:
            return False

    return True


def is_valid_username(username):
    """Validates a passed username."""

    valid_characters = string.ascii_letters + string.digits

    if len(username) > 20 or len(username) < 4:
        return False

    for character in username:
        if character not in valid_characters:
            return False

    return True


def is_valid_year(year):
    """Validates that the passed year is 4 digits, returns boolean."""

    valid_digits = string.digits

    if len(year) != 4:
        return False

    for digit in year:
        if digit not in valid_digits:
            return False

    return True


def new_user(gui, test_data):
    """Ensures all passed data for a new user is valid, returns errors if any, and
    returns is_tech, is_writer and lane/section information for the user."""

    if (
        not is_valid_username(test_data["username"])
        or not is_valid_password(test_data["pwrd"])
        or not is_valid_password(test_data["confirm_pwrd"])
    ):
        test_data["errors"] += "Invalid username or password!\n\n"

    if test_data["pwrd"] != test_data["confirm_pwrd"]:
        test_data["errors"] += "Passwords do not match!\n\n"

    if not is_valid_name(test_data["name"]):
        test_data["errors"] += "Invalid name!\n\n"

    if not is_valid_team(test_data["team"]):
        test_data["errors"] += "Invalid team!\n\n"

    if gui.new_user_tech_radio_button.isChecked():
        test_data["is_tech"] = 1
        test_data["is_writer"] = 0

        test_data["lane_or_section"] = gui.new_user_section_input_box.text()

        if not is_valid_name(test_data["lane_or_section"]):
            test_data["errors"] += "Invalid section!\n\n"

    if gui.new_user_service_writer_radio_button.isChecked():
        test_data["is_tech"] = 0
        test_data["is_writer"] = 1

        test_data["lane_or_section"] = gui.new_user_lane_input_box.text()

        if not is_valid_lane(test_data["lane_or_section"]):
            test_data["errors"] += "Invalid lane!\n\n"

        else:
            test_data["lane_or_section"] = int(test_data["lane_or_section"])

    if (
        not gui.new_user_tech_radio_button.isChecked()
        and not gui.new_user_service_writer_radio_button.isChecked()
    ):
        test_data["errors"] += "The user must be a Technician or Service Writer!"

    return test_data
