from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
import csv
from datetime import *
from time import *

# Create a database that stores data in the local directory's data.db file
engine = create_engine('sqlite:///survey.db')
Base = declarative_base()

# Define classes for each table in the database.
# Define attributes in each class to correspond to columns in table

# Passwords Table
class User(Base):

	__tablename__ = 'user'
	zid = Column(Integer, primary_key=True)
	password = Column(String, nullable = False)
	role = Column(String, nullable = False)
	auth = Column(String, nullable = False)

	def get_id(self):
		return self.zid

	def get_role(self):
		return self.role

	# Flask login functions:
	
	def is_active(self):
		return True

	def is_anonymous(self):
		return False

	def get_id(self):
		return self.zid

	def is_authenticated(self):
		return self.auth

# Course Table
class Courses(Base):

	__tablename__ = 'courses'
	id = Column(Integer, primary_key=True)
	name = Column(String)
	offering = Column(String(10))
	status = Column(String)
	closing_date = Column(String)

	def get_name(self):
		return self.name

	def get_offering(self):
		return self.offering

# Enrolments table
class Enrolments(Base):

	__tablename__ = 'enrolments'
	id = Column(Integer, primary_key=True)
	user_id = Column(Integer, ForeignKey('user.zid'))
	user = relationship(User)
	course_name = Column(String)
	course_offering = Column(String)
	status = Column(String)

# Questions table
class Questions(Base):

	__tablename__ = 'questions'
	name = Column(String, primary_key=True)
	types = Column(String, nullable = False) # Multiple Choice or Text Based Response
	option = Column(String, nullable = False) # Mandatory or Optional Question.
	responses = Column(String) # The responses are for the multiple choice questions. Text questions have a blank response section.

	def get_question(self):
		return self.name

	def get_type(self):
		return self.types

	def get_option(self):
		return self.option

	def get_responses(self):
		return self.responses

# Survey table
class Surveys(Base):

	__tablename__ = 'surveys'
	id = Column(Integer, primary_key=True)
	name = Column(String)
	offering = Column(String)
	question_name = Column(String)
	added_by = Column(String, nullable=False)

class Responses(Base):

	__tablename__ = 'responses'
	id = Column(Integer, primary_key=True)
	course_name = Column(String)
	offering = Column(String)
	question = Column(String)
	response = Column(String)

class Database(object):

#####################################################################################################################################################
	# Create all tables in the engine. This is equivalent to "Create Table" statements in raw SQL.
	def __init__(self):
		self.engine = create_engine('sqlite:///survey.db')
		try:
			Base.metadata.create_all(self.engine)
		except:
			pass
		Base.metadata.bind = self.engine
		self.DBSession = sessionmaker(bind=self.engine)

#####################################################################################################################################################
	# return a specific user object given an id
	def get_user(self, user_id):
		session = self.DBSession()
		u = session.query(User).filter(User.zid == user_id).first()
		return u

#####################################################################################################################################################
	# Authenticate a user by checking the user's password
	def authenticate(self, user_id, password):
		session = self.DBSession()

		# Query the user from the database
		u = session.query(User).filter(User.zid == user_id).first()
		if u == None:
			return None
		elif u.password == password:
			return u
		else:
			return None

#####################################################################################################################################################
	# Gather surveys of a particular status
	def get_closed_survey(self):
		session = self.DBSession()
		return session.query(Courses).filter(Courses.status == 'closed').all()

	def get_review_survey(self):
		session = self.DBSession()
		return session.query(Courses).filter(Courses.status == 'review').all()

	def get_active_survey(self):
		session = self.DBSession()
		return session.query(Courses).filter(Courses.status == 'active').all()

	def get_all_questions(self):
		session = self.DBSession()
		return session.query(Questions).all()

