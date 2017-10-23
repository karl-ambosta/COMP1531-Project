# Assignment Unit Testing

import unittest
import os
from Assignment_Class import *
import sqlite3
from sqlalchemy import exc, orm
import warnings

#database = Database()

class Test_Create_Survey(unittest.TestCase):
	
	def setUp(self):
		self.database = Database()
	
	def test_succesfully_create_survey(self):
		questions_list = ['Do you enjoy COMP1531?', 'How do you find the lectures?', 'Does your lecturer clearly explain content?']
		length = len(questions_list)
		self.database.create_survey(['COMP1531', '17s2'], ['Do you enjoy COMP1531?', 'How do you find the lectures?', 'Does your lecturer clearly explain content?'], '2018-01-01')
		data = self.database.query_survey('COMP1531', '17s2')
		self.assertEqual(len(data), length)
		
	def test_survey_with_no_questions(self):
		questions_list = []
		with self.assertRaises(ValueError):
			self.database.create_survey(['COMP1531', '17s2'], questions_list, '2017-10-29')

	def test_invalid_closing_date(self):
		td = '2012-09-28'
		questions_list = ['Do you enjoy COMP1531?', 'How do you find the lectures?', 'Does your lecturer clearly explain content?']
		with self.assertRaises(ValueError):
			self.database.create_survey(['COMP1531', '17s2'], questions_list, td)
		
	def tearDown(self):
		os.remove('survey.db')

class Test_Delete_Question(unittest.TestCase):
	
	def setUp(self):
		self.database = Database()
	
	def test_successfully_delete_question(self):
		q = Questions(name = 'What are your thoughts on the lectures', types = 'Text', option = 'Mandatory', responses = None)
		self.database.add_question(q)
		self.database.delete_question('What are your thoughts on the lectures')
		check = self.database.get_question('What are your thoughts on the lectures')
		self.assertEqual(check, None)
	
	def test_delete_question_not_present(self):
		q = Questions(name = 'What are your thoughts on the lectures', types = 'Text', option = 'Mandatory', responses = None)
		self.database.add_question(q)
		with self.assertRaises(ValueError):
			self.database.delete_question('How do you find COMP1531?')
	
	def tearDown(self):
		os.remove('survey.db')

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

class TestEnrolment(unittest.TestCase):

    def setUp(self):
        self.database = Database() 
        self.database.populate_table()

    # Test that student enrolment details are properly stores and queried
    def test_student_enrolment(self):
        enrols = self.database.get_enrolment_surveys(100, 'student')
        self.assertEqual(enrols[0][0],'COMP9333')
        self.assertEqual(enrols[0][1],'17s2')
        self.assertEqual(enrols[1][0],'COMP9334')
        self.assertEqual(enrols[1][1],'17s2')
        self.assertEqual(enrols[2][0],'COMP2911')
        self.assertEqual(enrols[2][1],'17s2')
        self.assertEqual(enrols[3][0],'COMP1000')
        self.assertEqual(enrols[3][1],'17s2')

    # Test that staff enrolment details are properly stores and queried
    def test_staff_enrolment(self):
        enrols = self.database.get_enrolment_surveys(50, 'staff')
        self.assertEqual(enrols[0][0],'COMP4931')
        self.assertEqual(enrols[0][1],'18s1')

    def tearDown(self):
        os.remove('survey.db')

if __name__ == '__main__':
	unittest.main()