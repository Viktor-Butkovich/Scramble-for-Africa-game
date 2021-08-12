import csv

def read_csv(file_path):
    '''
    Input:
        file path of .csv file as a string
    Output:
        Reads in .csv file, returning a list of lists of 1 string each, with each string being a line of the .csv file
    '''
    
    line_list = []
    file = open(file_path, 'r')
    csv_reader = csv.reader(file)
    
    for current_line in csv_reader:
        line_list.append(current_line)
    
    return(line_list)
