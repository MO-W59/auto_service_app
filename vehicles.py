"""This module handles all of the vehicle events for the application."""

import json
import validate


def new_vehicle_submit(database, gui):
    """Gets information for a new vehicle and passes it to the database for storage."""

    vin = gui.new_vehicle_vin_input_box.text()
    make = gui.new_vehicle_make_input_box.text()
    model = gui.new_vehicle_model_input_box.text()
    year = gui.new_vehicle_year_input_box.text()
    color = gui.new_vehicle_color_input_box.text()
    engine = gui.new_vehicle_engine_input_box.text()
    errors = ""

    if not validate.is_valid_vin(vin):
        errors += "Invalid vin!\n\n"

    if not validate.is_valid_name(make):
        errors += "Invalid make!\n\n"

    if not validate.is_valid_name(model):
        errors += "Invalid model!\n\n"

    if not validate.is_valid_year(year):
        errors += "Invalid year!\n\n"

    if not validate.is_valid_name(color):
        errors += "Invalid color!\n\n"

    if not validate.is_valid_id(engine):
        errors += "Invalid engine!\n\n"

    if errors != "":
        return gui.show_error(errors)

    if database.get_vehicle_data(vin):
        return gui.show_error("There is a vehicle with this VIN already!")

    vehicle_data = {
        "vin": vin,
        "model": model,
        "make": make,
        "year": year,
        "color": color,
        "engine": engine,
        "repair_history": json.dumps([]),
        "repair_request": None,
    }

    database.insert_vehicle(vehicle_data)

    return gui.show_success("Vehicle input successfully.")


def edit_vehicle_submit(database, gui):
    """Gets new information for a vehicle and passes it to the database for storage."""

    current_vin = gui.edit_vehicle_vin_display_label.text()
    checkbox_dispatcher = edit_vehicle_dispatcher(database, gui)
    errors = ""

    # run through dispatcher for errors
    for checkbox in checkbox_dispatcher.values():
        if checkbox["checked"]():
            if not checkbox["validator"](checkbox["input"]()):
                errors += checkbox["error"]

    # if errors display and return

    if errors != "":
        return gui.show_error(errors)

    # run through dispatcher for updates

    for checkbox in checkbox_dispatcher.values():
        if checkbox["checked"]():
            checkbox["updater"](current_vin, checkbox["input"]())

    # show success

    return gui.show_success("Vehicle update successful.")


def edit_vehicle_dispatcher(database, gui):
    """Creates the dictionary of dictionaries that contain the checkbox checked value in
    question, related validate function, related update function, related input variable
    and error message to use when updating user information."""

    checkbox_dispatcher = {
        gui.edit_vehicle_change_make_check_box: {
            "checked": gui.edit_vehicle_change_make_check_box.isChecked,
            "validator": validate.is_valid_name,
            "input": gui.edit_vehicle_make_input_box.text,
            "error": "Invalid make!\n\n",
            "updater": database.update_vehicle_make,
        },
        gui.edit_vehicle_change_model_check_box: {
            "checked": gui.edit_vehicle_change_model_check_box.isChecked,
            "validator": validate.is_valid_name,
            "input": gui.edit_vehicle_model_input_box.text,
            "error": "Invalid model!\n\n",
            "updater": database.update_vehicle_model,
        },
        gui.edit_vehicle_change_year_check_box: {
            "checked": gui.edit_vehicle_change_year_check_box.isChecked,
            "validator": validate.is_valid_year,
            "input": gui.edit_vehicle_year_input_box.text,
            "error": "Invalid year!\n\n",
            "updater": database.update_vehicle_year,
        },
        gui.edit_vehicle_change_color_check_box: {
            "checked": gui.edit_vehicle_change_color_check_box.isChecked,
            "validator": validate.is_valid_name,
            "input": gui.edit_vehicle_color_input_box.text,
            "error": "Invalid color!\n\n",
            "updater": database.update_vehicle_color,
        },
        gui.edit_vehicle_change_engine_check_box: {
            "checked": gui.edit_vehicle_change_engine_check_box.isChecked,
            "validator": validate.is_valid_name,
            "input": gui.edit_vehicle_engine_input_box.text,
            "error": "Invalid engine!\n\n",
            "updater": database.update_vehicle_engine,
        },
    }

    return checkbox_dispatcher


def go_to_new_vehicle_page(database, gui):
    """Takes the user to the new vehicles page."""

    if not database.get_login_status():
        return gui.show_error("You must be logged in to access this page.")

    return gui.widget_stack.setCurrentIndex(14)


def go_to_edit_vehicle_page(database, gui):
    """Gets a vin and takes the user to the edit vehicle page passes vin to database
    to get that vehicles data and passes that data to the GUI to populate the page."""

    if not database.get_login_status():
        return gui.show_error("You must be logged in to access this page.")

    while True:
        vin = gui.show_vin_search_request()

        # If the user clicked cancel
        if vin is False:
            return None

        if not validate.is_valid_vin(vin):
            gui.show_error("Invalid VIN.")

            continue

        vehicle_data = database.get_vehicle_data(vin)

        if not vehicle_data:
            gui.show_error("Vehicle not found.")

            continue

        break

    gui.update_edit_vehicle_page(vehicle_data)

    return gui.widget_stack.setCurrentIndex(15)


def search_repair_history(database, gui):
    """Gets a vin and passes it to the database to get that vehicle's repair history
    then passes it to the GUI to populate the message window."""

    if not database.get_login_status():
        return gui.show_error("You must be logged in to access this function.")

    while True:
        vin_to_search = gui.show_vin_search_request()

        # If the user clicked cancel
        if vin_to_search is False:
            return None

        if not validate.is_valid_vin(vin_to_search):
            gui.show_error("Invalid VIN.")

            continue

        vehicle_data = database.get_vehicle_data(vin_to_search)

        if not vehicle_data:
            gui.show_error("Vehicle not found.")

            continue

        break
    # use json loads to get a list from database return
    repair_history = json.loads(vehicle_data["repair_history"])

    repair_info = f"VIN : {vin_to_search}\n\n--- Pior Repair IDs ---\n\n"

    for repair in repair_history:
        repair_info = repair_info + (f"{repair}\n\n")

    return gui.show_vehicle_repair_history(repair_info)


def go_to_list_of_vehicles_page(database, gui):
    """Takes the user to the list of vehicles page, gets all vehicle data from
    the database and passes it to the GUI to populate the page."""

    if not database.get_login_status():
        return gui.show_error("You must be logged in to access this page.")

    vehicle_data = database.get_all_vehicles()

    vehicle_list = construct_vehicles_list(vehicle_data)

    gui.list_of_vehicles_text_browser.setText(vehicle_list)

    return gui.widget_stack.setCurrentIndex(16)


def construct_vehicles_list(vehicle_data):
    """Constructs a formated string of passed vehicle data for display."""

    vehicle_list = ""

    for vehicle in vehicle_data:
        vehicle_list = vehicle_list + (
            f"VIN : {vehicle['vin']}, Model : {vehicle['model']}, "
            f"Make : {vehicle['make']}, Year : {vehicle['year']}, "
            f"Color : {vehicle['color']}, Engine : {vehicle['engine']}, "
            f"Current Active Repair ID : {vehicle['repair_request']}\n\n"
        )

    return vehicle_list
