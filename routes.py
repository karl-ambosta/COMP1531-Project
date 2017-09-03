from flask import Flask, redirect, render_template, request, url_for
from server import app, user_input
from classes import *

# Possibly include a global dictionary of admin users

@app.route("/", methods=["GET", "POST"])
def welcome():
    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]

        # Create an admin object


        return redirect(url_for("dashboard"))
    return render_template("welcome.html")

@app.route("/Dashboard", methods=["GET", "POST"])
def dashboard():

    if request.method == "POST":

        if request.form["input"] == "1":
            return redirect(url_for("create"))

    return render_template("dashboard.html")

@app.route("/Create", methods=["GET", "POST"])
def create():

    return render_template("create.html")
