def find_object_distance(first, second):
    '''takes objects with x and y attributes'''
    return((((first.x - second.x) ** 2) + ((first.y - second.y) ** 2)) ** 0.5)

def find_coordinate_distance(first, second):
    '''takes sets of coordinates'''
    first_x, first_y = first
    second_x, second_y = second
    return((((first_x - second_x) ** 2) + ((first_y - second_y) ** 2)) ** 0.5)

    
def remove_from_list(received_list, item_to_remove):
    output_list = []
    for item in received_list:
        if not item == item_to_remove:
            output_list.append(item)
    return(output_list)

def toggle(variable):
    if variable == True:
        return(False)
    elif variable == False:
        return(True)

def generate_article(word):
    vowels = ['a', 'e', 'i', 'o', 'u']
    if word[0] in vowels:
        return('an')
    else:
        return('a')

def add_to_message(message, new):
    return (message + new)
