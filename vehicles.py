"""This module handles all of the vehicle events for the application."""

import validate

NO_LOGIN_MSG = "You must be logged in to access this page."


def new_vehicle_submit(database, gui):
    """Gets information for a new vehicle and passes it to the database for storage."""

    # Get new vehicle info from GUI
    vin = gui.new_vehicle_vin_input_box.text()
    make = gui.new_vehicle_make_input_box.text()
    model = gui.new_vehicle_model_input_box.text()
    year = gui.new_vehicle_year_input_box.text()
    color = gui.new_vehicle_color_input_box.text()
    engine = gui.new_vehicle_engine_input_box.text()
    errors = ""

    # validate for proper format, types ect
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

    # Show any errors collected and return
    if errors != "":
        return gui.show_error(errors)

    # Check if input vin is in use, show error and return
    if database.get_vehicle_data(vin):
        return gui.show_error("There is a vehicle with this VIN already!")

    # Construct vehicle
    vehicle_data = {
        "vin": vin,
        "model": model,
        "make": make,
        "year": year,
        "color": color,
        "engine": engine,
        "repair_request": None,
        "owner": None,
    }

    # Pass vehicle to database, reset page, show success, go to edit page for that vin
    database.insert_vehicle(vehicle_data)

    gui.reset_new_vehicle_page()

    gui.show_success("Vehicle input successfully.")

    return go_to_edit_vehicle_page(database, gui, vin)


def edit_vehicle_submit(database, gui):
    """Gets new information for a vehicle and passes it to the database for storage."""

    # Get vin from gui, setup dispatcher
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

    # show success, reset checkboxes
    gui.reset_edit_vehicle_page()

    return gui.show_success("Vehicle update successful.")


def edit_vehicle_dispatcher(database, gui):
    """Creates the dictionary of dictionaries that contain the checkbox checked value in
    question, related validate function, related update function, related input variable
    and error message to use when updating user information."""

    checkbox_dispatcher = {
        gui.edit_vehicle_change_make_check_box: {  # Check box on page
            "checked": gui.edit_vehicle_change_make_check_box.isChecked,  # Holds checked status
            "validator": validate.is_valid_name,  # Holds function to validate related input
            "input": gui.edit_vehicle_make_input_box.text,  # Holds function to get input
            "error": "Invalid make!\n\n",  # Holds error message if input is invalid
            "updater": database.update_vehicle_make,  # Holds function to update database with input
        },  # All below same as above
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
        return gui.show_error(NO_LOGIN_MSG)

    gui.reset_new_vehicle_page()

    return gui.widget_stack.setCurrentIndex(14)


def go_to_edit_vehicle_page(database, gui, vin=None):
    """Gets a vin and takes the user to the edit vehicle page passes vin to database
    to get that vehicles data and passes that data to the GUI to populate the page."""

    if not database.get_login_status():
        return gui.show_error(NO_LOGIN_MSG)

    # User requested page
    if vin is None:
        # Until user inputs a valid vin or hits cancel, run the loop
        while True:
            vin = gui.show_id_search_request("Edit Vehicle", "Input VIN to edit:")

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

    # New vehicle submit requested page
    else:
        vehicle_data = database.get_vehicle_data(vin)

    # Reset/update page
    gui.reset_edit_vehicle_page()

    gui.update_edit_vehicle_page(vehicle_data)

    return gui.widget_stack.setCurrentIndex(15)


def search_repair_history(database, gui):
    """Gets a vin and passes it to the database to get that vehicle's repair history
    then passes it to the GUI to populate the message window."""

    if not database.get_login_status():
        return gui.show_error("You must be logged in to access this function.")

    # Until user inputs valid vin or hits cancel, run the loop
    while True:
        vin_to_search = gui.show_id_search_request("Search History", "Input Repair ID ")

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

    # Search database for input vin and display
    repair_history = database.get_vehicle_repair_history(vin_to_search)

    repair_info = f"VIN : {vin_to_search}\n\n--- Pior Repair IDs ---\n\n"

    for repair in repair_history:
        repair_info = repair_info + (f"{repair['repair_id']}\n\n")

    return gui.show_vehicle_repair_history(repair_info)


def go_to_list_of_vehicles_page(database, gui):
    """Takes the user to the list of vehicles page, gets all vehicle data from
    the database and passes it to the GUI to populate the page."""

    if not database.get_login_status():
        return gui.show_error(NO_LOGIN_MSG)

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