#####################################################################################################################################################
	# Read from csv files and read them 
	def populate_table(self):
		session = self.DBSession()

		# Add courses details in the database
		i = 1
		with open('courses.csv','r') as csv_in:
			reader = csv.reader(csv_in)
			for row in reader:
				course = Courses(id = i, name = row[0], offering = row[1], status = 'None', closing_date = 'None')
				self.add_row(session, course)
				i += 1

		# Add staff/student enrolments in the database	
		with open('enrolments.csv','r') as csv_in:
			reader = csv.reader(csv_in)
			for row in reader:
				enrols = Enrolments(user_id = row[0], course_name = row[1], course_offering = row[2])
				self.add_row(session, enrols)

		# Add admin credentials in the database
		user = User(zid = '0', password = 'admin', role = 'admin', auth = False)
		self.add_row(session, user)

		# Add staff/student in the database	
		with open('passwords.csv','r') as csv_in:
			reader = csv.reader(csv_in)
			for row in reader:
				user = User(zid = row[0], password = row[1], role = row[2], auth = False)
				self.add_row(session, user)

#####################################################################################################################################################
	# Add data to table
	def add_row(self, session, row):
		session.add(row)
		session.commit()
		session.close()

#####################################################################################################################################################
	# Get survey corresponds to specified name
	def query_course_survey(self):
		session = self.DBSession()

		current = datetime.now()
		current.strftime("%Y-%m-%d")

		for course in session.query(Courses).all():
			
			if course.closing_date == 'None':
				print('no course survey for ', course.name, course.offering, course.status, course.closing_date)
				continue

			else:
				print('active course survey for ', course.name, course.offering, course.status, course.closing_date)
				td = datetime.strptime(course.closing_date, '%Y-%m-%d')
				print('current = ', current, 'td = ', td, 'current < td = ', current < td)

				if (current < td) == False:
					print('changing')
					session.query(Courses).filter(Courses.name == course.name).filter(Courses.offering ==  course.offering).update(values = {Courses.status:'closed'})
					print('changed')

		session.commit()

#####################################################################################################################################################
	# Query survey data
	def query_survey(self, name, offering):
		session = self.DBSession()
		q = session.query(Surveys).filter(Surveys.name == name).filter(Surveys.offering == offering).all()
		return q

#####################################################################################################################################################
	# Get multiple questions corresponding to specific question name
	def query_question(self, name):
		session = self.DBSession()
		data_list = []
		print('name = ', name)
		for q in name:
			for question in session.query(Questions).filter(Questions.name == q):
				data_list.append([question.name,question.types,question.responses])
		return data_list

#####################################################################################################################################################
	# Single question correspinding to specific name
	def get_question(self, name):
		session = self.DBSession()
		return session.query(Questions).filter(Questions.name == name).first()

#####################################################################################################################################################
	# Get user corressponding to specific user_id
	def query_user(self, user_id):
		session = self.DBSession()
		user = session.query(User).filter(User.zid == user_id).first()
		session.close()
		if user.zid is not None:
			return user.zid
		else: return None

#####################################################################################################################################################
	# Adding question to question pool
	def add_question(self, question):

		# Check that multiple choice questions have responses
		if question.get_type() == 'Multiple Choice':

			resp_list = question.get_responses().split(',')

			if not question.get_responses():
				raise ValueError('ERROR: No multiple choice responses entered')

			for r in resp_list:
				if not r:
					raise ValueError('ERROR: No multiple choice responses entered')

		session = self.DBSession()
		self.add_row(session, question)

#####################################################################################################################################################
	# Deleting question from question pool
	def delete_question(self, name):
		session = self.DBSession()
		delete_q = session.query(Questions).filter(Questions.name == name).first()
		if delete_q == None:
			raise ValueError('could not find name in question pool')
		session.delete(delete_q)
		session.commit()

#####################################################################################################################################################
	# Gather all question
	def get_admin_questions(self):
		questions = []
		session = self.DBSession()
		for q in session.query(Questions).all():
			questions.append([q.name, q.types, q.option, q.responses])

		return questions

#####################################################################################################################################################
	# Gather all courses
	def get_courses(self):
		courses = []
		session = self.DBSession()
		for c in session.query(Courses).all():
			courses.append(c)

		return courses

