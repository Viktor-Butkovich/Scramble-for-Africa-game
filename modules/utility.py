def find_object_distance(first, second):
    '''
    Input:
        Two objects with int x and y attributes
    Output:
        Calculates and returns the distance between the x and y coordinates of each inputted object
    '''
    return((((first.x - second.x) ** 2) + ((first.y - second.y) ** 2)) ** 0.5)

def find_coordinate_distance(first, second):
    '''
    Input:
        Two tuples containing two int variables each representing coordinates
    Output:
        Calculates and returns the distance between the x and y coordinates from each inputted tuple
    '''
    first_x, first_y = first
    second_x, second_y = second
    return((((first_x - second_x) ** 2) + ((first_y - second_y) ** 2)) ** 0.5)

    
def remove_from_list(received_list, item_to_remove):
    '''
    Input:
        A list and a variable value or object
    Output:
        Returns the list with all instances of inputted variable value or object removed
    '''
    output_list = []
    for item in received_list:
        if not item == item_to_remove:
            output_list.append(item)
    return(output_list)

def toggle(variable):
    '''
    Input:
        A boolean variable
    Output:
        Returns the opposite of the inputted boolean's value
    '''
    if variable == True:
        return(False)
    elif variable == False:
        return(True)

def generate_article(word):
    '''
    Input:
        A string
    Output:
        Returns 'an' if the word starts with a vowel or 'a' if the word does not start with a vowel
    '''
    vowels = ['a', 'e', 'i', 'o', 'u']
    exceptions = ['European', 'unit']
    if word[0] in vowels and (not word in exceptions):
        return('an')
    else:
        return('a')

def generate_plural(amount):
    '''
    Input:
        A string
    Output:
        Returns 'an' if the word starts with a vowel or 'a' if the word does not start with a vowel
    '''
    if amount == 1:
        return('')
    else:
        return('s')

def generate_capitalized_article(word):
    '''
    Input:
        A string
    Output:
        Returns 'An' if the word starts with a vowel or 'A' if the word does not start with a vowel
    '''
    vowels = ['a', 'e', 'i', 'o', 'u']
    exceptions = ['European', 'unit']
    if word[0] in vowels and (not word in exceptions):
        return('An')
    else:
        return('A')
    
def add_to_message(message, new):
    '''
    Input:
        Two strings
    Output:
        Returns a concatenation of the two strings
    '''
    return (message + new)
