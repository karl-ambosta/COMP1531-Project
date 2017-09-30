from flask import Flask, redirect, render_template, request, url_for
from server import app, user_input
from classes import *
from reading_classes import *

admins = {}
flag = 0
msg = ['','Question Successfuly Added!', "Survey Successfuly Created!"]

@app.route("/", methods=["GET", "POST"])
def welcome():
    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]

        ad = Admin(name, email) # Create an admin object
        admins[0] = ad # Add the admin to a dictionary

        return redirect(url_for("dashboard"))

    return render_template("welcome.html")

@app.route("/Dashboard", methods=["GET", "POST"])
def dashboard():

    if request.method == "POST":

        if request.form["input"] == "1":
            return redirect(url_for("create"))
        elif request.form["input"] == "2":
            return redirect(url_for("question"))

    return render_template("dashboard.html", admin = admins[0].get_name())

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
def question():

    if request.method == "POST":

        # Return to the dashboard if the user wishes to Cancel
        if request.form["input"] == "1":
            return redirect(url_for("dashboard"))

        # Collect the question text from the form
        q = request.form["question"]

        # Collect the response text from the form
        responses = []
        res = request.form["responseA"]
        if res:
            responses.append(res)
        res = request.form["responseB"]
        if res:
            responses.append(res)
        res = request.form["responseC"]
        if res:
            responses.append(res)
        res = request.form["responseD"]
        if res:
            responses.append(res)

        # Add the questions and responses to the admin object
        admins[0].add_question(q,responses)

        return redirect(url_for("dashboard"))

    return render_template("question.html")

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

@app.route("/Complete", methods=["GET", "POST"])
def complete():

    return render_template("complete.html")

@app.route("/Nothing", methods=["GET", "POST"])
def nothing():

    return render_template("nothing.html")
