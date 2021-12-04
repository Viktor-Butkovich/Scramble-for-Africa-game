#Contains functionality for group units

import time
import random
import math
from .mobs import mob
from .tiles import tile
from .tiles import veteran_icon
from .buttons import button
from . import actor_utility
from . import text_tools
from . import dice_utility
from . import utility
from . import notification_tools
from . import dice
from . import scaling
from . import main_loop_tools

class group(mob):
    '''
    Mob that is created by a combination of a worker and officer, has special capabilities depending on its officer, and separates its worker and officer upon being disbanded
    '''
    def __init__(self, from_save, input_dict, global_manager):
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
                'end_turn_destination_grid_type': string value - Required if end_turn_destination is not 'none', matches the global manager key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - Required if from save, how many movement points this actor currently has
                'worker': worker or dictionary value - If creating a new group, equals a worker that is part of this group. If loading, equals a dictionary of the saved information necessary to recreate the worker
                'officer': worker or dictionary value - If creating a new group, equals an officer that is part of this group. If loading, equals a dictionary of the saved information necessary to recreate the officer
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        if not from_save:
            self.worker = input_dict['worker']
            self.officer = input_dict['officer']
        else:
            self.worker = global_manager.get('actor_creation_manager').create(True, input_dict['worker'], global_manager)
            self.officer = global_manager.get('actor_creation_manager').create(True, input_dict['officer'], global_manager)
        super().__init__(from_save, input_dict, global_manager)
        self.worker.join_group()
        self.officer.join_group()
        self.is_group = True
        self.veteran = self.officer.veteran
        for current_commodity in self.global_manager.get('commodity_types'): #merges individual inventory to group inventory and clears individual inventory
            self.change_inventory(current_commodity, self.worker.get_inventory(current_commodity))
            self.change_inventory(current_commodity, self.officer.get_inventory(current_commodity))
        self.worker.inventory_setup()
        self.officer.inventory_setup()
        if not from_save:
            self.select()
            if self.veteran:
                self.set_name("Veteran " + self.name.lower())
        self.veteran_icons = self.officer.veteran_icons
        for current_veteran_icon in self.veteran_icons:
            current_veteran_icon.actor = self
        self.global_manager.get('group_list').append(self)
        if not from_save:
            if self.worker.movement_points > self.officer.movement_points: #a group should keep the lowest movement points out of its members
                self.set_movement_points(self.officer.movement_points)
            else:
                self.set_movement_points(self.worker.movement_points)
        self.current_roll_modifier = 0
        self.default_min_success = 4
        self.default_max_crit_fail = 1
        self.default_min_crit_success = 6
        self.set_group_type('none')

    def set_group_type(self, new_type):
        '''
        Description:
            Sets this group's type to the inputted value, determining its capabilities and which minister controls it
        Input:
            string new_type: Type to set this group to, like 'missionaries'
        Output:
            None
        '''
        self.group_type = new_type
        if not new_type == 'none':
            self.set_controlling_minister_type(self.global_manager.get('group_minister_dict')[self.group_type])
        else:
            self.set_controlling_minister_type('none')

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
                'worker': dictionary value - dictionary of the saved information necessary to recreate the worker
                'officer': dictionary value - dictionary of the saved information necessary to recreate the officer
        '''
        save_dict = super().to_save_dict()
        save_dict['worker'] = self.worker.to_save_dict()
        save_dict['officer'] = self.officer.to_save_dict()
        return(save_dict)

    def promote(self):
        '''
        Description:
            Promotes this group's officer to a veteran after performing various actions particularly well, improving the capabilities of groups the officer is attached to in the future. Creates a veteran star icon that follows this
                group and its officer
        Input:
            None
        Output:
            None
        '''
        self.veteran = True
        self.set_name("veteran " + self.name)
        self.officer.set_name("veteran " + self.officer.name)
        self.officer.veteran = True
        for current_grid in self.grids:
            if current_grid == self.global_manager.get('minimap_grid'):
                veteran_icon_x, veteran_icon_y = current_grid.get_mini_grid_coordinates(self.x, self.y)
            else:
                veteran_icon_x, veteran_icon_y = (self.x, self.y)
            input_dict = {}
            input_dict['coordinates'] = (veteran_icon_x, veteran_icon_y)
            input_dict['grid'] = current_grid
            input_dict['image'] = 'misc/veteran_icon.png'
            input_dict['name'] = 'veteran icon'
            input_dict['modes'] = ['strategic', 'europe']
            input_dict['show_terrain'] = False
            input_dict['actor'] = self 
            self.veteran_icons.append(veteran_icon(False, input_dict, self.global_manager))
        if self.global_manager.get('displayed_mob') == self:
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self) #updates actor info display with veteran icon

    def go_to_grid(self, new_grid, new_coordinates):
        '''
        Description:
            Links this group to a grid, causing it to appear on that grid and its minigrid at certain coordinates. Used when crossing the ocean and when a group that was previously attached to another actor becomes independent and
                visible, like when a group disembarks a ship. Also moves its officer and worker to the new grid
        Input:
            grid new_grid: grid that this group is linked to
            int tuple new_coordinates: Two values representing x and y coordinates to start at on the inputted grid
        Output:
            None
        '''
        if self.veteran:
            for current_veteran_icon in self.veteran_icons:
                current_veteran_icon.remove()
            self.veteran_icons = []
        super().go_to_grid(new_grid, new_coordinates)
        if self.veteran:
            for current_grid in self.grids:
                if current_grid == self.global_manager.get('minimap_grid'):
                    veteran_icon_x, veteran_icon_y = current_grid.get_mini_grid_coordinates(self.x, self.y)
                else:
                    veteran_icon_x, veteran_icon_y = (self.x, self.y)
                input_dict = {}
                input_dict['coordinates'] = (veteran_icon_x, veteran_icon_y)
                input_dict['grid'] = current_grid
                input_dict['image'] = 'misc/veteran_icon.png'
                input_dict['name'] = 'veteran icon'
                input_dict['modes'] = ['strategic', 'europe']
                input_dict['show_terrain'] = False
                input_dict['actor'] = self 
                self.veteran_icons.append(veteran_icon(False, input_dict, self.global_manager))
        self.officer.go_to_grid(new_grid, new_coordinates)
        self.officer.join_group() #hides images self.worker.hide_images()#
        self.worker.go_to_grid(new_grid, new_coordinates)
        self.worker.join_group() #self.worker.hide_images()#

    def update_tooltip(self): #to do: show carried commodities in tooltip
        '''
        Description:
            Sets this group's tooltip to what it should be whenever the player looks at the tooltip. By default, sets tooltip to this group's name, the names of its officer and worker, and its movement points
        Input:
            None
        Output:
            None
        '''
        self.set_tooltip(["Name: " + self.name.capitalize(), '    Officer: ' + self.officer.name.capitalize(), '    Worker: ' + self.worker.name.capitalize(),
            "Movement points: " + str(self.movement_points) + "/" + str(self.max_movement_points)])

    def disband(self):
        '''
        Description:
            Separates this group into its officer and worker, destroying the group
        Input:
            None
        Output:
            None
        '''
        if self.can_hold_commodities:
            self.drop_inventory()
        self.remove()
        self.worker.leave_group(self)
        self.worker.set_movement_points(self.movement_points)
        self.officer.veteran_icons = self.veteran_icons
        for current_veteran_icon in self.veteran_icons:
            current_veteran_icon.actor = self.officer
        self.officer.veteran = self.veteran
        self.officer.leave_group(self)
        self.officer.set_movement_points(self.movement_points)

    def remove(self):
        '''
        Description:
            Removes this object from relevant lists, prevents it from further appearing in or affecting the program, deselects it, and drops any commodities it is carrying. Used when the group is being disbanded, since it does not
                remove its worker or officer
        Input:
            None
        Output:
            None
        '''
        super().remove()
        self.global_manager.set('group_list', utility.remove_from_list(self.global_manager.get('group_list'), self))

    def die(self):
        '''
        Description:
            Removes this object from relevant lists, prevents it from further appearing in or affecting the program, deselects it, and drops any commodities it is carrying. Unlike remove, this is used when the group dies because it
                also removes its worker and officer
        Input:
            None
        Output:
            None
        '''
        self.remove()
        self.officer.remove()
        self.worker.remove()

    def start_construction(self, building_info_dict):
        '''
        Description
            Used when the player clicks on a construct building or train button, displays a choice notification that allows the player to construct it or not. Choosing to construct starts the construction process, costs an amount based
                on the building built, and consumes the caravan's movement points
        Input:
            dictionary building_info_dict: string keys corresponding to various values used to determine the building constructed
                string building_type: type of building, like 'resource'
                string building_name: name of building, like 'ivory camp'
                string attached_resource: optional, type of resource building produces, like 'ivory'
        Output:
            None
        '''
        self.building_type = building_info_dict['building_type']
        self.building_name = building_info_dict['building_name']
        if self.building_type == 'resource':
            self.attached_resource = building_info_dict['attached_resource']
        else:
            self.attached_resource = ''
        
        self.current_roll_modifier = 0
        self.current_min_success = self.default_min_success
        self.current_max_crit_fail = 0 #construction shouldn't have critical failures
        self.current_min_crit_success = self.default_min_crit_success
        
        self.current_min_success -= self.current_roll_modifier #positive modifier reduces number required for succcess, reduces maximum that can be crit fail
        self.current_max_crit_fail -= self.current_roll_modifier
        if self.current_min_success > self.current_min_crit_success:
            self.current_min_crit_success = self.current_min_success #if 6 is a failure, should not be critical success. However, if 6 is a success, it will always be a critical success
        choice_info_dict = {'constructor': self, 'type': 'start construction'}
        self.global_manager.set('ongoing_construction', True)
        message = "Are you sure you want to start constructing a " + self.building_name + "? /n /n"
        message += "The planning and materials will cost " + str(self.global_manager.get('building_prices')[self.building_type]) + " money. /n /n"
        message += "If successful, a " + self.building_name + " will be built. " #change to match each building
        if self.building_type == 'resource':
            message += "Each work crew attached to a " + self.building_name + " produces 1 unit of " + self.attached_resource + " each turn. "
            message += "It also expands the tile's warehouse capacity."
        elif self.building_type == 'infrastructure':
            if self.building_name == 'road':
                message += "A road halves movement cost when moving to another tile that has a road or railroad and can later be upgraded to a railroad."
            elif self.building_name == 'railroad':
                message += "A railroad, like a road, halves movement cost when moving to another tile that has a road or railroad. "
                message += "It is also required for trains to move and for a train station to be built."
        elif self.building_type == 'port':
            message += "A port allows ships to enter the tile. It also expands the tile's warehouse capacity. A port adjacent to the ocean can be used as a destination or starting point for ships traveling between theatres."
            if self.y == 1:
                message += "A port built here would be adjacent to the ocean."
            else:
                message += "A port built here would not be adjacent to the ocean."
        elif self.building_type == 'train_station':
            message += "A train station is required for a train to pick up or drop off cargo and passengers. It also expands the tile's warehouse capacity. A train can only be built at a train station."
        elif self.building_type == 'trading_post':
            message += "A trading post increases the likelihood that the natives of the local village will be willing to trade and reduces the risk of hostile interactions when trading."
        elif self.building_type == 'mission':
            message += "A mission decreases the difficulty of converting the natives of the local village and reduces the risk of hostile interactions when converting."
        elif self.building_type == 'train':
            message += "A train is a unit that can carry commodities and passengers at high speed along railroads. It can only exchange cargo at a train station and must stop moving for the rest of the turn after dropping off cargo. "
            message += "It also requires an attached worker as crew to function."
        else:
            message += "Placeholder building description"
        message += " /n /n"
            
        notification_tools.display_choice_notification(message, ['start construction', 'stop construction'], choice_info_dict, self.global_manager) #message, choices, choice_info_dict, global_manager

    def construct(self):
        '''
        Description:
            Controls the construction process, determining and displaying its result through a series of notifications
        Input:
            None
        Output:
            None
        '''
        roll_result = 0
        self.just_promoted = False
        self.set_movement_points(0)
        self.global_manager.get('money_tracker').change(-1 * self.global_manager.get('building_prices')[self.building_type])
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
        if roll_result >= self.current_min_success: #4+ required on D6 for exploration
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
            Used when the player finishes rolling for construction, shows the construction's results and making any changes caused by the result. If successful, the building is constructed, promotes engineer to a veteran on critical
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
        self.global_manager.set('ongoing_construction', False)

    def display_die(self, coordinates, result, min_success, min_crit_success, max_crit_fail):
        '''
        Description:
            Creates a die object at the inputted location and predetermined roll result to use for multi-step notification dice rolls. The color of the die's outline depends on the result
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

