import csv

def read_csv(file_path):
    '''
    Reads in .csv file.
    Input: file path of .csv file as a string
    Output: List of lists of 1 string containing contents of .csv file
    '''
    line_list = []
    
    file = open(file_path, 'r')
    csv_reader = csv.reader(file)
    
    for current_line in csv_reader:
        line_list.append(current_line)
    
    return line_list
