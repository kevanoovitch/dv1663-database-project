from logging import PlaceHolder
from rich.console import Console
from rich.table import Table
from rich.style import Style
from app.sqlHandler import SQLHandler
from app.AdminHandler import AdminHandler


class Menu:
    def __init__(self):
        self.console = Console()
        self.sqlHandler = SQLHandler(self)
        self.AdminHandler = AdminHandler(self)

        self._currentUserID = None

    def getCurrentUser(self):
        return self.sqlHandler._currentUserID

    def ShowMainMenu(self):
        table = Table(title="BookTracker")
        table.add_column("Option", style="Cyan")
        table.add_column("Action", style="sky_blue3")
        table.add_row("1", "Login/Sign up a user")
        table.add_row("2", "Add a new book")
        table.add_row("3", "Rate a book")
        table.add_row("4", "View your reading list")
        table.add_row("5", "View average rating")
        table.add_row("6", "View Admin options")
        table.add_row("7", "Exit")

        self.console.print(table)

    def UseMainMenu(self):

        while True:
            self.ShowMainMenu()
            userInput = self.console.input()  # get the input

            if userInput == "1":
                self.sqlHandler.UserAuth()
            elif userInput == "2":
                self.sqlHandler.AddBook()
            elif userInput == "3":
                print("[PlaceHolder] Rate a book")
            elif userInput == "4":
                self.sqlHandler.ViewUserList()
            elif userInput == "5":
                print("[PlaceHolder] View average rating")
            elif userInput == "6":
                if self._VerifyAdmin():
                    self._UseAdminMenu()
            elif userInput == "7":
                print("Exiting")
                return
            else:
                print("Error in main menu input try again")

    def ShowAdminMenu(self):

        # Verify admin user

        table = Table(title="Admin options")
        table.add_column("Option", style="Cyan")
        table.add_column("Action", style="sky_blue3")
        table.add_row("1", "Import Dataset")
        table.add_row("2", "View all users")
        table.add_row("3", "return to main menu")

        self.console.print(table)

    def _UseAdminMenu(self):

        while True:
            self.ShowAdminMenu()
            userInput = self.console.input()  # get the input
            if userInput == "1":
                print("[PlaceHolder] for inport of dataset")
            elif userInput == "2":
                self.AdminHandler.AdminListAllUsers()
            elif userInput == "3":
                print("Returning to main menu")
                return
            else:
                print("Error in admin menu input try again")

    def _VerifyAdmin(self):

        self._currentUserID = self.getCurrentUser()

        # if getCurrentUser = none
        if self._currentUserID == None:
            print("You will have to be a logged in to view this")
            return False

        # check userID in db for admin priv
        result = self.AdminHandler.CheckAdminPriv(self._currentUserID)
        if result:
            # They are an admin
            return True

        print("Access denied")
        return False


if __name__ == "__main__":
    menu = Menu()
    menu.UseMainMenu()
