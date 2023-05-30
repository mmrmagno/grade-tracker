from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

# Function to create a new database connection for each request
def get_db_connection():
    conn = sqlite3.connect('grades.db')
    conn.row_factory = sqlite3.Row
    return conn

# Function to create a new database cursor for each request
def get_db_cursor(connection):
    return connection.cursor()

# Custom filter: enumerate
@app.template_filter('enumerate')
def enumerate_filter(values):
    return zip(range(1, len(values) + 1), values)

@app.template_filter('average')
def average_filter(numbers):
    if numbers:
        return sum(numbers) / len(numbers)
    return 0

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        subject = request.form['subject']
        grade = float(request.form['grade'])

        conn = get_db_connection()
        c = get_db_cursor(conn)

        # Insert the grade into the database
        c.execute("INSERT INTO grades VALUES (?, ?)", (subject, grade))
        conn.commit()

        # Close the cursor and database connection
        c.close()
        conn.close()

    conn = get_db_connection()
    c = get_db_cursor(conn)

    # Fetch all grades from the database
    c.execute("SELECT subject, grade FROM grades")
    rows = c.fetchall()
    subjects = {}
    for row in rows:
        subject = row['subject']
        grade = row['grade']
        if subject in subjects:
            subjects[subject].append(grade)
        else:
            subjects[subject] = [grade]

    # Close the cursor and database connection
    c.close()
    conn.close()

    return render_template('index.html', subjects=subjects)


@app.route('/remove', methods=['POST'])
def remove():
    subject = request.form['subject']
    selected_grade = request.form['grade']
    grade, index = selected_grade.split('_')
    grade = float(grade)

    conn = get_db_connection()
    c = get_db_cursor(conn)

    # Fetch all grades for the subject from the database
    c.execute("SELECT rowid FROM grades WHERE subject=? AND grade=?", (subject, grade))
    row = c.fetchone()

    if row:
        rowid = row['rowid']
        # Delete the first occurrence of the grade for the subject from the database
        c.execute("DELETE FROM grades WHERE rowid=?", (rowid,))
        conn.commit()

    # Fetch all grades from the database
    c.execute("SELECT subject, grade FROM grades")
    rows = c.fetchall()
    subjects = {}
    for row in rows:
        subject = row['subject']
        grade = row['grade']
        if subject in subjects:
            subjects[subject].append(grade)
        else:
            subjects[subject] = [grade]

    # Close the cursor and database connection
    c.close()
    conn.close()

    return render_template('index.html', subjects=subjects)



if __name__ == '__main__':
    app.run(debug=True)
