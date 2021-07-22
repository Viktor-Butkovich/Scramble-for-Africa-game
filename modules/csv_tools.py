import csv

def read_csv(file_path):
    '''
    Reads in .csv file.
    Input: file path of .csv file as a string
    Output: List of strings containing contents of .csv file
    '''
    myList = []
    
    file = open(file_path, 'r')
    csv_reader = csv.reader(file)
    
    for row in csv_reader:
        myList.append(row)
    
    return myList

# To test:
#myTest = read_csv('../text/flavor_explorer.csv')
#for entry in myTest:
#    print(entry)
#print('end')