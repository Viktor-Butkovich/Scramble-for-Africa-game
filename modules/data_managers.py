#Contains functionality for objects that manage notifications, variables, files, etc.

import random
import pygame

from . import csv_tools
from . import notifications
from . import choice_notifications
from . import action_notifications
from . import scaling
from . import text_tools
from . import events

class global_manager_template():
    '''
    Object designed to manage a dictionary of shared variables and be passed between functions and objects as a simpler alternative to passing each variable or object separately
    '''
    def __init__(self):
        '''
        Description:
            Initializes this object
        Input:
            None
        Output:
            None
        '''
        self.global_dict = {}
        
    def get(self, name):
        '''
        Description:
            Returns the value in this object's dictionary corresponding to the inputted key
        Input:
            string name: Name of a key in this object's dictionary
        Output:
            any type: The value corresponding to the inputted key's entry in this object's dictionary
        '''
        return(self.global_dict[name])
    
    def set(self, name, value):
        '''
        Description:
            Sets or initializes the inputted value for the inputted key in this object's dictionary
        Input:
            string name: Name of the key in this object's dictionary to initialize/modify
            any type value: Value corresponding to the new/modified key
        Output:
            None
        '''
        self.global_dict[name] = value

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
        text_tools.print_to_screen(message, self.global_manager)
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
                self.global_manager.set('crashed', True)
            else:
                text_tools.print_to_screen('I didn\'t understand that.')

