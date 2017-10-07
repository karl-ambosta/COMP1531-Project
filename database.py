import sqlite3

# Add a question to the pool
def add_question(qu, type):

    connection = sqlite3.connect('survey.db')
    cursorObj = connection.cursor()

    string = """INSERT INTO questions (qu, type)
    VALUES ("{q}", "{t}")"""

    query = string.format(q=qu, t=type)
    print(query)
    cursorObj.execute(query)

    connection.commit()
    cursorObj.close()

def delete_question(qu):

    connection = sqlite3.connect('survey.db')
    cursorObj = connection.cursor()

    # string = """DELETE FROMquestions WHERE question='%s' AND type='%s'""" % (qu, ty)

    q = (qu)
    query = cursorObj.execute("DELETE FROM questions WHERE qu =?", q)
    print(query)

    connection.commit()
    cursorObj.close()

# Get all the questions in the pool
def get_admin_questions():

    connection = sqlite3.connect('survey.db')
    cursorObj = connection.cursor()

    questions = []
    for q in cursorObj.execute("SELECT * FROM questions"):
        questions.append(q)

    connection.commit()
    cursorObj.close()

    return questions

#Read all the courses from csv file into the database
def get_courses():

    connection = sqlite3.connect('survey.db')
    cursorObj = connection.cursor()

    course = []
    for c in cursorObj.execute("SELECT * FROM courses"):
        course.append(c)

    connection.commit()
    cursorObj.close()

    return course

# Read the courses and gather the different offerings for the courses
def get_offerings():

    connection = sqlite3.connect('survey.db')
    cursorObj = connection.cursor()

    course = []
    for c in cursorObj.execute("SELECT * FROM courses"):
        course.append(c)

    connection.commit()
    cursorObj.close()

    offerings = []

    for c in course:
        if c[1] not in offerings:
            offerings.append(c[1])

    return offerings

def create_survey(name, questions):

    connection = sqlite3.connect('survey.db')
    cursorObj = connection.cursor()

    # Change status of course to 'review'
    cursorObj.execute("UPDATE courses SET status='review' WHERE course =? AND offering=? ", (name[0], name[1]))

    query = """CREATE TABLE IF NOT EXISTS '%s_%s' (
    question TEXT,
    type TEXT,
    response TEXT,
    num, INT);""" % (name[0],name[1])

    # Create table with course survey name
    cursorObj.execute(query)

    qss = []

    for q in questions:
        for qs in cursorObj.execute("SELECT DISTINCT * FROM questions WHERE qu =?", (q)):
                qss.append(qs)

    for s in qss:
        if s[1] == 'Multiple Choice':
            cursorObj.execute("INSERT INTO '%s_%s' (question, type, response, num) VALUES ('?', 'Multiple Choice', 'Agree', '0') ", (name[0], name[1], s[0]))
            cursorObj.execute("INSERT INTO '%s_%s' (question, type, response, num) VALUES ('?', 'Multiple Choice', 'Disagree', '0') ", (name[0], name[1], t[0]))

    for t in qss:
        if t[1] == 'Text':
            cursorObj.execute("INSERT INTO '%s_%s' (question, type, response, num) VALUES ('?', 'Text', 'Answer', '0') ", (name[0], name[1], t[0]))

    connection.commit()
    cursorObj.close()

# checks status of survey
def check_survey_status(name):

    connection = sqlite3.connect('survey.db')
    cursorObj = connection.cursor()

    status = []

    # Check the status of course survey
    for w in cursorObj.execute("SELECT DISTINCT * FROM courses WHERE course =? AND offering =?", (name[0], name[1])):
            status.append(w)


    connection.commit()
    cursorObj.close()

    return status[0][2]

# For each course that the student is enrolled in, this function collects the surveys of a
# particular status i.e. for a student, will get 'active' and 'closed' surveys.
def get_survey_status(course_name, status):

    connection = sqlite3.connect('survey.db')
    cursorObj = connection.cursor()

    st = []
    if status == 'active':
        for s in cursorObj.execute("SELECT DISTINCT * FROM courses WHERE course=? AND status =?", (course_name, status)):
                st.append(s)

    connection.commit()
    cursorObj.close()


    return st

# Selects from enrolments table the courses a student is enrolled in
def get_student_enrolments(user_id):

    connection = sqlite3.connect('survey.db')
    cursorObj = connection.cursor()

    enrolled = []
    for e in cursorObj.execute("SELECT DISTINCT course FROM enrolments WHERE id =?", (user_id,)):
            enrolled.append(e)

    connection.commit()
    cursorObj.close()

    return enrolled

def get_survey_of_status(table_name, status):

    connection = sqlite3.connect('survey.db')
    cursorObj = connection.cursor()

    st = []
    for s in cursorObj.execute("SELECT DISTINCT * FROM '%s' WHERE status = '%s'" % (table_name, status)):
            st.append(s)

    connection.commit()
    cursorObj.close()

    return st

def get_survey_data(course_name):

    connection = sqlite3.connect('survey.db')
    cursorObj = connection.cursor()

    survey_questions = []
    for sq in cursorObj.execute("SELECT DISTINCT * FROM '%s'" % (course_name)):
            survey_questions.append(sq)

    connection.commit()
    cursorObj.close()

    return survey_questions

def add_to_survey(survey_name, question):

    connection = sqlite3.connect('survey.db')
    cursorObj = connection.cursor()

    question_check = []

    for i in cursorObj.execute("SELECT DISTINCT * FROM questions WHERE qu = '%s'" % (question)):
            question_check.append(i)

    if i[1] == 'Multiple Choice':
        cursorObj.execute("INSERT INTO '%s' (question, type, response, num) VALUES ('%s', 'Multiple Choice', 'Agree', '0') " % (survey_name, question))
        cursorObj.execute("INSERT INTO '%s' (question, type, response, num) VALUES ('%s', 'Multiple Choice', 'Disagree', '0') " % (survey_name, question))

    if i[1] == 'Text':
        cursorObj.execute("INSERT INTO '%s' (question, type, response, num) VALUES ('%s', 'Text', 'Answer', '0') " % (survey_name, question))

    connection.commit()
    cursorObj.close()

def release_survey(course_name):

    connection = sqlite3.connect('survey.db')
    cursorObj = connection.cursor()

    # Change status of course to 'active'
    cursorObj.execute("UPDATE courses SET status='active' WHERE course = '%s' AND offering = '%s'" % (course_name[0], course_name[1]))

    connection.commit()
    cursorObj.close()

def close_survey(course_name):

    connection = sqlite3.connect('survey.db')
    cursorObj = connection.cursor()

    # Change status of course to 'active'
    cursorObj.execute("UPDATE courses SET status='closed' WHERE course = '%s' AND offering = '%s'" % (course_name[0], course_name[1]))

    connection.commit()
    cursorObj.close()

def submit_survey(user_id, course_name):

    connection = sqlite3.connect('survey.db')
    cursorObj = connection.cursor()

    # Change status of course to 'active'
    cursorObj.execute("UPDATE enrolments SET status='complete' WHERE course = '%s' AND offering = '%s'" % (course_name[0], course_name[1]))

    connection.commit()
    cursorObj.close()
