#Contains functionality for non-player mobs

import random
from ..mobs import mob
from .. import utility

class npmob(mob):
    '''
    Short for non-player-mob, mob not controlled by the player
    '''
    def __init__(self, from_save, input_dict, global_manager):
        super().__init__(from_save, input_dict, global_manager)
        self.hostile = False
        self.controllable = False
        self.is_npmob = True
        self.saves_normally = True #units like native warriors are attached to other objects and do not save normally
        self.npmob_type = 'npmob'
        
        self.selection_outline_color = 'bright red'
        global_manager.get('npmob_list').append(self)
        
    def remove(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program. Also deselects this mob and drops any commodities it is carrying
        Input:
            None
        Output:
            None
        '''
        super().remove()
        self.global_manager.set('npmob_list', utility.remove_from_list(self.global_manager.get('npmob_list'), self)) #make a version of npmob_list without self and set npmob_list to it

    def find_closest_target(self):
        target_list = self.global_manager.get('pmob_list') + self.global_manager.get('building_list')
        min_distance = -1
        closest_targets = ['none']
        for possible_target in target_list:
            if not (possible_target.in_vehicle or possible_target.in_group or possible_target.in_building):
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
        
    def end_turn_move(self):
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

    def move(self, x_change, y_change):
        '''
        Description:
            Moves this mob x_change to the right and y_change upward. Moving to a ship in the water automatically embarks the ship
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
