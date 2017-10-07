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
    query = cursorObj.execute("DELETE FROM questions WHERE qu ='%s'", q)
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

def get_enrolment_surveys(user_id, role):

    connection = sqlite3.connect('survey.db')
    cursorObj = connection.cursor()

    user_enrolments = []
    enrol_survey_status = []
    read_enrols = []

    if role == 'admin':
        for s in cursorObj.execute("SELECT * FROM courses"):
            if s not in enrol_survey_status:
                enrol_survey_status.append(s)

    # Gather staff enrolments and append to user_enrolments
    for u in cursorObj.execute("SELECT * FROM enrolments WHERE id = '%d'" % (int(user_id))):
        if (u[1],u[2]) not in user_enrolments:
            us = u[1],u[2]
            user_enrolments.append(us)

    if role == 'staff':
        # From the staff's enrolments, check if the course has a survey in the review stage
        for w in cursorObj.execute("SELECT DISTINCT * FROM courses WHERE course = '%s' AND offering = '%s'" % (user_enrolments[0][0], user_enrolments[0][1])):
            if (w[0],w[1]) not in read_enrols:
                ws = w[0],w[1]
                read_enrols.append(ws)
                enrol_survey_status.append(w)

    if role == 'student':
        for user in user_enrolments:
            for v in cursorObj.execute("SELECT DISTINCT * FROM courses WHERE course = '%s' AND offering = '%s'" % (user[0], user[1])):
                if (v[0],v[1]) not in read_enrols:
                    vs = v[0],v[1]
                    read_enrols.append(vs)
                    enrol_survey_status.append(v)
 
    connection.commit()
    cursorObj.close()
    print(enrol_survey_status)

    return enrol_survey_status

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
    cursorObj.execute("UPDATE courses SET status='review' WHERE course ='%s' AND offering='%s' " % (name[0], name[1]))

    query = """CREATE TABLE IF NOT EXISTS '%s_%s' (
    question TEXT,
    type TEXT,
    response TEXT,
    num, INT);""" % (name[0],name[1])

    # Create table with course survey name
    cursorObj.execute(query)

    qss = []

    for q in questions:
        for qs in cursorObj.execute("SELECT * FROM questions WHERE qu ='%s'" % (q)):
                qss.append(qs)

    for s in qss:
        if s[1] == 'Multiple Choice':
            cursorObj.execute("INSERT INTO '%s_%s' (question, type, response, num) VALUES ('%s', 'Multiple Choice', 'Agree', '0') " % (name[0], name[1], s[0]))
            cursorObj.execute("INSERT INTO '%s_%s' (question, type, response, num) VALUES ('%s', 'Multiple Choice', 'Disagree', '0') " % (name[0], name[1], s[0]))

    for t in qss:
        if t[1] == 'Text':
            cursorObj.execute("INSERT INTO '%s_%s' (question, type, response, num) VALUES ('%s', 'Text', 'Answer', '0') " % (name[0], name[1], t[0]))

    connection.commit()
    cursorObj.close()

# checks status of survey
def check_survey_status(name):

    connection = sqlite3.connect('survey.db')
    cursorObj = connection.cursor()

    status = []

    # Check the status of course survey
    for w in cursorObj.execute("SELECT * FROM courses WHERE course ='%s' AND offering ='%s'" % (name[0], name[1])):
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
        for s in cursorObj.execute("SELECT * FROM courses WHERE course='%s' AND status ='%s'" % (course_name, status)):
                st.append(s)

    connection.commit()
    cursorObj.close()


    return st

# Selects from enrolments table the courses a student is enrolled in
def get_student_enrolments(user_id):

    connection = sqlite3.connect('survey.db')
    cursorObj = connection.cursor()

    enrolled = []
    for e in cursorObj.execute("SELECT * FROM enrolments WHERE id ='%s'" % (user_id)):
        if e not in enrolled:
            print(e)
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
    text_questions = []
    for sq in cursorObj.execute("SELECT DISTINCT * FROM '%s'" % (course_name)):
        print('sq = ', sq)

        if sq[1] == 'Multiple Choice':
            survey_questions.append(sq)

        elif sq[1] == 'Text':
                if sq[0] not in text_questions:
                    survey_questions.append(sq)
                    text_questions.append(sq[0])

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

    print('c[0] = ', course_name[0])
    print('c[1] = ', course_name[1])

    # Change status of course to 'active'
    cursorObj.execute("UPDATE courses SET status='closed' WHERE course = '%s' AND offering = '%s'" % (course_name[0], course_name[1]))

    connection.commit()
    cursorObj.close()

def submit_survey(user_id, course_name, submitted_responses):

    connection = sqlite3.connect('survey.db')
    cursorObj = connection.cursor()

    print(submitted_responses)

    # Change status of enrolment survey to 'complete'
    #cursorObj.execute("UPDATE enrolments SET status='complete' WHERE course = '%s' AND offering = '%s'" % (course_name[0], course_name[1]))

    for s in submitted_responses:
        if s[1] == 'Multiple Choice':
            for w in cursorObj.execute("SELECT * FROM '%s' WHERE question = '%s' AND response = '%s'" % (course_name, s[0], s[2])):
                ww = int(w[3])
                new = ww + 1
                print(new)
                cursorObj.execute("UPDATE '%s' SET num = '%d' WHERE question = '%s' AND response = '%s'" % (course_name, new, w[0], w[2]))

        elif s[1] == 'Text':
            print('s[2] = ', s[2])
            cursorObj.execute("INSERT INTO '%s' (question, type, response, num) VALUES ('%s', 'Text', '%s', '1')" % (course_name, s[0], s[2]))

    connection.commit()
    cursorObj.close()
