from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3

app = Flask(__name__)


def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # Drop all tables
    cursor.execute("DROP TABLE IF EXISTS students")
    cursor.execute("DROP TABLE IF EXISTS teachers")
    cursor.execute("DROP TABLE IF EXISTS ski_groups")

    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            emergency_contact TEXT NOT NULL,
            comment TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ski_groups (
            id INTEGER PRIMARY KEY,
            teacher_id INTEGER,
            student_id INTEGER,
            FOREIGN KEY (teacher_id) REFERENCES teachers (id),
            FOREIGN KEY (student_id) REFERENCES students (id),
            UNIQUE(student_id)
        )
    ''')

    # Insert dummy data
    cursor.execute('INSERT INTO teachers (name) VALUES ("John Doe")')
    cursor.execute('INSERT INTO teachers (name) VALUES ("Jane Smith")')
    cursor.execute(
        'INSERT INTO students (name, phone, emergency_contact, comment) VALUES ("Alice", "123456", "789012", "I am a student")')
    cursor.execute(
        'INSERT INTO students (name, phone, emergency_contact, comment) VALUES ("Bob", "234567", "890123", "I am a student too")')
    cursor.execute('INSERT INTO ski_groups (teacher_id, student_id) VALUES (1, 1)')

    conn.commit()
    conn.close()


@app.route('/')
def index():
    return redirect(url_for('add_entries'))


@app.route('/add_entries', methods=['GET', 'POST'])
def add_entries():
    if request.method == 'POST':
        if 'student_name' in request.form:
            student_name = request.form['student_name']
            phone = request.form['phone']
            emergency_contact = request.form['emergency_contact']
            comment = request.form.get('comment', '')
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO students (name, phone, emergency_contact, comment) VALUES (?, ?, ?, ?)', (student_name, phone, emergency_contact, comment))
            conn.commit()
            conn.close()
        elif 'teacher_name' in request.form:
            teacher_name = request.form['teacher_name']
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO teachers (name) VALUES (?)', (teacher_name,))
            conn.commit()
            conn.close()
        return redirect(url_for('add_entries'))
    return render_template('add_entries.html')

@app.route('/ski_groups')
def ski_groups():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM students')
    students = cursor.fetchall()
    cursor.execute('SELECT * FROM teachers')
    teachers = cursor.fetchall()
    cursor.execute('''
        SELECT ski_groups.student_id, students.name, students.phone, students.emergency_contact, students.comment, ski_groups.teacher_id
        FROM ski_groups
        JOIN students ON ski_groups.student_id = students.id
    ''')
    group_assignments = cursor.fetchall()
    conn.close()
    return render_template('ski_groups.html', students=students, teachers=teachers, group_assignments=group_assignments)

@app.route('/assign_group', methods=['POST'])
def assign_group():
    data = request.get_json()
    student_id = data['studentId']
    teacher_id = data['teacherId']
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM ski_groups WHERE student_id = ?', (student_id,))
    existing_assignment = cursor.fetchone()
    if existing_assignment:
        cursor.execute('DELETE FROM ski_groups WHERE student_id = ?', (student_id,))
    cursor.execute('INSERT INTO ski_groups (student_id, teacher_id) VALUES (?, ?)', (student_id, teacher_id))
    conn.commit()
    conn.close()
    return '', 204


init_db()

if __name__ == '__main__':
    app.run()
