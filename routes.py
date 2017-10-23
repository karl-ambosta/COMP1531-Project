from flask import Flask, redirect, render_template, request, url_for, session
from flask_login import LoginManager,login_user, current_user, login_required, logout_user
from server import app,login_manager
from model import *
from collections import Counter
from functools import wraps

flag = 0
msg = ['','Question Successfully Added!', 'Question Not Added! Question Already Exists', 'Survey Successfully Created!', 'Survey Already Exists!']

database = Database()

user_id = -1
user_role = []
course_name = []
choice = ''
resnums = 0
name = []
clicked_survey = []
c_s_data = []
enrolments = []

@login_manager.user_loader
def load_user(user_id):
    return database.get_user(user_id)

def login_required(role):
    def wrap(fn):
        @wraps(fn)
        def decor(*args, **kwargs):

            # Check if user is authenticated
            if current_user.is_authenticated == False:
                return login_manager.unauthorized()

            # Check if user is correct role
            if current_user.get_role() != role:
                return login_manager.unauthorized()

            return fn(*args, **kwargs)

        return decor
    return wrap

# Login page
@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        user_id = request.form["name"]
        password = request.form["password"]

        # Authenticate the user
        u = database.authenticate(user_id,password)

        if u == None:
            return render_template("login.html", msg = 'Login unsuccessful')

        elif u.get_role() == 'admin':
            login_user(u)
            return redirect(url_for("dashboard"))

        elif u.get_role() == 'staff':
            login_user(u)
            return redirect(url_for("staff_dash"))

        elif u.get_role() == 'student':
            login_user(u)

            # gets the courses that student is enrolled in. Return value is in the form of a list.
            enrolments = database.get_user_enrolments(user_id)

            # get open surveys for particular course
            open_surveys = []

            return redirect(url_for("student_dash"))

        else:
            return render_template("login.html", msg = 'Login unsuccessful')

    return render_template("login.html")


@app.route("/Dashboard", methods=["GET", "POST"])
@login_required('admin')
def dashboard():

    if request.method == "POST":

        if request.form["input"] == "1":
            return redirect(url_for("create"))
        elif request.form["input"] == "2":
            return redirect(url_for("question"))
        elif request.form["input"] == "3":
            return redirect(url_for("metrics"))
        elif request.form["input"] == "4":
            return redirect(url_for("logout"))
        else:
            close = request.form["input"]
            f = close.split('_')
            database.close_survey(f)

    return render_template("dashboard.html", review = database.get_review_survey(), active = database.get_active_survey(), closed = database.get_closed_survey())


# Add a question
@app.route("/Question", methods=["GET", "POST"])
@login_required('admin')
def question():

    if request.method == "POST":

        # BACK - Return to the dashboard
        if request.form["input"] == "1":
            return redirect(url_for("dashboard"))

        # ADD QUESTION
        if request.form["input"] == "2":
            return render_template("question.html", add_question = True, questions = database.get_all_questions())

        # DELETE QUESTION
        if request.form["input"] == "3":
            return render_template("question.html", delete_question = True, questions = database.get_all_questions())

        # CANCEL - Cancel the creation of the current question
        if request.form["input"] == "4":
            return render_template("question.html", questions = database.get_all_questions())

        # Question has been entered
        if request.form["input"] == "5":

            # Collect the question text, response type and option
            qu = request.form["addq"]
            re = request.form["type"]
            op = request.form["option"]

            # Multiple choice question -> proceed to collect MC responses
            if re == "Multiple Choice":

                # Store the question details in a temporary session
                session['Temp_Question'] = [qu,re,op]
                return render_template("question.html", set_MC_resnum = True, questions = database.get_all_questions())

            # Store text-response question in database
            else:

                # Add question to database
                question = Questions(name = qu, types = 'Text', option = op, responses = None)
                database.add_question(question)

                return render_template("question.html", set_MC_resnum = False, questions = database.get_all_questions())

        # Collect desired number of MC responses
        if request.form["input"] == "6":
            n = int(request.form["resnum"])
            l = session['Temp_Question']
            l.append(n)
            session['Temp_Question'] = l
            return render_template("question.html", MC_resnum = n, questions = database.get_all_questions())

        # Store MC-response question in database
        if request.form["input"] == "7":

            # Retrieve temporary session data
            data = session['Temp_Question']

            # Get a list of the responses
            responses = []
            n = data[3]
            for i in range(1,n+1):
                responses.append(request.form[str(i)])
                res_str = ",".join(responses)

            print(responses)
            # Add question to the database
            question = Questions(name = data[0], types = data[1], option = data[2], responses = res_str)

            try:
                database.add_question(question)

                # Remove temporary session data
                session.pop('Temp_Question', None)

                return render_template("question.html", questions = database.get_all_questions())

            except ValueError:
                return render_template("question.html", MC_resnum = n, questions = database.get_all_questions())

        # Delete the specified question from the survey
        if request.form["input"] == "8":

            q = request.form["delq"]
            database.delete_question(q)

            return render_template("question.html", questions = database.get_all_questions())

    return render_template("question.html", questions = database.get_all_questions())

