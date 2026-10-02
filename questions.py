import sqlite3
import pandas as pd

# Excel file read
df = pd.read_excel("AI_Career_Compass_100_MCQs.xlsx")

# SQLite database connect
connection = sqlite3.connect("career_compass.db")

cursor = connection.cursor()

# Create questions table
cursor.execute("""
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id TEXT,
    question TEXT,
    option_a TEXT,
    option_b TEXT,
    option_c TEXT,
    option_d TEXT,
    a_category TEXT,
    b_category TEXT,
    c_category TEXT,
    d_category TEXT
)
""")

# Insert questions
for _, row in df.iterrows():

    cursor.execute("""
    INSERT INTO questions (
        question_id,
        question,
        option_a,
        option_b,
        option_c,
        option_d,
        a_category,
        b_category,
        c_category,
        d_category
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        row["Question_ID"],
        row["Question"],
        row["Option_A"],
        row["Option_B"],
        row["Option_C"],
        row["Option_D"],
        row["A_Category"],
        row["B_Category"],
        row["C_Category"],
        row["D_Category"]
    ))

connection.commit()
connection.close()

print("100 MCQs successfully stored in SQLite!")