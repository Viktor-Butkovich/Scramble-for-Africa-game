from .buttons import button
from .game_transitions import set_game_mode
from .mobs import explorer
from .mobs import worker

class european_hq_button(button):
    '''
    A button that switches to the european headquarters screen, separated from buttons to reduce dependencies
    '''
    def __init__(self, coordinates, width, height, color, keybind_id, enters_europe, modes, image_id, global_manager):
        '''
        Inputs:
            same as superclass but without button type, except:
            enters_europe: boolean representing whether the button enters or leaves the europe screen
        '''
        button_type = 'europe_transactions'
        self.enters_europe = enters_europe
        super().__init__(coordinates, width, height, color, button_type, keybind_id, modes, image_id, global_manager)

    def on_click(self):
        if self.can_show():
            self.showing_outline = True
            if self.enters_europe:
                set_game_mode('europe', self.global_manager)
            else:
                set_game_mode('strategic', self.global_manager)

    def update_tooltip(self):
        if self.enters_europe:
            self.set_tooltip(['Enters the European Company Headquarters screen'])
        else:
            self.set_tooltip(['Exits the European Company Headquarters screen.'])

class recruitment_button(button):
    def __init__(self, coordinates, width, height, color, recruitment_type, keybind_id, modes, global_manager):
        possible_recruitment_types = ['European worker', 'explorer']
        if recruitment_type in possible_recruitment_types:
            image_id = 'mobs/' + recruitment_type + '/button.png'
            self.mob_image_id = 'mobs/' + recruitment_type + '/default.png'
        else:
            image_id = 'misc/default_button.png'
            self.mob_image_id = 'mobs/default/default.png'
        self.recruitment_type = recruitment_type
        super().__init__(coordinates, width, height, color, 'recruitment', keybind_id, modes, image_id, global_manager)

    def on_click(self):
        if self.can_show():
            self.showing_outline = True
            if self.recruitment_type == 'explorer':
                new_explorer = explorer((0, 0), [self.global_manager.get('europe_grid')], self.mob_image_id, 'Explorer', ['strategic', 'europe'], self.global_manager)
            elif self.recruitment_type == 'European worker':
                new_worker = worker((0, 0), [self.global_manager.get('europe_grid')], self.mob_image_id, 'European worker', ['strategic', 'europe'], self.global_manager)

    def update_tooltip(self):
        self.set_tooltip(['Recruits a ' + self.recruitment_type + '.'])
            
#create button that goes to slots in europe screen and matches mobs in the europe grid

#create button that matches different things that can be purchased and purchases them when clicked

#create button for each type of resources cargo that sells them and possibly allows you to sell a certain amount

#create a way to move entities onto ships within this screen
