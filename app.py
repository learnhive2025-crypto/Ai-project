from flask import Flask, render_template, request
import sqlite3
import random
import pandas as pd
import joblib
import os

app = Flask(__name__)

DATABASE = "career_compass.db"
MODEL_FILE = "career_model.pkl"
EXCEL_FILE = "career_ml_dataset.xlsx"


# =========================================================
# LOAD ML MODEL
# =========================================================

model = joblib.load(MODEL_FILE)


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db_connection():

    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    return connection


# =========================================================
# CREATE DATABASE TABLES
# =========================================================

def create_tables():

    connection = get_db_connection()

    # -----------------------------------------
    # Student individual answers
    # -----------------------------------------

    connection.execute("""
        CREATE TABLE IF NOT EXISTS student_responses (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            student_id TEXT,

            question_id TEXT,

            selected_option TEXT,

            category TEXT,

            score INTEGER

        )
    """)


    # -----------------------------------------
    # Student ML Dataset
    # -----------------------------------------

    connection.execute("""
        CREATE TABLE IF NOT EXISTS career_ml_data (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            student_id TEXT UNIQUE,

            CS INTEGER DEFAULT 0,

            ENG INTEGER DEFAULT 0,

            BIO INTEGER DEFAULT 0,

            BT INTEGER DEFAULT 0,

            COM INTEGER DEFAULT 0,

            ART INTEGER DEFAULT 0,

            MED INTEGER DEFAULT 0,

            DES INTEGER DEFAULT 0,

            Career TEXT

        )
    """)


    connection.commit()

    connection.close()


# =========================================================
# SAVE STUDENT ML DATA
# =========================================================

def save_ml_student(student_id, scores):

    connection = get_db_connection()


    # Highest score category
    career = max(
        scores,
        key=scores.get
    )


    connection.execute("""
        INSERT OR REPLACE INTO career_ml_data
        (
            student_id,
            CS,
            ENG,
            BIO,
            BT,
            COM,
            ART,
            MED,
            DES,
            Career
        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

    """,
    (
        student_id,

        scores["CS"],
        scores["ENG"],
        scores["BIO"],
        scores["BT"],
        scores["COM"],
        scores["ART"],
        scores["MED"],
        scores["DES"],

        career
    ))


    connection.commit()

    connection.close()


    print()
    print("===================================")
    print("ML DATA SAVED")
    print("===================================")
    print("Student ID :", student_id)
    print("Career     :", career)


# =========================================================
# EXPORT SQL DATA → EXCEL
# =========================================================

def export_ml_dataset():

    connection = get_db_connection()


    data = connection.execute("""
        SELECT

            student_id AS Student_ID,

            CS,
            ENG,
            BIO,
            BT,
            COM,
            ART,
            MED,
            DES,

            Career

        FROM career_ml_data

        ORDER BY id

    """).fetchall()


    connection.close()


    # Convert SQLite rows
    rows = [
        dict(row)
        for row in data
    ]


    # Create DataFrame
    df = pd.DataFrame(rows)


    # If no students
    if df.empty:

        print("No ML data available.")

        return


    # Temporary Excel file
    temp_file = "career_ml_dataset_temp.xlsx"


    try:

        # -------------------------------------
        # Create temporary Excel
        # -------------------------------------

        df.to_excel(
            temp_file,
            index=False
        )


        # -------------------------------------
        # Replace existing Excel
        # -------------------------------------

        if os.path.exists(EXCEL_FILE):

            try:

                os.replace(
                    temp_file,
                    EXCEL_FILE
                )

                print()
                print("Excel updated successfully!")

            except PermissionError:

                print()
                print("===================================")
                print("WARNING")
                print("===================================")

                print(
                    "career_ml_dataset.xlsx is open."
                )

                print(
                    "Close Excel to update the file."
                )

                # SQL data is already safe


                if os.path.exists(temp_file):

                    os.remove(temp_file)


        else:

            os.rename(
                temp_file,
                EXCEL_FILE
            )

            print()
            print("Excel created successfully!")


    except Exception as error:

        print()
        print("Excel Error:")
        print(error)


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =========================================================
# QUIZ PAGE
# =========================================================

