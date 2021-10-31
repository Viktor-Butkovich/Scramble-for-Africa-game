from .labels import label
from . import text_tools
from . import utility
from . import scaling

class notification(label):
    '''
    Label that has multiple lines, prompts the user to click on it, and disappears when clicked
    '''
    def __init__(self, coordinates, ideal_width, minimum_height, modes, image, message, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this notification
            int ideal_width: Pixel width that this notification will try to retain. Each time a word is added to the notification, if the word extends past the ideal width, the next line will be started
            int minimum_height: Minimum pixel height of this notification. Its height will increase if the contained text would extend past the bottom of the notification
            string list modes: Game modes during which this notification can appear
            string image: File path to the image used by this object
            string message: Text that will appear on the notification with lines separated by /n
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.global_manager = global_manager
        self.global_manager.get('notification_list').append(self)
        self.ideal_width = ideal_width
        self.minimum_height = minimum_height
        super().__init__(coordinates, ideal_width, minimum_height, modes, image, message, global_manager)
        self.in_notification = True

    def draw(self):
        '''
        Description:
            Draws this notification and draws its text on top of it
        Input:
            None
        Output:
            None
        '''
        if self.global_manager.get('current_game_mode') in self.modes:
            self.image.draw()
            for text_line_index in range(len(self.message)):
                text_line = self.message[text_line_index]
                self.global_manager.get('game_display').blit(text_tools.text(text_line, self.font, self.global_manager), (self.x + scaling.scale_width(10, self.global_manager), self.global_manager.get('display_height') -
                    (self.y + self.height - (text_line_index * self.font_size))))
                
    def format_message(self): #takes a string message and divides it into a list of strings based on length, /n used because there are issues with checking if something is equal to \
        '''
        Description:
            Converts this notification's string message to a list of strings, with each string representing a line of text. Each line of text ends when its width exceeds the ideal_width or when a '/n' is encountered in the text. Also
                adds a prompt to close the notification at the end of the message
        Input:
            None
        Output:
            None
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
        Description:
            Sets this notification's tooltip to what it should be. By default, notifications prompt the player to close them
        Input:
            None
        Output:
            None
        '''
        self.set_tooltip(["Click to remove this notification"])

    def set_label(self, new_message):
        '''
        Description:
            Sets each line of this notification's text to the corresponding item in the inputted list, adjusting width and height as needed
        Input:
            string list new_message: New text for this notification, with each item corresponding to a line of text
        Output:
            None
        '''
        self.message = new_message
        self.format_message()
        for text_line in self.message:
            if text_tools.message_width(text_line, self.font_size, self.font_name) > self.ideal_width:
                self.width = text_tools.message_width(text_line, self.font_size, self.font_name)

    def on_click(self):
        '''
        Description:
            Controls this notification's behavior when clicked. By default, notifications are removed when clicked
        Input:
            None
        Output:
            None
        '''
        self.remove()
            
    def remove(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program. By default, notifications are removed when clicked. When a notification is removed, the next notification is shown,
                if there is one
        Input:
            None
        Output:
            None
        '''
        super().remove()
        notification_manager = self.global_manager.get('notification_manager')
        self.global_manager.set('notification_list', utility.remove_from_list(self.global_manager.get('notification_list'), self))
        if len(notification_manager.notification_queue) >= 1:
            notification_manager.notification_queue.pop(0)
        if len(notification_manager.notification_queue) > 0:
            notification_manager.notification_to_front(notification_manager.notification_queue[0])

