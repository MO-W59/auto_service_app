"""This module contains all the logic to handle user events in the application."""


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

    username = gui.username_new_user_input_box.text()
    pwrd = gui.password_new_user_input_box.text()
    confirm_pwrd = gui.confirm_password_new_user_input_box.text()
    name = gui.new_user_name_input_box.text()
    team = gui.new_user_team_input_box.text()
    lane_or_section = None
    errors = ""

    if (
        not validate.is_valid_username(username)
        or not validate.is_valid_password(pwrd)
        or not validate.is_valid_password(confirm_pwrd)
    ):
        errors += "Invalid username or password!\n\n"

    if not pwrd == confirm_pwrd:
        errors += "Passwords do not match!\n\n"

    if not validate.is_valid_name(name):
        errors += "Invalid name!\n\n"

    if not validate.is_valid_team(team):
        errors += "Invalid team!\n\n"

    if gui.new_user_tech_radio_button.isChecked():
        is_tech = 1
        is_writer = 0

        lane_or_section = gui.new_user_section_input_box.text()

        if not validate.is_valid_name(lane_or_section):
            errors += "Invalid section!\n\n"

    if gui.new_user_service_writer_radio_button.isChecked():
        is_tech = 0
        is_writer = 1

        lane_or_section = gui.new_user_lane_input_box.text()

        if not validate.is_valid_lane(lane_or_section):
            errors += "Invalid lane!\n\n"

        else:
            lane_or_section = int(lane_or_section)

    if errors != "":
        return gui.show_error(errors)

    if database.is_username_in_use(username):
        return gui.show_error("Username already in use!")

    hash_pwrd = sha512_crypt.hash(pwrd)

    user_data = {
        "username": username,
        "hash_pwrd": hash_pwrd,
        "name": name,
        "team": team,
        "lane_or_section": lane_or_section,
        "is_tech": is_tech,
        "is_writer": is_writer,
    }

    database.insert_user(user_data)

    return gui.show_success("User input successfuly.")


def update_password_submit(database, gui):
    """Gets a new password for the user and passes it to the database for storage."""

    username = gui.update_password_username_input_box.text()
    old_pass = gui.old_password_input_box.text()
    new_pass = gui.new_password_input_box.text()
    confirm_new_pass = gui.confirm_new_password_input_box.text()
    errors = ""

    if not validate.is_valid_username(username) or not validate.is_valid_password(
        old_pass
    ):
        errors += "Invalid username or password!\n\n"

    if new_pass != confirm_new_pass:
        errors += "New passwords do not match!\n\n"

    if not validate.is_valid_password(new_pass):
        errors += "New password is invalid!\n\n"

    if old_pass == new_pass:
        errors += "New password can not be the same as the old password!\n\n"

    if errors != "":
        return gui.show_error(errors)

    if not database.is_current_users_password(old_pass):
        return gui.show_error("Invalid username or password!")

    database.update_pass(sha512_crypt.hash(new_pass))
    return gui.show_success("Password update successful.")


def update_user_submit(database, gui):
    """Gets information to update a user then passes it to the database for storage."""

    input_pass = gui.update_user_password_input_box.text()
    target_id = gui.update_user_user_id_display_label.text()
    checkbox_dispatcher = update_user_dispatcher(database, gui)
    errors = ""

    if not validate.is_valid_password(input_pass):
        errors += "Invalid password!\n\n"

    # run through dispatcher for errors

    for checkbox in checkbox_dispatcher.values():
        if checkbox["checked"]():
            if not checkbox["validator"](checkbox["input"]()):
                errors += checkbox["error"]

    # if errors display errors and return

    if errors != "":
        return gui.show_error(errors)

    if not database.is_current_users_password(input_pass):
        return gui.show_error("Invalid password!")

    # run through dispatcher for updates

    for checkbox in checkbox_dispatcher.values():
        if checkbox["checked"]():
            checkbox["updater"](target_id, checkbox["input"]())

    # show success

    gui.show_success("Update successful, click ok to see updated data.")

    user_data = database.search_for_user(target_id)

    information_to_display = user_string(database, user_data)

    gui.update_user_update_displays(user_data)

    return gui.show_user_search(information_to_display)


