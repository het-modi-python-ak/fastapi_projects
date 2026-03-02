from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import mysql.connector
from dotenv import load_dotenv,dotenv_values
import os

load_dotenv()





# Connect to the database
mydb = mysql.connector.connect(
    host=os.getenv("HOST"),
    user=os.getenv("USER1"),
    password=os.getenv("PASSWORD"),
    database=os.getenv("DATABASE")
)

# Create a cursor object
cursor = mydb.cursor()
print("hello")
app = FastAPI()

