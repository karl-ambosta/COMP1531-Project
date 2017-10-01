from read import *
import sqlite3

def fill_database():

    connection = sqlite3.connect('survey.db')
    cursorObj = connection.cursor()

    # Create passwords table
    query = """CREATE TABLE IF NOT EXISTS passwords (
    id INTEGER PRIMARY KEY,
    pw VARCHAR(255),
    role VARCHAR(10));"""
    cursorObj.execute(query)

    # Fill the passwords table
    users = read_passwords()
    for row in users:
        print(row[0], row[1], row[2])

        string = """INSERT INTO passwords (id, pw, role)
        VALUES ("{i}", "{p}", "{r}")"""

        query = string.format(i=row[0], p=row[1], r=row[2])
        print(query)
        cursorObj.execute(query)

    # Create courses table
    query = """CREATE TABLE IF NOT EXISTS courses (
    course VARCHAR(255),
    offering VARCHAR(10));"""
    cursorObj.execute(query)

    # Fill in courses table
    course = read_courses()
    for row in course:
        print(row[0], row[1])

        string = """INSERT INTO courses (course, offering)
        VALUES ("{c}", "{o}")"""

        query = string.format(c=row[0], o=row[1])
        print(query)
        cursorObj.execute(query)

    # Create enrolments table
    query = """CREATE TABLE IF NOT EXISTS enrolments (
    id INTEGER,
    course VARCHAR(255),
    offering VARCHAR(10),
    FOREIGN KEY(id) REFERENCES passwords(id),
    FOREIGN KEY(course) REFERENCES enrolments(course),
    FOREIGN KEY(offering) REFERENCES enrolments(offering));"""
    cursorObj.execute(query)

    # Fill in enrolments table
    enrolment = read_enrolments()
    for row in enrolment:
        print(row[0], row[1], row[2])

        string = """INSERT INTO enrolments (id, course, offering)
        VALUES ("{i}", "{c}", "{o}")"""

        query = string.format(i=row[0], c=row[1], o=row[2])
        print(query)
        cursorObj.execute(query)

    connection.commit()
    cursorObj.close()

def authenticate(user_id, password):

    connection = sqlite3.connect('survey.db')
    cursorObj = connection.cursor()

    #query = "SELECT pw, role from passwords where id = ?", user_id
    #result = cursorObj.execute(query)
    for result in cursorObj.execute( "SELECT pw, role from passwords where id = ?", (user_id,) ):
        print(result)

    connection.commit()
    cursorObj.close()

    # Password matches database
    if result[0] == password:
        return result[1]
    else:
        return "invalid"
