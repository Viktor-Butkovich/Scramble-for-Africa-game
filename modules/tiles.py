import pygame
from . import images
from . import utility
from . import actor_utility
from . import villages
from .actors import actor

class tile(actor): #to do: make terrain tiles a subclass
    '''
    An actor that appears under other actors and occupies a grid cell, being able to act as a passive icon, resource, terrain, or a hidden area
    '''
    def __init__(self, coordinates, grid, image, name, modes, show_terrain, global_manager): #show_terrain is like a subclass, true is terrain tile, false is non-terrain tile
        '''
        Input:
            coordinates: int tuple representing the coordinate location the tile will occupy on its grid
            grid: grid object representing the grid on which the tile will appear
            image: string representing a file path to the image used by the tile
            name: string representing the tile's name
            modes: list of string representing the game modes in which this tile can appear
            show_terrain: boolean representing whether the tile should act as terrain
            global_manager: global_manager_template object used to manage a dictionary of shared variables
        '''
        self.actor_type = 'tile'
        self.selection_outline_color = 'yellow'#'bright blue'
        self.actor_match_outline_color = 'white'
        super().__init__(coordinates, [grid], modes, global_manager)
        self.set_name(name)
        self.global_manager.get('tile_list').append(self)
        self.image_dict = {'default': image}
        self.image = images.tile_image(self, self.grid.get_cell_width(), self.grid.get_cell_height(), grid, 'default', global_manager)
        self.images = [self.image] #tiles only appear on 1 grid, but have a list of images defined to be more consistent with other actor subclasses
        self.show_terrain = show_terrain
        self.cell = self.grid.find_cell(self.x, self.y)
        self.can_hold_commodities = False
        if self.show_terrain:
            self.cell.tile = self
            self.resource_icon = 'none' #the resource icon is appearance, making it a property of the tile rather than the cell
            self.set_terrain(self.cell.terrain) #terrain is a property of the cell, being stored information rather than appearance, same for resource, set these in cell
            self.image_dict['hidden'] = 'scenery/paper_hidden.png'
            self.set_visibility(self.cell.visible)
            self.can_hold_commodities = True
        elif self.name == 'Europe': #abstract grid's tile has the same name as the grid, and Europe should be able to hold commodities despite not being terrain
            self.cell.tile = self
            self.resource_icon = 'none' #the resource icon is appearance, making it a property of the tile rather than the cell
            #self.set_terrain(self.cell.terrain) #terrain is a property of the cell, being stored information rather than appearance, same for resource, set these in cell
            self.image_dict['hidden'] = 'scenery/paper_hidden.png'
            self.set_visibility(self.cell.visible)
            self.can_hold_commodities = True
            self.terrain = 'none'
        elif self.name == 'resource icon':
            self.image_dict['hidden'] = 'misc/empty.png'
        else:
            self.terrain = 'none'
        self.update_tooltip()

    def update_resource_icon(self): #changes size of resource icon if building present
        if not self.resource_icon == 'none':
            self.resource_icon.update_resource_icon()

    def draw_destination_outline(self): #called directly by mobs
        for current_image in self.images:
            outline = self.cell.Rect#pygame.Rect(current_image.outline.x + 5, current_image.outline.y + 5, current_image.outline.width, current_image.outline.height)
            pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')[self.selection_outline_color], (outline), current_image.outline_width)

    def draw_actor_match_outline(self, called_by_equivalent):
        if self.images[0].can_show():
            for current_image in self.images:
                outline = self.cell.Rect#pygame.Rect(current_image.outline.x + 5, current_image.outline.y + 5, current_image.outline.width, current_image.outline.height)
                pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')[self.actor_match_outline_color], (outline), current_image.outline_width)
                equivalent_tile = self.get_equivalent_tile()
                if (not equivalent_tile == 'none') and (not called_by_equivalent):
                    equivalent_tile.draw_actor_match_outline(True)

    def change_inventory(self, commodity, change):
        '''
        Input:
            none
        Output:
            same as superclass, except, if this tile or its equivalent is currently being shown in the tile info display, updates the displayed commodities to reflect the change
        '''
        if self.can_hold_commodities:
            self.inventory[commodity] += change
            if not self.grid.attached_grid == 'none': #only get equivalent if there is an attached grid
                self.get_equivalent_tile().inventory[commodity] += change #doesn't call other tile's function to avoid recursion
            if self.global_manager.get('displayed_tile') == self or self.global_manager.get('displayed_tile') == self.get_equivalent_tile():
                actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), self)

    def set_inventory(self, commodity, new_value):
        '''
        Input:
            none
        Output:
            same as superclass, except, if this tile or its equivalent is currently being shown in the tile info display, updates the displayed commodities to reflect the change
        '''
        if self.can_hold_commodities:
            self.inventory[commodity] = new_value
            if not self.grid.attached_grid == 'none': #only get equivalent if there is an attached grid
                self.get_equivalent_tile.inventory[commodity] = new_value
            if self.global_manager.get('displayed_tile') == self or self.global_manager.get('displayed_tile') == self.get_equivalent_tile():
                actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), self)

    def get_main_grid_coordinates(self):
        if self.grid.is_mini_grid:
            return(self.grid.get_main_grid_coordinates(self.x, self.y))
        else:
            return((self.x, self.y))

    def get_equivalent_tile(self):
        '''
        Input:
            none
        Output:
            Returns the tile's equivalent on the grid. The equivalent should have different grid coordinates, depending on the minimap's location, but represent the same cell on the strategic map grid.
            A tile on the minimap grid will return its equivalent on the strategic map grid. A tile on the strategic map grid will return its equivalent on the minimap grid.
        '''
        if self.grid == self.global_manager.get('minimap_grid'):
            main_x, main_y = self.grid.get_main_grid_coordinates(self.x, self.y)
            #try:
            attached_cell = self.grid.attached_grid.find_cell(main_x, main_y)
            if not attached_cell == 'none':
                return(attached_cell.tile)
            return('none')
            #return(self.grid.attached_grid.find_cell(main_x, main_y).tile)
            #except:
            #    print("Minimap main grid conversion error, possibly when rmb near edge of map - (" + str(main_x) + ", " + str(main_y) + ")")
            #    return('none')
            
        elif self.grid == self.global_manager.get('strategic_map_grid'):
            mini_x, mini_y = self.grid.mini_grid.get_mini_grid_coordinates(self.x, self.y)
            equivalent_cell = self.grid.mini_grid.find_cell(mini_x, mini_y)
            if not equivalent_cell == 'none':
                return(equivalent_cell.tile)
            else:
                return('none')
        return('none')
            
    def set_visibility(self, new_visibility):
        '''
        Input:
            boolean representing the tile's new visibility status
        Output:
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
        Input:
            string representing the type of resource present in this terrain tile
        Output:
            Sets this tile's resource to the inputted string, removing or creating resource icons when applicable
        '''
        if not self.resource_icon == 'none':
            self.resource_icon.remove()
            self.resource_icon = 'none'
        self.resource = new_resource
        if not new_resource == 'none':
            if self.resource == 'natives':
                equivalent_tile = self.get_equivalent_tile()
                village_exists = False
                if not equivalent_tile == 'none':
                    if not equivalent_tile.cell.village == 'none': #if equivalent tile present and equivalent tile has village, copy village to equivalent instead of creating new one
                        village_exists = True
                        self.cell.village = equivalent_tile.cell.village
                if not village_exists: #make new village if village not present
                    self.cell.village = villages.village(self.cell)
            self.resource_icon = resource_icon((self.x, self.y), self.grid, self.cell.resource, 'resource icon', ['strategic'], False, self, self.global_manager)
        self.set_visibility(self.cell.visible)
            
    def set_terrain(self, new_terrain): #to do, add variations like grass to all terrains
        '''
        Input:
            string representing the type of terrain that will fill this tile
        Output:
            Sets this tile's terrain to the inputted string, changing its appearance when applicable
        '''
        if new_terrain == 'clear':
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
        Input:
            none
        Output:
            Sets this tile's tooltip to reflect its visibility status, terrain, and resource type
        '''
        if self.show_terrain: #if is terrain, show tooltip
            tooltip_message = []
            if self.cell.visible:
                tooltip_message.append('This is ' + utility.generate_article(self.cell.terrain) + ' ' + self.cell.terrain + ' tile.')
                if not self.cell.village == 'none': #if village present, show village
                    tooltip_message += self.cell.village.get_tooltip()
                elif not self.cell.resource == 'none': #if not village but other resource present, show resource
                    tooltip_message.append('This tile has ' + utility.generate_article(self.cell.resource) + ' ' + self.cell.resource + ' resource.')
            else:
                tooltip_message .append('This tile has not been explored.')
            self.set_tooltip(tooltip_message)
        else:
            self.set_tooltip([])

    def set_coordinates(self, x, y):
        '''
        Input:
            Two int variables reflecting this tile's new grid coordinates
        Output:
            Sets this tile's grid coordinates to the inputted int variables and changes its grid cell to the one it now occupies
        '''
        self.x = x
        self.y = y
        #my_cell = self.grid.find_cell(self.x, self.y)
                
    def remove(self):
        '''
        Input:
            none
        Output:
            Removes the object from relevant lists and prevents it from further appearing in or affecting the program
        '''
        super().remove()
        self.global_manager.set('tile_list', utility.remove_from_list(self.global_manager.get('tile_list'), self))
        self.global_manager.set('image_list', utility.remove_from_list(self.global_manager.get('image_list'), self.image)) #to do: see if this can be removed, should already be in actor

    def can_show_tooltip(self): #tiles don't have tooltips, except for terrain tiles
        '''
        Input:
            none
        Output:
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
        Input:
            grid: grid object representing the grid on which the tile will appear
            image: string representing a file path to the image used by the tile
            name: string representing the tile's name
            modes: list of string representing the game modes in which this tile can appear
            global_manager: global_manager_template object used to manage a dictionary of shared variables
        '''
        super().__init__((0, 0), grid, image, name, modes, False, global_manager)

    def update_tooltip(self):
        '''
        Input:
            none
        Output:
            Sets this tile's tooltip to reflect being part of an abstract grid
        '''
        self.set_tooltip([self.name])

    def can_show_tooltip(self):
        '''
        Input:
            none
        Output:
            Returns whether this tile should show its tooltip. It should show its tooltip only when it can appear and is touching the mouse. Unlike superclass, it does not require being a terrain tile.
        '''
        if self.touching_mouse() and self.global_manager.get('current_game_mode') in self.modes:
            return(True)
        else:
            return(False)

class resource_icon(tile):
    def __init__(self, coordinates, grid, resource, name, modes, show_terrain, attached_tile, global_manager):
        self.attached_tile = attached_tile
        self.resource = resource
        default_image_id = 'scenery/resources/' + self.resource + '.png'
        small_image_id = 'scenery/resources/small/' + self.resource + '.png'
        super().__init__(coordinates, grid, default_image_id, name, modes, show_terrain, global_manager)
        self.image_dict['small'] = small_image_id
        self.image_dict['large'] = default_image_id
        self.update_resource_icon()

    def update_resource_icon(self):
        if self.resource == 'natives':
            attached_village = self.attached_tile.cell.village
            if attached_village.population == 0: #0
                self.image_dict['small'] = 'scenery/resources/small/natives0.png'
                self.image_dict['large'] = 'scenery/resources/natives0.png'
            elif attached_village.population <= 3: #1-3
                self.image_dict['small'] = 'scenery/resources/small/natives1.png'
                self.image_dict['large'] = 'scenery/resources/natives1.png'
            elif attached_village.population <= 6: #4-6
                self.image_dict['small'] = 'scenery/resources/small/natives2.png'
                self.image_dict['large'] = 'scenery/resources/natives2.png'
            else: #7-10
                self.image_dict['small'] = 'scenery/resources/small/natives3.png'
                self.image_dict['large'] = 'scenery/resources/natives3.png'
                
        if (not self.attached_tile.cell.contained_buildings['port'] == 'none') or (not self.attached_tile.cell.contained_buildings['resource'] == 'none'): #make small if building present
            self.image.set_image('small')
            self.image_dict['default'] = self.image_dict['small']
        else:
            self.image.set_image('large')
            self.image_dict['default'] = self.image_dict['large']

class veteran_icon(tile):
    '''
    A tile that follows a veteran officer's image to show that it is a veteran officer
    '''
    def __init__(self, coordinates, grid, image, name, modes, show_terrain, actor, global_manager):
        '''
        Input:
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
        
class overlay_tile(tile):
    '''
    A tile that appears over other images, unlike most tiles
    '''
    def __init__(self, actor, width, height, grid, image_id, show_terrain, global_manager):
        '''
        Input:
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
        Input:
            none
        Output:
            Removes the object from relevant lists and prevents it from further appearing in or affecting the program
        '''
        super().remove()
        self.global_manager.set('overlay_tile_list', utility.remove_from_list(self.global_manager.get('overlay_tile_list'), self))
