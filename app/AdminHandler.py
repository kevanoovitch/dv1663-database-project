from sql.db import create_connection
import questionary
from rich import print
from rich.progress import Progress
from datetime import datetime
import csv
import os
from dateutil import parser

MAX_AUTHOR_LENGTH = 150
TRUNCATE_NOTICE = " (more was truncated)"


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

    def ImportDataset(self):
        # Title,Authors,Description,Category,Publisher,Publish Date,Price

        # For storing known authors to avoid duplicate inserts
        # Author : Author ID
        addedAuthorIDs = {}

        file_path = questionary.text("Enter path to the dataset file:").ask()
        if not self._VerifyPath(file_path):
            return

        with open(file_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)

            rows = list(reader)
        # Wrap in a progress meter
        with Progress() as progress:
            task = progress.add_task("[cyan]Importing books...", total=len(rows))

            # map rows in source to a variable
            for row in rows:
                author = row["Authors"]
                title = row["Title"]
                yearPub = row["Publish Date"]
                genres = row["Category"]

                # Convert published date to only the year
                yearPub = self._ConvertDateToYear(yearPub)

                # insert author if not already existing
                authorID = self._AddAuthor(author, addedAuthorIDs)

                # insert book if it not already exists
                bookID = self._AddBook(title, authorID, yearPub)

                # Convert category to a acceptable genre?
                genreIDs = self._ConvertDsCategoriesToGenres(genres)
                # Genres is now a list of ids

                # Link Category to genre
                self._linkGenreToBook(genreIDs, bookID)

                progress.update(task, advance=1)

    def _VerifyPath(self, path):
        # Check if the path exists and is a file
        if not os.path.isfile(path):
            print("Error: Path does not exist or is not a file.")
            return False

        # Check if it ends with .csv (case-insensitive)
        if not path.lower().endswith(".csv"):
            print("Error: File is not a .csv file.")
            return False

        return True

    def _ConvertDateToYear(self, dateStr):
        try:
            datetimeObject = parser.parse(dateStr)
            return str(datetimeObject.year)
        except (ValueError, TypeError):
            return None

    def _AddAuthor(self, author, addedIDs):

        newAuthorID = 0
        # Check added authors
        if addedIDs.get(author) is not None:
            # This author already exists
            #
            newAuthorID = addedIDs[author]
            return newAuthorID
        else:
            # It does not already exist check db
            self.cursor.execute("SELECT * FROM Authors WHERE Name=%s", (author,))
            result = self.cursor.fetchone()
            if result:
                # found in db get the id
                newAuthorID = result[0]
                return newAuthorID
            else:
                # If the schema is too small
                if len(author) > MAX_AUTHOR_LENGTH:
                    print(
                        f"[WARN] Truncating overly long author name ({len(author)} chars)"
                    )
                    cutoff = MAX_AUTHOR_LENGTH - len(TRUNCATE_NOTICE)
                    truncated = author[:cutoff]
                    # Cut at last whitespace to avoid breaking a word
                    if " " in truncated:
                        truncated = truncated[: truncated.rfind(" ")]
                    author = truncated + TRUNCATE_NOTICE

                # not in db add it with a new id
                self.cursor.execute("INSERT INTO Authors (Name) Values (%s)", (author,))
                self.conn.commit()

                # Get the lastrowid
                newAuthorID = self.cursor.lastrowid

                # Update addedIDs
                addedIDs[author] = newAuthorID

                return newAuthorID

    def _AddBook(self, title, authorID, yearPub):

        # title + author = unique

        # Check if it exist in the db
        self.cursor.execute(
            "SELECT bookID FROM Books WHERE Title=%s and AuthorID = %s",
            (
                title,
                authorID,
            ),
        )
        result = self.cursor.fetchone()

        if result:
            # it exists
            thisBookID = result[0]
            return thisBookID
        else:
            # insert it
            self.cursor.execute(
                "INSERT INTO Books (Title,PublishedYear,AuthorID) Values (%s,%s,%s)",
                (title, yearPub, authorID),
            )
            self.conn.commit()
            # retrieve the bookdID
            thisBookID = self.cursor.lastrowid
            return thisBookID

    def _ConvertDsCategoriesToGenres(self, categories):
        genreIDs = []
        # split and then strip the categories
        categories = categories.split(",")
        cleanedCategories = [c.strip() for c in categories]

        # Loop thorugh and check each category
        for word in cleanedCategories:
            # Warns if schema is to small
            if len(word) > 55:
                print(f"[!] Genre name too long ({len(word)} chars): {word}")
                continue  # I dictate that all genres larger than 55 chars are not genres

            # Match it to a know genre in db

            self.cursor.execute(
                "SELECT GenreID FROM Genres WHERE LOWER(GenreName)=%s",
                (word.lower(),),
            )
            result = self.cursor.fetchone()
            if result:
                # there is a match
                genreIDs.append(result[0])

            else:
                # insert a new genre
                self.cursor.execute(
                    "INSERT INTO Genres (GenreName) Values (%s)", (word,)
                )
                self.conn.commit()
                genreIDs.append(self.cursor.lastrowid)

        return genreIDs

    def _linkGenreToBook(self, genreIDs, bookID):
        for id in genreIDs:
            # Check for duplicates
            self.cursor.execute(
                "SELECT * FROM BookGenres WHERE BookID = %s AND GenreID = %s",
                (
                    bookID,
                    id,
                ),
            )
            result = self.cursor.fetchone()
            if not result:
                self.cursor.execute(
                    "INSERT INTO BookGenres (BookID,GenreID) VALUES (%s,%s)",
                    (
                        bookID,
                        id,
                    ),
                )

        self.conn.commit()
        return

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
