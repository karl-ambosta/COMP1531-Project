import csv

def read_course():
    course_list = []
    with open('courses.csv','r') as csv_in:
        reader = csv.reader(csv_in)
        for row in reader:
            course_list.append(row)
    return course_list

def read_question():
    question_list = []
    with open('questions.csv','r') as csv_in:
        reader = csv.reader(csv_in)
        for row in reader:
            question_list.append(row)
    return question_list

def read_password(id, password):
    details = []
    with open('passwords.csv', 'r') as csv_in:
        reader = csv.reader(csv_in)
        for row in reader:
            if id in row:
                if password in row:
                    return row
    return None

def read_enrolments(id):
    enrolments = []
    with open('enrolments.csv', 'r') as csv_in:
        reader = csv.reader(csv_in)
        for row in reader:
            if id in row:
                enrolments.append(row[1])

    return enrolments

    
def write(question):
    with open('questions.csv','a') as csv_out:
        writer = csv.writer(csv_out)
        writer.writerow([question])


def write_results(results):
    with open('results.csv','a') as csv_out:
        writer = csv.writer(csv_out)
        writer.writerow(results)