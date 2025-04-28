from sql.db import create_connection
import questionary


class SQLHandler:
    def __init__(self):
        self.conn = create_connection()
        self.cursor = self.conn.cursor()

    def UserAuth(self):
        # Will look up user
        # Will start login or sign up procedure

        username = input("Enter Username:")

        self.cursor.execute("SELECT * FROM Users WHERE Username = %s", (username,))
        user = self.cursor.fetchone()

        if user:
            self._UserLogin(username)
        else:
            self._UserReg(username)

    def _UserLogin(self, username):
        print(f"Welcome back, {username}!")

    def _UserReg(self, username):
        answer = input(f"{username} not found do you want to register y/n?")

        if answer.lower() == "y":
            # Do insert (Registration)
            email = input("enter email:")
            self.cursor.execute(
                "INSERT INTO Users (Username,Email) Values (%s,%s)", (username, email)
            )
            self.conn.commit()
            print(f"User {username} registered successfully!")

        else:
            print("Returning to main menu...")

    def AddBook(self):

        # Ask for book title
        bookTitle = input("What is the title of the book?")

        # Will look for the book in the table
        # _LookUpBook will ask the user to add info if it does not exist
        book = _LookUpBook(self, bookTitle)

        # When the book is created/found

        # Ask user which list to add to


        # If selected list doesnt exist add it

    def _LookUpBook(self, book):
        self.cursor.execute("SELECT * FROM Books WHERE title=%s", (book,))
        bookResult = self.cursor.fetchall()

        # if unique found great
        if len(bookResult) == 1:
            return bookResult[0]
        elif len(bookResult) > 1:
            # TODO: Show options and let user pick
            # if multiple return all option
            pass
        else:
            # if none found start addingProcedure
            self._addBookToDb(book)
            # search & return created book
            return self._LookUpBook(book)

    def _addBookToDb(self, bookTitle):
        author = input("Who is the author of the book?")
        pubYear = input("What is the publishing year?")
        genres = self._SelectGenres()

        print(f"adding {bookTitle} by {author}, ({pubYear}) to database")

        # check if author exist
        # self.cursor.execute("SELECT * FROM Books WHERE title=%s", (book,))

        self.cursor.execute("SELECT author_id FROM Authors WHERE name=%s", (author,))
        authorResult = self.cursor.fetchone()

        # INSERTs
        # 1. insert author if needed

        if authorResult:
            authorID = authorResult[0]
        else:
            self.cursor.execute("INSERT INTO Authors (name) Values(%s)", (author))
            self.conn.commit()
            self.cursor.execute("SELECT LAST_INSERT_ID()")
            authorID = self.cursor.fetchone()[0]

        # 2. Insert the book
        self.cursor.execute(
            "INSERT INTO Books (title, author_id, published_year) VALUES (%s, %s, %s)"
            (bookTitle, author, pubYear),
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
                "INSERT INTO BookGenres (book_id,genre_id) Values(%s,%s)", (bookID, genreID)
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

        print(f"You selected: {', '.join(selectedGenres)}")

        return selectedGenres
    
    def _SelectReadingList(self):
        selectedList= questionary.select(
            "Which booklist do you want to add the book to?"
            choices=[
                ("Want to read","wantToRead"),
                ("Currently Reading", "currentlyReading"),
                ("Read","Read")
            ]).ask()
        return selectedList