class porters(group):
    '''
    A group with a driver officer that can hold commodities
    '''
    def __init__(self, from_save, input_dict, global_manager):
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
                'end_turn_destination_grid_type': string value - Required if end_turn_destination is not 'none', matches the global manager key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - Required if from save, how many movement points this actor currently has
                'worker': worker or dictionary value - If creating a new group, equals a worker that is part of this group. If loading, equals a dictionary of the saved information necessary to recreate the worker
                'officer': worker or dictionary value - If creating a new group, equals an officer that is part of this group. If loading, equals a dictionary of the saved information necessary to recreate the officer
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(from_save, input_dict, global_manager)
        self.can_hold_commodities = True
        self.inventory_capacity = 9
        self.set_group_type('porters')
        if not from_save:
            self.inventory_setup()
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self) #updates mob info display list to account for inventory capacity changing
        else:
            self.load_inventory(input_dict['inventory'])

class construction_gang(group):
    '''
    A group with an engineer officer that is able to construct buildings and trains
    '''
    def __init__(self, from_save, input_dict, global_manager):
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
                'end_turn_destination_grid_type': string value - Required if end_turn_destination is not 'none', matches the global manager key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - Required if from save, how many movement points this actor currently has
                'worker': worker or dictionary value - If creating a new group, equals a worker that is part of this group. If loading, equals a dictionary of the saved information necessary to recreate the worker
                'officer': worker or dictionary value - If creating a new group, equals an officer that is part of this group. If loading, equals a dictionary of the saved information necessary to recreate the officer
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(from_save, input_dict, global_manager)
        self.can_construct = True
        self.set_group_type('construction_gang')
        if not from_save:
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self) #updates mob info display list to account for can_construct changing