def update_user_dispatcher(database, gui):
    """Creates the dictionary of dictionaries that contain the checkbox checked value in
    question, related validate function, related update function, related input variable
    and error message to use when updating user information."""

    checkbox_dispatcher = {
        gui.update_user_change_name_check_box: {
            "checked": gui.update_user_change_name_check_box.isChecked,
            "validator": validate.is_valid_name,
            "input": gui.update_user_name_input_box.text,
            "error": "Invalid name!\n\n",
            "updater": database.update_user_name,
        },
        gui.update_user_change_team_check_box: {
            "checked": gui.update_user_change_team_check_box.isChecked,
            "validator": validate.is_valid_team,
            "input": gui.update_user_team_input_box.text,
            "error": "Invalid team!\n\n",
            "updater": database.update_user_team,
        },
        gui.update_user_change_section_check_box: {
            "checked": lambda: all(
                list(
                    (
                        gui.update_user_tech_radio_button.isChecked(),
                        gui.update_user_change_section_check_box.isChecked(),
                    )
                )
            ),
            "validator": validate.is_valid_name,
            "input": gui.update_user_section_input_box.text,
            "error": "Invalid section!\n\n",
            "updater": database.update_user_lane_or_section,
        },
        gui.update_user_change_lane_check_box: {
            "checked": lambda: all(
                list(
                    (
                        gui.update_user_service_writer_radio_button.isChecked(),
                        gui.update_user_change_lane_check_box.isChecked(),
                    )
                )
            ),
            "validator": validate.is_valid_lane,
            "input": gui.update_user_lane_input_box.text,
            "error": "Invalid lane!\n\n",
            "updater": database.update_user_lane_or_section,
        },
    }

    return checkbox_dispatcher


def go_to_login_page(gui):
    """Takes user to the login page."""

    gui.widget_stack.setCurrentIndex(0)


def logout_user(database, gui):
    """Passes false to the login status in the database if the user is logged in,
    then moves them to the login page."""

    if not database.get_login_status():
        return gui.show_error("Unable to logout, you are currently not logged in.")

    database.set_login_status(False)
    database.set_current_user(None)

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
            return None

        if not validate.is_valid_id(id_to_search):
            gui.show_error("Invalid User ID.")

            continue

        user_data = database.search_for_user(id_to_search)

        if not user_data:
            gui.show_error("User not found!")

            continue

        break

    information_to_display = user_string(database, user_data)

    return gui.show_user_search(information_to_display)


def go_to_update_user_page(database, gui):
    """Takes the user to the update user page."""

    if not database.get_login_status():
        return gui.show_error("You must be logged in to access this page.")

    while True:
        id_to_update = gui.show_user_id_search_request()

        # If the user clicked cancel
        if id_to_update is False:
            return None

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


def show_all_users(database, gui):
    """Gets user data from Database and passes it to GUI message box for user
    to see a list of users."""

    if not database.get_login_status():
        return gui.show_error("You must be logged in to access this page.")

    user_list = list_users(database.get_all_users())

    return gui.show_user_search(user_list)


def list_users(user_data):
    """Creates a string listing users simple data(id, name, lane/section)"""

    user_list = ""

    for user in user_data:
        user_list = (
            user_list + f"User ID : {user['employee_id']}, Name : {user['name']}, "
            f"Lane/Section : {user['lane_or_section']}\n\n"
        )

    return user_list


def user_string(database, user_data):
    """Takes user data and returns a formated string for display of that users
    data."""

    repair_data = database.get_repairs_assigned(user_data["employee_id"])
    print(repair_data)

    informaion_to_display = (
        f"User ID : {user_data['employee_id']}\nUsername : {user_data['username']}\n"
        f"Name : {user_data['name']}\nTeam : {user_data['team']}\n"
        f"Lane/Section : {user_data['lane_or_section']}\n\n"
        f"--- Assigned Repairs ---\n\n"
    )

    for repair in repair_data:
        informaion_to_display = informaion_to_display + f"{repair['repair_id']}\n\n"

    return informaion_to_display
