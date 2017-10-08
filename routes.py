from flask import Flask, redirect, render_template, request, url_for, session
from flask_login import LoginManager,login_user, current_user, login_required, logout_user
from model import User
from server import app,login_manager
from classes import *
from authenticate import *
from database import *

admins = {}
flag = 0
msg = ['','Question Successfully Added!', 'Question Not Added! Question Already Exists', 'Survey Successfully Created!', 'Survey Already Exists!']

user_id = -1
user_role = []
course_name = []
choice = ''
resnums = 0
name = []
clicked_survey = []
c_s_data = []
enrolments = []


def get_user(user_id):
    """
    Your get user should get user details from the database
    """
    return User(user_id)

@login_manager.user_loader
def load_user(user_id):
    # get user information from db
    user = get_user(user_id)
    return user

@app.route("/", methods=["GET", "POST"])
def login():

    global user_id

    if request.method == "POST":

        user_id = request.form["name"]
        password = request.form["password"]

        # Send this information to the authentication module
        result = authenticate(user_id,password)

        if result == 'admin':
            user = User(user_id)
            login_user(user)
            print(get_enrolment_surveys(user_id, 'admin'))
            return redirect(url_for("dashboard"))
        elif result == 'staff':
            user = User(user_id)
            login_user(user)
            return redirect(url_for("staff_dash"))
        elif result == 'student':
            user = User(user_id)
            login_user(user)

            # gets the courses that student is enrolled in. Return value is in the form of a list.
            enrolments = get_student_enrolments(user_id)

             # get open surveys for particular course
            open_surveys = []

            return redirect(url_for("student_dash"))
        else:
            return render_template("login.html")

        return redirect(url_for("dashboard"))

    # Fill in databases
    # Possibly set a global flag to ensure that this only happens once
    fill_database()

    return render_template("login.html")


@app.route("/Dashboard", methods=["GET", "POST"])
@login_required
def dashboard():

    global user_id

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
            close_survey(f)

    return render_template("dashboard.html", surveys = get_enrolment_surveys(user_id, 'admin'))


@app.route("/Create", methods=["GET", "POST"])
def create():

    if request.method == "POST":

        # if admin wishes to cancel the creation of a survey
        if request.form["input"] == "1":
            return redirect(url_for("dashboard", created = get_survey_of_status('courses','review')))

        # when the admin chooses a offering period
        if request.form["input"] == "2":
            choice = 'offer'
            offering = request.form["offering"]


            c = get_courses()
            o = []

            course_name[:] = []
            course_name.append(offering)

            # Get all the courses offered in that period
            for i in c:
                if i[1] == offering:
                    o.append(i[0])

            return render_template("create.html", questions = get_admin_questions(), courses = get_courses(), offerings = get_offerings(), choice = 'offer', courseoff = '', offers = o)

        # When the admin submits a course name
        if request.form["input"] == "3":
            courseoff = 'course'
            course_name.insert(0, request.form["course"])

            return render_template("create.html", questions = get_admin_questions(), courses = get_courses(), offerings = get_offerings(), choice = 'offer', courseoff = 'course', offers = '')

        # When the admin submits the chosen questions
        if request.form["input"] == "4":

            # Check for existing survey or create new one
            if check_survey_status(course_name) != 'None':
                chosen_msg = msg[4]
                print(chosen_msg)
                return redirect(url_for("dashboard", created = get_survey_of_status('courses', 'review')))

            # Check which questions were submitted
            qus = request.form.getlist('check')
            print('qus = ', qus)
            create_survey(course_name,qus)
            chosen_msg = msg[3]
            print(chosen_msg)
            return redirect(url_for("dashboard", created = get_survey_of_status('courses','review'), msg = chosen_msg))

    return render_template("create.html", questions = get_admin_questions(), courses = get_courses(), offerings = get_offerings(), choice = '', offers = '')


@app.route("/Question", methods=["GET", "POST"])
@login_required
def question():

    if request.method == "POST":

        # BACK - Return to the dashboard
        if request.form["input"] == "1":
            return redirect(url_for("dashboard"))

        # ADD QUESTION
        if request.form["input"] == "2":
            return render_template("question.html", add_question = True, questions = get_admin_questions())

        # DELETE QUESTION
        if request.form["input"] == "3":
            return render_template("question.html", delete_question = True, questions = get_admin_questions())

        # CANCEL - Cancel the creation of the current question
        if request.form["input"] == "4":
            return render_template("question.html", questions = get_admin_questions())

        # Question has been entered
        if request.form["input"] == "5":

            # Collect the question text, response type and option
            qu = request.form["addq"]
            re = request.form["type"]
            op = request.form["option"]

            print(re)

            # Multiple choice question -> proceed to collect MC responses
            if re == "Multiple Choice":

                print("HEY")
                # Store the question details in a temporary session
                session['Temp_Question'] = [qu,re,op]
                return render_template("question.html", set_MC_resnum = True, questions = get_admin_questions())

            # Store text-response question in database
            else:
                add_question(qu,re,op,'None')
                return render_template("question.html", set_MC_resnum = False, questions = get_admin_questions())

        # Collect desired number of MC responses
        if request.form["input"] == "6":
            n = int(request.form["resnum"])
            l = session['Temp_Question']
            l.append(n)
            session['Temp_Question'] = l
            return render_template("question.html", MC_resnum = n, questions = get_admin_questions())

        # Store MC-response question in database
        if request.form["input"] == "7":

            # Retrieve temporary session data
            data = session['Temp_Question']

            # Get a list of the responses
            responses = []
            n = data[3]
            for i in range(1,n+1):
                responses.append(request.form[str(i)])

            # Remove temporary session data
            session.pop('Temp_Question', None)

            # Add the question to the database
            add_question(data[0],data[1],data[2],responses)

            return render_template("question.html", questions = get_admin_questions())

        if request.form["input"] == "8":

            q = request.form["delq"]
            delete_question(q)

            return render_template("question.html", questions = get_admin_questions())

    return render_template("question.html", questions = get_admin_questions())

