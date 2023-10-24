"""This module handles all the logic for repair events in the application"""

import datetime
import validate

NO_LOGIN_MSG = "You must be logged in to access this page."


def new_repair_submit(database, gui):
    """Gets information for a new repair and passes it to the database for storage."""

    writer_id = gui.new_repair_service_id_input_box.text()
    tech_id = gui.new_repair_tech_id_input_box.text()
    vin = gui.new_repair_vin_input_box.text()
    drop_off_date = gui.new_repair_current_date_display.text()
    problem_description = gui.new_repair_description_input_box.toPlainText()
    errors = ""

    if not validate.is_valid_id(writer_id):
        errors += "Invalid service writer id.\n\n"

    if not validate.is_valid_id(tech_id):
        errors += "Invalid technician id.\n\n"

    if not validate.is_valid_vin(vin):
        errors += "Invalid vin number.\n\n"

    if not validate.is_valid_description(problem_description):
        errors += "Invalid problem description.\n\n"

    if errors != "":
        return gui.show_error(errors)

    constructing_suffix = []
    constructing_suffix[:0] = drop_off_date
    repair_id_suffix = ""

    while "/" in constructing_suffix:
        constructing_suffix.remove("/")

    repair_id_suffix = repair_id_suffix.join(constructing_suffix)
    repair_id = vin + repair_id_suffix

    if (
        database.search_for_user(tech_id)["is_tech"] != 1
        or database.search_for_user(writer_id)["is_writer"] != 1
    ):
        errors += "Employee ID that does not match their role (tech/writer).\n\n"

    if not database.vehicle_is_owned(vin):
        errors += "The vehicle must first be owned by a customer.\n\n"

    if database.has_active_repair(vin):
        errors += "This vehicle already has an active repair.\n\n"

    if not database.get_vehicle_data(vin):
        errors += "A vehicle must be in the database to create a repair for it.\n\n"

    if database.search_for_repair(repair_id):
        errors += "That Repair ID is already in use.\n\n"

    if errors != "":
        return gui.show_error(errors)

    repair_data = {
        "repair_id": repair_id,
        "total_cost": 0.0,
        "labor": 0.0,
        "parts_cost": 0.0,
        "drop_off_date": drop_off_date,
        "problem_description": problem_description,
        "tech_id": tech_id,
        "writer_id": writer_id,
        "vin": vin,
    }

    database.insert_repair(repair_data)

    database.update_vehicle_active_repair(vin, repair_id)

    gui.reset_new_repair_page()

    gui.show_success("New repair input successfuly.")

    return go_to_edit_repair_page(database, gui, repair_id)


def edit_repair_submit(database, gui):
    """Gets new information for a repair and passes it to the database for storage."""

    checkbox_dispatcher = edit_repair_dispatcher(database, gui)
    repair_id = gui.edit_repair_repair_id_display_label.text()
    errors = ""

    # run through dispatcher for errors

    for checkbox in checkbox_dispatcher.values():
        if checkbox["checked"]():
            if not checkbox["validator"](checkbox["input"]()):
                errors += checkbox["error"]

    # if errors display and return

    if errors != "":
        return gui.show_error(errors)

    # ensure passed employee ids apply to their roles, if error display and return

    change_writer_checkbox = checkbox_dispatcher[gui.change_writer_check_box]
    change_tech_checkbox = checkbox_dispatcher[gui.change_tech_check_box]

    if (
        change_tech_checkbox["checked"]()
        and database.search_for_user(change_tech_checkbox["input"]())["is_tech"] != 1
        or change_tech_checkbox["checked"]()
        and database.search_for_user(change_writer_checkbox["input"]())["is_writer"]
        != 1
    ):
        return gui.show_error(
            "Employee ID entered that does not match their role (tech/writer).\n\n"
        )

    # if checked update via dispatch

    for checkbox in checkbox_dispatcher.values():
        if checkbox["checked"]():
            checkbox["updater"](repair_id, checkbox["input"]())

    total_cost = calculate_total_cost(repair_id, database)

    database.update_total_repair_cost(repair_id, total_cost)

    gui.show_success("Repair update successful.")

    repair_data = database.search_for_repair(repair_id)

    gui.reset_edit_repair_page()

    return gui.update_edit_repair_displays(repair_data)


