#Contains functionality for multi-step notifications

from ..constructs.images import free_image
from .notifications import notification
from ..util import scaling, actor_utility, trial_utility

class action_notification(notification):
    '''
    Interactive notification attached in a series to other notifications that is used for dice rolls and other real-time player interactions
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'message': string value - Default text for this label, with lines separated by /n
                'ideal_width': int value - Pixel width that this label will try to retain. Each time a word is added to the label, if the word extends past the ideal width, the next line 
                    will be started
                'minimum_height': int value - Minimum pixel height of this label. Its height will increase if the contained text would extend past the bottom of the label
                'notification_dice': int value - Number of dice allowed to be shown during this notification, allowign the correct set of dice to be shown when multiple notifications queued
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(input_dict, global_manager)
        self.is_action_notification = True
        self.notification_dice = input_dict['notification_dice'] #how many dice are allowed to be shown by selected mob when this notification shown

    def format_message(self):
        '''
        Description:
            Converts this notification's string message to a list of strings, with each string representing a line of text. Each line of text ends when its width exceeds the ideal_width or when a '/n' is encountered in the text. Unlike s
                uperclass, this version removes the automatic prompt to close the notification, as action notifications often require more specific messages not add a prompt to close the notification.
        Input:
            none
        Output:
            None
        '''
        super().format_message()
        self.message.pop(-1)

class dice_rolling_notification(action_notification):
    '''
    Notification that is removed when a dice roll is completed rather than when clicked
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'message': string value - Default text for this label, with lines separated by /n
                'ideal_width': int value - Pixel width that this label will try to retain. Each time a word is added to the label, if the word extends past the ideal width, the next line 
                    will be started
                'minimum_height': int value - Minimum pixel height of this label. Its height will increase if the contained text would extend past the bottom of the label
                'notification_dice': int value - Number of dice allowed to be shown during this notification, allowign the correct set of dice to be shown when multiple notifications queued
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(input_dict, global_manager)
        global_manager.set('current_dice_rolling_notification', self)
        if self.global_manager.get('ongoing_action_type') in ['combat', 'slave_capture', 'slave_trade_suppression']:
            if self.global_manager.get('displayed_mob').is_pmob and (self.global_manager.get('displayed_mob').is_battalion or self.global_manager.get('displayed_mob').is_safari):
                self.global_manager.get('sound_manager').play_sound('gunfire')

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
        return()

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
        if len(self.global_manager.get('dice_list')) > 1: #if there are multiple dice, check if any player-controlled dice are critical successes for promotion
            max_roll = 0
            max_die = 0
            for current_die in self.global_manager.get('dice_list'):
                if not (not current_die.normal_die and current_die.special_die_type == 'red'): #do not include enemy dice in this calculation
                    if current_die.roll_result > max_roll:
                        max_roll = current_die.roll_result
                        max_die = current_die
                if not current_die.normal_die: #change highlight color of special dice to show that roll is complete
                    if current_die.special_die_type == 'green':
                        current_die.outline_color = current_die.outcome_color_dict['crit_success']
                    elif current_die.special_die_type == 'red':
                        current_die.outline_color = current_die.outcome_color_dict['crit_fail']

                if current_die.final_result >= current_die.result_outcome_dict['min_crit_success']:
                    if not self.global_manager.get('displayed_mob').veteran:
                        if not self.global_manager.get('displayed_mob').veteran:
                            self.global_manager.get('sound_manager').play_sound('trumpet_1')

            for current_die in self.global_manager.get('dice_list'):
                if not (not current_die.normal_die and current_die.special_die_type == 'red'):
                    if not current_die == max_die:
                        current_die.normal_die = True
            max_die.highlighted = True
        else: #if only 1 die, check if it is a crtiical success for promotion
            self.global_manager.get('dice_list')[0].highlighted = True
            if self.global_manager.get('dice_list')[0].final_result >= self.global_manager.get('dice_list')[0].result_outcome_dict['min_crit_success']:
                if not self.global_manager.get('displayed_mob') == 'none':
                    if not self.global_manager.get('displayed_mob').veteran:
                        self.global_manager.get('sound_manager').play_sound('trumpet_1')

