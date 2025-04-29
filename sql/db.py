import mysql.connector


def create_connection():
    connection = mysql.connector.connect(
        host="localhost",  # or wherever your MySQL server is
        user="root",
        password="sql123",
        database="BookTracker",
    )
    return connection
