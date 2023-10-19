from ...util import scaling, text_utility
import modules.constants.constants as constants

class notification_manager_template():
    '''
    Object that controls the displaying of notifications
    '''
    def __init__(self, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.notification_queue = []
        self.global_manager = global_manager
        self.locked = False
        self.default_notification_y = 500
        self.default_notification_height = 300
        self.update_notification_layout()
        self.notification_modes = ['strategic', 'europe', 'ministers', 'trial', 'main_menu', 'new_game_setup']

    def update_notification_layout(self, notification_height=0):
        '''
        Description:
            Changes where notifications are displayed depending on the current game mode to avoid blocking relevant information. Also changes the height of the notification based on how much text it contains
        Input:
            int notification_height = 0: Height in pixels of the notification text. If the notification text height is greater than the default notification height, the notification will scale its height to the text
        Output:
            None
        '''
        self.notification_width = 500
        self.notification_height = self.default_notification_height
        self.notification_y = self.default_notification_y
        if self.global_manager.get('current_game_mode') in ['strategic', 'none']: #move notifications out of way of minimap on strategic mode or during setup
            self.notification_x = self.global_manager.get('minimap_grid_x') - (self.notification_width + 40)
        else: #show notifications in center on europe mode
            self.notification_x = 610
        if notification_height > self.notification_height:
            self.notification_height = notification_height
        self.notification_y -= self.notification_height / 2

    def format_message(self, message):
        new_message = []
        next_line = ''
        next_word = ''
        font_size = 25
        font_name = self.global_manager.get('font_name')
        for index in range(len(message)):
            if not ((not (index + 2) > len(message) and message[index] + message[index + 1]) == '/n'): #don't add if /n
                if not (index > 0 and message[index - 1] + message[index] == '/n'): #if on n after /, skip
                    next_word += message[index]
            if message[index] == ' ':
                if text_utility.message_width(next_line + next_word, font_size, font_name) > self.notification_width:
                    new_message.append(next_line)
                    next_line = ''
                next_line += next_word
                next_word = ''
            elif (not (index + 2) > len(message) and message[index] + message[index + 1]) == '/n': #don't check for /n if at last index
                new_message.append(next_line)
                next_line = ''
                next_line += next_word
                next_word = ''
        if text_utility.message_width(next_line + next_word, font_size, font_name) > self.notification_width:
            new_message.append(next_line)
            next_line = ''
        next_line += next_word
        new_message.append(next_line)
        return(new_message)
    '''
    def get_notification_height(self, notification_text):
        
        Description:
            Returns the height in pixels of the inputted text if it were put in a notification
        Input:
            string notification_text: Text that will appear on the notification with lines separated by /n
        Output:
            int: height in pixels of the inputted text if it were put in a notification
        
        new_message = []
        next_line = ''
        next_word = ''
        font_size = 25 #scaling.scale_height(25, self.global_manager) #self.global_manager.get('font_size') #25
        font_name = self.global_manager.get('font_name')
        font = pygame.font.SysFont(font_name, font_size)
        for index in range(len(notification_text)):
            if not ((not (index + 2) > len(notification_text) and notification_text[index] + notification_text[index + 1]) == '/n'): #don't add if /n
                if not (index > 0 and notification_text[index - 1] + notification_text[index] == '/n'): #if on n after /, skip
                    next_word += notification_text[index]
            if notification_text[index] == ' ':
                if text_tools.message_width(next_line + next_word, font_size, font_name) > self.notification_width:
                    new_message.append(next_line)
                    next_line = ''
                next_line += next_word
                next_word = ''
            elif (not (index + 2) > len(notification_text) and notification_text[index] + notification_text[index + 1]) == '/n': #don't check for /n if at last index
                new_message.append(next_line)
                next_line = ''
                next_line += next_word
                next_word = ''
        if text_tools.message_width(next_line + next_word, font_size, font_name) > self.notification_width:
            new_message.append(next_line)
            next_line = ''
        next_line += next_word
        new_message.append(next_line)
        new_message.append('Click to remove this notification.')
        return(len(new_message) * font_size)#self.message = new_message
    '''

    def handle_next_notification(self, transferred_interface_elements = None):
        '''
        Description:
            Creates the next queued notification, if any, whenever a notification is removed
        Input:
            none
        Output:
            None
        '''
        valid_transfer = False
        if self.global_manager.get('displayed_notification') == 'none':
            if self.notification_queue:
                if transferred_interface_elements and (self.notification_queue[0].get('notification_type', 'none') in ['action', 'roll'] or 'choices' in self.notification_queue[0]):
                    valid_transfer = True
                    if 'attached_interface_elements' in self.notification_queue[0]:
                        self.notification_queue[0]['attached_interface_elements'] = transferred_interface_elements + self.notification_queue[0]['attached_interface_elements']
                    else:
                        self.notification_queue[0]['attached_interface_elements'] = transferred_interface_elements
                self.notification_to_front(self.notification_queue.pop(0))

        if transferred_interface_elements and not valid_transfer:
            for element in transferred_interface_elements:
                element.remove_recursive(complete=True)

    def set_lock(self, new_lock):
        '''
        Description:
            Sets this notification manager's lock to the new lock value - any notifications received when locked will be displayed once the lock is removed
        Input:
            boolean new_lock: New lock value
        Output:
            None
        '''
        self.lock = new_lock
        if (not new_lock) and self.global_manager.get('displayed_notification') == 'none':
            self.handle_next_notification()

    def display_notification(self, input_dict, insert_index=None): #default, exploration, or roll
        '''
        Description:
            Adds a future notification to the notification queue with the inputted text and type. If other notifications are already in the notification queue, adds this notification to the back, causing it to appear last. When a
                notification is closed, the next notification in the queue is shown
        Input:
            dictionary notification_dict: Dictionary containing details regarding the notification, with 'message' being the only required parameter
        Output:
            None
        '''
        if self.locked or self.notification_queue or self.global_manager.get('displayed_notification') != 'none':
            if insert_index != None:
                self.notification_queue.insert(insert_index, input_dict)
            else:
                self.notification_queue.append(input_dict)
        else:
            self.notification_to_front(input_dict)

    def notification_to_front(self, notification_dict):
        '''
        Description:
            Displays and returns new notification with text matching the inputted string and a type based on what is in the front of this object's notification type queue
        Input:
            dictionary notification_dict: Dictionary containing details regarding the notification, with 'message' being the only required parameter
        Output:
            Notification: Returns the created notification
        '''
        message = notification_dict['message'] #message should be the only required parameter

        height = len(self.format_message(message)) * (self.global_manager.get('default_font_size') + 10) #maybe font size is being scaled incorrectly here?
        self.update_notification_layout(height)

        if 'notification_type' in notification_dict:
            notification_type = notification_dict['notification_type']
        elif 'choices' in notification_dict:
            notification_type = 'choice'
        elif 'zoom_destination' in notification_dict:
            notification_type = 'zoom'
        else:
            notification_type = 'default'

        if 'num_dice' in notification_dict:
            notification_dice = notification_dict['num_dice']
        else:
            notification_dice = 0

        if 'attached_interface_elements' in notification_dict and notification_dict['attached_interface_elements'] != 'none':
            attached_interface_elements = notification_dict['attached_interface_elements']
        else:
            attached_interface_elements = None

        transfer_interface_elements = False
        if 'transfer_interface_elements' in notification_dict:
            transfer_interface_elements = notification_dict['transfer_interface_elements']

        on_remove = None
        if 'on_remove' in notification_dict:
            on_remove = notification_dict['on_remove']

        if 'extra_parameters' in notification_dict and notification_dict['extra_parameters'] != 'none':
            extra_parameters = notification_dict['extra_parameters']
        else:
            extra_parameters = None

        input_dict = {
            'coordinates': scaling.scale_coordinates(self.notification_x, self.notification_y, self.global_manager),
            'ideal_width': scaling.scale_width(self.notification_width, self.global_manager),
            'minimum_height': scaling.scale_height(self.notification_height, self.global_manager),
            'modes': self.notification_modes,
            'image_id': 'misc/default_notification.png',
            'message': message,
            'notification_dice': notification_dice,
            'init_type': notification_type + ' notification',
            'notification_type': notification_type,
            'attached_interface_elements': attached_interface_elements,
            'transfer_interface_elements': transfer_interface_elements,
            'on_remove': on_remove,
            'extra_parameters': extra_parameters
        }

        if notification_type == 'roll':
            input_dict['init_type'] = 'dice rolling notification'
        elif notification_type in ['stop_trade', 'stop_trade_attacked', 'trade', 'trade_promotion', 'final_trade', 'successful_commodity_trade', 'failed_commodity_trade']:
            is_last = False
            commodity_trade = False
            stops_trade = False
            dies = False
            if notification_type == 'stop_trade':
                stops_trade = True
            elif notification_type == 'stop_trade_attacked':
                stops_trade = True
                dies = True
            elif notification_type == 'final_trade':
                is_last = True
            elif notification_type in ['successful_commodity_trade', 'failed_commodity_trade']:
                commodity_trade = True
            elif notification_type == 'trade_promotion':
                self.global_manager.get('trade_result')[0].promote() #promotes caravan
            trade_info_dict = {'is_last': is_last, 'commodity_trade': commodity_trade, 'commodity_trade_type': notification_type, 'stops_trade': stops_trade, 'dies': dies}
            input_dict['trade_info_dict'] = trade_info_dict
            input_dict['init_type'] = 'trade notification'
        elif notification_type == 'off_tile_exploration':
            input_dict['init_type'] = 'off tile exploration notification'
        elif notification_type == 'rumor_search':
            input_dict['init_type'] = 'rumor search notification'
            input_dict['is_last'] = False
        elif notification_type == 'final_rumor_search':
            input_dict['init_type'] = 'rumor search notification'
            input_dict['is_last'] = True
        elif notification_type == 'artifact_search':
            input_dict['init_type'] = 'artifact search notification'
            input_dict['is_last'] = False
        elif notification_type == 'final_artifact_search':
            input_dict['init_type'] = 'artifact search notification'
            input_dict['is_last'] = True
        elif notification_type == 'slave_capture':
            input_dict['init_type'] = 'capture slaves notification'
            input_dict['is_last'] = False
        elif notification_type == 'final_slave_capture':
            input_dict['init_type'] = 'capture slaves notification'
            input_dict['is_last'] = True
        elif notification_type == 'trial':
            input_dict['init_type'] = 'trial notification'
            input_dict['is_last'] = True
        elif notification_type == 'choice':
            del input_dict['notification_dice']
            input_dict['init_type'] = 'choice notification'
            input_dict['button_types'] = notification_dict['choices']
            input_dict['choice_info_dict'] = input_dict['extra_parameters']
        elif notification_type == 'zoom':
            del input_dict['notification_dice']
            input_dict['init_type'] = 'zoom notification'
            input_dict['target'] = notification_dict['zoom_destination']
        new_notification = constants.actor_creation_manager.create_interface_element(input_dict, self.global_manager)
        if notification_type == 'roll':
            for current_die in self.global_manager.get('dice_list'):
                current_die.start_rolling()

        if 'audio' in notification_dict and notification_dict['audio'] != 'none':
            if type(notification_dict['audio']) == list:
                sound_list = notification_dict['audio']
            else:
                sound_list = [notification_dict['audio']]
            channel = None
            for current_sound in sound_list:
                in_sequence = False
                if type(current_sound) == dict:
                    sound_file = current_sound['sound_id']
                    if current_sound.get('dampen_music', False):
                        constants.sound_manager.dampen_music(current_sound.get('dampen_time_interval', 0.5))
                    in_sequence = current_sound.get('in_sequence', False)
                else:
                    sound_file = current_sound
                if in_sequence and channel:
                    constants.sound_manager.queue_sound(sound_file, channel)
                else:
                    channel = constants.sound_manager.play_sound(sound_file)

        return(new_notification)