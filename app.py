"""This module contains the main fucntion that calls the GUI and Database construction then creates
listeners and links them to the handlers in their repective modules."""


import sys
from PyQt6 import QtWidgets, QtCore
from gui import UiGarageTrackerMainWindow
from data_interface import AppDatabase
import users
import repairs
import parts
import vehicles
import customers

# disable linter message due to using C extention
# pylint: disable=c-extension-no-member


def setup_button_handlers():
    """This function connects all the UI buttons (radio buttons not included)
    with their repective functions."""

    # submit, add, remove buttons
    # user buttons
    Gui.login_page_submit_button.clicked.connect(
        lambda: users.login_submit(Database, Gui)
    )
    Gui.new_user_page_submit_button.clicked.connect(
        lambda: users.new_user_submit(Database, Gui)
    )
    Gui.update_password_submit_button.clicked.connect(
        lambda: users.update_password_submit(Database, Gui)
    )
    Gui.update_user_page_submit_button.clicked.connect(
        lambda: users.update_user_submit(Database, Gui)
    )

    # repair buttons
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

    # part buttons
    Gui.new_part_submit_button.clicked.connect(
        lambda: parts.create_part_submit(Database, Gui)
    )
    Gui.edit_part_submit_button.clicked.connect(
        lambda: parts.edit_part_submit(Database, Gui)
    )

    # customer buttons
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

    # vehicle buttons
    Gui.new_vehicle_submit_button.clicked.connect(
        lambda: vehicles.new_vehicle_submit(Database, Gui)
    )
    Gui.edit_vehicle_submit_button.clicked.connect(
        lambda: vehicles.edit_vehicle_submit(Database, Gui)
    )

    # Go to functions for action menu (top menu bar)
    # user actions
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
    Gui.action_show_users.triggered.connect(lambda: users.show_all_users(Database, Gui))
    Gui.action_remove_user.triggered.connect(
        lambda: Database.remove_row(Gui, "employees")
    )

    # repair actions
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
    Gui.action_remove_repair.triggered.connect(
        lambda: Database.remove_row(Gui, "repairs")
    )

    # part actions
    Gui.action_new_part.triggered.connect(
        lambda: parts.go_to_new_part_page(Database, Gui)
    )
    Gui.action_edit_part.triggered.connect(
        lambda: parts.go_to_edit_part_page(Database, Gui)
    )
    Gui.action_list_of_parts.triggered.connect(
        lambda: parts.go_to_list_of_parts_page(Database, Gui)
    )
    Gui.action_remove_part.triggered.connect(lambda: Database.remove_row(Gui, "parts"))

    # customer actions
    Gui.action_new_customer.triggered.connect(
        lambda: customers.go_to_new_customer_page(Database, Gui)
    )
    Gui.action_edit_customer.triggered.connect(
        lambda: customers.go_to_edit_customer_page(Database, Gui)
    )
    Gui.action_list_of_customers.triggered.connect(
        lambda: customers.go_to_list_of_customers_page(Database, Gui)
    )
    Gui.action_remove_customer.triggered.connect(
        lambda: Database.remove_row(Gui, "customers")
    )

    # vehicle actions
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
    Gui.action_remove_vehicle.triggered.connect(
        lambda: Database.remove_row(Gui, "vehicles")
    )


class MainWindow(UiGarageTrackerMainWindow):
    """Creates a GUI from the UiGarageTracker template created by
    PyQt Designer and adds return and esc key press support."""

    def __init__(self):
        super().__init__()
        self.setup_ui(self)

    # disable linter message for invalid name, this is a PyQt variable
    # pylint: disable=invalid-name
    def keyPressEvent(self, event):
        """Event handler for key press events. Escape exits the program, return calls the
        current index then is matched with proper module function."""

        if event.key() == QtCore.Qt.Key.Key_Escape.value:
            self.close()

        if event.key() == QtCore.Qt.Key.Key_Return.value:
            index = Gui.widget_stack.currentIndex()

            match index:
                case 0:
                    users.login_submit(Database, Gui)

                case 1:
                    users.new_user_submit(Database, Gui)

                case 2:
                    users.update_password_submit(Database, Gui)

                case 3:
                    users.update_user_submit(Database, Gui)

                case 4:
                    repairs.new_repair_submit(Database, Gui)

                case 5:
                    repairs.edit_repair_submit(Database, Gui)

                case 8:
                    parts.create_part_submit(Database, Gui)

                case 9:
                    parts.edit_part_submit(Database, Gui)

                case 11:
                    customers.new_customer_submit(Database, Gui)

                case 12:
                    customers.edit_customer_submit(Database, Gui)

                case 14:
                    vehicles.new_vehicle_submit(Database, Gui)

                case 15:
                    vehicles.edit_vehicle_submit(Database, Gui)


def setup_text_handlers():
    """Sets up the handling for events on the edit repair QTextEdit objects
    (repair description and problem description)"""

    Gui.edit_repair_problem_description_input_box.textChanged.connect(
        lambda: Gui.set_repair_problem_has_changed(True)
    )
    Gui.edit_repair_repair_description_input_box.textChanged.connect(
        lambda: Gui.set_repair_repair_has_changed(True)
    )


# Set up application ui and database
App = QtWidgets.QApplication(sys.argv)
Gui = MainWindow()
Database = AppDatabase()


def main():
    """Main function of the program, calls setup of button handlers, shows the main app window
    and instucts system to exit when GUI is closed."""

    setup_button_handlers()
    setup_text_handlers()
    Gui.show()
    sys.exit(App.exec())


if __name__ == "__main__":
    main()
    Database.connection.close()