class caravan(group):
    '''
    A group with a merchant officer that is able to establish trading posts and trade with native villages
    '''
    def __init__(self, from_save, input_dict, global_manager):
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
                'end_turn_destination_grid_type': string value - Required if end_turn_destination is not 'none', matches the global manager key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - Required if from save, how many movement points this actor currently has
                'worker': worker or dictionary value - If creating a new group, equals a worker that is part of this group. If loading, equals a dictionary of the saved information necessary to recreate the worker
                'officer': worker or dictionary value - If creating a new group, equals an officer that is part of this group. If loading, equals a dictionary of the saved information necessary to recreate the officer
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(from_save, input_dict, global_manager)
        self.can_hold_commodities = True
        self.can_trade = True
        self.inventory_capacity = 9
        self.trades_remaining = 0
        self.set_group_type('caravan')
        if not from_save:
            self.inventory_setup()
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self) #updates mob info display list to account for inventory capacity changing
        else:
            self.load_inventory(input_dict['inventory'])

    def start_trade(self):
        '''
        Description:
            Used when the player clicks on the trade button, displays a choice notification that allows the player to trade or not. Choosing to trade starts the trading process and
                consumes the caravan's movement points
        Input:
            None
        Output:
            None
        '''
        village = self.images[0].current_cell.village
        choice_info_dict = {'caravan': self, 'village': village, 'type': 'start trading'}
        self.global_manager.set('ongoing_trade', True)
        message = "Are you sure you want to attempt to trade with the village of " + village.name + "? /n /n"

        self.current_roll_modifier = 0
        self.current_min_success = self.default_min_success
        self.current_max_crit_fail = self.default_max_crit_fail
        self.current_min_crit_success = self.default_min_crit_success

        if village.cell.contained_buildings['trading_post'] == 'none': #penalty for no trading post
            self.current_roll_modifier -= 1
            message += "Without an established trading post, the merchant will have difficulty convincing villagers to trade. /n /n"
        
        aggressiveness_modifier = village.get_aggressiveness_modifier()
        if aggressiveness_modifier < 0:
            message += "The villagers are hostile and are unlikely to be willing to trade. /n /n"
        elif aggressiveness_modifier > 0:
            message += "The villagers are friendly and are likely to be willing to trade. /n /n"
        else:
            message += "The villagers are wary of the merchant but may be willing to trade. /n /n"
        self.current_roll_modifier += aggressiveness_modifier

        risk_value = -1 * self.current_roll_modifier #modifier of -1 means risk value of 1
        if self.veteran: #reduce risk if veteran
            risk_value -= 1

        if risk_value < 0: #0/6 = no risk
            message = "RISK: LOW /n /n" + message  
        elif risk_value == 0: #1/6 death = moderate risk
            message = "RISK: MODERATE /n /n" + message #puts risk message at beginning
        elif risk_value == 1: #2/6 = high risk
            message = "RISK: HIGH /n /n" + message
        elif risk_value > 1: #3/6 or higher = extremely high risk
            message = "RISK: DEADLY /n /n" + message
        
        self.current_min_success -= self.current_roll_modifier #positive modifier reduces number required for succcess, reduces maximum that can be crit fail
        self.current_max_crit_fail -= self.current_roll_modifier
        if self.current_min_success > self.current_min_crit_success:
            self.current_min_crit_success = self.current_min_success #if 6 is a failure, should not be critical success. However, if 6 is a success, it will always be a critical success
        message += "In each trade, the merchant trades 1 of his " + str(self.get_inventory('consumer goods')) + " consumer goods for items that may or may not be valuable. /n /n"
        message += "Trading may also convince villagers to become available for hire as workers. "
        notification_tools.display_choice_notification(message, ['start trading', 'stop trading'], choice_info_dict, self.global_manager) #message, choices, choice_info_dict, global_manager

    def willing_to_trade(self, notification):
        '''
        Description:
            Used when the player decides to start trading, allows the player to roll a die to see if the villagers are willing to trade. If they are willing to trade, displays a choice notification that allows the player to start the
                transaction process or not. Otherwise, stops the trading process
        Input:
            notification notification: the current trade notification, used to access information relating to the trade such as which village is being traded with
        Output:
            None
        '''
        self.notification = notification
        self.set_movement_points(0)
        village = self.notification.choice_info_dict['village']
        text = ("The merchant attempts to convince the villagers to trade. /n /n")
        if self.veteran:
            text += ("The veteran merchant can roll twice and pick the higher result. /n /n")
            notification_tools.display_notification(text + "Click to roll. " + str(self.current_min_success) + "+ required on at least 1 die to succeed.", 'trade', self.global_manager)
        else:
            notification_tools.display_notification(text + "Click to roll. " + str(self.current_min_success) + "+ required to succeed.", 'trade', self.global_manager)
        notification_tools.display_notification(text + "Rolling... ", 'roll', self.global_manager)

        die_x = self.global_manager.get('notification_manager').notification_x - 140

        roll_result = 0
        if self.veteran:
            results = self.controlling_minister.roll_to_list(6, self.current_min_success, self.current_max_crit_fail, 2)
            
            #result = self.controlling_minister.roll(6, self.current_min_success, self.current_max_crit_fail)
            first_roll_list = dice_utility.roll_to_list(6, "Trade roll", self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, results[0]) #0 requirement for critical fail means critical fails will not occur
            self.display_die((die_x, 500), first_roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)

            #result = self.controlling_minister.roll(6, self.current_min_success, self.current_max_crit_fail)         
            second_roll_list = dice_utility.roll_to_list(6, "second", self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, results[1]) #0 requirement for critical fail means critical fails will not occur
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
            roll_list = dice_utility.roll_to_list(6, "Trade roll", self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, result) #0 requirement for critical fail means critical fails will not occur
            self.display_die((die_x, 440), roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)
                            
            text += roll_list[1]
            roll_result = roll_list[0]

        self.global_manager.set('trade_result', [self, roll_result])
        notification_tools.display_notification(text + "Click to continue.", 'final_trade', self.global_manager)

        if roll_result >= self.current_min_success:
            self.trades_remaining = math.ceil(village.population / 3)
            trade_type = 'trade'
            if (not self.veteran) and roll_result >= self.current_min_crit_success: #promotion occurs when trade_promotion notification appears, in notification_to_front in notification_manager
                text += "/nThe merchant negotiated well enough to become a veteran. /n"
                trade_type = 'trade_promotion'
            notification_tools.display_notification(text + "/nThe villagers are willing to trade " + str(self.trades_remaining) + " times. /n /nThe merchant has " + str(self.get_inventory('consumer goods')) +
                " consumer goods to sell. /n /nClick to start trading. /n /n", trade_type, self.global_manager)
            choice_info_dict = {'caravan': self, 'village': village, 'type': 'willing to trade'}
            text += "/nThe villagers are willing to trade " + str(self.trades_remaining) + " times. /n /n"
            text += "The merchant has " + str(self.get_inventory('consumer goods')) + " consumer goods to sell. /n /n"
            text += "Do you want to start trading consumer goods for items that may or may not be valuable?"
            notification_tools.display_choice_notification(text, ['trade', 'stop trading'], choice_info_dict, self.global_manager) #message, choices, choice_info_dict, global_manager
        else:
            text += "/nThe villagers are not willing to trade. /n"
            if roll_result <= self.current_max_crit_fail:
                text += " /nBelieving that the merchant seeks to trick them out of their valuables, the villagers attack the caravan. /n"
                text += " /nEveryone in the caravan has died "
                if not village.cell.contained_buildings['trading_post'] == 'none':
                    text += "and the trading post has been destroyed"
                text += ". /n"
                notification_tools.display_notification(text + " /nClick to close this notification. ", 'stop_trade_attacked', self.global_manager)
            else:
                notification_tools.display_notification(text + " /nClick to close this notification. ", 'stop_trade', self.global_manager)

    def trade(self, notification):
        '''
        Description:
            Used in each part of the transaction process, allows the player to sell a unit of consumer goods and roll a die to try to find commodities in return. After the transaction, if the villagers are able to trade more and the
                caravan has more consumer goods to sell, displays a choice notification that allows the player to start another transaction or not. Otherwise, stops the trading process
        Input:
            notification notification: the current trade notification, used to access information relating to the trade such as which village is being traded with
        Output:
            None
        '''
        self.current_roll_modifier = 0 #trading - getting good deals - is different from the willingness to trade roll and uses different modifiers
        self.current_min_success = 4
        self.current_max_crit_fail = 0 #0 requirement for critical fail means critical fails will not occur
        self.current_min_crit_success = 7 #no critical successes
        
        self.current_min_success -= self.current_roll_modifier #positive modifier reduces number required for succcess, reduces maximum that can be crit fail
        self.current_max_crit_fail -= self.current_roll_modifier
        if self.current_min_success > self.current_min_crit_success:
            self.current_min_crit_success = self.current_min_success #if 6 is a failure, should not be critical success. However, if 6 is a success, it will always be a critical success
        
        self.notification = notification
        village = self.notification.choice_info_dict['village']
        text = ("The merchant attempts to find valuable commodities in return for consumer goods. /n /n")
        if self.veteran:
            text += ("The veteran merchant can roll twice and pick the higher result. /n /n")
            notification_tools.display_notification(text + "Click to roll. " + str(self.current_min_success) + "+ required on at least 1 die to succeed.", 'trade', self.global_manager)
        else:
            notification_tools.display_notification(text + "Click to roll. " + str(self.current_min_success) + "+ required to succeed.", 'trade', self.global_manager)
        notification_tools.display_notification(text + "Rolling... ", 'roll', self.global_manager)

        die_x = self.global_manager.get('notification_manager').notification_x - 140

        roll_result = 0
        if self.veteran:
            results = self.controlling_minister.roll_to_list(6, self.current_min_success, self.current_max_crit_fail, 2)
            first_roll_list = dice_utility.roll_to_list(6, "Trade roll", self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, results[0])
            self.display_die((die_x, 500), first_roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)
    
            second_roll_list = dice_utility.roll_to_list(6, "second", self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, results[1]) #7 requirement for crit success - can't promote from trade deal, only willingness to trade roll
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
            roll_list = dice_utility.roll_to_list(6, "Trade roll", self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, result) #0 requirement for critical fail means critical fails will not occur
            self.display_die((die_x, 440), roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)
                            
            text += roll_list[1]
            roll_result = roll_list[0]
                
        notification_tools.display_notification(text + "Click to continue.", 'final_trade', self.global_manager)
        self.trades_remaining -= 1
        num_consumer_goods = self.get_inventory('consumer goods') - 1 #consumer goods are actually lost when clicking out of notification, so subtract 1 here to show accurate number
        commodity = 'none'
        notification_type = 'none'
        if roll_result >= self.current_min_success:
            commodity = random.choice(self.global_manager.get('collectable_resources'))
            text += "/n The merchant managed to buy a unit of " + commodity + ". /n /n"
            notification_type = 'successful_commodity_trade'
        else:
            text += "/n The merchant bought items that turned out to be worthless. /n /n"
            notification_type = 'failed_commodity_trade'
        if not self.trades_remaining == 0:
            text += "The villagers are willing to trade " + str(self.trades_remaining) + " more times /n /n"
            text += "The merchant has " + str(num_consumer_goods) + " more consumer goods to sell /n /n"
        notification_tools.display_notification(text, notification_type, self.global_manager)
        text = ""
        if self.trades_remaining > 0 and num_consumer_goods > 0:
            choice_info_dict = {'caravan': self, 'village': village, 'type': 'trade'}
            text += "The villagers are willing to trade " + str(self.trades_remaining) + " more times /n /n"
            text += "Do you want to trade consumer goods for items that may or may not be valuable?"
            notification_tools.display_choice_notification(text, ['trade', 'stop trading'], choice_info_dict, self.global_manager) #message, choices, choice_info_dict, global_manager
        else:
            if self.trades_remaining == 0:
                text += "The villagers are not willing to trade any more this turn. /n /n"
            if num_consumer_goods <= 0: #consumer goods are actually lost when user clicks out of
                text += "The merchant does not have any more consumer goods to sell. /n /n"
            notification_tools.display_notification(text + "Click to close this notification. ", 'stop_trade', self.global_manager)
        self.global_manager.set('trade_result', [self, roll_result, commodity]) #allows notification to give random commodity when clicked

