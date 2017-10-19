from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
import csv

# Create a database that stores data in the local directory's data.db file
engine = create_engine('sqlite:///survey.db.db')
Base = declarative_base()

# Define classes for each table in the database.
# Define attributes in each class to correspond to columns in table

# Passwords Table
class User(Base):

	__tablename__ = 'user'
	zid = Column(Integer, primary_key=True)
	password = Column(String, nullable = False)
	role = Column(String, nullable = False)

# Course Table
class Courses(Base):

	__tablename__ = 'courses'
	id = Column(Integer, primary_key=True)
	name = Column(String)
	offering = Column(String(10))
	status = Column(String)

# Enrolments table
class Enrolments(Base):

	__tablename__ = 'enrolments'
	id = Column(Integer, primary_key=True)
	user_id = Column(Integer, ForeignKey('user.zid'))
	user = relationship(User)
	course_name = Column(String)
	course_offering = Column(String)
	status = Column(String)
	# offer = relationship(Courses)

# Questions table
class Questions(Base):

	__tablename__ = 'questions'
	name = Column(String, primary_key=True)
	types = Column(String, nullable = False) # Multiple Choice or Text Based Response
	option = Column(String, nullable = False) # Mandatory or Optional Question.
	responses = Column(String) # The responses are for the multiple choice questions. Text questions have a blank response section.

# Survey table
class Surveys(Base):

	__tablename__ = 'surveys'
	id = Column(Integer, primary_key=True)
	name = Column(String)
	offering = Column(String)
	question_name = Column(String)

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
	# Add data to table
	def add_row(self, session, row):
		session.add(row)
		session.commit()
		session.close()

#####################################################################################################################################################
	# Delete data from table
	def delete_row(self, session, row):
		try:
			session.delete(row)
		except:
			pass
		session.commit()
		session.close()

#####################################################################################################################################################
	# Get question corresponding to specific question name
	def query_question(self, name):
		session = self.DBSession()
		question = session.query(Questions).filter(Questions.name == name).one()
		session.close()
		return item

#####################################################################################################################################################
	# Get user corressponding to specific user_id
	def query_user(self, user_id):
		session = self.DBSession()
		user = session.query(User).filter(User.id == user_id).one()
		session.close()
		if user is not None:
			return user
		else: return None

#####################################################################################################################################################
	# Adding question to question pool
	def add_question(self, name, types, option, responses):
		session = self.DBSession()
		question = Questions(name = name, types = types, option = option, responses = responses)
		self.add_row(session, question)

#####################################################################################################################################################
	# Deleting question from question pool
	def delete_question(self, name, types, option, responses):
		session = self.DBSession()
		question = Questions(name = name, types = types, option = option, responses = responses)
		self.delete_row(session, question)

#####################################################################################################################################################
	# Gather all question for admin ONLY
	def get_admin_questions(self):
		questions = []
		session = self.DBSession()
		for q in session.query(Questions).all():
			questions.append(q)

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
				if s not in enrol_survey_status:
					enrol_survey_status.append(s)

		# Gather staff/student enrolments and append to user_enrolments
		for u in session.query(Enrolments).filter(Enrolments.user_id == user):
			if (u[1],u[2]) not in user_enrolments:
				us = u[1],u[2]
				user_enrolments.append(us)

		# From the staff's enrolments, check for enrolled course surveys
		if role == 'staff':
			for w in session.query(Courses).filter(Courses.name == user_enrolments[0][0]).filter(Courses.offering == user_enrolments[0][1]):
				if (w[0],w[1]) not in read_enrols:
					ws = w[0],w[1]
					read_enrols.append(ws)
					enrol_survey_status.append(w)

		# From the student's enrolments, check for enrolled course surveys
		if role == 'student':
			for user in user_enrolments:
				for v in session.query(Courses).filter(Courses.name == user[0]).filter(Courses.offering == user[1]):
					if (v[0],v[1]) not in read_enrols:
						read_enrols.append((v[0],v[1]))
						enrol_survey_status(v)

		return enrol_survey_status

#####################################################################################################################################################
	# Gather all the different course offerings from the database
	def get_offerings(self):
		offerings = []
		session = self.DBSession()

		for c in session.query(Courses).all():
			if c[1] not in offerings:
				offerings.append(c[1])

		return offerings

#####################################################################################################################################################
	# Create a course survey, add the selected questions to Surveys and change it's status in Courses to 'review'
	def create_survey(self, name, offering, questions):
		session = self.DBSession()

		session.query(Courses).filter(Courses.name == name).filter(Courses.offering ==  offering).update(values = {Course.status:'review'})

		for q in questions:
			survey = Surveys(course_name = name, offering = offering, question_name = q[0])
			self.add_row(session, survey)

#####################################################################################################################################################
	# Check the status of a named survey
	def check_survey_status(self, name, offering):
		session = self.DBSession()

		# Check the status of course survey
		status = session.query(Courses).filter(Courses.name == name).filter(Courses.offering == offering).one()

		return status[0][2]

