import sqlite3
import time


class DB:

    ADMINS_TAB = "admins"
    CAMERAS_TAB = "cameras"

    def __init__(self, db_name):
        """
        The builder for DB class
        :param db_name: The database's name
        :type db_name: String
        """

        self.db_name = db_name

        # The pointer to the DB
        self.conn = None

        # The pointer to the DB's cursor
        self.cursor = None

        # Creating the DB
        self.create_db()

    def create_db(self):
        """
        The function creates 2 new tables in the given DB, the tables of the admins, and of the cameras
        """

        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

        sql = f"CREATE TABLE IF NOT EXISTS {self.ADMINS_TAB} (username TEXT, full_name TEXT, email TEXT, password TEXT)"

        self.cursor.execute(sql)

        sql = f"CREATE TABLE IF NOT EXISTS {self.CAMERAS_TAB} (MAC TEXT, position INT, place TEXT)"
        
        self.cursor.execute(sql)

        # So the DB will update
        self.conn.commit()

    def _username_exist(self, username):
        """
        The function gets a username and returns whether the username exists already (ADMINS_TAB)
        :param username: A username
        :type username: String
        :return: Whether the given username exists already
        :rtype: Boolean
        """

        sql = f"SELECT username FROM {self.ADMINS_TAB} WHERE username='{username}'"
        self.cursor.execute(sql)

        return len(self.cursor.fetchall()) != 0

    def _email_exist(self, email):
        """
        The function gets an email and returns whether the email exists already (ADMINS_TAB)
        :param email: An email
        :type email: String
        :return: Whether the given username exists already
        :rtype: Boolean
        """

        sql = f"SELECT email FROM {self.ADMINS_TAB} WHERE username='{email}'"
        self.cursor.execute(sql)

        return len(self.cursor.fetchall()) != 0

    def add_user(self, username, full_name, email, password):
        """
        The function gets a username, a name, an email and a password, and adds them to the current table if the username and email don't already exists, and returns whether he was added successfully or not (ADMINS_TAB)
        :param username: A username
        :type username: String
        :param full_name: A name
        :type full_name: String
        :param email: An email
        :type email: String
        :param password: A password
        :type password: String
        :return: Whether the user was added successfully or not
        :rtype: Boolean
        """

        ret_value = False

        if not self._email_exist(email):

            if not self._username_exist(username):

                ret_value = True
                sql = f"INSERT INTO {self.ADMINS_TAB} VALUES ('{username}','{full_name}','{email}','{password}')"
                self.cursor.execute(sql)
                # So the DB will update instantly
                self.conn.commit()

            else:
                print("The given username is already registered in the system")

        else:
            print("The given email address is already registered in the system")

        return ret_value

    def remove_user(self, username):
        """
        The function gets a username, checks if he is included in the table and if he is removes him and returns True, if he's not, returning False (ADMINS_TAB)
        :param username: A username
        :type username: String
        :return: Whether he was in the table and got removed, or he was not in the table
        :rtype: Boolean
        """

        ret_value = False

        if self._username_exist(username):

            sql = f"DELETE FROM {self.ADMINS_TAB} WHERE username='{username}'"
            self.cursor.execute(sql)
            # So the DB will update instantly
            self.conn.commit()

            ret_value = True

        return ret_value

    def update_full_name(self, username, new_full_name):
        """
        The function gets a key which is a username and a new name to change the current name of the key if found (ADMINS_TAB)
        :param username: A username
        :type username: String
        :param new_full_name: A name
        :type new_full_name: String
        :return: Whether the username was found and the name was updated or not
        """

        ret_value = False

        if self._username_exist(username):
            sql = f"UPDATE {self.ADMINS_TAB} SET full_name='{new_full_name}' WHERE username='{username}'"
            self.cursor.execute(sql)
            # So the DB will update instantly
            self.conn.commit()

            ret_value = True

        return ret_value

    def update_email(self, username, new_email):
        """
        The function gets a key which is a username and a new gender to change the current email of the key if found (ADMINS_TAB)
        :param username: A username
        :type username: String
        :param new_email: A email
        :type new_email: String
        :return: Whether the username was found and the email was updated or not
        """

        ret_value = False

        if self._username_exist(username):

            # Check if the email is already registered
            if not self._email_exist(new_email):
                sql = f"UPDATE {self.ADMINS_TAB} SET email='{new_email}' WHERE username='{username}'"
                self.cursor.execute(sql)
                # So the DB will update instantly
                self.conn.commit()

                ret_value = True

            else:
                print("The given email address is already registered in the system")

        return ret_value

    def update_password(self, username, new_password):
        """
        The function gets a key which is a username and a new gender to change the current password of the key if found (ADMINS_TAB)
        :param username: A username
        :type username: String
        :param new_password: A password
        :type new_password: String
        :return: Whether the username was found and the password was updated or not
        """

        ret_value = False

        if self._username_exist(username):
            sql = f"UPDATE {self.ADMINS_TAB} SET password='{new_password}' WHERE username='{username}'"
            self.cursor.execute(sql)
            # So the DB will update instantly
            self.conn.commit()

            ret_value = True

        return ret_value

    def get_name_by_username(self, username):
        """
        Returns the full name of the username (ADMINS_TAB)
        :param username: The username of the person
        :type username: String
        :return: Returns the full name corresponding to the username
        :rtype: String inside a tuple inside a list [("Amit Mor")]
        """

        ret_value = None

        if self._username_exist(username):
            self.cursor.execute(f"SELECT full_name FROM {self.ADMINS_TAB} WHERE username='{username}'")

            ret_value = self.cursor.fetchall()

        return ret_value

    def get_email_by_username(self, username):
        """
        Returns the email of the username (ADMINS_TAB)
        :param username: The username of the person
        :type username: String
        :return: Returns the email corresponding to the username
        :rtype: String inside a tuple inside a list [("amit.mor@gmail.com")]
        """

        ret_value = None

        if self._username_exist(username):
            self.cursor.execute(f"SELECT email FROM {self.ADMINS_TAB} WHERE username='{username}'")

            ret_value = self.cursor.fetchall()

        return ret_value

    def do_passwords_match(self, username, password):
        """
        The function gets a username and a password, and checks if the username matches the password and returns like it (ADMINS_TAB)
        :param username: The username
        :type username: String
        :param password: The password
        :type password: String
        :return: Whether the username and the password match
        :rtype: Boolean
        """

        ret_value = False

        if self._username_exist(username):

            sql = f"SELECT password FROM {self.ADMINS_TAB} WHERE username='{username}'"
            self.cursor.execute(sql)
            fetch = self.cursor.fetchall()

            if fetch[0][0] == password:
                ret_value = True

            else:
                print("The password is wrong")

        else:
            print("Username wasn't found")

        return ret_value


    def _mac_exist(self, mac_address):
        """
        The function gets a MAC address and returns whether the address exists already (CAMERAS_TAB)
        :param mac_address: A MAC address
        :type mac_address: String
        :return: Whether the given MAC address exists already
        :rtype: Boolean
        """

        sql = f"SELECT MAC FROM {self.CAMERAS_TAB} WHERE MAC='{mac_address}'"
        self.cursor.execute(sql)

        return len(self.cursor.fetchall()) != 0

    def _position_exists(self, position):
        """
        The function gets a position and returns whether the position exists already (CAMERAS_TAB)
        :param position: A position
        :type position: String
        :return: Whether the given position exists already
        :rtype: Boolean
        """

        sql = f"SELECT position FROM {self.CAMERAS_TAB} WHERE position='{position}'"
        self.cursor.execute(sql)

        return len(self.cursor.fetchall()) != 0

    def add_camera(self, mac_address, position, place):
        """
        The function gets a MAC address of a computer that's connected to a camera, the position of the camera, and the place of the camera, and adds them to the current table if the MAC address don't already exists, and returns whether he was added successfully or not (CAMERAS_TAB)
        :param mac_address: A MAC address of a computer connected to a camera
        :type mac_address: String
        :param position: The position of the camera
        :type position: Integer
        :param place: The place of the camera
        :type place: String
        :return: Whether the camera was added successfully or not
        :rtype: Boolean
        """

        ret_value = False

        if not self._mac_exist(mac_address):

            ret_value = True
            sql = f"INSERT INTO {self.CAMERAS_TAB} VALUES ('{mac_address}','{position}','{place}')"
            self.cursor.execute(sql)
            # So the DB will update instantly
            self.conn.commit()

        else:
            print("The given MAC address is already registered in the system")

        return ret_value

    def get_position_by_mac(self, mac_address):
        """
        Returns the position of the camera by the camera's MAC address(CAMERA_TAB)
        :param mac_address: The MAC address of the camera
        :type mac_address: String
        :return: Returns the position corresponding to the MAC address
        :rtype: Integer inside a tuple inside a list [(4)]
        """

        ret_value = None

        if self._mac_exist(mac_address):
            self.cursor.execute(f"SELECT position FROM {self.CAMERAS_TAB} WHERE mac='{mac_address}'")

            ret_value = self.cursor.fetchall()

        return ret_value

    def get_place_by_mac(self, mac_address):
        """
        Returns the place of the camera by the camera's MAC address(CAMERA_TAB)
        :param mac_address: The MAC address of the camera
        :type mac_address: String
        :return: Returns the place corresponding to the MAC address
        :rtype: String inside a tuple inside a list [("Living Room")]
        """

        ret_value = None

        if self._mac_exist(mac_address):
            self.cursor.execute(f"SELECT place FROM {self.CAMERAS_TAB} WHERE mac='{mac_address}'")

            ret_value = self.cursor.fetchall()

        return ret_value

    def update_place(self, mac_address, new_place):
        """
        The function gets a key which is a MAC address and a new place to change the current place of the key if found (CAMERAS_TAB)
        :param mac_address: A MAC address
        :type mac_address: String
        :param new_place: A place
        :type new_place: String
        :return: Whether the MAC address was found and the place was updated or not
        """

        ret_value = False

        if self._mac_exist(mac_address):
            sql = f"UPDATE {self.CAMERAS_TAB} SET email='{new_place}' WHERE MAC='{mac_address}'"
            self.cursor.execute(sql)
            # So the DB will update instantly
            self.conn.commit()

            ret_value = True

        return ret_value

    def update_position(self, mac_address, new_position):
        """
        The function gets a key which is a MAC address and a new position to change the current position of the key if found (CAMERAS_TAB)
        :param mac_address: A MAC address
        :type mac_address: String
        :param new_position: A position
        :type new_position: Integer
        :return: Whether the MAC address was found and the position was updated or not
        """

        ret_value = False

        if self._mac_exist(mac_address):
            if not self._position_exists(new_position):
                sql = f"UPDATE {self.CAMERAS_TAB} SET position='{new_position}' WHERE MAC='{mac_address}'"
                self.cursor.execute(sql)
                # So the DB will update instantly
                self.conn.commit()

                ret_value = True

            else:
                print("The given position is already taken in the system")

        return ret_value