class missionaries(group):
    '''
    A group with an evangelist officer and church volunteer workers that can build churches and convert native villages
    '''
    def __init__(self, from_save, input_dict, global_manager):
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
                'end_turn_destination_grid_type': string value - Required if end_turn_destination is not 'none', matches the global manager key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - Required if from save, how many movement points this actor currently has
                'worker': worker or dictionary value - If creating a new group, equals a worker that is part of this group. If loading, equals a dictionary of the saved information necessary to recreate the worker
                'officer': worker or dictionary value - If creating a new group, equals an officer that is part of this group. If loading, equals a dictionary of the saved information necessary to recreate the officer
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(from_save, input_dict, global_manager)
        self.can_convert = True
        self.set_group_type('missionaries')
        if not from_save:
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self) #updates mob info display list to account for new missionary actions

    def start_converting(self):
        '''
        Description:
            Used when the player clicks on the start converting button, displays a choice notification that allows the player to caonvert or not. Choosing to campaign starts the conversion process and consumes the missionaries'
                movement points
        Input:
            None
        Output:
            None
        '''
        village = self.images[0].current_cell.village
        self.current_roll_modifier = 0
        self.current_min_success = self.default_min_success
        self.current_max_crit_fail = self.default_max_crit_fail
        self.current_min_crit_success = self.default_min_crit_success
        message = "Are you sure you want to attempt to convert the natives? If successful, the natives will be less aggressive and easier to cooperate with. /n /n"
                            
        if village.cell.contained_buildings['mission'] == 'none': #penalty for no mission
            self.current_roll_modifier -= 1
            message += "Without an established mission, the missionaries will have difficulty converting the villagers. /n /n"
            
        aggressiveness_modifier = village.get_aggressiveness_modifier()
        if aggressiveness_modifier < 0:
            message += "The villagers are hostile and are unlikely to listen to the teachings of the missionaries. /n /n"
        elif aggressiveness_modifier > 0:
            message += "The villagers are friendly and are likely to listen to the teachings of the missionaries. /n /n"
        else:
            message += "The villagers are wary of the missionaries but may be willing to listen to their teachings. /n /n"
        self.current_roll_modifier += aggressiveness_modifier

        population_modifier = village.get_population_modifier()
        if population_modifier < 0:
            message += "The high population of this village will require more effort to convert. /n"
        elif population_modifier > 0:
            message += "The low population of this village will require less effort to convert /n"
        self.current_roll_modifier += population_modifier

        risk_value = -1 * self.current_roll_modifier #modifier of -1 means risk value of 1
        if self.veteran: #reduce risk if veteran
            risk_value -= 1

        if risk_value < 0: #0/6 = no risk
            message = "RISK: LOW /n /n" + message  
        elif risk_value == 0: #1/6 death = moderate risk
            message = "RISK: MODERATE /n /n" + message #puts risk message at beginning
        elif risk_value == 1: #2/6 = high risk
            message = "RISK: HIGH /n /n" + message
        elif risk_value > 1: #3/6 or higher = extremely high risk
            message = "RISK: DEADLY /n /n" + message
            
        self.current_min_success -= self.current_roll_modifier #positive modifier reduces number required for succcess, reduces maximum that can be crit fail
        self.current_max_crit_fail -= self.current_roll_modifier
        if self.current_min_success > self.current_min_crit_success:
            self.current_min_crit_success = self.current_min_success #if 6 is a failure, should not be critical success. However, if 6 is a success, it will always be a critical success
        
        choice_info_dict = {'evanglist': self,'type': 'start converting'}
        self.current_roll_modifier = 0
        self.global_manager.set('ongoing_conversion', True)
        notification_tools.display_choice_notification(message, ['start converting', 'stop converting'], choice_info_dict, self.global_manager) #message, choices, choice_info_dict, global_manager+

    def convert(self):
        '''
        Description:
            Controls the conversion process, determining and displaying its result through a series of notifications
        Input:
            None
        Output:
            None
        '''
        roll_result = 0
        self.just_promoted = False
        self.set_movement_points(0)
        village = self.images[0].current_cell.village
        text = ""
        text += "The missionaries try to convert the natives to reduce their aggressiveness. /n /n"

        if not self.veteran:    
            notification_tools.display_notification(text + "Click to roll. " + str(self.current_min_success) + "+ required to succeed.", 'convert', self.global_manager)
        else:
            text += ("The veteran evangelist can roll twice and pick the higher result. /n /n")
            notification_tools.display_notification(text + "Click to roll. " + str(self.current_min_success) + "+ required on at least 1 die to succeed.", 'convert', self.global_manager)

        notification_tools.display_notification(text + "Rolling... ", 'roll', self.global_manager)

        die_x = self.global_manager.get('notification_manager').notification_x - 140

        if self.veteran:
            results = self.controlling_minister.roll_to_list(6, self.current_min_success, self.current_max_crit_fail, 2)
            first_roll_list = dice_utility.roll_to_list(6, "Conversion roll", self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, results[0])
            self.display_die((die_x, 500), first_roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)
           
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
            roll_list = dice_utility.roll_to_list(6, "Conversion roll", self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, result)
            self.display_die((die_x, 440), roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)
                
            text += roll_list[1]
            roll_result = roll_list[0]

        notification_tools.display_notification(text + "Click to continue.", 'conversion', self.global_manager)
            
        text += "/n"
        if roll_result >= self.current_min_success: #4+ required on D6 for exploration
            text += "The missionaries have made progress in converting the natives and have reduced their aggressiveness from " + str(village.aggressiveness) + " to " + str(village.aggressiveness - 1) + ". /n /n"
        else:
            text += "The missionaries made little progress in converting the natives. /n /n"
        if roll_result <= self.current_max_crit_fail:
            text += "Angered by the missionaries' attempts to destroy their spiritual traditions, the natives attack the missionaries. The entire group of missionaries has died "
            if not village.cell.contained_buildings['mission'] == 'none':
                text += "and the mission building has been destroyed."
            text += ". /n"

        if (not self.veteran) and roll_result >= self.current_min_crit_success:
            self.just_promoted = True
            text += " /nThe evangelist has gained insights into converting natives and demonstrating connections between their beliefs and Christianity. /n"
            text += " /nThe evangelist is now a veteran and will be more successful in future ventures. /n"
        if roll_result >= self.current_min_success:
            notification_tools.display_notification(text + "/nClick to remove this notification.", 'final_conversion', self.global_manager)
        else:
            notification_tools.display_notification(text, 'default', self.global_manager)
        self.global_manager.set('conversion_result', [self, roll_result, village])

    def complete_conversion(self):
        '''
        Description:
            Used when the player finishes rolling for religious conversion, shows the conversion's results and making any changes caused by the result. If successful, reduces village aggressiveness, promotes evangelist to a veteran on
                critical success. Missionaries die on critical failure
        Input:
            None
        Output:
            None
        '''
        roll_result = self.global_manager.get('conversion_result')[1]
        village = self.global_manager.get('conversion_result')[2]
        if roll_result >= self.current_min_success: #if campaign succeeded
            village.change_aggressiveness(-1)
            if roll_result >= self.current_min_crit_success and not self.veteran:
                self.promote()
        if roll_result <= self.current_max_crit_fail:
            self.die()
            if not village.cell.contained_buildings['mission'] == 'none':
                village.cell.contained_buildings['mission'].remove()
        self.global_manager.set('ongoing_conversion', False)