class exploration_notification(action_notification):
    '''
    Notification that does not automatically prompt the user to remove it and shows the results of exploration when the last notification is removed
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'message': string value - Default text for this label, with lines separated by /n
                'ideal_width': int value - Pixel width that this label will try to retain. Each time a word is added to the label, if the word extends past the ideal width, the next line 
                    will be started
                'minimum_height': int value - Minimum pixel height of this label. Its height will increase if the contained text would extend past the bottom of the label
                'notification_dice': int value - Number of dice allowed to be shown during this notification, allowign the correct set of dice to be shown when multiple notifications queued
                'is_last': boolean value - Whether this is the last exploration notification - if it is last, its side images will be removed along with it
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.is_last = input_dict['is_last']
        if self.is_last:
            current_expedition = global_manager.get('displayed_mob')
            self.notification_images = []
            explored_cell = current_expedition.destination_cell
            explored_tile = explored_cell.tile
            background_dict = {
                'image_id': 'misc/tile_background.png',
                'level': -10
            }
            image_id_list = [background_dict] + explored_tile.get_image_id_list(force_visibility = True) + ['misc/tile_outline.png']
            self.notification_images.append(free_image(image_id_list, scaling.scale_coordinates(global_manager.get('notification_manager').notification_x - 225, 400, global_manager),
                scaling.scale_width(200, global_manager), scaling.scale_height(200, global_manager), input_dict['modes'], global_manager, True))
        super().__init__(input_dict, global_manager)

    def remove(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program. When a notification is removed, the next notification is shown, if there is one
        Input:
            None
        Output:
            None
        '''
        super().remove(handle_next_notification=False)
        notification_manager = self.global_manager.get('notification_manager')
        if len(notification_manager.notification_queue) >= 1:
            notification_manager.notification_queue.pop(0)
        if len(self.global_manager.get('notification_manager').notification_queue) == 1:
            notification_manager.notification_to_front(notification_manager.notification_queue[0])
            if self.global_manager.get('exploration_result')[0].movement_points >= 1: #fix to exploration completing multiple times bug
                self.global_manager.get('exploration_result')[0].complete_exploration() #tells index 0 of exploration result, the explorer object, to finish exploring when notifications removed
                for current_die in self.global_manager.get('dice_list'):
                    current_die.remove_complete()
                for current_minister_image in self.global_manager.get('dice_roll_minister_images'):
                    current_minister_image.remove_complete()
        elif len(notification_manager.notification_queue) > 0:
            notification_manager.notification_to_front(notification_manager.notification_queue[0])
        if self.is_last:
            for current_image in self.notification_images:
                current_image.remove_complete()

class off_tile_exploration_notification(action_notification):
    '''
    Notification that shows a tile explored by an expedition in an adjacent tile, focusing on the new tile and returning minimap to original position upon removal
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'message': string value - Default text for this label, with lines separated by /n
                'ideal_width': int value - Pixel width that this label will try to retain. Each time a word is added to the label, if the word extends past the ideal width, the next line 
                    will be started
                'minimum_height': int value - Minimum pixel height of this label. Its height will increase if the contained text would extend past the bottom of the label
                'notification_dice': int value - Number of dice allowed to be shown during this notification, allowign the correct set of dice to be shown when multiple notifications queued
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.current_expedition = global_manager.get('displayed_mob')
        self.notification_images = []
        
        explored_cell = self.current_expedition.destination_cells.pop(0)
        public_opinion_increase = self.current_expedition.public_opinion_increases.pop(0)
        explored_tile = explored_cell.tile
        if self.current_expedition.current_action_type == 'exploration': #use non-hidden version if exploring
            explored_terrain_image_id = explored_cell.tile.image_dict['default']
            new_visibility = True
        elif self.current_expedition.current_action_type == 'rumor_search': #use current tile image if found rumor location
            explored_terrain_image_id = explored_cell.tile.image.image_id
            new_visibility = explored_cell.visible
        image_id_list = explored_tile.get_image_id_list(force_visibility = new_visibility)
        
        self.notification_images.append(free_image(explored_terrain_image_id, scaling.scale_coordinates(global_manager.get('notification_manager').notification_x - 225, 400, global_manager),
            scaling.scale_width(200, global_manager), scaling.scale_height(200, global_manager), input_dict['modes'], global_manager, True))
        if new_visibility == True and not explored_tile.cell.resource == 'none':
            image_id_list.append(actor_utility.generate_resource_icon(explored_tile, global_manager))
        image_id_list.append('misc/tile_outline.png')
        #although global manager sets to busy here, calling object should also set to busy so that you can't click off before notification appears if another notification is opened when this one is queued
        global_manager.set('ongoing_action', True)
        global_manager.set('ongoing_action_type', self.current_expedition.current_action_type)
        if self.current_expedition.current_action_type == 'exploration':
            explored_cell.set_visibility(True)
        self.notification_images.append(free_image(image_id_list, scaling.scale_coordinates(global_manager.get('notification_manager').notification_x - 225, 400, global_manager),
            scaling.scale_width(200, global_manager), scaling.scale_height(200, global_manager), input_dict['modes'], global_manager, True))
        global_manager.get('public_opinion_tracker').change(public_opinion_increase)
        global_manager.get('minimap_grid').calibrate(explored_cell.x, explored_cell.y)
        super().__init__(input_dict, global_manager)

    def remove(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program. When a notification is removed, the next notification is shown, if there is one
        Input:
            None
        Output:
            None
        '''
        super().remove(handle_next_notification=False)
        self.global_manager.set('ongoing_action', False)
        self.global_manager.set('ongoing_action_type', 'none')
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
            current_image.remove_complete()
        
