import pygame
from .buttons import button
from .notifications import notification
from . import mobs
from . import vehicles
from . import text_tools
from . import scaling

class choice_notification(notification):
    '''
    Notification that presents 2 choices and is removed when one is chosen rather than when the notification itself is clicked, causing a different outcome depending on the chosen option
    '''
    def __init__(self, coordinates, ideal_width, minimum_height, modes, image, message, button_types, choice_info_dict, global_manager):
        button_height = 50
        coordinates = (coordinates[0], coordinates[1] + button_height)#coordinates[1] += button_height #raises notification and reduces its height to make room for choice buttons, causing the notification and its buttons to take up the inputted area together
        minimum_height -= button_height
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
        Input:
            none
        Output:
            Same as superclass except for the last line, "Click to remove this notification", being removed to allow for a more specific message for the circumstances of the notification
        '''
        super().format_message()
        self.message.pop(-1)

    def on_click(self):
        nothing = 0 #does not remove self when clicked

    def update_tooltip(self):
        self.set_tooltip(['Choose an option to close this notification'])

    def remove(self):
        self.global_manager.set('making_choice', False)
        super().remove()
        for current_choice_button in self.choice_buttons:
            current_choice_button.remove()

class choice_button(button):
    '''
    Button with no keybind that is attached to a choice notification and removes its notification and all of its buttons when clicked
    '''
    def __init__(self, coordinates, width, height, button_type, modes, image_id, notification, global_manager):
        self.notification = notification
        if button_type == 'recruitment': #done before superclass init so that tooltip setup works correctly
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
        elif button_type == 'end turn':
            self.message = 'End turn'
        elif button_type == 'none':
            self.message = 'Do nothing'
        else:
            self.message = button_type
        super().__init__(coordinates, width, height, 'blue', button_type, 'none', modes, image_id, global_manager)
        self.font_size = scaling.scale_width(25, global_manager)
        self.font_name = "Times New Roman"
        self.font = pygame.font.SysFont(self.font_name, self.font_size)
        self.in_notification = True

    def on_click(self):
        super().on_click()
        if self.can_show(): #copying conditions of superclass on_click to make sure that notification is only removed when effect of click is done
            self.notification.remove()

    def draw(self):
        if self.can_show():
            self.image.draw()
            self.global_manager.get('game_display').blit(text_tools.text(self.message, self.font, self.global_manager), (self.x + 10, self.global_manager.get('display_height') - (self.y + self.height)))

    def update_tooltip(self):
        if self.button_type == 'recruitment':
            self.set_tooltip(['Recruits a ' + self.recruitment_type + ' for ' + str(self.cost) + ' money'])
        elif self.button_type == 'exploration':
            self.set_tooltip(['Attempts an exploration for ' + str(self.cost) + ' money'])
        elif self.button_type == 'end turn':
            self.set_tooltip(['Ends the current turn'])
        else:
            self.set_tooltip(['Does nothing'])

class recruitment_choice_button(choice_button):
    def __init__(self, coordinates, width, height, button_type, modes, image_id, notification, global_manager):
        super().__init__(coordinates, width, height, button_type, modes, image_id, notification, global_manager)

    def on_click(self):
        if self.can_show():
            self.showing_outline = True
            self.global_manager.get('money_tracker').change(-1 * self.cost)
            if self.recruitment_type == 'explorer':
                new_explorer = mobs.explorer((0, 0), [self.global_manager.get('europe_grid')], self.mob_image_id, 'Explorer', ['strategic', 'europe'], self.global_manager)
            elif self.recruitment_type == 'European worker':
                new_worker = mobs.worker((0, 0), [self.global_manager.get('europe_grid')], self.mob_image_id, 'European worker', ['strategic', 'europe'], self.global_manager)
            elif self.recruitment_type == 'ship':
                image_dict = {'default': self.mob_image_id, 'crewed': self.mob_image_id, 'uncrewed': 'mobs/ship/uncrewed.png'}
                new_ship = vehicles.ship((0, 0), [self.global_manager.get('europe_grid')], image_dict, 'ship', ['strategic', 'europe'], 'none', self.global_manager)
        super().on_click()
