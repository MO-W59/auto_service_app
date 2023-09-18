"""This modules controls the interaction between the gui and data interface modules and 
contains the main program function."""


import sys
import json
import datetime
from passlib.hash import sha512_crypt
from PyQt6 import QtWidgets
from gui import UiGarageTrackerMainWindow
from data_interface import AppDatabase
import validate

# vvv--- TODO list ---vvv
# hide password text in password input boxes
# Enable submition of information when hitting the enter key
# use "CREATE TABLE IF NOT EXISTS table_name (...);" instead of empty list checking?
# !!?? use dictionary of functions to eliminate multiple if branches ??!!
# ensure the titles of the message/error windows can be read and are not cut off.
# use dictionaries instead of lists for large inputs?
# setup primary keys / Change gen of employee/customer ids? --> random number 0-1000? or count up?
# setup foriegn keys
# clear login boxes after login
# add column to table for vehicles showing customer id --> possibly done during foriegn keys if fk can be null
# change insert statments into the DB to a list rather than declaring all variables
# move all json.dumps/loads to main app
# move all functions to their proper module, move string construction the app module not in gui or DB
# add commas to dollar amounts and enforce two digits after the decimal point
# alter edit page submit button functions to have reduced if statments? search for alternatives.
# reduce lines in modules look at validte.py for example, is_valid = False --> return is_valid...just return False or True
# search for cut off diplay labels ---> extend width in gui
# list of parts text browser not in same location on gui as other list pages
# merge technicians and servicewriters? add column to display area of work and just have employees table?
# iterate over text boxes with a list of checkboxes and use python match feature?
# set restrictions on class set methods?
# protect against SQL race condition, options -> thread lock? queue? connection pool?
# consolidate code as much as possible --> edit customer submit make a update customer edit page function
# search for bugs
# update doc strings to describe things better
# change naming conventions to uniform naming conventions
# place comments where needed because you didnt do it at time of writing
# handle too many lines in module linter flags


# https://docs.python.org/3/library/sqlite3.html
# https://doc.qt.io/qtforpython-5/api.html#basic-modules


# disable linter message due to using C extention
# pylint: disable=c-extension-no-member

# Set up application ui and database
App = QtWidgets.QApplication(sys.argv)
App_Main_Window = QtWidgets.QMainWindow()
App_Ui = UiGarageTrackerMainWindow()
App_Ui.setup_ui(App_Main_Window)
App_Database = AppDatabase()


def setup_button_handlers():
    """This function connects all the UI buttons (radio buttons not included)
    with their repective functions."""

    # submit, add, remove buttons
    App_Ui.login_page_submit_button.clicked.connect(login_submit)
    App_Ui.new_part_submit_button.clicked.connect(create_part_submit)
    App_Ui.edit_part_submit_button.clicked.connect(edit_part_submit)
    App_Ui.new_vehicle_submit_button.clicked.connect(new_vehicle_submit)
    App_Ui.edit_vehicle_submit_button.clicked.connect(edit_vehicle_submit)
    App_Ui.new_customer_submit_button.clicked.connect(new_customer_submit)
    App_Ui.edit_customer_submit_button.clicked.connect(edit_customer_submit)
    App_Ui.new_user_page_submit_button.clicked.connect(new_user_submit)
    App_Ui.new_repair_page_submit_button.clicked.connect(new_repair_submit)
    App_Ui.update_password_submit_button.clicked.connect(update_password_submit)
    App_Ui.edit_repair_page_submit_complete_button.clicked.connect(finish_repair_submit)
    App_Ui.edit_repair_page_submit_update_button.clicked.connect(edit_repair_submit)
    App_Ui.update_user_page_submit_button.clicked.connect(update_user_submit)
    App_Ui.edit_repair_add_part_button.clicked.connect(add_part_to_repair)
    App_Ui.edit_repair_remove_part_button.clicked.connect(remove_part_from_repair)
    App_Ui.edit_customer_add_vehicle_button.clicked.connect(
        add_vehicle_to_customer_button
    )
    App_Ui.edit_customer_remove_vehicle_button.clicked.connect(
        remove_vehicle_from_customer_button
    )

    # Go to functions for action menu (top menu bar)
    App_Ui.action_login.triggered.connect(go_to_login_page)
    App_Ui.action_logout.triggered.connect(logout_user)
    App_Ui.action_new_user.triggered.connect(go_to_new_user_page)
    App_Ui.action_update_password.triggered.connect(go_to_update_password_page)
    App_Ui.action_update_user.triggered.connect(go_to_update_user_page)
    App_Ui.action_search_user.triggered.connect(search_for_user)
    App_Ui.action_new_repair.triggered.connect(go_to_new_repair_page)
    App_Ui.action_edit_repair.triggered.connect(go_to_edit_repair_page)
    App_Ui.action_active_repairs.triggered.connect(go_to_active_repairs_page)
    App_Ui.action_display_old_repair.triggered.connect(go_to_old_repair_page)
    App_Ui.action_new_part.triggered.connect(go_to_new_part_page)
    App_Ui.action_edit_part.triggered.connect(go_to_edit_part_page)
    App_Ui.action_list_of_parts.triggered.connect(go_to_list_of_parts_page)
    App_Ui.action_new_customer.triggered.connect(go_to_new_customer_page)
    App_Ui.action_edit_customer.triggered.connect(go_to_edit_customer_page)
    App_Ui.action_list_of_customers.triggered.connect(go_to_list_of_customers_page)
    App_Ui.action_new_vehicle.triggered.connect(go_to_new_vehicle_page)
    App_Ui.action_edit_vehicle.triggered.connect(go_to_edit_vehicle_page)
    App_Ui.action_get_repair_history.triggered.connect(search_repair_history)
    App_Ui.action_list_of_vehicles.triggered.connect(go_to_list_of_vehicles_page)


