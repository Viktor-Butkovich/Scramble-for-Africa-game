class global_manager_template():
    '''
    An object designed to be passed between functions and objects as a simpler alternative to passing each variable or object separately
    '''
    def __init__(self):#, global_dict):
        self.global_dict = {}#global_dict #dictionary with values in the format 'variable_name': variable_value
        
    def get(self, name):
        return(self.global_dict[name]) #variables in the dictionary are accessed with global_manager.get('variable_name')
    
    def set(self, name, value): #create a new dictionary value or change an existing one with global_manager.set('variable_name', new_variable_value)
        self.global_dict[name] = value

class input_manager_template():
    def __init__(self, global_manager):
        self.global_manager = global_manager
        self.previous_input = ''
        self.taking_input = False
        self.old_taking_input = self.taking_input
        self.stored_input = ''
        self.send_input_to = ''
        
    def check_for_input(self):
        if self.old_taking_input == True and self.taking_input == False: 
            return(True)
        else:
            return(False)
        
    def start_receiving_input(self, solicitant, message):
        text_tools.print_to_screen(message)
        self.send_input_to = solicitant
        self.taking_input = True
        
    def update_input(self):
        self.old_taking_input = self.taking_input
        
    def receive_input(self, received_input): #to do: add do something button for testing
        if self.send_input_to == 'do something':
            if received_input == 'done':
                self.global_manager.set('crashed', True)
            else:
                text_tools.print_to_screen("I didn't understand that.")
