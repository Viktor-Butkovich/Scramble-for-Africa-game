def find_object_distance(first, second):
    '''
    Inputs:
        Two objects with int x and y attributes
    Outputs:
        Calculates and returns the distance between the x and y coordinates of each inputted object
    '''
    return((((first.x - second.x) ** 2) + ((first.y - second.y) ** 2)) ** 0.5)

def find_coordinate_distance(first, second):
    '''
    Inputs:
        Two tuples containing two int variables each representing coordinates
    Outputs:
        Calculates and returns the distance between the x and y coordinates from each inputted tuple
    '''
    first_x, first_y = first
    second_x, second_y = second
    return((((first_x - second_x) ** 2) + ((first_y - second_y) ** 2)) ** 0.5)

    
def remove_from_list(received_list, item_to_remove):
    '''
    Inputs:
        A list and a variable value or object
    Outputs:
        Returns the list with all instances of inputted variable value or object removed
    '''
    output_list = []
    for item in received_list:
        if not item == item_to_remove:
            output_list.append(item)
    return(output_list)

def toggle(variable):
    '''
    Inputs:
        A boolean variable
    Outputs:
        Returns the opposite of the inputted boolean's value
    '''
    if variable == True:
        return(False)
    elif variable == False:
        return(True)

def generate_article(word):
    '''
    Inputs:
        A string
    Outputs:
        Returns 'an' if the word starts with a vowel or 'a' if the word does not start with a vowel
    '''
    vowels = ['a', 'e', 'i', 'o', 'u']
    if word[0] in vowels:
        return('an')
    else:
        return('a')

def add_to_message(message, new):
    '''
    Inputs:
        Two strings
    Outputs:
        Returns a concatenation of the two strings
    '''
    return (message + new)
