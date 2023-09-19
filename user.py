from passlib.hash import sha512_crypt
import validate


def login_submit(App_Database, App_Ui):
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


def new_user_submit(App_Database, App_Ui):
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