def login_submit():
    """Checks login status in database, validates inputs via validate, submits values
    to Database."""

    if App_Database.get_login_status():
        return App_Ui.show_error("You are already logged in!")

    input_user = App_Ui.username_login_input_box.text()
    input_pass = App_Ui.password_login_input_box.text()

    if not validate.is_valid_username(input_user) and validate.is_valid_password(
        input_pass
    ):
        return App_Ui.show_error("Invalid username or password!")

    if App_Database.is_valid_login_query(input_user, input_pass):
        return App_Ui.show_success("Login successful.")

    return App_Ui.show_error("Invalid username or password!")


def create_part_submit():
    """Creates new part from inputs and passed to database for storage."""

    new_part_id = App_Ui.new_part_part_id_input_box.text()
    new_part_cost = App_Ui.new_part_part_cost_input_box.text()
    new_part_descpition = App_Ui.new_part_description_input_box.text()

    if not validate.is_valid_id(new_part_id):
        return App_Ui.show_error("Invaild part id.")

    if not validate.is_valid_dollar_amount(new_part_cost):
        return App_Ui.show_error("Invalid part cost.")

    if not validate.is_valid_description(new_part_descpition):
        return App_Ui.show_error("Invalid description.")

    inputs = [new_part_id, new_part_cost, new_part_descpition]

    App_Database.insert_parts(inputs)

    return App_Ui.show_success("Part input successfully.")


def edit_part_submit():
    """Gets new information for a stored part and passes it to the database for storage."""

    part_id = App_Ui.edit_part_id_display_label.text()
    new_part_cost = App_Ui.edit_part_part_cost_input_box.text()
    new_part_description = App_Ui.edit_part_description_input_box.text()

    if not validate.is_valid_dollar_amount(new_part_cost):
        return App_Ui.show_error("Invalid part cost.")

    if not validate.is_valid_description(new_part_description):
        return App_Ui.show_error("Invalid part description.")

    if App_Ui.edit_part_change_cost_check_box.isChecked():
        App_Database.update_part_cost(part_id, new_part_cost)

    if App_Ui.edit_part_change_description_check_box.isChecked():
        App_Database.update_part_description(part_id, new_part_description)

    return App_Ui.show_success("Part update successful.")


def new_vehicle_submit():
    """Gets information for a new vehicle and passes it to the database for storage."""

    vin = App_Ui.new_vehicle_vin_input_box.text()
    make = App_Ui.new_vehicle_make_input_box.text()
    model = App_Ui.new_vehicle_model_input_box.text()
    year = App_Ui.new_vehicle_year_input_box.text()
    color = App_Ui.new_vehicle_color_input_box.text()
    engine = App_Ui.new_vehicle_engine_input_box.text()

    if not validate.is_valid_vin(vin):
        return App_Ui.show_error("Invalid vin.")

    if App_Database.get_vehicle_data(vin):
        return App_Ui.show_error("There is a vehicle with this VIN already.")

    if not validate.is_valid_name(make):
        return App_Ui.show_error("Invalid make.")

    if not validate.is_valid_name(model):
        return App_Ui.show_error("Invalid model.")

    if not validate.is_valid_year(year):
        return App_Ui.show_error("Invalid year.")

    if not validate.is_valid_name(color):
        return App_Ui.show_error("Invalid color.")

    if not validate.is_valid_id(engine):
        return App_Ui.show_error("Invalid engine.")

    vehicle_data = [vin, model, make, year, color, engine, [], None]

    App_Database.insert_vehicle(vehicle_data)

    return App_Ui.show_success("Vehicle input successfully.")


def edit_vehicle_submit():
    """Gets new information for a vehicle and passes it to the database for storage."""

    current_vin = App_Ui.edit_vehicle_vin_display_label.text()
    new_make = App_Ui.edit_vehicle_make_input_box.text()
    new_model = App_Ui.edit_vehicle_model_input_box.text()
    new_year = App_Ui.edit_vehicle_year_input_box.text()
    new_color = App_Ui.edit_vehicle_color_input_box.text()
    new_engine = App_Ui.edit_vehicle_engine_input_box.text()

    if App_Ui.edit_vehicle_change_make_check_box.isChecked():
        if not validate.is_valid_name(new_make):
            return App_Ui.show_error("Invalid make.")

    if App_Ui.edit_vehicle_change_model_check_box.isChecked():
        if not validate.is_valid_name(new_model):
            return App_Ui.show_error("Invalid model.")

    if App_Ui.edit_vehicle_change_year_check_box.isChecked():
        if not validate.is_valid_year(new_year):
            return App_Ui.show_error("Invalid year.")

    if App_Ui.edit_vehicle_change_color_check_box.isChecked():
        if not validate.is_valid_name(new_color):
            return App_Ui.show_error("Invalid color.")

    if App_Ui.edit_vehicle_change_engine_check_box.isChecked():
        if not validate.is_valid_name(new_engine):
            return App_Ui.show_error("Invalid engine")

    if App_Ui.edit_vehicle_change_make_check_box.isChecked():
        App_Database.update_vehicle_make(current_vin, new_make)

    if App_Ui.edit_vehicle_change_model_check_box.isChecked():
        App_Database.update_vehicle_model(current_vin, new_model)

    if App_Ui.edit_vehicle_change_year_check_box.isChecked():
        App_Database.update_vehicle_year(current_vin, new_year)

    if App_Ui.edit_vehicle_change_color_check_box.isChecked():
        App_Database.update_vehicle_color(current_vin, new_color)

    if App_Ui.edit_vehicle_change_engine_check_box.isChecked():
        App_Database.update_vehicle_engine(current_vin, new_engine)

    return App_Ui.show_success("Vehicle update successful.")


