from .labels import label
from .images import free_image
from . import text_tools
from . import utility
from . import scaling
from . import actor_utility

class notification(label):
    '''
    Label that disappear when clicked and prompts the user to click on it, can also have multiple lines
    '''
    
    def __init__(self, coordinates, ideal_width, minimum_height, modes, image, message, global_manager):
        '''
        Input:
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
        self.ideal_width = ideal_width
        self.minimum_height = minimum_height
        super().__init__(coordinates, ideal_width, minimum_height, modes, image, message, global_manager)
        self.in_notification = True

    def draw(self):
        '''
        Input:
            none
        Output:
            Draws this label's image with its text
        '''
        if self.global_manager.get('current_game_mode') in self.modes:
            self.image.draw()
            for text_line_index in range(len(self.message)):
                text_line = self.message[text_line_index]
                self.global_manager.get('game_display').blit(text_tools.text(text_line, self.font, self.global_manager), (self.x + 10, self.global_manager.get('display_height') - (self.y + self.height - (text_line_index * self.font_size))))

    #to do: make sure instructions use same format message function as label, maybe make a shared label subclass with multiple line messages that has format_message as a function
    def format_message(self): #takes a string message and divides it into a list of strings based on length, /n used because there are issues with checking if something is equal to \
        '''
        Input:
            none
        Output:
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
                next_line = ""
                next_line += next_word
                next_word = ""
        if text_tools.message_width(next_line + next_word, self.font_size, self.font_name) > self.ideal_width:
            new_message.append(next_line)
            next_line = ""
        next_line += next_word
        new_message.append(next_line)
        new_message.append("Click to remove this notification.")
        self.message = new_message
                    
    def update_tooltip(self):
        '''
        Input:
            none
        Output:
            Sets this notification's tooltip to an appropriate message
        '''
        self.set_tooltip(["Click to remove this notification"])

    def set_label(self, new_message):
        '''
        Input:
            string representing this label's new text
        Output:
            Sets this label's text to a list based on the inputted string and changes its size as needed
        '''
        self.message = new_message
        self.format_message()
        for text_line in self.message:
            if text_tools.message_width(text_line, self.font_size, self.font_name) > self.ideal_width:
                self.width = text_tools.message_width(text_line, self.font_size, self.font_name)

    def on_click(self):
        '''
        Input:
            none
        Output:
            The notification is deleted when clicked
        '''
        self.remove()
            
    def remove(self):
        '''
        Input:
            none
        Output:
            Removes the object from relevant lists and prevents it from further appearing in or affecting the program
        '''
        super().remove()
        notification_manager = self.global_manager.get('notification_manager')
        self.global_manager.set('notification_list', utility.remove_from_list(self.global_manager.get('notification_list'), self))
        if len(notification_manager.notification_queue) >= 1:
            notification_manager.notification_queue.pop(0)
        if len(notification_manager.notification_queue) > 0:
            notification_manager.notification_to_front(notification_manager.notification_queue[0])

class dice_rolling_notification(notification):
    '''
    Notification that is removed when a dice roll is completed rather than when clicked
    '''
    def __init__(self, coordinates, ideal_width, minimum_height, modes, image, message, global_manager):
        '''
        Input:
            Same as superclass
        '''
        super().__init__(coordinates, ideal_width, minimum_height, modes, image, message, global_manager)
        global_manager.set('current_dice_rolling_notification', self)

    def format_message(self):
        '''
        Input:
            none
        Output:
            Converts the notification's string message to a list of strings, with each string representing a line of text and having a length depending on the /n characters in the message and the notification's ideal width
            The list created will not have a prompt to click on the notification, unlike the superclass
        '''
        super().format_message()
        self.message.pop(-1) #remove "Click to remove this notification"

    def update_tooltip(self):
        self.set_tooltip(['Wait for the dice to finish rolling'])

    def on_click(self):
        '''
        Input:
            none
        Output:
            Dice rolling notifications do nothing when clicked, unlike the superclass
        '''
        nothing = 0 #does not remove self when clicked

    def remove(self):
        '''
        Input:
            none
        Output:
            Removes the object from relevant lists and prevents it from further appearing in or affecting the program. When a notification is removed, the next notification, if any, will be shown.
            A dice rolling notification is removed when all of the dice finish rolling, rather than when the notification is clicked.
            Additionally, if multiple dice are present, the dice rolling notification will highlight the highest result when the dice are finished rolling to show which die's result will be used. 
        '''
        super().remove()
        self.global_manager.set('current_dice_rolling_notification', 'none')
        if len(self.global_manager.get('dice_list')) > 1:
            max_roll = 0
            max_die = 0
            for current_die in self.global_manager.get('dice_list'):
                if current_die.roll_result > max_roll:
                    max_roll = current_die.roll_result
                    max_die = current_die
            max_die.highlighted = True
        else:
            self.global_manager.get('dice_list')[0].highlighted = True#outline_color = 'white'

