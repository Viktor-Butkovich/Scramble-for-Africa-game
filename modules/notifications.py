from .labels import label
from .images import free_image
from . import text_tools
from . import utility
from . import scaling
from . import actor_utility

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
            none
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

class dice_rolling_notification(notification):
    '''
    Notification that is removed when a dice roll is completed rather than when clicked
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
        super().__init__(coordinates, ideal_width, minimum_height, modes, image, message, global_manager)
        global_manager.set('current_dice_rolling_notification', self)

    def format_message(self):
        '''
        Description:
            Converts this notification's string message to a list of strings, with each string representing a line of text. Each line of text ends when its width exceeds the ideal_width or when a '/n' is encountered in the text. Does
                not add a prompt to close the notification
        Input:
            none
        Output:
            None
        '''
        super().format_message()
        self.message.pop(-1) #remove "Click to remove this notification"

    def update_tooltip(self):
        '''
        Description:
            Sets this notification's tooltip to what it should be. Dice rolling notifications tell the user to wait for the dice to finish rolling
        Input:
            None
        Output:
            None
        '''
        self.set_tooltip(['Wait for the dice to finish rolling'])

    def on_click(self):
        '''
        Description:
            Controls this notification's behavior when clicked. Unlike superclass, dice rolling notifications are not removed when clicked
        Input:
            None
        Output:
            None
        '''
        nothing = 0 #does not remove self when clicked

    def remove(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program. When a notification is removed, the next notification is shown, if there is one. Dice rolling notifications are
                removed when all dice finish rolling rather than when clicked. Upon removal, dice rolling notifications highlight the chosen die with a color corresponding to the roll's outcome
        Input:
            None
        Output:
            None
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

class trade_notification(notification):
    '''
    Notification used during trading that has various behaviors relevant to trading based on the values in its inputted trade_info_dict
    '''
    def __init__(self, coordinates, ideal_width, minimum_height, modes, image, message, trade_info_dict, global_manager):
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
            dictionary trade_info_dict: Contains information that affects this notification's behavior:
                string key: 'is_last', boolean value: If True, this notification removes currently rolling dice when removed
                string key: 'stops_trade', boolean value: If True, trading will stop when this notification is removed
                string key: 'commodity_trade', boolean value: If True, this notification will show a transaction
                string key: 'commodity_trade_type', string value: If equals 'successful_commodity_trade', the trade will be successful and a commodity will be given for the transaction
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''   
        self.trade_info_dict = trade_info_dict
        self.is_last = self.trade_info_dict['is_last']
        self.gives_commodity = False
        self.stops_trade = self.trade_info_dict['stops_trade']
        self.is_commodity_trade = self.trade_info_dict['commodity_trade']
        if self.is_commodity_trade:
            self.commodity_trade_type = self.trade_info_dict['commodity_trade_type']
            if self.commodity_trade_type == 'successful_commodity_trade':
                self.gives_commodity = True
        
        self.notification_images = []

        if self.is_commodity_trade:
            self.trade_result = global_manager.get('trade_result')
            consumer_goods_y = 0
            if self.commodity_trade_type == 'successful_commodity_trade':
                consumer_goods_y = 500
                self.notification_images.append(free_image('scenery/resources/' + self.trade_result[2] + '.png', scaling.scale_coordinates(global_manager.get('notification_manager').notification_x - 200, 300, global_manager),
                    scaling.scale_width(200, global_manager), scaling.scale_height(200, global_manager), modes, global_manager, True))
            else:
                consumer_goods_y = 400 #either have icon at 300 and 500 or a single icon at 400
            self.notification_images.append(free_image('scenery/resources/trade/sold consumer goods.png', scaling.scale_coordinates(global_manager.get('notification_manager').notification_x - 200, consumer_goods_y, global_manager),
                scaling.scale_width(200, global_manager), scaling.scale_height(200, global_manager), modes, global_manager, True))
        
        super().__init__(coordinates, ideal_width, minimum_height, modes, image, message, global_manager)
        
    def format_message(self):
        '''
        Description:
            Converts this notification's string message to a list of strings, with each string representing a line of text. Each line of text ends when its width exceeds the ideal_width or when a '/n' is encountered in the text. Does
                not add a prompt to close the notification
        Input:
            none
        Output:
            None
        '''
        super().format_message()
        self.message.pop(-1)
        
    def remove(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program.  When a notification is removed, the next notification is shown, if there is one. If this trade is a transaction,
                consumer goods wil be lost upon removal. If this trade is also a successful transaction, a random commodity will be gained in return. Removes dice and other side images as applicable
        Input:
            None
        Output:
            None
        '''
        if self.is_commodity_trade:
            caravan = self.trade_result[0]
            caravan.change_inventory('consumer goods', -1)
            if self.gives_commodity:
                commodity_gained = self.trade_result[2]
                if not commodity_gained == 'none':
                    caravan.change_inventory(commodity_gained, 1) #caravan gains unit of random commodity 
        super().remove()
        for current_image in self.notification_images:
            current_image.remove()
        if self.is_last:
            for current_die in self.global_manager.get('dice_list'):
                current_die.remove()
        if self.stops_trade:
            self.global_manager.set('ongoing_trade', False)

class exploration_notification(notification):
    '''
    Notification that does not automatically prompt the user to remove it and shows the results of exploration when the last notification is removed
    '''
    def __init__(self, coordinates, ideal_width, minimum_height, modes, image, message, is_last, global_manager):
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
            boolean is_last: Whether this is the last exploration notification. If it is the last, any side images will be removed when it is removed
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.is_last = is_last
        if self.is_last:
            current_expedition = actor_utility.get_selected_list(global_manager)[0]
            self.notification_images = []
            explored_cell = current_expedition.destination_cell
            explored_tile = explored_cell.tile
            explored_terrain_image_id = explored_cell.tile.image_dict['default']
            self.notification_images.append(free_image(explored_terrain_image_id, scaling.scale_coordinates(global_manager.get('notification_manager').notification_x - 225, 400, global_manager),
                scaling.scale_width(200, global_manager), scaling.scale_height(200, global_manager), modes, global_manager, True))
            if not explored_tile.resource_icon == 'none':
                explored_resource_image_id = explored_tile.resource_icon.image_dict['default']
                self.notification_images.append(free_image(explored_resource_image_id, scaling.scale_coordinates(global_manager.get('notification_manager').notification_x - 225, 400, global_manager),
                    scaling.scale_width(200, global_manager), scaling.scale_height(200, global_manager), modes, global_manager, True))
        super().__init__(coordinates, ideal_width, minimum_height, modes, image, message, global_manager)

    def format_message(self):
        '''
        Description:
            Converts this notification's string message to a list of strings, with each string representing a line of text. Each line of text ends when its width exceeds the ideal_width or when a '/n' is encountered in the text. Does
                not add a prompt to close the notification
        Input:
            none
        Output:
            None
        '''
        super().format_message()
        self.message.pop(-1)

    def remove(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program. When a notification is removed, the next notification is shown, if there is one
        Input:
            None
        Output:
            None
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
