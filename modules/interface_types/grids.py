#Contains functionality for grids

import random
import pygame
import itertools
import json
from . import cells, interface_elements
from ..util import actor_utility, utility
import modules.constants.constants as constants
import modules.constants.status as status
import modules.constants.flags as flags

class grid(interface_elements.interface_element):
    '''
    Grid of cells of the same size with different positions based on the grid's size and the number of cells. Each cell contains various actors, terrain, and resources
    '''
    def __init__(self, from_save, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of the bottom left corner of this grid
                'width': int value - Pixel width of this grid
                'height': int value - Pixel height of this grid
                'coordinate_width': int value - Number of columns in this grid
                'coordinate_height': int value - Number of rows in this grid
                'internal_line_color': string value - Color in the color_dict dictionary for lines between cells, like 'bright blue'
                'external_line_color': string value - Color in the color_dict dictionary for lines on the outside of the grid, like 'bright blue'
                'list modes': string list value - Game modes during which this grid can appear
                'strategic_grid': boolean value - True if this grid is the primary strategic map of the game, False if it is a different grid, like the minimap or the Europe grid
                'grid_line_width': int value - Pixel width of lines between cells. Lines on the outside of the grid are one pixel thicker
                'cell_list': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each cell in this grid
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(input_dict, global_manager)
        status.grid_list.append(self)
        self.grid_line_width = input_dict['grid_line_width']
        self.from_save = from_save
        self.is_mini_grid = False
        self.is_abstract_grid = False
        self.attached_grid = 'none'
        self.modes = input_dict['modes']
        self.coordinate_width = input_dict['coordinate_width']
        self.coordinate_height = input_dict['coordinate_height']
        self.internal_line_color = input_dict['internal_line_color']
        self.external_line_color = input_dict['external_line_color']
        self.mini_grid = 'none'
        self.cell_list = [[None] * self.coordinate_height for y in range(self.coordinate_width)]
        #printed list would be inverted - each row corresponds to an x value and each column corresponds to a y value, but can be indexed by cell_list[x][y]
        if not from_save: #terrain created after grid initialization by create_strategic_map in game_transitions
            self.create_cells()
        else:
            self.load_cells(input_dict['cell_list'])

    def to_save_dict(self):
        '''
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
                'grid_type': string value - String matching the global manager key of this grid, used to initialize the correct type of grid on loading
                'cell_list': dictionary list value - list of dictionaries of saved information necessary to recreate each cell in this grid
        '''
        save_dict = {}
        if status.strategic_map_grid == self:
            save_dict['grid_type'] = 'strategic_map_grid'
        else:
            save_dict['grid_type'] = 'default'
        save_dict['cell_list'] = [current_cell.to_save_dict() for current_cell in self.get_flat_cell_list()]
        return(save_dict)

    def generate_terrain(self):
        '''
        Description:
            Randomly creates the strategic map with biomes, rivers, and bottom row of ocean, but without resources - resources require that tiles and the mini grid are set
                up first, which occurs later in setup than grid initialization
        Input:
            None
        Output:
            None
        '''
        area = self.coordinate_width * self.coordinate_height
        num_worms = area // 5
        if constants.effect_manager.effect_active('enable_oceans'):
            constants.terrain_list.append('water')
        for i in range(num_worms):
            self.make_random_terrain_worm(round(area/24), round(area/12), constants.terrain_list)
        #if constants.effect_manager.effect_active('enable_oceans'):
        #    for i in range(num_worms // 6): #range(num_worms / 3):
        #        self.make_random_terrain_worm(round(area/24), round(area/12), ['water'])
        if not constants.effect_manager.effect_active('enable_oceans'):
            for row in self.cell_list:
                terrain_variant = random.randrange(0, constants.terrain_variant_dict['ocean_water'])
                row[0].set_terrain('water', terrain_variant)
            num_rivers = random.randrange(2, 4)
            valid = False
            while not valid:
                valid = True
                start_x_list = []
                for i in range(num_rivers):
                    start_x_list.append(random.randrange(0, self.coordinate_width))
                for index in range(len(start_x_list)):
                    for other_index in range(len(start_x_list)):
                        if index != other_index and abs(start_x_list[index] - start_x_list[other_index]) < 3:
                            valid = False
        
            for start_x in start_x_list:
                self.make_random_river_worm(round(self.coordinate_height * 0.75), round(self.coordinate_height * 1.25), start_x)

    def draw(self):
        '''
        Description:
            Draws each cell of this grid
        Input:
            None
        Output:
            None
        '''
        for cell in self.get_flat_cell_list():
            cell.draw()
        self.draw_grid_lines()

    def draw_grid_lines(self):
        '''
        Description:
            Draws lines between grid cells and on the outside of the grid. Also draws an outline of the area on this grid covered by this grid's minimap grid, if applicable
        Input:
            None
        Output:
            None
        '''
        if not constants.effect_manager.effect_active('hide_grid_lines'):
            for x in range(0, self.coordinate_width+1):
                pygame.draw.line(constants.game_display, constants.color_dict[self.internal_line_color], self.convert_coordinates((x, 0)), self.convert_coordinates((x, self.coordinate_height)), self.grid_line_width)
            for y in range(0, self.coordinate_height+1):
                pygame.draw.line(constants.game_display, constants.color_dict[self.internal_line_color], self.convert_coordinates((0, y)), self.convert_coordinates((self.coordinate_width, y)), self.grid_line_width)                     
        pygame.draw.line(constants.game_display, constants.color_dict[self.external_line_color], self.convert_coordinates((0, 0)), self.convert_coordinates((0, self.coordinate_height)), self.grid_line_width + 1)
        pygame.draw.line(constants.game_display, constants.color_dict[self.external_line_color], self.convert_coordinates((self.coordinate_width, 0)), self.convert_coordinates((self.coordinate_width, self.coordinate_height)), self.grid_line_width + 1)
        pygame.draw.line(constants.game_display, constants.color_dict[self.external_line_color], self.convert_coordinates((0, 0)), self.convert_coordinates((self.coordinate_width, 0)), self.grid_line_width + 1)
        pygame.draw.line(constants.game_display, constants.color_dict[self.external_line_color], self.convert_coordinates((0, self.coordinate_height)), self.convert_coordinates((self.coordinate_width, self.coordinate_height)), self.grid_line_width + 1) 
        if (not self.mini_grid == 'none') and flags.show_minimap_outlines:
            mini_map_outline_color = self.mini_grid.external_line_color
            left_x = self.mini_grid.center_x - ((self.mini_grid.coordinate_width - 1) / 2)
            right_x = self.mini_grid.center_x + ((self.mini_grid.coordinate_width - 1) / 2) + 1
            down_y = self.mini_grid.center_y - ((self.mini_grid.coordinate_height - 1) / 2)
            up_y = self.mini_grid.center_y + ((self.mini_grid.coordinate_height - 1) / 2) + 1
            if right_x > self.coordinate_width:
                right_x = self.coordinate_width
            if left_x < 0:
                left_x = 0
            if up_y > self.coordinate_height:
                up_y = self.coordinate_height
            if down_y < 0:
                down_y = 0
            pygame.draw.line(constants.game_display, constants.color_dict[mini_map_outline_color], self.convert_coordinates((left_x, down_y)), self.convert_coordinates((left_x, up_y)), self.grid_line_width + 1)
            pygame.draw.line(constants.game_display, constants.color_dict[mini_map_outline_color], self.convert_coordinates((left_x, up_y)), self.convert_coordinates((right_x, up_y)), self.grid_line_width + 1)
            pygame.draw.line(constants.game_display, constants.color_dict[mini_map_outline_color], self.convert_coordinates((right_x, up_y)), self.convert_coordinates((right_x, down_y)), self.grid_line_width + 1)
            pygame.draw.line(constants.game_display, constants.color_dict[mini_map_outline_color], self.convert_coordinates((right_x, down_y)), self.convert_coordinates((left_x, down_y)), self.grid_line_width + 1)

    def find_cell_center(self, coordinates):
        '''
        Description:
            Returns the pixel coordinates of the center of this grid's cell that occupies the inputted grid coordinates
        Input:
            int tuple coordinates: Two values representing x and y grid coordinates of the cell whose center is found
        Output:
            int tuple: Two values representing x and y pixel coordinates of the center of the requested cell
        '''
        x, y = coordinates
        return((int((self.width/(self.coordinate_width)) * x) + self.x + int(self.get_cell_width()/2)), (constants.display_height - (int((self.height/(self.coordinate_height)) * y) + self.y + int(self.get_cell_height()/2))))

    def convert_coordinates(self, coordinates):
        '''
        Description:
            Returns the pixel coordinates of the bottom left corner of this grid's cell that occupies the inputted grid coordinates
        Input:
            int tuple coordinates: Two values representing x and y grid coordinates of the cell whose corner is found
        Output:
            int tuple: Two values representing x and y pixel coordinates of the bottom left corner of the requested cell
        '''
        x, y = coordinates
        return((int((self.width/(self.coordinate_width)) * x) + self.x), (constants.display_height - (int((self.height/(self.coordinate_height)) * y) + self.y )))
    
    def get_height(self):
        '''
        Description:
            Returns how many rows this grid has
        Input:
            None
        Output:
            int: Number of rows this grid has
        '''
        return(self.coordinate_height)
    
    def get_width(self):
        '''
        Description:
            Returns how many columns this grid has
        Input:
            None
        Output:
            int: Number of columns this grid has
        '''
        return(self.coordinate_width)
    
    def get_cell_width(self):
        '''
        Description:
            Returns the pixel width of one of this grid's cells
        Input:
            None
        Output:
            int: Pixel width of one of this grid's cells
        '''
        return(int(self.width/self.coordinate_width) + 1)

    def get_cell_height(self):
        '''
        Description:
            Returns the pixel height of one of this grid's cells
        Input:
            None
        Output:
            int: Pixel height of one of this grid's cells
        '''
        return(int(self.height/self.coordinate_height) + 1)

    def find_cell(self, x, y):
        '''
        Description:
            Returns this grid's cell that occupies the inputted coordinates
        Input:
            int x: x coordinate for the grid location of the requested cell
            int y: y coordinate for the grid location of the requested cell
        Output:
            None/cell: Returns this grid's cell that occupies the inputted coordinates, or None if there are no cells at the inputted coordinates
        '''
        if x >= 0 and x < self.coordinate_width and y >= 0 and y < self.coordinate_height:
            return(self.cell_list[x][y])
        else:
            return(None)

    def choose_cell(self, requirements_dict):
        '''
        Description:
            Uses a series of requirements to choose and a return a random cell in this grid that fits those requirements
        Input:
            dictionary choice_info_dict: String keys corresponding to various values such as 'allowed_terrains', 'ocean_allowed', and 'nearby_buildings_allowed' to use as requirements for the chosen cell
        Output:
            cell: Returns a random cell in this grid that fits the inputted requirements
        '''
        allowed_terrains = requirements_dict['allowed_terrains']
        ocean_allowed = requirements_dict['ocean_allowed']
        nearby_buildings_allowed = requirements_dict['nearby_buildings_allowed']
        possible_cells = []
        for current_cell in self.get_flat_cell_list():
            if not current_cell.terrain in allowed_terrains:
                continue
            if (not ocean_allowed) and current_cell.y == 0:
                continue
            if (not nearby_buildings_allowed) and current_cell.adjacent_to_buildings():
                continue
            possible_cells.append(current_cell)
        if len(possible_cells) == 0:
            possible_cells.append('none')
        return(random.choice(possible_cells))
        
            
    def create_cells(self):
        '''
        Description:
            Creates a cell for each of this grid's coordinates
        Input:
            None
        Output:
            None
        '''
        for x in range(len(self.cell_list)):
            for y in range(len(self.cell_list[x])):
                self.create_cell(x, y)
        for current_cell in self.get_flat_cell_list():
            current_cell.find_adjacent_cells()

    def get_flat_cell_list(self):
        '''
        Description:
            Generates and returns a flattened version of this grid's 2-dimensional cell list
        Input:
            None
        Output:
            cell list: Returns a flattened version of this grid's 2-dimensional cell list
        '''
        return(itertools.chain.from_iterable(self.cell_list))

    def load_cells(self, cell_list):
        '''
        Description:
            Creates this grid's cells with correct resources and terrain based on the inputted saved information
        Input:
            dictionary list cell_list: list of dictionaries of saved information necessary to recreate each cell in this grid
        Output:
            None
        '''
        for current_cell_dict in cell_list:
            x, y = current_cell_dict['coordinates']
            self.create_cell(x, y, save_dict=current_cell_dict)
        for current_cell in self.get_flat_cell_list():
            current_cell.find_adjacent_cells()
            current_cell.set_terrain(current_cell.save_dict['terrain'])
            
    def create_cell(self, x, y, save_dict='none'):
        '''
        Description:
            Creates a cell at the inputted coordinates
        Input:
            int x: x coordinate at which to create a cell
            int y: y coordinate at which to create a cell
        Output:
            cell: Returns created cell
        '''
        return(cells.cell(x, y, self.get_cell_width(), self.get_cell_height(), self, constants.color_dict['bright green'], save_dict, self.global_manager))

    def create_resource_list_dict(self):
        '''
        Description:
            Creates and returns dictionary containing entries for each terrain type with the frequency of each resource type in that terrain
        Input:
            None
        Output:
            dictionary: Returns a dictionary in the format
                {'clear': [('none', 140), ('diamond', 142)]}
                for resource_frequencies.json {'clear': {'none': 140, 'diamond': 2}}
        '''
        file = open('configuration/resource_frequencies.json')
        resource_frequencies = json.load(file)
        resource_list_dict = {}
        for current_terrain in resource_frequencies:
            resource_list_dict[current_terrain] = []
            total_frequency = 0
            for current_resource in resource_frequencies[current_terrain]:
                total_frequency += resource_frequencies[current_terrain][current_resource]
                resource_list_dict[current_terrain].append((current_resource, total_frequency))
        file.close()
        return(resource_list_dict)

    def set_resources(self):
        '''
        Description:
            Spawns a random resource, village, or lack thereof in each of this grid's cells
        Input:
            None
        Output:
            None
        '''
        if self.from_save:
            for cell in self.get_flat_cell_list():
                cell.set_resource(cell.save_dict['resource'])
        else:
            resource_list_dict = self.create_resource_list_dict()
            for cell in self.get_flat_cell_list():
                terrain_number = random.randrange(resource_list_dict[cell.terrain][-1][1]) #number between 0 and terrain's max frequency
                set_resource = False
                for current_resource in resource_list_dict[cell.terrain]: #if random number falls in resource's frequency range for that terrain, set cell to that resource
                    if (not set_resource) and terrain_number < current_resource[1]:
                        cell.set_resource(current_resource[0])
                        break
            
    def make_random_terrain_worm(self, min_len, max_len, possible_terrains):
        '''
        Description:
            Chooses a random terrain from the inputted list and fills a random length chain of adjacent grid cells with the chosen terrain. Can go to the same cell multiple times
        Input:
            int min_len: minimum number of cells whose terrain can be changed
            int max_len: maximum number of cells whose terrain can be changed, inclusive
            string list possible_terrains: list of all terrain types that could randomly spawn, like 'swamp'
        Output:
            None
        '''
        start_x = random.randrange(0, self.coordinate_width)
        start_y = random.randrange(0, self.coordinate_height)
        current_x = start_x
        current_y = start_y
        worm_length = random.randrange(min_len, max_len + 1)
        terrain = random.choice(possible_terrains)
        terrain_variant = random.randrange(0, constants.terrain_variant_dict[terrain]) #randomly choose from number of terrain variants, if 2 variants then pick 0 or 1
        self.find_cell(current_x, current_y).set_terrain(terrain, terrain_variant)
        counter = 0        
        while not counter == worm_length:           
            counter = counter + 1
            direction = random.randrange(1, 5) #1 north, 2 east, 3 south, 4 west
            if not (((current_x == self.coordinate_width - 1) and direction == 2) or ((current_x == 0) and direction == 4) or ((current_y == self.coordinate_height - 1) and direction == 3) or ((current_y == 0) and direction == 1)):
                if direction == 3:
                    current_y = current_y + 1
                elif direction == 2:
                    current_x = current_x + 1
                elif direction == 1:
                    current_y = current_y - 1
                elif direction == 4:
                    current_x = current_x - 1
                terrain_variant = random.randrange(0, constants.terrain_variant_dict[terrain]) #randomly choose from number of terrain variants, if 2 variants then pick 0 or 1
                self.find_cell(current_x, current_y).set_terrain(terrain, terrain_variant)
                
    def make_random_river_worm(self, min_len, max_len, start_x):
        '''
        Description:
            Fills a random length chain of adjacent grid cells with water, starting at an inputted location. Weighted to generally move toward the top of the grid, away from the coast. Can go to the same cell multiple times
        Input:
            int min_len: minimum number of cells whose terrain can be changed
            int max_len: maximum number of cells whose terrain can be changed, inclusive
            int start_x: x coordinate at which to start the water chain. Always starts with a y location of 1
        Output:
            None
        '''
        start_y = 1
        current_x = start_x
        current_y = start_y
        worm_length = random.randrange(min_len, max_len + 1)
        terrain = 'water'
        water_type = 'water'
        if current_y == 0:
            water_type = 'ocean_water'
        else:
            water_type = 'river_water'
        #self.find_cell(current_x, current_y).set_terrain(terrain)
        terrain_variant = random.randrange(0, constants.terrain_variant_dict[water_type]) #randomly choose from number of terrain variants, if 2 variants then pick 0 or 1
        self.find_cell(current_x, current_y).set_terrain(terrain, terrain_variant)
        #self.find_cell(current_x, current_y).set_terrain(terrain)
        counter = 0        
        while not counter == worm_length:           
            counter = counter + 1
            direction = random.randrange(1, 7) #1 3 5 6 north, 2 east, 4 west
            if direction == 1 or direction == 5 or direction == 6:
                direction = 3 #turns extras and south to north
            if not (((current_x == self.coordinate_width - 1) and direction == 2) or ((current_x == 0) and direction == 4) or ((current_y == self.coordinate_height - 1) and direction == 3) or ((current_y == 0) and direction == 1)):
                if direction == 3:
                    current_y = current_y + 1
                elif direction == 2:
                    current_x = current_x + 1
                elif direction == 4:
                    current_x = current_x - 1
                water_type = 'water'
                if current_y == 0:
                    water_type = 'ocean_water'
                else:
                    water_type = 'river_water'
                #self.find_cell(current_x, current_y).set_terrain(terrain)
                terrain_variant = random.randrange(0, constants.terrain_variant_dict[water_type]) #randomly choose from number of terrain variants, if 2 variants then pick 0 or 1
                self.find_cell(current_x, current_y).set_terrain(terrain, terrain_variant)

    def touching_mouse(self):
        '''
        Description:
            Returns whether this grid is colliding with the mouse
        Input:
            None
        Output:
            boolean: Returns True if this grid is colliding with the mouse, otherwise returns False
        '''
        if self.Rect.collidepoint(pygame.mouse.get_pos()):
            return(True)
        else:
            return(False)

    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this grid can be shown. By default, it can be shown during game modes in which this grid can appear
        Input:
            None
        Output:
            boolean: Returns True if this grid can appear during the current game mode, otherwise returns False
        '''
        return(constants.current_game_mode in self.modes)

    def can_draw(self):
        '''
        Description:
            Calculates and returns whether it would be valid to call this object's draw()
        Input:
            None
        Output:
            boolean: Returns whether it would be valid to call this object's draw()
        '''
        return(self.showing)

    def remove(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program
        Input:
            None
        Output:
            None
        '''
        super().remove()
        status.grid_list = utility.remove_from_list(status.grid_list, self)
        
class mini_grid(grid):
    '''
    Grid that zooms in on a small area of a larger attached grid, centered on a certain cell of the attached grid. Which cell is being centered on can be changed
    '''
    def __init__(self, from_save, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of the bottom left corner of this grid
                'width': int value - Pixel width of this grid
                'height': int value - Pixel height of this grid
                'coordinate_width': int value - Number of columns in this grid
                'coordinate_height': int value - Number of rows in this grid
                'internal_line_color': string value - Color in the color_dict dictionary for lines between cells, like 'bright blue'
                'external_line_color': string value - Color in the color_dict dictionary for lines on the outside of the grid, like 'bright blue'
                'list modes': string list value - Game modes during which this grid can appear
                'attached_grid': grid value - grid to which this grid is attached
                'grid_line_width': int value - Pixel width of lines between cells. Lines on the outside of the grid are one pixel thicker
                'cell_list': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each cell in this grid
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['strategic_grid'] = False
        super().__init__(from_save, input_dict, global_manager)
        self.is_mini_grid = True
        self.attached_grid = input_dict['attached_grid']
        self.attached_grid.mini_grid = self
        self.center_x = 0
        self.center_y = 0

    def calibrate(self, center_x, center_y):
        '''
        Description:
            Centers this mini grid on the cell at the inputted coordinates of the attached grid, moving any displayed actors, terrain, and resources on this grid to their new locations as needed
        Input:
            int center_x: x coordinate on the attached grid to center on
            int center_y: y coordinate on the attached grid to center on
        Output:
            None
        '''
        if constants.current_game_mode in self.modes:
            self.center_x = center_x
            self.center_y = center_y
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display'), self.attached_grid.find_cell(self.center_x, self.center_y).tile) #calibrate tile display information to centered tile
            for current_cell in self.get_flat_cell_list():
                attached_x, attached_y = self.get_main_grid_coordinates(current_cell.x, current_cell.y)
                if attached_x >= 0 and attached_y >= 0 and attached_x < self.attached_grid.coordinate_width and attached_y < self.attached_grid.coordinate_height:
                    attached_cell = self.attached_grid.find_cell(attached_x, attached_y)
                    current_cell.copy(attached_cell)
                else: #if the current cell is beyond the boundaries of the attached grid, show an empty cell
                    current_cell.contained_mobs = []
                    current_cell.set_visibility(True, update_image_bundle=False)
                    current_cell.set_terrain('none', update_image_bundle=False)
                    current_cell.set_resource('none', update_image_bundle=False)
                    current_cell.reset_buildings()
                    current_cell.tile.update_image_bundle()
            for current_mob in status.mob_list:
                if current_mob.images[0].current_cell != 'none':
                    for current_image in current_mob.images:
                        if current_image.grid == self:
                            current_image.add_to_cell()

    def get_main_grid_coordinates(self, mini_x, mini_y):
        '''
        Description:
            Converts the inputted coordinates on this grid to the corresponding coordinates on the attached grid, returning the converted coordinates
        Input:
            int mini_x: x coordinate on this grid
            int mini_y: y coordinate on this grid
        Output:
            int: x coordinate of the attached grid corresponding to the inputted x coordinate
            int: y coordinate of the attached grid corresponding to the inputted y coordinate
        '''
        attached_x = self.center_x + mini_x - round((self.coordinate_width - 1) / 2) #if width is 5, ((5 - 1) / 2) = (4 / 2) = 2, since 2 is the center of a 5 width grid starting at 0
        attached_y = self.center_y + mini_y - round((self.coordinate_height - 1) / 2)
        return(attached_x, attached_y)
            
    def get_mini_grid_coordinates(self, original_x, original_y):
        '''
        Description:
            Converts the inputted coordinates on the attached grid to the corresponding coordinates on this grid, returning the converted coordinates
        Input:
            int mini_x: x coordinate on the attached grid
            int mini_y: y coordinate on the attached grid
        Output:
            int: x coordinate of this grid corresponding to the inputted x coordinate
            int: y coordinate of this grid corresponding to the inputted y coordinate
        '''
        return(int(original_x - self.center_x + (round(self.coordinate_width - 1) / 2)), int(original_y - self.center_y + round((self.coordinate_height - 1) / 2)))

    def is_on_mini_grid(self, original_x, original_y):
        '''
        Description:
            Returns whether the inputted attached grid coordinates are within the boundaries of this grid
        Input:
            int original_x: x coordinate on the attached grid
            int original_y: y coordinate on the attached grid
        Output:
            boolean: Returns True if the inputted attache grid coordinates are within the boundaries of this grid, otherwise returns False
        '''
        minimap_x = original_x - self.center_x + (round(self.coordinate_width - 1) / 2)
        minimap_y = original_y - self.center_y + (round(self.coordinate_height - 1) / 2)
        if(minimap_x >= 0 and minimap_x < self.coordinate_width and minimap_y >= 0 and minimap_y < self.coordinate_height):
            return(True)
        else:
            return(False)

    def draw_grid_lines(self):
        '''
        Description:
            Draws lines between grid cells and on the outside of the grid
        Input:
            None
        Output:
            None
        '''
        lower_left_corner = self.get_mini_grid_coordinates(0, 0)
        upper_right_corner = self.get_mini_grid_coordinates(self.attached_grid.coordinate_width - 1, self.attached_grid.coordinate_height)
        if lower_left_corner[0] < 0: #left
            left_x = 0
        else:
            left_x = lower_left_corner[0]
        if lower_left_corner[1] < 0: #down
            down_y = 0
        else:
            down_y = lower_left_corner[1]
        if upper_right_corner[0] >= self.coordinate_width: #right
            right_x = self.coordinate_width
        else:
            right_x = upper_right_corner[0] + 1
        if upper_right_corner[1] > self.coordinate_height: #up
            up_y = self.coordinate_height
        else:
            up_y = upper_right_corner[1]
        if not constants.effect_manager.effect_active('hide_grid_lines'):
                
            for x in range(0, self.coordinate_width+1):
                pygame.draw.line(constants.game_display, constants.color_dict[self.internal_line_color], self.convert_coordinates((x, 0)), self.convert_coordinates((x, self.coordinate_height)),
                                self.grid_line_width)

            for y in range(0, self.coordinate_height+1):
                pygame.draw.line(constants.game_display, constants.color_dict[self.internal_line_color], self.convert_coordinates((0, y)), self.convert_coordinates((self.coordinate_width, y)),
                                self.grid_line_width) 
        
        for y in range(0, self.coordinate_height+1):                    
            pygame.draw.line(constants.game_display, constants.color_dict[self.external_line_color], self.convert_coordinates((left_x, down_y)), self.convert_coordinates((left_x, up_y)),
                            self.grid_line_width + 1)

        pygame.draw.line(constants.game_display, constants.color_dict[self.external_line_color], self.convert_coordinates((left_x, up_y)), self.convert_coordinates((right_x, up_y)),
                        self.grid_line_width + 1)

        pygame.draw.line(constants.game_display, constants.color_dict[self.external_line_color], self.convert_coordinates((right_x, up_y)), self.convert_coordinates((right_x, down_y)),
                        self.grid_line_width + 1)

        pygame.draw.line(constants.game_display, constants.color_dict[self.external_line_color], self.convert_coordinates((right_x, down_y)), self.convert_coordinates((left_x, down_y)),
                        self.grid_line_width + 1) 

class abstract_grid(grid):
    '''
    1-cell grid that is not directly connected to the primary strategic grid but can be moved to by mobs from the strategic grid and vice versa
    '''
    def __init__(self, from_save, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of the bottom left corner of this grid
                'width': int value - Pixel width of this grid
                'height': int value - Pixel height of this grid
                'internal_line_color': string value - Color in the color_dict dictionary for lines between cells, like 'bright blue'
                'external_line_color': string value - Color in the color_dict dictionary for lines on the outside of the grid, like 'bright blue'
                'list modes': string list value - Game modes during which this grid can appear
                'grid_line_width': int value - Pixel width of lines between cells. Lines on the outside of the grid are one pixel thicker
                'cell_list': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each cell in this grid
                'tile_image_id': File path to the image used by this grid's tile
                'name': Name of this grid
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['coordinate_width'] = 1
        input_dict['coordinate_height'] = 1
        input_dict['strategic_grid'] = False
        super().__init__(from_save, input_dict, global_manager)
        self.is_abstract_grid = True
        self.name = input_dict['name']
        self.tile_image_id = input_dict['tile_image_id']
        self.cell_list[0][0].set_visibility(True)

    def to_save_dict(self):
        '''
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
                'grid_type': string value - String matching the global manager key of this grid, used to initialize the correct type of grid on loading
                'cell_list': dictionary list value - list of dictionaries of saved information necessary to recreate each cell in this grid
        '''
        save_dict = super().to_save_dict()
        if status.europe_grid == self:
            save_dict['grid_type'] = 'europe_grid'
        elif status.slave_traders_grid == self:
            save_dict['grid_type'] = 'slave_traders_grid'
        else:
            save_dict['grid_type'] = 'default'
        return(save_dict)
