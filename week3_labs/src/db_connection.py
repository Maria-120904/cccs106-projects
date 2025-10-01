import mysql.connector

def connect_db():
    """
    Return a mysql.connector connection object.
    Replace the password with your actual MySQL root password if needed.
    """
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="fletapp"
    )
