#### Author: Sean McKeown
#### Date: 17/12/18
#### Python Version 3
#### Requirements:
#       xlrd (https://pypi.org/project/xlrd/)
#       textdistance (https://pypi.org/project/textdistance/)

import argparse
import textdistance
from sys import argv
from xlrd import open_workbook, XLRDError


# note: on moodle quizzes the first response starts at column 9a
#       (other coluns have student information, test time, etc.)
# E.g.: ['Surname', 'First name', 'Email address', 'Username', 'State',
#        'Started on', 'Completed', 'Time taken', 'Grade/20.00', 'Response 1',
#        'Response 2', 'Response 3', 'Response 4', 'Response 5', 'Response 6',
#        'Response 7', 'Response 8', 'Response 9', 'Response 10']

# This is probably the case for all moodle quizzes, but the script should get
# the index of the first "Response" column, regardless.


DEFAULT_QT = 2
DEFAULT_ST = 0.85



parser = argparse.ArgumentParser(description="""
This script checks text questions in moodle quizzes for their cosine similarity for easy plagiarism detection.\n
The moodle responses should be downloaded to an excel file for parsing.\n
The user then selects which questions should be included in the comparison, as
multiple choice questions will result in many responses with identical text.
Ideally only long or short open question formats should be included.
If no question numbers are specified then all questions will be compared.
(This will be a mess if there are multiple choice or answers with exact values
- it's better to only select questions which have a reasonable expecation of different answers.)
""")
#parser.add_argument('alg', help="")
parser.add_argument('excelpath', help="Path to the excel file containing the quiz responses")
parser.add_argument('--questions', '-q', type=str, help='Select the questions to include in the comparison. \
                    This should be a comma separated list of numbers, e.g.: 1,3,5,6 with no spaces.')
parser.add_argument('--question_threshold', '-qt', type=int, help=f'The number of questions with similar answers required to flag two students.\
                    e.g. if -t is set to 2, then 2 similar answers will flag two students for inspection. Defaults to {DEFAULT_QT}')
parser.add_argument('--similarity_threshold', '-st', type=float, help=f'The similarity value used to flag a match between two responses.\
                    Specified as a floating point value - defaults to {DEFAULT_ST}. \n \
                    For short answer format where many of the same words are expected, set this pretty high, try around 0.8/0.85.\n \
                    For longer questions with varied answers, try lower thresholds (0.5, or experiment a bit)')


args = parser.parse_args()

# Get the question numbers, if any
if not args.questions:
    print("No questions specified. Comparing all answers.\
          \nNote: This may result in false positives if multiple choice questions are utilised.")
    questions = False
else:
    try:
        questions = [int(x) for x in args.questions.split(",")]
    except ValueError:
        print("Error: --questions values must be integer values only. e.g.: 1,2,6.\nAborting.")
        exit(-1)

if not args.question_threshold:
    print (f"No question threshold specified - defaulting to {DEFAULT_QT} to flag similar students.")
    threshold = DEFAULT_QT
else:
    print (f"Flagging students with {args.question_threshold} similar responses.")
    threshold = args.question_threshold

if not args.similarity_threshold:
    print (f"No similarity threshold specified, default to {DEFAULT_ST}")
    sim_threshold = DEFAULT_ST
else:
    print (f"Response similarity threshold is set to {args.similarity_threshold}")
    sim_threshold = args.similarity_threshold



# Attempt to read the excel file to process
try:
    wb = open_workbook(args.excelpath)
except XLRDError:
    print(f"Invalid file type for {args.excelpath}. Must be a valid XLSX file.")
except FileNotFoundError:
    print(f"Input file {args.excelpath} NOT FOUND.")
except Exception as inex:
    print("Print an error occurred when reading the input file:")
    print(f"{inex}")


# Read the input file.
for s in wb.sheets():
    #print 'Sheet:',s.name
    values = []
    for row in range(s.nrows):
        col_value = []
        for col in range(s.ncols):
            value  = (s.cell(row,col).value)
            try : value = str(int(value))
            except : pass
            col_value.append(value)
        values.append(col_value)

# Get the offsets of the first response column
first_response_index = False
num_cols = len(values[0]) # values[0] is the header row
for ind in range(num_cols):
    #print (values[0][ind], ind)
    if values[0][ind].startswith("Response"):
        first_response_index = ind
        break

# Check to see if any of the columns had "Response" in the title
if isinstance(first_response_index, bool):
    print ("""Didn't find any columns titled "Response".\n Aborting.""")
    exit(-1)
else:
    print (f"First response at index {ind}")

print ("\n")

# Adjust question response indexes.
# If the first response is on column 9, then Question 1 is at index 9.
# 1 is subtracted because Response columns start at 1, not 0.

if questions == False:
    # Handle the case where all questions are considered.
    question_inds = [x for x in range(first_response_index, num_cols)]
else:
    # Get the indexes of specified questions.
    question_inds = [x-1+first_response_index for x in questions]



# For each specified question - compare each student response to all others (pairwise)
# Flag up students who have args.threshold similar responses.
count= 1 # the number of students processed - used to stop repeat comparisons
for student in values[1:]: # skip the header row
    for student2 in values[count+1:]:   # count+1 to skip header
        if student != student2: # avoid comparing the same student at the end
            matches = []
            for q in question_inds:
                if student[q] != "-": # skip empty questions
                    if textdistance.cosine.normalized_similarity(student[q], student2[q]) > sim_threshold:
                        matches.append((q, student[q], student2[q]))
            if len(matches) > threshold:
                name1 = f"{student[1]} {student[0]}"
                name2 = f"{student2[1]} {student2[0]}"
                print (f"#### {name1}\n#### {name2}")
                #print (f"Similarity found for students {name1} and {name2}")
                for m in matches:
                    print ("---")
                    print (f"q {m[0]}:")
                    print (m[1])
                    print (m[2])
                print ("\n\n")
    count +=1

print ("Operation complete.")
