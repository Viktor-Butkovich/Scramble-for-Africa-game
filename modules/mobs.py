import pygame
import time
from . import images
from . import text_tools
from . import utility
from .actors import actor
from .tiles import veteran_icon

class mob(actor):
    '''
    Actor that can be controlled and selected and can appear on multiple grids at once
    '''
    def __init__(self, coordinates, grids, image_id, name, modes, global_manager):
        '''
        Inputs:
            coordinates: tuple of two int variables representing the pixel coordinates of the bottom left of the notification
            grids: list of grid objects on which the mob's images will appear
            image_id: string representing the file path to the mob's default image
            name: string representing the mob's name
            modes: list of strings representing the game modes in which the mob can appear
            global_manager: global_manager_template object used to manage a dictionary of shared variables
        '''
        super().__init__(coordinates, grids, modes, global_manager)
        self.image_dict = {'default': image_id}
        #self.grids = grids #for things like drawing images on each grid, go through each grid on which the mob can appear # moved to actor class
        #self.grid = grids[0] #for things like detecting if moving is possible, use the first grid, which will be the main map
        self.selection_outline_color = 'bright green'
        self.images = []
        for current_grid in self.grids:
            self.images.append(images.mob_image(self, current_grid.get_cell_width(), current_grid.get_cell_height(), current_grid, 'default', self.global_manager))#self, actor, width, height, grid, image_description, global_manager
        global_manager.get('mob_list').append(self)
        self.set_name(name)
        self.update_tooltip()

    def go_to_grid(self, new_grid, new_coordinates):
        '''
        Input:
            grid object representing the grid to which the mob is transferring, tuple of two int variables representing the coordinates to which the mob will move on the new grid
        Output:
            Moves this mob and all of its images to the inputted grid at the inputted coordinates
        '''
        if new_grid == self.global_manager.get('europe_grid'):
            self.modes.append('europe')
        else:
            self.modes = utility.remove_from_list(self.modes, 'europe')
        self.x, self.y = new_coordinates
        for current_image in self.images:
            current_image.remove_from_cell()
            self.global_manager.set('image_list', utility.remove_from_list(self.global_manager.get('image_list'), current_image))
        self.grids = [new_grid]
        self.grid = new_grid
        if not new_grid.mini_grid == 'none':
            new_grid.mini_grid.calibrate(new_coordinates[0], new_coordinates[1])
            self.grids.append(new_grid.mini_grid)
        self.images = []
        for current_grid in self.grids:
            self.images.append(images.mob_image(self, current_grid.get_cell_width(), current_grid.get_cell_height(), current_grid, 'default', self.global_manager))
            self.images[-1].add_to_cell()

    def select(self):
        '''
        Inputs:
            none
        Outputs:
            Causes this mob to be selected and causes the selection outline timer to be reset, displaying it immediately
        '''
        self.selected = True
        self.global_manager.set('show_selection_outlines', True)
        self.global_manager.set('last_selection_outline_switch', time.time())#outlines should be shown immediately when selected

    def draw_outline(self):
        '''
        Inputs:
            none
        Outputs:
            If selection outlines are currently allowed to appear and if this mob is showing, draw a selection outline around each of its images
        '''
        if self.global_manager.get('show_selection_outlines'):
            for current_image in self.images:
                if not current_image.current_cell == 'none' and self == current_image.current_cell.contained_mobs[0]: #only draw outline if on top of stack
                    pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')[self.selection_outline_color], (current_image.outline), current_image.outline_width)
        
    def update_tooltip(self):
        '''
        Inputs:
            none
        Outputs:
            Sets this mob's tooltip to its name
        '''
        self.set_tooltip([self.name])

    def remove(self):
        '''
        Inputs:
            none
        Outputs:
            Removes the object from relevant lists and prevents it from further appearing in or affecting the program
        '''
        for current_image in self.images:
            current_image.remove_from_cell()
        super().remove()
        self.global_manager.set('mob_list', utility.remove_from_list(self.global_manager.get('mob_list'), self)) #make a version of mob_list without self and set mob_list to it

    def can_move(self, x_change, y_change):
        '''
        Inputs:
            int representing the distance moved to the right from a proposed movement, int representing the distance moved upward from a proposed movement
        Outputs:
            Returns whether the proposed movement would be possible
        '''
        future_x = self.x + x_change
        future_y = self.y + y_change
        if not self.grid in self.global_manager.get('abstract_grid_list'):
            if future_x >= 0 and future_x < self.grid.coordinate_width and future_y >= 0 and future_y < self.grid.coordinate_height:
                if self.grid.find_cell(future_x, future_y).visible:
                    if not self.grid.find_cell(future_x, future_y).terrain == 'water':
                        return(True)
                    else:
                        if self.grid.find_cell(future_x, future_y).visible:
                            text_tools.print_to_screen("You can't move into the water.", self.global_manager) #to do: change this when boats are added
                            return(False)
                else:
                    text_tools.print_to_screen("You can't move into an unexplored tile.", self.global_manager)
                    return(False)

            else:
                text_tools.print_to_screen("You can't move off of the map.", self.global_manager)
                return(False)
        else:
            text_tools.print_to_screen("You can not move while in this area.", self.global_manager)
            return(False)

    def move(self, x_change, y_change):
        '''
        Inputs:
            int representing the distance moved to the right, int representing the distance moved upward
        Outputs:
            Moves this mob x_change tiles to the right and y_change tiles upward
        '''
        for current_image in self.images:
            current_image.remove_from_cell()
        self.x += x_change
        self.y += y_change
        self.global_manager.get('minimap_grid').calibrate(self.x, self.y)
        for current_image in self.images:
            current_image.add_to_cell()

    def touching_mouse(self):
        '''
        Inputs:
            none
        Outputs:
            Returns whether any of this mob's images are colliding with the mouse
        '''
        for current_image in self.images:
            if current_image.Rect.collidepoint(pygame.mouse.get_pos()): #if mouse is in image
                if not (current_image.grid == self.global_manager.get('minimap_grid') and not current_image.grid.is_on_mini_grid(self.x, self.y)): #do not consider as touching mouse if off-map
                    return(True)
        return(False) #return false if none touch mouse