def edit_repair_dispatcher(database, gui):
    """Creates a dictionary of dictionaries that contain the checkbox checked and field has changed
    value in question, related validation fuctions, related update functions, related input fields
    and error messages to use when updating repair data."""

    checkbox_dispatcher = {
        gui.change_writer_check_box: {
            "checked": gui.change_writer_check_box.isChecked,
            "validator": validate.is_valid_id,
            "input": gui.edit_repair_service_id_input_box.text,
            "error": "Invalid service writer ID!\n\n",
            "updater": database.update_repair_service_writer,
        },
        gui.change_tech_check_box: {
            "checked": gui.change_tech_check_box.isChecked,
            "validator": validate.is_valid_id,
            "input": gui.edit_repair_tech_id_input_box.text,
            "error": "Invalid technician ID!\n\n",
            "updater": database.update_repair_tech,
        },
        gui.change_labor_check_box: {
            "checked": gui.change_labor_check_box.isChecked,
            "validator": validate.is_valid_dollar_amount,
            "input": gui.edit_repair_labor_input_box.text,
            "error": "Invalid labor value!\n\n",
            "updater": database.update_labor_cost,
        },
        gui.edit_repair_problem_description_input_box: {
            "checked": gui.get_repair_problem_has_changed,
            "validator": validate.is_valid_description,
            "input": gui.edit_repair_problem_description_input_box.toPlainText,
            "error": "Invalid description entered!\n\n",
            "updater": database.update_repair_problem,
        },
        gui.edit_repair_repair_description_input_box: {
            "checked": gui.get_repair_repair_has_changed,
            "validator": validate.is_valid_description,
            "input": gui.edit_repair_repair_description_input_box.toPlainText,
            "error": "Invalid description entered!\n\n",
            "updater": database.update_repair_description,
        },
    }

    return checkbox_dispatcher


def finish_repair_submit(database, gui):
    """Gathers repair information, sets a completion date, passes that to the database for storage,
    then has the database update employee assignments and moves the user to view the completed
    repair page in the gui."""

    repair_id = gui.edit_repair_repair_id_display_label.text()

    while True:
        pass_confirm = gui.confirm_repair_complete()

        # if user clicked cancel button
        if pass_confirm is False:
            return None

        if pass_confirm is True:
            gui.show_error("No password entered!")

        if not validate.is_valid_password(pass_confirm):
            gui.show_error("Invalid password!")

            continue

        if not database.is_current_users_password(pass_confirm):
            gui.show_error("Invalid password!")

            continue

        break

    compelted_date = datetime.datetime.today().strftime("%Y/%m/%d")

    database.update_repair_complete_date(repair_id, compelted_date)

    gui.show_success("Repair completed.")

    repair_data = database.search_for_repair(repair_id)

    database.update_vehicle_active_repair(repair_data["vehicle"])

    parts_list = construct_repair_parts_list(repair_id, database)

    gui.update_old_repair_displays(repair_data, parts_list)

    gui.reset_edit_repair_page_finish()

    return gui.widget_stack.setCurrentIndex(7)


def add_part_to_repair(database, gui):
    """Gets a part as input and sends it to the database to add to the current repair."""

    repair_id = gui.edit_repair_repair_id_display_label.text()

    while True:
        part_to_add = gui.show_part_id_search_request_add()

        # if the user clicked the cancel button
        if part_to_add is False:
            return None

        if not validate.is_valid_id(part_to_add):
            gui.show_error("Invalid Part ID.")

            continue

        if not database.get_part_data(part_to_add):
            gui.show_error("Part not found.")

            continue

        break

    database.insert_part_listing(repair_id, part_to_add)
    parts_list = construct_repair_parts_list(repair_id, database)

    parts_cost = calculate_parts_cost(repair_id, database)
    database.update_repair_parts_cost(repair_id, parts_cost)

    total_cost = calculate_total_cost(repair_id, database)
    database.update_total_repair_cost(repair_id, total_cost)

    repair_data = database.search_for_repair(repair_id)

    gui.edit_repair_total_repair_cost_display_label.setText(
        str(repair_data["total_cost"])
    )
    gui.edit_repair_part_cost_display_label.setText(str(repair_data["parts_cost"]))
    gui.edit_repair_list_of_parts_text_browser.setText(parts_list)

    return gui.show_success("Part added successfuly.")


def remove_part_from_repair(database, gui):
    """Gets information on what part to remoe from the repair then passes
    that information to the database for update."""

    repair_id = gui.edit_repair_repair_id_display_label.text()

    while True:
        part_id_to_remove = gui.show_part_id_search_request_remove()

        # if the user hit the cancel button
        if part_id_to_remove is False:
            return None

        if not validate.is_valid_id(part_id_to_remove):
            gui.show_error("Invalid Part ID.")

            continue

        if not database.get_part_data(part_id_to_remove):
            gui.show_error("Part not found.")

            continue

        if not database.drop_part_listing(repair_id, part_id_to_remove):
            gui.show_error("Repair does not have that part currently listed.")

            continue

        break

    parts_list = construct_repair_parts_list(repair_id, database)

    parts_cost = calculate_parts_cost(repair_id, database)
    database.update_repair_parts_cost(repair_id, parts_cost)

    total_cost = calculate_total_cost(repair_id, database)
    database.update_total_repair_cost(repair_id, total_cost)

    repair_data = database.search_for_repair(repair_id)

    gui.edit_repair_part_cost_display_label.setText(str(repair_data["parts_cost"]))
    gui.edit_repair_total_repair_cost_display_label.setText(
        str(repair_data["total_cost"])
    )
    gui.edit_repair_list_of_parts_text_browser.setText(parts_list)

    return gui.show_success("Part successfuly removed.")