class effect_manager_template():
    '''
    Object that controls global effects
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
        self.possible_effects = []
        self.active_effects = []

    def __str__(self):
        '''
        Description:
            Returns text for a description of this object when printed
        Input:
            None
        Output:
            string: Returns text to print
        '''
        text = 'Active effects: '
        for current_effect in self.active_effects:
            text += '\n    ' + current_effect.__str__()
        return(text)

    def effect_active(self, effect_type):
        '''
        Description:
            Finds and returns whether any effect of the inputted type is active
        Input:
            string effect_type: Type of effect to check for
        Output:
            boolean: Returns whether any effect of the inputted type is active
        '''
        for current_effect in self.active_effects:
            if current_effect.effect_type == effect_type:
                return(True)
        return(False)

    def set_effect(self, effect_type, new_status):
        '''
        Description:
            Finds and returns whether any effect of the inputted type is active
        Input:
            string effect_type: Type of effect to check for
        Output:
            boolean: Returns whether any effect of the inputted type is active
        '''
        for current_effect in self.possible_effects:
            if current_effect.effect_type == effect_type:
                if new_status == True:
                    current_effect.apply()
                else:
                    current_effect.remove()

class flavor_text_manager_template():
    '''
    Object that reads flavor text from .csv files and distributes it to other parts of the program when requested
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
        self.subject_dict = {}
        self.set_flavor_text('exploration', 'text/explorer.csv')
        self.set_flavor_text('advertising_campaign', 'text/advertising.csv')
        self.set_flavor_text('minister_first_names', 'text/default.csv')
        self.set_flavor_text('minister_particles', 'text/default.csv')
        self.set_flavor_text('minister_last_names', 'text/default.csv')
        self.allow_particles = False
                
    def set_flavor_text(self, topic, file):
        '''
        Description:
            Sets this flavor text manager's list of flavor text for the inputted topic to the contents of the inputted csv file
        Input:
            string topic: Topic for the flavor text to set, like 'minister_first_names'
            string file: File to set flavor text to, like 'text/flavor_minister_first_names.csv'
        Output:
            None
        '''
        flavor_text_list = []
        current_flavor_text = csv_tools.read_csv(file)
        for line in current_flavor_text: #each line is a list
            flavor_text_list.append(line[0])
        self.subject_dict[topic] = flavor_text_list

    def generate_substituted_flavor_text(self, subject, replace_char, replace_with):
        '''
        Description:
            Returns a random flavor text statement based on the inputted string, with all instances of replace_char replaced with replace_with
        Input:
            string subject: Represents the type of flavor text to return
        Output:
            string: Random flavor text statement of the inputted subject
        '''
        base_text = random.choice(self.subject_dict[subject])
        return_text = ''
        for current_character in base_text:
            if current_character == replace_char:
                return_text += replace_with
            else:
                return_text += current_character
        return(return_text)

    def generate_substituted_indexed_flavor_text(self, subject, replace_char, replace_with):
        '''
        Description:
            Returns a random flavor text statement based on the inputted string, with all instances of replace_char replaced with replace_with
        Input:
            string subject: Represents the type of flavor text to return
        Output:
            string, int tuple: Random flavor text statement of the inputted subject, followed by the index in the flavor text list of the outputted flavor text
        '''
        base_text = random.choice(self.subject_dict[subject])
        index = self.subject_dict[subject].index(base_text)
        return_text = ''
        for current_character in base_text:
            if current_character == replace_char:
                return_text += replace_with
            else:
                return_text += current_character
        return((return_text, index))


    def generate_flavor_text(self, subject):
        '''
        Description:
            Returns a random flavor text statement based on the inputted string
        Input:
            string subject: Represents the type of flavor text to return
        Output:
            string: Random flavor text statement of the inputted subject
        '''
        return(random.choice(self.subject_dict[subject]))

    def generate_minister_name(self, background):
        '''
        Description:
            Generates and returns a random combination of minister first and last names
        Input:
            None
        Output:
            string: Returns a random combination of minister first and last names
        '''
        if self.global_manager.get('current_country') == self.global_manager.get('Belgium'):
            self.allow_particles = True
            if random.randrange(1, 7) >= 4:
                self.set_flavor_text('minister_first_names', 'text/names/dutch_first_names.csv')
                self.set_flavor_text('minister_last_names', 'text/names/dutch_last_names.csv')
                self.set_flavor_text('minister_particles', 'text/names/dutch_particles.csv')
                self.allow_double_last_names = False
            else:
                self.set_flavor_text('minister_first_names', 'text/names/french_first_names.csv')
                self.set_flavor_text('minister_last_names', 'text/names/french_last_names.csv')
                self.set_flavor_text('minister_particles', 'text/names/french_particles.csv')
                self.allow_double_last_names = True

        first_name = self.generate_flavor_text('minister_first_names')
        titles = ['Duke', 'Marquess', 'Earl', 'Viscount', 'Baron', 'Sir', 'Prince', 'Lord', 
                    'Duc', 'Marquis', 'Count', 'Vicomte', 'Chevalier', 'Écuyer',
                    'Duque', 'Marquês', 'Infante', 'Visconde', 'Barão', 'Conde', 'Dom', 'Fidalgo',
                    'Herzog', 'Markgraf', 'Landgraf', 'Pfalzgraf', 'Reichsgraf', 'Burggraf', 'Reichsfürst', 'Graf', 'Freiherr', 'Herr',
                    'Principe', 'Duca', 'Marchese', 'Conte', 'Visconte', 'Barone', 'Nobile', 'Cavaliere', 'Patrizio'                  
                ]
        if self.global_manager.get('current_country') == self.global_manager.get('Germany'): #Most German nobility had von particle but no inherited title
            if background == 'royal heir' or (background == 'aristocrat' and random.randrange(1, 7) >= 5):
                while not first_name in titles:
                    first_name = self.generate_flavor_text('minister_first_names')
            else:
                while first_name in titles:
                    first_name = self.generate_flavor_text('minister_first_names')
        else:
            if background in ['royal heir', 'aristocrat']:
                while not first_name in titles:
                    first_name = self.generate_flavor_text('minister_first_names')
            else:
                while first_name in titles:
                    first_name = self.generate_flavor_text('minister_first_names')
        name = first_name + ' '
        if self.allow_particles:
            if self.aristocratic_particles:
                if background in ['royal heir', 'aristocrat'] and self.aristocratic_particles:
                    name += self.generate_flavor_text('minister_particles')
            elif random.randrange(1, 7) >= 4:
                name += self.generate_flavor_text('minister_particles')
        last_name = self.generate_flavor_text('minister_last_names')

        name += last_name
        if self.allow_double_last_names and random.randrange(1, 7) >= 5:
            second_last_name = self.generate_flavor_text('minister_last_names')
            while second_last_name == last_name:
                second_last_name = self.generate_flavor_text('minister_last_names')
            name += '-' + second_last_name
        return(name)

