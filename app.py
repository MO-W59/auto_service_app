"""This module contains the main fucntion that calls the GUI and Database construction then creates
listeners and links them to the handlers in their repective modules."""


import sys
from PyQt6 import QtWidgets
from gui import UiGarageTrackerMainWindow
from data_interface import AppDatabase
import users
import repairs
import parts
import vehicles
import customers

# vvv--- TODO list ---vvv
# Enable submition of information when hitting the enter key (buttons autoDefault, textbox returnkey press)
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
Gui = UiGarageTrackerMainWindow()
Gui.setup_ui(App_Main_Window)
Database = AppDatabase()


def setup_button_handlers():
    """This function connects all the UI buttons (radio buttons not included)
    with their repective functions."""

    # submit, add, remove buttons

    # user items
    # login page
    Gui.login_page_submit_button.clicked.connect(
        lambda: users.login_submit(Database, Gui)
    )
    Gui.password_login_input_box.returnPressed.connect(
        lambda: users.login_submit(Database, Gui)
    )

    # new user page
    Gui.new_user_page_submit_button.clicked.connect(
        lambda: users.new_user_submit(Database, Gui)
    )
    Gui.confirm_password_new_user_input_box.returnPressed.connect(
        lambda: users.new_user_submit(Database, Gui)
    )

    # update password page
    Gui.update_password_submit_button.clicked.connect(
        lambda: users.update_password_submit(Database, Gui)
    )
    Gui.confirm_new_password_input_box.returnPressed.connect(
        lambda: users.update_password_submit(Database, Gui)
    )

    # update user page
    Gui.update_user_page_submit_button.clicked.connect(
        lambda: users.update_user_submit(Database, Gui)
    )
    Gui.update_user_password_input_box.returnPressed.connect(
        lambda: users.update_user_submit(Database, Gui)
    )

    Gui.new_repair_page_submit_button.clicked.connect(
        lambda: repairs.new_repair_submit(Database, Gui)
    )
    Gui.edit_repair_page_submit_complete_button.clicked.connect(
        lambda: repairs.finish_repair_submit(Database, Gui)
    )
    Gui.edit_repair_page_submit_update_button.clicked.connect(
        lambda: repairs.edit_repair_submit(Database, Gui)
    )
    Gui.edit_repair_add_part_button.clicked.connect(
        lambda: repairs.add_part_to_repair(Database, Gui)
    )
    Gui.edit_repair_remove_part_button.clicked.connect(
        lambda: repairs.remove_part_from_repair(Database, Gui)
    )

    Gui.new_part_submit_button.clicked.connect(
        lambda: parts.create_part_submit(Database, Gui)
    )
    Gui.edit_part_submit_button.clicked.connect(
        lambda: parts.edit_part_submit(Database, Gui)
    )

    Gui.new_customer_submit_button.clicked.connect(
        lambda: customers.new_customer_submit(Database, Gui)
    )
    Gui.edit_customer_submit_button.clicked.connect(
        lambda: customers.edit_customer_submit(Database, Gui)
    )
    Gui.edit_customer_add_vehicle_button.clicked.connect(
        lambda: customers.add_vehicle_to_customer_button(Database, Gui)
    )
    Gui.edit_customer_remove_vehicle_button.clicked.connect(
        lambda: customers.remove_vehicle_from_customer_button(Database, Gui)
    )

    Gui.new_vehicle_submit_button.clicked.connect(
        lambda: vehicles.new_vehicle_submit(Database, Gui)
    )
    Gui.edit_vehicle_submit_button.clicked.connect(
        lambda: vehicles.edit_vehicle_submit(Database, Gui)
    )

    # Go to functions for action menu (top menu bar)
    Gui.action_login.triggered.connect(lambda: users.go_to_login_page(Gui))
    Gui.action_logout.triggered.connect(lambda: users.logout_user(Database, Gui))
    Gui.action_new_user.triggered.connect(lambda: users.go_to_new_user_page(Gui))
    Gui.action_update_password.triggered.connect(
        lambda: users.go_to_update_password_page(Database, Gui)
    )
    Gui.action_update_user.triggered.connect(
        lambda: users.go_to_update_user_page(Database, Gui)
    )
    Gui.action_search_user.triggered.connect(
        lambda: users.search_for_user(Database, Gui)
    )

    Gui.action_new_repair.triggered.connect(
        lambda: repairs.go_to_new_repair_page(Database, Gui)
    )
    Gui.action_edit_repair.triggered.connect(
        lambda: repairs.go_to_edit_repair_page(Database, Gui)
    )
    Gui.action_active_repairs.triggered.connect(
        lambda: repairs.go_to_active_repairs_page(Database, Gui)
    )
    Gui.action_display_old_repair.triggered.connect(
        lambda: repairs.go_to_old_repair_page(Database, Gui)
    )

    Gui.action_new_part.triggered.connect(
        lambda: parts.go_to_new_part_page(Database, Gui)
    )
    Gui.action_edit_part.triggered.connect(
        lambda: parts.go_to_edit_part_page(Database, Gui)
    )
    Gui.action_list_of_parts.triggered.connect(
        lambda: parts.go_to_list_of_parts_page(Database, Gui)
    )

    Gui.action_new_customer.triggered.connect(
        lambda: customers.go_to_new_customer_page(Database, Gui)
    )
    Gui.action_edit_customer.triggered.connect(
        lambda: customers.go_to_edit_customer_page(Database, Gui)
    )
    Gui.action_list_of_customers.triggered.connect(
        lambda: customers.go_to_list_of_customers_page(Database, Gui)
    )

    Gui.action_new_vehicle.triggered.connect(
        lambda: vehicles.go_to_new_vehicle_page(Database, Gui)
    )
    Gui.action_edit_vehicle.triggered.connect(
        lambda: vehicles.go_to_edit_vehicle_page(Database, Gui)
    )
    Gui.action_get_repair_history.triggered.connect(
        lambda: vehicles.search_repair_history(Database, Gui)
    )
    Gui.action_list_of_vehicles.triggered.connect(
        lambda: vehicles.go_to_list_of_vehicles_page(Database, Gui)
    )


def main():
    """Main function of the program, calls setup of button handlers, shows the main app window
    and instucts system to exit when GUI is closed."""

    setup_button_handlers()
    App_Main_Window.show()
    sys.exit(App.exec())


if __name__ == "__main__":
    main()
    Database.connection.close()
