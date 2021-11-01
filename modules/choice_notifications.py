#Contains functionality for choice notifications

import pygame
from .buttons import button
from .notifications import notification
from . import mobs
from . import vehicles
from . import text_tools
from . import scaling
from . import workers
from . import officers

class choice_notification(notification):
    '''
    Notification that presents 2 choices and is removed when one is chosen rather than when the notification itself is clicked, causing a different outcome depending on the chosen option
    '''
    def __init__(self, coordinates, ideal_width, minimum_height, modes, image, message, button_types, choice_info_dict, global_manager):
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
            string list button_types: List of strings that correspond to the button types of this notification's choice buttons, like ['end turn', 'none'] for an end turn button and a do nothing button
            dictionary choice_info_dict: string keys corresponding to various values used by this notification's choice buttons when clicked
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        button_height = scaling.scale_height(50, global_manager)
        #coordinates = (coordinates[0], coordinates[1]  button_height)#coordinates[1] += button_height #raises notification and reduces its height to make room for choice buttons, causing the notification and its buttons to take up the inputted area together
        #minimum_height -= button_height
        super().__init__(coordinates, ideal_width, minimum_height, modes, image, message, global_manager)
        self.choice_buttons = []
        self.choice_info_dict = choice_info_dict
        for current_button_type_index in range(len(button_types)):
            button_type = button_types[current_button_type_index]
            if button_type == 'recruitment':
                new_choice_button = recruitment_choice_button((self.x + (current_button_type_index * round(self.width / len(button_types))), self.y - button_height), round(self.width / len(button_types)), button_height,
                                              button_type, modes, 'misc/paper_label.png', self, global_manager)
            else:
                new_choice_button = choice_button((self.x + (current_button_type_index * round(self.width / len(button_types))), self.y - button_height), round(self.width / len(button_types)), button_height,
                                              button_type, modes, 'misc/paper_label.png', self, global_manager)
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

class choice_button(button):
    '''
    Button with no keybind that is attached to a choice notification and removes its notification when clicked
    '''
    def __init__(self, coordinates, width, height, button_type, modes, image_id, notification, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string button_type: Determines the function of this button, like 'end turn'
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            choice_notification notification: notification to which this choice button is attached
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.notification = notification
        if button_type == 'recruitment':
            self.message = 'Recruit'
            self.recruitment_type = self.notification.choice_info_dict['recruitment_type']
            self.cost = self.notification.choice_info_dict['cost']
            self.mob_image_id = self.notification.choice_info_dict['mob_image_id']
            
        elif button_type == 'exploration':
            self.message = 'Explore'
            self.cost = self.notification.choice_info_dict['cost']
            self.expedition = self.notification.choice_info_dict['expedition']
            self.x_change = self.notification.choice_info_dict['x_change']
            self.y_change = self.notification.choice_info_dict['y_change']
            
        elif button_type == 'stop exploration':
            self.message = 'Do nothing'
            
        elif button_type == 'start trading':
            self.message = 'Start trading'
            
        elif button_type == 'trade':
            self.message = 'Trade'
            
        elif button_type == 'start religious campaign':
            self.message = 'Start campaign'

        elif button_type == 'start converting':
            self.message = 'Convert'
            
        elif button_type == 'stop trading':
            self.message = 'Stop trading'
            
        elif button_type == 'stop religious campaign':
            self.message = 'Stop campaign'

        elif button_type == 'stop converting':
            self.message = 'Stop converting'
            
        elif button_type == 'end turn':
            self.message = 'End turn'
            
        elif button_type == 'none':
            self.message = 'Do nothing'
            
        else:
            self.message = button_type
        super().__init__(coordinates, width, height, 'blue', button_type, 'none', modes, image_id, global_manager)
        self.font_size = scaling.scale_width(25, global_manager)
        self.font_name = self.global_manager.get('font_name')#"Times New Roman"
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
            self.set_tooltip(['Recruit a ' + self.recruitment_type + ' for ' + str(self.cost) + ' money'])

        elif self.button_type == 'end turn':
            self.set_tooltip(['End the current turn'])
            
        elif self.button_type == 'exploration':
            self.set_tooltip(['Attempt an exploration for ' + str(self.cost) + ' money'])
            
        elif self.button_type == 'trade':
            self.set_tooltip(['Attempt to trade by giving consumer goods'])

            
        elif self.button_type == 'start trading':
            self.set_tooltip(['Start trading, allowing consumer goods to be sold for commodities if the villagers are willing'])

        elif self.button_type == 'start religious campaign':
            self.set_tooltip(['Start a religious campaign, possibly convincing church volunteers to join you'])

        elif self.button_type == 'start converting':
            self.set_tooltip(['Start converting natives, possibly reducing their aggressiveness'])
            
            
        elif self.button_type == 'stop trading':
            self.set_tooltip(['Stop trading'])

        elif self.button_type == 'stop religious campaign':
            self.set_tooltip(['Stop religious campaign'])
            
        elif self.button_type == 'stop converting':
            self.set_tooltip(['Stop converting'])
            
            
        else:
            self.set_tooltip(['Do nothing'])

class recruitment_choice_button(choice_button):
    '''
    choice_button that recruits a unit when clicked
    '''
    def __init__(self, coordinates, width, height, button_type, modes, image_id, notification, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string button_type: Determines the function of this button, like 'end turn'
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            choice_notification notification: notification to which this choice button is attached
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(coordinates, width, height, button_type, modes, image_id, notification, global_manager)

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
            self.showing_outline = True
            self.global_manager.get('money_tracker').change(-1 * self.cost)
            if self.recruitment_type in self.global_manager.get('officer_types'): #'explorer':
                if self.recruitment_type == 'head missionary':
                    new_officer = officers.head_missionary((0, 0), [self.global_manager.get('europe_grid')], self.mob_image_id, self.recruitment_type.capitalize(), ['strategic', 'europe'], self.global_manager)
                else:
                    new_officer = officers.officer((0, 0), [self.global_manager.get('europe_grid')], self.mob_image_id, self.recruitment_type.capitalize(), ['strategic', 'europe'], self.recruitment_type, self.global_manager)
            elif self.recruitment_type == 'European worker':
                new_worker = workers.worker((0, 0), [self.global_manager.get('europe_grid')], self.mob_image_id, 'European worker', ['strategic', 'europe'], self.global_manager)
            elif self.recruitment_type == 'ship':
                image_dict = {'default': self.mob_image_id, 'crewed': self.mob_image_id, 'uncrewed': 'mobs/ship/uncrewed.png'}
                new_ship = vehicles.ship((0, 0), [self.global_manager.get('europe_grid')], image_dict, 'ship', ['strategic', 'europe'], 'none', self.global_manager)
        super().on_click()
