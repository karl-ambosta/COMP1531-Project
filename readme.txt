____________________________

Section 1: MODULES
____________________________

flask:                      Flask, redirect, render_template, request, url_for, session
flask_login:                LoginManager,login_user, current_user, login_required, logout_user
sql_alchemy:                Column, ForeignKey, Integer, String, create_engine, exec, orm
sqlalchemy.ext.declarative: declarative_base
sqlalchemy.orm:             relationship, sessionmaker
flask_bootstrap:            Bootstrap
flask_wtf:                  FlaskForm
wtform:                     StrignField, PasswordField, BooleanField
wtforms.validatiors:        InputRequired
sqlite3

____________________________

Section 2: RUN PROJECT
____________________________


First, create the survey.db database by running: 
                            python3 init_db.py

Then, run the project with: python3 run.py
Home page URL:              http://127.0.0.1:5000/

____________________________

Section 3: TESTS
____________________________


Run all tests with:         python3 tests.py
Notes:                      The tests may take as long as 1.5 minutes to complete

Test names:                 TestAddQuestion.test_add_question_no_name
                            TestAddQuestion.test_add_question_no_type
                            TestAddQuestion.test_add_question_no_option
                            TestAddQuestion.test_add_question_no_responses
                            TestAddQuestion.test_add_duplicate_question
                            TestAddQuestion.test_add_question

                            TestAuthenticate.test_auth_no_id
                            TestAuthenticate.test_auth_no_password
                            TestAuthenticate.test_auth_admin
                            TestAuthenticate.test_auth_staff
                            TestAuthenticate.test_auth_student

                            TestEnrolment.test_student_enrolment
                            TestEnrolment.test_staff_enrolment

                            Test_Create_Survey.test_succesfully_create_survey
                            Test_Create_Survey.test_survey_with_no_questions
                            Test_Create_Survey.test_invalid_closing_date

                            Test_Delete_Question.test_successfully_delete_question
                            Test_Delete_Question.test_delete_question_not_present
