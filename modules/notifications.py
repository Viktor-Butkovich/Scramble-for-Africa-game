from .labels import label
from . import text_tools
from . import utility
from . import scaling

class notification(label):
    '''
    Label that disappear when clicked and prompts the user to click on it
    '''
    
    def __init__(self, coordinates, ideal_width, minimum_height, modes, image, message, global_manager):
        '''
        Inputs:
            coordinates: tuple of two int variables representing the pixel coordinates of the bottom left of the notification
            ideal_width: int representing the width that the notification will try to keep - each line of text will create a new line after the ideal width is reached
            minimum_height: int representing the minimum height of the notification - if it has enough lines of text, its height will increase and the top of the notification will move up
            modes: list of strings representing the game modes in which the notification can appear
            image: string representing the file path to the notificaton's background image
            message: string with lines separated by /n representing the text that will appear on the notification
            global_manager: global_manager_template object used to manage a dictionary of shared variables
        '''
        self.global_manager = global_manager
        self.global_manager.get('notification_list').append(self)
        super().__init__(coordinates, ideal_width, minimum_height, modes, image, message, global_manager)

    def format_message(self): #takes a string message and divides it into a list of strings based on length, /n used because there are issues with checking if something is equal to \
        '''
        Inputs:
            none
        Outputs:
            Converts the notification's string message to a list of strings, with each string representing a line of text and having a length depending on the /n characters in the message and the notification's ideal width
        '''
        new_message = []
        next_line = ""
        next_word = ""
        for index in range(len(self.message)):
            if not ((not (index + 2) > len(self.message) and self.message[index] + self.message[index + 1]) == "/n"): #don't add if /n
                if not (index > 0 and self.message[index - 1] + self.message[index] == "/n"): #if on n after /, skip
                    next_word += self.message[index]
            if self.message[index] == " ":
                if text_tools.message_width(next_line + next_word, self.font_size, self.font_name) > self.ideal_width:
                    new_message.append(next_line)
                    next_line = ""
                next_line += next_word
                next_word = ""
            elif (not (index + 2) > len(self.message) and self.message[index] + self.message[index + 1]) == "/n": #don't check for /n if at last index
                new_message.append(next_line)
                #new_message.append("")
                next_line = ""
                next_line += next_word
                next_word = ""
        next_line += next_word
        new_message.append(next_line)
        new_message.append("Click to remove this notification.")
        self.message = new_message
                    
    def update_tooltip(self):
        '''
        Inputs:
            none
        Outputs:
            Sets this notification's tooltip to an appropriate message
        '''
        self.set_tooltip(["Click to remove this notification"])
            
    def on_click(self):
        '''
        Inputs:
            none
        Outputs:
            The notification is deleted when clicked
        '''
        self.remove()
            
    def remove(self):
        '''
        Inputs:
            none
        Outputs:
            Removes the object from relevant lists and prevents it from further appearing in or affecting the program
        '''
        super().remove()
        self.global_manager.set('notification_list', utility.remove_from_list(self.global_manager.get('notification_list'), self))
        if len(self.global_manager.get('notification_queue')) >= 1:
            self.global_manager.get('notification_queue').pop(0)
        if len(self.global_manager.get('notification_queue')) > 0:
            notification_to_front(self.global_manager.get('notification_queue')[0], self.global_manager)

class dice_rolling_notification(notification): #automatically removed when dice finish rolling, blocks other notifications
    '''
    Notification that is removed when a dice roll is completed rather than when clicked
    '''
    def __init__(self, coordinates, ideal_width, minimum_height, modes, image, message, global_manager):
        '''
        Inputs:
            Same as superclass
        '''
        super().__init__(coordinates, ideal_width, minimum_height, modes, image, message, global_manager)
        global_manager.set('current_dice_rolling_notification', self)

    def format_message(self):
        '''
        Inputs:
            none
        Outputs:
            Converts the notification's string message to a list of strings, with each string representing a line of text and having a length depending on the /n characters in the message and the notification's ideal width
            The list created will not have a prompt to click on the notification, unlike the superclass
        '''
        super().format_message()
        self.message.pop(-1) #remove "Click to remove this notification"
        
    def on_click(self):
        '''
        Inputs:
            none
        Outputs:
            Dice rolling notifications do nothing when clicked, unlike the superclass
        '''
        nothing = 0 #does not remove self when clicked

    def remove(self):
        '''
        Inputs:
            none
        Outputs:
            Removes the object from relevant lists and prevents it from further appearing in or affecting the program
        '''
        super().remove()
        self.global_manager.set('current_dice_rolling_notification', 'none')
        if len(self.global_manager.get('dice_list')) > 1:
            max_roll = 0
            max_die = 0#self.global_manager.get('dice_list')[0]
            for current_die in self.global_manager.get('dice_list'):
                if current_die.roll_result > max_roll:
                    max_roll = current_die.roll_result
                    max_die = current_die
            max_die.highlighted = True#outline_color = 'white'
        else:
            self.global_manager.get('dice_list')[0].highlighted = True#outline_color = 'white'

class exploration_notification(notification):
    '''
    Notification that does not automatically prompt the user to remove it and shows the results of exploration when the last notification is removed
    '''
    def __init__(self, coordinates, ideal_width, minimum_height, modes, image, message, global_manager):
        '''
        Inputs:
            Same as superclass
        '''
        super().__init__(coordinates, ideal_width, minimum_height, modes, image, message, global_manager)

    def format_message(self):
        super().format_message()
        self.message.pop(-1) #remove "Click to remove this notification"

    def remove(self):
        self.global_manager.set('button_list', utility.remove_from_list(self.global_manager.get('button_list'), self))
        self.global_manager.set('image_list', utility.remove_from_list(self.global_manager.get('image_list'), self.image))
        self.global_manager.set('label_list', utility.remove_from_list(self.global_manager.get('label_list'), self))
        self.global_manager.set('notification_list', utility.remove_from_list(self.global_manager.get('notification_list'), self))
        if len(self.global_manager.get('notification_queue')) >= 1:
            self.global_manager.get('notification_queue').pop(0)
        if len(self.global_manager.get('notification_queue')) > 0:
            notification_to_front(self.global_manager.get('notification_queue')[0], self.global_manager)
        else:
            self.global_manager.get('exploration_result')[0].complete_exploration() #tells index 0 of exploration result, the explorer object, to finish exploring when notifications removed
            
def notification_to_front(message, global_manager):
    '''#displays a notification from the queue, which is a list of string messages that this formats into notifications'''
    notification_type = global_manager.get('notification_type_queue').pop(0)
    if notification_type == 'roll':
        new_notification = dice_rolling_notification(scaling.scale_coordinates(610, 236, global_manager), scaling.scale_width(500, global_manager), scaling.scale_height(500, global_manager), ['strategic'], 'misc/default_notification.png', message, global_manager)
        for current_die in global_manager.get('dice_list'):
            current_die.start_rolling()
    elif notification_type == 'exploration':
        new_notification = exploration_notification(scaling.scale_coordinates(610, 236, global_manager), scaling.scale_width(500, global_manager), scaling.scale_height(500, global_manager), ['strategic'], 'misc/default_notification.png', message, global_manager)
    else:
        new_notification = notification(scaling.scale_coordinates(610, 236, global_manager), scaling.scale_width(500, global_manager), scaling.scale_height(500, global_manager), ['strategic'], 'misc/default_notification.png', message, global_manager)#coordinates, ideal_width, minimum_height, showing, modes, image, message

