#Contains functionality for notifications

from .labels import multi_line_label
from . import text_tools
from . import utility
from . import scaling

class notification(multi_line_label):
    '''
    Multi-line label that prompts the user to click on it, and disappears when clicked
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
        super().__init__(coordinates, ideal_width, minimum_height, modes, image, message, global_manager)
        self.in_notification = True
        self.global_manager.get('sound_manager').play_sound('opening_letter')

    def format_message(self): #takes a string message and divides it into a list of strings based on length, /n used because there are issues with checking if something is equal to \
        super().format_message()
        self.message.append("Click to remove this notification.")
                    
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

