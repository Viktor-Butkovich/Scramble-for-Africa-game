#Contains functionality for choice notifications

import pygame
from . import buttons
from . import notifications
from . import text_tools
from . import scaling
from . import market_tools
from . import utility

class choice_notification(notifications.notification):
    '''
    Notification that presents 2 choices and is removed when one is chosen rather than when the notification itself is clicked, causing a different outcome depending on the chosen option
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
                'button_types': string list value - List of string corresponding to the button types of this notification's choice buttons, like ['end turn', 'none']
                'choice_info_dict': dictionary value - Dictionary containing any case-specific information for choice buttons to function as intended
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        button_height = scaling.scale_height(50, global_manager)
        super().__init__(input_dict, global_manager)
        self.choice_buttons = []
        self.choice_info_dict = input_dict['choice_info_dict']
        button_types = input_dict['button_types']
        for current_button_type_index in range(len(button_types)):
            button_type = button_types[current_button_type_index]
            if button_type == 'recruitment':
                new_choice_button = recruitment_choice_button((self.x + (current_button_type_index * round(self.width / len(button_types))), self.y - button_height), round(self.width / len(button_types)), button_height,
                                              button_type, self.modes, 'misc/paper_label.png', self, global_manager)
            else:
                new_choice_button = choice_button((self.x + (current_button_type_index * round(self.width / len(button_types))), self.y - button_height), round(self.width / len(button_types)), button_height,
                                              button_type, self.modes, 'misc/paper_label.png', self, global_manager)
            self.choice_buttons.append(new_choice_button)
        self.global_manager.set('making_choice', True)

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

    def on_click(self):
        '''
        Description:
            Controls this notification's behavior when clicked. Choice notifications do nothing when clicked, instead acting when their choice buttons are clicked
        Input:
            None
        Output:
            None
        '''
        nothing = 0 #does not remove self when clicked

    def update_tooltip(self):
        '''
        Description:
            Sets this notification's tooltip to what it should be. Choice notifications prompt the user to click on one of its choice buttons to close it
        Input:
            None
        Output:
            None
        '''
        self.set_tooltip(['Choose an option to close this notification'])

    def remove(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program. When a notification is removed, the next notification is shown, if there is one. Choice notifications are removed
                when one of their choice buttons is clicked
        Input:
            None
        Output:
            None
        '''
        self.global_manager.set('making_choice', False)
        super().remove()
        for current_choice_button in self.choice_buttons:
            current_choice_button.remove()