def new_customer_submit():
    """Gets new customer data and passes it to the database for storage."""

    target_table = "customers"
    customer_name = App_Ui.new_customer_name_input_box.text()
    customer_address = App_Ui.new_customer_address_input_box.toPlainText()
    customer_phone = App_Ui.new_customer_phone_input_box.text()

    if not validate.is_valid_name(customer_name):
        return App_Ui.show_error("Invalid name.")

    if not validate.is_valid_address(customer_address):
        return App_Ui.show_error("Invalid address")

    if not validate.is_valid_phone_number(customer_phone):
        return App_Ui.show_error("Invalid phone number.")

    customer_id = App_Database.gen_id(target_table)

    list_of_vehicles = []

    inputs = [
        customer_id,
        customer_name,
        customer_address,
        customer_phone,
        json.dumps(list_of_vehicles),
    ]

    App_Database.insert_customer(inputs)

    return App_Ui.show_success("New customer input succesfully.")


def edit_customer_submit():
    """Gets new information for a customer and passes it to the database for storage."""

    customer_id = App_Ui.edit_customer_id_display_label.text()
    new_name = App_Ui.edit_customer_name_input_box.text()
    new_address = App_Ui.edit_customer_address_input_box.toPlainText()
    new_phone = App_Ui.edit_customer_phone_input_box.text()

    if App_Ui.edit_customer_change_name_check_box.isChecked():
        if not validate.is_valid_name(new_name):
            return App_Ui.show_error("Invalid name.")

    if App_Ui.edit_customer_change_address_check_box.isChecked():
        if not validate.is_valid_address(new_address):
            return App_Ui.show_error("Invalid address.")

    if App_Ui.edit_customer_change_phone_check_box.isChecked():
        if not validate.is_valid_phone_number(new_phone):
            return App_Ui.show_error("Invalid phone.")

    if App_Ui.edit_customer_change_name_check_box.isChecked():
        App_Database.update_customer_name(customer_id, new_name)

    if App_Ui.edit_customer_change_address_check_box.isChecked():
        App_Database.update_customer_address(customer_id, new_address)

    if App_Ui.edit_customer_change_phone_check_box.isChecked():
        App_Database.update_customer_phone(customer_id, new_phone)

    App_Ui.show_success("Customer update successful.")

    customer_data = App_Database.get_customer_data(customer_id)

    return (
        App_Ui.edit_customer_name_display_label.setText(customer_data[1]),
        App_Ui.edit_customer_address_text_browser.setText(customer_data[2]),
        App_Ui.edit_customer_phone_display_label.setText(customer_data[3]),
    )


def new_user_submit():
    """Gets information for a new user and passes it to the database for storage."""

    new_user = App_Ui.username_new_user_input_box.text()
    new_pass = App_Ui.password_new_user_input_box.text()
    confirm_new_pass = App_Ui.confirm_password_new_user_input_box.text()
    new_name = App_Ui.new_user_name_input_box.text()
    new_team = App_Ui.new_user_team_input_box.text()
    section_or_lane = None
    target_table = None
    assigned_repairs = []

    if (
        not validate.is_valid_username(new_user)
        or not validate.is_valid_password(new_pass)
        or not validate.is_valid_password(confirm_new_pass)
    ):
        return App_Ui.show_error("Invalid username or password!")

    if App_Database.is_username_in_use(new_user):
        return App_Ui.show_error("Username already in use.")

    if not new_pass == confirm_new_pass:
        return App_Ui.show_error("Passwords do not match!")

    if not validate.is_valid_name(new_name):
        return App_Ui.show_error("Invalid name!")

    if not validate.is_valid_team(new_team):
        return App_Ui.show_error("Invalid team!")

    if App_Ui.new_user_tech_radio_button.isChecked():
        target_table = "technicians"

        section_or_lane = App_Ui.new_user_section_input_box.text()

        if not validate.is_valid_name(section_or_lane):
            return App_Ui.show_error("Invalid section!")

    if App_Ui.new_user_service_writer_radio_button.isChecked():
        target_table = "service_writers"

        section_or_lane = App_Ui.new_user_lane_input_box.text()

        if not validate.is_valid_lane(section_or_lane):
            return App_Ui.show_error("Invalid lane!")

        int(section_or_lane)

    hashed_pass = sha512_crypt.hash(new_pass)

    user_id = App_Database.gen_id(target_table)

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

    App_Database.insert_user(inputs)

    return App_Ui.show_success("User input successfuly.")


