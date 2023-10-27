"""This module contains all the logic for handling parts events for the application."""

import validate

NO_LOGIN_MSG = "You must be logged in to access this page."


def create_part_submit(database, gui):
    """Creates new part from inputs and passed to database for storage."""

    part_id = gui.new_part_part_id_input_box.text()
    part_cost = gui.new_part_part_cost_input_box.text()
    part_descpition = gui.new_part_description_input_box.text()
    errors = ""

    if not validate.is_valid_id(part_id):
        errors += "Invaild part id!\n\n"

    if not validate.is_valid_dollar_amount(part_cost):
        errors += "Invalid part cost!\n\n"

    if not validate.is_valid_description(part_descpition):
        errors += "Invalid description!\n\n"

    if errors != "":
        return gui.show_error(errors)

    if database.get_part_data(part_id):
        return gui.show_error("That part ID is already in use!")

    part_data = {
        "part_id": part_id,
        "part_cost": part_cost,
        "part_description": part_descpition,
    }
    database.insert_part(part_data)

    gui.reset_new_part_page()

    gui.show_success("Part input successfully.")

    return go_to_edit_part_page(database, gui, part_id)


def edit_part_submit(database, gui):
    """Gets new information for a stored part and passes it to the database for storage."""

    part_id = gui.edit_part_id_display_label.text()
    new_part_cost = gui.edit_part_part_cost_input_box.text()
    new_part_description = gui.edit_part_description_input_box.text()
    errors = ""

    if not validate.is_valid_dollar_amount(new_part_cost):
        errors += "Invalid part cost!\n\n"

    if not validate.is_valid_description(new_part_description):
        errors += "Invalid part description!\n\n"

    if errors != "":
        return gui.show_error(errors)

    if gui.edit_part_change_cost_check_box.isChecked():
        database.update_part_cost(part_id, new_part_cost)

    if gui.edit_part_change_description_check_box.isChecked():
        database.update_part_description(part_id, new_part_description)

    gui.reset_edit_part_page()

    return gui.show_success("Part update successful.")


def go_to_new_part_page(database, gui):
    """Takes the user to the new parts page."""

    if not database.get_login_status():
        return gui.show_error(NO_LOGIN_MSG)

    gui.reset_new_part_page()

    return gui.widget_stack.setCurrentIndex(8)


def go_to_edit_part_page(database, gui, part_id=None):
    """Gets a part id to edit and passes it to the database to get
    that part's information then passes the data to the GUI to update
    the page."""

    if not database.get_login_status():
        return gui.show_error(NO_LOGIN_MSG)

    if part_id is None:
        while True:
            part_id = gui.show_id_search_request(
                "Search Part", "Input Part ID to edit:"
            )

            # If user clicked cancel
            if part_id is False:
                return None

            if not validate.is_valid_id(part_id):
                gui.show_error("Invalid Part ID.")

                continue

            part_data = database.get_part_data(part_id)

            if not part_data:
                gui.show_error("Part not found.")

                continue

            break

    else:
        part_data = database.get_part_data(part_id)

    gui.update_edit_part_page(part_data)

    gui.reset_edit_part_page()

    return gui.widget_stack.setCurrentIndex(9)


def go_to_list_of_parts_page(database, gui):
    """Takes the user to the list of parts page and pulls all
    part data from the database to pass the data to the GUI."""

    if not database.get_login_status():
        return gui.show_error(NO_LOGIN_MSG)

    parts_data = database.get_all_parts_in_database()

    parts_list = ""

    for part in parts_data:
        parts_list = (
            parts_list
            + f"Part ID : {part['part_id']}, Cost : ${part['part_cost']:,.2f}, "
            f"Description : {part['part_description']}\n\n"
        )

    gui.list_of_parts_text_browser.setText(parts_list)

    return gui.widget_stack.setCurrentIndex(10)