# Create a survey
@app.route("/Create", methods=["GET", "POST"])
@login_required('admin')
def create():

    if request.method == "POST":

        # if admin wishes to cancel the creation of a survey
        if request.form["input"] == "1":
            return redirect(url_for("dashboard", surveys = database.get_survey_of_status('review')))

        # when the admin chooses a offering period
        if request.form["input"] == "2":
            choice = 'offer'
            offering = request.form["offering"]


            c = database.get_courses()
            o = []

            course_name[:] = []
            course_name.append(offering)

            # Get all the courses offered in that period
            for i in c:
                if i.offering == offering:
                    o.append(i.name)

            return render_template("create.html", questions = database.get_admin_questions(), courses = database.get_courses(), offerings = database.get_offerings(), choice = 'offer', courseoff = '', offers = o)

        # When the admin submits a course name
        if request.form["input"] == "3":
            courseoff = 'course'
            course_name.insert(0, request.form["course"])

            return render_template("create.html", questions = database.get_admin_questions(), courses = database.get_courses(), offerings = database.get_offerings(), choice = 'offer', courseoff = 'course', offers = '')

        # When the admin submits the chosen questions
        if request.form["input"] == "4":


            print(course_name)

            # Check for existing survey or create new one
            if database.check_survey_status(course_name) != 'None':
                chosen_msg = msg[4]
                return redirect(url_for("dashboard", surveys = database.get_survey_of_status('review')))

            # Check which questions were submitted
            qus = request.form.getlist('check')
            database.create_survey(course_name,qus)
            chosen_msg = msg[3]
            return redirect(url_for("dashboard", surveys = database.get_survey_of_status('review'), msg = chosen_msg))

    return render_template("create.html", questions = database.get_admin_questions(), courses = database.get_courses(), offerings = database.get_offerings(), choice = '', offers = '')


@app.route("/Survey", methods=["GET", "POST"])
def survey():

    if request.method == "POST":

        if request.form["input"] == "0":
            return redirect(url_for("student_dash"))
        
        data = database.get_survey_data(clicked_survey[0])

        data_2 = []
        submitted = []

        for d in data:
            if d[0] not in data_2:
                data_2.append(d[0])

        if request.form["input"] == "1":

            for q in database.get_admin_questions():
                if q[0] in data_2:
                    if q[1] == 'Multiple Choice':
                        i = request.form.getlist(q[0])
                        if i == '':
                            return redirect(url_for("survey"))
                        qi = q[0],i
                        submitted.append(qi)

                    elif q[1] == 'Text':
                        i = request.form[q[0]]
                        if i == '':
                            return redirect(url_for("survey"))
                        qi = q[0],i
                        submitted.append(qi)

            database.submit_survey(user_id, clicked_survey[0], submitted)

            return redirect(url_for("complete"))

    return render_template("survey.html", course_name = clicked_survey, user = user_role, data = database.get_survey_data(clicked_survey[0]), cs_data = c_s_data)


@app.route("/Staff_Dash", methods=["GET", "POST"])
@login_required('staff')
def staff_dash():

    global different
    different = []
    tab = []
    global total_responses_per_question
    total_responses_per_question = []
    global t
    t = []
    global data_list
    global display

    if request.method == "POST":
        if request.form["input"] == "1":
            return redirect(url_for("logout"))

        else:
            s = request.form["input"].split('_')
            
            if s[2] == '1':
                clicked_survey[:] = []                              # resetting list
                s.remove('1')
                string = '_'.join(s)
                clicked_survey.append(string)
                database.get_survey_data(s)                       # gets data from selected course
                user_role[:] = []
                user_role.append('staff')

                # getting name of question
                c_s_data[:] = []
                for c in database.get_survey_data(s):
                    if c[0] not in c_s_data:
                        c_s_data.append(c[0])

                return redirect(url_for("review"))
            else:
                s.remove('2')
                string = '_'.join(s)
                view = database.survey_results(string)

                for v in view:
                    if v[0] not in different:
                        different.append(v[0])

                data_list = database.query_question(different)

                for d in different:
                    question = []

                    for v in view:
                        if v[0] == d:
                            question.append(v[1])

                    tab.append(question)

                index = 0;
                for i in tab:
                    total_responses_per_question.append(len(i))
                    results = []
                    j = Counter(i)
                    for key, value in j.items() :
                        results.append((key,value))
                    t.append(results)
                    index += 1

                display = request.form["input"].split('_')
                display.remove('2')

                return redirect(url_for("closed_metrics"))
            

    u_id = current_user.get_id()
    return render_template("staff_dash.html", user = u_id, user_enrols = database.get_enrolment_surveys(u_id, 'staff'))

