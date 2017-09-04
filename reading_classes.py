import csv

def read_course():
    course_list = []
    with open('courses.csv','r') as csv_in:
	    reader = csv.reader(csv_in)
	    for row in reader:
	        course_list.append(row)
    return course_list
    
def write(question):
	with open('questions.csv','a') as csv_out:
	    writer = csv.writer(csv_out)
	    writer.writerow([question])

def read_question():
    question_list = []
    with open('questions.csv','r') as csv_in:
	    reader = csv.reader(csv_in)
	    for row in reader:
	        question_list.append(row)
    return question_list

def write_results(results):
	with open('results.csv','a') as csv_out:
	    writer = csv.writer(csv_out)
	    writer.writerow(results)