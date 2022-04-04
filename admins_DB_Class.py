import sqlite3
import time


class DB:

    def __init__(self, DB_name):
        """
        The builder for DB class
        :param DB_name: The database's name
        :type DB_name: String
        """

        self.DB_name = DB_name

        # The table's name
        self.tbl_name = "admins"

        # The pointer to the DB
        self.conn = None

        # The pointer to the DB's cursor
        self.cursor = None

        # Creating the DB
        self.createDB()

    def createDB(self):
        """
        The function creates a new table in the given DB
        """

        self.conn = sqlite3.connect(self.DB_name)
        self.cursor = self.conn.cursor()

        sql = f"CREATE TABLE IF NOT EXISTS {self.tbl_name} (username TEXT, fullName TEXT, email TEXT, password TEXT)"
        self.cursor.execute(sql)

        # So the DB will update
        self.conn.commit()

    def _username_exist(self, username):
        """
        The function gets a username and returns whether the username exists already
        :param username: A username
        :type username: String
        :return: Whether the given username exists already
        :rtype: Boolean
        """

        sql = f"SELECT username FROM {self.tbl_name} WHERE username='{username}'"
        self.cursor.execute(sql)

        return not len(self.cursor.fetchall()) == 0

    def add_user(self, username, full_name, email, password):
        """
        The function gets a username and a name and adds them to the current table if the username don't already exists and whether he was added successfully or not
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

        if not self._username_exist(username):

            ret_value = True
            sql = f"INSERT INTO {self.tbl_name} VALUES ('{username}','{full_name}','{email}','{password}')"
            self.cursor.execute(sql)
            # So the DB will update instantly
            self.conn.commit()

        return ret_value

    def remove_user(self, username):
        """
        The function gets a username, checks if he is included in the table and if he is removes him and returns True, if he's not, returning False
        :param username: A username
        :type username: String
        :return: Whether he was in the table and got removed, or he was not in the table
        :rtype: Boolean
        """

        ret_value = False

        if self._username_exist(username):

            sql = f"DELETE FROM {self.tbl_name} WHERE username='{username}'"
            self.cursor.execute(sql)
            # So the DB will update instantly
            self.conn.commit()

            ret_value = True

        return ret_value

    def update_full_name(self, username, new_full_name):
        """
        The function gets a key which is a username and a new name to change the current name of the key if found
        :param username: A username
        :type username: String
        :param new_full_name: A name
        :type new_full_name: String
        :return: Whether the username was found and the name was updated or not
        """

        ret_value = False

        if self._username_exist(username):
            sql = f"UPDATE {self.tbl_name} SET fullName='{new_full_name}' WHERE username='{username}'"
            self.cursor.execute(sql)
            # So the DB will update instantly
            self.conn.commit()

            ret_value = True

        return ret_value

    def update_email(self, username, new_email):
        """
        The function gets a key which is a username and a new gender to change the current email of the key if found
        :param username: A username
        :type username: String
        :param new_email: A email
        :type new_email: String
        :return: Whether the username was found and the email was updated or not
        """

        ret_value = False

        if self._username_exist(username):
            sql = f"UPDATE {self.tbl_name} SET email='{new_email}' WHERE username='{username}'"
            self.cursor.execute(sql)
            # So the DB will update instantly
            self.conn.commit()

            ret_value = True

        return ret_value

    def update_password(self, username, new_password):
        """
        The function gets a key which is a username and a new gender to change the current password of the key if found
        :param username: A username
        :type username: String
        :param new_password: A password
        :type new_password: String
        :return: Whether the username was found and the password was updated or not
        """

        ret_value = False

        if self._username_exist(username):
            sql = f"UPDATE {self.tbl_name} SET password='{new_password}' WHERE username='{username}'"
            self.cursor.execute(sql)
            # So the DB will update instantly
            self.conn.commit()

            ret_value = True

        return ret_value

if __name__ == "__main__":

    # Creating a new DB object with the name adminsDB
    myDB = DB("adminsDB")

    newDB = DB("try1")

    # Testing the add_user function
    print(newDB.add_user("Noamiko", "Noam Tirosh", "noamiko.tirosh@gmail.com", "RandomPass"))
    print(newDB.add_user("Noamiko", "Noam Tirosh", "noamiko.tirosh@gmail.com", "RandomPass"))

    # Testing the remove_user function

    print(newDB.add_user("TempUser", "Delete This", "Temp.User@gmail.com", "TestDelete"))

    # Delay checking the user was really added
    time.sleep(7)

    print(newDB.remove_user("TempUser"))

    # Testing the update functions

    print(newDB.update_full_name("Noamiko", "Dina Kol"))

    print(newDB.update_email("Noamiko", "CheckBirth@gmail.com"))

    print(newDB.update_password("Noamiko", "NewPassword"))


    print(newDB.add_user("UserTest1", "User One", "User.One@gmail.com", "RandomPass"))

    print(newDB.add_user("UserTest2", "User Two", "User.Two@gmail.com", "RandomPass"))

    print(newDB.add_user("UserTest3", "User Three", "User.Three@gmail.com", "RandomPass"))
