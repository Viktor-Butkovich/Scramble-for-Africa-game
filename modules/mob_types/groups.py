#Contains functionality for group units

from .pmobs import pmob
from ..tiles import veteran_icon
from .. import actor_utility
from .. import dice_utility
from .. import utility
from .. import notification_tools
from .. import images
from .. import scaling

class group(pmob):
    '''
    pmob that is created by a combination of a worker and officer, has special capabilities depending on its officer, and separates its worker and officer upon being disbanded
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
        self.just_promoted = False
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
