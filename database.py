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

    query = cursorObj.execute("DELETE FROM questions WHERE qu = '%s'" % (qu))
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

def create_survey(name):

    connection = sqlite3.connect('survey.db')
    cursorObj = connection.cursor()

    status = []

    # Check if specified course and offering already has a survey in any stage
    for w in cursorObj.execute("SELECT * FROM courses WHERE course = '%s' AND offering = '%s'" % (name[0], name[1])):
        if w not in status:
            status.append(w)

    print(status[0][2])
    # If survey already exists, don't make a new one
    if status[0][2] != 'None':
        print('none if')
        return 'exists'

    print('some else')
    # Else, change status to created
    cursorObj.execute("UPDATE courses SET status='review' WHERE course = '%s' AND offering = '%s'" % (name[0], name[1]))

    connection.commit()
    cursorObj.close()
    return 'some'

def check_survey_status(status):

    connection = sqlite3.connect('survey.db')
    cursorObj = connection.cursor()

    st = []
    for s in cursorObj.execute("SELECT * FROM courses WHERE status = '%s'" % (status)):
        if s not in st:
            st.append(s)

    return st


    













