from flask import Flask, redirect, render_template, request, url_for
from server import app, user_input
from classes import *

# Possibly include a global dictionary of admin users
admins = {}

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






