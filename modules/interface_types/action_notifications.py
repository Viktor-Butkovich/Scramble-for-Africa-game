#Contains functionality for multi-step notifications

from .notifications import notification
from ..util import scaling, trial_utility, action_utility
import modules.constants.constants as constants
import modules.constants.status as status
import modules.constants.flags as flags

class action_notification(notification):
    '''
    Notification that supports attached interface elements
    '''
    def __init__(self, input_dict):
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
                'attached_interface_elements' = None: list value - Interface elements, either in initialized or input_dict form, to add to this notification's
                    sibling ordered collection
                'transfer_interface_elements' = False: boolean value - Whether this notification's sibling ordered collection's member should be transferred
                    to that of the next action notification on removal
                'on_remove' = None: function value - Function to run after this notification is removed
        Output:
            None
        '''
        super().__init__(input_dict)
        self.attached_interface_elements = input_dict.get('attached_interface_elements', None)
        if self.attached_interface_elements:
            if self.attached_interface_elements:
                self.insert_collection_above(override_input_dict={
                    'coordinates': (self.x, 0)
                })
                self.parent_collection.can_show_override = self
                self.set_origin(input_dict['coordinates'][0], input_dict['coordinates'][1])

                notification_manager = constants.notification_manager
                column_increment = 120
                collection_y = notification_manager.default_notification_y - (notification_manager.default_notification_height / 2)
                self.notification_ordered_collection = constants.actor_creation_manager.create_interface_element(
                    action_utility.generate_action_ordered_collection_input_dict(
                        scaling.scale_coordinates(-1 * column_increment + (column_increment / 2), collection_y),
                        override_input_dict = {'parent_collection': self.parent_collection,
                                               'second_dimension_increment': scaling.scale_width(column_increment),
                                               'anchor_coordinate': scaling.scale_height(notification_manager.default_notification_height / 2)
                        }
                    )
                )

                index = 0
                for element_input_dict in self.attached_interface_elements:
                    if type(element_input_dict) == dict:
                        element_input_dict['parent_collection'] = self.notification_ordered_collection #self.parent_collection
                        self.attached_interface_elements[index] = constants.actor_creation_manager.create_interface_element(element_input_dict) #if given input dict, create it and add it to notification
                    else:
                        self.notification_ordered_collection.add_member(element_input_dict, member_config=element_input_dict.transfer_info_dict)
                    index += 1

        self.transfer_interface_elements = input_dict.get('transfer_interface_elements', False)

    def on_click(self):
        '''
        Description:
            Controls this notification's behavior when clicked - action notifications recursively remove their automatically generated parent collections and
                transfer sibling ordered collection's interface elements, if applicable
        Input:
            None
        Output:
            None
        '''
        transferred_interface_elements = []
        if self.attached_interface_elements and self.transfer_interface_elements:
            transferred_interface_elements = []
            for interface_element in self.notification_ordered_collection.members.copy():
                for key in self.notification_ordered_collection.second_dimension_coordinates:
                    if interface_element in self.notification_ordered_collection.second_dimension_coordinates[key]:
                        second_dimension_coordinate = int(key)
                interface_element.transfer_info_dict = {
                    'x_offset': interface_element.x_offset,
                    'y_offset': interface_element.y_offset,
                    'order_x_offset': interface_element.order_x_offset,
                    'order_y_offset': interface_element.order_y_offset,
                    'second_dimension_coordinate': second_dimension_coordinate,
                    'order_overlap': interface_element in self.notification_ordered_collection.order_overlap_list,
                    'order_exempt': interface_element in self.notification_ordered_collection.order_exempt_list
                }

                self.notification_ordered_collection.remove_member(interface_element)
                transferred_interface_elements.append(interface_element)

        if self.has_parent_collection:
            self.parent_collection.remove_recursive(complete=False)
        else:
            self.remove()
        constants.notification_manager.handle_next_notification(transferred_interface_elements=transferred_interface_elements)

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
    def __init__(self, input_dict):
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
        Output:
            None
        '''
        super().__init__(input_dict)
        if status.ongoing_action_type in ['combat', 'slave_capture']:
            if status.displayed_mob.is_pmob and (status.displayed_mob.is_battalion or status.displayed_mob.is_safari):
                constants.sound_manager.play_sound('gunfire')

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

    def on_click(self, die_override=False):
        '''
        Description:
            Controls this notification's behavior when clicked. Unlike superclass, dice rolling notifications are not removed when clicked
        Input:
            None
        Output:
            None
        '''
        if die_override:
            super().on_click()
        else:
            return

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
        num_dice = len(status.dice_list)
        if num_dice > 1: #if there are multiple dice, check if any player-controlled dice are critical successes for promotion
            max_roll = 0
            max_die = 0
            for current_die in status.dice_list:
                if not (not current_die.normal_die and current_die.special_die_type == 'red'): #do not include enemy dice in this calculation
                    if current_die.roll_result > max_roll:
                        max_roll = current_die.roll_result
                        max_die = current_die
                if not current_die.normal_die: #change highlight color of special dice to show that roll is complete
                    if current_die.special_die_type == 'green':
                        current_die.outline_color = current_die.outcome_color_dict['crit_success']
                    elif current_die.special_die_type == 'red':
                        current_die.outline_color = current_die.outcome_color_dict['crit_fail']

            for current_die in status.dice_list:
                if not (not current_die.normal_die and current_die.special_die_type == 'red'):
                    if not current_die == max_die:
                        current_die.normal_die = True
            max_die.highlighted = True
        elif num_dice: #if only 1 die, check if it is a crtiical success for promotion
            status.dice_list[0].highlighted = True

