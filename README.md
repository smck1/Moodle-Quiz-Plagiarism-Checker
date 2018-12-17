# Moodle Quiz Plagiarism Checker

This python script parses the downloaded Excel (XLSX) version of a Moodle quiz and checks it for potential plagiarism.
The user should select which question numbers should be checked, ideally only those which have open text answers. Multiple choices questions or questions with exact answers will create a lot of false positives.

Answers will still need to be checked manually, however this tool makes it easy to quickly assess responses for a large number of students.


## How does it work?
It compares the responses of each student with every other student to see if the text for each answer is similar. Students who have similar answers for a set of number of questions (defaults to 2) will be flagged up for manual inspection. The actual text comparison is achieved using the Cosine Similarity (https://en.wikipedia.org/wiki/Cosine_similarity) of the text, which doesn't take the order of words into account. The default similarity to flag a match is very high as it was intended for use with short answers. However if you want to use it on longer answers then I suggest tweaking the match sensitivity (see below).

## What does it output?
The script essentially prints out a list of student pairs, and their responses to the questions which were flagged as similar.
Student1's response is above Student2's, given in the order they are named. 
Mock output is provided below:

\-------------------------------------------------
Flagging students with 2 similar responses.
Response similarity threshold is set to 0.85
First response at index 9
\#### Student_name1
\#### Student_name1
\#### Student_name2
\---
q 1:
This answer is similar to the one below
This answer is similar to the one above
\---
q 4:
This answer is similar to the one below
This answer is similar to the one above
\---
q 10:
This answer is similar to the one below
This answer is similar to the one above
\-------------------------------------------------


## How do I run it?
The script is written in Python 3 and has two dependencies. Install the dependencies then run it as follows:

### Install Dependencies
pip install -r requirements.txt

### Run the Script
py -3 .\plague_checker.py 'path_to_test.xlsx' -questions 1,2,5,19

If you want to save it to a file, just add > outfile.txt at the end of the command.


## Optional Parameters

Several optional parameters are available to tweak the output if it's being too conservative/generous for your needs.

### Number of Questions (Question Threshold)
This can be tweaked by passing the argument --question_threshold or -qt followed by an integer. e.g.:
 
py -3 .\plague_checker.py 'path_to_test.xlsx' -questions 1,2,5,19 -qt 3

The value (3 in the example above) specifies the number of answers which should match between two students before they are flagged for potential plagiarism.

### Match Sensitivity (Similarity Threshold)
This can be modified using the --similarity_threshold or -st argument, with a floating point value to specifcy the match criteria.
Cosine similarity works with values between 0 and 1, where 0 represents no similarity, and 1 represents items which are identical.
Example usage:

py -3 .\plague_checker.py 'path_to_test.xlsx' -questions 1,2,5,19 -st 0.7

This sets the similarity threshold to 0.7 before two answers are considered to be a match. How this parameter is set will depend on the type of questions which are asked. Longer questions should use smaller values, while questions in the short answer format should use high thresholds (defaults to 0.85)

