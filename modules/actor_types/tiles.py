#Contains functionality for tiles and other cell icons

import pygame
import random
from ..constructs import images, villages
from ..util import utility, actor_utility, main_loop_utility
from .actors import actor
import modules.constants.constants as constants
import modules.constants.status as status
import modules.constants.flags as flags

class tile(actor): #to do: make terrain tiles a subclass
    '''
    An actor that appears under other actors and occupies a grid cell, being able to act as a passive icon, resource, terrain, or a hidden area
    '''
    def __init__(self, from_save, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates on one of the game grids
                'grid': grid value - grid in which this tile can appear
                'image': string value - File path to the image used by this object
                'name': string value - This tile's name
                'modes': string list value - Game modes during which this actor's images can appear
                'show_terrain': boolean value - True if this tile shows a cell's terrain. False if it does not show terrain, like a veteran icon or resource icon
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.actor_type = 'tile'
        self.selection_outline_color = 'yellow'#'bright blue'
        self.actor_match_outline_color = 'white'
        input_dict['grids'] = [input_dict['grid']] #give actor a 1-item list of grids as input
        super().__init__(from_save, input_dict, global_manager)
        self.set_name(input_dict['name'])
        self.image_dict = {'default': input_dict['image']}
        self.image = images.tile_image(self, self.grid.get_cell_width(), self.grid.get_cell_height(), input_dict['grid'], 'default', global_manager)
        self.images = [self.image] #tiles only appear on 1 grid, but have a list of images defined to be more consistent with other actor subclasses
        self.show_terrain = input_dict['show_terrain']
        self.cell = self.grid.find_cell(self.x, self.y)
        self.hosted_images = []
        if self.show_terrain:
            self.cell.tile = self
            self.image_dict['hidden'] = 'scenery/paper_hidden.png'
            self.set_terrain(self.cell.terrain) #terrain is a property of the cell, being stored information rather than appearance, same for resource, set these in cell
            self.can_hold_commodities = True
            self.inventory_setup()
            if self.cell.grid.from_save: #load in saved inventory from cell
                self.load_inventory(self.cell.save_dict['inventory'])
        elif self.name in ['Europe', 'Slave traders']: #abstract grid's tile has the same name as the grid, and Europe should be able to hold commodities despite not being terrain
            self.cell.tile = self
            self.can_hold_commodities = True
            self.can_hold_infinite_commodities = True
            self.inventory_setup()
            self.terrain = 'none'
            if self.cell.grid.from_save: #load in saved inventory from cell
                self.load_inventory(self.cell.save_dict['inventory'])
        else:
            self.terrain = 'none'
        self.update_tooltip()
        self.update_image_bundle()

    def draw_destination_outline(self, color = 'default'): #called directly by mobs
        '''
        Description:
            Draws an outline around this tile when the displayed mob has a pending movement order to move to this tile
        Input:
            string color = 'default': If an input is given, that color from the color_dict will be used instead of the default destination outline color
        Output:
            None
        '''
        for current_image in self.images:
            outline = self.cell.Rect
            if color == 'default':
                color = constants.color_dict[self.selection_outline_color]
            else:
                color = constants.color_dict[color] #converts input string to RGB tuple
            pygame.draw.rect(constants.game_display, color, (outline), current_image.outline_width)

    def draw_actor_match_outline(self, called_by_equivalent):
        '''
        Description:
            Draws an outline around the displayed tile. If the tile is shown on a minimap, tells the equivalent tile to also draw an outline around the displayed tile
        Input:
            boolean called_by_equivalent: True if this function is being called by the equivalent tile on either the minimap grid or the strategaic map grid, otherwise False. Prevents infinite loops of equivalent tiles repeatedly
                calling each other
        Output:
            None
        '''
        if self.images[0].can_show():
            for current_image in self.images:
                outline = self.cell.Rect
                pygame.draw.rect(constants.game_display, constants.color_dict[self.actor_match_outline_color], (outline), current_image.outline_width)
                equivalent_tile = self.get_equivalent_tile()
                if (not equivalent_tile == 'none') and (not called_by_equivalent):
                    equivalent_tile.draw_actor_match_outline(True)

    def remove_excess_inventory(self):
        '''
        Description:
            Removes random excess commodities from this tile until the number of commodities fits in this tile's inventory capacity
        Input:
            None
        Output:
            None
        '''
        if self.can_hold_commodities and not self.can_hold_infinite_commodities:
            inventory_used = self.get_inventory_used()
            amount_to_remove = inventory_used - self.inventory_capacity
            if amount_to_remove > 0:
                commodity_types = self.get_held_commodities()
                amount_removed = 0
                while amount_removed < amount_to_remove:
                    commodity_removed = random.choice(commodity_types)
                    if self.get_inventory(commodity_removed) > 0:
                        self.change_inventory(commodity_removed, -1)
                        amount_removed += 1
        
    def change_inventory(self, commodity, change):
        '''
        Description:
            Changes the number of commodities of a certain type held by this tile. Also ensures that the tile info display is updated correctly
        Input:
            string commodity: Type of commodity to change the inventory of
            int change: Amount of commodities of the inputted type to add. Removes commodities of the inputted type if negative
        Output:
            None
        '''
        if self.can_hold_commodities:
            self.inventory[commodity] += change
            if not self.grid.attached_grid == 'none': #only get equivalent if there is an attached grid
                self.get_equivalent_tile().inventory[commodity] += change #doesn't call other tile's function to avoid recursion
            if status.displayed_tile == self or status.displayed_tile == self.get_equivalent_tile():
                actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display'), self)

    def set_inventory(self, commodity, new_value):
        '''
        Description:
            Sets the number of commodities of a certain type held by this tile. Also ensures that the tile info display is updated correctly
        Input:
            string commodity: Type of commodity to set the inventory of
            int new_value: Amount of commodities of the inputted type to set inventory to
        Output:
            None
        '''
        if self.can_hold_commodities:
            self.inventory[commodity] = new_value
            if not self.grid.attached_grid == 'none': #only get equivalent if there is an attached grid
                self.get_equivalent_tile.inventory[commodity] = new_value
            if status.displayed_tile == self or status.displayed_tile == self.get_equivalent_tile():
                actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display'), self)

    def get_main_grid_coordinates(self):
        '''
        Description:
            Returns the coordinates cooresponding to this tile on the strategic map grid. If this tile is already on the strategic map grid, just returns this tile's coordinates
        Input:
            None
        Output:
            int tuple: Two 
        '''
        if self.grid.is_mini_grid:
            return(self.grid.get_main_grid_coordinates(self.x, self.y))
        else:
            return((self.x, self.y))

    def get_equivalent_tile(self):
        '''
        Description:
            Returns the corresponding minimap tile if this tile is on the strategic map grid or vice versa
        Input:
            None
        Output:
            tile: tile on the corresponding tile on the grid attached to this tile's grid
        '''
        if self.grid == status.minimap_grid:
            main_x, main_y = self.grid.get_main_grid_coordinates(self.x, self.y)
            attached_cell = self.grid.attached_grid.find_cell(main_x, main_y)
            if attached_cell:
                return(attached_cell.tile)
            return('none')
        elif self.grid == status.strategic_map_grid:
            mini_x, mini_y = self.grid.mini_grid.get_mini_grid_coordinates(self.x, self.y)
            equivalent_cell = self.grid.mini_grid.find_cell(mini_x, mini_y)
            if equivalent_cell:
                return(equivalent_cell.tile)
            else:
                return('none')
        return('none')
            
    #maybe make these into general actor functions? override update image bundle for tile to account for resources/buildings, have group version with multiple entities
    def get_image_id_list(self, force_visibility = False):
        '''
        Description:
            Generates and returns a list this actor's image file paths and dictionaries that can be passed to any image object to display those images together in a particular order and 
                orientation
        Input:
            boolean force_visibility = False: Shows a fully visible version of this tile, even if it hasn't been explored yet
        Output:
            list: Returns list of string image file paths, possibly combined with string key dictionaries with extra information for offset images
        '''
        image_id_list = []
        if self.cell.grid.is_mini_grid:
            equivalent_tile = self.get_equivalent_tile()
            if equivalent_tile != 'none' and self.show_terrain:
                image_id_list = equivalent_tile.get_image_id_list()
            else:
                image_id_list.append(self.image_dict['default']) #blank void image if outside of matched area
        elif self.cell.grid.is_abstract_grid and self.cell.tile.name == 'Slave traders':
            image_id_list.append(self.image_dict['default'])
            strength_modifier = actor_utility.get_slave_traders_strength_modifier(self.global_manager)
            if strength_modifier == 'none':
                adjective = 'no'
            elif strength_modifier < 0:
                adjective = 'high'
            elif strength_modifier > 0:
                adjective = 'low'
            else:
                adjective = 'normal'
            image_id_list.append('locations/slave_traders/' + adjective + '_strength.png')
        else:
            if self.cell.visible or force_visibility: #force visibility shows full tile even if tile is not yet visible
                image_id_list.append({'image_id': self.image_dict['default'], 'size': 1, 'x_offset': 0, 'y_offset': 0, 'level': -9})
                if self.cell.resource != 'none':
                    image_id_list.append(actor_utility.generate_resource_icon(self, self.global_manager))
                for current_building_type in constants.building_types:
                    current_building = self.cell.get_building(current_building_type)
                    if current_building != 'none':
                        image_id_list += current_building.get_image_id_list()
            elif self.show_terrain:
                image_id_list.append(self.image_dict['hidden'])
            else:
                image_id_list.append(self.image_dict['default'])
            for current_image in self.hosted_images:
                image_id_list += current_image.get_image_id_list()
        return(image_id_list)

    def update_image_bundle(self, override_image=None):
        '''
        Description:
            Updates this actor's images with its current image id list, also updating the minimap grid version if applicable
        Input:
            image_bundle override_image=None: Image bundle to update image with, setting this tile's image to a copy of the image bundle instead of generating a new image
                bundle
        Output:
            None
        '''
        if override_image:
            self.set_image(override_image)
        else:
            self.set_image(self.get_image_id_list())
        if self.grid == status.strategic_map_grid:
            equivalent_tile = self.get_equivalent_tile()
            if equivalent_tile != 'none':
                equivalent_tile.update_image_bundle(override_image=override_image)
            
    def set_resource(self, new_resource, update_image_bundle = True):
        '''
        Description:
            Sets the resource type of this tile to the inputted value, removing or creating resource icons as needed
        Input:
            string new_resource: The new resource type of this tile, like 'exotic wood'
            boolean update_image_bundle: Whether to update the image bundle - if multiple sets are being used on a tile, optimal to only update after the last one
        Output:
            None
        '''
        self.resource = new_resource
        if not new_resource == 'none':
            if self.resource == 'natives':
                equivalent_tile = self.get_equivalent_tile()
                village_exists = False
                if not equivalent_tile == 'none':
                    if not equivalent_tile.cell.village == 'none': #if equivalent tile present and equivalent tile has village, copy village to equivalent instead of creating new one
                        village_exists = True
                        self.cell.village = equivalent_tile.cell.village
                        self.cell.village.tiles.append(self)
                        if self.cell.grid.is_mini_grid: #set main cell of village to one on strategic map grid, as opposed to the mini map
                            self.cell.village.cell = equivalent_tile.cell
                        else:
                            self.cell.village.cell = self.cell
                if not village_exists: #make new village if village not present
                    if self.cell.grid.from_save:
                        self.cell.village = villages.village(True, {
                            'name': self.cell.save_dict['village_name'],
                            'population': self.cell.save_dict['village_population'],
                            'aggressiveness': self.cell.save_dict['village_aggressiveness'],
                            'available_workers': self.cell.save_dict['village_available_workers'],
                            'attached_warriors': self.cell.save_dict['village_attached_warriors'],
                            'found_rumors': self.cell.save_dict['village_found_rumors'],
                            'cell': self.cell
                        }, self.global_manager)
                        self.cell.village.tiles.append(self)
                    else:
                        self.cell.village = villages.village(False, {
                            'cell': self.cell
                        }, self.global_manager)
                        self.cell.village.tiles.append(self)
        if update_image_bundle:
            self.update_image_bundle()
            
    def set_terrain(self, new_terrain, update_image_bundle = True): #to do, add variations like grass to all terrains
        '''
        Description:
            Sets the terrain type of this tile to the inputted value, changing its appearance as needed
        Input:
            string new_terrain: The new terrain type of this tile, like 'swamp'
            boolean update_image_bundle: Whether to update the image bundle - if multiple sets are being used on a tile, optimal to only update after the last one
        Output:
            None
        '''
        if new_terrain in constants.terrain_list + ['water']:
            base_word = new_terrain
            if new_terrain == 'water':
                current_y = self.y
                if self.cell.grid.is_mini_grid:
                    current_y = self.cell.grid.get_main_grid_coordinates(self.x, self.y)[1]
                if current_y == 0:
                    base_word = 'ocean_' + new_terrain
                else:
                    base_word = 'river_' + new_terrain
            self.image_dict['default'] = 'scenery/terrain/' + base_word + '_' + str(self.cell.terrain_variant) + '.png'
        elif new_terrain == 'none':
            self.image_dict['default'] = 'scenery/hidden.png'
        if update_image_bundle:
            self.update_image_bundle() #self.image.set_image('default')

    def update_tooltip(self):
        '''
        Description:
            Sets this tile's tooltip to what it should be whenever the player looks at the tooltip. If this tile is explored, sets tooltip to this tile's terrain and its resource, if any. Otherwise, sets tooltip to a description of how
                this tile has not explored
        Input:
            None
        Output:
            None
        '''
        if self.show_terrain: #if is terrain, show tooltip
            tooltip_message = []
            coordinates = self.get_main_grid_coordinates()
            tooltip_message.append('Coordinates: (' + str(coordinates[0]) + ', ' + str(coordinates[1]) + ')')
            if self.cell.visible:
                if self.cell.terrain == 'water':
                    if coordinates[1] == 0: #current_y == 0:
                        tooltip_message.append('This is an ocean water tile')
                    else:
                        tooltip_message.append('This is a river water tile')
                else:
                    tooltip_message.append('This is ' + utility.generate_article(self.cell.terrain) + ' ' + self.cell.terrain + ' tile')
                if not self.cell.village == 'none': #if village present, show village
                    tooltip_message += self.cell.village.get_tooltip()
                elif not self.cell.resource == 'none': #if not village but other resource present, show resource
                    tooltip_message.append('This tile has ' + utility.generate_article(self.cell.resource) + ' ' + self.cell.resource + ' resource')
            else:
                tooltip_message .append('This tile has not been explored')
            if not self.global_manager.get('current_lore_mission') == 'none':
                if self.global_manager.get('current_lore_mission').has_revealed_possible_artifact_location(coordinates[0], coordinates[1]):
                    tooltip_message.append('There are rumors that the ' + self.global_manager.get('current_lore_mission').name + ' may be found here')
            self.set_tooltip(tooltip_message)
        else:
            self.set_tooltip([])

    def set_coordinates(self, x, y):
        '''
        Description:
            Sets this tile's grid coordinates to the inputted values
        Input:
            int x: new grid x coordinate
            int y: new grid y coordinate
        Output:
            None
        '''
        self.x = x
        self.y = y

    def can_show_tooltip(self): #only terrain tiles have tooltips
        '''
        Description:
            Returns whether this tile's tooltip can be shown. Along with the superclass' requirements, only terrain tiles have tooltips and tiles outside of the strategic map boundaries on the minimap grid do not have tooltips
        Input:
            None
        Output:
            None
        '''
        if self.show_terrain == True:
            if self.touching_mouse() and constants.current_game_mode in self.modes: #and not targeting_ability
                if self.cell.terrain == 'none':
                    return(False)
                else:
                    return(True)
            else:
                return(False)
        else:
            return(False)

    def select(self):
        '''
        Description:
            Selects this tile and switches music based on which type of tile is selected, if the type of tile selected would change the music
        Input:
            None
        Output:
            None
        '''
        if flags.player_turn and main_loop_utility.action_possible(self.global_manager): #(not flags.choosing_destination):
            if self.name == 'Slave traders' and constants.slave_traders_strength > 0:
                if constants.sound_manager.previous_state != 'slave traders':
                    constants.event_manager.clear()
                    constants.sound_manager.play_random_music('slave traders')
            elif self.cell.village != 'none' and self.cell.visible and self.cell.village.population > 0 and not self.cell.has_intact_building('port'):
                new_state = 'village ' + self.cell.village.get_aggressiveness_adjective()
                if constants.sound_manager.previous_state != new_state: #village_peaceful/neutral/aggressive
                    constants.event_manager.clear()
                    constants.sound_manager.play_random_music(new_state)
            else:
                if constants.sound_manager.previous_state != 'europe':
                    constants.event_manager.clear()
                    constants.sound_manager.play_random_music('europe')

class abstract_tile(tile):
    '''
    tile for 1-cell abstract grids like Europe, can have a tooltip but has no terrain, instead having a unique image
    '''
    def __init__(self, from_save, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'grid': grid value - grid in which this tile can appear
                'image': string value - File path to the image used by this object
                'name': string value - This tile's name
                'modes': string list value - Game modes during which this actor's images can appear
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['coordinates'] = (0, 0)
        input_dict['show_terrain'] = False
        super().__init__(from_save, input_dict, global_manager)

    def update_tooltip(self):
        '''
        Description:
            Sets this tile's tooltip to what it should be whenever the player looks at the tooltip. An abstract tile's tooltip is its name
        Input:
            None
        Output:
            None
        '''
        if self.name == 'Slave traders':
            self.set_tooltip([self.name, 'Slave traders strength: ' + str(constants.slave_traders_strength)])
        else:
            self.set_tooltip([self.name])

    def can_show_tooltip(self):
        '''
        Description:
            Returns whether this tile's tooltip can be shown. Has default tooltip requirements of being visible and touching the mosue
        Input:
            None
        Output:
            None
        '''
        if self.touching_mouse() and constants.current_game_mode in self.modes:
            return(True)
        else:
            return(False)