#####################################################################################################################################################
	# For each course that the student is enrolled in, this function collects the surveys of a
	# particular status i.e. for a student, will get 'active' and 'closed' surveys.
	def get_survey_status(self, course_name, course_offering, status):
		session = self.DBSession()
		surveys = []

		for s in session.query(Courses).filter(Courses.name == course_name).filter(Courses.offering == offering).filter(Courses.status == status).all():
			st.append(s)

		return st

#####################################################################################################################################################
   	# Get the enrolments of the student user
	def get_student_enrolments(self, user_id):
		enrolled = []
		already_read = []
		session = self.DBSession()

		for e in session.query(Enrolments).filter(Enrolments.id == user_id).all():
			if (e[1],e[2]) not in already_in:
				already_in.append((e[1],e[2]))
				enrolled.append(e)

		return enrolled

#####################################################################################################################################################
	# Gather all surveys of a particular status
	def get_survey_of_status(self, status):
		st = []
		session = self.DBSession()

		for s in session.query(Courses).filter(Courses.status == status).all():
			st.append(s)

		return st

#####################################################################################################################################################
	# Gather a list of the questions associated with the named survey, compare it to the questions in the Questions table and get question data
	def get_survey_data(self, course_name, course_offering):
		survey_questions = []
		questions_list = []
		text_questions = []
		session = self.DBSession()

		for s in session.query(Surveys).filter(Survey.name == course_name).filter(Survey.offering == course_offering):
			survey_questions.append(s[3])

		for quest in survey_questions:
			element = session.query(Questions).filter(Questions.name == quest).one()
			questions_list.append(element)

		return questions_list

#####################################################################################################################################################
	# Add questions to course survey
	def add_to_survey(self, survey_name, survey_offering, question):
		session = self.DBSession()

		add = Surveys(name = survey_name, offering = survey_offering, question_name = question)
		self.add_row(session, add)

#####################################################################################################################################################
	# Change the status of course survey to 'active' in Courses and 'incomplete' in Enrolments 
	def release_survey(self, course_name):
		session = self.DBSession()
		session.query(Courses).filter(Courses.name == course_name[0]).filter(Courses.offering ==  course_name[1]).update(values = {Course.status:'active'})
		session.query(Enrolments).filter(Enrolments.course_name == course_name[0]).filter(Enrolments.course_offering == course_name[1]).update(values = {Enrolments.status:'incomplete'})

#####################################################################################################################################################
	# Change the status of course survey to 'closed' 
	def close_survey(self, course_name):
		session = self.DBSession()
		session.query(Courses).filter(Courses.name == course_name[0]).filter(Courses.offering ==  course_name[1]).update(values = {Course.status:'closed'})

#####################################################################################################################################################
	# Submit responses to particular course survey and changes the status of the named survey in Enrolments to 'complete'
	def submit_survey(self, user_id, course_name, course_offering, submitted_responses):
		session = self.DBSession()
		
		# Change the status of the student's enrolment survey to complete to show that the student has completed the survey
		# And acts as an indicator so that they cannot resubmit the survey
		session.query(Enrolments).filter(Enrolments.user_id == user_id).filter(Enrolments.course_name == course_name).filter(Enrolments.course_offering == course_offering).update(values = {Enrolments.status:'complete'})

		for s in submitted_responses:
			submit = Responses(course_name = course_name, offering = course_offering, question = s[0], response = s[1])
			self.add_row(session, submit)

#####################################################################################################################################################
	# Gather survey results to display in metrics
	def survey_results(self, course_name, course_offering):
		results = []
		session = self.DBSession()
		for res in session.query(Responses).filter(Responses.course_name == course_name).filter(Responses.offering == course_offering):
			results.append(res)

		return results

#####################################################################################################################################################

	def populate_table(self):
		session = self.DBSession()

		with open('courses.csv','r') as csv_in:
			reader = csv.reader(csv_in)
			for row in reader:
				course = Courses(name = row[0], offering = row[1], status = 'None')
				self.add_row(session, course)

		with open('enrolments.csv','r') as csv_in:
			reader = csv.reader(csv_in)
			for row in reader:
				enrols = Enrolments(user_id = row[0], course_name = row[1], course_offering = row[2])
				self.add_row(session, enrols)

		with open('passwords.csv','r') as csv_in:
			reader = csv.reader(csv_in)
			for row in reader:
				user = User(zid = row[0], password = row[1], role = row[2])
				self.add_row(session, user)

#####################################################################################################################################################



# database = Database()
# try:
#	database.populate_table()
#except:
#	pass
#database.submit_survey('100', 'COMP9333', '17s2', [('What is your name?', 'Karl'), ('What is your course?', 'Comp1531')])
#try:
#	i = database.survey_results('COMP9333', '17s2')
#	for e in i:
#		print(e.course_name, e.offering, e.question, e.response)

#except Exception as e:
#	print(e)

#for q in database.get_admin_questions():
#		print(q.name, q.types, q.option, q.responses)