class choice_button(buttons.button):
    '''
    Button with no keybind that is attached to a choice notification and removes its notification when clicked
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'button_type': string value - Determines the function of this button, like 'end turn'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'notification': choice_notification value: notification to which this choice button is attached
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.notification = input_dict['notification']
        if input_dict['button_type'] == 'recruitment':
            self.recruitment_type = self.notification.choice_info_dict['recruitment_type']
            if self.recruitment_type in ['steamship', 'slave workers']:
                self.message = 'Purchase'
                self.verb = 'purchase'
            else:
                self.message = 'Hire'
                self.verb = 'hire'
            self.cost = self.notification.choice_info_dict['cost']
            self.mob_image_id = self.notification.choice_info_dict['mob_image_id']
            
        elif input_dict['button_type'] == 'exploration':
            self.message = 'Explore'
            self.cost = self.notification.choice_info_dict['cost']
            self.expedition = self.notification.choice_info_dict['expedition']
            self.x_change = self.notification.choice_info_dict['x_change']
            self.y_change = self.notification.choice_info_dict['y_change']

        elif input_dict['button_type'] == 'attack':
            self.message = 'Attack'
            self.cost = self.notification.choice_info_dict['cost']
            self.battalion = self.notification.choice_info_dict['battalion']
            self.x_change = self.notification.choice_info_dict['x_change']
            self.y_change = self.notification.choice_info_dict['y_change']
            
        elif input_dict['button_type'] in ['start religious campaign', 'start public relations campaign', 'start advertising campaign', 'start suppress slave trade']:
            self.message = 'Start campaign'
            if input_dict['button_type'] == 'start advertising campaign':
                self.commodity = self.notification.choice_info_dict['commodity']

        elif input_dict['button_type'] == 'start loan search':
            self.message = 'Find loan'

        elif input_dict['button_type'] == 'start converting':
            self.message = 'Convert'

        elif input_dict['button_type'] in ['start rumor search', 'start artifact search']:
            self.message = 'Search'

        elif input_dict['button_type'] == 'start capture slaves':
            self.message = 'Capture slaves'
            
        elif input_dict['button_type'] in ['stop religious campaign', 'stop public relations campaign', 'stop advertising campaign']:
            self.message = 'Stop campaign'

        elif input_dict['button_type'] == 'stop loan search':
            self.message = 'Stop search'

        elif input_dict['button_type'] == 'accept loan offer':
            self.message = 'Accept'

        elif input_dict['button_type'] == 'decline loan offer':
            self.message = 'Decline'
            
        elif input_dict['button_type'] in ['none', 'stop exploration', 'stop attack', 'stop capture slaves', 'stop suppress slave trade', 'stop converting', 'stop rumor search', 'stop artifact search']:
            self.message = 'Do nothing'

        elif input_dict['button_type'] == 'confirm main menu':
            self.message = 'Main menu'

        elif input_dict['button_type'] == 'confirm remove minister':
            self.message = 'Confirm'

        elif input_dict['button_type'] == 'quit':
            self.message = 'Exit game'
    
        else:
            self.message = input_dict['button_type'].capitalize()
            

        super().__init__(input_dict, global_manager)
        self.font_size = scaling.scale_width(25, global_manager)
        self.font_name = self.global_manager.get('font_name')
        self.font = pygame.font.SysFont(self.font_name, self.font_size)
        self.in_notification = True

    def on_click(self):
        '''
        Description:
            Controls this button's behavior when clicked. Choice buttons remove their notifications when clicked, along with the normal behaviors associated with their button_type
        Input:
            None
        Output:
            None
        '''
        super().on_click()
        if self.can_show(): #copying conditions of superclass on_click to make sure that notification is only removed when effect of click is done
            self.notification.remove()

    def draw(self):
        '''
        Description:
            Draws this button below its choice notification and draws a description of what it does on top of it
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.image.draw()
            self.global_manager.get('game_display').blit(text_tools.text(self.message, self.font, self.global_manager), (self.x + scaling.scale_width(10, self.global_manager), self.global_manager.get('display_height') -
                (self.y + self.height)))

    def update_tooltip(self):
        '''
        Description:
            Sets this image's tooltip to what it should be, depending on its button_type
        Input:
            None
        Output:
            None
        '''
        if self.button_type == 'recruitment':
            if self.recruitment_type in ['African worker village', 'African worker slums', 'African worker labor broker']:
                self.set_tooltip([utility.capitalize(self.verb) + ' an African worker for ' + str(self.cost) + ' money'])
            else:
                self.set_tooltip([utility.capitalize(self.verb) + ' a ' + self.recruitment_type + ' for ' + str(self.cost) + ' money'])

        elif self.button_type == 'end turn':
            self.set_tooltip(['End the current turn'])
            
        elif self.button_type == 'exploration':
            self.set_tooltip(['Attempt an exploration for ' + str(self.cost) + ' money'])

        elif self.button_type == 'attack':
            self.set_tooltip(['Supply an attack for ' + str(self.cost) + ' money'])
            
        elif self.button_type == 'trade':
            self.set_tooltip(['Attempt to trade by giving consumer goods'])

        elif self.button_type == 'start trading':
            self.set_tooltip(['Start trading, allowing consumer goods to be sold for commodities if the villagers are willing'])

        elif self.button_type == 'start religious campaign':
            self.set_tooltip(['Start a religious campaign, possibly convincing church volunteers to join you'])

        elif self.button_type == 'start public relations campaign':
            self.set_tooltip(['Start a public relations campaign, possibly improving your company\'s public opinion'])

        elif self.button_type == 'start advertising campaign':
            self.set_tooltip(['Starts an advertising campaign for ' + self.commodity])

        elif self.button_type == 'start loan search':
            self.set_tooltip(['Starts a search for a low-interest loan offer'])

        elif self.button_type == 'start converting':
            self.set_tooltip(['Start converting natives, possibly reducing their aggressiveness'])

        elif self.button_type == 'start rumor search':
            self.set_tooltip(['Start searching for rumors about the artifact\'s location'])

        elif self.button_type == 'start artifact search':
            self.set_tooltip(['Start searching for an artifact at a rumored location'])

        elif self.button_type == 'start capture slaves':
            self.set_tooltip(['Start attempting to capture native villagers as slaves'])

        elif self.button_type == 'accept loan offer':
            self.set_tooltip(['Accepts the loan offer'])

        elif self.button_type == 'reject loan offer':
            self.set_tooltip(['Rejects the loan offer'])

        elif self.button_type == 'confirm main menu':
            self.set_tooltip(['Exits to the main menu without saving'])

        elif self.button_type == 'quit':
            self.set_tooltip(['Exits the game without saving'])

        elif self.button_type == 'none':
            self.set_tooltip(['Do nothing'])
            
        else:
            self.set_tooltip([self.button_type.capitalize()]) #stop trading -> ['Stop trading']