def go_to_new_repair_page(database, gui):
    """Takes the user to the new repair page and gets current date to display."""

    if not database.get_login_status():
        return gui.show_error(NO_LOGIN_MSG)

    drop_off_date = datetime.datetime.today().strftime("%Y/%m/%d")

    gui.new_repair_current_date_display.setText(drop_off_date)

    gui.reset_new_repair_page()

    return gui.widget_stack.setCurrentIndex(4)


def go_to_edit_repair_page(database, gui, requested_repair_id=None):
    """Takes the user to the edit repair page, gets information from the database
    based on entered repair id to populate the page with data."""

    if not database.get_login_status():
        return gui.show_error(NO_LOGIN_MSG)

    if requested_repair_id is None:
        repair_data = get_repair_data_loop(database, gui)

        if repair_data is None:
            return None

    else:
        repair_data = database.search_for_repair(requested_repair_id)

    gui.update_edit_repair_displays(repair_data)

    parts_list = construct_repair_parts_list(requested_repair_id, database)

    gui.edit_repair_list_of_parts_text_browser.setText(parts_list)

    gui.reset_edit_repair_page()

    return gui.widget_stack.setCurrentIndex(5)


def get_repair_data_loop(database, gui):
    """Loop to obtain a repair id from the user."""

    while True:
        requested_repair_id = gui.show_repair_id_search_request()

        # If the user clicked cancel
        if requested_repair_id is False:
            return None

        if not validate.is_valid_id(requested_repair_id):
            gui.show_error("Invalid Repair ID.")

            continue

        repair_data = database.search_for_repair(requested_repair_id)

        if repair_data["repair_completed_date"] is not None:
            gui.show_error("That repair has already been completed.")

            continue

        if not repair_data:
            gui.show_error("Repair not found.")

            continue

        return repair_data


def go_to_active_repairs_page(database, gui):
    """Takes the user to the active repairs page and gets all active repairs
    from the database to populate the page.."""

    if not database.get_login_status():
        return gui.show_error(NO_LOGIN_MSG)

    repair_data = database.get_all_active_repairs()

    list_of_repairs = ""

    for repair in repair_data:
        list_of_repairs = (
            list_of_repairs
            + f"Repair ID : {repair['repair_id']}, Total Cost : ${repair['total_cost']:.2f}, "
            f"Labor : ${repair['labor']:.2f}, Parts Cost : ${repair['parts_cost']:.2f}, "
            f"Drop off Date : {repair['drop_off_date']}, "
            f"Technician ID : {repair['technician']}, "
            f"Service Writer ID : {repair['service_writer']}\n\n"
        )

    gui.update_active_repair_list(list_of_repairs)

    return gui.widget_stack.setCurrentIndex(6)


def go_to_old_repair_page(database, gui):
    """Gets a repair id and passes it to the database to get information on an
    old repair, then populates the page with its data."""

    if not database.get_login_status():
        return gui.show_error(NO_LOGIN_MSG)

    while True:
        repair_id = gui.show_repair_id_search_request()

        # If the user clicked cancel
        if repair_id is False:
            return None

        if not validate.is_valid_id(repair_id):
            gui.show_error("Invalid Repair ID.")

            continue

        repair_data = database.search_for_repair(repair_id)

        if not repair_data:
            gui.show_error("Repair not found.")

            continue

        if repair_data["repair_completed_date"] is None:
            gui.show_error("That repair is still underway.")

            continue

        break

    list_of_parts = construct_repair_parts_list(repair_id, database)

    gui.update_old_repair_displays(repair_data, list_of_parts)

    return gui.widget_stack.setCurrentIndex(7)


def construct_repair_parts_list(repair_id, database):
    """Constructs a string containing the parts needed to complete
    a repair based of repair id and data from database."""

    parts_list = ""

    part_listings = database.get_repair_part_listings(repair_id)

    for listing in part_listings:
        part_data = database.get_part_data(listing["part_id"])
        parts_list = (
            parts_list
            + f"Part ID : {part_data['part_id']}, Cost : ${part_data['part_cost']:.2f}, "
            f"Description : {part_data['part_description']}\n\n"
        )

    return parts_list


def calculate_total_cost(repair_id, database):
    """Gets information from database based on passed repair id and then
    calculates the total cost of a repair with that data."""

    repair_data = database.search_for_repair(repair_id)

    parts_cost = calculate_parts_cost(repair_id, database)

    labor_cost = repair_data["labor"]

    total_cost = parts_cost + labor_cost

    return total_cost


def calculate_parts_cost(repair_id, database):
    """Gets information from the data base to calculate the total cost of parts."""

    parts_cost = 0.0

    part_listings = database.get_repair_part_listings(repair_id)

    for listing in part_listings:
        part_data = database.get_part_data(listing["part_id"])

        parts_cost = parts_cost + part_data["part_cost"]

    return parts_cost
