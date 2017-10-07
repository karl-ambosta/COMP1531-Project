from read import *
import sqlite3

def fill_database():

    connection = sqlite3.connect('survey.db')
    cursorObj = connection.cursor()

    # Create questions table
    query = """CREATE TABLE IF NOT EXISTS questions (
    qu VARCHAR(255) PRIMARY KEY,
    type VARCHAR(255),
    option VARCHAR(255),
    responses VARCHAR(255));"""
    
    cursorObj.execute(query)

    # Create passwords table
    query = """CREATE TABLE IF NOT EXISTS passwords (
    id INTEGER PRIMARY KEY,
    password VARCHAR(255),
    role VARCHAR(10));"""
    cursorObj.execute(query)

    # Fill the passwords table
    users = read_passwords()
    for row in users:
        print(row[0], row[1], row[2])

        string = """INSERT OR IGNORE INTO passwords (id, password, role)
        VALUES ("{i}", "{p}", "{r}")"""

        query = string.format(i=row[0], p=row[1], r=row[2])
        print(query)
        cursorObj.execute(query)

        # Add the admin user to the database
        query = """INSERT OR IGNORE INTO passwords (id, password, role)
        VALUES (0, "admin", "admin")"""
        cursorObj.execute(query)


    # Create courses table
    query = """CREATE TABLE IF NOT EXISTS courses (
    course VARCHAR(255),
    offering VARCHAR(10),
    status TEXT);"""
    cursorObj.execute(query)

    # Fill in courses table
    course = read_courses()
    for row in course:
        print(row[0], row[1])

        string = """INSERT OR IGNORE INTO courses (course, offering, status)
        VALUES ("{c}", "{o}", "None")"""

        query = string.format(c=row[0], o=row[1])
        print(query)
        cursorObj.execute(query)

    # Create enrolments table
    query = """CREATE TABLE IF NOT EXISTS enrolments (
    id INTEGER,
    course VARCHAR(255),
    offering VARCHAR(10),
    status INTEGER,
    FOREIGN KEY(id) REFERENCES passwords(id),
    FOREIGN KEY(course) REFERENCES enrolments(course),
    FOREIGN KEY(offering) REFERENCES enrolments(offering));"""
    cursorObj.execute(query)

    # Fill in enrolments table
    enrolment = read_enrolments()
    for row in enrolment:
        print(row[0], row[1], row[2])

        string = """INSERT OR IGNORE INTO enrolments (id, course, offering, status)
        VALUES ("{i}", "{c}", "{o}", 0)"""

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
    for result in cursorObj.execute( "SELECT password, role from passwords where id = ?", (user_id,) ):
        print(result)

    connection.commit()
    cursorObj.close()

    # Password matches database
    if result[0] == password:
        return result[1]
    else:
        return "invalid"
