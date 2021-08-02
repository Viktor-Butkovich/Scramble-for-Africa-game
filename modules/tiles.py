import pygame
from . import images
from . import utility
from . import actor_utility
from .actors import actor

class tile(actor): #to do: make terrain tiles a subclass
    '''
    An actor that appears under other actors and occupies a grid cell, being able to act as a passive icon, resource, terrain, or a hidden area
    '''
    def __init__(self, coordinates, grid, image, name, modes, show_terrain, global_manager): #show_terrain is like a subclass, true is terrain tile, false is non-terrain tile
        '''
        Inputs:
            coordinates: int tuple representing the coordinate location the tile will occupy on its grid
            grid: grid object representing the grid on which the tile will appear
            image: string representing a file path to the image used by the tile
            name: string representing the tile's name
            modes: list of string representing the game modes in which this tile can appear
            show_terrain: boolean representing whether the tile should act as terrain
            global_manager: global_manager_template object used to manage a dictionary of shared variables
        '''
        super().__init__(coordinates, [grid], modes, global_manager)
        self.set_name(name)
        self.global_manager.get('tile_list').append(self)
        self.image_dict = {'default': image}
        self.image = images.tile_image(self, self.grid.get_cell_width(), self.grid.get_cell_height(), grid, 'default', global_manager)
        self.images = [self.image] #tiles only appear on 1 grid, have images defined to be more consistent with other actor subclasses
        self.show_terrain = show_terrain
        self.cell = self.grid.find_cell(self.x, self.y)
        self.can_hold_commodities = False
        if self.show_terrain: #to do: make terrain tiles a subclass
            self.cell.tile = self
            self.resource_icon = 'none' #the resource icon is appearance, making it a property of the tile rather than the cell
            self.set_terrain(self.cell.terrain) #terrain is a property of the cell, being stored information rather than appearance, same for resource, set these in cell
            self.image_dict['hidden'] = 'scenery/paper_hidden.png'
            self.set_visibility(self.cell.visible)
            self.can_hold_commodities = True
        elif self.name == 'resource icon':
            self.image_dict['hidden'] = 'misc/empty.png'
        else:
            self.terrain = 'none'

    def change_inventory(self, commodity, change): #changes last 2 lines from actor version
        if self.can_hold_commodities:
            self.inventory[commodity] += change
            self.get_equivalent_tile().inventory[commodity] += change #doesn't call other tile's function to avoid recursion
            if self.global_manager.get('displayed_tile') == self or self.global_manager.get('displayed_tile') == self.get_equivalent_tile():
                actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), self)

    def set_inventory(self, commodity, new_value):
        if self.can_hold_commodities:
            self.inventory[commodity] = new_value
            self.get_equivalent_tile.inventory[commodity] = new_value
            if self.global_manager.get('displayed_tile') == self or self.global_manager.get('displayed_tile') == self.get_equivalent_tile():
                actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), self)

    def get_equivalent_tile(self):
        if self.grid == self.global_manager.get('minimap_grid'):
            main_x, main_y = self.grid.get_main_grid_coordinates(self.x, self.y)
            return(self.grid.attached_grid.find_cell(main_x, main_y).tile)
        elif self.grid == self.global_manager.get('strategic_map_grid'):
            mini_x, mini_y = self.grid.mini_grid.get_mini_grid_coordinates(self.x, self.y)
            return(self.grid.mini_grid.find_cell(mini_x, mini_y).tile)
            
    def set_visibility(self, new_visibility):
        '''
        Inputs:
            boolean representing the tile's new visibility status
        Outputs:
            Changes the tile's appearance to match whether it is now visible
        '''
        if new_visibility == True:
            image_name = 'default'
        else:
            image_name = 'hidden'
            
        self.image.set_image(image_name)
        self.image.previous_idle_image = image_name
        if not self.resource_icon == 'none':
            self.resource_icon.image.set_image(image_name)
            self.resource_icon.image.previous_idle_image = image_name
            
    def set_resource(self, new_resource):
        '''
        Inputs:
            string representing the type of resource present in this terrain tile
        Outputs:
            Sets this tile's resource to the inputted string, removing or creating resource icons when applicable
        '''
        if not self.resource_icon == 'none':
            self.resource_icon.remove()
            self.resource_icon = 'none'
        self.resource = new_resource
        self.resource_icon = tile((self.x, self.y), self.grid, 'scenery/resources/' + self.cell.resource + '.png', 'resource icon', ['strategic'], False, self.global_manager)
        self.set_visibility(self.cell.visible)
            
    def set_terrain(self, new_terrain): #to do, add variations like grass to all terrains
        '''
        Inputs:
            string representing the type of terrain that will fill this tile
        Outputs:
            Sets this tile's terrain to the inputted string, changing its appearance when applicable
        '''
        #print(self.cell.terrain + ' ' + new_terrain)
        if new_terrain == 'clear':
            #random_grass = random.randrange(1, 3) #clear, hills, jungle, water, mountain, swamp, desert
            #self.image_dict['default'] = 'scenery/terrain/clear' + str(random_grass) + '.png'
            self.image_dict['default'] = 'scenery/terrain/clear.png'
            
        elif new_terrain == 'hills':
            self.image_dict['default'] = 'scenery/terrain/hills.png'
            
        elif new_terrain == 'jungle':
            self.image_dict['default'] = 'scenery/terrain/jungle.png'
            
        elif new_terrain == 'water':
            self.image_dict['default'] = 'scenery/terrain/water.png'
            
        elif new_terrain == 'mountain':
            self.image_dict['default'] = 'scenery/terrain/mountain.png'
            
        elif new_terrain == 'swamp':
            self.image_dict['default'] = 'scenery/terrain/swamp.png'
            
        elif new_terrain == 'desert':
            self.image_dict['default'] = 'scenery/terrain/desert.png'

        elif new_terrain == 'none':
            self.image_dict['default'] = 'scenery/hidden.png'

        self.image.set_image('default')

    def update_tooltip(self):
        '''
        Inputs:
            none
        Outputs:
            Sets this tile's tooltip to reflect its visibility status, terrain, and resource type
        '''
        if self.show_terrain: #if is terrain, show tooltip
            tooltip_message = []
            if self.cell.visible:
                tooltip_message.append('This is a ' + self.cell.terrain + ' tile.')
                if not self.cell.resource == 'none':
                    tooltip_message.append('This tile has a ' + self.cell.resource + ' resource.')
            else:
                tooltip_message .append('This tile has not been explored.')
            self.set_tooltip(tooltip_message)
        else:
            self.set_tooltip([])
            
        #tooltip_list = [] #activate to see contained mobs in tiles
        #for index in range(len(self.cell.contained_mobs)):
        #   tooltip_list.append(str(self.cell.contained_mobs[index]))
        #self.set_tooltip(tooltip_list)

    def set_coordinates(self, x, y):
        '''
        Inputs:
            Two int variables reflecting this tile's new grid coordinates
        Outputs:
            Sets this tile's grid coordinates to the inputted int variables and changes its grid cell to the one it now occupies
        '''
        #my_cell = self.grid.find_cell(self.x, self.y)
        self.x = x
        self.y = y
        my_cell = self.grid.find_cell(self.x, self.y)
                
    def remove(self):
        '''
        Inputs:
            none
        Outputs:
            Removes the object from relevant lists and prevents it from further appearing in or affecting the program
        '''
        super().remove()
        self.global_manager.set('tile_list', utility.remove_from_list(self.global_manager.get('tile_list'), self))
        self.global_manager.set('image_list', utility.remove_from_list(self.global_manager.get('image_list'), self.image)) #to do: see if this can be removed, should already be in actor
        #self.global_manager.set('image_list', utility.remove_from_list(self.global_manager.get('image_list'), self.shader))
        #print('removing')
        #self.cell.tile = 'none'
        #to do: this remove function is being called incorrectly at some point in the program, causing tiles to be removed

    def can_show_tooltip(self): #tiles don't have tooltips, except for terrain tiles
        '''
        Inputs:
            none
        Outputs:
            Returns whether this tile should show its tooltip. It should show its tooltip only if it is a terrain tile and when it can appear and is touching the mouse
        '''
        if self.show_terrain == True:
            if self.touching_mouse() and self.global_manager.get('current_game_mode') in self.modes: #and not targeting_ability
                if self.cell.terrain == 'none':
                    return(False)
                else:
                    return(True)
            else:
                return(False)
        else:
            return(False)

