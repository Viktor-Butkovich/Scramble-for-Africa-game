#Contains functionality for notifications

import time
from .labels import multi_line_label
from ..util import actor_utility

class notification(multi_line_label):
    '''
    Multi-line label that prompts the user to click on it, and disappears when clicked
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
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        global_manager.set('displayed_notification', self)
        super().__init__(input_dict, global_manager)
        self.in_notification = True
        self.is_action_notification = False
        self.notification_dice = 0 #by default, do not show any dice when notification shown
        self.global_manager.get('sound_manager').play_sound('opening_letter')
        self.creation_time = time.time()
        self.notification_type = 'default'

    def format_message(self):
        '''
        Description:
            Converts this notification's string message to a list of strings, with each string representing a line of text. Each line of text ends when its width exceeds the ideal_width or when a '/n' is encountered in the text
        Input:
            None
        Output:
            None
        '''
        super().format_message()
        self.message.append('Click to remove this notification.')
                    
    def update_tooltip(self):
        '''
        Description:
            Sets this notification's tooltip to what it should be. By default, notifications prompt the player to close them
        Input:
            None
        Output:
            None
        '''
        self.set_tooltip(['Click to remove this notification'])

    def on_click(self):
        '''
        Description:
            Controls this notification's behavior when clicked. By default, notifications are removed when clicked
        Input:
            None
        Output:
            None
        '''
        if time.time() - 0.1 > self.creation_time: #don't accidentally remove notifications instantly when clicking between them
            self.remove_complete()
            
    def remove(self, handle_next_notification=True):
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
        self.global_manager.set('displayed_notification', 'none')
        if handle_next_notification:
            notification_manager = self.global_manager.get('notification_manager')
            if len(notification_manager.notification_queue) >= 1:
                notification_manager.notification_queue.pop(0)
            if len(notification_manager.notification_queue) > 0:
                notification_manager.notification_to_front(notification_manager.notification_queue[0])

class minister_notification(notification):
    '''
    Notification that is a message from a minister and has a minister portrait attached
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
                'attached_minister': minister value - Minister attached to this notification
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(input_dict, global_manager)
        self.attached_minister = input_dict['attached_minister']
        self.notification_type = 'minister'
        if self.attached_minister.current_position == 'Prosecutor' and global_manager.get('evidence_just_found'):
            self.attached_minister.play_voice_line('evidence')
            global_manager.set('evidence_just_found', False)

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
        for current_minister_image in self.global_manager.get('dice_roll_minister_images'):
            if current_minister_image.attached_minister == self.attached_minister:
                current_minister_image.remove_complete()
        
class zoom_notification(notification):
    '''
    Notification that selects a certain tile or mob and moves the minimap to it when first displayed
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
                'target': actor value - Tile or mob to select and move the minimap to when this notification is first displayed
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(input_dict, global_manager)
        target = input_dict['target']
        if self.global_manager.get('strategic_map_grid') in target.grids:
            self.global_manager.get('minimap_grid').calibrate(target.x, target.y)
        if target.actor_type == 'tile':
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display'), target)
            if not target.cell.grid.mini_grid == 'none':
                target.grids[0].mini_grid.calibrate(target.x, target.y)
        elif target.actor_type == 'mob':
            if not target.images[0].current_cell == 'none': #if non-hidden mob, move to front of tile and select
                target.select()
                target.move_to_front()
                if (not target.grids[0].mini_grid == 'none'): #if not in abstract grid, calibrate mini map to mob location
                   target.grids[0].mini_grid.calibrate(target.x, target.y)
            else: #if hidden mob, move to location and select tile
                target.grids[0].mini_grid.calibrate(target.x, target.y)
                actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('tile_info_display'), target.grids[0].find_cell(target.x, target.y).tile)