#####################################################################################################################################################	
	# Gather surveys dependent on type of user
	def get_enrolment_surveys(self, user_id, role):
		user_enrolments = []
		enrol_survey_status = []
		read_enrols = []
		session = self.DBSession()
		user = self.query_user(user_id)

		# If the user is an admin, gather all surveys
		if role == 'admin':
			for s in session.query(Courses).all():
				if (s.name,s.offering) not in enrol_survey_status:
					enrol_survey_status.append((s.name,s.offering))
			
			print(enrol_survey_status)
			return enrol_survey_status

		# Gather staff/student enrolments and append to user_enrolments
		for u in session.query(Enrolments).filter(Enrolments.user_id == user):
			if (u.course_name,u.course_offering) not in user_enrolments:
				us = u.course_name,u.course_offering
				user_enrolments.append(us)

		# From the staff's enrolments, check for enrolled course surveys
		if role == 'staff':
			for w in session.query(Courses).filter(Courses.name == user_enrolments[0][0]).filter(Courses.offering == user_enrolments[0][1]):
				if (w.name,w.offering) not in read_enrols:
					ws = w.name,w.offering
					read_enrols.append(ws)
					enrol_survey_status.append((w.name,w.offering,w.status,w.closing_date))

		# From the student's enrolments, check for enrolled course surveys
		if role == 'student':
			for user in user_enrolments:
				for v in session.query(Courses).filter(Courses.name == user[0]).filter(Courses.offering == user[1]):
					if (v.name,v.offering) not in read_enrols:
						read_enrols.append((v.name,v.offering))
						enrol_survey_status.append((v.name,v.offering,v.status,v.closing_date))

		print(enrol_survey_status)
		return enrol_survey_status

#####################################################################################################################################################
	# Gather all the different course offerings from the database
	def get_offerings(self):
		offerings = []
		session = self.DBSession()

		for c in session.query(Courses).all():
			if c.offering not in offerings:
				offerings.append(c.offering)

		return offerings

#####################################################################################################################################################
	# Create a course survey, add the selected questions to Surveys and change it's status in Courses to 'review'
	def create_survey(self, course_title, questions, closing_date):
		session = self.DBSession()
		
		if not questions:
			raise ValueError('No questions in survey')

		current = datetime.now()
		current.strftime("%Y-%m-%d")
		td = datetime.strptime(closing_date, '%Y-%m-%d')
		#chosen = closing_date.strftime('%Y-%m-%d')


		if (current > td) == True:
			raise ValueError('Invalid closing date. This date is in the past')

		session.query(Courses).filter(Courses.name == course_title[0]).filter(Courses.offering ==  course_title[1]).update(values = {Courses.status:'review',Courses.closing_date:closing_date})

		for q in questions:
			survey = Surveys(name = course_title[0], offering = course_title[1], question_name = q, added_by = 'admin')
			self.add_row(session, survey)

		session.commit()
	
#####################################################################################################################################################
	# Check the status of a named survey
	def check_survey_status(self, course_title):
		session = self.DBSession()

		# Check the status of course survey
		course = session.query(Courses).filter(Courses.name == course_title[0]).filter(Courses.offering == course_title[1]).first()

		return course.status

#####################################################################################################################################################
	# For each course that the student is enrolled in, this function collects the surveys of a
	# particular status i.e. for a student, will get 'active' and 'closed' surveys.
	def get_survey_status(self, course_name, course_offering, status):
		session = self.DBSession()
		surveys = []

		for s in session.query(Courses).filter(Courses.name == course_name).filter(Courses.offering == offering).filter(Courses.status == status).all():
			st.append([s.name,s.offering])

		return st

#####################################################################################################################################################
   	# Get the enrolments of the user
	def get_user_enrolments(self, zid):
		enrolled = []
		already_read = []
		session = self.DBSession()

		for e in session.query(Enrolments).filter(Enrolments.user_id == zid).all():
			if (e.course_name,e.course_offering) not in already_read:
				already_read.append((e.course_name,e.course_offering))
				enrolled.append((e.course_name,e.course_offering,e.status))

		return enrolled