class abstract_tile(tile):
    '''
    tile for abstract grids that can have a tooltip but does not have terrain
    '''
    def __init__ (self, grid, image, name, modes, global_manager):
        '''
        Inputs:
            grid: grid object representing the grid on which the tile will appear
            image: string representing a file path to the image used by the tile
            name: string representing the tile's name
            modes: list of string representing the game modes in which this tile can appear
            global_manager: global_manager_template object used to manage a dictionary of shared variables
        '''
        super().__init__((0, 0), grid, image, name, modes, False, global_manager)

    def update_tooltip(self):
        '''
        Inputs:
            none
        Outputs:
            Sets this tile's tooltip to reflect being part of an abstract grid
        '''
        self.set_tooltip([self.name])

    def can_show_tooltip(self):
        '''
        Inputs:
            none
        Outputs:
            Returns whether this tile should show its tooltip. It should show its tooltip only when it can appear and is touching the mouse. Unlike superclass, it does not require being a terrain tile.
        '''
        if self.touching_mouse() and self.global_manager.get('current_game_mode') in self.modes:
            return(True)
        else:
            return(False)

class veteran_icon(tile):
    '''
    A tile that follows a veteran officer's image to show that it is a veteran officer
    '''
    def __init__(self, coordinates, grid, image, name, modes, show_terrain, actor, global_manager):
        '''
        Inputs:
            coordinates: int tuple representing the coordinate location the tile will occupy on its grid
            grid: grid object representing the grid on which the tile will appear
            image: string representing a file path to the image used by the tile
            name: string representing the tile's name
            modes: list of string representing the game modes in which this tile can appear
            show_terrain: boolean representing whether the tile should act as terrain
            global_manager: global_manager_template object used to manage a dictionary of shared variables
        '''
        super().__init__(coordinates, grid, image, name, modes, show_terrain, global_manager)
        self.actor = actor
        self.global_manager.set('image_list', utility.remove_from_list(self.global_manager.get('image_list'), self.image))
        self.image = images.veteran_icon_image(self, self.grid.get_cell_width(), self.grid.get_cell_height(), grid, 'default', global_manager)
        self.images = [self.image]

    def remove(self):
        super().remove()
        
class overlay_tile(tile):
    '''
    A tile that appears over other images, unlike most tiles
    '''
    def __init__(self, actor, width, height, grid, image_id, show_terrain, global_manager):
        '''
        Inputs:
            actor: represents that actor that this tile will appear over
            width: int representing the width in pixels of this tile
            height: int representing the height in pixels of this tile
            grid: grid object representing the grid on which the tile will appear
            image_id: string representing a file path to the image used by the tile
            show_terrain: boolean representing whether the tile should act as terrain
            global_manager: global_manager_template object used to manage a dictionary of shared variables
        '''
        super().__init__(actor, width, height, grid, image_id, show_terrain, global_manager)
        self.global_manager.get('overlay_tile_list').append(self)
        
    def remove(self):
        '''
        Inputs:
            none
        Outputs:
            Removes the object from relevant lists and prevents it from further appearing in or affecting the program
        '''
        super().remove()
        self.global_manager.set('overlay_tile_list', utility.remove_from_list(self.global_manager.get('overlay_tile_list'), self))