class off_tile_exploration_notification(action_notification):
    '''
    Notification that shows a tile explored by an expedition in an adjacent tile, focusing on the new tile and returning minimap to original position upon removal
    '''
    def __init__(self, input_dict):
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
        Output:
            None
        '''
        cell = input_dict['extra_parameters']['cell']
        reveal_cell = input_dict['extra_parameters'].get('reveal_cell', True)
        public_opinion_increase = input_dict['extra_parameters'].get('public_opinion_increase', 0)

        if (not 'attached_interface_elements' in input_dict) or not input_dict['attached_interface_elements']:
            input_dict['attached_interface_elements'] = []
        input_dict['attached_interface_elements'].append(action_utility.generate_free_image_input_dict(
                action_utility.generate_tile_image_id_list(cell, force_visibility=(reveal_cell or cell.visible)),
                250,
                override_input_dict={
                    'member_config': {
                        'second_dimension_coordinate': -1, 'centered': True
                    }
                }
            ))

        flags.ongoing_action = True
        status.ongoing_action_type = 'exploration'
        if reveal_cell:
            cell.set_visibility(True)
        constants.public_opinion_tracker.change(public_opinion_increase)
        status.minimap_grid.calibrate(cell.x, cell.y)
        super().__init__(input_dict)

    def remove(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program. When a notification is removed, the next notification is shown, if there is one
        Input:
            None
        Output:
            None
        '''
        status.minimap_grid.calibrate(status.displayed_mob.x, status.displayed_mob.y)
        flags.ongoing_action = False
        status.ongoing_action_type = None
        super().remove()

