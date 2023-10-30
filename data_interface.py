"""This module defines the the database class and functions used to query/execute to it."""


import os
import sqlite3
from passlib.hash import sha512_crypt
import validate


class AppDatabase:
    """This class defines database objects for the application."""

    def __init__(self):
        self.is_logged_in = False
        self.current_user = None
        # set directory to data folder in app path
        self.data_directory = os.path.dirname(os.path.realpath(__file__)) + "\\data\\"
        self.connection = sqlite3.connect(self.data_directory + "data.db")
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
        self.create_tables()
        self.remove_row_distpatcher = self.create_remove_row_dispatcher()

    def create_tables(self):
        """Creates the tables in the database if they do not already exist."""

        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS customers 
                (customer_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                name TEXT NOT NULL, 
                address TEXT NOT NULL, 
                phone_number TEXT NOT NULL);"""
        )

        self.connection.commit()

        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS employees 
                (employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT NOT NULL,
                team TEXT NOT NULL,
                lane_or_section TEXT NOT NULL,
                is_tech INTEGER NOT NULL,
                is_writer INTEGER NOT NULL);"""
        )

        self.connection.commit()

        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS parts
                (part_id TEXT PRIMARY KEY NOT NULL,
                part_cost REAL NOT NULL,
                part_description TEXT NOT NULL);"""
        )

        self.connection.commit()

        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS part_listings 
                (listing_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                part_id TEXT NOT NULL, 
                repair_id TEXT NOT NULL,
                FOREIGN KEY (part_id) REFERENCES parts (part_id),
                FOREIGN KEY (repair_id) REFERENCES repairs (repair_id));"""
        )

        self.connection.commit()

        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS repairs
                (repair_id TEXT PRIMARY KEY,
                total_cost REAL,
                labor REAL,
                parts_cost REAL,
                drop_off_date TEXT NOT NULL,
                repair_completed_date TEXT,
                problem_description TEXT NOT NULL,
                repair_description TEXT,
                technician INTEGER NOT NULL,
                service_writer INTEGER NOT NULL,
                vehicle TEXT NOT NULL,
                FOREIGN KEY (technician) REFERENCES employees (employee_id),
                FOREIGN KEY (service_writer) REFERENCES employees (employee_id),
                FOREIGN KEY (vehicle) REFERENCES vehicles (vin));"""
        )

        self.connection.commit()

        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS vehicles
                (vin TEXT PRIMARY KEY,
                model TEXT NOT NULL,
                make TEXT NOT NULL,
                year TEXT NOT NULL,
                color TEXT NOT NULL,
                engine TEXT NOT NULL,
                repair_request TEXT,
                owner INTEGER,
                FOREIGN KEY (repair_request) REFERENCES repairs (repair_id),
                FOREIGN KEY (owner) REFERENCES customers (customer_id));"""
        )

        self.connection.commit()

    def create_remove_row_dispatcher(self):
        """Creates a dictionary of dictionaries used when removing a row from
        a table."""

        remove_dispatcher = {
            "customers": {  # target table to match too
                "title": "Remove Customer",  # title to pass to gui
                "msg": "Input Customer ID to remove:",  # message to pass to gui
                "remover": self.remove_customer,  # function to call for remove
                "search": self.get_customer_data,  # function to call to search
            },  # same below
            "employees": {
                "title": "Remove User",
                "msg": "Input User ID to remove:",
                "remover": self.remove_user,
                "search": self.search_for_user,
            },
            "parts": {
                "title": "Remove Part",
                "msg": "Input Part ID to remove:",
                "remover": self.remove_part,
                "search": self.get_part_data,
            },
            "repairs": {
                "title": "Remove Repair",
                "msg": "Input Repair ID to remove:",
                "remover": self.remove_repair,
                "search": self.search_for_repair,
            },
            "vehicles": {
                "title": "Remove Vehicle",
                "msg": "Input VIN to remove:",
                "remover": self.remove_vehicle,
                "search": self.get_vehicle_data,
            },
        }

        return remove_dispatcher

    def is_valid_login_query(self, input_user, input_pass):
        """Searches the database for the queried user to see if
        the password matches, then sets the login status to true and sets
        the current user variable to the matched user's user id if the pior
        verfication was successful."""

        # search for input users password
        user_data = self.cursor.execute(
            """SELECT employee_id, password FROM employees WHERE username = (?);""",
            (input_user,),
        ).fetchone()

        if user_data is None:
            return False  # no user was found --> return false

        if sha512_crypt.verify(input_pass, user_data["password"]):
            # password matches --> set current user and login status, return true
            self.set_current_user(user_data["employee_id"])
            self.set_login_status(True)

            return True

        # password did not match --> not valid query return false
        return False

    def remove_user(self, employee_id, password):
        """Takes passed employee id and removes that employee from the database if
        the passed password is the correct password for that employee."""

        # get password for passed id
        target_pass = self.cursor.execute(
            """SELECT password FROM employees WHERE employee_id = (?);""",
            (employee_id,),
        ).fetchone()

        if target_pass is None:
            return False  # no password found for that id (invalid id) --> return false

        if sha512_crypt.verify(password, target_pass["password"]):
            # password matches --> remove user from database, return true
            self.cursor.execute(
                """DELETE FROM employees WHERE employee_id = (?);""", (employee_id,)
            )
            self.connection.commit()

            return True

        # password did not match --> return false
        return False

    def is_current_users_password(self, input_pass):
        """Checks if an input password matches the current users
        password in the database."""

        # search for current user's password
        user_pass = self.cursor.execute(
            """SELECT password FROM employees WHERE employee_id = (?);""",
            (self.current_user,),
        ).fetchone()

        if user_pass is None:
            return False  # no user was found for passed id (no current user)--> return false

        if sha512_crypt.verify(input_pass, user_pass["password"]):
            return True  # is current users password --> return true

        return False  # password did not match --> return false

    def is_current_users_username(self, username):
        """Checks if the passed username is the username of the current logged in database user."""

        # get username of current user
        current_username = self.cursor.execute(
            """SELECT username FROM employees WHERE employee_id = (?)""",
            (self.current_user,),
        ).fetchone()

        if current_username["username"] != username:
            return False  # passed username does not match --> return False

        return True  # matched --> return true

    def set_current_user(self, user_id):
        """Database's current user as the passed user_id, or switches to
        None if the user logged out."""

        self.current_user = user_id

    def insert_user(self, user_data):
        """Takes a set of inputs for a new user and inputs it into
        the database."""

        self.cursor.execute(
            """INSERT INTO employees 
            (username, 
            password, 
            name, 
            team, 
            lane_or_section, 
            is_tech, 
            is_writer) 
            VALUES(?, ?, ?, ?, ?, ?, ?);""",
            (
                user_data["username"],
                user_data["hash_pwrd"],
                user_data["name"],
                user_data["team"],
                user_data["lane_or_section"],
                user_data["is_tech"],
                user_data["is_writer"],
            ),
        )

        self.connection.commit()

    def set_login_status(self, status):
        """Sets the login status of the database."""

        self.is_logged_in = status

    def get_login_status(self):
        """Gets the login status of the database."""

        return self.is_logged_in

    def update_pass(self, new_pass):
        """Updates the users password in the database."""

        self.cursor.execute(
            """UPDATE employees SET password = (?) WHERE employee_id = (?);""",
            (
                new_pass,
                self.current_user,
            ),
        )

        self.connection.commit()

    def update_user_name(self, user_id, name):
        """Updates a user's name in the database."""

        self.cursor.execute(
            """UPDATE employees SET name = (?) WHERE employee_id = (?);""",
            (
                name,
                user_id,
            ),
        )

        self.connection.commit()

    def update_user_team(self, user_id, team):
        """Update a user's team in the database."""

        self.cursor.execute(
            """UPDATE employees SET team = (?) WHERE employee_id = (?);""",
            (
                team,
                user_id,
            ),
        )

        self.connection.commit()

    def update_user_lane_or_section(self, user_id, lane_or_section):
        """Update a user's lane or section in the database."""

        self.cursor.execute(
            """UPDATE employees SET lane_or_section = (?) WHERE employee_id = (?);""",
            (
                lane_or_section,
                user_id,
            ),
        )

        self.connection.commit()

    def search_for_user(self, user_id):
        """Searchs the database for the requested id and return that users
        data back to the app for display."""

        return self.cursor.execute(
            """SELECT * FROM employees WHERE employee_id = (?);""", (user_id,)
        ).fetchone()

    def is_username_in_use(self, username):
        """Checks the database to see if a username is already in use."""

        return self.cursor.execute(
            """SELECT username FROM employees WHERE username = (?);""", (username,)
        ).fetchall()

    def get_all_users(self):
        """Returns all users id's, names, and lane/section in the database."""

        return self.cursor.execute(
            """SELECT employee_id, name, lane_or_section FROM employees;"""
        ).fetchall()

    def get_user_id_for_username(self, username):
        """Searches the database for a username and returns that users employee_id."""

        return self.cursor.execute(
            """SELECT employee_id FROM employees WHERE username = (?)""", (username,)
        ).fetchone()

    def insert_repair(self, repair_data):
        """Inserts a new repair into the database and call the functions
        need to add the repair to the valid employee's repair list."""

        self.cursor.execute(
            """INSERT INTO repairs 
            (repair_id, 
            total_cost, 
            labor, 
            parts_cost, 
            drop_off_date, 
            problem_description, 
            technician, 
            service_writer, 
            vehicle) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);""",
            (
                repair_data["repair_id"],
                repair_data["total_cost"],
                repair_data["labor"],
                repair_data["parts_cost"],
                repair_data["drop_off_date"],
                repair_data["problem_description"],
                repair_data["tech_id"],
                repair_data["writer_id"],
                repair_data["vin"],
            ),
        )

        self.connection.commit()

    def remove_repair(self, repair, password):
        """Removes the passed repair id if passed password is correct."""

        # if password is valid delete the repair from the table --> return true for success
        if self.is_current_users_password(password):
            self.cursor.execute(
                """DELETE FROM repairs WHERE repair_id = (?)""", (repair,)
            )

            self.connection.commit()

            return True

        return False

    def search_for_repair(self, repair_id):
        """Takes the repair id passed to it and retrieves it from the database,
        then returns that data to be displayed."""

        return self.cursor.execute(
            """SELECT * FROM repairs WHERE repair_id = (?);""", (repair_id,)
        ).fetchone()

    def get_all_active_repairs(self):
        """Returns all active repairs (no completion date)."""

        return self.cursor.execute(
            """SELECT * FROM repairs WHERE repair_completed_date IS NULL;"""
        ).fetchall()

    def get_repairs_assigned(self, employee_id):
        """Returns all repair_ids assosiated with the passed employee id (No
        completion data)."""

        # get user data
        user = self.search_for_user(employee_id)

        # get repair id where tech id matches passed id if user is tech
        if user["is_tech"] == 1:
            return self.cursor.execute(
                """SELECT repair_id FROM repairs WHERE technician = (?)
                AND repair_completed_date IS NULL;""",
                (employee_id,),
            ).fetchall()

        # get repair id where writer id matches passed id if user is writer
        if user["is_writer"] == 1:
            return self.cursor.execute(
                """SELECT repair_id FROM repairs WHERE service_writer = (?)
                AND repair_completed_date IS NULL;""",
                (employee_id,),
            ).fetchall()

        # passed id did not produce a result --> return false
        return None

    def update_repair_service_writer(self, repair_id, service_writer_id):
        """Updates the targted repair with a new service writer."""

        self.cursor.execute(
            """UPDATE repairs SET service_writer = (?) WHERE repair_id = (?);""",
            (
                service_writer_id,
                repair_id,
            ),
        )

        self.connection.commit()

    def update_repair_tech(self, repair_id, tech_id):
        """Updates the targeted repair with a new technician."""

        self.cursor.execute(
            """UPDATE repairs SET technician = (?) WHERE repair_id = (?);""",
            (
                tech_id,
                repair_id,
            ),
        )

        self.connection.commit()

    def update_total_repair_cost(self, repair_id, total_cost):
        """Updates the total repair cost of the targeted repair."""

        self.cursor.execute(
            """UPDATE repairs SET total_cost = (?) WHERE repair_id = (?);""",
            (
                total_cost,
                repair_id,
            ),
        )

        self.connection.commit()

    def update_labor_cost(self, repair_id, labor_repair_cost):
        """Updates the labor cost of the targeted repair."""

        labor_repair_cost = float(labor_repair_cost)

        self.cursor.execute(
            """UPDATE repairs SET labor = (?) WHERE repair_id = (?);""",
            (
                labor_repair_cost,
                repair_id,
            ),
        )

        self.connection.commit()

    def update_repair_parts_cost(self, repair_id, parts_cost):
        """Updates the part cost of the targeted repair."""

        self.cursor.execute(
            """UPDATE repairs SET parts_cost = (?) WHERE repair_id = (?);""",
            (
                parts_cost,
                repair_id,
            ),
        )

        self.connection.commit()

    def update_repair_complete_date(self, repair_id, completion_date):
        """Updates the completion date of the targeted repair."""

        self.cursor.execute(
            """UPDATE repairs SET repair_completed_date = (?) WHERE repair_id = (?);""",
            (
                completion_date,
                repair_id,
            ),
        )

        self.connection.commit()

    def update_repair_problem(self, repair_id, problem_description):
        """Updates the problem description of the targted repair."""

        self.cursor.execute(
            """UPDATE repairs SET problem_description = (?) WHERE repair_id = (?);""",
            (
                problem_description,
                repair_id,
            ),
        )

        self.connection.commit()

    def update_repair_description(self, repair_id, repair_description):
        """Updates the repair description of the targeted repair."""

        self.cursor.execute(
            """UPDATE repairs SET repair_description = (?) WHERE repair_id = (?);""",
            (
                repair_description,
                repair_id,
            ),
        )

        self.connection.commit()

    def insert_part_listing(self, repair_id, part_id):
        """Updates the list of required parts for the repair."""

        self.cursor.execute(
            """INSERT INTO part_listings (part_id, repair_id) VALUES (?, ?);""",
            (part_id, repair_id),
        )

        self.connection.commit()

    def drop_part_listing(self, repair_id, part_id):
        """Removes one part listing from the part listings table, does so by
        referening both a repair id and part id then fetching one listing
        for a listing id."""

        # produce a listing id from passed repair and part ids
        listing_id = self.cursor.execute(
            """SELECT listing_id FROM part_listings 
                WHERE part_id = (?) AND repair_id = (?)""",
            (part_id, repair_id),
        ).fetchone()

        if listing_id is None:
            return False  # no such listing --> return false

        # delete produced listing --> return true for success
        self.cursor.execute(
            """DELETE FROM part_listings WHERE listing_id = (?)""",
            (listing_id["listing_id"],),
        )

        self.connection.commit()

        return True

    def get_repair_part_listings(self, repair_id):
        """Returns all part listings for the assosiated repair_id."""

        return self.cursor.execute(
            """SELECT * FROM part_listings WHERE repair_id = (?)""", (repair_id,)
        ).fetchall()

    def insert_part(self, part_data):
        """Inserts a new part into the database."""

        self.cursor.execute(
            """INSERT INTO parts VALUES(?, ?, ?);""",
            (
                part_data["part_id"],
                part_data["part_cost"],
                part_data["part_description"],
            ),
        )

        self.connection.commit()

    def remove_part(self, part, password):
        """Removes the passed part id if the passed password is the current
        users password."""

        # if password is valid --> remove part from table, return true for success
        if self.is_current_users_password(password):
            self.cursor.execute("""DELETE FROM parts WHERE part_id = (?)""", (part,))

            self.connection.commit()

            return True

        # password invalid --> return false for failure
        return False

    def get_all_parts_in_database(self):
        """Returns a list containing all parts in the database."""

        return self.cursor.execute("""SELECT * FROM parts;""").fetchall()

    def get_part_data(self, part_id):
        """Returns data for the passed part id."""

        return self.cursor.execute(
            """SELECT * FROM parts WHERE part_id = (?);""",
            (part_id,),
        ).fetchone()

    def update_part_cost(self, part_id, new_cost):
        """Updates the part cost in the database for the passed part id."""

        self.cursor.execute(
            """UPDATE parts SET part_cost = (?) WHERE part_id = (?);""",
            (
                new_cost,
                part_id,
            ),
        )

        self.connection.commit()

    def update_part_description(self, part_id, new_description):
        """Updates the part description in the databse for the passed part id."""

        self.cursor.execute(
            """UPDATE parts SET part_description = (?) WHERE part_id = (?);""",
            (
                new_description,
                part_id,
            ),
        )

        self.connection.commit()

    def insert_customer(self, customer_data):
        """Takes the passed customer data and enters a new customer into the database,
        returns the new customer id based on name, address and phone."""

        self.cursor.execute(
            """INSERT INTO customers (name, address, phone_number) VALUES (?, ?, ?);""",
            (
                customer_data["name"],
                customer_data["address"],
                customer_data["phone"],
            ),
        )

        self.connection.commit()

        customer_id = self.cursor.execute(
            """SELECT customer_id FROM customers WHERE
              name = (?) AND address = (?) AND phone_number = (?)""",
            (
                customer_data["name"],
                customer_data["address"],
                customer_data["phone"],
            ),
        ).fetchone()

        return customer_id["customer_id"]

    def remove_customer(self, customer, password):
        """Removes the passed customer id if the passed password is the current
        users password."""

        # if password is valid --> remove customer from table, return true for success
        if self.is_current_users_password(password):
            self.cursor.execute(
                """DELETE FROM customers WHERE customer_id = (?)""", (customer,)
            )

            self.connection.commit()

            return True

        # invalid password --> return false for failure
        return False

    def get_customer_data(self, customer_id):
        """Returns customer data for the passed customer id from the database."""

        return self.cursor.execute(
            """SELECT * FROM customers WHERE customer_id = (?);""",
            (customer_id,),
        ).fetchone()

    def get_all_customers(self):
        """Returns a all customers in the database."""

        return self.cursor.execute("""SELECT * FROM customers;""").fetchall()

    def update_customer_name(self, customer_id, new_name):
        """Updates the passed customer id to show the new name in the database."""

        self.cursor.execute(
            """UPDATE customers SET name = (?) WHERE customer_id = (?);""",
            (
                new_name,
                customer_id,
            ),
        )

        self.connection.commit()

    def update_customer_address(self, customer_id, new_address):
        """Updates the passed customer id to show the new address in the database."""

        self.cursor.execute(
            """UPDATE customers SET address = (?) WHERE customer_id = (?);""",
            (
                new_address,
                customer_id,
            ),
        )

        self.connection.commit()

    def update_customer_phone(self, customer_id, new_phone):
        """Updates the passed customer id to show the new phone number in the database."""

        self.cursor.execute(
            """UPDATE customers SET phone_number = (?) WHERE customer_id = (?);""",
            (
                new_phone,
                customer_id,
            ),
        )

        self.connection.commit()

    def insert_vehicle(self, vehicle_data):
        """Inserts new vehicle into the database from passed vehicle data."""

        self.cursor.execute(
            """INSERT INTO vehicles VALUES(?, ?, ?, ?, ?, ?, ?, ?);""",
            (
                vehicle_data["vin"],
                vehicle_data["model"],
                vehicle_data["make"],
                vehicle_data["year"],
                vehicle_data["color"],
                vehicle_data["engine"],
                vehicle_data["repair_request"],
                vehicle_data["owner"],
            ),
        )

        self.connection.commit()

    def remove_vehicle(self, vin, password):
        """Removes passed vehicle if the passed password is the current users
        password."""

        # if valid password --> delete passed vin from table, return true for success
        if self.is_current_users_password(password):
            self.cursor.execute("""DELETE FROM vehicles WHERE vin = (?)""", (vin,))

            self.connection.commit()

            return True

        # password invalid --> return false for failure
        return False

    def get_vehicle_data(self, vin):
        """Returns vehicle data based on vin."""

        return self.cursor.execute(
            """SELECT * FROM vehicles WHERE vin = (?);""",
            (vin,),
        ).fetchone()

    def get_all_vehicles(self):
        """Returns all vehicles in the database."""

        return self.cursor.execute("""SELECT * FROM vehicles;""").fetchall()

    def vehicle_is_owned(self, vin):
        """Checks if a vin has a owner listed."""

        # get owner of passed vin
        owner = self.cursor.execute(
            """SELECT owner FROM vehicles WHERE vin = (?);""", (vin,)
        ).fetchone()

        if owner["owner"] is not None:
            return True  # vehicle has listed owner --> return true

        return False

    def get_owned_vehicles(self, customer_id):
        """Returns all vehicles assosiated with the passed customer id."""

        return self.cursor.execute(
            """SELECT * FROM vehicles WHERE owner = (?)""", (customer_id,)
        ).fetchall()

    def add_vehicle_owner(self, vin, customer_id):
        """Adds owner to passed vin."""

        self.cursor.execute(
            """UPDATE vehicles SET owner = (?) WHERE vin = (?);""",
            (customer_id, vin),
        )

        self.connection.commit()

    def remove_vehicle_owner(self, vin, customer_id):
        """Removes owner from passed vin."""

        # get vehicle data
        vehicle = self.cursor.execute(
            """SELECT * FROM vehicles WHERE owner = (?) AND vin = (?)""",
            (
                customer_id,
                vin,
            ),
        ).fetchone()

        #  if vins and ids match --> set owner to none, return true for success
        if vehicle["vin"] == vin and vehicle["owner"] == int(customer_id):
            self.cursor.execute(
                """UPDATE vehicles SET owner = (?) WHERE vin = (?);""",
                (None, vin),
            )

            self.connection.commit()

            return True

        # vin did not have that owner listed --> return false for failure
        return False

    def update_vehicle_make(self, vin, new_make):
        """Updates the passed vin to have the passed new make in the database."""

        self.cursor.execute(
            """UPDATE vehicles SET make = (?) WHERE vin = (?);""",
            (
                new_make,
                vin,
            ),
        )

        self.connection.commit()

    def update_vehicle_model(self, vin, new_model):
        """Updates the passed vin to have the passed new model in the database."""

        self.cursor.execute(
            """UPDATE vehicles SET model = (?) WHERE vin = (?);""",
            (
                new_model,
                vin,
            ),
        )

        self.connection.commit()

    def update_vehicle_year(self, vin, new_year):
        """Updates the passed vin to have the passed new year in the database."""

        self.cursor.execute(
            """UPDATE vehicles SET year = (?) WHERE vin = (?);""",
            (
                new_year,
                vin,
            ),
        )

        self.connection.commit()

    def update_vehicle_color(self, vin, new_color):
        """Updates the passed vin to have the passed new color in the database."""

        self.cursor.execute(
            """UPDATE vehicles SET color = (?) WHERE vin = (?);""",
            (
                new_color,
                vin,
            ),
        )

        self.connection.commit()

    def update_vehicle_engine(self, vin, new_engine):
        """Updates the passed vin to have the new passed engine in the database."""

        self.cursor.execute(
            """UPDATE vehicles SET engine = (?) WHERE vin = (?);""",
            (
                new_engine,
                vin,
            ),
        )

        self.connection.commit()

    def update_vehicle_active_repair(self, vin, repair_id=None):
        """Updates the active repair id of a passed vehicle to the passed repair id,
        defaults to none for if repair was completed."""

        self.cursor.execute(
            """UPDATE vehicles SET repair_request = (?) WHERE vin = (?);""",
            (repair_id, vin),
        )

        self.connection.commit()

    def has_active_repair(self, vin):
        """Searches if a passed vin has an active repair."""

        # gets repair request for passed vin
        repair_request = self.cursor.execute(
            """SELECT repair_request FROM vehicles WHERE vin = (?);""", (vin,)
        ).fetchone()

        # if none --> return false for no current repair assigned
        if repair_request["repair_request"] is None:
            return False

        # has repair request --> return it
        return repair_request["repair_request"]

    def get_vehicle_repair_history(self, vin):
        """Returns all completed repairs assosiated with the passed vin."""

        return self.cursor.execute(
            """SELECT repair_id FROM repairs WHERE vehicle = (?) 
            AND repair_completed_date IS NOT NULL""",
            (vin,),
        ).fetchall()

    def remove_row(self, gui, target):
        """Takes passed gui and table to reference the remove row dispatcher
        and remove the input id from its applicable table."""

        # set the title, msg, and remover (function) variables based on passed target
        title = self.remove_row_distpatcher[target]["title"]
        msg = self.remove_row_distpatcher[target]["msg"]
        remover = self.remove_row_distpatcher[target]["remover"]

        if not self.get_login_status():
            return gui.show_error(
                "You must be logged in to access this page or function."
            )

        # get an id to remove from user
        id_to_remove = self.get_remove_id_loop(gui, target, title, msg)

        # user canceled at id --> return none
        if not id_to_remove:
            return None

        while True:
            # get password
            password = gui.confirm_delete(title)

            # if the user clicked cancel --> return none
            if password is False:
                return None

            # user hit ok but no password
            if password is True:
                gui.show_error("No password entered!")

                continue

            # if password does not meet the app requirements
            if not validate.is_valid_password(password):
                gui.show_error("Invalid password!")

                continue

            # if remove function fails
            if not remover(id_to_remove, password):
                gui.show_error("Invalid ID/VIN and or password!")

                continue

            # removal successful
            return gui.show_success("Removed succesfully.")

    def get_remove_id_loop(self, gui, target, title, msg):
        """Loop to contiune asking for an user id to remove."""

        while True:
            # get id from user
            id_to_remove = gui.show_id_search_request(title, msg)

            # if the user clicked cancel
            if id_to_remove is False:
                return None

            # if user hit ok but put in no id
            if id_to_remove is True:
                gui.show_error("No ID/VIN entered!")

                continue

            # if id does not match app requirements
            if not validate.is_valid_id(id_to_remove):
                gui.show_error("Invalid ID/VIN!")

                continue

            # if no row found for input id
            if not self.remove_row_distpatcher[target]["search"](id_to_remove):
                gui.show_error("Invalid ID/VIN!")

                continue

            # return valid id
            return id_to_remove
