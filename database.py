import sqlite3

connection = sqlite3.connect("career_compass.db")

cursor = connection.cursor()

cursor.execute("SELECT COUNT(*) FROM questions")

count = cursor.fetchone()[0]

print("Total Questions:", count)

connection.close()