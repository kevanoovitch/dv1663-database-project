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
