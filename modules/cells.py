#Contains functionality for grid cells

import pygame
from . import actor_utility

class cell():
    '''
    Object representing one cell of a grid corresponding to one of its coordinates, able to contain terrain, resources, mobs, and tiles
    '''
    def __init__(self, x, y, width, height, grid, color, save_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int x: the x coordinate of this cell in its grid
            int y: the y coordinate of this cell in its grid
            int width: Pixel width of this button
            int height: Pixel height of this button
            grid grid: The grid that this cell is attached to
            string color: Color in the color_dict dictionary for this cell when nothing is covering it
            string or dictionary save_dict: Equals 'none' if creating new grid, equals dictionary of saved information necessary to recreate this cell if loading grid
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.global_manager = global_manager
        self.move_priority = 99
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.grid = grid
        self.color = color
        self.pixel_x, self.pixel_y = self.grid.convert_coordinates((self.x, self.y))
        self.Rect = pygame.Rect(self.pixel_x, self.pixel_y - self.height, self.width, self.height) #(left, top, width, height)
        self.corners = [(self.Rect.left, self.Rect.top ), (self.Rect.left + self.Rect.width, self.Rect.top), (self.Rect.left, self.Rect.top - self.Rect.height), (self.Rect.left + self.Rect.width, self.Rect.top - self.Rect.height)]
        self.grid.cell_list.append(self)
        self.tile = 'none'
        self.resource = 'none'
        self.village = 'none'
        self.terrain = 'none'
        self.set_terrain('clear')
        self.contained_mobs = []
        self.reset_buildings()
        self.adjacent_cells = {'up': 'none', 'down': 'none', 'right': 'none', 'left': 'none'}        
        if not save_dict == 'none':
            self.save_dict = save_dict
            self.set_visibility(save_dict['visible'])
        else:
            self.set_visibility(False)

    def to_save_dict(self):
        '''
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
                'coordinates': int tuple value - Two values representing x and y coordinates on one of the game grids
                'visible': boolean value - Whether this cell is visible or not
                'terrain': string value - Terrain type of this cell and its tile, like 'swamp'
                'resource': string value - Resource type of this cell and its tile, like 'exotic wood'
                'inventory': string/string dictionary value - Version of the inventory dictionary of this cell's tile only containing commodity types with 1+ units held
                'village_name': Only saved if resource is natives, name of this cell's village
                'village_population': Only saved if resource is natives, population of this cell's village
                'village_aggressiveness': Only saved if resource is natives, aggressiveness of this cell's village
                'village_available_workers': Only saved if resource is natives, how many workers this cell's village has
        '''
        save_dict = {}
        save_dict['coordinates'] = (self.x, self.y)
        save_dict['visible'] = self.visible
        save_dict['terrain'] = self.terrain
        save_dict['resource'] = self.resource

        saved_inventory = {}
        if self.tile.can_hold_commodities: #only save inventory if not empty
            for current_commodity in self.global_manager.get('commodity_types'):
               if self.tile.inventory[current_commodity] > 0:
                   saved_inventory[current_commodity] = self.tile.inventory[current_commodity]
        save_dict['inventory'] = saved_inventory
        
        if self.resource == 'natives':
            save_dict['village_name'] = self.village.name
            save_dict['village_population'] = self.village.population
            save_dict['village_aggressiveness'] = self.village.aggressiveness
            save_dict['village_available_workers'] = self.village.available_workers
            save_dict['village_attached_warriors'] = []
            for attached_warrior in self.village.attached_warriors:
                save_dict['village_attached_warriors'].append(attached_warrior.to_save_dict)
        return(save_dict)

    def has_village(self):
        '''
        Description:
            Returns whether this cell contains a village
        Input:
            None
        Output:
            boolean: Returns False if this cell does not contain a village, otherwise returns True
        '''
        if self.village == 'none':
            return(False)
        return(True)

    def has_trading_post(self):
        '''
        Description:
            Returns whether this cell contains a trading post
        Input:
            None
        Output:
            boolean: Returns False if this cell does not contain a trading post, otherwise returns True
        '''
        if self.contained_buildings['trading_post'] == 'none':
            return(False)
        return(True)

    def has_mission(self):
        '''
        Description:
            Returns whether this cell contains a mission
        Input:
            None
        Output:
            boolean: Returns False if this cell does not contain a mission, otherwise returns True
        '''
        if self.contained_buildings['mission'] == 'none':
            return(False)
        return(True)

    def has_road(self):
        '''
        Description:
            Returns whether this cell contains a road
        Input:
            None
        Output:
            boolean: Returns True if this cell contains a road, otherwise returns False
        '''
        if self.contained_buildings['infrastructure'] == 'none':
            return(False)
        if self.contained_buildings['infrastructure'].is_road:
            return(True)
        return(False)

    def has_railroad(self):
        '''
        Description:
            Returns whether this cell contains a railroad
        Input:
            None
        Output:
            boolean: Returns True if this cell contains a railroad, otherwise returns False
        '''
        if self.contained_buildings['infrastructure'] == 'none':
            return(False)
        if self.contained_buildings['infrastructure'].is_railroad:
            return(True)
        return(False)

    def reset_buildings(self):
        '''
        Description:
            Resets the values of this cell's dictionary of contained buildings to 'none', initializing the dictionary or removing existing buildings
        Input:
            None
        Output:
            None
        '''
        self.contained_buildings = {}
        for current_building_type in self.global_manager.get('building_types'):
            self.contained_buildings[current_building_type] = 'none'

    def get_buildings(self):
        '''
        Description:
            Returns a list of the buildings contained in this cell
        Input:
            None
        Output:
            building list contained_buildings_list: buildings contained in this cell
        '''
        contained_buildings_list = []
        for current_building_type in self.global_manager.get('building_types'):
            if not self.contained_buildings[current_building_type] == 'none':
                contained_buildings_list.append(self.contained_buildings[current_building_type])
        return(contained_buildings_list)
        

    def has_port(self):
        '''
        Description:
            Returns whether this cell contains a port
        Input:
            None
        Output:
            boolean: Returns False if this cell does not contain a port, otherwise returns True
        '''
        if self.contained_buildings['port'] == 'none':
            return(False)
        return(True)

    def has_slums(self):
        '''
        Description:
            Returns whether this cell contains slums
        Input:
            None
        Output:
            boolean: Returns False if this cell does not contain slums, otherwise returns True
        '''
        if self.contained_buildings['slums'] == 'none':
            return(False)
        return(True)

    def create_slums(self):
        '''
        Description:
            Creates an empty slums building when a worker migrates to this cell, if there is not already one present
        Input:
            None
        Outptu:
            None
        '''
        input_dict = {}
        input_dict['coordinates'] = (self.x, self.y)
        input_dict['grids'] = [self.grid, self.grid.mini_grid]
        input_dict['name'] = 'slums'
        input_dict['modes'] = ['strategic']
        input_dict['init_type'] = 'slums'
        #input_dict['image'] = 'buildings/slums.png'
        self.global_manager.get('actor_creation_manager').create(False, input_dict, self.global_manager)
        if self.tile == self.global_manager.get('displayed_tile'):
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), self.tile) #update tile display to show new building

    def has_vehicle(self, vehicle_type):
        '''
        Description:
            Returns whether this cell contains a crewed vehicle of the inputted type
        Input:
            string vehicle_type: 'train' or 'ship', determines what kind of vehicle is searched for
        Output:
            boolean: Returns True if this cell contains a crewed vehicle of the inputted type, otherwise returns False
        '''
        for current_mob in self.contained_mobs:
            if current_mob.is_vehicle and current_mob.has_crew and current_mob.vehicle_type == vehicle_type:
                return(True)
        return(False)

    def get_vehicle(self, vehicle_type):
        '''
        Description:
            Returns the first crewed vehicle of the inputted type in this cell, or 'none' if none are present
        Input:
            string vehicle_type: 'train' or 'ship', determines what kind of vehicle is searched for
        Output:
            string/vehicle: Returns the first crewed vehicle of the inputted type in this cell, or 'none' if none are present
        '''
        for current_mob in self.contained_mobs:
            if current_mob.is_vehicle and current_mob.has_crew and current_mob.vehicle_type == vehicle_type:
                return(current_mob)
        return('none')

    def has_uncrewed_vehicle(self, vehicle_type):
        '''
        Description:
            Returns whether this cell contains an uncrewed vehicle of the inputted type
        Input:
            string vehicle_type: 'train' or 'ship', determines what kind of vehicle is searched for
        Output:
            boolean: Returns True if this cell contains an uncrewed vehicle of the inputted type, otherwise returns False
        '''
        for current_mob in self.contained_mobs:
            if current_mob.is_vehicle and (not current_mob.has_crew) and current_mob.vehicle_type == vehicle_type:
                return(True)
        return(False)

    def get_uncrewed_vehicle(self, vehicle_type):
        '''
        Description:
            Returns the first uncrewed vehicle of the inputted type in this cell, or 'none' if none are present
        Input:
            string vehicle_type: 'train' or 'ship', determines what kind of vehicle is searched for
        Output:
            string/vehicle: Returns the first uncrewed vehicle of the inputted type in this cell, or 'none' if none are present
        '''
        for current_mob in self.contained_mobs:
            if current_mob.is_vehicle and (not current_mob.has_crew) and current_mob.vehicle_type == vehicle_type:
                return(current_mob)
        return('none')

    def has_worker(self):
        '''
        Description:
            Returns whether this cell contains a worker
        Input:
            None
        Output:
            Returns True if this cell contains a worker, otherwise returns False
        '''
        for current_mob in self.contained_mobs:
            if current_mob in self.global_manager.get('worker_list') and not current_mob.is_church_volunteers:
                return(True)
        return(False)

    def get_worker(self):
        '''
        Description:
            Returns the first worker in this cell, or 'none' if none are present. Does not inclue church volunteers
        Input:
            None
        Output:
            string/worker: Returns the first worker in this cell, or 'none' if none are present
        '''
        for current_mob in self.contained_mobs:
            if current_mob in self.global_manager.get('worker_list') and not current_mob.is_church_volunteers:
                return(current_mob)
        return('none')

    def get_church_volunteers(self):
        '''
        Description:
            Returns the first church volunteer in this cell, or 'none' if none are present
        Input:
            None
        Output:
            string/church_volunteers: Returns the first church volunteer in this cell, or 'none' if none are present
        '''
        for current_mob in self.contained_mobs:
            if current_mob in self.global_manager.get('worker_list') and current_mob.is_church_volunteers:
                return(current_mob)
        return('none')

    def set_visibility(self, new_visibility):
        '''
        Description:
            Sets the visibility of this cell and its attached tile to the inputted value. A visible cell's terrain and resource can be seen by the player.
        Input:
            boolean new_visibility: This cell's new visibility status
        Output:
            None
        '''
        self.visible = new_visibility
        if not self.tile == 'none':
            self.tile.set_visibility(new_visibility)
    
    def set_resource(self, new_resource):
        '''
        Description:
            Sets the resource type of this cell and its attached tile to the inputted value
        Input:
            string new_resource: The new resource type of this cell and its attached tile, like 'exotic wood'
        Output:
            None
        '''
        self.resource = new_resource
        self.tile.set_resource(new_resource)

    def set_terrain(self, new_terrain):
        '''
        Description:
            Sets the terrain type of this cell and its attached tile to the inputted value
        Input:
            string new_terrain: The new terrain type of this cell and its attached tile, like 'swamp'
        Output:
            None
        '''
        self.terrain = new_terrain
        if (not self.tile == 'none'):
            self.tile.set_terrain(new_terrain)
        self.color = self.global_manager.get('terrain_colors')[new_terrain]
            
    def draw(self):
        '''
        Description:
            Draws this cell as a rectangle with a certain color on its grid, depending on this cell's color value
        Input:
            none
        Output:
            None
        '''
        current_color = self.color
        red = current_color[0]
        green = current_color[1]
        blue = current_color[2]
        pygame.draw.rect(self.global_manager.get('game_display'), (red, green, blue), self.Rect)

    def show_num_mobs(self):
        '''
        Description:
            Draws a number showing how many mobs are in this cell if it contains multiple mobs, otherwise does nothing
        Input:
            None
        Output:
            None
        '''
        length = len(self.contained_mobs)
        if length >= 2 and not self.terrain == 'none':
            message = str(length)
            color = 'white'
            font_size = round(self.width * 0.3)
            current_font = pygame.font.SysFont(self.global_manager.get('font_name'), font_size)
            textsurface = current_font.render(message, False, self.global_manager.get('color_dict')[color])
            text_x = self.pixel_x + self.width - (font_size * 0.5)
            text_y = self.pixel_y - font_size
            self.global_manager.get('game_display').blit(textsurface, (text_x, text_y))

    def touching_mouse(self):
        '''
        Description:
            Returns True if this cell is colliding with the mouse, otherwise returns False
        Input:
            None
        Output:
            boolean: Returns True if this cell is colliding with the mouse, otherwise returns False
        '''
        if self.Rect.collidepoint(pygame.mouse.get_pos()):
            return(True)
        else:
            return(False)

    def find_adjacent_cells(self):
        '''
        Description:
            Records a list of the cells directly adjacent to this cell. Also records these cells as values in a dictionary with string keys corresponding to their direction relative to this cell
        Input:
            None
        Output:
            None
        '''
        adjacent_list = []
        if not self.x == 0:
            adjacent_cell = self.grid.find_cell(self.x - 1, self.y)
            adjacent_list.append(adjacent_cell)
            self.adjacent_cells['left'] = adjacent_cell
        if not self.x == self.grid.coordinate_width - 1:
            adjacent_cell = self.grid.find_cell(self.x + 1, self.y)
            adjacent_list.append(adjacent_cell)
            self.adjacent_cells['right'] = adjacent_cell
        if not self.y == 0:
            adjacent_cell = self.grid.find_cell(self.x, self.y - 1)
            adjacent_list.append(adjacent_cell)
            self.adjacent_cells['down'] = adjacent_cell
        if not self.y == self.grid.coordinate_height - 1:
            adjacent_cell = self.grid.find_cell(self.x, self.y + 1)
            adjacent_list.append(adjacent_cell)
            self.adjacent_cells['up'] = adjacent_cell
        self.adjacent_list = adjacent_list

