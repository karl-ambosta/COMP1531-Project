from flask import Flask, redirect, render_template, request, url_for
from flask_login import LoginManager,login_user, current_user, login_required, logout_user
from model import User
from server import app,login_manager
from classes import *
from reading_classes import *
from authenticate import *
from database import *

admins = {}
flag = 0
msg = ['','Question Successfuly Added!', "Survey Successfuly Created!"]

user_id = -1



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
            return redirect(url_for("question_pool"))
        elif request.form["input"] == "4":
            return redirect(url_for("logout"))

    return render_template("dashboard.html")




@app.route("/Create", methods=["GET", "POST"])
def create():

    if request.method == "POST":

        course = request.form["course"]

        # Create a survey object
        s = Survey(course)

        # Retrieve questions
        qu = admins[0].get_questions()

        # Collect a list of all the selected questions
        indexes = request.form.getlist("question")
        selected = []
        for j in indexes:
            selected.append(qu[int(j)])

        # Retrieve responses
        re = admins[0].get_responses()

        # Create a list containing both questions and responses
        new = []
        for e in selected:
            print("E")
            print(e)
            # Find corresponding index of responses
            i = qu.index(e)
            new.append([e,re[i]])

        print(new)

        # Add the questions/responses to the survey
        s.add_questions(new)

        # Add the survey to the admin object
        admins[0].add_survey(course,s)

        return redirect(url_for("dashboard"))

    return render_template("create.html", questions = admins[0].get_questions(), courses = read_course())






@app.route("/Question", methods=["GET", "POST"])
@login_required
def question():

    if request.method == "POST":

        # Return to the dashboard if the user wishes to Cancel
        if request.form["input"] == "1":
            return redirect(url_for("dashboard"))

        # Collect the question text from the form
        q = request.form["question"]

        # Collect question type
        t = request.form["type"]

        # Send data to server
        add_question(q,t)

        return redirect(url_for("dashboard"))

    return render_template("question.html")






@app.route("/Question_Pool", methods=["GET", "POST"])
@login_required
def question_pool():

    if request.method == "POST":

        # Return to the dashboard if the user wishes to Return
        if request.form["input"] == "1":
            return redirect(url_for("dashboard"))

    questions = get_admin_questions()

    return render_template("view_questions.html", questions = questions)




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

    return render_template("survey.html", data = data, course = admins[0].get_active_survey())




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
