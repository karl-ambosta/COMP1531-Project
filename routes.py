from flask import Flask, redirect, render_template, request, url_for
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
course_name = []
choice = ''
resnums = 0
name = []


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
            return redirect(url_for("dashboard"))
        elif result == 'staff':
            user = User(user_id)
            login_user(user)
            return redirect(url_for("staff_dash"))
        elif result == 'student':
            user = User(user_id)
            login_user(user)
            return redirect(url_for("student_dash"))
        else:
            return render_template("login.html")

        ##################################################
        # DO NOT NEED
        ad = Admin(user_id, email) # Create an admin object
        admins[0] = ad # Add the admin to a dictionary
        ##################################################

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
            return redirect(url_for("logout"))

    return render_template("dashboard.html", created = get_survey_status('review'))


@app.route("/Create", methods=["GET", "POST"])
def create():

    if request.method == "POST":

        # if admin wishes to cancel the creation of a survey
        if request.form["input"] == "1":
            return redirect(url_for("dashboard", created = get_survey_status('review')))

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
                return redirect(url_for("dashboard", created = get_survey_status('review')))

            # Check which questions were submitted
            qus = request.form.getlist('check')
            print('qus = ',qus)
            create_survey(course_name,qus)
            chosen_msg = msg[3]
            print(chosen_msg)
            return redirect(url_for("dashboard", created = get_survey_status('review'), msg = chosen_msg))

    return render_template("create.html", questions = get_admin_questions(), courses = get_courses(), offerings = get_offerings(), choice = '', offers = '')


@app.route("/Question", methods=["GET", "POST"])
@login_required
def question():

    if request.method == "POST":

        # Return to the dashboard if the user wishes to Cancel
        if request.form["input"] == "1":
            return redirect(url_for("dashboard"))

        # If the user wishes to add a question
        if request.form["input"] == "2":
            choice = 'add'
            return render_template("question.html", choice = choice, questions = get_admin_questions())

        # If the user wishes to delete a question
        if request.form["input"] == "3":
            choice = 'delete'
            return render_template("question.html", choice = choice, questions = get_admin_questions())

        # After the user has cancelled the adding question process
        if request.form["input"] == "4":
            return redirect(url_for("question", choice = '', questions = get_admin_questions()))

        # After the user has chosen the question type
        if request.form["input"] == "5": 
            
            # Collect chosen question name and type
            t = request.form["type"]
            q = request.form["addq"]

            if t == '':
                print('no type input')

            if q == '':
                print('no question input')

            for quest in get_admin_questions():
                if quest[0] == q:
                    print('if')
                    return render_template("question.html", choice = 'add', questions = get_admin_questions(), msg = msg[2])
            # ADD QUESTION TO DATABASE
            if t == 'Multiple Choice':
                choice = 'add'
                name[:] = []
                name.append(request.form["addq"])
                return render_template("question.html", choice = 'add', response = 'MC', questions = get_admin_questions(), msg = msg[1])
            
            add_question(q,t)

            return redirect(url_for("question", choice = '', questions = get_admin_questions()))

        if request.form["input"] == "6":
            global resnums
            resnums = request.form["resnum"]
            try:
                int(resnums)
                return render_template("question.html", choice = 'add', response = 'MC', options = 'options', resnums = int(resnums), questions = get_admin_questions())
            except ValueError:
                return render_template("question.html", choice = 'add', response = 'MC', questions = get_admin_questions())

            
        if request.form["input"] == "7":
            add_question(name[0], 'Multiple Choice')
            return redirect(url_for("question", choice = '', questions = get_admin_questions()))

        if request.form["input"] == "8":
            delq = request.form["delq"]
            delete_question(delq)
            return redirect(url_for("question", choice = '', questions = get_admin_questions()))

        return redirect(url_for("dashboard"))

    return render_template("question.html", choice = '', questions = get_admin_questions())


@app.route("/Survey", methods=["GET", "POST"])
def survey():

    # Check that the admin has created a survey
    # NEED TO ADD A CHECK FOR AN EXCEPTION: NO ADMINS IN DICTIONARY
    if admins[0].get_active_survey() == 0:
        return redirect(url_for("nothing"))

    # Get question data from the admin
    data = admins[0].get_survey(admins[0].get_active_survey()).get_q()

    if request.method == "POST":

        # Extract the survey reponses
        responses = []
        for d in data:
            responses.append(d[1])

        # Collect the survey results
        results = []
        for d in range(len(data)):
            i = request.form[str(d)]
            results.append(responses[d][int(i)])

        write_results(results)

        return redirect(url_for("complete"))

    return render_template("survey.html", data = data)




@app.route("/Staff_Dash", methods=["GET", "POST"])
@login_required
def staff_dash():

    if request.method == "POST":
        if request.form["input"] == "1":
            return redirect(url_for("logout"))

    return render_template("staff_dash.html")

@app.route("/Student_Dash", methods=["GET", "POST"])
@login_required
def student_dash():

    if request.method == "POST":
        if request.form["input"] == "1":
            return redirect(url_for("logout"))

    return render_template("student_dash.html")

@app.route('/logout')
def logout():
    global user_id
    user_id = -1
    logout_user()
    return redirect(url_for('login'))


# Miscellaneous Survey Pages

@app.route("/Complete", methods=["GET", "POST"])
def complete():

    return render_template("complete.html")

@app.route("/Nothing", methods=["GET", "POST"])
def nothing():

    return render_template("nothing.html")