class trade_notification(action_notification):
    '''
    Notification used during trading that has various behaviors relevant to trading based on the values in its inputted trade_info_dict
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'message': string value - Default text for this label, with lines separated by /n
                'ideal_width': int value - Pixel width that this label will try to retain. Each time a word is added to the label, if the word extends past the ideal width, the next line 
                    will be started
                'minimum_height': int value - Minimum pixel height of this label. Its height will increase if the contained text would extend past the bottom of the label
                'notification_dice': int value - Number of dice allowed to be shown during this notification, allowign the correct set of dice to be shown when multiple notifications queued
                'trade_info_dict': dictionary value - Contains information that affects this notification's behavior, look into if this can be merged with choice_info_dict
                    'is_last', boolean value: If True, this notification removes currently rolling dice when removed
                    'stops_trade', boolean value: If True, trading will stop when this notification is removed
                    'commodity_trade', boolean value: If True, this notification will show a transaction
                    'commodity_trade_type', string value: If equals 'successful_commodity_trade', the trade will be successful and a commodity will be given for the transaction
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.trade_info_dict = input_dict['trade_info_dict']
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
                    scaling.scale_width(200, global_manager), scaling.scale_height(200, global_manager), input_dict['modes'], global_manager, True))
            else:
                consumer_goods_y = 400 #either have icon at 300 and 500 or a single icon at 400
                min_y = 400
            self.notification_images.append(free_image('scenery/resources/trade/sold consumer goods.png', scaling.scale_coordinates(global_manager.get('notification_manager').notification_x - 200, consumer_goods_y, global_manager),
                scaling.scale_width(200, global_manager), scaling.scale_height(200, global_manager), input_dict['modes'], global_manager, True))
            if self.trade_result[3]: #if gets available worker
                background_dict = {
                    'image_id': 'mobs/default/button.png',
                    'size': 1,
                    'x_offset': 0,
                    'y_offset': 0,
                    'level': -10
                } 
                left_worker_dict = {
                    'image_id': 'mobs/African workers/default.png',
                    'size': 0.8,
                    'x_offset': -0.2,
                    'y_offset': 0,
                    'level': 1
                }
                right_worker_dict = left_worker_dict.copy()
                right_worker_dict['x_offset'] *= -1
                button_image_id_list = [background_dict, left_worker_dict, right_worker_dict]
            
                self.notification_images.append(free_image(button_image_id_list, scaling.scale_coordinates(global_manager.get('notification_manager').notification_x - 175, min_y - 175, global_manager),
                    scaling.scale_width(150, global_manager), scaling.scale_height(150, global_manager), input_dict['modes'], global_manager, True))
        elif self.dies:
            self.trade_result = global_manager.get('trade_result') #allows caravan object to be found so that it can die
        super().__init__(input_dict, global_manager)
        
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
            current_image.remove_complete()
        if self.dies:
            caravan = self.trade_result[0]
            village = caravan.images[0].current_cell.village
            warrior = village.spawn_warrior()
            warrior.show_images()
            warrior.attack_on_spawn()
        if self.is_last:
            for current_die in self.global_manager.get('dice_list'):
                current_die.remove_complete()
            for current_minister_image in self.global_manager.get('dice_roll_minister_images'):
                current_minister_image.remove_complete()
        if self.stops_trade:
            self.global_manager.set('ongoing_action', False)
            self.global_manager.set('ongoing_action_type', 'none')

class religious_campaign_notification(action_notification):
    '''
    Notification that does not automatically prompt the user to remove it and shows the results of a religious campaign when the last notification is removed
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'message': string value - Default text for this label, with lines separated by /n
                'ideal_width': int value - Pixel width that this label will try to retain. Each time a word is added to the label, if the word extends past the ideal width, the next line 
                    will be started
                'minimum_height': int value - Minimum pixel height of this label. Its height will increase if the contained text would extend past the bottom of the label
                'notification_dice': int value - Number of dice allowed to be shown during this notification, allowign the correct set of dice to be shown when multiple notifications queued
                'is_last': boolean value - Whether this is the last exploration notification - if it is last, its side images will be removed along with it
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.is_last = input_dict['is_last']
        if self.is_last: #if last, show result
            self.notification_images = []
            background_dict = {
                'image_id': 'mobs/default/button.png',
                'size': 1,
                'x_offset': 0,
                'y_offset': 0,
                'level': -10
            } 
            left_worker_dict = {
                'image_id': 'mobs/church_volunteers/default.png',
                'size': 0.8,
                'x_offset': -0.2,
                'y_offset': 0,
                'level': 1
            }
            right_worker_dict = left_worker_dict.copy()
            right_worker_dict['x_offset'] *= -1
            button_image_id_list = [background_dict, left_worker_dict, right_worker_dict]
            self.notification_images.append(free_image(button_image_id_list, scaling.scale_coordinates(global_manager.get('notification_manager').notification_x - 225, 400, global_manager),
                scaling.scale_width(200, global_manager), scaling.scale_height(200, global_manager), input_dict['modes'], global_manager, True))
        elif len(global_manager.get('notification_manager').notification_queue) == 2: #if 2nd last advertising notification
            if global_manager.get('religious_campaign_result')[2]: #and if success is True, play sound once dice roll finishes
                global_manager.get('sound_manager').dampen_music()
                if global_manager.get('current_country').religion == 'protestant':
                    global_manager.get('sound_manager').play_sound('onward christian soldiers')
                elif global_manager.get('current_country').religion == 'catholic':
                    global_manager.get('sound_manager').play_sound('ave maria')
        super().__init__(input_dict, global_manager)

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
        super().remove(handle_next_notification=False)
        notification_manager = self.global_manager.get('notification_manager')
        if len(notification_manager.notification_queue) >= 1:
            notification_manager.notification_queue.pop(0)
        if len(self.global_manager.get('notification_manager').notification_queue) == 1: #if last notification, create church volunteers if success, remove dice, and allow actions again
            notification_manager.notification_to_front(notification_manager.notification_queue[0])
            for current_die in self.global_manager.get('dice_list'):
                current_die.remove_complete()
            for current_minister_image in self.global_manager.get('dice_roll_minister_images'):
                current_minister_image.remove_complete()
            self.global_manager.get('religious_campaign_result')[0].complete_religious_campaign()
            
        elif len(notification_manager.notification_queue) > 0:
            notification_manager.notification_to_front(notification_manager.notification_queue[0])
        if self.is_last: #if is last notification in successful campaign, remove image of church volunteer
            for current_image in self.notification_images:
                current_image.remove_complete()

