from flask import Flask, redirect, render_template, request, url_for
from server import app, user_input
from classes import *

# Possibly include a global dictionary of admin users
admins = {}
names = ['q1','q2','q3']

@app.route("/", methods=["GET", "POST"])
def welcome():
    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]

        print(name)

        ad = Admin(name, email) # Create an admin object
        print(ad.get_name())
        admins[name] = ad # Add the admin to a dictionary

        #return redirect(url_for("dashboard", admin = ad))
        return redirect(url_for("dashboard"))
        #return redirect(url_for("dashboard", admin = ad.get_name()))
    return render_template("welcome.html")

@app.route("/Dashboard", methods=["GET", "POST"])
def dashboard():

    if request.method == "POST":

        if request.form["input"] == "1":
            return redirect(url_for("create"))
        elif request.form["input"] == "2":
            return redirect(url_for("question"))
        #elif request.form["input"] == "3":
            #return redirect(url_for("view"))

    return render_template("dashboard.html")

@app.route("/Create", methods=["GET", "POST"])
def create():

    return render_template("create.html")

@app.route("/Question", methods=["GET", "POST"])
def question():

    if request.method == "POST":

        # Return to the dashboard if the user wishes to Cancel
        if request.form["input"] == "1":
                return redirect(url_for("dashboard"))

        q = request.form["question"]
        a = request.form["responseA"]
        b = request.form["responseB"]
        c = request.form["responseC"]
        d = request.form["responseD"]
        # Add this data to the admin object

        return redirect(url_for("dashboard"))

    return render_template("question.html")

@app.route("/Survey", methods=["GET", "POST"])
def survey():

    global names

    if request.method == "POST":

        #result = request.form["{{name}}"]
        #if request.form["q1"] == 'q1':
        #   print("WORKING")

        # The following code verifies that we can get a list from checkbox answers
        answers = request.form.getlist("question")
        for response in answers:
            print(response)
            #print(answers[response])

    return render_template("survey.html", names = names)

'''

    Admin contains a list of active surveys
    Admin contains a dictionary of actual survey classes
    Admin contains a list of quesitons
    Admin contains a list of sample response


    Get the current survey from the admin class
        If there isn't one, print "NO SURVEY ACTIVE"
        Else, 

    Starting a survey
        Get the course name from admin.get_active_survey()
        We need a way of keeping track of what question the survey is up to
        Each time it is loaded, it needs a string of the question and list of the answer strings

'''