@app.route("/Student_Dash", methods=["GET", "POST"])
@login_required('student')
def student_dash():

    global different
    different = []
    tab = []
    global total_responses_per_question
    total_responses_per_question = []
    global t
    t = []
    global data_list
    global display

    if request.method == "POST":
        if request.form["input"] == "1":
            return redirect(url_for("logout"))

        else:
            s = request.form["input"].split('_')
            
            if s[2] == '1':
                clicked_survey[:] = []                              # resetting list
                s.remove('1')
                string = '_'.join(s)
                clicked_survey.append(string)
                database.get_survey_data(s)                       # gets data from selected course
                user_role[:] = []
                user_role.append('staff')

                # getting name of question
                c_s_data[:] = []
                for c in database.get_survey_data(s):
                    if c[0] not in c_s_data:
                        c_s_data.append(c[0])

                return redirect(url_for("survey"))
            else:
                s.remove('2')
                string = '_'.join(s)
                view = database.survey_results(string)

                for v in view:
                    if v[0] not in different:
                        different.append(v[0])

                data_list = database.query_question(different)

                for d in different:
                    question = []

                    for v in view:
                        if v[0] == d:
                            question.append(v[1])

                    tab.append(question)

                index = 0;
                for i in tab:
                    total_responses_per_question.append(len(i))
                    results = []
                    j = Counter(i)
                    for key, value in j.items() :
                        results.append((key,value))
                    t.append(results)
                    index += 1

                display = request.form["input"].split('_')
                display.remove('2')

                return redirect(url_for("closed_metrics"))

    u_id = current_user.get_id()
    return render_template("student_dash.html", user = u_id, enrolments = enrolments, surv = database.get_enrolment_surveys(u_id, 'student'), enrols = database.get_user_enrolments(u_id))

@app.route('/logout')
def logout():
    global user_id
    user_id = -1
    logout_user()
    return redirect(url_for('login'))


# Miscellaneous Survey Pages

@app.route("/Complete", methods=["GET", "POST"])
def complete():

    if request.method == "POST":

        if request.form["input"] == "1":
            return redirect(url_for("student_dash"))

    return render_template("complete.html")

@app.route("/Nothing", methods=["GET", "POST"])
def nothing():

    return render_template("nothing.html")

@app.route("/Review", methods=["GET", "POST"])
@login_required('staff')
def review():

    if request.method == "POST":

        if request.form["input"] == "0":
            return redirect(url_for("staff_dash"))

        if request.form["input"] == "1":
            d = clicked_survey[0]
            e = d.split('_')
            database.release_survey(e)
            return redirect(url_for("staff_dash"))

        else:
            question = request.form["input"].split('_')
            if question[1] == 'add':
                c_s_data.append(question[0])
                database.add_to_survey(clicked_survey[0],question[0])
                return redirect(url_for("review"))
            
            else:
                database.delete_from_survey(clicked_survey[0],question[0])
                c_s_data.remove(question[0])

    return render_template("review.html", course_name = clicked_survey, user = user_role, data = database.get_survey_data(clicked_survey[0]), cs_data = c_s_data, questions = database.get_admin_questions())

@app.route("/Metrics", methods=["GET", "POST"])
def metrics():

    if request.method == "POST":

        global view 
        global different
        global data_list
        different = []
        question_options = []
        data_list = []
        global display_results

        if request.form["input"] == "1":
            return redirect(url_for("dashboard"))

        elif request.form["input"] == "2":
            display_results = request.form["active"]
            view = database.survey_results(display_results)
            
            for v in view:
                if v[0] not in different:
                    different.append(v[0])

            data_list = database.query_question(different)
            return redirect(url_for("metrics2"))

        elif request.form["input"] == "3":
            display_results = request.form["closed"]
            view = database.survey_results(display_results)

            for v in view:
                if v[0] not in different:
                    different.append(v[0])

            data_list = database.query_question(different)

            return redirect(url_for("metrics2"))



    return render_template("metrics.html", active = database.get_survey_of_status('active'), closed = database.get_survey_of_status('closed'))

@app.route("/Metrics2", methods=["GET", "POST"])
def metrics2():

    if request.method == "POST":

        if request.form["input"] == "1":
            return redirect(url_for("metrics"))

    global results
    results = []
    tab = []
    global t
    t = []
    global total_responses_per_question
    total_responses_per_question = []

    for d in different:
        question = []

        for v in view:
            if v[0] == d:
                question.append(v[1])

        tab.append(question)

    index = 0;
    for i in tab:
        total_responses_per_question.append(len(i))
        results = []
        j = Counter(i)
        for key, value in j.items() :
            results.append((key,value))
        t.append(results)
        index += 1

    return render_template("metrics2.html", name = display_results, diff = different, data = data_list, results = t, length = len(different), total = total_responses_per_question)
   
@app.route("/closed_metrics", methods=["GET", "POST"])
def closed_metrics():

    return render_template("closed_metrics.html", name = display, diff = different, data = data_list, results = t, length = len(different), total = total_responses_per_question)
