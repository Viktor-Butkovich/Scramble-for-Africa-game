#Contains functionality for group units

import random
import math
from .pmobs import pmob
from ...util import actor_utility

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
                'image': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'name': string value - Required if from save, this group's name
                'modes': string list value - Game modes during which this group's images can appear
                'end_turn_destination': string or int tuple value - Required if from save, 'none' if no saved destination, destination coordinates if saved destination
                'end_turn_destination_grid_type': string value - Required if end_turn_destination is not 'none', matches the global manager key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - Required if from save, how many movement points this actor currently has
                'max_movement_points': int value - Required if from save, maximum number of movement points this mob can have
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
        self.group_type = 'none'
        super().__init__(from_save, input_dict, global_manager)
        self.worker.join_group()
        self.officer.join_group()
        self.is_group = True
        for current_commodity in self.global_manager.get('commodity_types'): #merges individual inventory to group inventory and clears individual inventory
            self.change_inventory(current_commodity, self.worker.get_inventory(current_commodity))
            self.change_inventory(current_commodity, self.officer.get_inventory(current_commodity))
        self.worker.inventory_setup()
        self.officer.inventory_setup()
        self.set_group_type('none')
        self.update_image_bundle()
        if not from_save:
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display'), 'none', override_exempt=True)
            self.select()
        if self.officer.veteran:
            self.promote()
        if not from_save:
            self.status_icons = self.officer.status_icons
            for current_status_icon in self.status_icons:
                current_status_icon.actor = self
            self.set_movement_points(actor_utility.generate_group_movement_points(self.worker, self.officer, global_manager))

    def replace_worker(self, new_worker_type):
        '''
        Description:
            Fires this group's current worker and replaces it with a worker of the inputted type, affecting worker upkeep prices and public opinion as usual
        Input:
            string new_worker_type: New type of worker to create
        Output:
            None
        '''
        input_dict = {
            'coordinates': (self.x, self.y),
            'grids': self.grids,
            'modes': self.modes
        }

        if new_worker_type == 'European':
            input_dict['image'] = 'mobs/European workers/default.png'
            input_dict['name'] = 'European workers'
            input_dict['init_type'] = 'workers'
            input_dict['worker_type'] = 'European'
        elif new_worker_type == 'African':
            input_dict['image'] = 'mobs/African workers/default.png'
            input_dict['name'] = 'African workers'
            input_dict['init_type'] = 'workers'
            input_dict['worker_type'] = 'African'
        elif new_worker_type == 'slaves':
            self.global_manager.get('money_tracker').change(-1 * self.cost, 'unit_recruitment')
            input_dict['image'] = 'mobs/slave workers/default.png'
            input_dict['name'] = 'slave workers'
            input_dict['init_type'] = 'slaves'
            input_dict['purchased'] = False
        previous_selected = self.global_manager.get('displayed_mob')#self.selected
        new_worker = self.global_manager.get('actor_creation_manager').create(False, input_dict, self.global_manager)
        new_worker.set_automatically_replace(self.worker.automatically_replace)
        self.worker.fire(wander = False)
        self.worker = new_worker
        self.worker.update_image_bundle()
        self.worker.join_group()
        self.update_image_bundle()
        if previous_selected == self:
            self.select()
        elif previous_selected != 'none':
            previous_selected.select()
        else:
            actor_utility.deselect_all(self.global_manager)

        if self.images[0].current_cell != 'none' and self.global_manager.get('displayed_tile') == self.images[0].current_cell.tile:
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display'), self.images[0].current_cell.tile)

    def move(self, x_change, y_change):
        '''
        Description:
            Moves this mob x_change to the right and y_change upward, also making sure to update the positions of the group's worker and officer
        Input:
            int x_change: How many cells are moved to the right in the movement
            int y_change: How many cells are moved upward in the movement
        Output:
            None
        '''
        super().move(x_change, y_change)
        self.calibrate_sub_mob_positions()

    def calibrate_sub_mob_positions(self):
        '''
        Description:
            Updates the positions of this mob's submobs (mobs inside of a building or other mob that are not able to be independently viewed or selected) to match this mob
        Input:
            None
        Output:
            None
        '''
        self.officer.x = self.x
        self.officer.y = self.y
        self.worker.x = self.x
        self.worker.y = self.y

    def manage_health_attrition(self, current_cell = 'default'):
        '''
        Description:
            Checks this mob for health attrition each turn. A group's worker and officer each roll for attrition independently, but the group itself cannot suffer attrition
        Input:
            string/cell current_cell = 'default': Records which cell the attrition is taking place in, used when a unit is in a building or another mob and does not technically exist in any cell
        Output:
            None
        '''
        if current_cell == 'default':
            current_cell = self.images[0].current_cell
        if current_cell == 'none':
            return()

        transportation_minister = self.global_manager.get('current_ministers')[self.global_manager.get('type_minister_dict')['transportation']]
    
        if current_cell.local_attrition():
            if transportation_minister.no_corruption_roll(6, 'health_attrition') == 1 or self.global_manager.get('effect_manager').effect_active('boost_attrition'):
                self.attrition_death('officer')
        if current_cell.local_attrition():
            if transportation_minister.no_corruption_roll(6, 'health_attrition') == 1 or self.global_manager.get('effect_manager').effect_active('boost_attrition'):
                worker_type = self.worker.worker_type
                if (not worker_type in ['African', 'slave']) or random.randrange(1, 7) == 1:
                    self.attrition_death('worker')

    def attrition_death(self, target):
        '''
        Description:
            Resolves either the group's worker or officer dying from attrition, preventing the group from moving in the next turn and automatically recruiting a new one
        Input:
            None
        Output:
            None
        '''
        self.global_manager.get('evil_tracker').change(3)
        self.temp_disable_movement()
        if self.in_vehicle:
            zoom_destination = self.vehicle
            destination_type = 'vehicle'
            destination_message = ' from the ' + self.name + ' aboard the ' + zoom_destination.name + ' at (' + str(self.x) + ', ' + str(self.y) + ') '
        elif self.in_building:
            zoom_destination = self.building.cell.get_intact_building('resource')
            destination_type = 'building'
            destination_message = ' from the ' + self.name + ' working in the ' + zoom_destination.name + ' at (' + str(self.x) + ', ' + str(self.y) + ') '
        else:
            zoom_destination = self
            destination_type = 'self'
            destination_message = ' from the ' + self.name + ' at (' + str(self.x) + ', ' + str(self.y) + ') '
            
        remaining_unit = 'none'
        if target == 'officer':
            text = 'The ' + self.officer.name + destination_message + 'has died from attrition. /n /n '
            if self.officer.automatically_replace:
                text += self.officer.generate_attrition_replacement_text() #'The ' + self.name + ' will remain inactive for the next turn as a replacement is found. /n /n'
                self.officer.replace(self) #self.officer.die()
                self.officer.death_sound()
            else:
                if self.in_vehicle:
                    self.disembark_vehicle(zoom_destination)
                if self.in_building:
                    self.leave_building(zoom_destination)
                officer = self.officer
                worker = self.worker
                self.disband()
                officer.attrition_death(False)
                if self.in_vehicle:
                    worker.embark_vehicle(zoom_destination)

            self.global_manager.get('notification_manager').display_notification({
                'message': text,
                'zoom_destination': zoom_destination,
            })

        elif target == 'worker':
            text = 'The ' + self.worker.name + destination_message + 'have died from attrition. /n /n '
            if self.worker.automatically_replace:
                text += self.worker.generate_attrition_replacement_text() #'The ' + self.name + ' will remain inactive for the next turn as replacements are found.'
                self.worker.replace(self)
                self.worker.death_sound()
            else:
                if self.in_vehicle:
                    self.disembark_vehicle(zoom_destination)
                if self.in_building:
                    self.leave_building(zoom_destination)
                officer = self.officer
                worker = self.worker
                self.disband()
                worker.attrition_death(False)
                if self.in_vehicle:
                    officer.embark_vehicle(zoom_destination)

            self.global_manager.get('notification_manager').display_notification({
                'message': text,
                'zoom_destination': zoom_destination,
            })

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
        self.remove_complete()

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
        self.update_image_bundle()

    def to_save_dict(self):
        '''
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
                Same pairs as superclass, along with:
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
        if not self.veteran:
            self.veteran = True
            self.set_name('veteran ' + self.name)
        if not self.officer.veteran:
            self.officer.set_name('veteran ' + self.officer.name)
            self.officer.veteran = True
        self.update_image_bundle()
        self.officer.update_image_bundle()
        #self.officer.update_image_bundle()
        if self.global_manager.get('displayed_mob') == self:
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display'), self) #updates actor info display with veteran icon

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
        super().go_to_grid(new_grid, new_coordinates)
        self.officer.go_to_grid(new_grid, new_coordinates)
        self.officer.join_group()
        self.worker.go_to_grid(new_grid, new_coordinates)
        self.worker.join_group()

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
        self.worker.leave_group(self)

        movement_ratio_remaining = self.movement_points / self.max_movement_points
        self.worker.set_movement_points(math.floor(movement_ratio_remaining * self.worker.max_movement_points))
        self.officer.status_icons = self.status_icons
        for current_status_icon in self.status_icons:
            current_status_icon.actor = self.officer
        self.officer.veteran = self.veteran
        self.officer.leave_group(self)
        self.officer.set_movement_points(math.floor(movement_ratio_remaining * self.officer.max_movement_points))
        self.remove_complete()

    def die(self, death_type = 'violent'):
        '''
        Description:
            Removes this object from relevant lists, prevents it from further appearing in or affecting the program, deselects it, and drops any commodities it is carrying. Unlike remove, this is used when the group dies because it
                also removes its worker and officer
        Input:
            string death_type == 'violent': Type of death for this unit, determining the type of sound played
        Output:
            None
        '''
        super().die(death_type)
        self.officer.die('none')
        self.worker.die('none')

    def get_image_id_list(self, override_values={}):
        '''
        Description:
            Generates and returns a list this actor's image file paths and dictionaries that can be passed to any image object to display those images together in a particular order and 
                orientation
        Input:
            None
        Output:
            list: Returns list of string image file paths, possibly combined with string key dictionaries with extra information for offset images
        '''
        #make an actor utility function that generates group image id list from worker and officer, regarless of if they are in the same group
        image_id_list = super().get_image_id_list(override_values)
        image_id_list.remove(self.image_dict['default']) #group default image is empty
        image_id_list += actor_utility.generate_group_image_id_list(self.worker, self.officer, self.global_manager)
        return(image_id_list)
