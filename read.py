import csv

def read_passwords():
    user_list = []
    with open('passwords.csv','r') as csv_in:
        reader = csv.reader(csv_in)
        for row in reader:
            user_list.append(row)
    return user_list

def read_courses():
    course_list = []
    with open('courses.csv','r') as csv_in:
        reader = csv.reader(csv_in)
        for row in reader:
            course_list.append(row)
    return course_list

def read_enrolments():
    enrolment_list = []
    with open('enrolments.csv','r') as csv_in:
        reader = csv.reader(csv_in)
        for row in reader:
            enrolment_list.append(row)
    return enrolment_list