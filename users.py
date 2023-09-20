"""This module contains all the logic to handle user events in the application."""

import json
from passlib.hash import sha512_crypt
import validate


def login_submit(database, gui):
    """Checks login status in database, validates inputs via validate, submits values
    to Database."""

    if database.get_login_status():
        return gui.show_error("You are already logged in!")

    input_user = gui.username_login_input_box.text()
    input_pass = gui.password_login_input_box.text()

    if not validate.is_valid_username(input_user) and validate.is_valid_password(
        input_pass
    ):
        return gui.show_error("Invalid username or password!")

    if database.is_valid_login_query(input_user, input_pass):
        return gui.show_success("Login successful.")

    return gui.show_error("Invalid username or password!")


def new_user_submit(database, gui):
    """Gets information for a new user and passes it to the database for storage."""

    new_user = gui.username_new_user_input_box.text()
    new_pass = gui.password_new_user_input_box.text()
    confirm_new_pass = gui.confirm_password_new_user_input_box.text()
    new_name = gui.new_user_name_input_box.text()
    new_team = gui.new_user_team_input_box.text()
    section_or_lane = None
    target_table = None
    assigned_repairs = []
    has_error = False
    errors = ""

    if (
        not validate.is_valid_username(new_user)
        or not validate.is_valid_password(new_pass)
        or not validate.is_valid_password(confirm_new_pass)
    ):
        has_error = True
        errors += "Invalid username or password!\n\n"

    if database.is_username_in_use(new_user):
        has_error = True
        errors += "Username already in use!\n\n"

    if not new_pass == confirm_new_pass:
        has_error = True
        errors += "Passwords do not match!\n\n"

    if not validate.is_valid_name(new_name):
        has_error = True
        errors += "Invalid name!\n\n"

    if not validate.is_valid_team(new_team):
        has_error = True
        errors += "Invalid team!\n\n"

    if gui.new_user_tech_radio_button.isChecked():
        target_table = "technicians"

        section_or_lane = gui.new_user_section_input_box.text()

        if not validate.is_valid_name(section_or_lane):
            has_error = True
            errors += "Invalid section!\n\n"

    if gui.new_user_service_writer_radio_button.isChecked():
        target_table = "service_writers"

        section_or_lane = gui.new_user_lane_input_box.text()

        if not validate.is_valid_lane(section_or_lane):
            has_error = True
            errors += "Invalid lane!\n\n"

    if has_error:
        return gui.show_error(errors)

    int(section_or_lane)

    hashed_pass = sha512_crypt.hash(new_pass)

    user_id = database.gen_id(target_table)

    inputs = [
        target_table,
        user_id,
        new_user,
        hashed_pass,
        new_name,
        new_team,
        section_or_lane,
        assigned_repairs,
    ]

    database.insert_user(inputs)

    return gui.show_success("User input successfuly.")


def update_password_submit(database, gui):
    """Gets a new password for the user and passes it to the database for storage."""

    username = gui.update_password_username_input_box.text()
    old_pass = gui.old_password_input_box.text()
    new_pass = gui.new_password_input_box.text()
    confirm_new_pass = gui.confirm_new_password_input_box.text()

    if not validate.is_valid_username(username) or not validate.is_valid_password(
        old_pass
    ):
        return gui.show_error("Invalid username or password!")

    if new_pass != confirm_new_pass:
        return gui.show_error("New passwords do not match!")

    if not validate.is_valid_password(new_pass):
        return gui.show_error("New password is invalid!")

    if old_pass == new_pass:
        return gui.show_error("New password can not be the same as the old password!")

    if database.update_pass(username, old_pass, new_pass):
        return gui.show_success("Password update successful.")

    return gui.show_error("Invalid username or password!")


