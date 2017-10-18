import sqlite3

class db_utils():

    # Add a question to the pool
    @staticmethod
    def add_question(q):

        connection = sqlite3.connect('survey.db')
        cursorObj = connection.cursor()

        string = """INSERT INTO questions (qu, type, option, responses)
        VALUES ("{q}", "{t}", "{o}", "{r}")"""

        query = string.format(q=q.qu, t=q.type, o=q.option, r=q.responses)
        print(query)
        cursorObj.execute(query)

        connection.commit()
        cursorObj.close()

    @staticmethod
    def delete_question(qu):

        connection = sqlite3.connect('survey.db')
        cursorObj = connection.cursor()

        # string = """DELETE FROMquestions WHERE question='%s' AND type='%s'""" % (qu, ty)

        q = (qu)
        query = cursorObj.execute("DELETE FROM questions WHERE qu ='%s'" % (q))
        print(query)

        connection.commit()
        cursorObj.close()

    # Get all the questions in the pool
    @staticmethod
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
    @staticmethod
    def get_courses():

        connection = sqlite3.connect('survey.db')
        cursorObj = connection.cursor()

        course = []
        for c in cursorObj.execute("SELECT * FROM courses"):
            course.append(c)

        connection.commit()
        cursorObj.close()

        return course

    @staticmethod
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
        # print(enrol_survey_status)

        return enrol_survey_status

    # Read the courses and gather the different offerings for the courses
    @staticmethod
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

    @staticmethod
    def create_survey(name, questions):

        connection = sqlite3.connect('survey.db')
        cursorObj = connection.cursor()

        # Change status of course to 'review'
        cursorObj.execute("UPDATE courses SET status='review' WHERE course ='%s' AND offering='%s' " % (name[0], name[1]))

        query = """CREATE TABLE IF NOT EXISTS '%s_%s' (
        question TEXT,
        type TEXT,
        response TEXT,
        num, TEXT);""" % (name[0],name[1])

        # Create table with course survey name
        cursorObj.execute(query)

        print('questions = ', questions)

        qss = []

        for q in questions:
            for qs in cursorObj.execute("SELECT * FROM questions WHERE qu ='%s'" % (q)):
                    qss.append(qs)

        print('qss = ', qss)

        for s in qss:
            if s[1] == 'Multiple Choice':
                print(s[3])
                i = s[3].strip('[]')
                num = 1
                for j in i:
                    if j == ',':
                        num = num + 1
                l = ['0']
                for k in range(1,num):
                    l.append('0')

                string = """INSERT INTO '%s_%s' (question, type, response, num)
                VALUES ("{q}", "Multiple Choice", "{r}", "{n}")""" % (name[0], name[1])
                query = string.format(q=s[0], r=s[3], n=l)
                print('query = ',query)
                cursorObj.execute(query)

        for t in qss:
            if t[1] == 'Text':
                cursorObj.execute("INSERT INTO '%s_%s' (question, type, response, num) VALUES ('%s', 'Text', 'Answer', '0') " % (name[0], name[1], t[0]))

        connection.commit()
        cursorObj.close()

    # checks status of survey
    @staticmethod
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
    @staticmethod
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
    @staticmethod
    def get_student_enrolments(user_id):

        connection = sqlite3.connect('survey.db')
        cursorObj = connection.cursor()

        enrolled = []
        already_in = []
        for e in cursorObj.execute("SELECT * FROM enrolments WHERE id ='%s'" % (user_id)):
            if (e[1],e[2]) not in already_in:
                print('e = ', e)
                already_in.append((e[1],e[2]))
                enrolled.append(e)
                print(already_in)

        print('enrolled = ', enrolled)
        connection.commit()
        cursorObj.close()

        return enrolled

    @staticmethod
    def get_survey_of_status(table_name, status):

        connection = sqlite3.connect('survey.db')
        cursorObj = connection.cursor()

        st = []
        for s in cursorObj.execute("SELECT DISTINCT * FROM '%s' WHERE status = '%s'" % (table_name, status)):
                st.append(s)

        connection.commit()
        cursorObj.close()

        return st

    @staticmethod
    def get_survey_data(course_name):

        connection = sqlite3.connect('survey.db')
        cursorObj = connection.cursor()

        survey_questions = []
        questions_list = []
        text_questions = []
        for sq in cursorObj.execute("SELECT DISTINCT * FROM '%s'" % (course_name)):
            print('sq = ', sq)

            if sq[1] == 'Multiple Choice':
                survey_questions.append(sq)

            elif sq[1] == 'Text':
                    if sq[0] not in text_questions:
                        survey_questions.append(sq)
                        text_questions.append(sq[0])

        for s in survey_questions:
            if s[1] == 'Multiple Choice':
                i = s[2].replace('[','').replace(']', '').replace("'",'')
                j = i.split(',')
                i = s[3].replace('[','').replace(']', '').replace("'",'')
                k = i.split(',')
                questions_list.append([s[0],s[1],j,k])

        connection.commit()
        cursorObj.close()

        return questions_list

    @staticmethod
    def add_to_survey(survey_name, question):

        connection = sqlite3.connect('survey.db')
        cursorObj = connection.cursor()

        question_check = []

        for i in cursorObj.execute("SELECT DISTINCT * FROM questions WHERE qu = '%s'" % (question)):
                question_check.append(i)

        if i[1] == 'Multiple Choice':
            r = question_check[0][3].replace('[','').replace(']', '').replace("'",'')
            s = r.split(',')
            l = []
            for t in s:
                l.append('0')


            # cursorObj.execute("INSERT INTO '%s' (question, type, response, num) VALUES ('%s', 'Multiple Choice', 'Agree', '0') " % (survey_name, question))
            string = """INSERT INTO '%s' (question, type, response, num)
                VALUES ("{q}", "Multiple Choice", "{r}", "{n}")""" % (survey_name)
            query = string.format(q=question, r=s, n=l)
            print('query = ',query)
            cursorObj.execute(query)

            # cursorObj.execute("INSERT INTO '%s' (question, type, response, num) VALUES ('%s', 'Multiple Choice', 'Disagree', '0') " % (survey_name, question))

        if i[1] == 'Text':
            cursorObj.execute("INSERT INTO '%s' (question, type, response, num) VALUES ('%s', 'Text', 'Answer', '0') " % (survey_name, question))

        connection.commit()
        cursorObj.close()

    @staticmethod
    def release_survey(course_name):

        connection = sqlite3.connect('survey.db')
        cursorObj = connection.cursor()

        # Change status of course to 'active'
        cursorObj.execute("UPDATE courses SET status='active' WHERE course = '%s' AND offering = '%s'" % (course_name[0], course_name[1]))

        connection.commit()
        cursorObj.close()

    @staticmethod
    def close_survey(course_name):

        connection = sqlite3.connect('survey.db')
        cursorObj = connection.cursor()

        print('c[0] = ', course_name[0])
        print('c[1] = ', course_name[1])

        # Change status of course to 'active'
        cursorObj.execute("UPDATE courses SET status='closed' WHERE course = '%s' AND offering = '%s'" % (course_name[0], course_name[1]))

        connection.commit()
        cursorObj.close()

    @staticmethod
    def submit_survey(user_id, course_name, submitted_responses):

        connection = sqlite3.connect('survey.db')
        cursorObj = connection.cursor()

        print(submitted_responses)

        # Change status of enrolment survey to 'complete'
        #cursorObj.execute("UPDATE enrolments SET status='complete' WHERE course = '%s' AND offering = '%s'" % (course_name[0], course_name[1]))

        for s in submitted_responses:

            print('s[2][0] = ', s[2][0])
            if s[1] == 'Multiple Choice':

                    # question = w[0]
                    # Type = w[1]
                    # Responses = w[2]
                    # Numbers = w[3]

                for w in cursorObj.execute("SELECT * FROM '%s' WHERE question = '%s'" % (course_name, s[0])):
                    print('w = ',w)

                    r = w[2].replace('[','').replace(']', '').replace("'",'')
                    responses = r.split(',')

                    index = 0
                    for i in responses:
                        if i != s[2][0]:
                            index = index + 1
                        else:
                            break


                    n = w[3].replace('[','').replace(']', '').replace("'",'')
                    numbers = n.split(',')

                    nindex = int(numbers[index]) + 1
                    numbers[index] = nindex
                    print(numbers)

                    string = """UPDATE '%s' SET response = "{r}", num = "{n}" WHERE question = "{q}" """ % (course_name)
                    query = string.format(q=w[0], r=responses, n=numbers)
                    print('MC query = ',query)
                    cursorObj.execute(query)

            elif s[1] == 'Text':
                print('s[2] = ', s[2])
                # cursorObj.execute("INSERT INTO '%s' (question, type, response, num) VALUES ('%s', 'Text', '%s', '1')" % (course_name, s[0], s[2]))
                string = """INSERT INTO '%s' (question, type, response, num) VALUES ("{q}", 'Text', "{r}", "1")""" % (course_name)
                query = string.format(q=s[0], r=s[2])
                print('Text query = ',query)
                cursorObj.execute(query)



        c = course_name.split('_')
        string = string = """UPDATE enrolments SET status = 'complete' WHERE course = "{c}" AND offering = "{o}" """
        query = string.format(c=c[0], o=c[1])
        print('query = ', query)
        cursorObj.execute(query)

        connection.commit()
        cursorObj.close()

    @staticmethod
    def survey_results(course_name):
        
        connection = sqlite3.connect('survey.db')
        cursorObj = connection.cursor()

        surv_results = []
        surv_list = []
        print('name = ', course_name)

        for sr in cursorObj.execute("SELECT * FROM '%s'" % (course_name)):
            surv_results.append(sr)



        for s in surv_results:
            # s[2] and s[3] are not lists
            resp = s[2].replace('[','').replace(']', '').replace("'",'')
            responses = resp.split(',')
            print('responses = ', responses)

            for r in responses:
                print('r = ', r)

            numb = s[3].replace('[','').replace(']', '').replace("'",'')
            num = numb.split(',')
            print('num = ', num)

            for n in num:
                print('n = ', n)

            surv_list.append([s[0], s[1], responses, num])

        return surv_list