"""This module handles all the logic for repair events in the application"""

import json
import datetime
import validate


def new_repair_submit(database, gui):
    """Gets information for a new repair and passes it to the database for storage."""

    service_writer_id = gui.new_repair_service_id_input_box.text()
    technician_id = gui.new_repair_tech_id_input_box.text()
    vin = gui.new_repair_vin_input_box.text()
    drop_off_date = gui.new_repair_current_date_display.text()
    problem_description = gui.new_repair_description_input_box.toPlainText()

    if not validate.is_valid_id(service_writer_id):
        return gui.show_error("Invalid service writer id.")

    if not validate.is_valid_id(technician_id):
        return gui.show_error("Invalid technician id.")

    if not validate.is_valid_vin(vin):
        return gui.show_error("Invalid vin number.")

    if not database.get_vehicle_data(vin):
        return gui.show_error(
            "A vehicle must be in the database to create a repair for it."
        )

    if not validate.is_valid_description(problem_description):
        return gui.show_error("Invalid problem description.")

    if not database.vehicle_is_owned(vin):
        return gui.show_error("The vehicle must first be owned by a customer.")

    if database.has_active_repair(vin):
        return gui.show_error("This vehicle already has an active repair.")

    constructing_suffix = []
    constructing_suffix[:0] = drop_off_date
    repair_id_suffix = ""

    while "/" in constructing_suffix:
        constructing_suffix.remove("/")

    repair_id_suffix = repair_id_suffix.join(constructing_suffix)
    repair_id = vin + repair_id_suffix

    if database.search_for_repair(repair_id):
        return gui.show_error("That Repair ID is already in use.")

    inputs = [
        repair_id,
        0.0,
        0.0,
        0.0,
        drop_off_date,
        None,
        problem_description,
        None,
        [],
        technician_id,
        service_writer_id,
        vin,
    ]

    database.insert_repair(inputs)

    database.update_vehicle_active_repair(vin, repair_id)

    return gui.show_success("New repair input successfuly.")


def edit_repair_submit(database, gui):
    """Gets new information for a repair and passes it to the database for storage."""

    new_service_writer_id = gui.edit_repair_service_id_input_box.text()
    new_tech_id = gui.edit_repair_tech_id_input_box.text()
    new_labor_amount = gui.edit_repair_labor_input_box.text()
    problem_description = gui.edit_repair_problem_description_input_box.toPlainText()
    repair_description = gui.edit_repair_repair_description_input_box.toPlainText()
    repair_id = gui.edit_repair_repair_id_display_label.text()
    old_tech_id = gui.edit_repair_tech_id_display_label.text()
    old_writer_id = gui.edit_repair_service_id_display_label.text()

    if gui.change_writer_check_box.isChecked():
        if not validate.is_valid_id(new_service_writer_id):
            return gui.show_error("Invalid service writer ID.")

    if gui.change_tech_check_box.isChecked():
        if not validate.is_valid_id(new_tech_id):
            return gui.show_error("Invalid technician ID.")

    if gui.change_labor_check_box.isChecked():
        if not validate.is_valid_dollar_amount(new_labor_amount):
            return gui.show_error("Invalid labor value.")

    if not validate.is_valid_description(
        problem_description
    ) or not validate.is_valid_description(repair_description):
        return gui.show_error("Invalid description entered.")

    if gui.change_writer_check_box.isChecked():
        database.update_repair_service_writer(
            repair_id, new_service_writer_id, old_writer_id
        )

    if gui.change_tech_check_box.isChecked():
        database.update_repair_tech(repair_id, new_tech_id, old_tech_id)

    if gui.change_labor_check_box.isChecked():
        database.update_labor_cost(repair_id, new_labor_amount)

        total_cost = calculate_total_cost(repair_id, database)

        database.update_total_repair_cost(repair_id, total_cost)

    database.update_repair_problem(repair_id, problem_description)
    database.update_repair_description(repair_id, repair_description)

    gui.show_success("Repair update successful.")

    repair_data = database.search_for_repair(repair_id)

    return gui.update_edit_repair_displays(repair_data)


def finish_repair_submit(database, gui):
    """Gathers repair information, sets a completion date, passes that to the database for storage,
    then has the database update employee assignments and moves the user to view the completed
    repair page in the gui."""

    pass_confirm = gui.confirm_repair_complete()
    compelting_repair_id = gui.edit_repair_repair_id_display_label.text()
    service_writer_id = gui.edit_repair_service_id_display_label.text()
    tech_id = gui.edit_repair_tech_id_display_label.text()

    if not validate.is_valid_password(pass_confirm):
        return gui.show_error("Invalid password.")

    if not database.is_current_users_password(pass_confirm):
        return gui.show_error("Invalid password.")

    compelted_date = datetime.datetime.today().strftime("%Y/%m/%d")

    database.update_repair_complete_date(compelting_repair_id, compelted_date)

    database.remove_repair_from_writer(compelting_repair_id, service_writer_id)
    database.remove_repair_from_tech(compelting_repair_id, tech_id)

    gui.show_success("Repair completed.")

    repair_data = database.search_for_repair(compelting_repair_id)

    vin = repair_data[11]

    parts_list = construct_repair_parts_list(compelting_repair_id, database)

    database.update_vehicle_completed_repairs(vin)

    gui.update_old_repair_displays(repair_data, parts_list)

    return gui.widget_stack.setCurrentIndex(7)


