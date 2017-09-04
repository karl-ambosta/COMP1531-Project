from flask import Flask, redirect, render_template, request, url_for
from server import app, user_input
from classes import *
from reading_classes import *

# Possibly include a global dictionary of admin users
admins = {}
questions = ['q1','q2','q3']
responses = ['a','b','c','d']
message_flag = 0
msg = {'1': 'Question Successfuly Added!','2':"Survey Successfuly Created"}

@app.route("/", methods=["GET", "POST"])
def welcome():
    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]

        print(name)

        ad = Admin(name, email) # Create an admin object
        print(ad.get_name())
        admins[0] = ad # Add the admin to a dictionary

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

    return render_template("dashboard.html", admin = admins[0].get_name())

@app.route("/Create", methods=["GET", "POST"])
def create():

    return render_template("create.html")

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

        # TEMPORARILY CREATE A SURVEY FOR TESTING
        admins[0].add_survey()

        return redirect(url_for("dashboard"))

    return render_template("question.html")

@app.route("/Survey", methods=["GET", "POST"])
def survey():

    #Check that the admin has created a survey
    # If they have, then do the following

    # NEED TO ADD A CHECK FOR AN EXCEPTION: NO ADMINS IN DICTIONARY
    if admins[0].get_active_survey() == 0:
        return redirect(url_for("nothing"))

    # Get question data from the admin
    questions = admins[0].get_questions()
    responses = admins[0].get_responses()
    #global questions

    if request.method == "POST":

        # The following code verifies that we can get a list from checkbox answers
        #answers = request.form.getlist("question")
        #for response in answers:
        #    print(response)

        results = []

        for q in questions:

            # Add all multiple-choice responses to a list
            results.append(request.form[q])
            #result = [q, request.form[q],]
            print(q, request.form[q])
            #if request.form[q] == '1':
             #   print("WORKING")
              #  print(q)
        write_results(results)

        return redirect(url_for("complete"))

    return render_template("survey.html", questions = questions, responses = responses)

@app.route("/Complete", methods=["GET", "POST"])
def complete():

    return render_template("complete.html")

@app.route("/Nothing", methods=["GET", "POST"])
def nothing():

    return render_template("nothing.html")