def new_repair_submit():
    """Gets information for a new repair and passes it to the database for storage."""

    service_writer_id = App_Ui.new_repair_service_id_input_box.text()
    technician_id = App_Ui.new_repair_tech_id_input_box.text()
    vin = App_Ui.new_repair_vin_input_box.text()
    drop_off_date = App_Ui.new_repair_current_date_display.text()
    problem_description = App_Ui.new_repair_description_input_box.toPlainText()

    if not validate.is_valid_id(service_writer_id):
        return App_Ui.show_error("Invalid service writer id.")

    if not validate.is_valid_id(technician_id):
        return App_Ui.show_error("Invalid technician id.")

    if not validate.is_valid_vin(vin):
        return App_Ui.show_error("Invalid vin number.")

    if not App_Database.get_vehicle_data(vin):
        return App_Ui.show_error(
            "A vehicle must be in the database to create a repair for it."
        )

    if not validate.is_valid_description(problem_description):
        return App_Ui.show_error("Invalid problem description.")

    if not App_Database.vehicle_is_owned(vin):
        return App_Ui.show_error("The vehicle must first be owned by a customer.")

    if App_Database.has_active_repair(vin):
        return App_Ui.show_error("This vehicle already has an active repair.")

    constructing_suffix = []
    constructing_suffix[:0] = drop_off_date
    repair_id_suffix = ""

    while "/" in constructing_suffix:
        constructing_suffix.remove("/")

    repair_id_suffix = repair_id_suffix.join(constructing_suffix)
    repair_id = vin + repair_id_suffix

    if App_Database.search_for_repair(repair_id):
        return App_Ui.show_error("That Repair ID is already in use.")

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

    App_Database.insert_repair(inputs)

    App_Database.update_vehicle_active_repair(vin, repair_id)

    return App_Ui.show_success("New repair input successfuly.")


def update_password_submit():
    """Gets a new password for the user and passes it to the database for storage."""

    user = App_Ui.update_password_username_input_box.text()
    old_pass = App_Ui.old_password_input_box.text()
    new_pass = App_Ui.new_password_input_box.text()
    confirm_new_pass = App_Ui.confirm_new_password_input_box.text()

    if not validate.is_valid_username(user) or not validate.is_valid_password(old_pass):
        return App_Ui.show_error("Invalid username or password!")

    if new_pass != confirm_new_pass:
        return App_Ui.show_error("New passwords do not match!")

    if not validate.is_valid_password(new_pass):
        return App_Ui.show_error("New password is invalid!")

    if App_Database.update_pass(user, old_pass, new_pass):
        return App_Ui.show_success("Password update successful.")


def edit_repair_submit():
    """Gets new information for a repair and passes it to the database for storage."""

    new_service_writer_id = App_Ui.edit_repair_service_id_input_box.text()
    new_tech_id = App_Ui.edit_repair_tech_id_input_box.text()
    new_labor_amount = App_Ui.edit_repair_labor_input_box.text()
    problem_description = App_Ui.edit_repair_problem_description_input_box.toPlainText()
    repair_description = App_Ui.edit_repair_repair_description_input_box.toPlainText()
    repair_id = App_Ui.edit_repair_repair_id_display_label.text()
    old_tech_id = App_Ui.edit_repair_tech_id_display_label.text()
    old_writer_id = App_Ui.edit_repair_service_id_display_label.text()

    if App_Ui.change_writer_check_box.isChecked():
        if not validate.is_valid_id(new_service_writer_id):
            return App_Ui.show_error("Invalid service writer ID.")

    if App_Ui.change_tech_check_box.isChecked():
        if not validate.is_valid_id(new_tech_id):
            return App_Ui.show_error("Invalid technician ID.")

    if App_Ui.change_labor_check_box.isChecked():
        if not validate.is_valid_dollar_amount(new_labor_amount):
            return App_Ui.show_error("Invalid labor value.")

    if not validate.is_valid_description(
        problem_description
    ) or not validate.is_valid_description(repair_description):
        return App_Ui.show_error("Invalid description entered.")

    if App_Ui.change_writer_check_box.isChecked():
        App_Database.update_repair_service_writer(
            repair_id, new_service_writer_id, old_writer_id
        )

    if App_Ui.change_tech_check_box.isChecked():
        App_Database.update_repair_tech(repair_id, new_tech_id, old_tech_id)

    if App_Ui.change_labor_check_box.isChecked():
        App_Database.update_labor_cost(repair_id, new_labor_amount)

        total_cost = calculate_total_cost(repair_id)

        App_Database.update_total_repair_cost(repair_id, total_cost)

    App_Database.update_repair_problem(repair_id, problem_description)
    App_Database.update_repair_description(repair_id, repair_description)

    App_Ui.show_success("Repair update successful.")

    repair_data = App_Database.search_for_repair(repair_id)

    return App_Ui.update_edit_repair_displays(repair_data)


def finish_repair_submit():
    """Gathers repair information, sets a completion date, passes that to the database for storage,
    then has the database update employee assignments and moves the user to view the completed
    repair page in the gui."""

    pass_confirm = App_Ui.confirm_repair_complete()
    compelting_repair_id = App_Ui.edit_repair_repair_id_display_label.text()
    service_writer_id = App_Ui.edit_repair_service_id_display_label.text()
    tech_id = App_Ui.edit_repair_tech_id_display_label.text()

    if not validate.is_valid_password(pass_confirm):
        return App_Ui.show_error("Invalid password.")

    if not App_Database.is_current_users_password(pass_confirm):
        return App_Ui.show_error("Invalid password.")

    compelted_date = datetime.datetime.today().strftime("%Y/%m/%d")

    App_Database.update_repair_complete_date(compelting_repair_id, compelted_date)

    App_Database.remove_repair_from_writer(compelting_repair_id, service_writer_id)
    App_Database.remove_repair_from_tech(compelting_repair_id, tech_id)

    App_Ui.show_success("Repair completed.")

    repair_data = App_Database.search_for_repair(compelting_repair_id)

    vin = repair_data[11]

    parts_list = construct_repair_parts_list(compelting_repair_id)

    App_Database.update_vehicle_completed_repairs(vin)

    App_Ui.update_old_repair_displays(repair_data, parts_list)

    return App_Ui.widget_stack.setCurrentIndex(7)