def update_user_submit(database, gui):
    """Gets information to update a user then passes it to the database for storage."""

    input_pass = gui.update_user_password_input_box.text()
    target_id = gui.update_user_user_id_display_label.text()

    if not validate.is_valid_password:
        return gui.show_error("Invalid password.")

    if not database.is_current_users_password(input_pass):
        return gui.show_error("Invalid password.")

    if gui.update_user_change_name_check_box.isChecked():
        new_name = gui.update_user_name_input_box.text()

        if not validate.is_valid_name(new_name):
            return gui.show_error("Invalid name input.")

    if gui.update_user_change_team_check_box.isChecked():
        new_team = gui.update_user_team_input_box.text()

        if not validate.is_valid_team(new_team):
            return gui.show_error("Invalid team input.")

    if (
        gui.update_user_tech_radio_button.isChecked()
        and gui.update_user_change_section_check_box.isChecked()
    ):
        new_lane_or_section = gui.update_user_section_input_box.text()

        if not validate.is_valid_name(new_lane_or_section):
            return gui.show_error("Invalid section input.")

    if (
        gui.update_user_service_writer_radio_button.isChecked()
        and gui.update_user_change_lane_check_box.isChecked()
    ):
        new_lane_or_section = gui.update_user_lane_input_box.text()

        if not validate.is_valid_lane(new_lane_or_section):
            return gui.show_error("Invalid lane input.")

    if gui.update_user_change_name_check_box.isChecked():
        database.update_user_name(target_id, new_name)

    if gui.update_user_change_team_check_box.isChecked():
        database.update_user_team(target_id, new_team)

    if (
        gui.update_user_change_section_check_box.isChecked()
        and gui.update_user_tech_radio_button.isChecked()
    ):
        database.update_user_section(target_id, new_lane_or_section)

    if (
        gui.update_user_service_writer_radio_button.isChecked()
        and gui.update_user_change_lane_check_box.isChecked()
    ):
        database.update_user_lane(target_id, new_lane_or_section)

    gui.show_success("Update successful, click ok to see updated data.")

    user_data = database.search_for_user(target_id)

    information_to_display = user_string(user_data)

    return gui.show_user_search(information_to_display)


def go_to_login_page(gui):
    """Takes user to the login page."""

    gui.widget_stack.setCurrentIndex(0)


def logout_user(database, gui):
    """Passes false to the login status in the database if the user is logged in,
    then moves them to the login page."""

    if not database.get_login_status():
        return gui.show_error("Unable to logout, you are currently not logged in.")

    database.set_login_status(False)

    gui.show_success("Logout successful.")

    return gui.widget_stack.setCurrentIndex(0)


def go_to_new_user_page(gui):
    """Takes the user to the new user page."""

    gui.widget_stack.setCurrentIndex(1)


def go_to_update_password_page(database, gui):
    """Takes the user to the update password page."""

    if not database.get_login_status():
        return gui.show_error("You must be logged in to access this page.")

    return gui.widget_stack.setCurrentIndex(2)


def search_for_user(database, gui):
    """Gets a user id and passes it to the database to get that users data."""

    if not database.get_login_status():
        return gui.show_error("You must be logged in to access this function.")

    while True:
        id_to_search = gui.show_user_id_search_request()

        # If the user clicked cancel
        if id_to_search is False:
            return

        if not validate.is_valid_id(id_to_search):
            gui.show_error("Invalid User ID.")

            continue

        user_data = database.search_for_user(id_to_search)

        if not user_data:
            gui.show_error("User not found!")

            continue

        break

    information_to_display = user_string(user_data)

    return gui.show_user_search(information_to_display)


def go_to_update_user_page(database, gui):
    """Takes the user to the update user page."""

    if not database.get_login_status():
        return gui.show_error("You must be logged in to access this page.")

    while True:
        id_to_update = gui.show_user_id_search_request()

        # If the user clicked cancel
        if id_to_update is False:
            return

        if not validate.is_valid_id(id_to_update):
            gui.show_error("Invalid User ID.")

            continue

        user_data = database.search_for_user(id_to_update)

        if not user_data:
            gui.show_error("User not found!")

            continue

        break

    gui.update_user_update_displays(user_data)

    return gui.widget_stack.setCurrentIndex(3)


def user_string(user_data):
    """Takes user data and returns a formated string for display of that users
    data."""

    repair_data = json.loads(user_data[6])

    informaion_to_display = (
        f"User ID : {user_data[0]}\nUsername : {user_data[1]}\n"
        f"Name : {user_data[3]}\nTeam : {user_data[4]}\n"
        f"Lane/Section : {user_data[5]}\n\n"
        f"--- Assigned Repairs ---\n\n"
    )

    for repair in repair_data:
        informaion_to_display = informaion_to_display + f"{repair}\n\n"

    return informaion_to_display
