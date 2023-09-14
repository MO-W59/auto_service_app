"""This module defines the the database class and functions used to query/execute to it."""


import os
import sqlite3
import json
from passlib.hash import sha512_crypt


class AppDatabase:
    """This class defines database objects for the application."""

    def __init__(self):
        self.is_logged_in = False
        self.current_user = None
        self.data_directory = os.path.dirname(os.path.realpath(__file__)) + "\\data\\"
        self.connection = sqlite3.connect(self.data_directory + "data.db")
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        """This function will create the tables in the database if they do not already exist."""

        checked_list = self.cursor.execute(
            """SELECT name FROM sqlite_master WHERE type='table'
                    AND name='customers'; """
        ).fetchall()

        if checked_list == []:
            self.cursor.execute(
                """CREATE TABLE customers (
                                    customer_id text,
                                    name text,
                                    address text,
                                    phone_number text,
                                    list_of_vehicles text)"""
            )

            self.connection.commit()

        checked_list = self.cursor.execute(
            """SELECT name FROM sqlite_master WHERE type='table'
                    AND name='service_writers'; """
        ).fetchall()

        if checked_list == []:
            self.cursor.execute(
                """CREATE TABLE service_writers (
                                    employee_id text,
                                    username text,
                                    password text,
                                    name text,
                                    team text,
                                    lane integer,
                                    assigned_repairs text)"""
            )

            self.connection.commit()

        checked_list = self.cursor.execute(
            """SELECT name FROM sqlite_master WHERE type='table'
                    AND name='technicians'; """
        ).fetchall()

        if checked_list == []:
            self.cursor.execute(
                """CREATE TABLE technicians (
                                    employee_id text,
                                    username text,
                                    password text,
                                    name text,
                                    team text,
                                    section text,
                                    assigned_repairs text)"""
            )

            self.connection.commit()

        checked_list = self.cursor.execute(
            """SELECT name FROM sqlite_master WHERE type='table'
                    AND name='parts'; """
        ).fetchall()

        if checked_list == []:
            self.cursor.execute(
                """CREATE TABLE parts (
                                    part_id text,
                                    part_cost real,
                                    part_description text)"""
            )

            self.connection.commit()

        checked_list = self.cursor.execute(
            """SELECT name FROM sqlite_master WHERE type='table'
                    AND name='repairs'; """
        ).fetchall()

        if checked_list == []:
            self.cursor.execute(
                """CREATE TABLE repairs (
                                    repair_id text,
                                    total_cost real,
                                    labor real,
                                    parts_cost real,
                                    drop_off_date text,
                                    repair_completed_date text,
                                    problem_description text,
                                    repair_description text,
                                    required_parts text,
                                    technician text,
                                    service_writer text,
                                    vehicle text)"""
            )

            self.connection.commit()

        checked_list = self.cursor.execute(
            """SELECT name FROM sqlite_master WHERE type='table'
                    AND name='vehicles'; """
        ).fetchall()

        if checked_list == []:
            self.cursor.execute(
                """CREATE TABLE vehicles (
                                    vin text,
                                    model text,
                                    make text,
                                    year text,
                                    color text,
                                    engine text,
                                    repair_history text,
                                    repair_request text)"""
            )

            self.connection.commit()

        checked_list = self.cursor.execute(
            """SELECT name FROM sqlite_master WHERE type='table'
                    AND name='counter_ids'; """
        ).fetchall()

        if checked_list == []:
            self.cursor.execute(
                """CREATE TABLE counter_ids (
                                    writer_count integer,
                                    tech_count integer,
                                    customer_count integer)"""
            )

            self.cursor.execute("""INSERT INTO counter_ids VALUES (1, 1, 1)""")

            self.connection.commit()

    def gen_id(self, target_table):
        """This function will read the counter_ids table in the database and return a string with
        an appilcable id for the targeted table. Then it will update the counter in the counter_ids
        table."""

        created_id = ""
        counter_list = self.cursor.execute("""SELECT * FROM counter_ids""").fetchone()

        writer_count = counter_list[0]
        tech_count = counter_list[1]
        customer_count = counter_list[2]

        if target_table == "service_writers":
            created_id = "w" + str(writer_count)

            new_writer_count = writer_count + 1

            sql_statement = f"""UPDATE counter_ids SET writer_count = {new_writer_count}
                         WHERE writer_count = {writer_count}"""

            self.cursor.execute(sql_statement)

            self.connection.commit()

            return created_id

        if target_table == "technicians":
            created_id = "t" + str(tech_count)

            new_tech_count = tech_count + 1

            sql_statement = f"""UPDATE counter_ids SET tech_count = {new_tech_count}
                         WHERE tech_count = {tech_count}"""

            self.cursor.execute(sql_statement)

            self.connection.commit()

            return created_id

        if target_table == "customers":
            created_id = "c" + str(customer_count)

            new_customer_count = customer_count + 1

            sql_statement = f"""UPDATE counter_ids SET customer_count = {new_customer_count}
                         WHERE customer_count = {customer_count}"""

            self.cursor.execute(sql_statement)

            self.connection.commit()

            return created_id

    def is_valid_login_query(self, input_user, input_pass):
        """This function searches the database for the queried user to see if
        the password matches, then sets the login status to true and sets
        the current user variable to the matched users user id if the pior
        verfication was successful."""

        user_data = self.cursor.execute(
            """SELECT * FROM service_writers
                                                 WHERE username = (?)""",
            (input_user,),
        ).fetchall()
        user_data = (
            user_data
            + self.cursor.execute(
                """SELECT * FROM technicians
                                                 WHERE username = (?)""",
                (input_user,),
            ).fetchall()
        )

        if user_data == []:
            return False

        target_hash = user_data[0][2]

        if sha512_crypt.verify(input_pass, target_hash):
            self.set_current_user(user_data[0][0])

            self.set_login_status(True)

            return True

        return False

    def is_current_users_password(self, input_pass):
        """This function will check if an input password matches the current users password in the database."""

        user_data = self.cursor.execute(
            """SELECT * FROM service_writers
                                                 WHERE employee_id = (?)""",
            (self.current_user,),
        ).fetchall()
        user_data = (
            user_data
            + self.cursor.execute(
                """SELECT * FROM technicians
                                                         WHERE employee_id = (?)""",
                (self.current_user,),
            ).fetchall()
        )

        if user_data == []:
            return False

        if sha512_crypt.verify(input_pass, user_data[0][2]):
            return True

        return False

    def set_current_user(self, user_id):
        """This function will set the databases current user as the passed user_id."""

        self.current_user = user_id

    def insert_user(self, inputs):
        """This function takes a set of inputs for a new user and inputs it into
        the database."""

        target_table = inputs[0]
        user_id = inputs[1]
        input_user = inputs[2]
        hashed_pass = str(inputs[3])
        new_name = inputs[4]
        new_team = inputs[5]
        section_or_lane = inputs[6]
        assigined_repairs = json.dumps(inputs[7])

        if target_table == "service_writers":
            self.cursor.execute(
                """INSERT INTO service_writers VALUES(?, ?, ?, ?, ?, ?, ?);""",
                (
                    user_id,
                    input_user,
                    hashed_pass,
                    new_name,
                    new_team,
                    section_or_lane,
                    assigined_repairs,
                ),
            )

            self.connection.commit()

        if target_table == "technicians":
            self.cursor.execute(
                """INSERT INTO technicians VALUES(?, ?, ?, ?, ?, ?, ?);""",
                (
                    user_id,
                    input_user,
                    hashed_pass,
                    new_name,
                    new_team,
                    section_or_lane,
                    assigined_repairs,
                ),
            )

            self.connection.commit()

    def set_login_status(self, passed_bool):
        """Sets the login status of the database."""

        self.is_logged_in = passed_bool

    def get_login_status(self):
        """Gets the login status of the database."""

        return self.is_logged_in

    def update_pass(self, user, old_pass, new_pass):
        """This function will update the users password in the data base."""

        new_pass = sha512_crypt.hash(new_pass)

        user_data = self.cursor.execute(
            """SELECT * FROM service_writers
                                                 WHERE username = (?)""",
            (user,),
        ).fetchall()
        user_data = (
            user_data
            + self.cursor.execute(
                """SELECT * FROM technicians
                                                 WHERE username = (?)""",
                (user,),
            ).fetchall()
        )

        if user_data == []:
            return False

        target_hash = user_data[0][2]

        target_id = user_data[0][0]

        if sha512_crypt.verify(old_pass, target_hash):
            if target_id.startswith("t"):
                self.cursor.execute(
                    """UPDATE technicians SET password = (?) WHERE
                                             employee_id = (?)""",
                    (
                        new_pass,
                        target_id,
                    ),
                )

                self.connection.commit()

                return True

            if target_id.startswith("w"):
                self.cursor.execute(
                    """UPDATE service_writers SET password = (?)
                                             WHERE employee_id = (?)""",
                    (
                        new_pass,
                        target_id,
                    ),
                )

                self.connection.commit()

                return True

        return False

    def update_user_name(self, user_id, new_name):
        """This fucntion will update a user's name in the database."""

        if user_id.startswith("t"):
            self.cursor.execute(
                """UPDATE technicians SET name = (?) WHERE
                                         employee_id = (?)""",
                (
                    new_name,
                    user_id,
                ),
            )

            self.connection.commit()

            return

        if user_id.startswith("w"):
            self.cursor.execute(
                """UPDATE service_writers SET name = (?) WHERE
                                             employee_id = (?)""",
                (
                    new_name,
                    user_id,
                ),
            )

            self.connection.commit()

            return

    def update_user_team(self, user_id, new_team):
        """This function will update a user's team in the database."""

        if user_id.startswith("t"):
            self.cursor.execute(
                """UPDATE technicians SET team = (?) WHERE
                                         employee_id = (?)""",
                (
                    new_team,
                    user_id,
                ),
            )

            self.connection.commit()

            return

        if user_id.startswith("w"):
            self.cursor.execute(
                """UPDATE service_writers SET name = (?) WHERE
                                         employee_id = (?)""",
                (
                    new_team,
                    user_id,
                ),
            )

            self.connection.commit()

            return

    def update_user_lane(self, user_id, new_lane):
        """This function will update a user's lane in the database. (service writers)"""

        self.cursor.execute(
            """UPDATE service_writers SET lane = (?) WHERE
                                     employee_id = (?)""",
            (
                new_lane,
                user_id,
            ),
        )

        self.connection.commit()

    def update_user_section(self, user_id, new_section):
        """This function will update a user's section in the database. (technicians)"""

        self.cursor.execute(
            """UPDATE technicians SET section = (?) WHERE
                                     employee_id = (?)""",
            (
                new_section,
                user_id,
            ),
        )

        self.connection.commit()

    def search_for_user(self, user_id):
        """This function will search the database for the requested id and return that users
        data back to the app for display."""

        if user_id.startswith("t"):
            user_data = self.cursor.execute(
                """SELECT * FROM technicians WHERE employee_id = (?)""", (user_id,)
            ).fetchone()

            return user_data

        elif user_id.startswith("w"):
            user_data = self.cursor.execute(
                """SELECT * FROM service_writers WHERE
                                                     employee_id = (?)""",
                (user_id,),
            ).fetchone()

            return user_data

        else:
            return None

    def is_username_in_use(self, username):
        """Checks the database to see if a username is already in use."""

        user_data = self.cursor.execute(
            """SELECT * FROM technicians WHERE
                                        username = (?)""",
            (username,),
        ).fetchall()

        user_data = (
            user_data
            + self.cursor.execute(
                """SELECT * FROM service_writers WHERE
                                                    username = (?)""",
                (username,),
            ).fetchall()
        )

        return user_data

    def insert_repair(self, inputs):
        """This function will insert a new repair into the database and call the functions
        need to add the repair to the valid employee's repair list."""

        repair_id = inputs[0]
        total_cost = inputs[1]
        labor = inputs[2]
        parts_cost = inputs[3]
        drop_off_date = inputs[4]
        repair_completed_date = inputs[5]
        problem_description = inputs[6]
        repair_description = inputs[7]
        required_parts = json.dumps(inputs[8])
        technician_id = inputs[9]
        service_writer_id = inputs[10]
        vehicle = inputs[11]

        self.cursor.execute(
            """INSERT INTO repairs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                repair_id,
                total_cost,
                labor,
                parts_cost,
                drop_off_date,
                repair_completed_date,
                problem_description,
                repair_description,
                required_parts,
                technician_id,
                service_writer_id,
                vehicle,
            ),
        )

        self.connection.commit()

        self.add_repair_to_tech(technician_id, repair_id)

        self.add_repair_to_writer(service_writer_id, repair_id)

    def add_repair_to_tech(self, technician_id, repair_id):
        """This function will add the passed repair to the passed technician's repair list."""

        user_data = self.cursor.execute(
            """SELECT * FROM technicians WHERE employee_id = (?)""", (technician_id,)
        ).fetchone()

        new_repair_list = []
        repair_data = json.loads(user_data[6])

        if repair_data != []:
            for prior_entry in repair_data:
                new_repair_list.append(prior_entry)

        new_repair_list.append(repair_id)

        new_dumped_list = json.dumps(new_repair_list)

        self.cursor.execute(
            """UPDATE technicians SET assigned_repairs = (?) WHERE
                                     employee_id = (?)""",
            (
                new_dumped_list,
                technician_id,
            ),
        )

        self.connection.commit()

    def remove_repair_from_tech(self, repair_id, tech_id):
        """This function will remove the passed repair from the technicians repair list."""

        user_data = self.cursor.execute(
            """SELECT * FROM technicians WHERE
                                                 employee_id = (?)""",
            (tech_id,),
        ).fetchone()

        new_repair_list = []
        repair_data = json.loads(user_data[6])

        if repair_data != []:
            for prior_entry in repair_data:
                if repair_id == prior_entry:
                    continue

                new_repair_list.append(prior_entry)

        new_dumped_list = json.dumps(new_repair_list)

        self.cursor.execute(
            """UPDATE technicians SET assigned_repairs = (?) WHERE
                                     employee_id = (?)""",
            (
                new_dumped_list,
                tech_id,
            ),
        )

        self.connection.commit()

    def add_repair_to_writer(self, service_writer_id, repair_id):
        """This function will add the passed repair to the passed service writer's repair list."""

        user_data = self.cursor.execute(
            """SELECT * FROM service_writers WHERE employee_id = (?)""",
            (service_writer_id,),
        ).fetchone()

        new_repair_list = []
        repair_data = json.loads(user_data[6])

        if repair_data != []:
            for prior_entry in repair_data:
                new_repair_list.append(prior_entry)

        new_repair_list.append(repair_id)

        new_dumped_list = json.dumps(new_repair_list)

        self.cursor.execute(
            """UPDATE service_writers SET assigned_repairs = (?) WHERE
                                     employee_id = (?)""",
            (
                new_dumped_list,
                service_writer_id,
            ),
        )

        self.connection.commit()

    def remove_repair_from_writer(self, repair_id, service_writer_id):
        """This function will remove the passed repair from the service writers repair list."""

        user_data = self.cursor.execute(
            """SELECT * FROM service_writers WHERE
                                                 employee_id = (?)""",
            (service_writer_id,),
        ).fetchone()

        new_repair_list = []
        repair_data = json.loads(user_data[6])

        if repair_data != []:
            for prior_entry in repair_data:
                if repair_id == prior_entry:
                    continue

                new_repair_list.append(prior_entry)

        new_dumped_list = json.dumps(new_repair_list)

        self.cursor.execute(
            """UPDATE service_writers SET assigned_repairs = (?) WHERE
                                     employee_id = (?)""",
            (
                new_dumped_list,
                service_writer_id,
            ),
        )

        self.connection.commit()

    def search_for_repair(self, repair_id):
        """This function will take the repair id passed to it and retrieve it from the database,
        then return that data to be displayed."""

        repair_data = self.cursor.execute(
            """SELECT * FROM repairs WHERE repair_id = (?)""", (repair_id,)
        ).fetchone()

        return repair_data

    def get_all_repairs(self):
        """This function will return all active repairs (no completion date)."""

        list_of_repairs = self.cursor.execute("""SELECT * FROM repairs""").fetchall()

        for repair in list_of_repairs:
            if repair[5] is not None:
                list_of_repairs.remove(repair)

        return list_of_repairs

    def update_repair_service_writer(self, repair_id, service_writer_id, old_writer_id):
        """This function will update the targted repair with a new service writer."""

        self.cursor.execute(
            """UPDATE repairs SET service_writer = (?) WHERE
                                     repair_id = (?)""",
            (
                service_writer_id,
                repair_id,
            ),
        )

        self.connection.commit()

        self.add_repair_to_writer(service_writer_id, repair_id)

        self.remove_repair_from_writer(repair_id, old_writer_id)

    def update_repair_tech(self, repair_id, tech_id, old_tech_id):
        """This function will update the targeted repair with a new technician."""

        self.cursor.execute(
            """UPDATE repairs SET technician = (?) WHERE
                                     repair_id = (?)""",
            (
                tech_id,
                repair_id,
            ),
        )

        self.connection.commit()

        self.add_repair_to_tech(tech_id, repair_id)

        self.remove_repair_from_tech(repair_id, old_tech_id)

    def update_total_repair_cost(self, repair_id, total_repair_cost):
        """This function will update the total repair cost of the targeted repair."""

        self.cursor.execute(
            """UPDATE repairs SET total_cost = (?) WHERE
                                     repair_id = (?)""",
            (
                total_repair_cost,
                repair_id,
            ),
        )

        self.connection.commit()

    def update_labor_cost(self, repair_id, labor_repair_cost):
        """This function will update the labor cost of the targeted repair."""

        labor_repair_cost = float(labor_repair_cost)

        self.cursor.execute(
            """UPDATE repairs SET labor = (?) WHERE
                                     repair_id = (?)""",
            (
                labor_repair_cost,
                repair_id,
            ),
        )

        self.connection.commit()

    def update_repair_parts_cost(self, repair_id, parts_cost):
        """This function will update the part cost of the targeted repair."""

        self.cursor.execute(
            """UPDATE repairs SET parts_cost = (?) WHERE
                                     repair_id = (?)""",
            (
                parts_cost,
                repair_id,
            ),
        )

        self.connection.commit()

    def update_repair_complete_date(self, repair_id, completion_date):
        """This funcition will update the completion date of the targeted repair."""

        self.cursor.execute(
            """UPDATE repairs SET repair_completed_date = (?) WHERE
                                     repair_id = (?)""",
            (
                completion_date,
                repair_id,
            ),
        )

        self.connection.commit()

    def update_repair_problem(self, repair_id, problem_description):
        """This function will update the problem description of the targted repair."""

        self.cursor.execute(
            """UPDATE repairs SET problem_description = (?) WHERE
                                     repair_id = (?)""",
            (
                problem_description,
                repair_id,
            ),
        )

        self.connection.commit()

    def update_repair_description(self, repair_id, repair_description):
        """This function will update the repair description of the targeted repair."""

        self.cursor.execute(
            """UPDATE repairs SET repair_description = (?) WHERE
                                     repair_id = (?)""",
            (
                repair_description,
                repair_id,
            ),
        )

        self.connection.commit()

    def update_required_parts_add(self, repair_id, new_part):
        """This function will update the list of required parts for the repair."""

        repair_data = self.cursor.execute(
            """SELECT * FROM repairs WHERE
                                                   repair_id = (?)""",
            (repair_id,),
        ).fetchone()

        parts_list = json.loads(repair_data[8])
        new_parts_list = []

        if parts_list != []:
            for part in parts_list:
                new_parts_list.append(part)

        new_parts_list.append(new_part)
        new_dumped_list = json.dumps(new_parts_list)

        self.cursor.execute(
            """UPDATE repairs SET required_parts = (?) WHERE
                                     repair_id = (?)""",
            (
                new_dumped_list,
                repair_id,
            ),
        )

        self.connection.commit()

    def update_required_parts_remove(self, repair_id, removal_id):
        """This function will remove one instance of the passed part id from the
        repairs list of required parts."""

        repair_data = self.cursor.execute(
            """SELECT * FROM repairs WHERE
                                                   repair_id = (?)""",
            (repair_id,),
        ).fetchone()

        parts_list = json.loads(repair_data[8])
        parts_list.remove(removal_id)
        new_dumped_list = json.dumps(parts_list)

        self.cursor.execute(
            """UPDATE repairs SET required_parts = (?) WHERE
                            repair_id = (?)""",
            (
                new_dumped_list,
                repair_id,
            ),
        )

        self.connection.commit()

    def insert_parts(self, inputs):
        """This function will insert a new part into the database."""

        part_id = inputs[0]
        part_cost = float(inputs[1])
        part_description = inputs[2]

        self.cursor.execute(
            """INSERT INTO parts VALUES(?, ?, ?)""",
            (
                part_id,
                part_cost,
                part_description,
            ),
        )

        self.connection.commit()

    def get_all_parts_in_database(self):
        """This function will return a list containing all parts in the database."""

        return self.cursor.execute("""SELECT * FROM parts""").fetchall()

    def get_part_data(self, part_id):
        """This function will return data for the passed part id."""

        return self.cursor.execute(
            """SELECT * FROM parts WHERE
                                                 part_id = (?)""",
            (part_id,),
        ).fetchone()

    def update_part_cost(self, part_id, new_cost):
        """Updates the part cost in the database for the passed part id."""

        self.cursor.execute(
            """UPDATE parts SET part_cost = (?) WHERE
                            part_id = (?)""",
            (
                new_cost,
                part_id,
            ),
        )

        self.connection.commit()

    def update_part_description(self, part_id, new_description):
        """Updates the part description in the databse for the passed part id."""

        self.cursor.execute(
            """UPDATE parts SET part_description = (?) WHERE
                            part_id = (?)""",
            (
                new_description,
                part_id,
            ),
        )

        self.connection.commit()

    def insert_customer(self, inputs):
        """Takes the passed customer data and enters a new customer into the database."""

        self.cursor.execute(
            """INSERT INTO customers VALUES (?, ?, ?, ?, ?)""",
            (
                inputs[0],
                inputs[1],
                inputs[2],
                inputs[3],
                inputs[4],
            ),
        )

        self.connection.commit()

    def get_customer_data(self, customer_id):
        """Returns customer data for the passed customer id from the database."""

        return self.cursor.execute(
            """SELECT * FROM customers WHERE
                            customer_id = (?)""",
            (customer_id,),
        ).fetchone()

    def get_all_customers(self):
        """Returns a all customers in the database."""

        return self.cursor.execute("""SELECT * FROM customers""").fetchall()

    def vehicle_is_owned(self, vin_to_add):
        """Checks if a vin is listed in any customer's data in the database."""

        customer_data = self.get_all_customers()

        for data_set in customer_data:
            list_of_vins = json.loads(data_set[4])

            for vin in list_of_vins:
                if vin == vin_to_add:
                    return True

        return False

    def update_customer_name(self, customer_id, new_name):
        """Updates the passed customer id to show the new name in the database."""

        self.cursor.execute(
            """UPDATE customers SET name = (?) WHERE
                            customer_id = (?)""",
            (
                new_name,
                customer_id,
            ),
        )

        self.connection.commit()

    def update_customer_address(self, customer_id, new_address):
        """Updates the passed customer id to show the new address in the database."""

        self.cursor.execute(
            """UPDATE customers SET address = (?) WHERE
                            customer_id = (?)""",
            (
                new_address,
                customer_id,
            ),
        )

        self.connection.commit()

    def update_customer_phone(self, customer_id, new_phone):
        """Updates the passed customer id to show the new phone number in the database."""

        self.cursor.execute(
            """UPDATE customers SET phone_number = (?) WHERE
                            customer_id = (?)""",
            (
                new_phone,
                customer_id,
            ),
        )

        self.connection.commit()

    def add_vehicle_to_customer(self, customer_id, vin):
        """Adds vehicle to passed customer ID."""

        customer_data = self.cursor.execute(
            """SELECT * FROM customers WHERE
                            customer_id = (?)""",
            (customer_id,),
        ).fetchone()

        vehicle_list = json.loads(customer_data[4])

        new_vehicle_list = []

        new_vehicle_list.append(vin)

        for vehicle in vehicle_list:
            new_vehicle_list.append(vehicle)

        new_dumped_list = json.dumps(new_vehicle_list)

        self.cursor.execute(
            """UPDATE customers SET list_of_vehicles = (?) WHERE
                            customer_id = (?)""",
            (new_dumped_list, customer_id),
        )

        self.connection.commit()

    def remove_vehicle_from_customer(self, customer_id, vin):
        """Removes vehicle from passed customer ID."""

        customer_data = self.cursor.execute(
            """SELECT * FROM customers WHERE
                                            customer_id = (?)""",
            (customer_id,),
        ).fetchone()

        vehicle_list = json.loads(customer_data[4])

        vehicle_list.remove(vin)

        new_vehicle_list = []

        for vehicle in vehicle_list:
            new_vehicle_list.append(vehicle)

        new_dumped_list = json.dumps(new_vehicle_list)

        self.cursor.execute(
            """UPDATE customers SET list_of_vehicles = (?) WHERE
                            customer_id = (?)""",
            (new_dumped_list, customer_id),
        )

        self.connection.commit()

    def insert_vehicle(self, vehicle_data):
        """Inserts new vehicle into the database from passed vehicle data."""

        self.cursor.execute(
            """INSERT INTO vehicles VALUES(?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                vehicle_data[0],
                vehicle_data[1],
                vehicle_data[2],
                vehicle_data[3],
                vehicle_data[4],
                vehicle_data[5],
                json.dumps(vehicle_data[6]),
                vehicle_data[7],
            ),
        )

        self.connection.commit()

    def get_vehicle_data(self, vin):
        """Returns vehicle data based on vin."""

        return self.cursor.execute(
            """SELECT * FROM vehicles WHERE
                            vin = (?)""",
            (vin,),
        ).fetchone()

    def get_all_vehicles(self):
        """Returns all vehicles in the database."""

        return self.cursor.execute("""SELECT * FROM vehicles""").fetchall()

    def update_vehicle_make(self, vin, new_make):
        """Updates the passed vin to have the passed new make in the database."""

        self.cursor.execute(
            """UPDATE vehicles SET make = (?) WHERE
                            vin = (?)""",
            (
                new_make,
                vin,
            ),
        )

        self.connection.commit()

    def update_vehicle_model(self, vin, new_model):
        """Updates the passed vin to have the passed new model in the database."""

        self.cursor.execute(
            """UPDATE vehicles SET model = (?) WHERE
                            vin = (?)""",
            (
                new_model,
                vin,
            ),
        )

        self.connection.commit()

    def update_vehicle_year(self, vin, new_year):
        """Updates the passed vin to have the passed new year in the database."""

        self.cursor.execute(
            """UPDATE vehicles SET year = (?) WHERE
                            vin = (?)""",
            (
                new_year,
                vin,
            ),
        )

        self.connection.commit()

    def update_vehicle_color(self, vin, new_color):
        """Updates the passed vin to have the passed new color in the database."""

        self.cursor.execute(
            """UPDATE vehicles SET color = (?) WHERE
                            vin = (?)""",
            (
                new_color,
                vin,
            ),
        )

        self.connection.commit()

    def update_vehicle_engine(self, vin, new_engine):
        """Updates the passed vin to have the new passed engine in the database."""

        self.cursor.execute(
            """UPDATE vehicles SET engine = (?) WHERE
                            vin = (?)""",
            (
                new_engine,
                vin,
            ),
        )

        self.connection.commit()

    def update_vehicle_active_repair(self, vin, repair_id):
        """Updates the active repair id of a passed vehicle to the passed repair id."""

        self.cursor.execute(
            """UPDATE vehicles SET repair_request = (?)
                            WHERE vin = (?)""",
            (repair_id, vin),
        )

        self.connection.commit()

    def update_vehicle_completed_repairs(self, vin):
        """Moves the current acitve repair of a vehicle to the history of repairs."""

        vehicle_data = self.cursor.execute(
            """SELECT * FROM vehicles WHERE
                            vin = (?)""",
            (vin,),
        ).fetchone()

        completed_repair = vehicle_data[7]

        repair_history = json.loads(vehicle_data[6])

        repair_history.append(completed_repair)

        new_dumped_list = json.dumps(repair_history)

        self.cursor.execute(
            """UPDATE vehicles SET repair_history = (?), repair_request = (?)
                            WHERE vin = (?)""",
            (new_dumped_list, None, vin),
        )

        self.connection.commit()

    def has_active_repair(self, vin):
        """Searches if a passed vin has an active repair."""

        vehicle_data = self.cursor.execute(
            """SELECT * FROM vehicles WHERE vin = (?)""", (vin,)
        ).fetchone()

        return vehicle_data[7]