def update_user_submit():
    """Gets information to update a user then passes it to the database for storage."""

    input_pass = App_Ui.update_user_password_input_box.text()
    target_id = App_Ui.update_user_user_id_display_label.text()

    if not validate.is_valid_password:
        return App_Ui.show_error("Invalid password.")

    if not App_Database.is_current_users_password(input_pass):
        return App_Ui.show_error("Invalid password.")

    if App_Ui.update_user_change_name_check_box.isChecked():
        new_name = App_Ui.update_user_name_input_box.text()

        if not validate.is_valid_name(new_name):
            return App_Ui.show_error("Invalid name input.")

    if App_Ui.update_user_change_team_check_box.isChecked():
        new_team = App_Ui.update_user_team_input_box.text()

        if not validate.is_valid_team(new_team):
            return App_Ui.show_error("Invalid team input.")

    if (
        App_Ui.update_user_tech_radio_button.isChecked()
        and App_Ui.update_user_change_section_check_box.isChecked()
    ):
        new_lane_or_section = App_Ui.update_user_section_input_box.text()

        if not validate.is_valid_name(new_lane_or_section):
            return App_Ui.show_error("Invalid section input.")

    if (
        App_Ui.update_user_service_writer_radio_button.isChecked()
        and App_Ui.update_user_change_lane_check_box.isChecked()
    ):
        new_lane_or_section = App_Ui.update_user_lane_input_box.text()

        if not validate.is_valid_lane(new_lane_or_section):
            return App_Ui.show_error("Invalid lane input.")

    if App_Ui.update_user_change_name_check_box.isChecked():
        App_Database.update_user_name(target_id, new_name)

    if App_Ui.update_user_change_team_check_box.isChecked():
        App_Database.update_user_team(target_id, new_team)

    if (
        App_Ui.update_user_change_section_check_box.isChecked()
        and App_Ui.update_user_tech_radio_button.isChecked()
    ):
        App_Database.update_user_section(target_id, new_lane_or_section)

    if (
        App_Ui.update_user_service_writer_radio_button.isChecked()
        and App_Ui.update_user_change_lane_check_box.isChecked()
    ):
        App_Database.update_user_lane(target_id, new_lane_or_section)

    App_Ui.show_success("Update successful, click ok to see updated data.")

    user_data = App_Database.search_for_user(target_id)

    return App_Ui.show_user_search(user_data)


def add_part_to_repair():
    """Gets a part as input and sends it to the database to add to the current repair."""

    repair_id = App_Ui.edit_repair_repair_id_display_label.text()

    while True:
        part_to_add = App_Ui.show_part_id_search_request_add()

        # if the user clicked the cancel button
        if part_to_add is False:
            return

        if not validate.is_valid_id(part_to_add):
            App_Ui.show_error("Invalid Part ID.")

            continue

        if not App_Database.get_part_data(part_to_add):
            App_Ui.show_error("Part not found.")

            continue

        break

    App_Database.update_required_parts_add(repair_id, part_to_add)
    parts_list = construct_repair_parts_list(repair_id)

    parts_cost = calculate_parts_cost(repair_id)
    App_Database.update_repair_parts_cost(repair_id, parts_cost)

    total_cost = calculate_total_cost(repair_id)
    App_Database.update_total_repair_cost(repair_id, total_cost)

    repair_data = App_Database.search_for_repair(repair_id)

    App_Ui.edit_repair_total_repair_cost_display_label.setText(str(repair_data[1]))
    App_Ui.edit_repair_part_cost_display_label.setText(str(repair_data[3]))
    App_Ui.edit_repair_list_of_parts_text_browser.setText(parts_list)

    return App_Ui.show_success("Part added successfuly.")


def construct_repair_parts_list(repair_id):
    """Constructs a string containing the parts needed to complete
    a repair based of repair id and data from database."""

    parts_list = ""

    repair_data = App_Database.search_for_repair(repair_id)

    # use json loads to get a list from the database return value
    part_id_list = json.loads(repair_data[8])

    for part_id in part_id_list:
        part_data = App_Database.get_part_data(part_id)
        parts_list = (
            parts_list
            + f"Part ID : {part_data[0]}, Cost : ${part_data[1]}, Description : {part_data[2]}\n\n"
        )

    return parts_list


def calculate_total_cost(repair_id):
    """Gets information from database based on passed repair id and then
    calculates the total cost of a repair with that data."""

    repair_data = App_Database.search_for_repair(repair_id)

    parts_cost = calculate_parts_cost(repair_id)

    labor_cost = repair_data[2]

    total_cost = parts_cost + labor_cost

    return total_cost


def calculate_parts_cost(repair_id):
    """Gets information from the data base to calculate the total cost of parts."""

    parts_cost = 0.0

    repair_data = App_Database.search_for_repair(repair_id)

    part_id_list = json.loads(repair_data[8])

    for part_id in part_id_list:
        part_data = App_Database.get_part_data(part_id)

        parts_cost = parts_cost + part_data[1]

    return parts_cost


