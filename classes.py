import csv

class Survey:

    def __init__(self, course):
        self._course = course

    def add_question(self, q, responses):
    	self._questions.append(q)
    	self._responses.append(responses)





class Admin:

    def __init__(self, username, email):
        self._username = username
        self._email = email
        self._active_survey = 0
        self._questions = []
        self._responses = []

    def get_name(self):
        return self._username

    def add_question(self, q, responses):
    	self._questions.append(q)
    	self._responses.append(responses)

    def get_questions(self):
    	return self._questions

    def get_responses(self):
    	return self._responses

    def get_active_survey(self):
    	return self._active_survey

    def add_survey(self):
    	self._active_survey = 1