def add_part_to_repair(database, gui):
    """Gets a part as input and sends it to the database to add to the current repair."""

    repair_id = gui.edit_repair_repair_id_display_label.text()

    while True:
        part_to_add = gui.show_part_id_search_request_add()

        # if the user clicked the cancel button
        if part_to_add is False:
            return

        if not validate.is_valid_id(part_to_add):
            gui.show_error("Invalid Part ID.")

            continue

        if not database.get_part_data(part_to_add):
            gui.show_error("Part not found.")

            continue

        break

    database.update_required_parts_add(repair_id, part_to_add)
    parts_list = construct_repair_parts_list(repair_id, database)

    parts_cost = calculate_parts_cost(repair_id, database)
    database.update_repair_parts_cost(repair_id, parts_cost)

    total_cost = calculate_total_cost(repair_id, database)
    database.update_total_repair_cost(repair_id, total_cost)

    repair_data = database.search_for_repair(repair_id)

    gui.edit_repair_total_repair_cost_display_label.setText(str(repair_data[1]))
    gui.edit_repair_part_cost_display_label.setText(str(repair_data[3]))
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
            return

        if not validate.is_valid_id(part_id_to_remove):
            gui.show_error("Invalid Part ID.")

            continue

        if not database.get_part_data(part_id_to_remove):
            gui.show_error("Part not found.")

            continue

        try:
            database.update_required_parts_remove(repair_id, part_id_to_remove)

        except ValueError:
            gui.show_error("Repair does not have that part currently listed.")

            continue

        break

    parts_list = construct_repair_parts_list(repair_id, database)

    parts_cost = calculate_parts_cost(repair_id, database)
    database.update_repair_parts_cost(repair_id, parts_cost)

    total_cost = calculate_total_cost(repair_id, database)
    database.update_total_repair_cost(repair_id, total_cost)

    repair_data = database.search_for_repair(repair_id)

    gui.edit_repair_part_cost_display_label.setText(str(repair_data[3]))
    gui.edit_repair_total_repair_cost_display_label.setText(str(repair_data[1]))
    gui.edit_repair_list_of_parts_text_browser.setText(parts_list)

    return gui.show_success("Part successfuly removed.")


def go_to_new_repair_page(database, gui):
    """Takes the user to the new repair page and gets current date to display."""

    if not database.get_login_status():
        return gui.show_error("You must be logged in to access this page.")

    drop_off_date = datetime.datetime.today().strftime("%Y/%m/%d")

    gui.new_repair_current_date_display.setText(drop_off_date)

    return gui.widget_stack.setCurrentIndex(4)


def go_to_edit_repair_page(database, gui):
    """Takes the user to the edit repair page, gets information from the database
    based on entered repair id to populate the page with data."""

    if not database.get_login_status():
        return gui.show_error("You must be logged in to access this page.")

    while True:
        requested_repair_id = gui.show_repair_id_search_request()

        # If the user clicked cancel
        if requested_repair_id is False:
            return

        if not validate.is_valid_id(requested_repair_id):
            gui.show_error("Invalid Repair ID.")

            continue

        repair_data = database.search_for_repair(requested_repair_id)

        if not repair_data:
            gui.show_error("Repair not found.")

            continue

        break

    gui.update_edit_repair_displays(repair_data)

    parts_list = construct_repair_parts_list(requested_repair_id, database)

    gui.edit_repair_list_of_parts_text_browser.setText(parts_list)

    return gui.widget_stack.setCurrentIndex(5)


def go_to_active_repairs_page(database, gui):
    """Takes the user to the active repairs page and gets all active repairs
    from the database to populate the page.."""

    if not database.get_login_status():
        return gui.show_error("You must be logged in to access this page.")

    repair_data = database.get_all_repairs()

    list_of_repairs = ""

    for repair in repair_data:
        list_of_repairs = (
            list_of_repairs + f"Repair ID : {repair[0]}, Total Cost : {repair[1]}, "
            f"Labor : {repair[2]}, Parts Cost : {repair[3]}, Drop off Date : {repair[4]}, "
            f"Repair Completed Date : {repair[5]}, Technician ID : {repair[9]}, "
            f"Service Writer ID : {repair[10]}\n\n"
        )

    gui.update_active_repair_list(list_of_repairs)

    return gui.widget_stack.setCurrentIndex(6)


def go_to_old_repair_page(database, gui):
    """Gets a repair id and passes it to the database to get information on an
    old repair, then populates the page with its data."""

    if not database.get_login_status():
        return gui.show_error("You must be logged in to access this page.")

    while True:
        repair_id = gui.show_repair_id_search_request()

        # If the user clicked cancel
        if repair_id is False:
            return

        if not validate.is_valid_id(repair_id):
            gui.show_error("Invalid Repair ID.")

            continue

        repair_data = database.search_for_repair(repair_id)

        if not repair_data:
            gui.show_error("Repair not found.")

            continue

        if repair_data[5] is None:
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

    repair_data = database.search_for_repair(repair_id)

    # use json loads to get a list from the database return value
    part_id_list = json.loads(repair_data[8])

    for part_id in part_id_list:
        part_data = database.get_part_data(part_id)
        parts_list = (
            parts_list
            + f"Part ID : {part_data[0]}, Cost : ${part_data[1]}, Description : {part_data[2]}\n\n"
        )

    return parts_list


def calculate_total_cost(repair_id, database):
    """Gets information from database based on passed repair id and then
    calculates the total cost of a repair with that data."""

    repair_data = database.search_for_repair(repair_id)

    parts_cost = calculate_parts_cost(repair_id, database)

    labor_cost = repair_data[2]

    total_cost = parts_cost + labor_cost

    return total_cost


def calculate_parts_cost(repair_id, database):
    """Gets information from the data base to calculate the total cost of parts."""

    parts_cost = 0.0

    repair_data = database.search_for_repair(repair_id)

    part_id_list = json.loads(repair_data[8])

    for part_id in part_id_list:
        part_data = database.get_part_data(part_id)

        parts_cost = parts_cost + part_data[1]

    return parts_cost
