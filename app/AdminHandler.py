from sql.db import create_connection
import questionary
from rich import print


class AdminHandler:

    def __init__(self, menu: "Menu"):
        self.conn = create_connection()
        self.cursor = self.conn.cursor()

        # Attributes
        self._currentUserID = None
        self.menu = menu

    # ===========================================
    #            1. Import dataset
    # ===========================================

    # ===========================================
    #            2. List all users
    # ===========================================

    def AdminListAllUsers(self):
        self.cursor.execute("SELECT * FROM Users")

        allUsers = self.cursor.fetchall()

        for UserID, Username, Email, isAdmin in allUsers:
            if isAdmin:
                print(f"ID: {UserID} Username: {Username} Email: {Email} [ADMIN]")
            else:
                print(f"ID: {UserID} Username: {Username} Email: {Email} [USER]")

    # ===========================================
    #             Helper. Check for admin priviliges
    # ===========================================

    def CheckAdminPriv(self, UserID):
        self.cursor.execute("SELECT isAdmin FROM Users WHERE UserID=%s", (UserID,))
        result = self.cursor.fetchone()

        if result:
            # found the user

            if result[0] == True:
                # Found user and they had admin rights
                return True

            return False
        else:
            # did not find the userID
            return False
