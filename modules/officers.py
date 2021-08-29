from .mobs import mob
from .tiles import veteran_icon
from . import actor_utility
from . import utility

class officer(mob):
    '''
    Mob that is considered an officer and can join groups and become a veteran
    '''
    def __init__(self, coordinates, grids, image_id, name, modes, global_manager):
        '''
        Input:
            Same as superclass
        '''
        super().__init__(coordinates, grids, image_id, name, modes, global_manager)
        global_manager.get('officer_list').append(self)
        self.veteran = False
        self.veteran_icons = []
        self.is_officer = True
        self.officer_type = 'default'
        actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self) #updates mob info display list to account for is_officer changing

    def go_to_grid(self, new_grid, new_coordinates):
        '''
        Input:
            Same as superclass
        Output:
            Same as superclass, except it also moves veteran icons to the new grid and coordinates
        '''
        if self.veteran and not self.in_group: #if (not (self.in_group or self.in_vehicle)) and self.veteran:
            for current_veteran_icon in self.veteran_icons:
                current_veteran_icon.remove()
        self.veteran_icons = []
        super().go_to_grid(new_grid, new_coordinates)
        if self.veteran and not self.in_group: #if (not (self.in_group or self.in_vehicle)) and self.veteran:
            for current_grid in self.grids:
                if current_grid == self.global_manager.get('minimap_grid'):
                    veteran_icon_x, veteran_icon_y = current_grid.get_mini_grid_coordinates(self.x, self.y)
                else:
                    veteran_icon_x, veteran_icon_y = (self.x, self.y)
                self.veteran_icons.append(veteran_icon((veteran_icon_x, veteran_icon_y), current_grid, 'misc/veteran_icon.png', 'veteran icon', ['strategic'], False, self, self.global_manager))

    def can_show_tooltip(self):
        '''
        Input:
            none
        Output:
            Same as superclass but only returns True if not part of a group
        '''
        if not (self.in_group or self.in_vehicle):
            return(super().can_show_tooltip())
        else:
            return(False)

    def join_group(self):
        '''
        Input:
            none
        Output:
            Prevents this officer from being seen and interacted with, storing it as part of a group
        '''
        self.in_group = True
        self.selected = False
        self.hide_images()
        #for current_image in self.images:
        #    current_image.remove_from_cell()

    def leave_group(self, group):
        '''
        Input:
            group object from which this officer is leaving
        Output:
            Allows this officer to be seen and interacted with, moving it to where the group was disbanded
        '''
        self.in_group = False
        self.x = group.x
        self.y = group.y
        #for current_image in self.images:
        #    current_image.add_to_cell()
        self.show_images()
        self.select()
        actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), self.images[0].current_cell.tile) #calibrate info display to officer's tile upon disbanding

    def remove(self):
        '''
        Input:
            none
        Output:
            Removes the object from relevant lists and prevents it from further appearing in or affecting the program
        '''
        super().remove()
        self.global_manager.set('officer_list', utility.remove_from_list(self.global_manager.get('officer_list'), self))
        for current_veteran_icon in self.veteran_icons:
            current_veteran_icon.remove()

class porter_foreman(officer):
    '''
    Officer that is considered a porter foreman
    '''
    def __init__(self, coordinates, grids, image_id, name, modes, global_manager):
        super().__init__(coordinates, grids, image_id, name, modes, global_manager)
        self.officer_type = 'porter foreman'

class explorer(officer):
    '''
    Officer that is considered an explorer
    '''
    def __init__(self, coordinates, grids, image_id, name, modes, global_manager):
        '''
        Input:
            Same as superclass
        '''
        super().__init__(coordinates, grids, image_id, name, modes, global_manager)
        self.officer_type = 'explorer'

class engineer(officer):
    '''
    Officer that is considered an engineer
    '''
    def __init__(self, coordinates, grids, image_id, name, modes, global_manager):
        '''
        Input:
            Same as superclass
        '''
        super().__init__(coordinates, grids, image_id, name, modes, global_manager)
        #self.grid.find_cell(self.x, self.y).set_visibility(True)
        self.officer_type = 'engineer'