class public_relations_campaign_notification(action_notification):
    '''
    Notification that does not automatically prompt the user to remove it and shows the results of a PR campaign when the last notification is removed
    ''' 
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'message': string value - Default text for this label, with lines separated by /n
                'ideal_width': int value - Pixel width that this label will try to retain. Each time a word is added to the label, if the word extends past the ideal width, the next line 
                    will be started
                'minimum_height': int value - Minimum pixel height of this label. Its height will increase if the contained text would extend past the bottom of the label
                'notification_dice': int value - Number of dice allowed to be shown during this notification, allowign the correct set of dice to be shown when multiple notifications queued
                'is_last': boolean value - Whether this is the last exploration notification - if it is last, its side images will be removed along with it
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.is_last = input_dict['is_last']
        super().__init__(input_dict, global_manager)

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
        super().remove(handle_next_notification=False)
        notification_manager = self.global_manager.get('notification_manager')
        if len(notification_manager.notification_queue) >= 1:
            notification_manager.notification_queue.pop(0)
        if len(self.global_manager.get('notification_manager').notification_queue) == 1: #if last notification, create church volunteers if success, remove dice, and allow actions again
            notification_manager.notification_to_front(notification_manager.notification_queue[0])
            for current_die in self.global_manager.get('dice_list'):
                current_die.remove_complete()
            for current_minister_image in self.global_manager.get('dice_roll_minister_images'):
                current_minister_image.remove_complete()
            self.global_manager.get('public_relations_campaign_result')[0].complete_public_relations_campaign()

        elif len(notification_manager.notification_queue) > 0:
            notification_manager.notification_to_front(notification_manager.notification_queue[0])

