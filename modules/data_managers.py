import random
from . import csv_tools

class global_manager_template():
    '''
    An object designed to manage a dictionary of shared variables and be passed between functions and objects as a simpler alternative to passing each variable or object separately
    '''
    def __init__(self):#, global_dict):
        '''
        Inputs:
            none
        '''
        self.global_dict = {}#global_dict #dictionary with values in the format 'variable_name': variable_value
        
    def get(self, name):
        '''
        Inputs:
            string name representing the name of an entry in this global_manager's dictionary
        Outputs:
            Returns the value corresponding to name's entry in this global_manager's dictionary
        '''
        return(self.global_dict[name]) #variables in the dictionary are accessed with global_manager.get('variable_name')
    
    def set(self, name, value): #create a new dictionary value or change an existing one with global_manager.set('variable_name', new_variable_value)
        '''
        Inputs:
            string name representing the name of an entry to create/replace in this global_manager's dictionary, variable representing the value to set this entry to
        Outputs:
            Creates/replaces an entry in this global_manager's dictionary based on the inputted name and value
        '''
        self.global_dict[name] = value

class input_manager_template():
    '''
    An object designed to manage the passing of typed input from the text box to different parts of the program
    '''
    def __init__(self, global_manager):
        '''
        Inputs:
            global_manager_template object
        '''
        self.global_manager = global_manager
        self.previous_input = ''
        self.taking_input = False
        self.old_taking_input = self.taking_input
        self.stored_input = ''
        self.send_input_to = ''
        
    def check_for_input(self):
        '''
        Inputs:
            None
        Outputs:
            Returns True if input was just being taken and is no longer being taken, showing that there is input ready. Otherwise, returns False.
        '''
        if self.old_taking_input == True and self.taking_input == False: 
            return(True)
        else:
            return(False)
        
    def start_receiving_input(self, solicitant, message):
        '''
        Inputs:
            string representing the part of the program to sent input to, string representing the prompt for the user to enter input
        Outputs:
            Displays the prompt for the user to enter input and prepares to receive input and send it to the part of the program requesting input
        '''
        text_tools.print_to_screen(message, self.global_manager)
        self.send_input_to = solicitant
        self.taking_input = True
        
    def update_input(self):
        '''
        Inputs:
            none
        Outputs:
            Updates whether the input_manager_template is currently taking input
        '''
        self.old_taking_input = self.taking_input
        
    def receive_input(self, received_input):
        '''
        Inputs:
            string representing the input entered by the user into the text box
        Outputs:
            Sends the inputted string to the part of the program that initially requested input
        '''
        if self.send_input_to == 'do something':
            if received_input == 'done':
                self.global_manager.set('crashed', True)
            else:
                text_tools.print_to_screen("I didn't understand that.")

class flavor_text_manager_template():
    '''
    An object designed to read in flavor text and manage it, distributing it to other parts of the program when requested
    '''
    def __init__(self, global_manager):
        '''
        Inputs:
            global_manager_template object
        '''
        self.global_manager = global_manager
        self.explorer_flavor_text_list = []
        current_flavor_text = csv_tools.read_csv('text/flavor_explorer.csv')
        for line in current_flavor_text: #each line is a list
            self.explorer_flavor_text_list.append(line[0])
        self.subject_dict = {}
        self.subject_dict['explorer'] = self.explorer_flavor_text_list
                
    def generate_flavor_text(self, subject):
        '''
        Inputs:
            string representing the type of flavor text to return
        Outputs:
            Returns a random flavor text statement based on the inputted string
        '''
        return(random.choice(self.subject_dict['explorer']))
