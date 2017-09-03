import csv

class Admin:

    def __init__(self, username, email):
        self._username = username
        self._email = email

    def get_name(self):
        return self._username

class Survey:

    def __init__(self, course):
        self._course = course
