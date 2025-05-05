from sql.db import create_connection
import questionary
from rich import print
from datetime import datetime


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
        definedGenres = [
            "Fantasy",
            "Science Fiction",
            "Romance",
            "Thriller",
            "Non-fiction",
            "Fiction",
        ]
        # Title,Authors,Description,Category,Publisher,Publish Date,Price

        # For storing known authors to avoid duplicate inserts
        # Author : Author ID
        addedAuthorIDs = {}

        with open("kaggle_books.csv", newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            # map rows in source to a variable
            for row in reader:
                author = row["Authors"]
                title = row["Title"]
                yearPub = row["Publish Date"]
                genres = row["Category"]

                # Convert published date to only the year
                yearPub = self._ConvertDateToYear(yearPub)

                # insert author if not already existing
                authorID = self._AddAuthor(author, addedAuthorIDs)

                # insert book if it not already exists
                self._AddBook(title, authorID, yearPub)

                # Convert category to a acceptable genre?
                # Link Category to genre

    def _ConvertDateToYear(self, dateStr):
        try:
            datetimeObject = datetime.strptime(dateStr, "%A, %B %d, %Y")
            YearStr = str(datetimeObject.year)
            return YearStr
        except ValueError:
            return None

    def _AddAuthor(self, author, addedIDs):

        newAuthorID = 0
        # Check added authors
        if addedIDs.get(author) is not None:
            # This author already exists
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