class exploration_notification(notification):
    '''
    Notification that does not automatically prompt the user to remove it and shows the results of exploration when the last notification is removed
    '''
    def __init__(self, coordinates, ideal_width, minimum_height, modes, image, message, is_last, global_manager):
        '''
        Input:
            Same as superclass
        '''
        self.is_last = is_last
        if self.is_last:
            current_expedition = actor_utility.get_selected_list(global_manager)[0]
            self.notification_images = []
            explored_cell = current_expedition.destination_cell
            explored_tile = explored_cell.tile
            explored_terrain_image_id = explored_cell.tile.image_dict['default']
            self.notification_images.append(free_image(explored_terrain_image_id, scaling.scale_coordinates(400, 400, global_manager), scaling.scale_width(200, global_manager), scaling.scale_height(200, global_manager), modes, global_manager))
            if not explored_tile.resource_icon == 'none':
                explored_resource_image_id = explored_tile.resource_icon.image_dict['default']
                self.notification_images.append(free_image(explored_resource_image_id, scaling.scale_coordinates(400, 400, global_manager), scaling.scale_width(200, global_manager), scaling.scale_height(200, global_manager), modes, global_manager))
        super().__init__(coordinates, ideal_width, minimum_height, modes, image, message, global_manager)

    def format_message(self):
        '''
        Input:
            none
        Output:
            Same as superclass except for the last line, "Click to remove this notification", being removed to allow for a more specific message for the circumstances of the notification
        '''
        super().format_message()
        self.message.pop(-1)

    def remove(self):
        '''
        Input:
            none
        Output:
            Removes the object from relevant lists and prevents it from further appearing in or affecting the program. When a notification is removed, the next notification, if any, will be shown.
            Exploration notifications
        '''
        self.global_manager.set('button_list', utility.remove_from_list(self.global_manager.get('button_list'), self))
        self.global_manager.set('image_list', utility.remove_from_list(self.global_manager.get('image_list'), self.image))
        self.global_manager.set('label_list', utility.remove_from_list(self.global_manager.get('label_list'), self))
        self.global_manager.set('notification_list', utility.remove_from_list(self.global_manager.get('notification_list'), self))
        notification_manager = self.global_manager.get('notification_manager')
        if len(notification_manager.notification_queue) >= 1:
            notification_manager.notification_queue.pop(0)
        if len(self.global_manager.get('notification_manager').notification_queue) == 1:
            notification_manager.notification_to_front(notification_manager.notification_queue[0])
            self.global_manager.get('exploration_result')[0].complete_exploration() #tells index 0 of exploration result, the explorer object, to finish exploring when notifications removed
        elif len(notification_manager.notification_queue) > 0:
            notification_manager.notification_to_front(notification_manager.notification_queue[0])

        if self.is_last:
            for current_image in self.notification_images:
                current_image.remove()
'''            
def notification_to_front(message, global_manager):
    Input:
        string from the notification_queue representing the text of the new notification, global_manager_template object
    Output:
        Displays a new notification with text matching the inputted string. The type of notification is determined by first item of the notification_type_queue, a list of strings corresponding to the notification_queue.
    notification_type = global_manager.get('notification_type_queue').pop(0)
    if notification_type == 'roll':
        new_notification = dice_rolling_notification(scaling.scale_coordinates(610, 236, global_manager), scaling.scale_width(500, global_manager), scaling.scale_height(500, global_manager), ['strategic'], 'misc/default_notification.png', message, global_manager)
        for current_die in global_manager.get('dice_list'):
            current_die.start_rolling()
    elif notification_type == 'exploration':
        new_notification = exploration_notification(scaling.scale_coordinates(610, 236, global_manager), scaling.scale_width(500, global_manager), scaling.scale_height(500, global_manager), ['strategic'], 'misc/default_notification.png', message, False, global_manager)
    elif notification_type == 'final_exploration':
        new_notification = exploration_notification(scaling.scale_coordinates(610, 236, global_manager), scaling.scale_width(500, global_manager), scaling.scale_height(500, global_manager), ['strategic'], 'misc/default_notification.png', message, True, global_manager)
    else:
        new_notification = notification(scaling.scale_coordinates(610, 236, global_manager), scaling.scale_width(500, global_manager), scaling.scale_height(500, global_manager), ['strategic'], 'misc/default_notification.png', message, global_manager)#coordinates, ideal_width, minimum_height, showing, modes, image, message
'''
