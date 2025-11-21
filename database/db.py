import mysql.connector
from config import DATABASE

def get_connection():
    return mysql.connector.connect(**DATABASE)