class value_tracker():
    '''
    Object that controls the value of a certain variable
    '''
    def __init__(self, value_key, initial_value, min_value, max_value, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            string value_key: Key used to access this tracker's variable in the global manager
            any type initial_value: Value that this tracker's variable is set to when initialized
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.global_manager = global_manager
        self.global_manager.set(value_key, initial_value)
        self.value_label = 'none'
        self.value_key = value_key
        self.min_value = min_value
        self.max_value = max_value

    def get(self):
        '''
        Description:
            Returns the value of this tracker's variable
        Input:
            None
        Output:
            any type: Value of this tracker's variable
        '''
        return(self.global_manager.get(self.value_key))

    def change(self, value_change):
        '''
        Description:
            Changes the value of this tracker's variable by the inputted amount. Only works if this tracker's variable is a type that can be added to, like int, float, or string
        Input:
            various types value_change: Amount that this tracker's variable is changed. Must be the same type as this tracker's variable
        Output:
            None
        '''
        #self.global_manager.set(self.value_key, self.get() + value_change)
        self.set(self.get() + value_change)
        if not self.value_label == 'none':
            self.value_label.update_label(self.get())
    
    def set(self, new_value):
        '''
        Description:
            Sets the value of this tracker's variable to the inputted amount
        Input:
            any type value_change: Value that this tracker's variable is set to
        Output:
            None
        '''
        self.global_manager.set(self.value_key, new_value)
        if not self.min_value == 'none':
            if self.get() < self.min_value:
                self.global_manager.set(self.value_key, self.min_value)
        if not self.max_value == 'none':
            if self.get() > self.max_value:
                self.global_manager.set(self.value_key, self.max_value)
        if not self.value_label == 'none':
            self.value_label.update_label(self.get())

class public_opinion_tracker(value_tracker):
    '''
    Value tracker that tracks public opinion
    '''
    def change(self, value_change):
        '''
        Description:
            Changes the value of this tracker's variable by the inputted amount. Only works if this tracker's variable is a type that can be added to, like int, float, or string
        Input:
            various types value_change: Amount that this tracker's variable is changed. Must be the same type as this tracker's variable
        Output:
            None
        '''
        super().change(value_change)
        self.global_manager.get('money_label').check_for_updates()

class money_tracker(value_tracker):
    '''
    Value tracker that tracks money and causes the game to be lost when money runs out
    '''
    def __init__(self, initial_value, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            any type initial_value: Value that the money variable is set to when initialized
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.transaction_history = {}
        self.transaction_types = global_manager.get('transaction_types')
        self.reset_transaction_history()
        super().__init__('money', initial_value, 'none', 'none', global_manager)

    def reset_transaction_history(self):
        '''
        Description:
            Resets the stored transactions from the last turn, allowing new transactions to be recorded for the current turn's financial report
        Input:
            None
        Output:
            None
        '''
        self.transaction_history = {}
        for current_transaction_type in self.transaction_types:
            self.transaction_history[current_transaction_type] = 0

    def change(self, value_change, change_type = 'misc.'):
        '''
        Description:
            Changes the money variable by the inputted amount
        Input:
            int value_change: Amount that the money variable is changed
        Output:
            None
        '''
        if change_type == 'misc.':
            if value_change > 0:
                change_type = 'misc_revenue'
            else:
                change_type = 'misc_expenses'
        self.transaction_history[change_type] += value_change
        if not value_change == 0:
            if abs(value_change) < 15:
                self.global_manager.get('sound_manager').play_sound('coins_1')
            else:
                self.global_manager.get('sound_manager').play_sound('coins_2')
        super().change(value_change)

    def set(self, new_value):
        '''
        Description:
            Sets the money variable to the inputted amount
        Input:
            int value_change: Value that the money variable is set to
        Output:
            None
        '''
        super().set(round(new_value, 2))

    def prepare_financial_report(self):
        '''
        Description:
            Creates and formats the text for a financial report based on the last turn's transactions
        Input:
            None
        Output:
            string: Formatted financial report text with /n being a new line
        '''
        notification_text = 'Financial report: /n /n'
        notification_text += 'Revenue: /n'
        total_revenue = 0
        for transaction_type in self.transaction_types:
            if self.transaction_history[transaction_type] > 0:
                notification_text += '  ' + self.global_manager.get('transaction_descriptions')[transaction_type].capitalize() + ': ' + str(self.transaction_history[transaction_type]) + ' /n'
                total_revenue += self.transaction_history[transaction_type]
        if total_revenue == 0:
            notification_text += '  None /n'
        
        notification_text += '/nExpenses: /n'
        total_expenses = 0
        for transaction_type in self.transaction_types:
            if self.transaction_history[transaction_type] < 0:
                #if transaction_type == 'misc. expenses':
                #    notification_text += '  Misc: ' + str(self.transaction_history[transaction_type]) + ' /n'
                #else:
                notification_text += '  ' + self.global_manager.get('transaction_descriptions')[transaction_type].capitalize() + ': ' + str(self.transaction_history[transaction_type]) + ' /n'
                total_expenses += self.transaction_history[transaction_type]
        if total_expenses == 0:
            notification_text += '  None /n'
        notification_text += ' /n'
        notification_text += 'Total revenue: ' + str(round(total_revenue, 2)) + ' /n'
        notification_text += 'Total expenses: ' + str(round(total_expenses, 2)) + ' /n'
        notification_text += 'Total profit: ' + str(round(total_revenue + total_expenses, 2)) + ' /n'
        return(notification_text)
                    
class notification_manager_template():
    '''
    Object that controls the displaying of notifications
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
        self.notification_queue = []
        self.notification_type_queue = []
        self.notification_dice_queue = []
        self.choice_notification_choices_queue = []
        self.choice_notification_info_dict_queue = []
        self.minister_message_queue = []
        self.global_manager = global_manager
        self.update_notification_layout()
        self.notification_modes = ['strategic', 'europe', 'ministers', 'trial', 'main_menu', 'new_game_setup']

    def update_notification_layout(self, notification_height = 0):
        '''
        Description:
            Changes where notifications are displayed depending on the current game mode to avoid blocking relevant information. Also changes the height of the notification based on how much text it contains
        Input:
            int notification_height = 0: Height in pixels of the notification text. If the notification text height is greater than the default notification height, the notification will scale its height to the text
        Output:
            None
        '''
        self.notification_width = 500
        self.notification_height = 300 #300 #500#600
        self.notification_y = 500#236#186
        #height_difference = notification_height - self.notification_height
        #if height_difference > 0: #if notification height greater than default notification height
        #    self.notification_y -= (height_difference / 2) #lower by half of height change
        #    self.notification_height += height_difference #increase height by height change
            #should change top and bottom locations while keeping same center
        if self.global_manager.get('current_game_mode') in ['strategic', 'none']: #move notifications out of way of minimap on strategic mode or during setup
            self.notification_x = self.global_manager.get('minimap_grid_origin_x') - (self.notification_width + 40)
        else: #show notifications in center on europe mode
            self.notification_x = 610
        #self.notification_height = 300
        if notification_height > self.notification_height:
            self.notification_height = notification_height
        self.notification_y -= self.notification_height / 2

    def format_message(self, message):
        new_message = []
        next_line = ''
        next_word = ''
        font_size = 25
        font_name = self.global_manager.get('font_name')
        for index in range(len(message)):
            if not ((not (index + 2) > len(message) and message[index] + message[index + 1]) == '/n'): #don't add if /n
                if not (index > 0 and message[index - 1] + message[index] == '/n'): #if on n after /, skip
                    next_word += message[index]
            if message[index] == ' ':
                if text_tools.message_width(next_line + next_word, font_size, font_name) > self.notification_width:
                    new_message.append(next_line)
                    next_line = ''
                next_line += next_word
                next_word = ''
            elif (not (index + 2) > len(message) and message[index] + message[index + 1]) == '/n': #don't check for /n if at last index
                new_message.append(next_line)
                next_line = ''
                next_line += next_word
                next_word = ''
        if text_tools.message_width(next_line + next_word, font_size, font_name) > self.notification_width:
            new_message.append(next_line)
            next_line = ''
        next_line += next_word
        new_message.append(next_line)
        #new_height = len(new_message) * font_size #scaling.scale_height(25, self.global_manager) #font size
        #print(len(new_message))
        return(new_message)
        #if new_height > self.minimum_height:
        #    self.height = new_height
    '''
    def get_notification_height(self, notification_text):
        
        Description:
            Returns the height in pixels of the inputted text if it were put in a notification
        Input:
            string notification_text: Text that will appear on the notification with lines separated by /n
        Output:
            int: height in pixels of the inputted text if it were put in a notification
        
        new_message = []
        next_line = ''
        next_word = ''
        font_size = 25 #scaling.scale_height(25, self.global_manager) #self.global_manager.get('font_size') #25
        font_name = self.global_manager.get('font_name')
        font = pygame.font.SysFont(font_name, font_size)
        for index in range(len(notification_text)):
            if not ((not (index + 2) > len(notification_text) and notification_text[index] + notification_text[index + 1]) == '/n'): #don't add if /n
                if not (index > 0 and notification_text[index - 1] + notification_text[index] == '/n'): #if on n after /, skip
                    next_word += notification_text[index]
            if notification_text[index] == ' ':
                if text_tools.message_width(next_line + next_word, font_size, font_name) > self.notification_width:
                    new_message.append(next_line)
                    next_line = ''
                next_line += next_word
                next_word = ''
            elif (not (index + 2) > len(notification_text) and notification_text[index] + notification_text[index + 1]) == '/n': #don't check for /n if at last index
                new_message.append(next_line)
                next_line = ''
                next_line += next_word
                next_word = ''
        if text_tools.message_width(next_line + next_word, font_size, font_name) > self.notification_width:
            new_message.append(next_line)
            next_line = ''
        next_line += next_word
        new_message.append(next_line)
        new_message.append('Click to remove this notification.')
        return(len(new_message) * font_size)#self.message = new_message
    '''
    def notification_to_front(self, message):
        '''
        Description:
            Displays a new notification with text matching the inputted string and a type based on what is in the front of this object's notification type queue
        Input:
            string message: The text to put in the displayed notification
        Output:
            None
        '''
        height = len(self.format_message(message)) * (self.global_manager.get('default_font_size') + 10)
        #print(height)
        #self.update_notification_layout(self.get_notification_height(message))
        self.update_notification_layout(height)

        notification_type = self.notification_type_queue.pop(0)
        notification_dice = self.notification_dice_queue.pop(0) #number of dice of selected mob to show when notification is visible
        if notification_type == 'roll':
            new_notification = action_notifications.dice_rolling_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width, self.global_manager),
                scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, notification_dice, self.global_manager)
            
            for current_die in self.global_manager.get('dice_list'):
                current_die.start_rolling()

        elif notification_type in ['stop_trade', 'stop_trade_attacked', 'trade', 'trade_promotion', 'final_trade', 'successful_commodity_trade', 'failed_commodity_trade']:
            is_last = False
            commodity_trade = False
            commodity_trade_type = notification_type #for successful/failed_commodity_trade
            stops_trade = False
            dies = False
            if notification_type == 'stop_trade':
                stops_trade = True
            elif notification_type == 'stop_trade_attacked':
                stops_trade = True
                dies = True
            elif notification_type == 'final_trade':
                is_last = True
            elif notification_type in ['successful_commodity_trade', 'failed_commodity_trade']:
                commodity_trade = True
            elif notification_type == 'trade_promotion':
                self.global_manager.get('trade_result')[0].promote() #promotes caravan
            trade_info_dict = {'is_last': is_last, 'commodity_trade': commodity_trade, 'commodity_trade_type': notification_type, 'stops_trade': stops_trade, 'dies': dies}
            new_notification = action_notifications.trade_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width, self.global_manager),
                scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, trade_info_dict, notification_dice, self.global_manager)
                
        elif notification_type == 'exploration':
            new_notification = action_notifications.exploration_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width, self.global_manager),
                scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, False, notification_dice, self.global_manager)

        elif notification_type == 'final_exploration':
            new_notification = action_notifications.exploration_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width, self.global_manager),
                scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, True, notification_dice, self.global_manager)

        elif notification_type == 'off_tile_exploration':
            new_notification = action_notifications.off_tile_exploration_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager),
                scaling.scale_width(self.notification_width, self.global_manager), scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message,
                notification_dice, self.global_manager)

        elif notification_type == 'religious_campaign':
            new_notification = action_notifications.religious_campaign_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width,
                self.global_manager), scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, False, notification_dice, self.global_manager)
            
        elif notification_type == 'final_religious_campaign':
            new_notification = action_notifications.religious_campaign_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width,
                self.global_manager), scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, True, notification_dice, self.global_manager)

        elif notification_type == 'public_relations_campaign':
            new_notification = action_notifications.public_relations_campaign_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width,
                self.global_manager), scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, False, notification_dice, self.global_manager)
            
        elif notification_type == 'final_public_relations_campaign':
            new_notification = action_notifications.public_relations_campaign_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width,
                self.global_manager), scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, True, notification_dice, self.global_manager)

        elif notification_type == 'advertising_campaign':
            new_notification = action_notifications.advertising_campaign_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width,
                self.global_manager), scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, False, notification_dice, self.global_manager)
            
        elif notification_type == 'final_advertising_campaign':
            new_notification = action_notifications.advertising_campaign_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width,
                self.global_manager), scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, True, notification_dice, self.global_manager)

        elif notification_type == 'conversion':
            new_notification = action_notifications.conversion_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width,
                self.global_manager), scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, False, notification_dice, self.global_manager)
            
        elif notification_type == 'final_conversion':
            new_notification = action_notifications.conversion_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width,
                self.global_manager), scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, True, notification_dice, self.global_manager)

        elif notification_type == 'rumor_search':
            new_notification = action_notifications.rumor_search_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width,
                self.global_manager), scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, False, notification_dice, self.global_manager)
            
        elif notification_type == 'final_rumor_search':
            new_notification = action_notifications.rumor_search_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width,
                self.global_manager), scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, True, notification_dice, self.global_manager)

        elif notification_type == 'artifact_search':
            new_notification = action_notifications.artifact_search_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width,
                self.global_manager), scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, False, notification_dice, self.global_manager)
            
        elif notification_type == 'final_artifact_search':
            new_notification = action_notifications.artifact_search_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width,
                self.global_manager), scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, True, notification_dice, self.global_manager)

        elif notification_type == 'slave_capture':
            new_notification = action_notifications.capture_slaves_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width,
                self.global_manager), scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, False, notification_dice, self.global_manager)
            
        elif notification_type == 'final_slave_capture':
            new_notification = action_notifications.capture_slaves_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width,
                self.global_manager), scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, True, notification_dice, self.global_manager)

        elif notification_type == 'suppress_slave_trade':
            new_notification = action_notifications.suppress_slave_trade_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width,
                self.global_manager), scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, False, notification_dice, self.global_manager)
            
        elif notification_type == 'final_suppress_slave_trade':
            new_notification = action_notifications.suppress_slave_trade_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width,
                self.global_manager), scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, True, notification_dice, self.global_manager)

        elif notification_type == 'construction':
            new_notification = action_notifications.construction_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width,
                self.global_manager), scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, False, notification_dice, self.global_manager)
            
        elif notification_type == 'final_construction':
            new_notification = action_notifications.construction_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width,
                self.global_manager), scaling.scale_height(self.notification_height, self.global_manager), ['strategic', 'europe'], 'misc/default_notification.png', message, True, notification_dice, self.global_manager)

        elif notification_type == 'combat':
            new_notification = action_notifications.combat_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width,
                self.global_manager), scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, False, notification_dice, self.global_manager)
            
        elif notification_type == 'final_combat':
            new_notification = action_notifications.combat_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width,
                self.global_manager), scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, True, notification_dice, self.global_manager)

        elif notification_type == 'trial':
            new_notification = action_notifications.trial_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width,
                self.global_manager), scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, True, notification_dice, self.global_manager)
            
        elif notification_type == 'choice':
            choice_notification_choices = self.choice_notification_choices_queue.pop(0)
            choice_notification_info_dict = self.choice_notification_info_dict_queue.pop(0)
            new_notification = choice_notifications.choice_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width, self.global_manager),
                scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, choice_notification_choices, choice_notification_info_dict, notification_dice,
                self.global_manager)

        elif notification_type == 'zoom':
            target = self.choice_notification_choices_queue.pop(0) #repurposing communication method used for choice notifications to tell notification which target
            self.choice_notification_info_dict_queue.pop(0)
            new_notification = notifications.zoom_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width, self.global_manager),
                scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, target, self.global_manager)     
            
        elif notification_type == 'minister':
            new_notification = notifications.minister_notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width, self.global_manager),
                scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, self.global_manager, self.minister_message_queue.pop(0))

        else:
            new_notification = notifications.notification(scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager), scaling.scale_width(self.notification_width, self.global_manager),
                scaling.scale_height(self.notification_height, self.global_manager), self.notification_modes, 'misc/default_notification.png', message, self.global_manager)
                #coordinates, ideal_width, minimum_height, showing, modes, image, message

class sound_manager_template():
    '''
    Object that controls sounds
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
        self.default_music_dict = {
            'europe': ['French theme', 'French generic song', 'French generic song 2', 'German generic song', 'Over the hills and far away', 'Italian theme'],
            'main menu': ['main theme'],
            'village peaceful': ['village peaceful'],
            'village neutral': ['village neutral'],
            'village aggressive': ['village aggressive'],
            'slave traders': ['slave traders theme']
        }
        self.previous_state = 'none'
        self.previous_song = 'none'

    def play_sound(self, file_name, volume = 0.3):
        '''
        Description:
            Plays the sound effect from the inputted file
        Input:
            string file_name: Name of .wav file to play sound of
            double volume = 0.3: Volume from 0.0 to 1.0 to play sound at - mixer usually uses a default of 1.0
        Output:
            Channel: Returns the pygame mixer Channel object that the sound was played on
        '''
        current_sound = pygame.mixer.Sound('sounds/' + file_name + '.wav')
        current_sound.set_volume(volume)
        channel = current_sound.play()
        return(channel)

    def queue_sound(self, file_name, channel, volume = 0.3):
        '''
        Description:
            Queues the sound effect from the inputted file to be played once the inputted channel is done with its current sound
        Input:
            string file_name: Name of .wav file to play sound of
            Channel channel: Pygame mixer channel to queue the sound in
            double volume = 0.3: Volume from 0.0 to 1.0 to play sound at - mixer usually uses a default of 1.0
        Output:
            None
        '''   
        current_sound = pygame.mixer.Sound('sounds/' + file_name + '.wav')
        current_sound.set_volume(volume)
        channel.queue(current_sound)

    def play_music(self, file_name, volume = -0.1):
        '''
        Description:
            Starts playing the music from the inputted file, replacing any current music
        Input:
            string file_name: Name of .wav file to play music of
            double volume = -0.1: Volume from 0.0 to 1.0 to play sound at - replaces negative or absent volume input with default
        Output:
            None
        '''
        if volume < 0: #negative volume value -> use default
            volume = self.global_manager.get('default_music_volume')
        pygame.mixer.music.load('sounds/music/' + file_name + '.wav')
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(0) #music loops when loop argument is -1

    def music_transition(self, file_name, time_interval = 0.75):
        '''
        Description:
            Fades out the current song and plays a new song at the previous volume
        Input:
            string file_name: Name of .wav file to play music of, or 'none' if music should fade out but not restart
            double time_interval = 0.75: Time to wait between each volume change event
        Output:
            None
        '''
        original_volume = self.global_manager.get('default_music_volume') #pygame.mixer.music.get_volume()
        pygame.mixer.music.set_volume(original_volume)
        #pygame.mixer.music.set_volume(original_volume)
        #time_interval = 0.75
        time_passed = 0
        if pygame.mixer.music.get_busy(): #only delay starting music for fade out if there is any current music to fade out
            for i in range(1, 5):
                time_passed += time_interval #with each interval, time_interval time passes and volume decreases by 0.25
                self.global_manager.get('event_manager').add_event(pygame.mixer.music.set_volume, [original_volume * (1 - (0.25 * i))], time_passed)

        if not file_name == 'none':
            time_passed += time_interval
            self.global_manager.get('event_manager').add_event(self.play_music, [file_name, 0], time_passed)
            for i in range(1, 5):
                self.global_manager.get('event_manager').add_event(pygame.mixer.music.set_volume, [original_volume * (0.25 * i)], time_passed)
                time_passed += time_interval #with each interval, time_interval time passes and volume increases by 0.25
        else:
            self.global_manager.get('event_manager').add_event(pygame.mixer.music.stop, [], time_passed)
            self.global_manager.get('event_manager').add_event(pygame.mixer.music.unload, [], time_passed)
            self.global_manager.get('event_manager').add_event(pygame.mixer.music.set_volume, [original_volume], time_passed)     

    def dampen_music(self, time_interval = 0.5):
        '''
        Description:
            Temporarily reduces the volume of the music to allow for other sounds
        Input:
            double time_interval = 0.5: Time to wait between each volume change event
        Output:
            None
        '''
        self.global_manager.get('event_manager').clear()
        original_volume = self.global_manager.get('default_music_volume')
        pygame.mixer.music.set_volume(0)
        time_passed = 0
        for i in range(-5, 6):
            time_passed += time_interval
            if i > 0:
                self.global_manager.get('event_manager').add_event(pygame.mixer.music.set_volume, [original_volume * i * 0.1], time_passed)

    def play_random_music(self, current_state, previous_song = 'none'):
        '''
        Description:
            Plays random music depending on the current state of the game, like 'main menu', 'europe', or 'village', and the current player country
        Input:
            string current_state: Descriptor for the current state of the game to play music for
            string previous_song: The previous song that just ended, if any, to avoid playing it again unless it is the only option
        Output:
            None
        '''
        self.previous_song = 'none'
        if not (self.previous_state == current_state):
            state_changed = True
        else:
            state_changed = False
        self.previous_state = current_state
        current_country = self.global_manager.get('current_country')
        if current_state == 'europe' and not current_country == 'none':
            if self.global_manager.get('creating_new_game') and len(self.global_manager.get('current_country').music_list) > 0:
                possible_songs = self.global_manager.get('current_country').music_list
            else:
                possible_songs = self.default_music_dict[current_state] + self.global_manager.get('current_country').music_list
        else:
            possible_songs = self.default_music_dict[current_state]
        if len(possible_songs) == 1:
            chosen_song = random.choice(possible_songs)
        elif len(possible_songs) > 0:
            chosen_song = random.choice(possible_songs)
            if not previous_song == 'none': #plays different song if multiple choices available
                while chosen_song == previous_song:
                    chosen_song = random.choice(possible_songs)
        else:
            chosen_song = 'none'
        if current_state in ['slave traders', 'village peaceful', 'village neutral', 'village aggressive'] or self.previous_state in ['slave traders', 'village peaceful', 'village neutral', 'village aggressive']:
            time_interval = 0.4
        else:
            time_interval = 0.75
        if (not state_changed) and (not chosen_song == 'none'):
            self.play_music(chosen_song)
        else:
            self.music_transition(chosen_song, time_interval)
        self.previous_song = chosen_song
        #pygame.mixer.music.set_endevent(SONG_END)
        #print(pygame.mixer.music.get_endevent())

    def song_done(self):
        '''
        Description:
            Called when a song finishes, plays a new random song for the same state, with the new song being different if possible
        Input:
            None
        Output:
            None
        '''
        self.play_random_music(self.previous_state, self.previous_song)

class event_manager_template():
    '''
    Object that tracks a list of events and calls the relevant functions once an inputted amount of time has passed
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
        self.event_list = []
        self.event_time_list = []
        self.global_manager = global_manager
        self.previous_time = self.global_manager.get('current_time')
        #self.add_event(self.go, (), 5) #calls this object's go function after 5 seconds with no inputs

    def add_event(self, function, inputs, activation_time):
        '''
        Description:
            Creates a new event with the inputted function and time that will call the inputted function with inputs after the inputted time has elapsed
        Input:
            function function: Function that will be called after the inputted time has elapsed
            list inputs: List of inputs the function will be called with, in order
            double activation_time: Amount of time that will pass before the function is called
        Output:
            None
        '''
        self.event_list.append(events.event(function, inputs, activation_time, self))

    def add_repeating_event(self, function, inputs, activation_time, num_repeats = -1):
        '''
        Description:
            Creates a new event with the inputted function and time that will call the inputted function with inputs after the inputted time has elapsed
        Input:
            function function: Function that will be called each time the inputted time elapses
            list inputs: List of inputs the function will be called with, in order
            double activation_time: Amount of time that will pass between each function call
        Output:
            None
        '''
        self.event_list.append(events.repeating_event(function, inputs, activation_time, self, num_repeats))
        
    def update(self, new_time):
        '''
        Description:
            Updates events with the current time, activating any that run out of time
        Input:
            double new_time: New time to update this object with
        Output:
            None
        '''
        time_difference = new_time - self.previous_time
        activated_events = []

        for current_event in self.event_list:
            current_event.activation_time -= time_difference #updates event times with new time
            if current_event.activation_time <= 0: #if any event runs out of time, activate it
                activated_events.append(current_event)

        if len(activated_events) > 0: #when an event activates, call its stored function 
            for current_event in activated_events:
                current_event.activate()
                current_event.remove()

        self.previous_time = new_time

    def clear(self):
        '''
        Description:
            Removes this object's events, removing them from storage and stopping them before activation
        Input:
            None
        Output:
            None
        '''
        existing_events = []
        for current_event in self.event_list:
            existing_events.append(current_event)
        for current_event in existing_events:
            current_event.remove()

    def go(self):
        #function to call for event testing
        #calls the money tracker's change function with an input of -20 every second, repeats infinitely because no num_repeats is provided
        self.add_repeating_event(self.global_manager.get('money_tracker').change, [-20], activation_time = 1)