def remove_part_from_repair():
    """Gets information on what part to remoe from the repair then passes
    that information to the database for update."""

    repair_id = App_Ui.edit_repair_repair_id_display_label.text()

    while True:
        part_id_to_remove = App_Ui.show_part_id_search_request_remove()

        # if the user hit the cancel button
        if part_id_to_remove is False:
            return

        if not validate.is_valid_id(part_id_to_remove):
            App_Ui.show_error("Invalid Part ID.")

            continue

        if not App_Database.get_part_data(part_id_to_remove):
            App_Ui.show_error("Part not found.")

            continue

        try:
            App_Database.update_required_parts_remove(repair_id, part_id_to_remove)

        except ValueError:
            App_Ui.show_error("Repair does not have that part currently listed.")

            continue

        break

    parts_list = construct_repair_parts_list(repair_id)

    parts_cost = calculate_parts_cost(repair_id)
    App_Database.update_repair_parts_cost(repair_id, parts_cost)

    total_cost = calculate_total_cost(repair_id)
    App_Database.update_total_repair_cost(repair_id, total_cost)

    repair_data = App_Database.search_for_repair(repair_id)

    App_Ui.edit_repair_part_cost_display_label.setText(str(repair_data[3]))
    App_Ui.edit_repair_total_repair_cost_display_label.setText(str(repair_data[1]))
    App_Ui.edit_repair_list_of_parts_text_browser.setText(parts_list)

    return App_Ui.show_success("Part successfuly removed.")


def add_vehicle_to_customer_button():
    """Gets a vin and passes it to the database to add to a customers vehicle list."""

    customer_id = App_Ui.edit_customer_id_display_label.text()

    while True:
        vin_to_add = App_Ui.show_vin_search_request()

        # if the user hit the cancel button
        if vin_to_add is False:
            return

        if not validate.is_valid_vin(vin_to_add):
            App_Ui.show_error("Invalid VIN.")

            continue

        if not App_Database.get_vehicle_data(vin_to_add):
            App_Ui.show_error("Vehicle not found.")

            continue

        if App_Database.vehicle_is_owned(vin_to_add):
            App_Ui.show_error("This or a different customer already owns that vehicle.")

            continue

        break

    App_Database.add_vehicle_to_customer(customer_id, vin_to_add)

    customer_data = App_Database.get_customer_data(customer_id)

    list_of_vins = json.loads(customer_data[4])

    vehicle_data = []

    for vin in list_of_vins:
        vehicle_data.append(list(App_Database.get_vehicle_data(vin)))

    list_of_vehicles = construct_vehicles_list(vehicle_data)

    App_Ui.edit_customer_vechile_list_text_browser.setText(list_of_vehicles)

    return App_Ui.show_success("Vehicle added.")


def remove_vehicle_from_customer_button():
    """Gets a vin from the user and passes it to the database to remove it to that
    customers vehicle list."""

    customer_id = App_Ui.edit_customer_id_display_label.text()

    while True:
        vin_to_remove = App_Ui.show_vin_search_request()

        # If the user clicked the cancel button
        if vin_to_remove is False:
            return

        if not validate.is_valid_vin(vin_to_remove):
            App_Ui.show_error("Invalid VIN.")

            continue

        if not App_Database.get_vehicle_data(vin_to_remove):
            App_Ui.show_error("Vehicle not found.")

            continue

        try:
            App_Database.remove_vehicle_from_customer(customer_id, vin_to_remove)

        except ValueError:
            App_Ui.show_error("Customer does not have ownership of that vehicle.")

            continue

        break

    customer_data = App_Database.get_customer_data(customer_id)

    list_of_vins = json.loads(customer_data[4])

    vehicle_data = []

    for vin in list_of_vins:
        vehicle_data.append(list(App_Database.get_vehicle_data(vin)))

    list_of_vehicles = construct_vehicles_list(vehicle_data)

    App_Ui.edit_customer_vechile_list_text_browser.setText(list_of_vehicles)

    return App_Ui.show_success("Vehicle removed.")


def go_to_login_page():
    """Takes user to login page."""

    App_Ui.widget_stack.setCurrentIndex(0)


def logout_user():
    """Passes false to the login status in the database if the user is logged in,
    then moves them to the login page."""

    if not App_Database.get_login_status():
        return App_Ui.show_error("Unable to logout, you are currently not logged in.")

    App_Database.set_login_status(False)

    App_Ui.show_success("Logout successful.")

    return App_Ui.widget_stack.setCurrentIndex(0)


def go_to_new_user_page():
    """Takes the user to the new user page."""

    App_Ui.widget_stack.setCurrentIndex(1)


def go_to_update_password_page():
    """Takes the user to the update password page."""

    if not App_Database.get_login_status():
        return App_Ui.show_error("You must be logged in to access this page.")

    return App_Ui.widget_stack.setCurrentIndex(2)


