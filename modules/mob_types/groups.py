#Contains functionality for group units

from ..mobs import mob
from ..tiles import veteran_icon
from .. import actor_utility
from .. import dice_utility
from .. import utility
from .. import notification_tools
from .. import dice
from .. import images
from .. import scaling

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

    def fire(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program. Also fires this group's worker and officer
        Input:
            None
        Output:
            None
        '''
        #super().fire()
        #self.officer.fire()
        #self.worker.fire()
        self.officer.fire()
        self.worker.fire()
        self.remove()

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
        super().die()
        self.officer.die()
        self.worker.die()

    def start_construction(self, building_info_dict):
        '''
        Description
            Used when the player clicks on a construct building or train button, displays a choice notification that allows the player to construct it or not. Choosing to construct starts the construction process, costs an amount based
                on the building built, and consumes the group's movement points
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
        minister_icon_coordinates = (coordinates[0], coordinates[1] + 120)
        minister_position_icon = images.dice_roll_minister_image(minister_icon_coordinates, scaling.scale_width(100, self.global_manager), scaling.scale_height(100, self.global_manager), self.modes, self.controlling_minister,
            'position', self.global_manager)
        minister_portrait_icon = images.dice_roll_minister_image(minister_icon_coordinates, scaling.scale_width(100, self.global_manager), scaling.scale_height(100, self.global_manager), self.modes, self.controlling_minister,
            'portrait', self.global_manager)
