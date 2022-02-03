#Contains functionality for multi-step notifications

from .labels import label
from .images import free_image
from .notifications import notification
from . import text_tools
from . import utility
from . import scaling
from . import actor_utility

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
            if self.global_manager.get('exploration_result')[0].movement_points >= 1: #fix to exploration completing multiple times bug
                self.global_manager.get('exploration_result')[0].complete_exploration() #tells index 0 of exploration result, the explorer object, to finish exploring when notifications removed
                #self.global_manager.get('exploration_result')[0].resolve_off_tile_exploration()
        elif len(notification_manager.notification_queue) > 0:
            notification_manager.notification_to_front(notification_manager.notification_queue[0])
        if self.is_last:
            for current_image in self.notification_images:
                current_image.remove()

class off_tile_exploration_notification(notification):
    '''
    Notification that shows a tile explored by an expedition in an adjacent tile, focusing on the new tile and returning minimap to original position upon removal
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
        current_expedition = actor_utility.get_selected_list(global_manager)[0]
        self.notification_images = []
        explored_cell = current_expedition.destination_cells.pop(0)
        explored_tile = explored_cell.tile
        explored_terrain_image_id = explored_cell.tile.image_dict['default']
        self.notification_images.append(free_image(explored_terrain_image_id, scaling.scale_coordinates(global_manager.get('notification_manager').notification_x - 225, 400, global_manager),
            scaling.scale_width(200, global_manager), scaling.scale_height(200, global_manager), modes, global_manager, True))
        if not explored_tile.resource_icon == 'none':
            explored_resource_image_id = explored_tile.resource_icon.image_dict['default']
            self.notification_images.append(free_image(explored_resource_image_id, scaling.scale_coordinates(global_manager.get('notification_manager').notification_x - 225, 400, global_manager),
                scaling.scale_width(200, global_manager), scaling.scale_height(200, global_manager), modes, global_manager, True))
        global_manager.set('ongoing_exploration', True)
        explored_cell.set_visibility(True)
        global_manager.get('minimap_grid').calibrate(explored_cell.x, explored_cell.y)
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
        self.global_manager.set('ongoing_exploration', False)
        self.global_manager.set('button_list', utility.remove_from_list(self.global_manager.get('button_list'), self))
        self.global_manager.set('image_list', utility.remove_from_list(self.global_manager.get('image_list'), self.image))
        self.global_manager.set('label_list', utility.remove_from_list(self.global_manager.get('label_list'), self))
        self.global_manager.set('notification_list', utility.remove_from_list(self.global_manager.get('notification_list'), self))
        notification_manager = self.global_manager.get('notification_manager')
        
        if len(notification_manager.notification_queue) >= 1:
            notification_manager.notification_queue.pop(0)
        if len(self.global_manager.get('notification_manager').notification_queue) == 1:
            notification_manager.notification_to_front(notification_manager.notification_queue[0])
        elif len(notification_manager.notification_queue) > 0:
            notification_manager.notification_to_front(notification_manager.notification_queue[0])
        else:
            current_expedition = self.global_manager.get('displayed_mob')
            self.global_manager.get('minimap_grid').calibrate(current_expedition.x, current_expedition.y)
        for current_image in self.notification_images:
            current_image.remove()
        
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
        self.dies = self.trade_info_dict['dies']
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
                min_y = 300
                self.notification_images.append(free_image('scenery/resources/' + self.trade_result[2] + '.png', scaling.scale_coordinates(global_manager.get('notification_manager').notification_x - 200, 300, global_manager),
                    scaling.scale_width(200, global_manager), scaling.scale_height(200, global_manager), modes, global_manager, True))
            else:
                consumer_goods_y = 400 #either have icon at 300 and 500 or a single icon at 400
                min_y = 400
            self.notification_images.append(free_image('scenery/resources/trade/sold consumer goods.png', scaling.scale_coordinates(global_manager.get('notification_manager').notification_x - 200, consumer_goods_y, global_manager),
                scaling.scale_width(200, global_manager), scaling.scale_height(200, global_manager), modes, global_manager, True))
            if self.trade_result[3]: #if gets available worker
                self.notification_images.append(free_image('mobs/African worker/button.png', scaling.scale_coordinates(global_manager.get('notification_manager').notification_x - 175, min_y - 175, global_manager),
                    scaling.scale_width(150, global_manager), scaling.scale_height(150, global_manager), modes, global_manager, True))
        elif self.dies:
            self.trade_result = global_manager.get('trade_result') #allows caravan object to be found so that it can die
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
            caravan.complete_trade(self.gives_commodity, self.trade_result)
        super().remove()
        for current_image in self.notification_images:
            current_image.remove()
        if self.dies:
            caravan = self.trade_result[0]
            if not caravan.images[0].current_cell.contained_buildings['trading_post'] == 'none':
                caravan.images[0].current_cell.contained_buildings['trading_post'].remove()
            caravan.die() 
        if self.is_last:
            for current_die in self.global_manager.get('dice_list'):
                current_die.remove()
        if self.stops_trade:
            self.global_manager.set('ongoing_trade', False)

class religious_campaign_notification(notification):
    '''
    Notification that does not automatically prompt the user to remove it and shows the results of a religious campaign when the last notification is removed
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
            boolean is_last: Whether this is the last religious campaign notification. If it is the last, any side images will be removed when it is removed
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        ''' 
        self.is_last = is_last
        if self.is_last: #if last, show result
            current_head_missionary = actor_utility.get_selected_list(global_manager)[0]
            self.notification_images = []
            self.notification_images.append(free_image('mobs/church_volunteers/button.png', scaling.scale_coordinates(global_manager.get('notification_manager').notification_x - 225, 400, global_manager),
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
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program.  When a notification is removed, the next notification is shown, if there is one. Executes notification results,
                such as recruiting a unit, as applicable. Removes dice and other side images as applicable
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
        if len(self.global_manager.get('notification_manager').notification_queue) == 1: #if last notification, create church volunteers if success, remove dice, and allow actions again
            notification_manager.notification_to_front(notification_manager.notification_queue[0])
            for current_die in self.global_manager.get('dice_list'):
                current_die.remove()
            self.global_manager.get('religious_campaign_result')[0].complete_religious_campaign()
            
        elif len(notification_manager.notification_queue) > 0:
            notification_manager.notification_to_front(notification_manager.notification_queue[0])
        if self.is_last: #if is last notification in successful campaign, remove image of church volunteer
            for current_image in self.notification_images:
                current_image.remove()

class advertising_campaign_notification(notification):
    '''
    Notification that does not automatically prompt the user to remove it and shows the results of an advertising campaign when the last notification is removed
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
            boolean is_last: Whether this is the last advertising campaign notification. If it is the last, any side images will be removed when it is removed
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        ''' 
        self.is_last = is_last
        if self.is_last: #if last, show result
            current_merchant = actor_utility.get_selected_list(global_manager)[0]
            self.notification_images = []
            self.notification_images.append(free_image('scenery/resources/' + current_merchant.current_advertised_commodity + '.png', scaling.scale_coordinates(global_manager.get('notification_manager').notification_x - 225, 500,
                global_manager), scaling.scale_width(200, global_manager), scaling.scale_height(200, global_manager), modes, global_manager, True))
            self.notification_images.append(free_image('scenery/resources/plus.png', scaling.scale_coordinates(global_manager.get('notification_manager').notification_x - 125, 600, global_manager),
                scaling.scale_width(100, global_manager), scaling.scale_height(100, global_manager), modes, global_manager, True))
            self.notification_images.append(free_image('scenery/resources/' + current_merchant.current_unadvertised_commodity + '.png', scaling.scale_coordinates(global_manager.get('notification_manager').notification_x - 225, 300,
                global_manager), scaling.scale_width(200, global_manager), scaling.scale_height(200, global_manager), modes, global_manager, True))
            self.notification_images.append(free_image('scenery/resources/minus.png', scaling.scale_coordinates(global_manager.get('notification_manager').notification_x - 125, 400, global_manager),
                scaling.scale_width(100, global_manager), scaling.scale_height(100, global_manager), modes, global_manager, True))
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
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program.  When a notification is removed, the next notification is shown, if there is one. Executes notification results,
                such as recruiting a unit, as applicable. Removes dice and other side images as applicable
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
        if len(self.global_manager.get('notification_manager').notification_queue) == 1: #if last notification, create church volunteers if success, remove dice, and allow actions again
            notification_manager.notification_to_front(notification_manager.notification_queue[0])
            for current_die in self.global_manager.get('dice_list'):
                current_die.remove()
            self.global_manager.get('advertising_campaign_result')[0].complete_advertising_campaign()
            
        elif len(notification_manager.notification_queue) > 0:
            notification_manager.notification_to_front(notification_manager.notification_queue[0])
        if self.is_last: #if is last notification in successful campaign, remove image of church volunteer
            for current_image in self.notification_images:
                current_image.remove()

class conversion_notification(notification):
    '''
    Notification that does not automatically prompt the user to remove it and shows the results of a religious conversion attempt when the last notification is removed
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
            boolean is_last: Whether this is the last religious campaign notification. If it is the last, any side images will be removed when it is removed
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        ''' 
        self.is_last = is_last
        if self.is_last: #if last, show result
            current_head_missionary = actor_utility.get_selected_list(global_manager)[0]
            self.notification_images = []
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
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program.  When a notification is removed, the next notification is shown, if there is one. Executes notification results,
                such as reducing village aggressiveness, as applicable. Removes dice and other side images as applicable
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
        if len(self.global_manager.get('notification_manager').notification_queue) == 1: #if last notification, create church volunteers if success, remove dice, and allow actions again
            notification_manager.notification_to_front(notification_manager.notification_queue[0])
            for current_die in self.global_manager.get('dice_list'):
                current_die.remove()
            self.global_manager.get('conversion_result')[0].complete_conversion()
            
        elif len(notification_manager.notification_queue) > 0:
            notification_manager.notification_to_front(notification_manager.notification_queue[0])
        if self.is_last: #if is last notification in successful campaign, remove image of church volunteer
            for current_image in self.notification_images:
                current_image.remove()

class construction_notification(notification):
    '''
    Notification that does not automatically prompt the user to remove it and shows the results of a construction attempt when the last notification is removed
    '''
    def __init__(self, coordinates, ideal_width, minimum_height, modes, image, message, is_last, global_manager):
        self.is_last = is_last
        if self.is_last: #if last, show result
            current_constructor = actor_utility.get_selected_list(global_manager)[0]
            self.notification_images = []
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
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program.  When a notification is removed, the next notification is shown, if there is one. Executes notification results,
                such as reducing village aggressiveness, as applicable. Removes dice and other side images as applicable
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
            for current_die in self.global_manager.get('dice_list'):
                current_die.remove()
            if self.global_manager.get('construction_result')[0].current_construction_type == 'default':
                self.global_manager.get('construction_result')[0].complete_construction()
            elif self.global_manager.get('construction_result')[0].current_construction_type == 'upgrade':
                self.global_manager.get('construction_result')[0].complete_upgrade()
    
        elif len(notification_manager.notification_queue) > 0:
            notification_manager.notification_to_front(notification_manager.notification_queue[0])
