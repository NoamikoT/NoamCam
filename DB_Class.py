import sqlite3
import time

# !!! DB = Database !!!

class DB:

    def __init__(self, DB_name):
        """
        The builder for DB class
        :param DB_name: The database's name
        :type DB_name: String
        """

        self.DB_name = DB_name

        # The table's name
        self.tbl_name = "players"

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

        sql = f"CREATE TABLE IF NOT EXISTS {self.tbl_name} (username TEXT, fullName TEXT, gender TEXT, birth TEXT, email TEXT, password TEXT)"
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

    def add_user(self, username, fullName, gender, birth, email, password):
        """
        The function gets a username and a name and adds them to the current table if the username doesn't already exists and whether he was added successfully or not
        :param username: A username
        :type username: String
        :param fullName: A name
        :type fullName: String
        :return: Whether he was added successfully or not
        :rtype: Boolean
        """

        retValue = False

        if not self._username_exist(username):

            retValue = True
            sql = f"INSERT INTO {self.tbl_name} VALUES ('{username}','{fullName}','{gender}','{birth}','{email}','{password}')"
            self.cursor.execute(sql)
            # So the DB will update instantly
            self.conn.commit()

        return retValue

    def remove_user(self, username):
        """
        The function gets a username, checks if he is included in the table and if he is removes him and returns True, if he's not, returning False
        :param username: A username
        :type username: String
        :return: Whether he was in the table and got removed, or he was not in the table
        :rtype: Boolean
        """

        retValue = False

        if self._username_exist(username):

            sql = f"DELETE FROM {self.tbl_name} WHERE username='{username}'"
            self.cursor.execute(sql)
            # So the DB will update instantly
            self.conn.commit()

            retValue = True

        return retValue

    def update_fullName(self, username, new_fullName):
        """
        The function gets a key which is a username and a new name to change the current name of the key if found
        :param username: A username
        :type username: String
        :param new_fullName: A name
        :type new_fullName: String
        :return: Whether the username was found and the name was updated or not
        """

        retValue = False

        if self._username_exist(username):
            sql = f"UPDATE {self.tbl_name} SET fullName='{new_fullName}' WHERE username='{username}'"
            self.cursor.execute(sql)
            # So the DB will update instantly
            self.conn.commit()

            retValue = True

        return retValue

    def update_gender(self, username, new_gender):
        """
        The function gets a key which is a username and a new gender to change the current gender of the key if found
        :param username: A username
        :type username: String
        :param new_gender: A gender
        :type new_gender: String
        :return: Whether the username was found and the gender was updated or not
        """

        retValue = False

        if self._username_exist(username):
            sql = f"UPDATE {self.tbl_name} SET gender='{new_gender}' WHERE username='{username}'"
            self.cursor.execute(sql)
            # So the DB will update instantly
            self.conn.commit()

            retValue = True

        return retValue

    def update_birth(self, username, new_birth):
        """
        The function gets a key which is a username and a new gender to change the current birth of the key if found
        :param username: A username
        :type username: String
        :param new_birth: A birth
        :type new_birth: String
        :return: Whether the username was found and the birth was updated or not
        """

        retValue = False

        if self._username_exist(username):
            sql = f"UPDATE {self.tbl_name} SET birth='{new_birth}' WHERE username='{username}'"
            self.cursor.execute(sql)
            # So the DB will update instantly
            self.conn.commit()

            retValue = True

        return retValue

    def update_email(self, username, new_email):
        """
        The function gets a key which is a username and a new gender to change the current email of the key if found
        :param username: A username
        :type username: String
        :param new_email: A email
        :type new_email: String
        :return: Whether the username was found and the email was updated or not
        """

        retValue = False

        if self._username_exist(username):
            sql = f"UPDATE {self.tbl_name} SET email='{new_email}' WHERE username='{username}'"
            self.cursor.execute(sql)
            # So the DB will update instantly
            self.conn.commit()

            retValue = True

        return retValue

    def update_password(self, username, new_password):
        """
        The function gets a key which is a username and a new gender to change the current password of the key if found
        :param username: A username
        :type username: String
        :param new_password: A password
        :type new_password: String
        :return: Whether the username was found and the password was updated or not
        """

        retValue = False

        if self._username_exist(username):
            sql = f"UPDATE {self.tbl_name} SET password='{new_password}' WHERE username='{username}'"
            self.cursor.execute(sql)
            # So the DB will update instantly
            self.conn.commit()

            retValue = True

        return retValue

    def get_by_gender(self, gender):
        """
        The function gets a gender and returns a list with all the rows where the gender match the given gender
        :param gender: A gender
        :type gender: String
        :return: A list with all the rows where the gender match the given gender
        :rtype: List
        """

        sql = f"SELECT * FROM {self.tbl_name} WHERE gender='{gender}'"
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def get_by_age(self, age):
        """
        The function gets an age and returns a list with all the rows where the birth date match the given age
        :param age: An age
        :type age: String
        :return: A list with all the rows where the birth date the given age
        :rtype: List
        """

        sql = f"SELECT * FROM {self.tbl_name} WHERE birth LIKE '%{2021 - int(age)}'"
        self.cursor.execute(sql)
        return self.cursor.fetchall()



if __name__ == "__main__":

    # Creating a new DB object with the name playersDB
    myDB = DB("playersDB")

    newDB = DB("try1")

    # Testing the add_user function
    print(newDB.add_user("Noamiko", "Noam Tirosh", "Male", "8/7/2004", "noamiko.tirosh@gmail.com", "RandomPass"))
    print(newDB.add_user("Noamiko", "Noam Tirosh", "Male", "8/7/2004", "noamiko.tirosh@gmail.com", "RandomPass"))




    # Testing the remove_user function

    print(newDB.add_user("TempUser", "Delete This", "Male", "1/1/2000", "Temp.User@gmail.com", "TestDelete"))

    # Delaying to check the user was really added
    time.sleep(7)

    print(newDB.remove_user("TempUser"))


    # Testing the update functions

    print(newDB.update_fullName("Noamiko", "Dina Kol"))

    print(newDB.update_gender("Noamiko", "Female"))

    print(newDB.update_birth("Noamiko", "20/2/1991"))

    print(newDB.update_email("Noamiko", "CheckBirth@gmail.com"))

    print(newDB.update_password("Noamiko", "NewPassword"))


    # Testing the getting gender and age from all function

    print(newDB.add_user("UserTest1", "User One", "Male", "8/7/1987", "User.One@gmail.com", "RandomPass"))

    print(newDB.add_user("UserTest2", "User Two", "Female", "22/2/1950", "User.Two@gmail.com", "RandomPass"))

    print(newDB.add_user("UserTest3", "User Three", "Male", "1/9/2010", "User.Three@gmail.com", "RandomPass"))


    # Testing the get_by_gender and get_by_age functions

    print(newDB.get_by_gender("Male"))

    print(newDB.get_by_age(11))








