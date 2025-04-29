from logging import PlaceHolder
from rich.console import Console
from rich.table import Table
from rich.style import Style
from app.sqlHandler import SQLHandler


class Menu:
    def __init__(self):
        self.console = Console()
        self.sqlHandler = SQLHandler(self)

    def ShowMainMenu(self):
        table = Table(title="BookTracker")
        table.add_column("Option", style="Cyan")
        table.add_column("Action", style="sky_blue3")
        table.add_row("1", "Login/Sign up a user")
        table.add_row("2", "Add a new book")
        table.add_row("3", "Rate a book")
        table.add_row("4", "View your reading list")
        table.add_row("5", "View average rating")

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
            else:
                print("Error in main menu input try again")


if __name__ == "__main__":
    menu = Menu()
    menu.UseMainMenu()
