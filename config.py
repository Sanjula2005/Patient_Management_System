import MySQLdb

def get_db_connection():
    return MySQLdb.connect(
        host="localhost",
        user="root",
        passwd="root123",      # your MySQL root password
        db="x",
        charset='utf8mb4'
    )
