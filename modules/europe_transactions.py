from .buttons import button
from .game_transitions import set_game_mode
from .mobs import explorer
from .mobs import worker
from . import main_loop_tools
from . import notification_tools
from . import text_tools

class european_hq_button(button):
    '''
    A button that switches to the european headquarters screen, separated from buttons to reduce dependencies
    '''
    def __init__(self, coordinates, width, height, color, keybind_id, enters_europe, modes, image_id, global_manager):
        '''
        Input:
            same as superclass but without button type, except:
            enters_europe: boolean representing whether the button enters or leaves the europe game mode
        '''
        button_type = 'europe_transactions'
        self.enters_europe = enters_europe
        super().__init__(coordinates, width, height, color, button_type, keybind_id, modes, image_id, global_manager)

    def on_click(self):
        '''
        Input:
            none
        Output:
            Controls the button's behavior when clicked. A european_hq_button will transfer between the europe and strategic game modes, depending on the type of european_hq_button.
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):
                if self.enters_europe:
                    set_game_mode('europe', self.global_manager)
                else:
                    set_game_mode('strategic', self.global_manager)
            else:
                text_tools.print_to_screen('You are busy and can not switch screens.', self.global_manager)

    def update_tooltip(self):
        '''
        Input:
            none
        Output:
            Sets the button's tooltip to what it should be. A european_hq_button will have a tooltip describing whether it enters or exits the europe game mode.
        '''
        if self.enters_europe:
            self.set_tooltip(['Enters the European Company Headquarters screen'])
        else:
            self.set_tooltip(['Exits the European Company Headquarters screen.'])

class recruitment_button(button):
    '''
    Button that, when clicked, creates a new unit and places it in Europe. The unit created will depend on the button's recruitment type.
    '''
    def __init__(self, coordinates, width, height, color, recruitment_type, keybind_id, modes, global_manager):
        '''
        Input:
            same as superclass, except:
                recruitment_type: string representing the type of unit recruited by this button
                button_type is always set to 'recruitment'
        '''
        possible_recruitment_types = ['European worker', 'explorer']
        if recruitment_type in possible_recruitment_types:
            image_id = 'mobs/' + recruitment_type + '/button.png'
            self.mob_image_id = 'mobs/' + recruitment_type + '/default.png'
        else:
            image_id = 'misc/default_button.png'
            self.mob_image_id = 'mobs/default/default.png'
        self.recruitment_type = recruitment_type
        if self.recruitment_type == 'explorer':
            self.cost = 5
        elif self.recruitment_type == 'European worker':
            self.cost = 3
        else:
            self.cost = 0
        super().__init__(coordinates, width, height, color, 'recruitment', keybind_id, modes, image_id, global_manager)

    def on_click(self):
        '''
        Input:
            none
        Output:
            Controls the button's behavior when clicked. A recruitment button will create a new unit and place it in Europe. The unit created will depend on the button's recruitment type.
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):
                if self.global_manager.get('money_tracker').get() >= self.cost:
                    choice_info_dict = {'recruitment_type': self.recruitment_type, 'cost': self.cost, 'mob_image_id': self.mob_image_id}
                    notification_tools.display_choice_notification('Are you sure you want to recruit a ' + self.recruitment_type + '? A ' + self.recruitment_type + ' would cost ' + str(choice_info_dict['cost']) + ' money to recruit.',
                                                                   ['recruitment', 'none'], choice_info_dict, self.global_manager) #message, choices, choice_info_dict, global_manager
                else:
                    text_tools.print_to_screen('You do not have enough money to recruit this unit', self.global_manager)
            else:
                text_tools.print_to_screen('You are busy and can not recruit a unit', self.global_manager)
            #if self.recruitment_type == 'explorer':
            #    new_explorer = explorer((0, 0), [self.global_manager.get('europe_grid')], self.mob_image_id, 'Explorer', ['strategic', 'europe'], self.global_manager)
            #elif self.recruitment_type == 'European worker':
            #    new_worker = worker((0, 0), [self.global_manager.get('europe_grid')], self.mob_image_id, 'European worker', ['strategic', 'europe'], self.global_manager)

    def update_tooltip(self):
        '''
        Input:
            none
        Output:
            Sets the button's tooltip to what it should be. A recruitment button will have a tooltip describing the type of unit it recruits.
        '''
        self.set_tooltip(['Recruits a ' + self.recruitment_type + '.'])
            
#create button that goes to slots in europe screen and matches mobs in the europe grid

#create button that matches different things that can be purchased and purchases them when clicked

#create button for each type of resources cargo that sells them and possibly allows you to sell a certain amount

#create a way to move entities onto ships within this screen