if __name__ == "__main__":

    # Creating a new DB object with the name adminsDB
    myDB = DB("myDB")

    # Testing the add_user function
    print(myDB.add_user("Noamiko", "Noam Tirosh", "noamiko.tirosh@gmail.com", "RandomPass"))
    print(myDB.add_user("Noamiko", "Noam Tirosh", "noamiko.tirosh@gmail.com", "RandomPass"))

    # Testing the remove_user function

    print(myDB.add_user("TempUser", "Delete This", "Temp.User@gmail.com", "TestDelete"))

    # Delay checking the user was really added
    time.sleep(3)

    print(myDB.remove_user("TempUser"))

    # Testing the update functions

    print(myDB.update_full_name("Noamiko", "Dina Kol"))

    print(myDB.update_email("Noamiko", "Check@gmail.com"))

    print(myDB.update_password("Noamiko", "NewPassword"))

    print(myDB.add_user("UserTest1", "User One", "User.One@gmail.com", "RandomPass"))

    print(myDB.add_user("UserTest2", "User Two", "User.Two@gmail.com", "RandomPass"))

    print(myDB.add_user("UserTest3", "User Three", "User.Three@gmail.com", "RandomPass"))

    get_name = myDB.get_name_by_username("Noamiko")

    try:
        print(get_name[0][0])
    except Exception as e:
        print("DB_Class.py:276", str(e))

    get_email = myDB.get_email_by_username("Noamiko")

    try:
        print(get_email[0][0])
    except Exception as e:
        print("DB_Class.py:283", str(e))