@app.route("/Survey", methods=["GET", "POST"])
def survey():

    if request.method == "POST":

        if request.form["input"] == "0":
            return redirect(url_for("student_dash"))
        
        data = get_survey_data(clicked_survey[0])
        print('data = ', data)

        data_2 = []
        submitted = []

        for d in data:
            if d[0] not in data_2:
                data_2.append(d[0])

        print('data_2 = ',data_2)

        if request.form["input"] == "1":

            for q in get_admin_questions():
                if q[0] in data_2:
                    if q[1] == 'Multiple Choice':
                        i = request.form.getlist(q[0])
                        qi = q[0],'Multiple Choice',i
                        submitted.append(qi)

                    elif q[1] == 'Text':
                        i = request.form[q[0]]
                        qi = q[0],'Text',i
                        submitted.append(qi)
                print(submitted)

            submit_survey(user_id, clicked_survey[0], submitted)

            return redirect(url_for("complete"))

    return render_template("survey.html", course_name = clicked_survey, user = user_role, data = get_survey_data(clicked_survey[0]), cs_data = c_s_data)


@app.route("/Staff_Dash", methods=["GET", "POST"])
@login_required
def staff_dash():

    if request.method == "POST":
        if request.form["input"] == "1":
            return redirect(url_for("logout"))

        else:
            clicked_survey[:] = []                                  # resetting list
            c_s = request.form["input"]
            clicked_survey.append(request.form["input"])
            get_survey_data(c_s)                                    # gets data from selected course
            user_role[:] = []
            user_role.append('staff')

            # getting name of question
            c_s_data[:] = []
            for c in get_survey_data(c_s):
                if c[0] not in c_s_data:
                    c_s_data.append(c[0])

            return redirect(url_for("review"))

    return render_template("staff_dash.html", user = user_id, user_enrols = get_enrolment_surveys(user_id, 'staff'))

@app.route("/Student_Dash", methods=["GET", "POST"])
@login_required
def student_dash():

    if request.method == "POST":
        if request.form["input"] == "1":
            return redirect(url_for("logout"))

        else:
            clicked_survey[:] = []
            c_s = request.form["input"]
            print('clicked =', c_s)
            clicked_survey.append(c_s)
            get_survey_data(c_s)
            user_role[:] = []
            user_role.append('student')

            c_s_data[:] = []
            for c in get_survey_data(c_s):
                if c[0] not in c_s_data:
                    c_s_data.append(c[0])

            return redirect(url_for("survey"))

    return render_template("student_dash.html", user = user_id, enrolments = enrolments, surv = get_enrolment_surveys(user_id, 'student'))

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
def review():

    if request.method == "POST":

        if request.form["input"] == "0":
            return redirect(url_for("staff_dash"))

        if request.form["input"] == "1":
            d = clicked_survey[0]
            e = d.split('_')
            release_survey(e)
            return redirect(url_for("staff_dash"))

        else:
            add_q = request.form["input"]
            c_s_data.append(add_q)
            add_to_survey(clicked_survey[0],add_q)
            return redirect(url_for("review"))


    return render_template("review.html", course_name = clicked_survey, user = user_role, data = get_survey_data(clicked_survey[0]), cs_data = c_s_data, questions = get_admin_questions())

@app.route("/Metrics", methods=["GET", "POST"])
def metrics():

    if request.method == "POST":

        global view 
        global different
        different = []

        if request.form["input"] == "1":
            return redirect(url_for("dashboard"))

        elif request.form["input"] == "2":
            a = request.form["active"]
            view = survey_results(a)
            
            for v in view:
                if v[0] not in different:
                    different.append(v[0])

            #print('diff = ', different)

            return redirect(url_for("metrics2"))

        elif request.form["input"] == "3":
            c = request.form["closed"]
            view = survey_results(c)

            for v in view:
                if v[0] not in different:
                    different.append(v[0])

            #print('diff = ', different)

            return redirect(url_for("metrics2"))



    return render_template("metrics.html", results = get_enrolment_surveys(user_id, 'admin'))

@app.route("/Metrics2", methods=["GET", "POST"])
def metrics2():

    print('metrics2 view = ',view)

    if request.method == "POST":

        if request.form["input"] == "1":
            return redirect(url_for("metrics"))

    return render_template("metrics2.html", results = view, diff = different)