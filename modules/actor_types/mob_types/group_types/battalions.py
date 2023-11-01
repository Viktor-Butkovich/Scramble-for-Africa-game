#Contains functionality for battalions

from ..groups import group
from ....util import actor_utility
import modules.constants.constants as constants
import modules.constants.status as status
import modules.constants.flags as flags

class battalion(group):
    '''
    A group with a major officer that can attack non-beast enemies
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
        Output:
            None
        '''
        super().__init__(from_save, input_dict)
        self.is_battalion = True
        if self.worker.worker_type == 'European':
            self.battalion_type = 'imperial'
        else:
            self.battalion_type = 'colonial'
        self.set_group_type('battalion')
        if not from_save:
            actor_utility.calibrate_actor_info_display(status.mob_info_display, self) #updates label to show new combat strength

    def get_movement_cost(self, x_change, y_change, post_attack = False):
        '''
        Description:
            Returns the cost in movement points of moving by the inputted amounts. Only works when one inputted amount is 0 and the other is 1 or -1, with 0 and -1 representing moving 1 cell downward
        Input:
            int x_change: How many cells would be moved to the right in the hypothetical movement
            int y_change: How many cells would be moved upward in the hypothetical movement
            boolean post_attack = False: Whether this movement is occuring directly after an attack order or not. A battalion/safari can move into a cell to attack it by using only 1 movement point but must return afterward if not
                enough movement points to move there normally
        Output:
            double: How many movement points would be spent by moving by the inputted amount
        '''
        cost = self.movement_cost
        if not (self.is_npmob and not self.visible()):
            local_cell = self.images[0].current_cell
        else:
            local_cell = self.grids[0].find_cell(self.x, self.y)

        direction = 'none'
        if x_change < 0:
            direction = 'left'
        elif x_change > 0:
            direction = 'right'
        elif y_change > 0:
            direction = 'up'
        elif y_change < 0:
            direction = 'down'
        elif x_change == 0 and y_change == 0:
            direction = 'none'
            
        if direction == 'none':
            adjacent_cell = local_cell
        else:
            adjacent_cell = local_cell.adjacent_cells[direction]
            
        if adjacent_cell:
            if (not post_attack) and self.is_battalion and not adjacent_cell.get_best_combatant('npmob') == 'none': #if battalion attacking non-beast
                cost = 1
            elif (not post_attack) and self.is_safari and not adjacent_cell.get_best_combatant('npmob', 'beast') == 'none': #if safari attacking beast
                cost = 1
            else:
                cost = super().get_movement_cost(x_change, y_change)
        return(cost)

    def move(self, x_change, y_change, attack_confirmed = False):
        '''
        Description:
            Moves this mob x_change to the right and y_change upward. Moving to a ship in the water automatically embarks the ship. If moving into a cell with an npmob, asks for a confirmation to attack instead of moving. If the attack
                is confirmed, move is called again to cause a combat to start
        Input:
            int x_change: How many cells are moved to the right in the movement
            int y_change: How many cells are moved upward in the movement
            boolean attack_confirmed = False: Whether an attack has already been confirmed. If an attack has been confirmed, a move into the target cell will occur and a combat will start
        Output:
            None
        '''
        flags.show_selection_outlines = True
        flags.show_minimap_outlines = True
        constants.last_selection_outline_switch = constants.current_time #outlines should be shown immediately when selected
        if not status.actions['combat'].on_click(
            self,
            on_click_info_dict={
                'x_change': x_change,
                'y_change': y_change,
                'attack_confirmed': attack_confirmed
            }
        ): #if destination empty or attack already confirmed, move in
            initial_movement_points = self.movement_points
            if attack_confirmed:
                original_disorganized = self.disorganized
            super().move(x_change, y_change)
            if attack_confirmed:
                self.set_disorganized(original_disorganized) #cancel effect from moving into river until after combat
            if attack_confirmed:
                self.set_movement_points(initial_movement_points) #gives back movement points for moving, movement points will be consumed anyway for attacking but will allow unit to move onto beach after disembarking ship

class safari(battalion):
    '''
    A group with a hunter officer that can track down and attack beast enemies
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
                'image': string value - File path to the image used by this object
                'name': string value - Required if from save, this group's name
                'modes': string list value - Game modes during which this group's images can appear
                'end_turn_destination': string or int tuple value - Required if from save, 'none' if no saved destination, destination coordinates if saved destination
                'end_turn_destination_grid_type': string value - Required if end_turn_destination is not 'none', matches the status key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - Required if from save, how many movement points this actor currently has
                'max_movement_points': int value - Required if from save, maximum number of movement points this mob can have
                'worker': worker or dictionary value - If creating a new group, equals a worker that is part of this group. If loading, equals a dictionary of the saved information necessary to recreate the worker
                'officer': worker or dictionary value - If creating a new group, equals an officer that is part of this group. If loading, equals a dictionary of the saved information necessary to recreate the officer
                'canoes_image': string value - File path tothe image used by this object when it is in a river
        Output:
            None
        '''
        super().__init__(from_save, input_dict)    
        self.is_battalion = False
        self.is_safari = True
        self.set_has_canoes(True)
        self.battalion_type = 'none'
        self.set_group_type('safari')
        if not from_save:
            actor_utility.calibrate_actor_info_display(status.mob_info_display, self) #updates label to show new combat strength