class recruitment_choice_button(choice_button):
    '''
    Choice_button that recruits a unit when clicked
    '''
    def on_click(self):
        '''
        Description:
            Controls this button's behavior when clicked. Recruitment choice buttons recruit a unit, pay for the unit's cost, and remove their attached notification when clicked
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            input_dict = {'select_on_creation': True}
            if self.recruitment_type == 'slave workers':
                self.global_manager.get('money_tracker').change(-1 * self.cost, 'unit_recruitment')
                input_dict['grids'] = [self.global_manager.get('slave_traders_grid')]
                attached_cell = input_dict['grids'][0].cell_list[0]
                input_dict['coordinates'] = (attached_cell.x, attached_cell.y)
                input_dict['image'] = 'mobs/slave workers/default.png'
                input_dict['modes'] = ['strategic']
                input_dict['name'] = 'slave workers'
                input_dict['init_type'] = 'slaves'
                input_dict['purchased'] = True
                self.global_manager.get('actor_creation_manager').create(False, input_dict, self.global_manager)

            elif self.recruitment_type == 'African worker village':
                self.global_manager.get('displayed_tile').cell.get_building('village').recruit_worker()

            elif self.recruitment_type == 'African worker slums':
                self.global_manager.get('displayed_tile').cell.get_building('slums').recruit_worker()

            elif self.recruitment_type == 'African worker labor broker':
                recruiter = self.global_manager.get('displayed_mob')
                input_dict['coordinates'] = (recruiter.x, recruiter.y)
                input_dict['grids'] = recruiter.grids
                input_dict['image'] = 'mobs/African workers/default.png'
                input_dict['modes'] = ['strategic']
                input_dict['name'] = 'African workers'
                input_dict['init_type'] = 'workers'
                input_dict['worker_type'] = 'African'
                self.global_manager.get('money_tracker').change(-1 * self.notification.choice_info_dict['cost'], 'unit_recruitment')
                self.notification.choice_info_dict['village'].change_population(-1)
                market_tools.attempt_worker_upkeep_change('decrease', 'African', self.global_manager) #adds 1 worker to the pool
                worker = self.global_manager.get('actor_creation_manager').create(False, input_dict, self.global_manager)
                if recruiter.is_vehicle:
                    recruiter.set_movement_points(0)
                    worker.crew_vehicle(recruiter)
                else:
                    recruiter.set_movement_points(0)
                    self.global_manager.get('actor_creation_manager').create_group(worker, recruiter, self.global_manager)

            else:
                input_dict['coordinates'] = (0, 0)
                input_dict['grids'] = [self.global_manager.get('europe_grid')]
                input_dict['image'] = self.mob_image_id
                input_dict['modes'] = ['strategic', 'europe']
                self.showing_outline = True
                self.global_manager.get('money_tracker').change(-1 * self.cost, 'unit_recruitment')
                if self.recruitment_type in self.global_manager.get('officer_types'):
                    name = ''
                    for character in self.recruitment_type:
                        if not character == '_':
                            name += character
                        else:
                            name += ' '
                    input_dict['name'] = name
                    input_dict['init_type'] = self.recruitment_type
                    input_dict['officer_type'] = self.recruitment_type

                elif self.recruitment_type == 'European workers':
                    input_dict['name'] = 'European workers'
                    input_dict['init_type'] = 'workers'
                    input_dict['worker_type'] = 'European'

                elif self.recruitment_type == 'African workers':
                    input_dict['name'] = 'African workers'
                    input_dict['init_type'] = 'workers'
                    input_dict['worker_type'] = 'African'

                elif self.recruitment_type == 'steamship':
                    image_dict = {'default': self.mob_image_id, 'uncrewed': 'mobs/steamship/uncrewed.png'}
                    input_dict['image_dict'] = image_dict
                    input_dict['name'] = 'steamship'
                    input_dict['crew'] = 'none'
                    input_dict['init_type'] = 'ship'
                    
                self.global_manager.get('actor_creation_manager').create(False, input_dict, self.global_manager)
        super().on_click()
