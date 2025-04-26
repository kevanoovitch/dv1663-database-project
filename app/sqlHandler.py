from sql.db import create_connection


class SQLHandler:
    def __init__(self):
        self.conn = create_connection()
        self.cursor = self.conn.cursor()

    def UserAuth(self):
        # Will look up user
        # Will start login or sign up procedure

        username = input("Enter Username:")

        self.cursor.execute("SELECT * FROM Users WHERE Username = ?", (username))
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
                "INSERT INTO Users (Username,Email) Values (?,?)", (username, email)
            )
            self.conn.commit()
            print(f"User {username} registered successfully!")

        else:
            print("Returning to main menu...")
