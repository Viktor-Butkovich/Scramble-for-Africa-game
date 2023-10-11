#Contains all functionality for public relations campaigns

import pygame
import random
from . import action
from ..util import action_utility, utility, actor_utility

class construction(action.action):
    '''
    Action for construction gang to construct a certain type of building
    '''
    def initial_setup(self, **kwargs):
        '''
        Description:
            Completes any configuration required for this action during setup - automatically called during action_setup
        Input:
            None
        Output:
            None
        '''
        super().initial_setup(**kwargs)
        self.building_type = kwargs.get('building_type', 'none')
        del self.global_manager.get('actions')[self.action_type]
        self.global_manager.get('actions')[self.building_type] = self
        self.building_name = self.building_type.replace('_', ' ')
        if self.building_type == 'infrastructure':
            self.building_name = 'road' #deal with infrastructure exceptions later
        self.global_manager.get('transaction_descriptions')['construction'] = 'construction'
        if self.building_type == 'trading_post':
            self.requirement = 'can_trade'
        elif self.building_type == 'mission':
            self.requirement = 'can_convert'
        elif self.building_type == 'fort':
            self.requirement = 'is_battalion'
        else:
            self.requirement = 'can_construct'
        if self.building_type == 'resource':
            self.attached_resource = 'none'
        self.name = 'construction'

    def button_setup(self, initial_input_dict):
        '''
        Description:
            Completes the inputted input_dict with any values required to create a button linked to this action - automatically called during actor display label
                setup
        Input:
            None
        Output:
            None
        '''
        initial_input_dict = super().button_setup(initial_input_dict)
        if self.building_type == 'resource':
            initial_input_dict['image_id'] = self.global_manager.get('resource_building_button_dict')[self.attached_resource] #need way to update button image from action
        elif self.building_type == 'infrastructure':
            if self.current_unit != 'none':
                if self.current_unit.images[0].current_cell.terrain == 'water' and self.current_unit.images[0].current_cell.y > 0:
                    if self.current_unit.images[0].current_cell.contained_buildings[self.building_type] != 'none':
                        initial_input_dict['image_id'] = 'buildings/buttons/railroad_bridge.png'
                    else:
                        initial_input_dict['image_id'] = 'buildings/buttons/road_bridge.png'
                else:
                    if self.current_unit.images[0].current_cell.contained_buildings[self.building_type] != 'none':
                        initial_input_dict['image_id'] = 'buildings/buttons/railroad.png'
                    else:
                        initial_input_dict['image_id'] = 'buildings/buttons/road.png'
            else:
                initial_input_dict['image_id'] = 'buildings/buttons/road.png'
        else:
            initial_input_dict['image_id'] = 'buildings/buttons/' + self.building_type + '.png'
        initial_input_dict['keybind_id'] = {
            'resource': pygame.K_g,
            'port': pygame.K_p,
            'infrastructure': pygame.K_r,
            'train_station': pygame.K_t,
            'trading_post': pygame.K_y,
            'mission': pygame.K_y,
            'fort': pygame.K_v,
            'warehouses': pygame.K_k
        }[self.building_type]
        return(initial_input_dict)

    def update_tooltip(self):
        '''
        Description:
            Sets this tooltip of a button linked to this action
        Input:
            None
        Output:
            None
        '''
        message = []
        if self.building_type != 'infrastructure':
            message += self.global_manager.get('list_descriptions')[self.building_type]
        else:
            message += self.global_manager.get('list_descriptions')[self.building_name]
            if self.building_name == 'railroad':
                message += ['Upgrades this tile\'s road into a railroad, retaining the benefits of a road']
            elif self.building_name == 'railroad_bridge':
                message += ['Upgrades this tile\'s road bridge into a railroad bridge, retaining the benefits of a road bridge']

        if self.building_type == 'trading_post':
            message.append('Can only be built in a village')
        elif self.building_type == 'mission':
            message.append('Can only be built in a village')

        if self.building_type in ['train_station', 'port', 'resource']:
            message.append('Also upgrades this tile\'s warehouses by 9 inventory capacity, or creates new warehouses if none are present')
        
        base_cost = actor_utility.get_building_cost(self.global_manager, 'none', self.building_type, self.building_name)
        cost = actor_utility.get_building_cost(self.global_manager, self.current_unit, self.building_type, self.building_name)
        
        message.append('Attempting to build costs ' + str(cost) + ' money and all remaining movement points, at least 1')
        if self.building_type in ['train', 'steamboat']:
            message.append('Unlike buildings, the cost of vehicle assembly is not impacted by local terrain')

        if self.current_unit != 'none' and self.global_manager.get('strategic_map_grid') in self.current_unit.grids:
            terrain = self.current_unit.images[0].current_cell.terrain
            message.append(utility.generate_capitalized_article(self.building_name) + self.building_name + ' ' + utility.conjugate('cost', self.building_name) + ' ' + str(base_cost) + ' money by default, which is multiplied by ' + str(self.global_manager.get('terrain_build_cost_multiplier_dict')[terrain]) + ' when built in ' + terrain + ' terrain')
        return(message)

    def generate_notification_text(self, subject):
        '''
        Description:
            Returns text regarding a particular subject for this action
        Input:
            string subject: Determines type of text to return
        Output:
            string: Returns text for the inputted subject
        '''
        text = super().generate_notification_text(subject)
        if subject == 'confirmation':
            text += 'Are you sure you want to start building a ' + self.building_name + '? /n /n'
            text += 'The planning and materials will cost ' + str(self.get_price()) + ' money. /n /n'
            text += 'If successful, a ' + self.building_name + ' will be built. '
            text += self.global_manager.get('string_descriptions')[self.building_type]
        elif subject == 'initial':
            text += 'The evangelist campaigns to increase your company\'s public opinion with word of your company\'s benevolent goals and righteous deeds in Africa. /n /n'
        elif subject == 'success':
            self.public_relations_change = random.randrange(1, 7)
            text += 'Met with gullible and enthusiastic audiences, the evangelist successfully improves your company\'s public opinion by ' + str(self.public_relations_change) + '. /n /n'
        elif subject == 'failure':
            text += 'Whether by a lack of charisma, a reluctant audience, or a doomed cause, the evangelist fails to improve your company\'s public opinion. /n /n'
        elif subject == 'critical_failure':
            text += self.generate_notification_text('failure')
            text += 'The evangelist is deeply embarassed by this public failure and decides to abandon your company. /n /n'
        elif subject == 'critical_success':
            text += self.generate_notification_text('success')
            text += 'With fiery word and true belief in his cause, the evangelist becomes a veteran and will be more successful in future ventures. /n /n'
        return(text)

    def get_price(self):
        '''
        Description:
            Calculates and returns the price of this action
        Input:
            None
        Output:
            float: Returns price of this action
        '''
        return(actor_utility.get_building_cost(self.global_manager, self.current_unit, self.building_type, self.building_name))

    def can_show(self):
        '''
        Description:
            Returns whether a button linked to this action should be drawn
        Input:
            None
        Output:
            boolean: Returns whether a button linked to this action should be drawn
        '''
        return(super().can_show() and 
               self.global_manager.get('displayed_mob').is_group and
               getattr(self.global_manager.get('displayed_mob'), self.requirement)
        )

    def on_click(self, unit):
        '''
        Description:
            Used when the player clicks a linked action button - checks if the unit can do the action, proceeding with 'start' if applicable
        Input:
            pmob unit: Unit selected when the linked button is clicked
        Output:
            None
        '''
        if super().on_click(unit):
            self.start(unit)

    def start(self, unit):
        '''
        Description:
            Used when the player clicks on the start campaign button, displays a choice notification that allows the player to campaign or not. Choosing to campaign starts the campaign process and consumes the evangelist's
                movement points
        Input:
            pmob unit: Unit selected when the linked button is clicked
        Output:
            None
        '''
        if super().start(unit):
            self.global_manager.get('notification_manager').display_notification({
                'message': action_utility.generate_risk_message(self, unit) + self.generate_notification_text('confirmation'),
                'choices': [
                    {
                    'on_click': (self.middle, []),
                    'tooltip': ['Starts a ' + self.name + ', possibly improving your company\'s public opinion'],
                    'message': 'Start campaign'
                    },
                    {
                    'on_click': (action_utility.cancel_ongoing_actions, [self.global_manager]),
                    'tooltip': ['Stop ' + self.name],
                    'message': 'Stop campaign'
                    }
                ],
            })

    def complete(self):
        '''
        Description:
            Used when the player finishes rolling for a PR campaign, shows the campaign's results and making any changes caused by the result. If successful, increases public opinion by random amount, promotes evangelist to a veteran on
                critical success. Evangelist dies on critical failure
        Input:
            None
        Output:
            None
        '''
        if self.roll_result >= self.current_min_success:
            return #build building
        super().complete()
