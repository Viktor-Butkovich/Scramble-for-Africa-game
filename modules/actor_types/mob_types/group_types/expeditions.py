#Contains functionality for expeditions

import random
from ..groups import group
from ....util import actor_utility, dice_utility
import modules.constants.constants as constants
import modules.constants.status as status
import modules.constants.flags as flags

class expedition(group):
    '''
    A group with an explorer officer that is able to explore and move on water
    '''
    def __init__(self, from_save, input_dict):
        '''
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates on one of the game grids
                'grids': grid list value - grids in which this group's images can appear
                'image': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'name': string value - Required if from save, this group's name
                'modes': string list value - Game modes during which this group's images can appear
                'end_turn_destination': string or int tuple value - Required if from save, 'none' if no saved destination, destination coordinates if saved destination
                'end_turn_destination_grid_type': string value - Required if end_turn_destination is not 'none', matches the status key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - Required if from save, how many movement points this actor currently has
                'max_movement_points': int value - Required if from save, maximum number of movement points this mob can have
                'worker': worker or dictionary value - If creating a new group, equals a worker that is part of this group. If loading, equals a dictionary of the saved information necessary to recreate the worker
                'officer': worker or dictionary value - If creating a new group, equals an officer that is part of this group. If loading, equals a dictionary of the saved information necessary to recreate the officer
                'canoes_image': string value - File path to the image used by this object when it is in a river
        Output:
            None
        '''
        super().__init__(from_save, input_dict)
        self.can_explore = True
        self.set_has_canoes(True)
        
        self.set_group_type('expedition')
        if self.images[0].current_cell != 'none': #if did not just board vehicle
            self.resolve_off_tile_exploration()

    def move(self, x_change, y_change):
        '''
        Description:
            Moves this mob x_change to the right and y_change upward. Moving to a ship in the water automatically embarks the ship. Also allows exploration when moving into unexplored areas. Attempting an exploration starts the
                exploration process, which requires various dice rolls to succeed and can also result in the death of the expedition or the promotion of its explorer. A successful exploration uncovers the area and units to move into it
                normally in the future. As expeditions move, they automatically discover adjacent water tiles, and they also automatically discover all adjacent tiles when looking from a water tile
        Input:
            int x_change: How many cells are moved to the right in the movement
            int y_change: How many cells are moved upward in the movement
        Output:
            None
        '''
        flags.show_selection_outlines = True
        flags.show_minimap_outlines = True
        constants.last_selection_outline_switch = constants.current_time
        
        future_x = self.x + x_change
        future_y = self.y + y_change
        roll_result = 0
        if x_change > 0:
            direction = 'east'
        elif x_change < 0:
            direction = 'west'
        elif y_change > 0:
            direction = 'north'
        elif y_change < 0:
            direction = 'south'
        else:
            direction = 'none'
        future_cell = self.grid.find_cell(future_x, future_y)
        if future_cell.visible == False: #if moving to unexplored area, try to explore it
            status.actions['exploration'].on_click(self, on_click_info_dict={'x_change': x_change, 'y_change': y_change, 'direction': direction})
        else: #if moving to explored area, move normally
            super().move(x_change, y_change)
            if self.images[0].current_cell != 'none': #if not in vehicle
                self.resolve_off_tile_exploration()

    def disembark_vehicle(self, vehicle):
        '''
        Description:
            Shows this mob and disembarks it from the inputted vehicle after being a passenger. Also automatically explores nearby tiles when applicable, as if this expedition had moved
        Input:
            vehicle vehicle: vehicle that this mob disembarks from
        Output:
            None
        '''
        super().disembark_vehicle(vehicle)
        self.resolve_off_tile_exploration()

    def resolve_off_tile_exploration(self):
        '''
        Description:
            Whenever an expedition arrives in a tile for any reason, they automatically discover any adjacent water tiles. Additionally, when standing on water, they automatically discover all adjacent tiles
        Input:
            None
        Output:
            None
        '''
        self.current_action_type = 'exploration' #used in action notification to tell whether off tile notification should explore tile or not
        cardinal_directions = {'up': 'north', 'down': 'south', 'right': 'east', 'left': 'west'}
        current_cell = self.images[0].current_cell
        for current_direction in ['up', 'down', 'left', 'right']:
            target_cell = current_cell.adjacent_cells[current_direction]
            if target_cell and not target_cell.visible:
                if current_cell.terrain == 'water' or target_cell.terrain == 'water': #if on water, discover all adjacent undiscovered tiles. Also, discover all adjacent water tiles, regardless of if currently on water
                    if current_cell.terrain == 'water':
                        text = 'From the water, the expedition has discovered a '
                    elif target_cell.terrain == 'water':
                        text = 'The expedition has discovered a '
                    public_opinion_increase = random.randrange(0, 3)
                    if not target_cell.resource == 'none':
                        if target_cell.resource == 'natives':
                            text += target_cell.terrain.upper() + ' tile to the ' + cardinal_directions[current_direction] + ' that contains the village of ' + target_cell.village.name + '. /n /n'
                        else:
                            text += target_cell.terrain.upper() + ' tile with a ' + target_cell.resource.upper() + ' resource (currently worth ' + str(constants.commodity_prices[target_cell.resource]) + ' money each) to the ' + cardinal_directions[current_direction] + '. /n /n'
                        public_opinion_increase += 3
                    else:
                        text += target_cell.terrain.upper() + ' tile to the ' + cardinal_directions[current_direction] + '. /n /n'

                    if public_opinion_increase > 0: #Royal/National/Imperial
                        text += 'The ' + status.current_country.government_type_adjective.capitalize() + ' Geographical Society is pleased with these findings, increasing your public opinion by ' + str(public_opinion_increase) + '. /n /n'
                    
                    flags.ongoing_action = True
                    constants.notification_manager.display_notification({
                        'message': text + 'Click to remove this notification. /n /n',
                        'notification_type': 'off_tile_exploration',
                        'extra_parameters': {
                            'cell': target_cell,
                            'reveal_cell': True,
                            'public_opinion_increase': public_opinion_increase
                        }
                    })