@app.route("/quiz")
def quiz():

    connection = get_db_connection()


    questions = connection.execute("""
        SELECT *
        FROM questions
    """).fetchall()


    connection.close()


    # -------------------------------------
    # Need at least 15 questions
    # -------------------------------------

    if len(questions) < 15:

        return "Minimum 15 questions required."


    # -------------------------------------
    # Select random 15
    # -------------------------------------

    selected_questions = random.sample(
        questions,
        15
    )


    return render_template(

        "quiz.html",

        questions=selected_questions

    )


# =========================================================
# SUBMIT QUIZ
# =========================================================

@app.route(
    "/submit",
    methods=["POST"]
)
def submit():


    # =====================================================
    # 1. STUDENT ID
    # =====================================================

    student_id = request.form.get(
        "student_id"
    )


    if not student_id:

        student_id = "STUDENT001"


    # Remove spaces
    student_id = student_id.strip()


    print()
    print("===================================")
    print("QUIZ SUBMITTED")
    print("===================================")
    print("Student ID:", student_id)



    career_scores = {

        "CS": 0,

        "ENG": 0,

        "BIO": 0,

        "BT": 0,

        "COM": 0,

        "ART": 0,

        "MED": 0,

        "DES": 0

    }



    connection = get_db_connection()




    connection.execute("""
        CREATE TABLE IF NOT EXISTS student_responses (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            student_id TEXT,

            question_id TEXT,

            selected_option TEXT,

            category TEXT,

            score INTEGER

        )
    """)



    for question_id, answer in request.form.items():


        # Skip Student ID
        if question_id == "student_id":

            continue


        question = connection.execute("""

            SELECT *

            FROM questions

            WHERE question_id = ?

        """,
        (question_id,)).fetchone()


        if question is None:

            continue


        if answer == "A":

            category = question["a_category"]


        elif answer == "B":

            category = question["b_category"]


        elif answer == "C":

            category = question["c_category"]


        elif answer == "D":

            category = question["d_category"]


        else:

            continue


        score = 3



        if category in career_scores:

            career_scores[category] += score



        connection.execute("""

            INSERT INTO student_responses

            (
                student_id,
                question_id,
                selected_option,
                category,
                score
            )

            VALUES (?, ?, ?, ?, ?)

        """,
        (
            student_id,
            question_id,
            answer,
            category,
            score
        ))



    connection.commit()

    connection.close()



    save_ml_student(

        student_id,

        career_scores

    )



    export_ml_dataset()



    student_data = pd.DataFrame([{

        "CS":
        career_scores["CS"],

        "ENG":
        career_scores["ENG"],

        "BIO":
        career_scores["BIO"],

        "BT":
        career_scores["BT"],

        "COM":
        career_scores["COM"],

        "ART":
        career_scores["ART"],

        "MED":
        career_scores["MED"],

        "DES":
        career_scores["DES"]

    }])


    print(student_data)


    prediction = model.predict(

        student_data

    )


    predicted_category = prediction[0]

    career_names = {

        "CS":
        "Computer Science / AI",

        "ENG":
        "Engineering",

        "BIO":
        "Biology / Medicine",

        "BT":
        "Biotechnology / Life Science",

        "COM":
        "Commerce / CA / Finance",

        "ART":
        "Arts / Humanities / History",

        "MED":
        "Media / Communication",

        "DES":
        "Design / Creative Technology"

    }


    recommended_career = career_names.get(

        predicted_category,

        predicted_category

    )
    scores = {

        "CS":
        career_scores["CS"],

        "ENG":
        career_scores["ENG"],

        "BIO":
        career_scores["BIO"],

        "BT":
        career_scores["BT"],

        "COM":
        career_scores["COM"],

        "ART":
        career_scores["ART"],

        "MED":
        career_scores["MED"],

        "DES":
        career_scores["DES"]

    }

    return render_template(

        "result.html",

        student_id=student_id,

        scores=scores,

        recommendation=recommended_career

    )

if __name__ == "__main__":
    create_tables()
    app.run(
        debug=True
    )