class expedition(group):
    '''
    A group with an explorer officer that is able to explore
    '''
    def __init__(self, from_save, input_dict, global_manager):
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
                'end_turn_destination_grid_type': string value - Required if end_turn_destination is not 'none', matches the global manager key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - Required if from save, how many movement points this actor currently has
                'worker': worker or dictionary value - If creating a new group, equals a worker that is part of this group. If loading, equals a dictionary of the saved information necessary to recreate the worker
                'officer': worker or dictionary value - If creating a new group, equals an officer that is part of this group. If loading, equals a dictionary of the saved information necessary to recreate the officer
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(from_save, input_dict, global_manager)
        self.exploration_mark_list = []
        self.exploration_cost = 2
        self.can_explore = True
        self.set_group_type('expedition')

    def move(self, x_change, y_change):
        '''
        Description:
            Moves this mob x_change to the right and y_change upward. Moving to a ship in the water automatically embarks the ship. Also allows exploration when moving into unexplored areas. Attempting an exploration starts the
                exploration process, which requires various dice rolls to succeed and can also result in the death of the expedition or the promotion of its explorer. A successful exploration uncovers the area and units to move into it
                normally in the future
        Input:
            int x_change: How many cells are moved to the right in the movement
            int y_change: How many cells are moved upward in the movement
        Output:
            None
        '''
        self.global_manager.set('show_selection_outlines', True)
        self.global_manager.set('show_minimap_outlines', True)
        self.global_manager.set('last_selection_outline_switch', time.time())#outlines should be shown immediately when selected
        self.global_manager.set('last_minimap_outline_switch', time.time())
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
            if self.global_manager.get('money_tracker').get() >= self.exploration_cost:
                if self.check_if_minister_appointed():
                    choice_info_dict = {'expedition': self, 'x_change': x_change, 'y_change': y_change, 'cost': self.exploration_cost, 'type': 'exploration'}
                    
                    self.current_roll_modifier = 0
                    self.current_min_success = self.default_min_success
                    self.current_max_crit_fail = self.default_max_crit_fail
                    self.current_min_crit_success = self.default_min_crit_success
                    
                    self.current_min_success -= self.current_roll_modifier #positive modifier reduces number required for succcess, reduces maximum that can be crit fail
                    self.current_max_crit_fail -= self.current_roll_modifier
                    if self.current_min_success > self.current_min_crit_success:
                        self.current_min_crit_success = self.current_min_success #if 6 is a failure, should not be critical success. However, if 6 is a success, it will always be a critical success
                    message = ""

                    risk_value = -1 * self.current_roll_modifier #modifier of -1 means risk value of 1
                    if self.veteran: #reduce risk if veteran
                        risk_value -= 1

                    if risk_value < 0: #0/6 = no risk
                        message = "RISK: LOW /n /n" + message  
                    elif risk_value == 0: #1/6 death = moderate risk
                        message = "RISK: MODERATE /n /n" + message #puts risk message at beginning
                    elif risk_value == 1: #2/6 = high risk
                        message = "RISK: HIGH /n /n" + message
                    elif risk_value > 1: #3/6 or higher = extremely high risk
                        message = "RISK: DEADLY /n /n" + message
                    
                    notification_tools.display_choice_notification(message + "Are you sure you want to spend " + str(choice_info_dict['cost']) + " money to attempt an exploration to the " + direction + "?", ['exploration', 'stop exploration'],
                        choice_info_dict, self.global_manager) #message, choices, choice_info_dict, global_manager
                    self.global_manager.set('ongoing_exploration', True)
                    for current_grid in self.grids:
                        coordinates = (0, 0)
                        if current_grid.is_mini_grid:
                            coordinates = current_grid.get_mini_grid_coordinates(self.x + x_change, self.y + y_change)
                        else:
                            coordinates = (self.x + x_change, self.y + y_change)
                        input_dict = {}
                        input_dict['coordinates'] = coordinates
                        input_dict['grid'] = current_grid
                        input_dict['image'] = 'misc/exploration_x/' + direction + '_x.png'
                        input_dict['name'] = 'exploration mark'
                        input_dict['modes'] = ['strategic']
                        input_dict['show_terrain'] = False
                        self.global_manager.get('exploration_mark_list').append(tile(False, input_dict, self.global_manager))
            else:
                text_tools.print_to_screen("You do not have enough money to attempt an exploration.", self.global_manager)
        else: #if moving to explored area, move normally
            super().move(x_change, y_change)

    def start_exploration(self, x_change, y_change):
        '''
        Description:
            Used when the player issues a move order into an unexplored area with an expedition, displays a choice notification that allows the player to explore or not. Choosing to explore starts the exploration process. This function
                also determines the expedition's result, but the results are only shown to the player after a dice roll and the complete_exploration function
        Input:
            None
        Output:
            None
        '''
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
        
        self.just_promoted = False
        text = ""
        text += "The expedition heads towards the " + direction + ". /n /n"
        text += (self.global_manager.get('flavor_text_manager').generate_flavor_text('explorer') + " /n /n")
        
        if not self.veteran:    
            notification_tools.display_notification(text + "Click to roll. " + str(self.current_min_success) + "+ required to succeed.", 'exploration', self.global_manager)
        else:
            text += ("The veteran explorer can roll twice and pick the higher result. /n /n")
            notification_tools.display_notification(text + "Click to roll. " + str(self.current_min_success) + "+ required on at least 1 die to succeed.", 'exploration', self.global_manager)

        notification_tools.display_notification(text + "Rolling... ", 'roll', self.global_manager)

        die_x = self.global_manager.get('notification_manager').notification_x - 140

        if self.veteran:
            results = self.controlling_minister.roll_to_list(6, self.current_min_success, self.current_max_crit_fail, 2)
            first_roll_list = dice_utility.roll_to_list(6, "Exploration roll", self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, results[0])
            self.display_die((die_x, 500), first_roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)

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
            roll_list = dice_utility.roll_to_list(6, "Exploration roll", self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, result)
            self.display_die((die_x, 440), roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)
                
            text += roll_list[1]
            roll_result = roll_list[0]

        notification_tools.display_notification(text + "Click to continue.", 'exploration', self.global_manager)
            
        text += "/n"
        if roll_result >= self.current_min_success: #4+ required on D6 for exploration by default
            if not future_cell.resource == 'none':
                text += "You discovered a " + future_cell.terrain.upper() + " tile with a " + future_cell.resource.upper() + " resource. /n"
            else:
                text += "You discovered a " + future_cell.terrain.upper() + " tile. /n"
        else:
            text += "You were not able to explore the tile. /n"
        if roll_result <= self.current_max_crit_fail:
            text += "Everyone in the expedition has died. /n" #actual death occurs when exploration completes

        if (not self.veteran) and roll_result >= self.current_min_crit_success:
            self.veteran = True
            self.just_promoted = True
            text += "This explorer is now a veteran. /n"
        if roll_result >= self.current_min_success:
            self.destination_cell = future_cell
            notification_tools.display_notification(text + "Click to remove this notification.", 'final_exploration', self.global_manager)
        else:
            notification_tools.display_notification(text, 'default', self.global_manager)
        self.global_manager.set('exploration_result', [self, roll_result, x_change, y_change])

    def complete_exploration(self): #roll_result, x_change, y_change
        '''
        Description:
            Used when the player finishes rolling for an exploration, shows the exploration's results and making any changes caused by the result. If successful, the expedition moves into the explored area, consumes its movement
                points, promotes its explorer to a veteran on critical success. If not successful, the expedition consumes its movement points and dies on critical failure
        Input:
            None
        Output:
            None
        '''
        exploration_result = self.global_manager.get('exploration_result')
        roll_result = exploration_result[1]
        x_change = exploration_result[2]
        y_change = exploration_result[3]
        future_cell = self.grid.find_cell(x_change + self.x, y_change + self.y)
        died = False
        if roll_result >= self.current_min_success:
            future_cell.set_visibility(True)
            if not future_cell.terrain == 'water':
                super().move(x_change, y_change)
            else: #if discovered a water tile, update minimap but don't move there
                self.global_manager.get('minimap_grid').calibrate(self.x, self.y)
                self.change_movement_points(-1 * self.get_movement_cost(x_change, y_change)) #when exploring, movement points should be consumed regardless of exploration success or destination
        else:
            self.change_movement_points(-1 * self.get_movement_cost(x_change, y_change)) #when exploring, movement points should be consumed regardless of exploration success or destination
        if self.just_promoted:
            self.promote()
        elif roll_result <= self.current_max_crit_fail:
            self.die()
            died = True
        copy_dice_list = self.global_manager.get('dice_list')
        for current_die in copy_dice_list:
            current_die.remove()
        actor_utility.stop_exploration(self.global_manager) #make function that sets ongoing exploration to false and destroys exploration marks
