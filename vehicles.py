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

    if not validate.is_valid_vin(vin):
        return gui.show_error("Invalid vin.")

    if database.get_vehicle_data(vin):
        return gui.show_error("There is a vehicle with this VIN already.")

    if not validate.is_valid_name(make):
        return gui.show_error("Invalid make.")

    if not validate.is_valid_name(model):
        return gui.show_error("Invalid model.")

    if not validate.is_valid_year(year):
        return gui.show_error("Invalid year.")

    if not validate.is_valid_name(color):
        return gui.show_error("Invalid color.")

    if not validate.is_valid_id(engine):
        return gui.show_error("Invalid engine.")

    vehicle_data = [vin, model, make, year, color, engine, [], None]

    database.insert_vehicle(vehicle_data)

    return gui.show_success("Vehicle input successfully.")


def edit_vehicle_submit(database, gui):
    """Gets new information for a vehicle and passes it to the database for storage."""

    current_vin = gui.edit_vehicle_vin_display_label.text()
    new_make = gui.edit_vehicle_make_input_box.text()
    new_model = gui.edit_vehicle_model_input_box.text()
    new_year = gui.edit_vehicle_year_input_box.text()
    new_color = gui.edit_vehicle_color_input_box.text()
    new_engine = gui.edit_vehicle_engine_input_box.text()

    if gui.edit_vehicle_change_make_check_box.isChecked():
        if not validate.is_valid_name(new_make):
            return gui.show_error("Invalid make.")

    if gui.edit_vehicle_change_model_check_box.isChecked():
        if not validate.is_valid_name(new_model):
            return gui.show_error("Invalid model.")

    if gui.edit_vehicle_change_year_check_box.isChecked():
        if not validate.is_valid_year(new_year):
            return gui.show_error("Invalid year.")

    if gui.edit_vehicle_change_color_check_box.isChecked():
        if not validate.is_valid_name(new_color):
            return gui.show_error("Invalid color.")

    if gui.edit_vehicle_change_engine_check_box.isChecked():
        if not validate.is_valid_name(new_engine):
            return gui.show_error("Invalid engine")

    if gui.edit_vehicle_change_make_check_box.isChecked():
        database.update_vehicle_make(current_vin, new_make)

    if gui.edit_vehicle_change_model_check_box.isChecked():
        database.update_vehicle_model(current_vin, new_model)

    if gui.edit_vehicle_change_year_check_box.isChecked():
        database.update_vehicle_year(current_vin, new_year)

    if gui.edit_vehicle_change_color_check_box.isChecked():
        database.update_vehicle_color(current_vin, new_color)

    if gui.edit_vehicle_change_engine_check_box.isChecked():
        database.update_vehicle_engine(current_vin, new_engine)

    return gui.show_success("Vehicle update successful.")


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
            return

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
            return

        if not validate.is_valid_vin(vin_to_search):
            gui.show_error("Invalid VIN.")

            continue

        vehicle_data = database.get_vehicle_data(vin_to_search)

        if not vehicle_data:
            gui.show_error("Vehicle not found.")

            continue

        break
    # use json loads to get a list from database return
    repair_history = json.loads(vehicle_data[6])

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
            f"VIN : {vehicle[0]}, Model : {vehicle[1]}, "
            f"Make : {vehicle[2]}, Year : {vehicle[3]}, Color : {vehicle[4]}, "
            f"Engine : {vehicle[5]}, Current Active Repair ID : {vehicle[7]}\n\n"
        )

    return vehicle_list