#####################################################################################################################################################
	# Gather all surveys of a particular status
	def get_survey_of_status(self, status):
		st = []
		session = self.DBSession()

		for s in session.query(Courses).filter(Courses.status == status).all():
			if [s.name, s.offering] not in st:
				st.append([s.name, s.offering, s.closing_date])

		return st

#####################################################################################################################################################
	# Gather a list of the questions associated with the named survey, compare it to the questions in the Questions table and get question data
	def get_survey_data(self, course_title):
		survey_questions = []
		questions_list = []
		text_questions = []
		session = self.DBSession()
		try:
			course = course_title.split('_')
		except:
			course = course_title

		for s in session.query(Surveys).filter(Surveys.name == course[0]).filter(Surveys.offering == course[1]):
			survey_questions.append((s.question_name,s.added_by))

		for quest in survey_questions:
			element = session.query(Questions).filter(Questions.name == quest[0]).one()
			questions_list.append([element.name,element.types,element.responses,quest[1]])

		return questions_list

#####################################################################################################################################################
	# Add questions to course survey
	def add_to_survey(self, survey_title, question):
		session = self.DBSession()
		survey = survey_title.split('_')

		add = Surveys(name = survey[0], offering = survey[1], question_name = question, added_by = 'staff')
		self.add_row(session, add)

#####################################################################################################################################################
	# Add questions to course survey
	def delete_from_survey(self, survey_title, question):
		session = self.DBSession()
		survey = survey_title.split('_')

		delete = session.query(Surveys).filter(Surveys.name == survey[0]).filter(Surveys.offering == survey[1]).filter(Surveys.question_name == question).first()
		session.delete(delete)
		session.commit()
#####################################################################################################################################################
	# Change the status of course survey to 'active' in Courses and 'incomplete' in Enrolments 
	def release_survey(self, course_name):
		session = self.DBSession()
		session.query(Courses).filter(Courses.name == course_name[0]).filter(Courses.offering ==  course_name[1]).update(values = {Courses.status:'active'})
		session.query(Enrolments).filter(Enrolments.course_name == course_name[0]).filter(Enrolments.course_offering == course_name[1]).update(values = {Enrolments.status:'incomplete'})
		session.commit()

#####################################################################################################################################################
	# Change the status of course survey to 'closed' 
	def close_survey(self, course_name):
		session = self.DBSession()
		session.query(Courses).filter(Courses.name == course_name[0]).filter(Courses.offering ==  course_name[1]).update(values = {Courses.status:'closed'})
		session.commit()

#####################################################################################################################################################
	# Submit responses to particular course survey and changes the status of the named survey in Enrolments to 'complete'
	def submit_survey(self, user_id, course_title, submitted_responses):
		session = self.DBSession()
		course = course_title.split('_')
		
		# Change the status of the student's enrolment survey to complete to show that the student has completed the survey
		# And acts as an indicator so that they cannot resubmit the survey
		session.query(Enrolments).filter(Enrolments.user_id == user_id).filter(Enrolments.course_name == course[0]).filter(Enrolments.course_offering == course[1]).update(values = {Enrolments.status:'complete'})


		for s in submitted_responses:
			q = session.query(Questions).filter(Questions.name== s[0]).first()
			if q.types == 'Multiple Choice':
				submit = Responses(course_name = course[0], offering = course[1], question = s[0], response = s[1][0])
			else :
				submit = Responses(course_name = course[0], offering = course[1], question = s[0], response = s[1])
			
			self.add_row(session, submit)

		session.commit()

#####################################################################################################################################################
	# Gather survey results to display in metrics
	def survey_results(self, course_name):
		results = []
		session = self.DBSession()
		course = course_name.split('_')

		for res in session.query(Responses).filter(Responses.course_name == course[0]).filter(Responses.offering == course[1]):
			print(res.question,res.response)
			results.append([res.question,res.response])

		return results

#####################################################################################################################################################