def search_for_user():
    """Gets a user id and passes it to the database to get that users data."""

    if not App_Database.get_login_status():
        return App_Ui.show_error("You must be logged in to access this function.")

    while True:
        id_to_search = App_Ui.show_user_id_search_request()

        # If the user clicked cancel
        if id_to_search is False:
            return

        if not validate.is_valid_id(id_to_search):
            App_Ui.show_error("Invalid User ID.")

            continue

        user_data = App_Database.search_for_user(id_to_search)

        if not user_data:
            App_Ui.show_error("User not found!")

            continue

        break

    repair_data = json.loads(user_data[6])

    informaion_to_display = (
        f"User ID : {user_data[0]}\nUsername : {user_data[1]}\n"
        f"Name : {user_data[3]}\nTeam : {user_data[4]}\n"
        f"Lane/Section : {user_data[5]}\n\n"
        f"--- Assigned Repairs ---\n\n"
    )

    for repair in repair_data:
        informaion_to_display = informaion_to_display + f"{repair}\n\n"

    return App_Ui.show_user_search(informaion_to_display)


def go_to_update_user_page():
    """Takes the user to the update user page."""

    if not App_Database.get_login_status():
        return App_Ui.show_error("You must be logged in to access this page.")

    while True:
        id_to_update = App_Ui.show_user_id_search_request()

        # If the user clicked cancel
        if id_to_update is False:
            return

        if not validate.is_valid_id(id_to_update):
            App_Ui.show_error("Invalid User ID.")

            continue

        user_data = App_Database.search_for_user(id_to_update)

        if not user_data:
            App_Ui.show_error("User not found!")

            continue

        break

    App_Ui.update_user_update_displays(user_data)

    return App_Ui.widget_stack.setCurrentIndex(3)


def go_to_new_repair_page():
    """Takes the user to the new repair page and gets current date to display."""

    if not App_Database.get_login_status():
        return App_Ui.show_error("You must be logged in to access this page.")

    drop_off_date = datetime.datetime.today().strftime("%Y/%m/%d")

    App_Ui.new_repair_current_date_display.setText(drop_off_date)

    return App_Ui.widget_stack.setCurrentIndex(4)


def go_to_edit_repair_page():
    """Takes the user to the edit repair page, gets information from the database
    based on entered repair id to populate the page with data."""

    if not App_Database.get_login_status():
        return App_Ui.show_error("You must be logged in to access this page.")

    while True:
        requested_repair_id = App_Ui.show_repair_id_search_request()

        # If the user clicked cancel
        if requested_repair_id is False:
            return

        if not validate.is_valid_id(requested_repair_id):
            App_Ui.show_error("Invalid Repair ID.")

            continue

        repair_data = App_Database.search_for_repair(requested_repair_id)

        if not repair_data:
            App_Ui.show_error("Repair not found.")

            continue

        break

    App_Ui.update_edit_repair_displays(repair_data)

    parts_list = construct_repair_parts_list(requested_repair_id)

    App_Ui.edit_repair_list_of_parts_text_browser.setText(parts_list)

    return App_Ui.widget_stack.setCurrentIndex(5)


def go_to_active_repairs_page():
    """Takes the user to the active repairs page and gets all active repairs
    from the database to populate the page.."""

    if not App_Database.get_login_status():
        return App_Ui.show_error("You must be logged in to access this page.")

    repair_data = App_Database.get_all_repairs()

    list_of_repairs = ""

    for repair in repair_data:
        list_of_repairs = (
            list_of_repairs + f"Repair ID : {repair[0]}, Total Cost : {repair[1]}, "
            f"Labor : {repair[2]}, Parts Cost : {repair[3]}, Drop off Date : {repair[4]}, "
            f"Repair Completed Date : {repair[5]}, Technician ID : {repair[9]}, "
            f"Service Writer ID : {repair[10]}\n\n"
        )

    App_Ui.update_active_repair_list(list_of_repairs)

    return App_Ui.widget_stack.setCurrentIndex(6)


def go_to_old_repair_page():
    """Gets a repair id and passes it to the database to get information on an
    old repair, then populates the page with its data."""

    if not App_Database.get_login_status():
        return App_Ui.show_error("You must be logged in to access this page.")

    while True:
        repair_id = App_Ui.show_repair_id_search_request()

        # If the user clicked cancel
        if repair_id is False:
            return

        if not validate.is_valid_id(repair_id):
            App_Ui.show_error("Invalid Repair ID.")

            continue

        repair_data = App_Database.search_for_repair(repair_id)

        if not repair_data:
            App_Ui.show_error("Repair not found.")

            continue

        if repair_data[5] is None:
            App_Ui.show_error("That repair is still underway.")

            continue

        break

    list_of_parts = construct_repair_parts_list(repair_id)

    App_Ui.update_old_repair_displays(repair_data, list_of_parts)

    return App_Ui.widget_stack.setCurrentIndex(7)


def go_to_new_part_page():
    """Takes the user to the new parts page."""

    if not App_Database.get_login_status():
        return App_Ui.show_error("You must be logged in to access this page.")

    return App_Ui.widget_stack.setCurrentIndex(8)


def go_to_edit_part_page():
    """Gets a part id to edit and passes it to the database to get
    that part's information then passes the data to the GUI to update
    the page."""

    if not App_Database.get_login_status():
        return App_Ui.show_error("You must be logged in to access this page.")

    while True:
        part_id = App_Ui.show_part_id_search_request()

        # If user clicked cancel
        if part_id is False:
            return

        if not validate.is_valid_id(part_id):
            App_Ui.show_error("Invalid Part ID.")

            continue

        part_data = App_Database.get_part_data(part_id)

        if not part_data:
            App_Ui.show_error("Part not found.")

            continue

        break

    App_Ui.update_edit_part_page(part_data)

    return App_Ui.widget_stack.setCurrentIndex(9)


