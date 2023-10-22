from ...util import text_utility
import modules.constants.constants as constants
import modules.constants.flags as flags

class input_manager_template():
    '''
    Object designed to manage the passing of typed input from the text box to different parts of the program
    '''
    def __init__(self, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.global_manager = global_manager
        self.previous_input = ''
        self.taking_input = False
        self.old_taking_input = self.taking_input
        self.stored_input = ''
        self.send_input_to = ''
        
    def check_for_input(self):
        '''
        Description:
            Returns true if input was just being taken and is no longer being taken, showing that there is input ready. Otherwise, returns False.
        Input:
            None
        Output:
            boolean: True if input was just being taken and is no longer being taken, showing that there is input ready. Otherwise, returns False.
        '''
        if self.old_taking_input == True and self.taking_input == False: 
            return(True)
        else:
            return(False)
        
    def start_receiving_input(self, solicitant, message):
        '''
        Description:
            Displays the prompt for the user to enter input and prepares to receive input and send it to the part of the program requesting input
        Input:
            string solicitant: Represents the part of the program to send input to
            string message: Prompt given to the player to enter input
        Output:
            None
        '''
        text_utility.print_to_screen(message, self.global_manager)
        self.send_input_to = solicitant
        self.taking_input = True
        
    def update_input(self):
        '''
        Description:
            Updates whether this object is currently taking input
        Input:
            None
        Output:
            None
        '''
        self.old_taking_input = self.taking_input
        
    def receive_input(self, received_input):
        '''
        Description:
            Sends the inputted string to the part of the program that initially requested input
        Input:
            String received_input: Input entered by the user into the text box
        Output:
            None
        '''
        if self.send_input_to == 'do something':
            if received_input == 'done':
                self.flags.crashed = True
            else:
                text_utility.print_to_screen('I didn\'t understand that.')