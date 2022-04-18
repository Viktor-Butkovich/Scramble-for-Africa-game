#Contains functionality for non-player mobs

import random
from ..mobs import mob
from .. import utility

class npmob(mob):
    '''
    Short for non-player-controlled mob, mob not controlled by the player
    '''
    def __init__(self, from_save, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates on one of the game grids
                'grids': grid list value - grids in which this mob's images can appear
                'image': string value - File path to the image used by this object
                'name': string value - Required if from save, this mob's name
                'modes': string list value - Game modes during which this mob's images can appear
                'movement_points': int value - Required if from save, how many movement points this actor currently has
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(from_save, input_dict, global_manager)
        self.hostile = False
        self.controllable = False
        self.is_npmob = True
        self.saves_normally = True #units like native warriors are attached to other objects and do not save normally
        self.npmob_type = 'npmob'
        
        self.selection_outline_color = 'bright red'
        self.last_move_direction = (0, 0)
        global_manager.get('npmob_list').append(self)
    
    def remove(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program
        Input:
            None
        Output:
            None
        '''
        super().remove()
        self.global_manager.set('npmob_list', utility.remove_from_list(self.global_manager.get('npmob_list'), self)) #make a version of npmob_list without self and set npmob_list to it

    def find_closest_target(self):
        '''
        Description:
            Find and returns one of the closest reachable pmobs or buildings
        Input:
            None
        Output:
            string/actor: Returns one of the closest reachable pmobs or buildings, or returns 'none' if none are reachable
        '''
        target_list = self.global_manager.get('pmob_list') + self.global_manager.get('building_list')
        min_distance = -1
        closest_targets = ['none']
        for possible_target in target_list:
            if possible_target.actor_type == 'building' or not (possible_target.in_vehicle or possible_target.in_group or possible_target.in_building):
                distance = utility.find_grid_distance(self, possible_target)
                if min_distance == -1 and (not distance == -1): #automatically choose first one to replace initial value
                    min_distance = distance
                    closest_targets = [possible_target]
                else:
                    if not distance == -1: #if on same grid
                        if distance < min_distance: #if closer than any previous, replace all previous
                            min_distance = distance
                            closest_targets = [possible_target]
                        elif distance == min_distance: #if as close as previous, add as alternative to previous
                            closest_targets.append(possible_target)
        return(random.choice(closest_targets)) #return one of the closest ones, or 'none' if none were found

    def attempt_local_combat(self):
        '''
        Description:
            When this unit moves, it checks if combat is possible in the cell it moved into. If combat is possible, it will attempt to start a combat at the end of the turn with any local pmobs. If, for example, another npmob killed
                the pmob found in this npmob's cell, then this npmob will not start a combat
        Input:
            None
        Output:
            None
        '''
        defender = self.images[0].current_cell.get_best_combatant('pmob')
        if not defender == 'none':
            defender.start_combat('defending', self)
        else:
            if len(self.global_manager.get('attacker_queue')) > 0:
                   self.global_manager.get('attacker_queue').pop(0).attempt_local_combat()
        
    def end_turn_move(self):
        '''
        Moves this npmob towards pmobs and buildings at the end of the turn and schedules this npmob to start combat if any pmobs are encountered. Movement is weighted based on the distance on each axis, so movement towards a pmob
            that is far to the north and slightly to the east will be more likely to move north than east
        '''
        closest_target = self.find_closest_target()
        if not closest_target == 'none':
            if closest_target.x > self.x: #decides moving left or right
                horizontal_multiplier = 1
            elif closest_target.x == self.x:
                horizontal_multiplier = 0
            else:
                horizontal_multiplier = -1

            if closest_target.y > self.y: #decides moving up or down
                vertical_multiplier = 1
            elif closest_target.y == self.y:
                vertical_multiplier = 0
            else:
                vertical_multiplier = -1


            if horizontal_multiplier == 0:
                if not vertical_multiplier == 0:
                    while self.movement_points > 0:
                        self.move(0, 1 * vertical_multiplier)
            elif vertical_multiplier == 0:
                while self.movement_points > 0:
                    self.move(1 * horizontal_multiplier, 0)
            else:
                horizontal_difference = abs(self.x - closest_target.x) #decides moving left/right or up/down
                vertical_difference = abs(self.y - closest_target.y)
                total_difference = horizontal_difference + vertical_difference #if horizontal is 3 and vertical is 2, move horizontally if random from 1 to 5 is 3 or lower: 60% chance of moving horizontally, 40% of moving vertically
                if random.randrange(0, total_difference + 1) <= horizontal_difference: #allows weighting of movement to be more likely to move along more different axis
                    while self.movement_points > 0:
                        self.move(1 * horizontal_multiplier, 0)
                else:
                    while self.movement_points > 0:
                        self.move(0, 1 * vertical_multiplier)
            if self.combat_possible():
                self.global_manager.get('attacker_queue').append(self)

    def move(self, x_change, y_change):
        '''
        Description:
            Moves this mob x_change to the right and y_change upward
        Input:
            int x_change: How many cells are moved to the right in the movement
            int y_change: How many cells are moved upward in the movement
        Output:
            None
        '''
        self.change_movement_points(-1)
        for current_image in self.images:
            current_image.remove_from_cell()
        self.x += x_change
        self.y += y_change
        for current_image in self.images:
            current_image.add_to_cell()

        if (self.is_vehicle and self.vehicle_type == 'ship') or self.images[0].current_cell.terrain == 'water': #do terrain check before embarking on ship
            self.global_manager.get('sound_manager').play_sound('water')
        else:
            self.global_manager.get('sound_manager').play_sound('footsteps')
        self.last_move_direction = (x_change, y_change)
