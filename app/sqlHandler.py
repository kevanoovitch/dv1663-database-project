from sql.db import create_connection
import questionary
from rich import print
from rich.console import Console
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from menu import Menu  # for type hinting only
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
            print("[bold red]That action requries you to be logged in![/bold red]")
            return False
        else:
            return True

    # ===========================================
    #            1. USER AUTHENTICATION
    # ===========================================

    def UserAuth(self):
        # Will look up user
        # Will start login or sign up procedure

        username = input("Enter Username:")

        self.cursor.execute("SELECT * FROM Users WHERE Username = %s", (username,))
        user = self.cursor.fetchone()

        # if this is first user make it an admin
        self.cursor.execute("SELECT COUNT(*) FROM Users")
        user_count = self.cursor.fetchone()[0]

        if user_count == 0:
            # This is the first user so create an admin
            print("You are the first user so this has to be an admin")
            self._AdminReg(username, user)
            return

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
            self.cursor.execute(
                "SELECT UserID FROM Users WHERE Username = %s", (username,)
            )
            result = self.cursor.fetchone()
            if result:
                self._currentUserID = result[0]

        else:
            print("Returning to main menu...")

    def _AdminReg(self, username, user):
        print("Starting Admin registration procedure")

        email = input("Enter Email:")
        self.cursor.execute(
            "INSERT INTO Users (Username,Email,isAdmin) Values (%s,%s, %s)",
            (username, email, True),
        )

        self.conn.commit()
        print(f"Admin user '{username}' registered successfully.")

    # ===========================================
    #           2. Add book to list and db
    # ===========================================

    def AddBook(self):

        if self._VerifyLoggedInUser() == False:
            return

        # Ask for book title
        bookTitle = input("What is the title of the book?")

        # _LookUpBook will ask the user to add info if it does not exist
        book = self._LookUpBook(bookTitle)
        if book == None:
            # The book was not found and the function cancelled
            return

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
        """
        Will return the bookID or None
        """
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
            console = Console()
            console.print(
                "This book is not in the db, do you want to start the adding procedure? y/n",
                style="bold red",
            )
            answer = input()

            if answer.lower() == "n":
                return None

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

    # ===========================================
    #            3. Show users lists
    # ===========================================

    def ViewUserList(self):
        # Verify login
        if self._VerifyLoggedInUser() == False:
            return
        # Select list
        selectedList = self._SelectReadingList()

        # Print the list
        self.cursor.execute(
            """
                            SELECT title, Authors.Name, Books.publishedYear, rating
                            FROM UserBooks 
                            JOIN Books ON UserBooks.BookID = Books.BookID
                            JOIN Authors ON Books.AuthorID = Authors.AuthorID
                            WHERE UserBooks.UserID = %s AND UserBooks.status = %s
                        """,
            (self._currentUserID, selectedList),
        )

        books = self.cursor.fetchall()

        if not books:
            print(
                f"[bold red] No books found in your '{selectedList}' list.[/bold red]"
            )
            return

        print(f"[bold green] Books in your '{selectedList}' list:[/bold green]")

        for title, author, year, rating in books:
            if selectedList == "Read":
                stars = "⭐" * rating if rating is not None else "Not rated"
                print(f"- {title} by {author} ({year}) - Rating: {stars}")
            else:
                print(f"- {title} by {author} ({year})")

    # ===========================================
    #            4. Rate a book
    # ===========================================

    def RateBook(self):
        # Verify that the user is logged in
        if self._VerifyLoggedInUser() == False:
            return

        bookTitle = input("What is the title of the book?")

        # _LookUpBook will ask the user to add info if it does not exist
        book = self._LookUpBook(bookTitle)
        if book == None:
            # The book was not found and the function cancelled
            return

        # input rating
        userRating = self._PickRating()

        # use a sql proocedure to check that the book is in read else add it add the rating
        review = "placeholder review"
        bookID = book
        self.cursor.callproc(
            "RateBookProcedure", (self._currentUserID, bookID, userRating, review)
        )
        self.conn.commit()

    def _PickRating(self):
        userRating = questionary.select(
            "What do you rate the book",
            choices=[
                "☆",
                "☆☆",
                "☆☆☆",
                "☆☆☆☆",
                "☆☆☆☆☆",
            ],
        ).ask()

        return len(userRating)

    # ===========================================
    #            5. Avreage Rating of a book
    # ===========================================


def ViewAvreageRating(self):
    return
