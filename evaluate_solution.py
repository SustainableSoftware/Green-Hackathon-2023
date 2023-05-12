import sys
import subprocess
import os
import pandas as pd

# how to create a call to an external program '/Users/me/src/program' with arguments 'a.txt' and 'b.txt'
#cmd = ['/Users/me/src/program', 'a.txt', 'b.txt']

# --- IMPORTANT---:
# Make sure to change these lines (1-19), so they
# - execute your RP1 program and
# - we have the file name where RP1 program stores the predictions.

# our RP1 program is located in the same folder as this script.
# our test program is written in python3, is called 'raspberryPi1.py', and takes one input argument 'raspberryPi1.ini' (also located in this folder).
cmd = ['python3', 'raspberryPi1.py', 'raspberryPi1.ini']



# ---- The following code may not be changed ----
# your predictions should be put in a csv-file called 'result.csv' (located in the same folder as this script)
solution_file = 'result.csv'



def checkSentimentCorrectness(id, sentiment, checklistData):
    global correct
    global incorrect
    data = checklistData.loc[checklistData['id'] == id]
    if not data.empty:
        row = data.iloc[0]
        if row['sentiment'] == sentiment:
            correct += 1
            
def evaluate(checklist, solution):
    # Headers: id, sentiment
    checklist_data = pd.read_csv(checklist_file, delimiter=",", usecols=['id','sentiment'])
    solution_data = pd.read_csv(solution_file, delimiter=",", usecols=['id', 'sentiment'])

    solution_data['save_id'] = solution_data['id']
    checklist_data['save_id'] = checklist_data['id']
    solution_data_ID = solution_data.set_index('id')
    checklist_data_ID = checklist_data.set_index('id')
    solution_data_ID = solution_data_ID.sort_index()
    solution_data_ID_groupby_sentiment = solution_data_ID.groupby('sentiment')

    # find the number of correct positive sentiments and correct negative sentiments
    correct_solutions = {}

    test = 1
    for sentiment, solution_subset in solution_data_ID_groupby_sentiment:
        # extract the subset of checklist with the same IDs
        ind_list = list(solution_subset.index)
        checklist_subset = checklist_data_ID.iloc[ind_list]
        # check whether the predicted category is the same as the correct category
        correctness_of_answers = solution_subset.eq(checklist_subset).all(1)
        solution_subset['correctness'] = correctness_of_answers
        df_count = solution_subset['correctness'].value_counts()
        # store the number of correct predictions for this sentiment category
        correct_solutions[sentiment] = df_count[True]
    # find the total number of 1 sentiments and the total number of 0 sentiments
    checklist_count = checklist_data_ID['sentiment'].value_counts()
    correct_checklist = {0: checklist_count[0], 1: checklist_count[1]}

    # calculate the percentage of correct guesses for each category
    correct_0_percentage = correct_solutions[0] / correct_checklist[0]
    correct_1_percentage = correct_solutions[1] / correct_checklist[1]

    judgement = ""
    if (correct_0_percentage > 0.8) & (correct_1_percentage > 0.8):
        judgement = "\nThe solution is functional\n"
    else:
        judgement = "\nThe solution is not yet functional\n"

    print(judgement +
          f"you have correctly categorized: {correct_solutions[0]} out of {correct_checklist[0]} 0s. Correctness percentage: {correct_0_percentage}\n" +
          f"you have correctly categorized: {correct_solutions[1]} out of {correct_checklist[1]} 1s. Correctness percentage: {correct_1_percentage}\n"
          )

    #print('Rigtige: ' + str(correct) + ', forkerte: '+ str(incorrect) + ', dvs. '+ str(percentage) + '% rigtige!')

def run_RP1():
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    process.wait()
    for line in process.stdout:
        print(line)

if __name__ == '__main__':

    if len(sys.argv) > 2:
        print(f"Usage A: {sys.argv[1]} and {sys.argv[2]}")
        # -- for testing purposes only --
        # the program can be called where both the checklist file and the solution file are given as input
        # example:
        # '''
        # python3 evaluate_solution.py movie_dev_checklist.csv result.csv
        # '''
        checklist_file = sys.argv[1]
        solution_file = sys.argv[2]
        run_RP1()
        evaluate(checklist_file, solution_file)
    elif len(sys.argv) > 1:
        print(f"Usage B: {sys.argv[1]} and default {solution_file}")
        # checklist_file = 'movie_dev_checklist.csv'
        # -- for testing purposes only --
        # the program can be called where another checklist file is given as input, e.g,
        # '''
        # python3 evaluate_solution.py movie_dev_checklist.csv
        # '''
        # thus, if you provide movie_dev.csv as input to your RP1 program, then the above call will pre-test your
        # solution's functionality. Note that an evaluation using movie_dev_checklist may not give the same correctness
        # score as the evaluation we perform with movie_test and movie_test_checklist (not provided during development).
        checklist_file = sys.argv[1]
        run_RP1()
        evaluate(checklist_file, solution_file)
    else:
        checklist_file = 'movie_test_checklist.csv'
        print(f"Usage C: default {checklist_file} and default {solution_file}")
        # -- for official evaluation of your solution --
        # We will use this call when testing your correctness score and measuring your energy

        # IMPORTANT: Make sure to change the lines 1-19 according to your solution

        print('The standard files have been used for checking')
        print('Alt. Usage: python3 evaluate_solution.py <checklist with correct categories - f.x. id_and_sentiment_nine.csv> <your results - fx. result.csv>')


        run_RP1()
        evaluate(checklist_file, solution_file)
