import pygame
import random

from ..mobs import mob
from .. import text_tools
from .. import utility
from .. import actor_utility
from .. import notification_tools
from .. import dice
from .. import scaling
from .. import images

class pmob(mob):
    '''
    mob that can be controlled
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
                'end_turn_destination': string or int tuple value - Required if from save, 'none' if no saved destination, destination coordinates if saved destination
                'end_turn_destination_grid_type': string - Required if end_turn_destination is not 'none', matches the global manager key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - Required if from save, how many movement points this actor currently has
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''   
        super().__init__(from_save, input_dict, global_manager)
        self.selection_outline_color = 'bright green'
        global_manager.get('pmob_list').append(self)
        self.is_pmob = True

        self.set_controlling_minister_type('none')
        if from_save:
            if not input_dict['end_turn_destination'] == 'none': #end turn destination is a tile and can't be pickled, need to find it again after loading
                end_turn_destination_x, end_turn_destination_y = input_dict['end_turn_destination']
                end_turn_destination_grid = self.global_manager.get(input_dict['end_turn_destination_grid_type'])
                self.end_turn_destination = end_turn_destination_grid.find_cell(end_turn_destination_x, end_turn_destination_y).tile
            else:
                self.end_turn_destination = 'none'
        else:
            self.end_turn_destination = 'none'
            actor_utility.deselect_all(self.global_manager)
            self.select()
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), self.images[0].current_cell.tile)

        self.current_roll_modifier = 0
        self.default_min_success = 4
        self.default_max_crit_fail = 1
        self.default_min_crit_success = 6

    def to_save_dict(self):
        '''
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
                'init_type': string value - Represents the type of actor this is, used to initialize the correct type of object on loading
                'coordinates': int tuple value - Two values representing x and y coordinates on one of the game grids
                'modes': string list value - Game modes during which this actor's images can appear
                'grid_type': string value - String matching the global manager key of this actor's primary grid, allowing loaded object to start in that grid
                'name': string value - This actor's name
                'inventory': string/string dictionary value - Version of this actor's inventory dictionary only containing commodity types with 1+ units held
                'end_turn_destination': string or int tuple value- 'none' if no saved destination, destination coordinates if saved destination
                'end_turn_destination_grid_type': string value - Required if end_turn_destination is not 'none', matches the global manager key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - How many movement points this actor currently has
                'image': string value - File path to the image used by this object
        '''
        save_dict = super().to_save_dict()
        if self.end_turn_destination == 'none':
            save_dict['end_turn_destination'] = 'none'
        else: #end turn destination is a tile and can't be pickled, need to save its location to find it again after loading
            for grid_type in self.global_manager.get('grid_types_list'):
                if self.end_turn_destination.grid == self.global_manager.get(grid_type):
                    save_dict['end_turn_destination_grid_type'] = grid_type
            save_dict['end_turn_destination'] = (self.end_turn_destination.x, self.end_turn_destination.y)
        return(save_dict)

    def remove(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program. Also deselects this mob and drops any commodities it is carrying
        Input:
            None
        Output:
            None
        '''
        if (not self.images[0].current_cell == 'none') and (not self.images[0].current_cell.tile == 'none'): #drop inventory on death
            current_tile = self.images[0].current_cell.tile
            for current_commodity in self.global_manager.get('commodity_types'):
                current_tile.change_inventory(current_commodity, self.get_inventory(current_commodity))
        super().remove()
        self.global_manager.set('pmob_list', utility.remove_from_list(self.global_manager.get('pmob_list'), self)) #make a version of pmob_list without self and set pmob_list to it

    def draw_outline(self):
        '''
        Description:
            Draws a flashing outline around this mob if it is selected, also shows its end turn destination, if any
        Input:
            None
        Output:
            None
        '''
        if self.global_manager.get('show_selection_outlines'):
            for current_image in self.images:
                if not current_image.current_cell == 'none' and self == current_image.current_cell.contained_mobs[0]: #only draw outline if on top of stack
                    pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')[self.selection_outline_color], (current_image.outline), current_image.outline_width)
            if (not self.end_turn_destination == 'none') and self.end_turn_destination.images[0].can_show(): #only show outline if tile is showing
                self.end_turn_destination.draw_destination_outline()
                equivalent_tile = self.end_turn_destination.get_equivalent_tile()
                if not equivalent_tile == 'none':
                    equivalent_tile.draw_destination_outline()

    def check_if_minister_appointed(self):
        '''
        Description:
            Returns whether there is currently an appointed minister to control this unit
        Input:
            None
        Output:
            boolean: Returns whether there is currently an appointed minister to control this unit
        '''
        if not self.controlling_minister == 'none':
            return(True)
        else:
            keyword = self.global_manager.get('minister_type_dict')[self.controlling_minister_type]
            text_tools.print_to_screen("", self.global_manager)
            text_tools.print_to_screen("You can not do " + keyword + " actions because a " + self.controlling_minister_type + " has not been appointed", self.global_manager)
            text_tools.print_to_screen("Press q or the button in the upper left corner of the screen to manage your ministers", self.global_manager)
            return(False)

    def set_controlling_minister_type(self, new_type):
        '''
        Description:
            Sets the type of minister that controls this unit, like "Minister of Trade"
        Input:
            Type of minister to control this unit, like "Minister of Trade"
        Output:
            None
        '''
        self.controlling_minister_type = new_type
        self.update_controlling_minister()

    def update_controlling_minister(self):
        '''
        Description:
            Sets the minister that controls this unit to the one occupying the office that has authority over this unit
        Input:
            None
        Output:
            None
        '''
        if self.controlling_minister_type == 'none':
            self.controlling_minister = 'none'
        else:
            self.controlling_minister = self.global_manager.get('current_ministers')[self.controlling_minister_type]
            for current_minister_type_image in self.global_manager.get('minister_image_list'):
                if current_minister_type_image.minister_type == self.controlling_minister_type:
                    current_minister_type_image.calibrate(self.controlling_minister)

    def end_turn_move(self):
        '''
        Description:
            If this mob has any pending movement orders at the end of the turn, this executes the movement. Currently used to move ships between Africa and Europe at the end of the turn
        Input:
            None
        Output:
            None
        '''
        if not self.end_turn_destination == 'none':
            if self.grids[0] in self.end_turn_destination.grids: #if on same grid
                nothing = 0 #do later
            else: #if on different grid
                if self.can_travel():
                    self.go_to_grid(self.end_turn_destination.grids[0], (self.end_turn_destination.x, self.end_turn_destination.y))
            self.end_turn_destination = 'none'
    
    def can_travel(self): #if can move between Europe, Africa, etc.
        '''
        Description:
            Returns whether this mob can cross the ocean, like going between Africa and Europe. By default, mobs cannot cross the ocean, but subclasses like ship are able to return True
        Input:
            None
        Output:
            boolean: Returns True if this mob can cross the ocean, otherwise returns False
        '''
        return(False) #different for subclasses

    def change_inventory(self, commodity, change):
        '''
        Description:
            Changes the number of commodities of a certain type held by this mob. Also ensures that the mob info display is updated correctly
        Input:
            string commodity: Type of commodity to change the inventory of
            int change: Amount of commodities of the inputted type to add. Removes commodities of the inputted type if negative
        Output:
            None
        '''
        if self.can_hold_commodities:
            self.inventory[commodity] += change
            if self.global_manager.get('displayed_mob') == self:
                actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self)

    def set_inventory(self, commodity, new_value):
        '''
        Description:
            Sets the number of commodities of a certain type held by this mob. Also ensures that the mob info display is updated correctly
        Input:
            string commodity: Type of commodity to set the inventory of
            int new_value: Amount of commodities of the inputted type to set inventory to
        Output:
            None
        '''
        if self.can_hold_commodities:
            self.inventory[commodity] = new_value
            if self.global_manager.get('displayed_mob') == self:
                actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self)

    def fire(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program. Used instead of die to improve consistency with workers/groups/vehicles, whose die and fire have different
                functionalities
        Input:
            None
        Output:
            None
        '''
        self.die()

    def can_leave(self):
        '''
        Description:
            Returns whether this mob is allowed to move away from its current cell. By default, mobs can always allowed to move away from their current cells, but subclasses like ship are able to return False
        Input:
            None
        Output:
            boolean: Returns True
        '''
        return(True) #different in subclasses, controls whether anything in starting tile would prevent leaving, while can_move sees if anything in destination would prevent entering

    def can_move(self, x_change, y_change):
        '''
        Description:
            Returns whether this mob can move to the tile x_change to the right of it and y_change above it. Movement can be prevented by not being able to move on water/land, the edge of the map, limited movement points, etc.
        Input:
            int x_change: How many cells would be moved to the right in the hypothetical movement
            int y_change: How many cells would be moved upward in the hypothetical movement
        Output:
            boolean: Returns True if this mob can move to the proposed destination, otherwise returns False
        '''
        future_x = self.x + x_change
        future_y = self.y + y_change
        if self.can_leave():
            if not self.grid in self.global_manager.get('abstract_grid_list'):
                if future_x >= 0 and future_x < self.grid.coordinate_width and future_y >= 0 and future_y < self.grid.coordinate_height:
                    future_cell = self.grid.find_cell(future_x, future_y)
                    if future_cell.visible or self.can_explore:
                        destination_type = 'land'
                        if future_cell.terrain == 'water':
                            destination_type = 'water' #if can move to destination, possible to move onto ship in water, possible to 'move' into non-visible water while exploring
                        if ((destination_type == 'land' and (self.can_walk or self.can_explore or (future_cell.has_port() and self.images[0].current_cell.terrain == 'water'))) or
                            (destination_type == 'water' and (self.can_swim or (future_cell.has_vehicle('ship') and not self.is_vehicle) or (self.can_explore and not future_cell.visible)))): 
                            if self.movement_points >= self.get_movement_cost(x_change, y_change) or self.has_infinite_movement and self.movement_points > 0: #self.movement_cost:
                                return(True)
                            else:
                                text_tools.print_to_screen("You do not have enough movement points to move.", self.global_manager)
                                text_tools.print_to_screen("You have " + str(self.movement_points) + " movement points while " + str(self.get_movement_cost(x_change, y_change)) + " are required.", self.global_manager)
                                return(False)
                        elif destination_type == 'land' and not self.can_walk: #if trying to walk on land and can't
                            #if future_cell.visible or self.can_explore: #already checked earlier
                            text_tools.print_to_screen("You can not move on land with this unit unless there is a port.", self.global_manager)
                            return(False)
                        else: #if trying to swim in water and can't 
                            #if future_cell.visible or self.can_explore: #already checked earlier
                            text_tools.print_to_screen("You can not move on water with this unit.", self.global_manager)
                            return(False)
                    else:
                        text_tools.print_to_screen("You can not move into an unexplored tile.", self.global_manager)
                        return(False)
                else:
                    text_tools.print_to_screen("You can not move off of the map.", self.global_manager)
                    return(False)
            else:
                text_tools.print_to_screen("You can not move while in this area.", self.global_manager)
                return(False)

    def can_show_tooltip(self):
        '''
        Description:
            Returns whether this mob's tooltip can be shown. Along with the superclass' requirements, mob tooltips can not be shown when attached to another actor, such as when working in a building
        Input:
            None
        Output:
            None
        '''
        if self.in_vehicle or self.in_group or self.in_building:
            return(False)
        else:
            return(super().can_show_tooltip())

    def embark_vehicle(self, vehicle):
        '''
        Description:
            Hides this mob and embarks it on the inputted vehicle as a passenger. Any commodities held by this mob are put on the vehicle if there is cargo space, or dropped in its tile if there is no cargo space
        Input:
            vehicle vehicle: vehicle that this mob becomes a passenger of
        Output:
            None
        '''
        self.in_vehicle = True
        self.selected = False
        for current_commodity in self.get_held_commodities(): #gives inventory to ship
            num_held = self.get_inventory(current_commodity)
            for current_commodity_unit in range(num_held):
                if vehicle.get_inventory_remaining() > 0:
                    vehicle.change_inventory(current_commodity, 1)
                else:
                    self.images[0].current_cell.tile.change_inventory(current_commodity, 1)
        self.hide_images()
        vehicle.contained_mobs.append(self)
        self.inventory_setup() #empty own inventory
        vehicle.hide_images()
        vehicle.show_images() #moves vehicle images to front
        if not vehicle.initializing: #don't select vehicle if loading in at start of game
            vehicle.select()
        if not self.global_manager.get('loading_save'):
            self.global_manager.get('sound_manager').play_sound('footsteps')

    def disembark_vehicle(self, vehicle):
        '''
        Description:
            Shows this mob and disembarks it from the inputted vehicle after being a passenger
        Input:
            vehicle vehicle: vehicle that this mob disembarks from
        Output:
            None
        '''
        vehicle.contained_mobs = utility.remove_from_list(vehicle.contained_mobs, self)
        self.in_vehicle = False
        self.x = vehicle.x
        self.y = vehicle.y
        for current_image in self.images:
            current_image.add_to_cell()
        vehicle.selected = False
        self.select()
        if self.global_manager.get('minimap_grid') in self.grids:
            self.global_manager.get('minimap_grid').calibrate(self.x, self.y)
        actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), self.images[0].current_cell.tile)
        self.global_manager.get('sound_manager').play_sound('footsteps')

    def start_combat(self, combat_type, enemy):
        if combat_type == 'defending': #if being attacked on main grid, move minimap there to show location
            if self.global_manager.get('strategic_map_grid') in self.grids:
                self.global_manager.get('minimap_grid').calibrate(self.x, self.y)
                
        self.current_roll_modifier = 0
        self.current_min_success = self.default_min_success
        self.current_max_crit_fail = 0 #construction shouldn't have critical failures
        self.current_min_crit_success = self.default_min_crit_success
        
        self.current_min_success -= self.current_roll_modifier #positive modifier reduces number required for succcess, reduces maximum that can be crit fail
        self.current_max_crit_fail -= self.current_roll_modifier
        if self.current_min_success > self.current_min_crit_success:
            self.current_min_crit_success = self.current_min_success #if 6 is a failure, should not be critical success. However, if 6 is a success, it will always be a critical success
        choice_info_dict = {'constructor': self, 'type': 'start construction'}
        self.global_manager.set('ongoing_combat', True)
        if combat_type == 'defending':
            message = "Your " + self.name + " is being attacked by " + enemy.name + " at (" + str(self.x) + ", " + str(self.y) + ")."
        elif combat_type == 'attacking':
            message = "Your " + self.name + " is attacking " + enemy.name + " at (" + str(self.x) + ", " + str(self.y) + ")."
        self.current_combat_type = combat_type
        self.current_enemy = enemy
        notification_tools.display_notification(message, 'default', self.global_manager)
        self.combat() #later call next step when closing combat action notification instead of immediately

    def combat(self):
        #show combat rolls and such
        combat_type = self.current_combat_type
        enemy = self.current_enemy
        own_roll = random.randrange(1, 7)
        enemy_roll = random.randrange(1, 7)
        result = own_roll - enemy_roll
        if result <= -2:
            conclusion = 'lose'
        elif result <= 1:
            conclusion = 'draw'
        else:
            conclusion = 'win'
        message = self.name + ' roll: ' + str(own_roll)
        message += enemy.name + ' roll: ' + str(enemy_roll)
        message = 'Result: ' + str(result) + ' - ' + conclusion
        notification_tools.display_notification(message, 'default', self.global_manager)
        self.complete_combat(conclusion)

    def complete_combat(self, conclusion):
        combat_type = self.current_combat_type
        enemy = self.current_enemy
        if conclusion == 'win':
            enemy.die()
            message = enemy.name  + ' has died.'
        elif conclusion == 'draw':
            if combat_type == 'defending':
                enemy.retreat() #have as function of npmobs
                message = enemy.name + ' has been forced to retreat.'
            elif combat_type == 'attacking':
                self.retreat() #have as function of military units only
                message = 'Your ' + self.name + ' has been forced to retreat.'
        elif conclusion == 'lose':
            self.die()
            message = 'Your ' + self.name + ' has died.'
        notification_tools.display_notification(message, 'default', self.global_manager)
        self.global_manager.set('ongoing_combat', False)
        if len(self.global_manager.get('attacker_queue')) > 0:
            self.global_manager.get('attacker_queue').pop(0).attempt_local_combat()
        
        

    def construct(self):
        '''
        Description:
            Controls the construction process, determining and displaying its result through a series of notifications
        Input:
            None
        Output:
            None
        '''
        self.current_construction_type = 'default'
        roll_result = 0
        self.just_promoted = False
        self.set_movement_points(0)
        self.global_manager.get('money_tracker').change(-1 * self.global_manager.get('building_prices')[self.building_type], 'construction')
        text = ""
        text += "The " + self.name + " attempts to construct a " + self.building_name + ". /n /n"
        if not self.veteran:    
            notification_tools.display_notification(text + "Click to roll. " + str(self.current_min_success) + "+ required to succeed.", 'construction', self.global_manager)
        else:
            text += ("The " + self.officer.name + " can roll twice and pick the higher result. /n /n")
            notification_tools.display_notification(text + "Click to roll. " + str(self.current_min_success) + "+ required on at least 1 die to succeed.", 'construction', self.global_manager)

        notification_tools.display_notification(text + "Rolling... ", 'roll', self.global_manager)

        die_x = self.global_manager.get('notification_manager').notification_x - 140

        if self.veteran:
            results = self.controlling_minister.roll_to_list(6, self.current_min_success, self.current_max_crit_fail, 2)
            #result = self.controlling_minister.roll(6, self.current_min_success, self.current_max_crit_fail)
            first_roll_list = dice_utility.roll_to_list(6, "Construction roll", self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, results[0])
            self.display_die((die_x, 500), first_roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)

            #result = self.controlling_minister.roll(6, self.current_min_success, self.current_max_crit_fail)
            second_roll_list = dice_utility.roll_to_list(6, "second", self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, results[1])
            self.display_die((die_x, 380), second_roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)
                                
            text += (first_roll_list[1] + second_roll_list[1]) #add strings from roll result to text
            roll_result = max(first_roll_list[0], second_roll_list[0])
            result_outcome_dict = {}
            for i in range(1, 7):
                if i <= self.current_max_crit_fail:
                    word = "CRITICAL FAILURE"
                elif i >= self.current_min_crit_success:
                    word = "CRITICAL SUCCESS"
                elif i >= self.current_min_success:
                    word = "SUCCESS"
                else:
                    word = "FAILURE"
                result_outcome_dict[i] = word
            text += ("The higher result, " + str(roll_result) + ": " + result_outcome_dict[roll_result] + ", was used. /n")
        else:
            result = self.controlling_minister.roll(6, self.current_min_success, self.current_max_crit_fail)
            roll_list = dice_utility.roll_to_list(6, "Construction roll", self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, result)
            self.display_die((die_x, 440), roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)
                
            text += roll_list[1]
            roll_result = roll_list[0]

        notification_tools.display_notification(text + "Click to continue.", 'construction', self.global_manager)
            
        text += "/n"
        if roll_result >= self.current_min_success:
            text += "The " + self.name + " successfully constructed the " + self.building_name + ". /n"
        else:
            text += "Little progress was made and the " + self.officer.name + " requests more time and funds to complete the construction of the " + self.building_name + ". /n"

        if (not self.veteran) and roll_result >= self.current_min_crit_success:
            self.just_promoted = True
            text += " /nThe " + self.officer.name + " managed the construction well enough to become a veteran. /n"
        if roll_result >= 4:
            notification_tools.display_notification(text + " /nClick to remove this notification.", 'final_construction', self.global_manager)
        else:
            notification_tools.display_notification(text, 'default', self.global_manager)
        self.global_manager.set('construction_result', [self, roll_result])  

        
    def complete_construction(self):
        '''
        Description:
            Used when the player finishes rolling for construction, shows the construction's results and makes any changes caused by the result. If successful, the building is constructed, promotes engineer to a veteran on critical
                success
        Input:
            None
        Output:
            None
        '''
        roll_result = self.global_manager.get('construction_result')[1]
        if roll_result >= self.current_min_success: #if campaign succeeded
            if roll_result >= self.current_min_crit_success and not self.veteran:
                self.promote()
            self.set_movement_points(0)

            input_dict = {}
            input_dict['coordinates'] = (self.x, self.y)
            input_dict['grids'] = self.grids
            input_dict['name'] = self.building_name
            input_dict['modes'] = ['strategic']
            input_dict['init_type'] = self.building_type
            if not self.building_type == 'train':
                if not self.images[0].current_cell.contained_buildings[self.building_type] == 'none': #if building of same type exists, remove it and replace with new one
                    self.images[0].current_cell.contained_buildings[self.building_type].remove()
            if self.building_type == 'resource':
                input_dict['image'] = self.global_manager.get('resource_building_dict')[self.attached_resource]
                input_dict['resource_type'] = self.attached_resource
            elif self.building_type == 'infrastructure':
                building_image_id = 'none'
                if self.building_name == 'road':
                    building_image_id = 'buildings/infrastructure/road.png'
                elif self.building_name == 'railroad':
                    building_image_id = 'buildings/infrastructure/railroad.png'
                input_dict['image'] = building_image_id
                input_dict['infrastructure_type'] = self.building_name
            elif self.building_type == 'port':
                input_dict['image'] = 'buildings/port.png'
            elif self.building_type == 'train_station':
                input_dict['image'] = 'buildings/train_station.png'
            elif self.building_type == 'trading_post':
                input_dict['image'] = 'buildings/trading_post.png'
            elif self.building_type == 'mission':
                input_dict['image'] = 'buildings/mission.png'
            elif self.building_type == 'train':
                image_dict = {'default': 'mobs/train/crewed.png', 'crewed': 'mobs/train/crewed.png', 'uncrewed': 'mobs/train/uncrewed.png'}
                input_dict['image_dict'] = image_dict
                input_dict['crew'] = 'none'
            else:
                input_dict['image'] = 'buildings/' + self.building_type + '.png'
            self.global_manager.get('actor_creation_manager').create(False, input_dict, self.global_manager)
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), self.images[0].current_cell.tile) #update tile display to show new building
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self) #update mob display to show new upgrade possibilities
        self.global_manager.set('ongoing_construction', False)

    def display_die(self, coordinates, result, min_success, min_crit_success, max_crit_fail, uses_minister = True):
        '''
        Description:
            Creates a die object at the inputted location and predetermined roll result to use for multi-step notification dice rolls. Also shows a picture of the minister controlling the roll. The color of the die's outline depends on
                the result
        Input:
            int tuple coordinates: Two values representing x and y pixel coordinates for the bottom left corner of the die
            int result: Predetermined result that the die will end on after rolling
            int min_success: Minimum roll required for a success
            int min_crit_success: Minimum roll required for a critical success
            int max_crit_fail: Maximum roll required for a critical failure
        Output:
            None
        '''
        result_outcome_dict = {'min_success': min_success, 'min_crit_success': min_crit_success, 'max_crit_fail': max_crit_fail}
        outcome_color_dict = {'success': 'dark green', 'fail': 'dark red', 'crit_success': 'bright green', 'crit_fail': 'bright red', 'default': 'black'}
        new_die = dice.die(scaling.scale_coordinates(coordinates[0], coordinates[1], self.global_manager), scaling.scale_width(100, self.global_manager), scaling.scale_height(100, self.global_manager), self.modes, 6,
            result_outcome_dict, outcome_color_dict, result, self.global_manager)
        if uses_minister:
            minister_icon_coordinates = (coordinates[0], coordinates[1] + 120)
            minister_position_icon = images.dice_roll_minister_image(minister_icon_coordinates, scaling.scale_width(100, self.global_manager), scaling.scale_height(100, self.global_manager), self.modes, self.controlling_minister,
                'position', self.global_manager)
            minister_portrait_icon = images.dice_roll_minister_image(minister_icon_coordinates, scaling.scale_width(100, self.global_manager), scaling.scale_height(100, self.global_manager), self.modes, self.controlling_minister,
                'portrait', self.global_manager)
        
