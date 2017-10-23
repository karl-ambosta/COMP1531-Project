import unittest
import os
from model import *
import sqlite3
from sqlalchemy import exc, orm
import warnings

class TestAddQuestion(unittest.TestCase):

    def setUp(self):
        self.database = Database()

    # Question name is not defined
    def test_add_question_no_name(self):
        q = Questions(name = None, types = 'Text', option = 'Mandatory', responses = None)
        with self.assertRaises(exc.IntegrityError):
            warnings.simplefilter("ignore")
            self.database.add_question(q)

    # Question type is not defined
    def test_add_question_no_type(self):
        q = Questions(name = 'Test question', types = None, option = 'Mandatory', responses = None)
        with self.assertRaises(exc.IntegrityError):
            warnings.simplefilter("ignore")
            self.database.add_question(q)

    # Question option is not defined
    def test_add_question_no_option(self):
        q = Questions(name = 'Test question', types = 'Text', option = None, responses = None)
        with self.assertRaises(exc.IntegrityError):
            warnings.simplefilter("ignore")
            self.database.add_question(q)

    # Multiple choice question has no specified responses
    def test_add_question_no_responses(self):
        q = Questions(name = 'Test question', types = 'Multiple Choice', option = 'Mandatory', responses = '')
        with self.assertRaises(ValueError):
            self.database.add_question(q)

    # Add a duplicate question
    def test_add_duplicate_question(self):
        q = Questions(name = 'Duplicate question', types = 'Text', option = 'Mandatory', responses = None)
        self.database.add_question(q)
        with self.assertRaises(exc.IntegrityError):
            q = Questions(name = 'Duplicate question', types = 'Text', option = 'Mandatory', responses = None)
            self.database.add_question(q)

    # Add a question
    def test_add_question(self):
        q = Questions(name = 'Test question', types = 'Text', option = 'Mandatory', responses = None)
        self.database.add_question(q)
        quest = self.database.get_question('Test question')
        self.assertEqual(quest.name, 'Test question')
        self.assertEqual(quest.types, 'Text')
        self.assertEqual(quest.option, 'Mandatory')
        self.assertEqual(quest.responses, None)

    def tearDown(self):
        os.remove('survey.db')

class TestAuthenticate(unittest.TestCase):

    def setUp(self):
        self.database = Database()
        self.database.populate_table()

    # Authenticate with invalid ID
    def test_auth_no_id(self):
        id = None
        password = 'pw'
        user = self.database.authenticate(id,password)
        self.assertEqual(user, None)

    # Authenticate with invalid password
    def test_auth_no_password(self):
        id = 50
        password = None
        user = self.database.authenticate(id,password)
        self.assertEqual(user, None)

    # Authenticate admin
    def test_auth_admin(self):
        id = 0
        password = 'admin'
        user = self.database.authenticate(id,password)
        self.assertEqual(user.get_id(), 0)
        self.assertEqual(user.get_role(), 'admin')

    # Authenticate staff
    def test_auth_staff(self):
        id = 50
        password = 'staff670'
        user = self.database.authenticate(id,password)
        self.assertEqual(user.get_id(), 50)
        self.assertEqual(user.get_role(), 'staff')

    # Authenticate student
    def test_auth_student(self):
        id = 100
        password = 'student228'
        user = self.database.authenticate(id,password)
        self.assertEqual(user.get_id(), 100)
        self.assertEqual(user.get_role(), 'student')

    def tearDown(self):
        os.remove('survey.db')        

if __name__=="__main__":
    unittest.main()
