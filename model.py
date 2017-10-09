from flask_login import UserMixin

class User(UserMixin):

    def __init__(self, id):
        self.id = id

class quest():

    def __init__(self,q,t,o):
        self.qu = q
        self.type = t
        self.option = o
        self.responses = []

    def add_responses(self, r):
        self.responses = r # List of multiple choice responses

class survey():

    def __init__(self):
        self.name = n
        self.status