class trade_notification(action_notification):
    '''
    Notification used during trading that has various behaviors relevant to trading based on the values in its inputted trade_info_dict
    '''
    def __init__(self, input_dict):
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
            self.trade_result = {} #trade_result
            consumer_goods_y = 0
            if self.commodity_trade_type == 'successful_commodity_trade':
                consumer_goods_y = 500
                min_y = 300
                self.notification_images.append(constants.actor_creation_manager.create_interface_element({
                    'image_id': 'scenery/resources/' + self.trade_result[2] + '.png',
                    'coordinates': scaling.scale_coordinates(constants.notification_manager.notification_x - 200, 300),
                    'width': scaling.scale_width(200),
                    'height': scaling.scale_height(200),
                    'modes': input_dict['modes'],
                    'to_front': True,
                    'init_type': 'free image'
                }))
            else:
                consumer_goods_y = 400 #either have icon at 300 and 500 or a single icon at 400
                min_y = 400

            self.notification_images.append(constants.actor_creation_manager.create_interface_element({
                'image_id': 'scenery/resources/trade/sold consumer goods.png',
                'coordinates': scaling.scale_coordinates(constants.notification_manager.notification_x - 200, consumer_goods_y),
                'width': scaling.scale_width(200),
                'height': scaling.scale_height(200),
                'modes': input_dict['modes'],
                'to_front': True,
                'init_type': 'free image'
            }))

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

                self.notification_images.append(constants.actor_creation_manager.create_interface_element({
                    'image_id': button_image_id_list,
                    'coordinates': scaling.scale_coordinates(constants.notification_manager.notification_x - 175, min_y - 175),
                    'width': scaling.scale_width(150),
                    'height': scaling.scale_height(150),
                    'modes': input_dict['modes'],
                    'to_front': True,
                    'init_type': 'free image'
                }))

        elif self.dies:
            self.trade_result = {} #trade result, #allows caravan object to be found so that it can die
        super().__init__(input_dict)
        
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
        if self.stops_trade:
            flags.ongoing_action = False
            status.ongoing_action_type = None

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
        for current_die in status.dice_list:
            current_die.remove_complete()
        previous_roll = status.trial_rolls.pop(0)
        if previous_roll >= 5:
            status.trial_rolls = [] #stop trial after success
        if len(status.trial_rolls) > 0:
            trial_utility.display_evidence_roll()
        else:
            trial_utility.complete_trial(previous_roll)

        notification_manager = constants.notification_manager
        if len(notification_manager.notification_queue) >= 1:
            notification_manager.notification_queue.pop(0)
        if len(notification_manager.notification_queue) > 0:
            notification_manager.notification_to_front(notification_manager.notification_queue[0])

class artifact_search_notification(action_notification):
    '''
    Notification that does not automatically prompt the user to remove it and shows the results of an artifact search attempt when the last notification is removed
    '''
    def __init__(self, input_dict):
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
        Output:
            None
        '''
        self.is_last = input_dict['is_last']
        if self.is_last: #if last, show result
            self.notification_images = []
        super().__init__(input_dict)

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
        notification_manager = constants.notification_manager
        if len(notification_manager.notification_queue) >= 1:
            notification_manager.notification_queue.pop(0)
        if len(notification_manager.notification_queue) > 0 and notification_manager.notification_type_queue[0] in ['final_artifact_search', 'default'] and not self.is_last: #if roll failed or succeeded and about to complete
            #artifact_search_result[0].complete_artifact_search()
            notification_manager.notification_to_front(notification_manager.notification_queue[0])

        elif len(notification_manager.notification_queue) > 0:
            notification_manager.notification_to_front(notification_manager.notification_queue[0])

class capture_slaves_notification(action_notification):
    '''
    Notification that does not automatically prompt the user to remove it and shows the results of a slave capture attempt when the last notification is removed
    '''
    def __init__(self, input_dict):
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
            self.notification_images.append(constants.actor_creation_manager.create_interface_element({
                'image_id': button_image_id_list,
                'coordinates': scaling.scale_coordinates(constants.notification_manager.notification_x - 225, 400),
                'width': scaling.scale_width(200),
                'height': scaling.scale_height(200),
                'modes': input_dict['modes'],
                'to_front': True,
                'init_type': 'free image'
            }))
        super().__init__(input_dict)

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
        notification_manager = constants.notification_manager
        if len(notification_manager.notification_queue) >= 1:
            notification_manager.notification_queue.pop(0)
        if len(constants.notification_manager.notification_queue) == 1: #if last notification, create church volunteers if success, remove dice, and allow actions again
            notification_manager.notification_to_front(notification_manager.notification_queue[0])
            #capture_slaves_result[0].complete_capture_slaves()
            
        elif len(notification_manager.notification_queue) > 0:
            notification_manager.notification_to_front(notification_manager.notification_queue[0])
        if self.is_last: #if is last notification in successful capture, remove image of slaves
            for current_image in self.notification_images:
                current_image.remove_complete()
