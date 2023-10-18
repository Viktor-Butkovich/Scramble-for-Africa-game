#Contains all functionality for exploration

import random
from . import action
from ..util import action_utility

class exploration(action.action):
    '''
    Action for expedition to explore a land tile
    '''
    def initial_setup(self):
        '''
        Description:
            Completes any configuration required for this action during setup - automatically called during action_setup
        Input:
            None
        Output:
            None
        '''
        super().initial_setup()
        self.global_manager.get('transaction_descriptions')[self.action_type] = 'exploration'
        self.name = 'exploration'
        self.x_change = None
        self.y_change = None
        self.direction = None
        self.future_cell = None

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
        return
    
    def pre_start(self, unit):
        '''
        Description:
            Prepares for starting an action starting with roll modifiers, setting ongoing action, etc.
        Input:
            pmob unit: Unit selected when the linked button is clicked
        Output:
            none
        '''
        super().pre_start(unit)
        self.public_relations_change = 0
        self.initial_movement_points = unit.movement_points

    def update_tooltip(self, tooltip_info_dict=None):
        '''
        Description:
            Sets this tooltip of a button linked to this action
        Input:
            None
        Output:
            None
        '''
        message = []
        if self.global_manager.get('displayed_mob').can_explore:
            message.append('Press to attempt to explore in the ' + tooltip_info_dict['direction'])
            message.append('Attempting to explore would cost ' + str(self.get_price()) + ' money and all remaining movement points, at least 1')
        else:
            message.append('This unit cannot currently move to the ' + tooltip_info_dict['direction'])
            message.append('This unit cannot move into unexplored areas')
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
            text += 'Are you sure you want to spend ' + str(self.get_price()) + ' money to attempt an exploration to the ' + self.direction + '?'
        elif subject == 'initial':
            self.future_cell = self.current_unit.grid.find_cell(self.current_unit.x + self.x_change, self.current_unit.y + self.y_change)
            text += 'The expedition heads towards the ' + self.direction + '. /n /n'
            text += (self.global_manager.get('flavor_text_manager').generate_flavor_text(self.action_type) + ' /n /n')
        elif subject == 'success':
            text += '/n'
            self.public_relations_change = random.randrange(0, 3)
            if self.future_cell.resource != 'none':
                if self.future_cell.resource == 'natives':
                    text += 'The expedition has discovered a ' + self.future_cell.terrain.upper() + ' tile containing the village of ' + self.future_cell.village.name + '. /n /n'
                else:
                    text += 'The expedition has discovered a ' + self.future_cell.terrain.upper() + ' tile with a ' + self.future_cell.resource.upper() + ' resource (currently worth ' + str(self.global_manager.get('commodity_prices')[self.future_cell.resource]) + ' money each). /n /n'
                self.public_relations_change += 3
            else:
                text += 'The expedition has discovered a ' + self.future_cell.terrain.upper() + ' tile. /n /n'
            if self.public_relations_change > 0: #Royal/National/Imperial
                text += 'The ' + self.global_manager.get('current_country').government_type_adjective.capitalize() + ' Geographical Society is pleased with these findings, increasing your public opinion by ' + str(self.public_relations_change) + '. /n /n'
        elif subject == 'failure':
            text += 'The expedition was not able to explore the tile. /n /n'
        elif subject == 'critical_failure':
            text += self.generate_notification_text('failure')
            text += 'Everyone in the expedition has died. /n /n'
        elif subject == 'critical_success':
            text += self.generate_notification_text('success')
            text += 'This explorer is now a veteran. /n /n'
        return(text)

    def generate_attached_interface_elements(self, subject):
        '''
        Description:
            Returns list of input dicts of interface elements to attach to a notification regarding a particular subject for this action
        Input:
            string subject: Determines input dicts
        Output:
            dictionary list: Returns list of input dicts for inputted subject
        '''
        return_list = super().generate_attached_interface_elements(subject)
        if subject in ['success', 'critical_success']:
            image_id_list = [action_utility.generate_background_image_input_dict()] + self.future_cell.tile.get_image_id_list(force_visibility = True) + ['misc/tile_outline.png']
            return_list.append(action_utility.generate_free_image_input_dict(image_id_list, 250, self.global_manager, override_input_dict={
                'member_config': {
                    'second_dimension_coordinate': -2, 'centered': True
                }
            }))
        return(return_list)

    def on_click(self, unit, on_click_info_dict=None):
        '''
        Description:
            Used when the player clicks a linked action button - checks if the unit can do the action, proceeding with 'start' if applicable
        Input:
            pmob unit: Unit selected when the linked button is clicked
        Output:
            None
        '''
        if super().on_click(unit):
            self.x_change = on_click_info_dict['x_change']
            self.y_change = on_click_info_dict['y_change']
            self.direction = on_click_info_dict['direction']
            self.start(unit)
            unit.create_cell_icon(unit.x + self.x_change, unit.y + self.y_change, 'misc/exploration_x/' + self.direction + '_x.png')
            return(True)
        return(False)

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
                    'tooltip': ['Attempt an exploration for ' + str(self.get_price()) + ' money'],
                    'message': 'Explore'
                    },
                    {
                    'on_click': ([action_utility.cancel_ongoing_actions, self.current_unit.clear_attached_cell_icons], [[self.global_manager], []]),
                    'tooltip': ['Stop ' + self.name],
                    'message': 'Do nothing'
                    }
                ],
            })

    def complete(self):
        '''
        Description:
            Used when the player finishes rolling for a PR campaign, shows the campaign's results and making any changes caused by the result
        Input:
            None
        Output:
            None
        '''
        if self.roll_result >= self.current_min_success:
            self.global_manager.get('public_opinion_tracker').change(self.public_relations_change)
            self.future_cell.set_visibility(True)
            if self.initial_movement_points >= self.current_unit.get_movement_cost(self.x_change, self.y_change):
                self.current_unit.set_movement_points(self.initial_movement_points)
                if self.current_unit.can_move(self.x_change, self.y_change): #checks for npmobs in explored tile
                    self.current_unit.move(self.x_change, self.y_change)
                else:
                    self.global_manager.get('minimap_grid').calibrate(self.current_unit.x, self.current_unit.y) #changes minimap to show unexplored tile without moving
            else:
                self.global_manager.get('notification_manager').display_notification({
                    'message': 'This unit\'s ' + str(self.initial_movement_points) + ' remaining movement points are not enough to move into the newly explored tile. /n /n',
                })
                self.global_manager.get('minimap_grid').calibrate(self.current_unit.x, self.current_unit.y)
        self.current_unit.set_movement_points(0)
        self.current_unit.clear_attached_cell_icons()
        super().complete()
        if self.roll_result <= self.current_max_crit_fail:
            self.current_unit.die()
