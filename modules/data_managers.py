import random
from . import csv_tools
from . import notifications
from . import choice_notifications
from . import scaling

class global_manager_template():
    '''
    An object designed to manage a dictionary of shared variables and be passed between functions and objects as a simpler alternative to passing each variable or object separately
    '''
    def __init__(self):
        '''
        Input:
            none
        '''
        self.global_dict = {}
        
    def get(self, name):
        '''
        Input:
            string name representing the name of an entry in this global_manager's dictionary
        Output:
            Returns the value corresponding to name's entry in this global_manager's dictionary
        '''
        return(self.global_dict[name])
    
    def set(self, name, value):
        '''
        Input:
            string name representing the name of an entry to create/replace in this global_manager's dictionary, variable representing the value to set this entry to
        Output:
            Creates/replaces an entry in this global_manager's dictionary based on the inputted name and value
        '''
        self.global_dict[name] = value

class input_manager_template():
    '''
    An object designed to manage the passing of typed input from the text box to different parts of the program
    '''
    def __init__(self, global_manager):
        '''
        Input:
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
        Input:
            None
        Output:
            Returns True if input was just being taken and is no longer being taken, showing that there is input ready. Otherwise, returns False.
        '''
        if self.old_taking_input == True and self.taking_input == False: 
            return(True)
        else:
            return(False)
        
    def start_receiving_input(self, solicitant, message):
        '''
        Input:
            string representing the part of the program to sent input to, string representing the prompt for the user to enter input
        Output:
            Displays the prompt for the user to enter input and prepares to receive input and send it to the part of the program requesting input
        '''
        text_tools.print_to_screen(message, self.global_manager)
        self.send_input_to = solicitant
        self.taking_input = True
        
    def update_input(self):
        '''
        Input:
            none
        Output:
            Updates whether the input_manager_template is currently taking input
        '''
        self.old_taking_input = self.taking_input
        
    def receive_input(self, received_input):
        '''
        Input:
            string representing the input entered by the user into the text box
        Output:
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
        Input:
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
        Input:
            string representing the type of flavor text to return
        Output:
            Returns a random flavor text statement based on the inputted string
        '''
        return(random.choice(self.subject_dict['explorer']))

class value_tracker():
    def __init__(self, value_key, initial_value, global_manager):
        self.global_manager = global_manager
        self.global_manager.set(value_key, initial_value)
        self.value_label = 'none'
        self.value_key = value_key

    def get(self):
        return(self.global_manager.get(self.value_key))

    def change(self, value_change):
        self.global_manager.set(self.value_key, self.get() + value_change)
        if not self.value_label == 'none':
            self.value_label.update_label(self.get())
    
    def set(self, new_value):
        self.global_manager.set(self.value_key, initial_value)
        if not self.value_label == 'none':
            self.value_label.update_label(self.get())

class money_tracker(value_tracker):
    def __init__(self, initial_value, global_manager):
        super().__init__('money', initial_value, global_manager)

    def change(self, value_change):
        super().change(value_change)
        if self.get() < 0:
            self.global_manager.set('crashed', True)
            #print("You do not have enough money to continue running your company. GAME OVER")

    def set(self, new_value):
        super().set(new_value)
        if self.get() < 0:
            self.global_manager.set('crashed', True)
            #print("You do not have enough money to continue running your company. GAME OVER")

class notification_manager_template():
    def __init__(self, global_manager):
        self.notification_queue = []
        self.notification_type_queue = []
        self.choice_notification_choices_queue = []
        self.choice_notification_info_dict_queue = []
        self.global_manager = global_manager
        self.update_notification_layout()

    def update_notification_layout(self):
        self.notification_width = 500
        self.notification_height = 500
        self.notification_y = 236
        if self.global_manager.get('current_game_mode') in ['strategic', 'none']: #move notifications out of way of minimap on strategic mode or during setup
            self.notification_x = (scaling.unscale_width(self.global_manager.get('minimap_grid').origin_x, self.global_manager) - (self.notification_width + 40))
        else: #show notifications in center on europe mode
            self.notification_x = 610
            
    def notification_to_front(self, message):
        '''
        Input:
            string from the notification_queue representing the text of the new notification, global_manager_template object
        Output:
            Displays a new notification with text matching the inputted string. The type of notification is determined by first item of the notification_type_queue, a list of strings corresponding to the notification_queue.
        '''
        self.update_notification_layout()
        notification_type = self.notification_type_queue.pop(0)
        if notification_type == 'roll':
            new_notification = notifications.dice_rolling_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width, self.global_manager),
                scaling.scale_height(self.notification_height, self.global_manager), ['strategic', 'europe'], 'misc/default_notification.png', message, self.global_manager)
            
            for current_die in self.global_manager.get('dice_list'):
                current_die.start_rolling()

        elif notification_type == 'trade':
            new_notification = notifications.trade_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width, self.global_manager),
                scaling.scale_height(self.notification_height, self.global_manager), ['strategic', 'europe'], 'misc/default_notification.png', message, False, False, self.global_manager)

        elif notification_type == 'final_trade': #removes dice when clicked
            new_notification = notifications.trade_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width, self.global_manager),
                scaling.scale_height(self.notification_height, self.global_manager), ['strategic', 'europe'], 'misc/default_notification.png', message, True, False, self.global_manager)

        elif notification_type == 'commodity_trade': #gives commodity when clicked
            new_notification = notifications.trade_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width, self.global_manager),
                scaling.scale_height(self.notification_height, self.global_manager), ['strategic', 'europe'], 'misc/default_notification.png', message, False, True, self.global_manager)
                
        elif notification_type == 'exploration':
            new_notification = notifications.exploration_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width, self.global_manager),
                scaling.scale_height(self.notification_height, self.global_manager), ['strategic', 'europe'], 'misc/default_notification.png', message, False, self.global_manager)
            
        elif notification_type == 'final_exploration':
            new_notification = notifications.exploration_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width, self.global_manager),
                scaling.scale_height(self.notification_height, self.global_manager), ['strategic', 'europe'], 'misc/default_notification.png', message, True, self.global_manager)
            
        elif notification_type == 'choice':
            choice_notification_choices = self.choice_notification_choices_queue.pop(0)
            choice_notification_info_dict = self.choice_notification_info_dict_queue.pop(0)
            new_notification = choice_notifications.choice_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width, self.global_manager),
                scaling.scale_height(self.notification_height, self.global_manager), ['strategic', 'europe'], 'misc/default_notification.png', message, choice_notification_choices, choice_notification_info_dict, self.global_manager)

        else:
            new_notification = notifications.notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width, self.global_manager),
                scaling.scale_height(self.notification_height, self.global_manager), ['strategic', 'europe'], 'misc/default_notification.png', message, self.global_manager)
                #coordinates, ideal_width, minimum_height, showing, modes, image, message
    