class worker(mob):
    '''
    Mob that is considered a worker and can join groups
    '''
    def __init__(self, coordinates, grids, image_id, name, modes, global_manager):
        '''
        Inputs:
            same as superclass 
        '''
        super().__init__(coordinates, grids, image_id, name, modes, global_manager)
        global_manager.get('worker_list').append(self)
        self.in_group = False

    def can_show_tooltip(self):
        '''
        Inputs:
            none
        Outputs:
            Same as superclass but only returns True if not part of a group
        '''
        if self.touching_mouse() and self.global_manager.get('current_game_mode') in self.modes and not self.in_group: #and not targeting_ability
            return(True)
        else:
            return(False)

    def join_group(self):
        '''
        Inputs:
            none
        Outputs:
            Prevents this worker from being seen and interacted with, storing it as part of a group
        '''
        self.in_group = True
        self.selected = False
        for current_image in self.images:
            current_image.remove_from_cell()

    def leave_group(self, group):
        '''
        Inputs:
            group object from which this worker is leaving
        Outputs:
            Allows this worker to be seen and interacted with, moving it to where the group was disbanded
        '''
        self.in_group = False
        self.x = group.x
        self.y = group.y
        for current_image in self.images:
            current_image.add_to_cell()
        #self.select()

    def remove(self):
        '''
        Inputs:
            none
        Outputs:
            Removes the object from relevant lists and prevents it from further appearing in or affecting the program
        '''
        super().remove()
        self.global_manager.set('worker_list', utility.remove_from_list(self.global_manager.get('worker_list'), self))

class officer(mob):
    '''
    Mob that is considered an officer and can join groups and become a veteran
    '''
    def __init__(self, coordinates, grids, image_id, name, modes, global_manager):
        super().__init__(coordinates, grids, image_id, name, modes, global_manager)
        global_manager.get('officer_list').append(self)
        self.veteran = False
        self.veteran_icons = []
        self.in_group = False
        self.officer_type = 'default'

    def go_to_grid(self, new_grid, new_coordinates):
        if (not self.in_group) and self.veteran:
            for current_veteran_icon in self.veteran_icons:
                current_veteran_icon.remove()
            self.veteran_icons = []
        super().go_to_grid(new_grid, new_coordinates)
        if (not self.in_group) and self.veteran:
            for current_grid in self.grids:
                if current_grid == self.global_manager.get('minimap_grid'):
                    veteran_icon_x, veteran_icon_y = current_grid.get_mini_grid_coordinates(self.x, self.y)
                else:
                    veteran_icon_x, veteran_icon_y = (self.x, self.y)
                self.veteran_icons.append(veteran_icon((veteran_icon_x, veteran_icon_y), current_grid, 'misc/veteran_icon.png', 'veteran icon', ['strategic'], False, self, self.global_manager))

    def can_show_tooltip(self): #moved to actor
        '''
        Inputs:
            none
        Outputs:
            Same as superclass but only returns True if not part of a group
        '''
        if self.touching_mouse() and self.global_manager.get('current_game_mode') in self.modes and not self.in_group: #and not targeting_ability 
            return(True)
        else:
            return(False)

    def join_group(self):
        '''
        Inputs:
            none
        Outputs:
            Prevents this officer from being seen and interacted with, storing it as part of a group
        '''
        self.in_group = True
        self.selected = False
        for current_image in self.images:
            current_image.remove_from_cell()

    def leave_group(self, group):
        '''
        Inputs:
            group object from which this officer is leaving
        Outputs:
            Allows this officer to be seen and interacted with, moving it to where the group was disbanded
        '''
        self.in_group = False
        self.x = group.x
        self.y = group.y
        self.update_veteran_icons()
        for current_image in self.images:
            current_image.add_to_cell()
        self.select()

    def remove(self):
        '''
        Inputs:
            none
        Outputs:
            Removes the object from relevant lists and prevents it from further appearing in or affecting the program
        '''
        super().remove()
        self.global_manager.set('officer_list', utility.remove_from_list(self.global_manager.get('officer_list'), self))
        for current_veteran_icon in self.veteran_icons:
            current_veteran_icon.remove()

    def update_veteran_icons(self):
        '''
        Inputs:
            none
        Outputs:
            Moves this officer's veteran icons to follow its images
        '''
        for current_veteran_icon in self.veteran_icons:
            if current_veteran_icon.grid.is_mini_grid:
                current_veteran_icon.x, current_veteran_icon.y = current_veteran_icon.grid.get_mini_grid_coordinates(self.x, self.y)
            else:
                current_veteran_icon.x = self.x
                current_veteran_icon.y = self.y

    def move(self, x_change, y_change):
        '''
        Inputs:
            Same as superclass
        Outputs:
            Same as superclass but also moves its veteran icons to follow its images
        '''
        super().move(x_change, y_change)
        self.update_veteran_icons()
        #print(self.veteran_icons)

class explorer(officer):
    '''
    Officer that is considered an explorer
    '''
    def __init__(self, coordinates, grids, image_id, name, modes, global_manager):
        '''
        Inputs:
            Same as superclass
        '''
        super().__init__(coordinates, grids, image_id, name, modes, global_manager)
        self.grid.find_cell(self.x, self.y).set_visibility(True)
        self.officer_type = 'explorer'
