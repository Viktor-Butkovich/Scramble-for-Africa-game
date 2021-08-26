import random
import pygame
from . import cells
from . import actor_utility

class grid():
    '''
    Grid of cells of the same size with different positions based on the grid's size and the number of cells
    '''
    def __init__(self, origin_coordinates, pixel_width, pixel_height, coordinate_width, coordinate_height, internal_line_color, external_line_color, modes, strategic_grid, grid_line_width, global_manager):
        '''
        Input:
            origin_coordinates: tuple of two int variables that represents the pixel location at which the bottom left corner of the grid is
            pixel_width: int representing the width in pixels of the grid
            pixel_height: int representing the height in pixels of the grid
            coordinate_width: int representing the width in number of cells of the grid
            coordinate_height: int representing the height in number of cells of the grid
            internal_line_color: string representing the name of the color of the lines of the grid between cells
            external_line_color: string representing the name of the color of the lines on the outside of the grid
            modes: list of strings representing the game modes in which the grid can appear
            strategic_grid: boolean representing whether this grid is the primary strategic map of the game
            grid_line_width: int representing the width in pixels of the lines of the grid between cells. The lines on the outside of the grid are one pixel thicker.
            global_manager: global_manager_template object
        '''
        self.global_manager = global_manager
        self.global_manager.get('grid_list').append(self)
        self.grid_line_width = grid_line_width
        self.is_mini_grid = False
        self.is_abstract_grid = False
        self.attached_grid = 'none'
        self.modes = modes
        self.origin_x, self.origin_y = origin_coordinates
        self.coordinate_width = coordinate_width
        self.coordinate_height = coordinate_height
        self.pixel_width = pixel_width
        self.pixel_height = pixel_height
        self.Rect = pygame.Rect(self.origin_x, self.origin_y - self.pixel_height, self.pixel_width, self.pixel_height)
        self.internal_line_color = internal_line_color
        self.external_line_color = external_line_color
        self.cell_list = []
        self.mini_grid = 'none'
        self.create_cells()
        if strategic_grid:
            area = self.coordinate_width * self.coordinate_height
            num_worms = area // 5
            for i in range(num_worms):
                self.make_random_terrain_worm(round(area/24), round(area/12), self.global_manager.get('terrain_list'))
            for cell in self.cell_list:
                if cell.y == 0:
                    cell.set_terrain('water')
            num_rivers = random.randrange(2, 4)
            valid = False
            while not valid:
                valid = True
                start_x_list = []
                for i in range(num_rivers):
                    start_x_list.append(random.randrange(0, self.coordinate_width))
                for index in range(len(start_x_list)):
                    for other_index in range(len(start_x_list)):
                        if not index == other_index:
                            if abs(start_x_list[index] - start_x_list[other_index]) < 3:
                                valid = False
            
            for start_x in start_x_list:
                self.make_random_river_worm(round(coordinate_height * 0.75), round(coordinate_height * 1.25), start_x)
                
            for cell in self.cell_list:
                if cell.y == 0 or cell.y == 1:
                    cell.set_visibility(True)
                    
    def draw(self):
        '''
        Input:
            none
        Output:
            Draws each cell of the grid
        '''
        if self.global_manager.get('current_game_mode') in self.modes:
            for cell in self.cell_list:
                cell.draw()

    def draw_grid_lines(self):
        '''
        Input:
            none
        Output:
            Draws the lines between the cells of the grid and the lines on the outside of the grid. If the grid has an attached mini_grid, the outline of the area the mini_grid covers will be shown
        '''
        if self.global_manager.get('show_grid_lines'):
            for x in range(0, self.coordinate_width+1):
                pygame.draw.line(self.global_manager.get('game_display'), self.global_manager.get('color_dict')[self.internal_line_color], self.convert_coordinates((x, 0)), self.convert_coordinates((x, self.coordinate_height)), self.grid_line_width)
            for y in range(0, self.coordinate_height+1):
                pygame.draw.line(self.global_manager.get('game_display'), self.global_manager.get('color_dict')[self.internal_line_color], self.convert_coordinates((0, y)), self.convert_coordinates((self.coordinate_width, y)), self.grid_line_width)                     
            pygame.draw.line(self.global_manager.get('game_display'), self.global_manager.get('color_dict')[self.external_line_color], self.convert_coordinates((0, 0)), self.convert_coordinates((0, self.coordinate_height)), self.grid_line_width + 1)
            pygame.draw.line(self.global_manager.get('game_display'), self.global_manager.get('color_dict')[self.external_line_color], self.convert_coordinates((self.coordinate_width, 0)), self.convert_coordinates((self.coordinate_width, self.coordinate_height)), self.grid_line_width + 1)
            pygame.draw.line(self.global_manager.get('game_display'), self.global_manager.get('color_dict')[self.external_line_color], self.convert_coordinates((0, 0)), self.convert_coordinates((self.coordinate_width, 0)), self.grid_line_width + 1)
            pygame.draw.line(self.global_manager.get('game_display'), self.global_manager.get('color_dict')[self.external_line_color], self.convert_coordinates((0, self.coordinate_height)), self.convert_coordinates((self.coordinate_width, self.coordinate_height)), self.grid_line_width + 1) 
            if (not self.mini_grid == 'none') and self.global_manager.get('show_minimap_outlines'):
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
                pygame.draw.line(self.global_manager.get('game_display'), self.global_manager.get('color_dict')[mini_map_outline_color], self.convert_coordinates((left_x, down_y)), self.convert_coordinates((left_x, up_y)), self.grid_line_width + 1)
                pygame.draw.line(self.global_manager.get('game_display'), self.global_manager.get('color_dict')[mini_map_outline_color], self.convert_coordinates((left_x, up_y)), self.convert_coordinates((right_x, up_y)), self.grid_line_width + 1)
                pygame.draw.line(self.global_manager.get('game_display'), self.global_manager.get('color_dict')[mini_map_outline_color], self.convert_coordinates((right_x, up_y)), self.convert_coordinates((right_x, down_y)), self.grid_line_width + 1)
                pygame.draw.line(self.global_manager.get('game_display'), self.global_manager.get('color_dict')[mini_map_outline_color], self.convert_coordinates((right_x, down_y)), self.convert_coordinates((left_x, down_y)), self.grid_line_width + 1)

    def find_cell_center(self, coordinates):
        '''
        Input:
            tuple of two int variables representing the grid coordinates of the cell to find the center of
        Output:
            Returns a tuple of two int variables representing the pixel coordinates at the center of the requested cell
        '''
        x, y = coordinates
        return((int((self.pixel_width/(self.coordinate_width)) * x) + self.origin_x + int(self.get_cell_width()/2)), (display_height - (int((self.pixel_height/(self.coordinate_height)) * y) + self.origin_y + int(self.get_cell_height()/2))))

    def convert_coordinates(self, coordinates):
        '''
        Input:
            tuple of two int variables representing the grid coordinates of the cell to find the center of
        Output:
            Returns a tuple of two int variables representing the pixel coordinates at the bottom left of the requested cell
        '''
        x, y = coordinates
        return((int((self.pixel_width/(self.coordinate_width)) * x) + self.origin_x), (self.global_manager.get('display_height') - (int((self.pixel_height/(self.coordinate_height)) * y) + self.origin_y )))
    
    def get_height(self):
        '''
        Input:
            none
        Output:
            Returns the number of cells in each of this grid's columns
        '''
        return(self.coordinate_height)
    
    def get_width(self):
        '''
        Input:
            none
        Output:
            Returns the number of cells in each of this grid's rows
        '''
        return(self.coordinate_width)
    
    def get_cell_width(self):
        '''
        Input:
            none
        Output:
            Returns the width in pixels of one of this grid's cells
        '''
        return(int(self.pixel_width/self.coordinate_width) + 1)

    def get_cell_height(self):
        '''
        Input:
            none
        Output:
            Returns the height in pixels of one of this grid's cells
        '''
        return(int(self.pixel_height/self.coordinate_height) + 1)

    def find_cell(self, x, y):
        '''
        Input:
            int representing the x coordinate in this grid of the cell to search for, int representing the y coordinate in this grid of the cell to search for, 
        Output:
            Returns this grid's cell object with the inputted coordinates
        '''
        for cell in self.cell_list:
            if cell.x == x and cell.y == y:
                return(cell)
        return('none')
            
    def create_cells(self):
        '''
        Input:
            none
        Output:
            Creates a cell object for each coordinate of this grid
        '''
        for x in range(0, self.coordinate_width):
            for y in range(0, self.coordinate_height):
                self.create_cell(x, y)
        for current_cell in self.cell_list:
            current_cell.find_adjacent_cells()
            
    def create_cell(self, x, y):
        '''
        Input:
            int representing the x coordinate in this grid in which to make a new cell, int representing the y coordinate in this grid in which to make a new cell
        Output:
            Creates a cell object at a location in this grid based on the inputted coordinates
        '''
        new_cell = cells.cell(x, y, self.get_cell_width(), self.get_cell_height(), self, self.global_manager.get('color_dict')['bright green'], self.global_manager)

    def make_resource_list(self, terrain):
        '''
        Input:
            string representing the type of terrain for which to make a resource list
        Output:
            Returns a list of strings of possible resource types based on the inputted terrain. The frequency of each resource in the list determines the chance of that resource appearing in a tile of the inputted resource
        '''
        resource_list = []
        if terrain == 'clear':
            for i in range(135):
                resource_list.append('none')
            for i in range(5):
                resource_list.append('ivory')
            for i in range(20):
                resource_list.append('natives')
                
        elif terrain == 'mountain':
            for i in range(135):
                resource_list.append('none')
            resource_list.append('diamond')
            for i in range(2):
                resource_list.append('gold')
            for i in range(4):
                resource_list.append('coffee')
            for i in range(4):
                resource_list.append('copper')
            for i in range(4):
                resource_list.append('iron')
            for i in range(10):
                resource_list.append('natives')
                
        elif terrain == 'hills':
            for i in range(135):
                resource_list.append('none')
            resource_list.append('diamond')
            for i in range(2):
                resource_list.append('gold')
            for i in range(4):
                resource_list.append('coffee')
            for i in range(4):
                resource_list.append('copper')
            for i in range(4):
                resource_list.append('iron')
            for i in range(10):
                resource_list.append('natives')
        elif terrain == 'jungle':
            for i in range(125):
                resource_list.append('none')
            resource_list.append('diamond')
            for i in range(6):
                resource_list.append('rubber')
            resource_list.append('coffee')
            for i in range(6):
                resource_list.append('exotic wood')
            for i in range(6):
                resource_list.append('fruit')
            for i in range(15):
                resource_list.append('natives')
        elif terrain == 'swamp':
            for i in range(130):
                resource_list.append('none')
            for i in range(4):
                resource_list.append('ivory')
            for i in range(4):
                resource_list.append('rubber')
            resource_list.append('coffee')
            for i in range(4):
                resource_list.append('exotic wood')
            for i in range(2):
                resource_list.append('fruit')
            for i in range(15):
                resource_list.append('natives')
        elif terrain == 'desert':
            for i in range(140):
                resource_list.append('none')
            for i in range(2):
                resource_list.append('diamond')
            resource_list.append('gold')
            resource_list.append('ivory')
            for i in range(2):
                resource_list.append('fruit')
            for i in range(2):
                resource_list.append('copper')
            for i in range(2):
                resource_list.append('iron')
            for i in range(10):
                resource_list.append('natives')
        else:
            resource_list.append('none')
        return(resource_list)

    def set_resources(self):
        '''
        Input:
            none
        Output:
            Assigns a resource to each cell in this grid, depending on each cell's terrain
        '''
        resource_list_dict = {}
        for terrain in self.global_manager.get('terrain_list'):
            resource_list_dict[terrain] = self.make_resource_list(terrain)
        resource_list_dict['water'] = self.make_resource_list('water')
        for cell in self.cell_list:
            cell.set_resource(random.choice(resource_list_dict[cell.terrain]))
            
    def make_random_terrain_worm(self, min_len, max_len, possible_terrains):
        '''
        Input:
            int representing the minimum length of a terrain worm, int representing the maximum length of a terrain worm, list of string representing the types of terrain the terrain worm can spread
        Output:
            Chooses a random terrain from the inputted possible terrains and assigns a random connected string of cells in this grid of a length between the minimum and maximum lengths to the chosen terrain
        '''
        start_x = random.randrange(0, self.coordinate_width)
        start_y = random.randrange(0, self.coordinate_height)
        current_x = start_x
        current_y = start_y
        worm_length = random.randrange(min_len, max_len + 1)
        terrain = random.choice(possible_terrains)
        self.find_cell(current_x, current_y).set_terrain(terrain)
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
                self.find_cell(current_x, current_y).set_terrain(terrain)
                
    def make_random_river_worm(self, min_len, max_len, start_x):
        '''
        Input:
            int representing the minimum length of a terrain worm, int representing the maximum length of a terrain worm
        Output:
            Assigns a random connected string of cells in this grid of a length between the minimum and maximum lengths to the water terrain.
            These strings will start at the coast and be more likely to move inland than to the sides and will be more likely to move to the sides than towards the coast.
        '''
        start_y = 1
        current_x = start_x
        current_y = start_y
        worm_length = random.randrange(min_len, max_len + 1)
        terrain = 'water'
        self.find_cell(current_x, current_y).set_terrain(terrain)
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
                self.find_cell(current_x, current_y).set_terrain(terrain)

    def touching_mouse(self):
        '''
        Input:
            none
        Output:
            Returns whether this grid is colliding with the mouse
        '''
        if self.Rect.collidepoint(pygame.mouse.get_pos()):
            return(True)
        else:
            return(False)

    def can_show(self):
        if self.global_manager.get('current_game_mode') in self.modes:
            return(True)
        else:
            return(False)