class trial_notification(action_notification):
    '''
    Notification that does not automatically prompt the user to remove it and shows the results of a trial when the last notification is removed
    '''
    def remove(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program.  When a notification is removed, the next notification is shown, if there is one. Executes notification results,
                such as recruiting a unit, as applicable. Removes dice and other side images as applicable. A trial notification in a series of evidence rolls stops the series and wins the trial if it rolls a 6
        Input:
            None
        Output:
            None
        '''
        super().remove(handle_next_notification=False)
        for current_die in self.global_manager.get('dice_list'):
            current_die.remove_complete()
        previous_roll = self.global_manager.get('trial_rolls').pop(0)
        if previous_roll >= 5:
            self.global_manager.set('trial_rolls', []) #stop trial after success
        if len(self.global_manager.get('trial_rolls')) > 0:
            trial_utility.display_evidence_roll(self.global_manager)
        else:
            trial_utility.complete_trial(previous_roll, self.global_manager)

        notification_manager = self.global_manager.get('notification_manager')
        if len(notification_manager.notification_queue) >= 1:
            notification_manager.notification_queue.pop(0)
        if len(notification_manager.notification_queue) > 0:
            notification_manager.notification_to_front(notification_manager.notification_queue[0])

class advertising_campaign_notification(action_notification):
    '''
    Notification that does not automatically prompt the user to remove it and shows the results of an advertising campaign when the last notification is removed
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'message': string value - Default text for this label, with lines separated by /n
                'ideal_width': int value - Pixel width that this label will try to retain. Each time a word is added to the label, if the word extends past the ideal width, the next line 
                    will be started
                'minimum_height': int value - Minimum pixel height of this label. Its height will increase if the contained text would extend past the bottom of the label
                'notification_dice': int value - Number of dice allowed to be shown during this notification, allowign the correct set of dice to be shown when multiple notifications queued
                'is_last': boolean value - Whether this is the last exploration notification - if it is last, its side images will be removed along with it
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.is_last = input_dict['is_last']
        if self.is_last: #if last, show result
            current_merchant = global_manager.get('displayed_mob')
            self.notification_images = []
            self.notification_images.append(free_image('scenery/resources/' + current_merchant.current_advertised_commodity + '.png', scaling.scale_coordinates(global_manager.get('notification_manager').notification_x - 225, 500,
                global_manager), scaling.scale_width(200, global_manager), scaling.scale_height(200, global_manager), input_dict['modes'], global_manager, True))
            self.notification_images.append(free_image('scenery/resources/plus.png', scaling.scale_coordinates(global_manager.get('notification_manager').notification_x - 125, 600, global_manager),
                scaling.scale_width(100, global_manager), scaling.scale_height(100, global_manager), input_dict['modes'], global_manager, True))
            self.notification_images.append(free_image('scenery/resources/' + current_merchant.current_unadvertised_commodity + '.png', scaling.scale_coordinates(global_manager.get('notification_manager').notification_x - 225, 300,
                global_manager), scaling.scale_width(200, global_manager), scaling.scale_height(200, global_manager), input_dict['modes'], global_manager, True))
            self.notification_images.append(free_image('scenery/resources/minus.png', scaling.scale_coordinates(global_manager.get('notification_manager').notification_x - 125, 400, global_manager),
                scaling.scale_width(100, global_manager), scaling.scale_height(100, global_manager), input_dict['modes'], global_manager, True))
        elif len(global_manager.get('notification_manager').notification_queue) == 2: #if 2nd last advertising notification
            if global_manager.get('advertising_campaign_result')[2]: #and if success is True, play sound once dice roll finishes
                global_manager.get('sound_manager').dampen_music(0.75)
                channel = global_manager.get('sound_manager').play_sound('voices/advertising/messages/' + str(global_manager.get('current_sound_file_index')), 1.0)
                global_manager.get('sound_manager').queue_sound('voices/advertising/commodities/' + global_manager.get('current_advertised_commodity'), channel)
        super().__init__(input_dict, global_manager)

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
        super().remove(handle_next_notification=False)
        notification_manager = self.global_manager.get('notification_manager')
        if len(notification_manager.notification_queue) >= 1:
            notification_manager.notification_queue.pop(0)
        if len(self.global_manager.get('notification_manager').notification_queue) == 1: #if last notification, create church volunteers if success, remove dice, and allow actions again
            notification_manager.notification_to_front(notification_manager.notification_queue[0])
            for current_die in self.global_manager.get('dice_list'):
                current_die.remove_complete()
            for current_minister_image in self.global_manager.get('dice_roll_minister_images'):
                current_minister_image.remove_complete()
            self.global_manager.get('advertising_campaign_result')[0].complete_advertising_campaign()
            
        elif len(notification_manager.notification_queue) > 0:
            notification_manager.notification_to_front(notification_manager.notification_queue[0])
        if self.is_last: #if is last notification in successful campaign, remove image of church volunteer
            for current_image in self.notification_images:
                current_image.remove_complete()

class conversion_notification(action_notification):
    '''
    Notification that does not automatically prompt the user to remove it and shows the results of a religious conversion attempt when the last notification is removed
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'message': string value - Default text for this label, with lines separated by /n
                'ideal_width': int value - Pixel width that this label will try to retain. Each time a word is added to the label, if the word extends past the ideal width, the next line 
                    will be started
                'minimum_height': int value - Minimum pixel height of this label. Its height will increase if the contained text would extend past the bottom of the label
                'notification_dice': int value - Number of dice allowed to be shown during this notification, allowign the correct set of dice to be shown when multiple notifications queued
                'is_last': boolean value - Whether this is the last exploration notification - if it is last, its side images will be removed along with it
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.is_last = input_dict['is_last']
        if self.is_last: #if last, show result
            self.notification_images = []
        elif len(global_manager.get('notification_manager').notification_queue) == 2: #if 2nd last advertising notification
            if global_manager.get('conversion_result')[4]: #and if success is True, play sound once dice roll finishes
                global_manager.get('sound_manager').dampen_music()
                if global_manager.get('current_country').religion == 'protestant':
                    global_manager.get('sound_manager').play_sound('onward christian soldiers')
                elif global_manager.get('current_country').religion == 'catholic':
                    global_manager.get('sound_manager').play_sound('ave maria')
        super().__init__(input_dict, global_manager)

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
        super().remove(handle_next_notification=False)
        notification_manager = self.global_manager.get('notification_manager')
        if len(notification_manager.notification_queue) >= 1:
            notification_manager.notification_queue.pop(0)
        if len(self.global_manager.get('notification_manager').notification_queue) == 1: #if last notification, create church volunteers if success, remove dice, and allow actions again
            notification_manager.notification_to_front(notification_manager.notification_queue[0])
            for current_die in self.global_manager.get('dice_list'):
                current_die.remove_complete()
            for current_minister_image in self.global_manager.get('dice_roll_minister_images'):
                current_minister_image.remove_complete()
            self.global_manager.get('conversion_result')[0].complete_conversion()
            
        elif len(notification_manager.notification_queue) > 0:
            notification_manager.notification_to_front(notification_manager.notification_queue[0])
        if self.is_last: #if is last notification in successful campaign, remove image of church volunteer
            for current_image in self.notification_images:
                current_image.remove_complete()

class rumor_search_notification(action_notification):
    '''
    Notification that does not automatically prompt the user to remove it and shows the results of a rumor search attempt when the last notification is removed
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'message': string value - Default text for this label, with lines separated by /n
                'ideal_width': int value - Pixel width that this label will try to retain. Each time a word is added to the label, if the word extends past the ideal width, the next line 
                    will be started
                'minimum_height': int value - Minimum pixel height of this label. Its height will increase if the contained text would extend past the bottom of the label
                'notification_dice': int value - Number of dice allowed to be shown during this notification, allowign the correct set of dice to be shown when multiple notifications queued
                'is_last': boolean value - Whether this is the last exploration notification - if it is last, its side images will be removed along with it
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.is_last = input_dict['is_last']
        if self.is_last: #if last, show result
            self.notification_images = []
        super().__init__(input_dict, global_manager)

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
        super().remove(handle_next_notification=False)
        notification_manager = self.global_manager.get('notification_manager')
        if len(notification_manager.notification_queue) >= 1:
            notification_manager.notification_queue.pop(0)
        if len(self.global_manager.get('notification_manager').notification_queue) == 1 and not self.global_manager.get('notification_manager').notification_type_queue[0] in ['none', 'off_tile_exploration']: #if last notification, remove dice and complete action
            notification_manager.notification_to_front(notification_manager.notification_queue[0])
            for current_die in self.global_manager.get('dice_list'):
                current_die.remove_complete()
            for current_minister_image in self.global_manager.get('dice_roll_minister_images'):
                current_minister_image.remove_complete()
            self.global_manager.get('rumor_search_result')[0].complete_rumor_search()
            
        elif len(notification_manager.notification_queue) > 0:
            notification_manager.notification_to_front(notification_manager.notification_queue[0])
        if self.is_last: #if is last notification in successful campaign, remove any attached images
            for current_image in self.notification_images:
                current_image.remove_complete()

class artifact_search_notification(action_notification):
    '''
    Notification that does not automatically prompt the user to remove it and shows the results of an artifact search attempt when the last notification is removed
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'message': string value - Default text for this label, with lines separated by /n
                'ideal_width': int value - Pixel width that this label will try to retain. Each time a word is added to the label, if the word extends past the ideal width, the next line 
                    will be started
                'minimum_height': int value - Minimum pixel height of this label. Its height will increase if the contained text would extend past the bottom of the label
                'notification_dice': int value - Number of dice allowed to be shown during this notification, allowign the correct set of dice to be shown when multiple notifications queued
                'is_last': boolean value - Whether this is the last exploration notification - if it is last, its side images will be removed along with it
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.is_last = input_dict['is_last']
        if self.is_last: #if last, show result
            self.notification_images = []
        super().__init__(input_dict, global_manager)

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
        super().remove(handle_next_notification=False)
        notification_manager = self.global_manager.get('notification_manager')
        if len(notification_manager.notification_queue) >= 1:
            notification_manager.notification_queue.pop(0)
        if len(notification_manager.notification_type_queue) > 0 and not notification_manager.notification_type_queue[0] == 'roll':
            for current_die in self.global_manager.get('dice_list'):
                current_die.remove_complete()
            for current_minister_image in self.global_manager.get('dice_roll_minister_images'):
                current_minister_image.remove_complete()
        if len(notification_manager.notification_queue) > 0 and notification_manager.notification_type_queue[0] in ['final_artifact_search', 'default'] and not self.is_last: #if roll failed or succeeded and about to complete
            self.global_manager.get('artifact_search_result')[0].complete_artifact_search()
            notification_manager.notification_to_front(notification_manager.notification_queue[0])

        elif len(notification_manager.notification_queue) > 0:
            notification_manager.notification_to_front(notification_manager.notification_queue[0])

class capture_slaves_notification(action_notification):
    '''
    Notification that does not automatically prompt the user to remove it and shows the results of a slave capture attempt when the last notification is removed
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'message': string value - Default text for this label, with lines separated by /n
                'ideal_width': int value - Pixel width that this label will try to retain. Each time a word is added to the label, if the word extends past the ideal width, the next line 
                    will be started
                'minimum_height': int value - Minimum pixel height of this label. Its height will increase if the contained text would extend past the bottom of the label
                'notification_dice': int value - Number of dice allowed to be shown during this notification, allowign the correct set of dice to be shown when multiple notifications queued
                'is_last': boolean value - Whether this is the last exploration notification - if it is last, its side images will be removed along with it
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.is_last = input_dict['is_last']
        if self.is_last: #if last, show result
            self.notification_images = []
            background_dict = {
                'image_id': 'mobs/default/button.png',
                'size': 1,
                'x_offset': 0,
                'y_offset': 0,
                'level': -10
            } 
            left_worker_dict = {
                'image_id': 'mobs/Slave workers/default.png',
                'size': 0.8,
                'x_offset': -0.2,
                'y_offset': 0,
                'level': 1
            }
            right_worker_dict = left_worker_dict.copy()
            right_worker_dict['x_offset'] *= -1
            button_image_id_list = [background_dict, left_worker_dict, right_worker_dict]
            self.notification_images.append(free_image(button_image_id_list, scaling.scale_coordinates(global_manager.get('notification_manager').notification_x - 225, 400, global_manager),
                scaling.scale_width(200, global_manager), scaling.scale_height(200, global_manager), input_dict['modes'], global_manager, True))
        super().__init__(input_dict, global_manager)

    def remove(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program.  When a notification is removed, the next notification is shown, if there is one. Executes notification results,
                such as spawning slave unit, as applicable. Removes dice and other side images as applicable
        Input:
            None
        Output:
            None
        '''
        super().remove(handle_next_notification=False)
        notification_manager = self.global_manager.get('notification_manager')
        if len(notification_manager.notification_queue) >= 1:
            notification_manager.notification_queue.pop(0)
        if len(self.global_manager.get('notification_manager').notification_queue) == 1: #if last notification, create church volunteers if success, remove dice, and allow actions again
            notification_manager.notification_to_front(notification_manager.notification_queue[0])
            for current_die in self.global_manager.get('dice_list'):
                current_die.remove_complete()
            for current_minister_image in self.global_manager.get('dice_roll_minister_images'):
                current_minister_image.remove_complete()
            self.global_manager.get('capture_slaves_result')[0].complete_capture_slaves()
            
        elif len(notification_manager.notification_queue) > 0:
            notification_manager.notification_to_front(notification_manager.notification_queue[0])
        if self.is_last: #if is last notification in successful capture, remove image of slaves
            for current_image in self.notification_images:
                current_image.remove_complete()

class suppress_slave_trade_notification(action_notification):
    '''
    Notification that does not automatically prompt the user to remove it and shows the results of a slave trade suppression attempt when the last notification is removed
    '''
    def __init__(self, input_dict, global_manager):
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
            boolean is_last: Whether this is the last slave trade suppression notification. If it is the last, any side images will be removed when it is removed
            int notification_dice: Number of dice allowed to be shown during this notification, allowing the correct set of dice to be shown when multiple notifications are queued
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        ''' 
        self.is_last = input_dict['is_last']
        if self.is_last: #if last, show result
            self.notification_images = []
        super().__init__(input_dict, global_manager)

    def remove(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program.  When a notification is removed, the next notification is shown, if there
            is one. Executes notification results, as applicable. Removes dice and other side images as applicable
        Input:
            None
        Output:
            None
        '''
        super().remove(handle_next_notification=False)
        notification_manager = self.global_manager.get('notification_manager')
        if len(notification_manager.notification_queue) >= 1:
            notification_manager.notification_queue.pop(0)
        if len(self.global_manager.get('notification_manager').notification_queue) == 1 and not self.global_manager.get('notification_manager').notification_type_queue[0] == 'none': #if last notification, remove dice and complete action
            notification_manager.notification_to_front(notification_manager.notification_queue[0])
            for current_die in self.global_manager.get('dice_list'):
                current_die.remove_complete()
            for current_minister_image in self.global_manager.get('dice_roll_minister_images'):
                current_minister_image.remove_complete()
            self.global_manager.get('suppress_slave_trade_result')[0].complete_suppress_slave_trade()
            
        elif len(notification_manager.notification_queue) > 0:
            notification_manager.notification_to_front(notification_manager.notification_queue[0])

class construction_notification(action_notification):
    '''
    Notification that does not automatically prompt the user to remove it and shows the results of a construction attempt when the last notification is removed
    '''
    def __init__(self, input_dict, global_manager):
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
            boolean is_last: Whether this is the last construction notification. If it is the last, any side images will be removed when it is removed
            int notification_dice: Number of dice allowed to be shown during this notification, allowing the correct set of dice to be shown when multiple notifications are queued
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.is_last = input_dict['is_last']
        if self.is_last: #if last, show result
            self.notification_images = []
        elif len(global_manager.get('notification_manager').notification_queue) == 2:
            if global_manager.get('construction_result')[2] and global_manager.get('construction_result')[3] == 'mission': #if building mission success is True, play sound once dice roll finishes
                global_manager.get('sound_manager').dampen_music()
                if global_manager.get('current_country').religion == 'protestant':
                    global_manager.get('sound_manager').play_sound('onward christian soldiers')
                elif global_manager.get('current_country').religion == 'catholic':
                    global_manager.get('sound_manager').play_sound('ave maria')
        super().__init__(input_dict, global_manager)

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
        super().remove(handle_next_notification=False)
        notification_manager = self.global_manager.get('notification_manager')
        if len(notification_manager.notification_queue) >= 1:
            notification_manager.notification_queue.pop(0)
        if len(self.global_manager.get('notification_manager').notification_queue) == 1:
            notification_manager.notification_to_front(notification_manager.notification_queue[0])
            for current_die in self.global_manager.get('dice_list'):
                current_die.remove_complete()
            for current_minister_image in self.global_manager.get('dice_roll_minister_images'):
                current_minister_image.remove_complete()
            constructor = self.global_manager.get('construction_result')[0]
            if constructor.current_construction_type == 'default':
                constructor.complete_construction()
            elif constructor.current_construction_type == 'upgrade':
                constructor.complete_upgrade()
            elif constructor.current_construction_type == 'repair':
                constructor.complete_repair()
    
        elif len(notification_manager.notification_queue) > 0:
            notification_manager.notification_to_front(notification_manager.notification_queue[0])

class combat_notification(action_notification):
    '''
    Notification that does not automatically prompt the user to remove it and shows the results of a combat when the last notification is removed
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'message': string value - Default text for this label, with lines separated by /n
                'ideal_width': int value - Pixel width that this label will try to retain. Each time a word is added to the label, if the word extends past the ideal width, the next line 
                    will be started
                'minimum_height': int value - Minimum pixel height of this label. Its height will increase if the contained text would extend past the bottom of the label
                'notification_dice': int value - Number of dice allowed to be shown during this notification, allowign the correct set of dice to be shown when multiple notifications queued
                'is_last': boolean value - Whether this is the last exploration notification - if it is last, its side images will be removed along with it
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.is_last = input_dict['is_last']
        if len(global_manager.get('combatant_images')) == 0: #if none already exist
            image_x = global_manager.get('notification_manager').notification_x - 165#175
            if input_dict['notification_dice'] > 2:
                image_x -= 60
            background_dict = {
                'image_id': 'misc/mob_background.png',
                'size': 1,
                'x_offset': 0,
                'y_offset': 0,
                'level': -10
            }
            pmob_image_id_list = [background_dict] + global_manager.get('displayed_mob').get_image_id_list() + ['misc/pmob_outline.png']
            global_manager.get('combatant_images').append(free_image(pmob_image_id_list, scaling.scale_coordinates(image_x, 280, global_manager),
                scaling.scale_width(150, global_manager), scaling.scale_height(150, global_manager), input_dict['modes'], global_manager, True))
            npmob_image_id_list = [background_dict] + global_manager.get('displayed_mob').current_enemy.get_image_id_list() + ['misc/pmob_outline.png']
            global_manager.get('combatant_images').append(free_image(npmob_image_id_list, scaling.scale_coordinates(image_x, 670, global_manager),
                scaling.scale_width(150, global_manager), scaling.scale_height(150, global_manager), input_dict['modes'], global_manager, True))  
        super().__init__(input_dict, global_manager)

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
        super().remove(handle_next_notification=False)
        notification_manager = self.global_manager.get('notification_manager')
        if len(notification_manager.notification_queue) >= 1:
            notification_manager.notification_queue.pop(0)
        if len(self.global_manager.get('notification_manager').notification_queue) == 1:
            notification_manager.notification_to_front(notification_manager.notification_queue[0])
            for current_die in self.global_manager.get('dice_list'):
                current_die.remove_complete()
            for current_minister_image in self.global_manager.get('dice_roll_minister_images'):
                current_minister_image.remove_complete()
    
        elif len(notification_manager.notification_queue) > 0:
            notification_manager.notification_to_front(notification_manager.notification_queue[0])

        if self.is_last:
            self.global_manager.get('combat_result')[0].complete_combat()
            for current_image in self.global_manager.get('combatant_images'):
                current_image.remove_complete()
            self.global_manager.set('combatant_images', [])
