import pygame

def message_width(message, fontsize, font_name):
    '''
    Input:
        string representing a message that will be rendered, int representing the message's font size, string representing the name of the font being used
    Output:
        returns an int representing the width in pixels that the message would occupy if rendered with the inputted font size and font name
    '''
    current_font = pygame.font.SysFont(font_name, fontsize)
    text_width, text_height = current_font.size(message)
    return(text_width)


def get_input(solicitant, message, global_manager):
    '''
    Input:
        string representing the part of the program requesting input, string representing the displayed prompt for input, global_manager_template object
    Output:
        Tells the input manager to receive input that will display the inputted prompt and send the result to the part of the program requesting input
    '''
    global_manager.get('input_manager').start_receiving_input(solicitant, message)

def text(message, font, global_manager):
    '''
    Input:
        string representing the text that will be rendered, font object representing the font that will be used, global_manager_template object
    Output:
        Returns a rendered message based on the inputted font and message
    '''
    return(font.render(message, False, global_manager.get('color_dict')['black']))

def manage_text_list(text_list, max_length):
    '''
    Input:
        list of strings representing each line of text in the text box, int representing the number of lines the text box should have
    Output:
        Returns a version of the inputted list with older messages past the inputted length removed
    '''
    if len(text_list) > max_length:
        while not len(text_list) == max_length:
            text_list.pop(0)
    return(text_list)


def print_to_screen(input_message, global_manager):
    '''
    Input:
        string representing a line of text to add to the text box, global_manager_template object
    Output:
        Adds the inputted message to a new line of the text box
    '''
    global_manager.get('text_list').append(input_message)

    
def print_to_previous_message(message, global_manager):
    '''
    Input:
        string representing text to be added to the most recent line of the text box, global_manager_template object
    Output:
        Adds the inputted message to the most recent line of the text box
    '''
    global_manager.get('text_list')[-1] = global_manager.get('text_list')[-1] + message

    
def clear_message(global_manager):
    '''
    Input:
        global_manager_template object
    Output:
        Deletes the line of text currently being typed
    '''
    global_manager.set('message', '')
