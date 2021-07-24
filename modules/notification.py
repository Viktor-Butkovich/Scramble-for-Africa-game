from .label import label
from . import text_tools
from . import utility
from . import scaling

class notification(label):
    '''special label with slightly different message and disappears when clicked'''
    
    def __init__(self, coordinates, ideal_width, minimum_height, modes, image, message, global_manager):
        self.global_manager = global_manager
        self.global_manager.get('notification_list').append(self)
        super().__init__(coordinates, ideal_width, minimum_height, modes, image, message, global_manager)

    def format_message(self): #takes a string message and divides it into a list of strings based on length, /n used because there are issues with checking if something is equal to \
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
        new_message.append("Click to remove this notification")
        self.message = new_message
                    
    def update_tooltip(self):
        self.set_tooltip(["Click to remove this notification"])
            
    def on_click(self):
        self.remove()
            
    def remove(self):
        super().remove()
        self.global_manager.set('notification_list', utility.remove_from_list(self.global_manager.get('notification_list'), self))
        if len(self.global_manager.get('notification_queue')) >= 1:
            self.global_manager.get('notification_queue').pop(0)
        if len(self.global_manager.get('notification_queue')) > 0:
            notification_to_front(self.global_manager.get('notification_queue')[0], self.global_manager)

class exploration_notification(notification):
    def __init__(self, coordinates, ideal_width, minimum_height, modes, image, message, global_manager):
        super().__init__(coordinates, ideal_width, minimum_height, modes, image, message, global_manager)

    def remove(self):
        self.global_manager.set('button_list', utility.remove_from_list(self.global_manager.get('button_list'), self))
        self.global_manager.set('image_list', utility.remove_from_list(self.global_manager.get('image_list'), self.image))
        self.global_manager.set('label_list', utility.remove_from_list(self.global_manager.get('label_list'), self))
        self.global_manager.set('notification_list', utility.remove_from_list(self.global_manager.get('notification_list'), self))
        if len(self.global_manager.get('notification_queue')) >= 1:
            self.global_manager.get('notification_queue').pop(0)
        if len(self.global_manager.get('notification_queue')) > 0:
            exploration_notification_to_front(self.global_manager.get('notification_queue')[0], self.global_manager)
        else:
            self.global_manager.get('exploration_result')[0].complete_exploration() #tells index 0 of exploration result, the explorer object, to finish exploring when notifications removed
        #super().remove()
        #if len(self.global_manager.get('notification_queue')) > 0:
        #    exploration_notification_to_front(self.global_manager.get('notification_queue')[0], self.global_manager)
        #else:
        #    self.global_manager.get('exploration_result')[0].complete_exploration() #tells index 0 of exploration result, the explorer object, to finish exploring when notifications removed
            
def exploration_notification_to_front(message, global_manager):
    '''#displays a notification from the queue, which is a list of string messages that this formats into notifications'''
    new_notification = exploration_notification(scaling.scale_coordinates(610, 236, global_manager), scaling.scale_width(500, global_manager), scaling.scale_height(500, global_manager), ['strategic'], 'misc/default_notification.png', message, global_manager)

def notification_to_front(message, global_manager):
    '''#displays a notification from the queue, which is a list of string messages that this formats into notifications'''
    new_notification = notification(scaling.scale_coordinates(610, 236, global_manager), scaling.scale_width(500, global_manager), scaling.scale_height(500, global_manager), ['strategic'], 'misc/default_notification.png', message, global_manager)#coordinates, ideal_width, minimum_height, showing, modes, image, message