class mini_grid(grid):
    '''
    Grid that zooms in on a small area of a larger attached grid, centered on a certain cell in the attached grid that can be moved
    '''
    def __init__(self, origin_coordinates, pixel_width, pixel_height, coordinate_width, coordinate_height, internal_line_color, external_line_color, modes, attached_grid, grid_line_width, global_manager):
        '''
        Input:
            Same as superclass except:
            attached_grid: grid object to which this grid is attached
            Can not be the primary strategic_grid, unlike superclass
        '''
        super().__init__(origin_coordinates, pixel_width, pixel_height, coordinate_width, coordinate_height, internal_line_color, external_line_color, modes, False, grid_line_width, global_manager)
        self.is_mini_grid = True
        self.attached_grid = attached_grid
        self.attached_grid.mini_grid = self
        self.center_x = 0
        self.center_y = 0

    def calibrate(self, center_x, center_y):
        '''
        Input:
            int representing the x coordinate of the attached grid to center on, int representing the y coordinate of the attached grid to center on
        Output:
            Centers this mini grid on the inputted coordinates of the attached grid
        '''
        if self.global_manager.get('current_game_mode') in self.modes:
            for current_exploration_mark in self.global_manager.get('exploration_mark_list'):
                if self in current_exploration_mark.grids:
                    current_exploration_mark.main_x, current_exploration_mark.main_y = self.get_main_grid_coordinates(current_exploration_mark.x, current_exploration_mark.y)
            self.center_x = center_x
            self.center_y = center_y
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), self.attached_grid.find_cell(self.center_x, self.center_y).tile) #calibrate tile display information to centered tile
            for current_cell in self.cell_list:
                attached_x, attached_y = self.get_main_grid_coordinates(current_cell.x, current_cell.y)
                if attached_x >= 0 and attached_y >= 0 and attached_x < self.attached_grid.coordinate_width and attached_y < self.attached_grid.coordinate_height:
                    attached_cell = self.attached_grid.find_cell(attached_x, attached_y)
                    current_cell.set_visibility(attached_cell.visible)
                    current_cell.set_terrain(attached_cell.terrain)
                    current_cell.set_resource(attached_cell.resource)
                    current_cell.contained_mobs = attached_cell.contained_mobs
                    current_cell.contained_buildings = attached_cell.contained_buildings
                else: #if off-map
                    current_cell.set_visibility(True)
                    current_cell.set_terrain('none')
                    current_cell.set_resource('none')
                    current_cell.reset_buildings()
            self.Rect = pygame.Rect(self.origin_x, self.origin_y - self.pixel_height, self.pixel_width, self.pixel_height)
            for current_mob in self.global_manager.get('mob_list'):
                if not (current_mob.in_group or current_mob.in_vehicle or current_mob.in_building): #if not ((current_mob in self.global_manager.get('officer_list') or current_mob in self.global_manager.get('worker_list')) and current_mob.in_group):
                    for current_image in current_mob.images:
                        if current_image.grid == self:
                            current_image.add_to_cell()
        if self.global_manager.get('current_game_mode') in self.modes:
            for current_exploration_mark in self.global_manager.get('exploration_mark_list'):
                if self in current_exploration_mark.grids:
                    current_exploration_mark.x, current_exploration_mark.y = self.get_mini_grid_coordinates(current_exploration_mark.main_x, current_exploration_mark.main_y)

    def get_main_grid_coordinates(self, mini_x, mini_y):
        '''
        Input:
            int representing an x coordinate on this mini grid, int representing a y coordinate on this mini grid
        Output:
            Returns an int representing the corresponding x_coordinate of the attached grid and an int representing the corresponding y_coordinate of the attached grid
        '''
        attached_x = self.center_x + mini_x - round((self.coordinate_width - 1) / 2) #if width is 5, ((5 - 1) / 2) = (4 / 2) = 2, since 2 is the center of a 5 width grid starting at 0
        attached_y = self.center_y + mini_y - round((self.coordinate_height - 1) / 2)
        return(attached_x, attached_y)
            
    def get_mini_grid_coordinates(self, original_x, original_y):
        '''
        Input:
            int representing an x coordinate on the attached grid, int representing a y coordinate on the attached grid
        Output:
            Returns an int representing the corresponding x_coordinate of this mini grid and an int representing the corresponding y_coordinate of this mini grid
        '''
        return(original_x - self.center_x + (round(self.coordinate_width - 1) / 2), original_y - self.center_y + round((self.coordinate_height - 1) / 2))

    def is_on_mini_grid(self, original_x, original_y):
        '''
        Input:
            int representing an x coordinate on the attached grid, int representing a y coordinate on the attached grid
        Output:
            Returns whether the inputted attached grid coordinates are in the area covered by this mini grid
        '''
        minimap_x = original_x - self.center_x + (round(self.coordinate_width - 1) / 2)
        minimap_y = original_y - self.center_y + (round(self.coordinate_height - 1) / 2)
        if(minimap_x >= 0 and minimap_x < self.coordinate_width and minimap_y >= 0 and minimap_y < self.coordinate_height):
            return(True)
        else:
            return(False)

    def draw_grid_lines(self):
        '''
        Input:
            none
        Output:
            Draws the lines between the cells of the grid and the lines on the outside of the grid
        '''
        if self.global_manager.get('show_grid_lines'):
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
                
            for x in range(0, self.coordinate_width+1):
                pygame.draw.line(self.global_manager.get('game_display'), self.global_manager.get('color_dict')[self.internal_line_color], self.convert_coordinates((x, 0)), self.convert_coordinates((x, self.coordinate_height)),
                                 self.grid_line_width)

            for y in range(0, self.coordinate_height+1):
                pygame.draw.line(self.global_manager.get('game_display'), self.global_manager.get('color_dict')[self.internal_line_color], self.convert_coordinates((0, y)), self.convert_coordinates((self.coordinate_width, y)),
                                 self.grid_line_width)                     
                pygame.draw.line(self.global_manager.get('game_display'), self.global_manager.get('color_dict')[self.external_line_color], self.convert_coordinates((left_x, down_y)), self.convert_coordinates((left_x, up_y)),
                                 self.grid_line_width + 1)

            pygame.draw.line(self.global_manager.get('game_display'), self.global_manager.get('color_dict')[self.external_line_color], self.convert_coordinates((left_x, up_y)), self.convert_coordinates((right_x, up_y)),
                             self.grid_line_width + 1)

            pygame.draw.line(self.global_manager.get('game_display'), self.global_manager.get('color_dict')[self.external_line_color], self.convert_coordinates((right_x, up_y)), self.convert_coordinates((right_x, down_y)),
                             self.grid_line_width + 1)

            pygame.draw.line(self.global_manager.get('game_display'), self.global_manager.get('color_dict')[self.external_line_color], self.convert_coordinates((right_x, down_y)), self.convert_coordinates((left_x, down_y)),
                             self.grid_line_width + 1) 

class abstract_grid(grid):
    '''
    1-cell grid that is not directly connected to the primary strategic grid
    '''
    def __init__(self, origin_coordinates, pixel_width, pixel_height, internal_line_color, external_line_color, modes, grid_line_width, tile_image_id, name, global_manager):
        '''
        Input:
            origin_coordinates: tuple of two int variables that represents the pixel location at which the bottom left corner of the grid is
            pixel_width: int representing the width in pixels of the grid
            pixel_height: int representing the height in pixels of the grid
            internal_line_color: string representing the name of the color of the lines of the grid between cells
            external_line_color: string representing the name of the color of the lines on the outside of the grid
            modes: list of strings representing the game modes in which the grid can appear
            grid_line_width: int representing the width in pixels of the lines of the grid between cells. The lines on the outside of the grid are one pixel thicker.
            name: string representing the name of this grid
            global_manager: global_manager_template object
        '''
        super().__init__(origin_coordinates, pixel_width, pixel_height, 1, 1, internal_line_color, external_line_color, modes, False, grid_line_width, global_manager)
        self.is_abstract_grid = True
        self.name = name
        self.global_manager.get('abstract_grid_list').append(self)
        self.tile_image_id = tile_image_id
        self.cell_list[0].set_visibility(True)

