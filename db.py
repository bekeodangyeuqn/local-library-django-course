# importing required libraries
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

dataBase = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    passwd=os.getenv("DB_USER_PASSWORD")
)

# preparing a cursor object
cursorObject = dataBase.cursor()

# creating database
cursorObject.execute("CREATE DATABASE locallibrary")
