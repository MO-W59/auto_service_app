"""This module contains all the handling for customer events in the application."""

import json
import validate


def new_customer_submit(database, gui):
    """Gets new customer data and passes it to the database for storage."""

    target_table = "customers"
    name = gui.new_customer_name_input_box.text()
    address = gui.new_customer_address_input_box.toPlainText()
    phone = gui.new_customer_phone_input_box.text()
    errors = ""

    if not validate.is_valid_name(name):
        errors += "Invalid name!"

    if not validate.is_valid_address(address):
        errors += "\n\nInvalid address!"

    if not validate.is_valid_phone_number(phone):
        errors += "\n\nInvalid phone number!"

    if errors != "":
        return gui.show_error(errors)

    customer_id = database.gen_id(target_table)

    list_of_vehicles = []

    customer_data = {
        "customer_id": customer_id,
        "name": name,
        "adress": address,
        "phone": phone,
        "list_of_vehicles": json.dumps(list_of_vehicles),
    }

    database.insert_customer(customer_data)

    return gui.show_success("New customer input succesfully.")


def edit_customer_submit(database, gui):
    """Gets new information for a customer and passes it to the database for storage."""

    customer_id = gui.edit_customer_id_display_label.text()
    name = gui.edit_customer_name_input_box.text()
    address = gui.edit_customer_address_input_box.toPlainText()
    phone = gui.edit_customer_phone_input_box.text()
    errors = ""

    if gui.edit_customer_change_name_check_box.isChecked():
        if not validate.is_valid_name(name):
            errors += "Invalid name!\n\n"

    if gui.edit_customer_change_address_check_box.isChecked():
        if not validate.is_valid_address(address):
            errors += "Invalid address!\n\n"

    if gui.edit_customer_change_phone_check_box.isChecked():
        if not validate.is_valid_phone_number(phone):
            errors += "Invalid phone!\n\n"

    if errors != "":
        return gui.show_error(errors)

    if gui.edit_customer_change_name_check_box.isChecked():
        database.update_customer_name(customer_id, name)

    if gui.edit_customer_change_address_check_box.isChecked():
        database.update_customer_address(customer_id, address)

    if gui.edit_customer_change_phone_check_box.isChecked():
        database.update_customer_phone(customer_id, phone)

    gui.show_success("Customer update successful.")

    customer_data = database.get_customer_data(customer_id)

    return (
        gui.edit_customer_name_display_label.setText(customer_data["name"]),
        gui.edit_customer_address_text_browser.setText(customer_data["address"]),
        gui.edit_customer_phone_display_label.setText(customer_data["phone_number"]),
    )


def add_vehicle_to_customer_button(database, gui):
    """Gets a vin and passes it to the database to add to a customers vehicle list."""

    customer_id = gui.edit_customer_id_display_label.text()

    while True:
        vin_to_add = gui.show_vin_search_request()

        # if the user hit the cancel button
        if vin_to_add is False:
            return None

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

    list_of_vins = json.loads(customer_data["list_of_vehicles"])

    list_of_vehicles = construct_vehicles_list(database, list_of_vins)

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
            return None

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

    list_of_vins = json.loads(customer_data["list_of_vehicles"])

    list_of_vehicles = construct_vehicles_list(database, list_of_vins)

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
            return None

        if not validate.is_valid_id(customer_id):
            gui.show_error("Invalid Customer ID.")

            continue

        customer_data = database.get_customer_data(customer_id)

        if not customer_data:
            gui.show_error("Customer not found.")

            continue

        break

    # Use json loads to get a list from database return
    list_of_vins = json.loads(customer_data["list_of_vehicles"])

    list_of_vehicles = construct_vehicles_list(database, list_of_vins)

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
            f"Customer ID : {customer['customer_id']}, Name : {customer['name']}, "
            f"Phone Number : {customer['phone_number']}, Address : {customer['address']}\n\n"
        )

    return customer_list


def construct_vehicles_list(database, list_of_vins):
    """Constructs a formated string of passed vehicle data for display."""

    vehicle_list = ""

    for vin in list_of_vins:
        vehicle = database.get_vehicle_data(vin)

        vehicle_list = vehicle_list + (
            f"VIN : {vehicle['vin']}, Model : {vehicle['model']}, "
            f"Make : {vehicle['make']}, Year : {vehicle['year']}, Color : {vehicle['color']}, "
            f"Engine : {vehicle['engine']}, Current Active Repair ID : {vehicle['repair_request']}\n\n"
        )

    return vehicle_list
