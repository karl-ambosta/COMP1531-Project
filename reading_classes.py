import csv

def read():
    course_list = []
    with open('courses.csv','r') as csv_in:
	    reader = csv.reader(csv_in)
	    for row in reader:
	        course_list.append(row)
    return course_list
