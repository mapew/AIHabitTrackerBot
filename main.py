import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import sqlite3
from datetime import date
from datetime import datetime

#this function (create_sql_table) is remove from the system due to token useage if need it. Add it to tools list
#and add "- ask user if user want to create table if table is not exit" to instruct.md prompt if want to use this function
def create_sql_table() -> None:
    """
    Check whether the SQL table exists.  
    If it does not, this function will create the table after prompting the user for confirmation.
    """
    try:
        conn = sqlite3.connect('habit_tracker.db')
        cursor = conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Habits (
            HabitID INTEGER PRIMARY KEY AUTOINCREMENT,
            HabitName TEXT NOT NULL,
            GoalType TEXT,
            StartDate TEXT,
            EndDate TEXT
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS HabitLogs (
            LogID INTEGER PRIMARY KEY AUTOINCREMENT,
            HabitID INTEGER,
            Date TEXT,
            Completed BOOLEAN,
            Notes TEXT,
            FOREIGN KEY (HabitID) REFERENCES Habits(HabitID)
        )
        ''')

        conn.commit()
        print("Table Created successfully!")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

def get_todays_date() -> str:
    """
    Get today's date. uses this function when today date information is needed.

    Returns:
        str: A string representing today's date and the full name of the weekday.
    """
    return str(date.today()) + "\n" + str(datetime.today().strftime("%A")
)

def create_habit_tracker(HabitName: str,GoalType: str,StartDate:str, EndDate:str) -> str:
    """
    Create a habit tracker using SQLite3.

    This function allows the user to set and track goals such as drinking water, exercising, or reading.

    Args:
        HabitName (str): The name of the habit to track (e.g., "Read a book", "Drink water", "Exercise").
        GoalType (str): The frequency of the habit (e.g., "Daily", "Weekly", "Monthly", "Every Monday").
        StartDate (str): The date tracking begins (formatted as "YYYY-MM-DD").
        EndDate (str): The date tracking ends. Can be None when the habit is first created.

    Returns:
        str: Success message if the habit is created, or an error message if creation fails.
    """
    habit_data = (HabitName, GoalType, StartDate, EndDate)

    try:  
        conn = sqlite3.connect('habit_tracker.db')
        cursor = conn.cursor()

        cursor.execute('''
        INSERT INTO Habits (HabitName, GoalType, StartDate, EndDate)
        VALUES (?, ?, ?, ?)
        ''', habit_data)

        conn.commit()
        ESmessage = "task successfully created"
    except sqlite3.Error as e:
        ESmessage = f"An error occurred: {e}"
    finally:
        if conn:
            conn.close()

    return ESmessage

def find_habit_id_in_table() -> list:
    """
        Displays HabitID and HabitName

        Returns:
            list: A list of records, each ordered as (TaskID, TaskName, duration, Frequency, StartDate, IsActive).
    """

    conn = sqlite3.connect('habit_tracker.db')
    cursor = conn.cursor()

    cursor.execute("SELECT HabitID, HabitName FROM Habits")
    habits = cursor.fetchall()
    
    conn.close()
    return habits

def update_habit_tracker(HabitID:int,Date: str,Completed: str,Notes:str) -> str:
    """
    Update a specific field in the habit tracker while preserving other values.

    Args:
        HabitID (int): The ID of the task to update.
        Date (str) Date completed
        Completed(boolen): completed Habit True or False
        Notes (str, optional) any Notes user want to write

    Return:
        message (str): it will return error message or successfully update message
    """
    themessage = "could not update it"
    try:
        conn = sqlite3.connect('habit_tracker.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM HabitLogs")
        row = cursor.fetchall()

        updated_values = (HabitID,Date,Completed,Notes)

        cursor.execute('''
        INSERT INTO HabitLogs (HabitID, Date, Completed, Notes)
        VALUES (?, ?, ?, ?)
        ''', updated_values)
        
        conn.commit()
        themessage = f"Task {HabitID} updated successfully."

    except sqlite3.Error as e:
        errorM = f"An error occurred: {e}"
        return errorM
    finally:
        conn.close()
        return themessage


def show_habit_table() -> list:
    """
        Displays all data from the hablt list. This table have HabitID (PK),HabitName,GoalType,StartDate,EndDate

        Returns:
            list: A list of records, each ordered as (HabitID,HabitName,GoalType,StartDate,EndDate).
        
    """

    conn = sqlite3.connect('habit_tracker.db')  
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Habits")
    habits = cursor.fetchall()

    conn.close()

    return habits

def show_habit_log_table() -> list:
    """
        Displays all data from the hablt list. This table have LogID,HabitID(FK),Date,Completed,Note

        Returns:
            list: A list of records, each ordered as (LogID,HabitID,Date,Completed,Note).
        
    """
    conn = sqlite3.connect('habit_tracker.db')
    cursor  = conn.cursor()

    cursor.execute("SELECT * FROM HabitLogs")
    habits_list = cursor.fetchall()

    conn.close()
    
    return habits_list

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

try:
    with open("instruct.md","r",encoding='utf-8') as file:
        instruction = file.read().strip()
except FileNotFoundError:
    print("Warning: instruct.md not found. Using empty system instruction.")
    instruction = ""

tools = [get_todays_date,
         create_habit_tracker,
         show_habit_log_table,
         show_habit_table,
         update_habit_tracker
        ]

if api_key:
    if "chat_session" not in st.session_state:
        client = genai.Client(api_key=api_key)
        st.session_state.chat_session = client.chats.create(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                system_instruction=instruction,
                tools = tools
            )
        )

st.title("Hello, I am AI Habit Tracker Bot")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.chat_input("Say something")

if user_input:
    st.session_state.chat_history.append({"role": "user","content": user_input})
    try:
        response = st.session_state.chat_session.send_message(user_input)
        response_text = response.text
    except Exception as e:
        response_text = f"Error: {e}\n"

    st.session_state.chat_history.append({"role": "assistant","content": response_text})

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
