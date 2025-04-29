from sql.db import create_connection
import questionary
from rich import print
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from app.menu import Menu  # for type hinting only
import datetime
from typing import cast, Sequence, Any


class SQLHandler:
    def __init__(self, menu: "Menu"):
        self.conn = create_connection()
        self.cursor = self.conn.cursor()

        # Attributes
        self._currentUserID = None
        self.menu = menu

    def _VerifyLoggedInUser(self):
        if self._currentUserID == None:
            print("author_ids action requries you to be logged in!")
            return False
        else:
            return True

    def UserAuth(self):
        # Will look up user
        # Will start login or sign up procedure

        username = input("Enter Username:")

        self.cursor.execute("SELECT * FROM Users WHERE Username = %s", (username,))
        user = self.cursor.fetchone()

        if user:
            self._UserLogin(username, user)
        else:
            self._UserReg(username, user)

    def _UserLogin(self, username, user):
        print(f"Welcome back, {username}!")
        self._currentUserID = user[0]

    def _UserReg(self, username, user):
        answer = input(f"{username} not found do you want to register y/n?")

        if answer.lower() == "y":
            # Do insert (Registration)
            email = input("enter email:")
            self.cursor.execute(
                "INSERT INTO Users (Username,Email) Values (%s,%s)", (username, email)
            )
            self.conn.commit()
            print(f"User {username} registered successfully!")
            self._currentUserID = user[0]

        else:
            print("Returning to main menu...")

    def AddBook(self):

        # TODO Verfiy user status
        if self._VerifyLoggedInUser() == False:
            return

        # Ask for book title
        bookTitle = input("What is the title of the book?")

        # _LookUpBook will ask the user to add info if it does not exist
        book = self._LookUpBook(bookTitle)

        # When the book is created/found

        # Ask user which list to add to
        selectedList = self._SelectReadingList()

        # Get userID
        userID = self._currentUserID

        # 6. Insert (user_id, book_id, status, NULL rating, NULL review, today's date) into UserBooks
        today = datetime.date.today()
        self.cursor.execute(
            "INSERT INTO UserBooks(UserID, BookID, status, rating, review, dateAdded) Values(%s, %s, %s, NULL, NULL, %s)",
            (userID, book, selectedList, today),
        )
        print(
            f'[orange3]Added to your "[italic dark_orange3]{selectedList}[/italic dark_orange3]" list[/orange3]'
        )

    def _LookUpBook(self, book):
        self.cursor.execute("SELECT * FROM Books WHERE title=%s", (book,))
        bookResult = self.cursor.fetchall()

        # if unique found great
        if len(bookResult) == 1:
            return bookResult[0][0]  # Return BookID
        elif len(bookResult) > 1:
            # TODO: Show options and let user pick
            # if multiple return all option
            pass
        else:
            # if none found start addingProcedure
            print(
                "[bold red]This book is not in the db, starting adding procedure[/bold red]"
            )
            self._addBookToDb(book)
            # search & return created book
            return self._LookUpBook(book)

    def _addBookToDb(self, bookTitle):
        author = input("Who is the author of the book?")
        pubYear = input("What is the publishing year?")
        genresList = self._SelectGenres()

        print(f"adding {bookTitle} by {author}, ({pubYear}) to database")

        # check if author exist
        # self.cursor.execute("SELECT * FROM Books WHERE title=%s", (book,))

        self.cursor.execute("SELECT AuthorID FROM Authors WHERE name=%s", (author,))
        authorResult = self.cursor.fetchone()

        # INSERTs
        # 1. insert author if needed

        if authorResult:
            authorID = authorResult[0]
        else:
            self.cursor.execute("INSERT INTO Authors (Name) Values(%s)", (author,))
            self.conn.commit()
            self.cursor.execute("SELECT LAST_INSERT_ID()")
            authorID = self.cursor.fetchone()[0]

        # 2. Insert the book
        self.cursor.execute(
            "INSERT INTO Books (title, AuthorID, publishedYear) VALUES (%s, %s, %s)",
            (bookTitle, authorID, pubYear),
        )
        self.conn.commit()

        # Get the newly inserted book's ID
        self.cursor.execute("SELECT LAST_INSERT_ID()")
        bookID = self.cursor.fetchone()[0]

        # 3. insert genres
        for genreName in genresList:
            self.cursor.execute(
                "SELECT genre_id FROM Genres WHERE genre_name=%s", (genreName,)
            )
            genreResult = self.cursor.fetchone()

            if genreResult:
                genreID = genreResult[0]
            else:
                self.cursor.execute(
                    "INSERT INTO Genres (genre_name) Values (%s)", (genreName,)
                )
                self.conn.commit()
                self.cursor.execute("SELECT LAST_INSERT_ID()")
                genreID = self.cursor.fetchone()[0]

            # Link genre to book
            self.cursor.execute(
                "INSERT INTO BookGenres (book_id,genre_id) Values(%s,%s)",
                (bookID, genreID),
            )
        self.conn.commit()
        print(f"Successfully added '{bookTitle}' with genres: {', '.join(genresList)}.")

    def _SelectGenres(self):
        # A multi line select of defined genres
        selectedGenres = []
        genres = [
            "Fantasy",
            "Science Fiction",
            "Romance",
            "Thriller",
            "Non-fiction",
            "Fiction",
        ]

        selectedGenres = questionary.checkbox(
            "Select the genres:", choices=genres
        ).ask()

        return selectedGenres

    def _SelectReadingList(self):
        selectedList = questionary.select(
            "Which booklist do you want to add the book to?",
            choices=[
                "Want to read",
                "Currently Reading",
                "Read",
            ],
        ).ask()
        return selectedList