def go_to_list_of_parts_page():
    """Takes the user to the list of parts page and pulls all
    part data from the database to pass the data to the GUI."""

    if not App_Database.get_login_status():
        return App_Ui.show_error("You must be logged in to access this page.")

    parts_data = App_Database.get_all_parts_in_database()

    parts_list = ""

    for entry in parts_data:
        parts_list = (
            parts_list
            + f"Part ID : {entry[0]}, Cost : ${entry[1]}, Description : {entry[2]}\n\n"
        )

    App_Ui.list_of_parts_text_browser.setText(parts_list)

    return App_Ui.widget_stack.setCurrentIndex(10)


def go_to_new_customer_page():
    """Takes the user to the new customer page."""

    if not App_Database.get_login_status():
        return App_Ui.show_error("You must be logged in to access this page.")

    return App_Ui.widget_stack.setCurrentIndex(11)


def go_to_edit_customer_page():
    """Gets a customer id and takes them to the edit customer page
    uses the id to get customer information from the database and passes
    it to the GUI to update the page data."""

    if not App_Database.get_login_status():
        return App_Ui.show_error("You must be logged in to access this page.")

    while True:
        customer_id = App_Ui.show_customer_id_search_request()

        # if the user clicked cancel
        if customer_id is False:
            return

        if not validate.is_valid_id(customer_id):
            App_Ui.show_error("Invalid Customer ID.")

            continue

        customer_data = App_Database.get_customer_data(customer_id)

        if not customer_data:
            App_Ui.show_error("Customer not found.")

            continue

        break

    # Use json loads to get a list from database return
    list_of_vins = json.loads(customer_data[4])

    vehicle_data = []

    for vin in list_of_vins:
        vehicle_data.append(list(App_Database.get_vehicle_data(vin)))

    list_of_vehicles = construct_vehicles_list(vehicle_data)

    App_Ui.update_edit_customer_page(customer_data, list_of_vehicles)

    return App_Ui.widget_stack.setCurrentIndex(12)


def go_to_list_of_customers_page():
    """Takes the user to the list of customers page, gets information from database on
    all customers and passes it to the GUI to populate data on the page."""

    if not App_Database.get_login_status():
        return App_Ui.show_error("You must be logged in to access this page.")

    customer_data = App_Database.get_all_customers()

    customer_list = construct_list_of_customers(customer_data)

    App_Ui.list_of_customers_text_browser.setText(customer_list)

    return App_Ui.widget_stack.setCurrentIndex(13)


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


def go_to_new_vehicle_page():
    """Takes the user to the new vehicles page."""

    if not App_Database.get_login_status():
        return App_Ui.show_error("You must be logged in to access this page.")

    return App_Ui.widget_stack.setCurrentIndex(14)


def go_to_edit_vehicle_page():
    """Gets a vin and takes the user to the edit vehicle page passes vin to database
    to get that vehicles data and passes that data to the GUI to populate the page."""

    if not App_Database.get_login_status():
        return App_Ui.show_error("You must be logged in to access this page.")

    while True:
        vin = App_Ui.show_vin_search_request()

        # If the user clicked cancel
        if vin is False:
            return

        if not validate.is_valid_vin(vin):
            App_Ui.show_error("Invalid VIN.")

            continue

        vehicle_data = App_Database.get_vehicle_data(vin)

        if not vehicle_data:
            App_Ui.show_error("Vehicle not found.")

            continue

        break

    App_Ui.update_edit_vehicle_page(vehicle_data)

    return App_Ui.widget_stack.setCurrentIndex(15)


def search_repair_history():
    """Gets a vin and passes it to the database to get that vehicle's repair history
    then passes it to the GUI to populate the message window."""

    if not App_Database.get_login_status():
        return App_Ui.show_error("You must be logged in to access this function.")

    while True:
        vin_to_search = App_Ui.show_vin_search_request()

        # If the user clicked cancel
        if vin_to_search is False:
            return

        if not validate.is_valid_vin(vin_to_search):
            App_Ui.show_error("Invalid VIN.")

            continue

        vehicle_data = App_Database.get_vehicle_data(vin_to_search)

        if not vehicle_data:
            App_Ui.show_error("Vehicle not found.")

            continue

        break
    # use json loads to get a list from database return
    repair_history = json.loads(vehicle_data[6])

    repair_info = f"VIN : {vin_to_search}\n\n--- Pior Repair IDs ---\n\n"

    for repair in repair_history:
        repair_info = repair_info + (f"{repair}\n\n")

    return App_Ui.show_vehicle_repair_history(repair_info)


def go_to_list_of_vehicles_page():
    """Takes the user to the list of vehicles page, gets all vehicle data from
    the database and passes it to the GUI to populate the page."""

    if not App_Database.get_login_status():
        return App_Ui.show_error("You must be logged in to access this page.")

    vehicle_data = App_Database.get_all_vehicles()

    vehicle_list = construct_vehicles_list(vehicle_data)

    App_Ui.list_of_vehicles_text_browser.setText(vehicle_list)

    return App_Ui.widget_stack.setCurrentIndex(16)


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


def main():
    """Main function of the program, calls setup of button handlers, shows the main app window
    and instucts system to exit when GUI is closed."""

    setup_button_handlers()
    App_Main_Window.show()
    sys.exit(App.exec())


if __name__ == "__main__":
    main()
    App_Database.connection.close()
