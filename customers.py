"""This module contains all the handling for customer events in the application."""

import json
import validate


def new_customer_submit(database, gui):
    """Gets new customer data and passes it to the database for storage."""

    target_table = "customers"
    customer_name = gui.new_customer_name_input_box.text()
    customer_address = gui.new_customer_address_input_box.toPlainText()
    customer_phone = gui.new_customer_phone_input_box.text()

    if not validate.is_valid_name(customer_name):
        return gui.show_error("Invalid name.")

    if not validate.is_valid_address(customer_address):
        return gui.show_error("Invalid address")

    if not validate.is_valid_phone_number(customer_phone):
        return gui.show_error("Invalid phone number.")

    customer_id = database.gen_id(target_table)

    list_of_vehicles = []

    inputs = [
        customer_id,
        customer_name,
        customer_address,
        customer_phone,
        json.dumps(list_of_vehicles),
    ]

    database.insert_customer(inputs)

    return gui.show_success("New customer input succesfully.")


def edit_customer_submit(database, gui):
    """Gets new information for a customer and passes it to the database for storage."""

    customer_id = gui.edit_customer_id_display_label.text()
    new_name = gui.edit_customer_name_input_box.text()
    new_address = gui.edit_customer_address_input_box.toPlainText()
    new_phone = gui.edit_customer_phone_input_box.text()

    if gui.edit_customer_change_name_check_box.isChecked():
        if not validate.is_valid_name(new_name):
            return gui.show_error("Invalid name.")

    if gui.edit_customer_change_address_check_box.isChecked():
        if not validate.is_valid_address(new_address):
            return gui.show_error("Invalid address.")

    if gui.edit_customer_change_phone_check_box.isChecked():
        if not validate.is_valid_phone_number(new_phone):
            return gui.show_error("Invalid phone.")

    if gui.edit_customer_change_name_check_box.isChecked():
        database.update_customer_name(customer_id, new_name)

    if gui.edit_customer_change_address_check_box.isChecked():
        database.update_customer_address(customer_id, new_address)

    if gui.edit_customer_change_phone_check_box.isChecked():
        database.update_customer_phone(customer_id, new_phone)

    gui.show_success("Customer update successful.")

    customer_data = database.get_customer_data(customer_id)

    return (
        gui.edit_customer_name_display_label.setText(customer_data[1]),
        gui.edit_customer_address_text_browser.setText(customer_data[2]),
        gui.edit_customer_phone_display_label.setText(customer_data[3]),
    )


def add_vehicle_to_customer_button(database, gui):
    """Gets a vin and passes it to the database to add to a customers vehicle list."""

    customer_id = gui.edit_customer_id_display_label.text()

    while True:
        vin_to_add = gui.show_vin_search_request()

        # if the user hit the cancel button
        if vin_to_add is False:
            return

        if not validate.is_valid_vin(vin_to_add):
            gui.show_error("Invalid VIN.")

            continue

        if not database.get_vehicle_data(vin_to_add):
            gui.show_error("Vehicle not found.")

            continue

        if database.vehicle_is_owned(vin_to_add):
            gui.show_error("This or a different customer already owns that vehicle.")

            continue

        break

    database.add_vehicle_to_customer(customer_id, vin_to_add)

    customer_data = database.get_customer_data(customer_id)

    list_of_vins = json.loads(customer_data[4])

    vehicle_data = []

    for vin in list_of_vins:
        vehicle_data.append(list(database.get_vehicle_data(vin)))

    list_of_vehicles = construct_vehicles_list(vehicle_data)

    gui.edit_customer_vechile_list_text_browser.setText(list_of_vehicles)

    return gui.show_success("Vehicle added.")


def remove_vehicle_from_customer_button(database, gui):
    """Gets a vin from the user and passes it to the database to remove it to that
    customers vehicle list."""

    customer_id = gui.edit_customer_id_display_label.text()

    while True:
        vin_to_remove = gui.show_vin_search_request()

        # If the user clicked the cancel button
        if vin_to_remove is False:
            return

        if not validate.is_valid_vin(vin_to_remove):
            gui.show_error("Invalid VIN.")

            continue

        if not database.get_vehicle_data(vin_to_remove):
            gui.show_error("Vehicle not found.")

            continue

        try:
            database.remove_vehicle_from_customer(customer_id, vin_to_remove)

        except ValueError:
            gui.show_error("Customer does not have ownership of that vehicle.")

            continue

        break

    customer_data = database.get_customer_data(customer_id)

    list_of_vins = json.loads(customer_data[4])

    vehicle_data = []

    for vin in list_of_vins:
        vehicle_data.append(list(database.get_vehicle_data(vin)))

    list_of_vehicles = construct_vehicles_list(vehicle_data)

    gui.edit_customer_vechile_list_text_browser.setText(list_of_vehicles)

    return gui.show_success("Vehicle removed.")


def go_to_new_customer_page(database, gui):
    """Takes the user to the new customer page."""

    if not database.get_login_status():
        return gui.show_error("You must be logged in to access this page.")

    return gui.widget_stack.setCurrentIndex(11)


def go_to_edit_customer_page(database, gui):
    """Gets a customer id and takes them to the edit customer page
    uses the id to get customer information from the database and passes
    it to the GUI to update the page data."""

    if not database.get_login_status():
        return gui.show_error("You must be logged in to access this page.")

    while True:
        customer_id = gui.show_customer_id_search_request()

        # if the user clicked cancel
        if customer_id is False:
            return

        if not validate.is_valid_id(customer_id):
            gui.show_error("Invalid Customer ID.")

            continue

        customer_data = database.get_customer_data(customer_id)

        if not customer_data:
            gui.show_error("Customer not found.")

            continue

        break

    # Use json loads to get a list from database return
    list_of_vins = json.loads(customer_data[4])

    vehicle_data = []

    for vin in list_of_vins:
        vehicle_data.append(list(database.get_vehicle_data(vin)))

    list_of_vehicles = construct_vehicles_list(vehicle_data)

    gui.update_edit_customer_page(customer_data, list_of_vehicles)

    return gui.widget_stack.setCurrentIndex(12)


def go_to_list_of_customers_page(database, gui):
    """Takes the user to the list of customers page, gets information from database on
    all customers and passes it to the GUI to populate data on the page."""

    if not database.get_login_status():
        return gui.show_error("You must be logged in to access this page.")

    customer_data = database.get_all_customers()

    customer_list = construct_list_of_customers(customer_data)

    gui.list_of_customers_text_browser.setText(customer_list)

    return gui.widget_stack.setCurrentIndex(13)


def construct_list_of_customers(customer_data):
    """Constructs a string to display in the ui containing all passed customers from the
    database."""

    customer_list = ""

    for customer in customer_data:
        customer_list = customer_list + (
            f"Customer ID : {customer[0]}, Name : {customer[1]}, "
            f"Phone Number : {customer[3]}, Address : {customer[2]}\n\n"
        )

    return customer_list


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
