from sql.db import create_connection
import questionary
from rich import print
from rich.table import Table
from rich.console import Console
from typing import TYPE_CHECKING
from app.AdminHandler import AdminHandler


if TYPE_CHECKING:
    from menu import Menu  # for type hinting only

import datetime
from typing import cast, Sequence, Any


class SQLHandler:
    def __init__(self, menu: "Menu"):
        self.conn = create_connection()
        self.cursor = self.conn.cursor()
        self.admin_handler = AdminHandler(menu, self.conn)

        self.console = Console()

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
        self.console.clear()
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
        self.console.clear()

        if self._VerifyLoggedInUser() == False:
            return

        # Ask for book title
        bookTitle = input("What is the title of the book?")

        # _LookUpBook will ask the user to add info if it does not exist
        bookID = self._LookUpBook(bookTitle)
        if bookID == None:
            # The book was not found so add it
            console = Console()
            console.print(
                "This book is not in the db, do you want to start the adding procedure? y/n",
                style="bold red",
            )
            answer = input()

            if answer.lower() == "n":
                return None

            bookID = self._addBookToDb(bookTitle)

        # When the book is created/found

        # Ask user which list to add to
        selectedList = self._SelectReadingList()

        # Get userID
        userID = self._currentUserID

        # 6. Insert (user_id, book_id, status, NULL rating, NULL review, today's date) into UserBooks
        today = datetime.date.today()
        self.cursor.execute(
            "INSERT INTO UserBooks(UserID, BookID, status, rating, review, dateAdded) Values(%s, %s, %s, NULL, NULL, %s)",
            (userID, bookID, selectedList, today),
        )
        print(
            f'[orange3]Added to your "[italic dark_orange3]{selectedList}[/italic dark_orange3]" list[/orange3]'
        )

    def _LookUpBook(self, book):
        """
        Will return the bookID or None
        """
        self.cursor.execute(
            "SELECT * FROM Books WHERE LOWER(title) = LOWER(%s)", (book,)
        )
        bookResult = self.cursor.fetchall()

        # if unique found great
        if len(bookResult) == 1:
            return bookResult[0][0]  # Return BookID
        elif len(bookResult) > 1:
            print("[yellow]Multiple books found with similar titles:[/yellow]")
            for idx, row in enumerate(bookResult):
                book_id, title, year, *_ = row
                print(f"{idx + 1}. {title} ({year}) - ID: {book_id}")
            choice = input(
                "Enter the number of the correct book (or press Enter to cancel): "
            )
            if choice.isdigit():
                choice_index = int(choice) - 1
                if 0 <= choice_index < len(bookResult):
                    return bookResult[choice_index][0]  # BookID       else:
            print("[red]Cancelled selection.[/red]")

        # else  Not found
        return None

    def _addBookToDb(self, bookTitle):
        rawAuthors = input("Who is the author (or authors, separated by 'and')?")
        pubYear = input("What is the publishing year?")
        genresList = self._SelectGenres()

        # parse authors
        authors = self.admin_handler.ParseAuthors(rawAuthors)

        print(f"adding {bookTitle} by {', '.join(authors)}, ({pubYear}) to database")

        # Insert book
        self.cursor.execute(
            "INSERT INTO Books (Title,publishedYear) VALUES (%s,%s)",
            (bookTitle, pubYear),
        )
        self.conn.commit()

        self.cursor.execute("SELECT LAST_INSERT_ID()")
        bookID = self.cursor.fetchone()[0]

        # Add authors and link to book

        for author in authors:
            self.cursor.execute(
                "SELECT AuthorID FROM Authors WHERE Name = %s", (author,)
            )
            result = self.cursor.fetchone()

            if result:
                authorID = result[0]
            else:
                self.cursor.execute("INSERT INTO Authors (Name) VALUES (%s)", (author,))
                self.conn.commit()
                self.cursor.execute("SELECT LAST_INSERT_ID()")
                authorID = self.cursor.fetchone()[0]

            self.cursor.execute(
                "INSERT INTO BookAuthors (BookID, AuthorID) VALUES (%s,%s)",
                (bookID, authorID),
            )

        # Insertt genres and link to book
        for genreName in genresList:
            self.cursor.execute(
                "SELECT GenreID FROM Genres WHERE LOWER(GenreName)=LOWER(%s)",
                (genreName,),
            )
            genreResult = self.cursor.fetchone()

            if genreResult:
                genreID = genreResult[0]
            else:
                self.cursor.execute(
                    "INSERT INTO Genres (GenreName) Values (%s)", (genreName,)
                )
                self.conn.commit()
                self.cursor.execute("SELECT LAST_INSERT_ID()")
                genreID = self.cursor.fetchone()[0]

            # Link Genre to book
            self.cursor.execute(
                "INSERT INTO BookGenres (BookID,GenreID) Values(%s,%s)",
                (bookID, genreID),
            )

        self.conn.commit()
        print(f"Successfully added '{bookTitle}' with genres: {', '.join(genresList)}.")

        return bookID

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
            "Select the genres: \n <space> to select then enter", choices=genres
        ).ask()

        if not selectedGenres:
            print(
                "[bold red]You did not select anything! Press <space> to select and then Enter.[/bold red]"
            )
            self._SelectGenres()

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
        self.console.clear()
        # Verify login
        if self._VerifyLoggedInUser() == False:
            return
        # Select list
        selectedList = self._SelectReadingList()

        # Print the list
        self.cursor.execute(
            """
            SELECT 
                b.Title,
                GROUP_CONCAT(DISTINCT a.Name SEPARATOR ', ') AS Authors,
                b.PublishedYear,
                ub.rating
            FROM UserBooks ub
            JOIN Books b ON ub.BookID = b.BookID
            JOIN BookAuthors ba ON b.BookID = ba.BookID
            JOIN Authors a ON ba.AuthorID = a.AuthorID
            WHERE ub.UserID = %s AND ub.status = %s
            GROUP BY b.BookID, b.Title, b.PublishedYear, ub.rating                        
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
        self.console.clear()
        # Verify that the user is logged in
        if self._VerifyLoggedInUser() == False:
            return

        bookTitle = input("What is the title of the book?")

        book = self._LookUpBook(bookTitle)
        if book == None:
            # The book was not found and the function canceled
            print("Didn't find the book in db check spelling or add it")
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
    #            5. Average Rating of a book
    # ===========================================

    def ViewAvreageRating(self):
        self.console.clear()

        # Look up the book and get the bookID
        bookTitle = input("What is the title of the book?")

        bookID = self._LookUpBook(bookTitle)

        if bookID == None:
            print("[bold red]Could not find the book returning to main menu[/bold red]")
            return

        # Call the sql function
        self.cursor.execute("SELECT ReturnAvgRating(%s)", (bookID,))
        result = self.cursor.fetchone()

        avgRating = result[0]

        if avgRating is None:
            print("[bold yellow] No rating yet for this book.[/book yellow]")
        else:
            print(f"[green] Avreage rating:[/green] {avgRating:.2f}")

    # ================================================
    #            7. List a usersbooks based on genre
    # ================================================

    def ListBasedOnGenre(self):
        self.console.clear()
        # Verify login
        if self._VerifyLoggedInUser() == False:
            return

        # ask for genre
        genre = input("What is the genre?")

        self.cursor.execute(
            """
            SELECT
            b.Title,
            ub.rating,
            ub.status,
            ub.review,
            ub.dateAdded

            FROM Users u 
            JOIN UserBooks ub ON u.UserID = ub.UserID
            JOIN Books b ON ub.bookID = b.BookID
            JOIN BookGenres bg ON b.BookID = bg.BookID
            JOIN Genres g ON bg.GenreID = g.GenreID 
            WHERE u.UserID = %s AND LOWER(g.GenreName) = LOWER(%s)
            ORDER BY ub.dateAdded DESC; 
            """,
            (self._currentUserID, genre),
        )

        rows = self.cursor.fetchall()
        if not rows:
            print(f"[yellow] No books found in genre '{genre}' for user")
            return

        for row in rows:
            title, rating, status, review, dateAdded = row

            if rating is None:
                stars = "[dim]Not rated[/dim]"
            else:
                stars = "⭐" * rating

            print(
                f"\n{title}\nRating: {stars}\nStatus: {status}\nReview: {review or 'None'}\nAdded: {dateAdded}"
            )

    # ===============================================================
    #            8. View all users that have a specifc book on a list
    # ===============================================================
    def GetUserWithCommonBook(self):
        self.console.clear()
        # Verify login
        if self._VerifyLoggedInUser() == False:
            return

        # ask for book
        book = input("What is the book title?")
        bookID = self._LookUpBook(book)

        self.cursor.execute(
            """
            SELECT u.Username, ub.status
            FROM Users u
            JOIN UserBooks ub ON u.UserID = ub.UserID
            JOIN Books b ON ub.BookID = b.BookID
            WHERE b.bookID = %s;
            """,
            (bookID,),
        )
        rows = self.cursor.fetchall()

        console = Console()
        table = Table(title="Users with This Book")

        table.add_column("Username", style="cyan", no_wrap=True)
        table.add_column("Status", style="magenta")

        for username, status in rows:
            table.add_row(username, status.capitalize())

        console.print(table)

    # ===============================================================
    #            9. View how many books the current user has read
    # ===============================================================

    def CountReadBooks(self):
        self.console.clear()

        self.cursor.execute(
            """
                SELECT COUNT(*) AS ReadCount
                 FROM UserBooks
                WHERE UserID = %s AND status = 'Read';
            """,
            (self._currentUserID,),
        )
        result = self.cursor.fetchone()

        if result == None or result[0] == 0:
            self.console.print("[bold red]You have not read any books.[/bold red]")
            return

        readCount = result[0]
        self.console.print(
            f"[green]You have read[/green] [bold cyan]{readCount}[/bold cyan] [green]books.[/green]"
        )
