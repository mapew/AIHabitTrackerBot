import sqlite3

def ceate_sql_table():
    conn = sqlite3.connect('habit_tracker.db')
    cursor = conn.cursor()

    # Create Habits table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Habits (
        HabitID INTEGER PRIMARY KEY AUTOINCREMENT,
        HabitName TEXT NOT NULL,
        GoalType TEXT,
        StartDate TEXT,
        EndDate TEXT
    )
    ''')

    # Create HabitLogs table
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

    # Save and close
    conn.commit()
    conn.close()



def showall():
    conn = sqlite3.connect('habit_tracker.db')
    cursor = conn.cursor()

    # Fetch all habits
    cursor.execute("SELECT * FROM Habits")
    habits = cursor.fetchall()

    # Display habits
    for habit in habits:
        print(habit)

    cursor.execute("SELECT * FROM HabitLogs")
    logs = cursor.fetchall()

    for log in logs:
        print(log)

    conn.close()

ceate_sql_table()

#showall()
