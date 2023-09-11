#Contains functionality for buttons relating to the European headquarters screen
import random


from .buttons import button
from . import main_loop_tools
from . import text_tools
from . import market_tools
from . import utility
from . import actor_utility

class recruitment_button(button):
    '''
    Button that creates a new unit with a type depending on recruitment_type and places it in Europe
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
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'recruitment_type': string value - Type of unit recruited by this button, like 'explorer'
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.recruitment_type = input_dict['recruitment_type']
        if self.recruitment_type in global_manager.get('country_specific_units'):
            if global_manager.get('current_country') != 'none':
                self.mob_image_id = 'mobs/' + self.recruitment_type + '/' + global_manager.get('current_country').adjective + '/default.png'
            else:
                self.mob_image_id = 'mobs/default/default.png'
        elif self.recruitment_type in global_manager.get('recruitment_types'):
            self.mob_image_id = 'mobs/' + self.recruitment_type + '/default.png'
        else:
            self.mob_image_id = 'mobs/default/default.png'
        self.recruitment_name = ''
        for character in self.recruitment_type:
            if not character == '_':
                self.recruitment_name += character
            else:
                self.recruitment_name += ' '
        self.cost = global_manager.get('recruitment_costs')[self.recruitment_type]
        global_manager.get('recruitment_button_list').append(self)
        if self.recruitment_name in ['European workers']:
            image_id_list = ['mobs/default/button.png']
            left_worker_dict = {
                'image_id': self.mob_image_id,
                'size': 0.8,
                'x_offset': -0.2,
                'y_offset': 0,
                'level': 1
            }
            image_id_list.append(left_worker_dict)

            right_worker_dict = left_worker_dict.copy()
            right_worker_dict['x_offset'] *= -1
            image_id_list.append(right_worker_dict)
        else:
            image_id_list = ['mobs/default/button.png', {'image_id': self.mob_image_id, 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
        input_dict['image_id'] = image_id_list
        input_dict['button_type'] = 'recruitment'
        super().__init__(input_dict, global_manager)

    def on_click(self):
        '''
        Description:
            Controls this button's behavior when clicked. This type of button creates a new unit with a type depending on recruitment_type and places it in Europe
        Input:
            None
        Output:
            None
        '''
        if main_loop_tools.action_possible(self.global_manager):
            if self.global_manager.get('money_tracker').get() >= self.cost:
                choice_info_dict = {'recruitment_type': self.recruitment_type, 'cost': self.cost, 'mob_image_id': self.mob_image_id, 'type': 'recruitment'}
                self.global_manager.get('actor_creation_manager').display_recruitment_choice_notification(choice_info_dict, self.recruitment_name, self.global_manager)
            else:
                text_tools.print_to_screen('You do not have enough money to recruit this unit', self.global_manager)
        else:
            text_tools.print_to_screen('You are busy and cannot recruit a unit', self.global_manager)

    def calibrate(self, country):
        '''
        Description:
            Sets this button's image to the country-specific version for its unit, like a British or French major. Should make sure self.recruitment_type is in the country_specific_units 
                list
        Input:
            country country: Country that this button's unit should match
        Output:
            None
        '''
        self.mob_image_id = {'image_id': 'mobs/' + self.recruitment_type + '/' + country.adjective + '/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}
        image_id_list = ['mobs/default/button.png', self.mob_image_id]
        self.image.set_image(image_id_list)

    def update_tooltip(self):
        '''
        Description:
            Sets this image's tooltip to what it should be, depending on its button_type. This type of button has a tooltip describing the type of unit it recruits
        Input:
            None
        Output:
            None
        '''
        actor_utility.update_recruitment_descriptions(self.global_manager, self.recruitment_type)
        if self.recruitment_type == 'European workers':
            self.set_tooltip(['Recruits a unit of ' + self.recruitment_name + ' for ' + str(self.cost) + ' money.'] + self.global_manager.get('recruitment_list_descriptions')[self.recruitment_type])
        else:
            self.set_tooltip(['Recruits ' + utility.generate_article(self.recruitment_type) + ' ' + self.recruitment_name + ' for ' + str(self.cost) + ' money.'] + self.global_manager.get('recruitment_list_descriptions')[self.recruitment_type])

class buy_commodity_button(button):
    '''
    Button that buys a unit of commodity_type when clicked and has an image matching that of its commodity
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
                'commodity_type': string value - Type of commodity that this button buys, like 'consumer goods'
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        possible_commodity_types = global_manager.get('commodity_types')
        self.commodity_type = input_dict['commodity_type']
        if self.commodity_type in possible_commodity_types:
            input_dict['image_id'] = 'scenery/resources/buttons/' + self.commodity_type + '.png'
        else:
            input_dict['image_id'] = 'buttons/default_button.png'
        self.cost = global_manager.get('commodity_prices')[self.commodity_type] #update this when price changes
        global_manager.set(self.commodity_type + ' buy button', self) #consumer goods buy button, used to update prices
        input_dict['button_type'] = 'buy commodity'
        super().__init__(input_dict, global_manager)

    def on_click(self):
        '''
        Description:
            Controls this button's behavior when clicked. This type of button buys a unit of the commodity_type commodity
        Input:
            None
        Output:
            None
        '''
        if main_loop_tools.action_possible(self.global_manager):
            self.cost = self.global_manager.get('commodity_prices')[self.commodity_type]
            if self.global_manager.get('money_tracker').get() >= self.cost:
                if main_loop_tools.minister_appointed(self.global_manager.get('type_minister_dict')['trade'], self.global_manager): #requires trade minister
                    self.global_manager.get('europe_grid').cell_list[0].tile.change_inventory(self.commodity_type, 1) #adds 1 of commodity type to
                    self.global_manager.get('money_tracker').change(-1 * self.cost, 'consumer_goods')
                    text_tools.print_to_screen('You have lost ' + str(self.cost) + ' money from buying 1 unit of consumer goods.', self.global_manager)
                    if random.randrange(1, 7) == 1: #1/6 chance
                        market_tools.change_price('consumer goods', 1, self.global_manager)
                        text_tools.print_to_screen('The price of consumer goods has increased from ' + str(self.cost) + ' to ' + str(self.cost + 1) + '.', self.global_manager)
            else:
                text_tools.print_to_screen('You do not have enough money to purchase this commodity', self.global_manager)
        else:
            text_tools.print_to_screen('You are busy and cannot purchase commodities', self.global_manager)

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
        