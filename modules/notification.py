from .label import label
from . import text_tools
from . import utility

class notification(label):
    '''special label with slightly different message and disappears when clicked'''
    
    def __init__(self, coordinates, ideal_width, minimum_height, modes, image, message, global_manager):
        self.global_manager = global_manager
        self.global_manager.get('notification_list').append(self)
        super().__init__(coordinates, ideal_width, minimum_height, modes, image, message, global_manager)

    def format_message(self): #takes a string message and divides it into a list of strings based on length
        new_message = []
        next_line = ""
        next_word = ""
        for index in range(len(self.message)):
            next_word += self.message[index]
            if self.message[index] == " ":
                if text_tools.message_width(next_line + next_word, self.font_size, self.font_name) > self.ideal_width:
                    new_message.append(next_line)
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
