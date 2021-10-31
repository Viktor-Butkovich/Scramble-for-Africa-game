from .buttons import button
from .game_transitions import set_game_mode
from . import main_loop_tools
from . import notification_tools
from . import text_tools
from . import utility

class european_hq_button(button):
    '''
    A button that switches to the European Headquarters screen
    '''
    def __init__(self, coordinates, width, height, color, keybind_id, enters_europe, modes, image_id, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string color: Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
            pygame key object keybind_id: Determines the keybind id that activates this button, like pygame.K_n
            boolean enters_europe: True if this button goes from the strategic game mode to the europe game mode, False if it does the opposite
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        button_type = 'europe_transactions'
        self.enters_europe = enters_europe
        super().__init__(coordinates, width, height, color, button_type, keybind_id, modes, image_id, global_manager)

    def on_click(self):
        '''
        Description:
            Controls this button's behavior when clicked. This type of button goes between the europe and strategic game modes
        Input:
            None
        Output:
            None
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
        Description:
            Sets this image's tooltip to what it should be, depending on its button_type. This type of button has a tooltip describing whether it enters or exits the europe game mode
        Input:
            None
        Output:
            None
        '''
        if self.enters_europe:
            self.set_tooltip(['Enters the European Company Headquarters screen'])
        else:
            self.set_tooltip(['Exits the European Company Headquarters screen.'])

class recruitment_button(button):
    '''
    Button that creates a new unit with a type depending on recruitment_type and places it in Europe
    '''
    def __init__(self, coordinates, width, height, color, recruitment_type, keybind_id, modes, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string color: Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
            string recruitment_type: Type of unit recruited by this button, like 'explorer'
            pygame key object keybind_id: Determines the keybind id that activates this button, like pygame.K_n
            string list modes: Game modes during which this button can appear
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        if recruitment_type in global_manager.get('recruitment_types'):
            image_id = 'mobs/' + recruitment_type + '/button.png'
            self.mob_image_id = 'mobs/' + recruitment_type + '/default.png'
        else:
            image_id = 'misc/default_button.png'
            self.mob_image_id = 'mobs/default/default.png'
        self.recruitment_type = recruitment_type
        self.cost = global_manager.get('recruitment_costs')[self.recruitment_type]
        super().__init__(coordinates, width, height, color, 'recruitment', keybind_id, modes, image_id, global_manager)

    def on_click(self):
        '''
        Description:
            Controls this button's behavior when clicked. This type of button creates a new unit with a type depending on recruitment_type and places it in Europe
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):
                if self.global_manager.get('money_tracker').get() >= self.cost:
                    choice_info_dict = {'recruitment_type': self.recruitment_type, 'cost': self.cost, 'mob_image_id': self.mob_image_id, 'type': 'recruitment'}
                    notification_tools.display_choice_notification('Are you sure you want to recruit ' + utility.generate_article(self.recruitment_type) + ' ' + self.recruitment_type + '? ' +
                                                                   utility.generate_capitalized_article(self.recruitment_type) + ' ' + self.recruitment_type + ' would cost ' + str(choice_info_dict['cost']) + ' money to recruit.',
                                                                   ['recruitment', 'none'], choice_info_dict, self.global_manager) #message, choices, choice_info_dict, global_manager
                else:
                    text_tools.print_to_screen('You do not have enough money to recruit this unit', self.global_manager)
            else:
                text_tools.print_to_screen('You are busy and can not recruit a unit', self.global_manager)

    def update_tooltip(self):
        '''
        Description:
            Sets this image's tooltip to what it should be, depending on its button_type. This type of button has a tooltip describing the type of unit it recruits
        Input:
            None
        Output:
            None
        '''
        self.set_tooltip(['Recruits ' + utility.generate_article(self.recruitment_type) + ' ' + self.recruitment_type + ' for ' + str(self.cost) + ' money.'])

class buy_commodity_button(button):
    '''
    Button that buys a unit of commodity_type when clicked and has an image matching that of its commodity
    '''
    def __init__(self, coordinates, width, height, color, commodity_type, modes, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string color: Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
            string commodity_type: Type of commmodity that this button buys, like 'consumer goods'
            string list modes: Game modes during which this button can appear
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        possible_commodity_types = global_manager.get('commodity_types')
        if commodity_type in possible_commodity_types:
            image_id = 'scenery/resources/buttons/' + commodity_type + '.png'
        else:
            image_id = 'misc/default_button.png'
        self.commodity_type = commodity_type
        self.cost = global_manager.get('commodity_prices')[self.commodity_type] #update this when price changes
        global_manager.set(commodity_type + ' buy button', self) #consumer goods buy button, used to update prices
        super().__init__(coordinates, width, height, color, 'recruitment', 'none', modes, image_id, global_manager)

    def on_click(self):
        '''
        Description:
            Controls this button's behavior when clicked. This type of button buys a unit of the commodity_type commodity
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):
                if self.global_manager.get('money_tracker').get() >= self.cost:
                    self.global_manager.get('europe_grid').cell_list[0].tile.change_inventory(self.commodity_type, 1) #adds 1 of commodity type to
                    self.global_manager.get('money_tracker').change(-1 * self.cost)
                else:
                    text_tools.print_to_screen('You do not have enough money to purchase this commodity', self.global_manager)
            else:
                text_tools.print_to_screen('You are busy and can not purchase commodities', self.global_manager)

    def update_tooltip(self):
        '''
        Description:
            Sets this image's tooltip to what it should be, depending on its button_type. This type of button has a tooltip describing the commodity that it buys and its price
        Input:
            None
        Output:
            None
        '''
        self.cost = self.global_manager.get('commodity_prices')[self.commodity_type]
        self.set_tooltip(['Purchases 1 unit of ' + self.commodity_type + ' for ' + str(self.cost) + ' money.'])
        
