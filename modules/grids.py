import random
import pygame
from . import cells

class grid():
    def __init__(self, origin_coordinates, pixel_width, pixel_height, coordinate_width, coordinate_height, color, modes, global_manager):
        self.global_manager = global_manager
        self.global_manager.get('grid_list').append(self)
        self.modes = modes
        self.origin_x, self.origin_y = origin_coordinates
        self.coordinate_width = coordinate_width
        self.coordinate_height = coordinate_height
        self.pixel_width = pixel_width
        self.pixel_height = pixel_height
        self.color = color
        self.cell_list = []
        self.create_cells()
        if self.modes == ['strategic']:
            area = self.coordinate_width * self.coordinate_height
            num_worms = area // 5
            for i in range(num_worms):
                self.make_random_terrain_worm(round(area/24), round(area/12), self.global_manager.get('terrain_list')) #sand['mountain', 'grass', 'forest']
            for cell in self.cell_list:
                if cell.y == 0:
                    cell.set_terrain('water')
            num_rivers = random.randrange(2, 4)#2-3
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
                #self.make_random_river_worm(10, 21, start_x)
            for cell in self.cell_list:
                if cell.y == 0 or cell.y == 1:
                    cell.set_visibility(True)
                
    def draw(self):
        if self.global_manager.get('current_game_mode') in self.modes:
            for cell in self.cell_list:
                cell.draw()

    def draw_grid_lines(self):
        if self.global_manager.get('show_grid_lines'):
            for x in range(0, self.coordinate_width+1):
                pygame.draw.line(self.global_manager.get('game_display'), self.global_manager.get('color_dict')['black'], self.convert_coordinates((x, 0)), self.convert_coordinates((x, self.coordinate_height)))
            for y in range(0, self.coordinate_height+1):
                pygame.draw.line(self.global_manager.get('game_display'), self.global_manager.get('color_dict')['black'], self.convert_coordinates((0, y)), self.convert_coordinates((self.coordinate_width, y)))                     



    def find_cell_center(self, coordinates):
        '''converts grid coordinates to pixel coordinates at center of cell'''
        x, y = coordinates
        return((int((self.pixel_width/(self.coordinate_width)) * x) + self.origin_x + int(self.get_cell_width()/2)), (display_height - (int((self.pixel_height/(self.coordinate_height)) * y) + self.origin_y + int(self.get_cell_height()/2))))

    def convert_coordinates(self, coordinates):
        '''converts grid coordinates to pixel coordinates'''
        x, y = coordinates
        return((int((self.pixel_width/(self.coordinate_width)) * x) + self.origin_x), (self.global_manager.get('display_height') - (int((self.pixel_height/(self.coordinate_height)) * y) + self.origin_y )))
    
    def get_height(self):
        return(self.coordinate_height)
    
    def get_width(self):
        return(self.coordinate_width)
    
    def get_cell_width(self):
        return(int(self.pixel_width/self.coordinate_width) + 1)

    def get_cell_height(self):
        return(int(self.pixel_height/self.coordinate_height) + 1)

    def find_cell(self, x, y):
        for cell in self.cell_list:
            if cell.x == x and cell.y == y:
                return(cell)
            
    def create_cells(self):
        for x in range(0, self.coordinate_width):
            for y in range(0, self.coordinate_height):
                self.create_cell(x, y, self)
        for current_cell in self.cell_list:
            current_cell.find_adjacent_cells()
                
    def create_cell(self, x, y, grid):
        new_cell = cells.cell(x, y, self.get_cell_width(), self.get_cell_height(), self, self.color, self.global_manager)
        
    def is_clear(self, x, y):
        if self.find_cell(x, y).occupied == False:
            return(True)
        else:
            return(False)

    def make_resource_list(self, terrain):
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
            resource_list.append('diamonds')
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
            resource_list.append('diamonds')
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
            resource_list.append('diamonds')
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
                resource_list.append('diamonds')
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
        #terrain_list = ['clear', 'mountain', 'hills', 'jungle', 'swamp', 'desert']
        #clear_resources = make_resource_list('clear')
        #mountain_resources = make_resource_list('mountain')
        #hills_resources = make_resource_list('hills')
        #jungle_resources = make_resource_list('jungle')
        #swamp_resources = make_resource_list('desert')
        #water_resources = make_resource_list('water')
        #resource_list_dict = {'clear': clear_resources, 'mountain': mountain_resources, 'hills': hills_resources, 'jungle': jungle_resources, 'swamp': swamp_resources, 'desert': desert_resources, 'water': water_resources}
        resource_list_dict = {}
        for terrain in self.global_manager.get('terrain_list'):
            resource_list_dict[terrain] = self.make_resource_list(terrain)
        resource_list_dict['water'] = self.make_resource_list('water')
        for cell in self.cell_list:
            cell.set_resource(random.choice(resource_list_dict[cell.terrain]))
            
    def make_random_terrain_worm(self, min_len, max_len, possible_terrains):
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
            direction = random.randrange(1, 5) #1 north 2 east 3 south 4 west
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
        #start_x = random.randrange(0, self.coordinate_width)
        start_y = 1 #random.randrange(0, self.coordinate_height)
        current_x = start_x
        current_y = start_y
        worm_length = random.randrange(min_len, max_len + 1)
        terrain = 'water' #random.choice(possible_terrains)
        self.find_cell(current_x, current_y).set_terrain(terrain)
        counter = 0        
        while not counter == worm_length:           
            counter = counter + 1
            direction = random.randrange(1, 7) #1 north 2 east 3 south 4 west
            if direction == 1 or direction == 5 or direction == 6:
                direction = 3 #turns extras and south to north
            if not (((current_x == self.coordinate_width - 1) and direction == 2) or ((current_x == 0) and direction == 4) or ((current_y == self.coordinate_height - 1) and direction == 3) or ((current_y == 0) and direction == 1)):
                if direction == 3: #or direction == 1:
                    current_y = current_y + 1
                elif direction == 2:
                    current_x = current_x + 1
                #if direction == 1:
                #   current_y = current_y - 1
                elif direction == 4:
                    current_x = current_x - 1
                self.find_cell(current_x, current_y).set_terrain(terrain)
    '''            
    def make_coordinate_terrain_worm(self, start_x, start_y, min_len, max_len, possible_terrains):
        current_x = start_x
        current_y = start_y
        worm_length = random.randrange(min_len, max_len + 1)
        terrain = random.choice(possible_terrains)
        self.find_cell(current_x, current_y).set_terrain(terrain)
        counter = 0        
        while not counter == worm_length:           
            counter = counter + 1
            direction = random.randrange(1, 5)
            if not (((current_x == self.coordinate_width - 1) and direction == 2) or ((current_x == 0) and direction == 4) or ((current_y == self.coordinate_height - 1) and direction == 3) or ((current_y == 0) and direction == 1)):
                if direction == 3:
                    current_y = current_y + 1
                if direction == 2:
                    current_x = current_x + 1
                if direction == 1:
                   current_y = current_y - 1
                if direction == 4:
                    current_x = current_x - 1
                self.find_cell(current_x, current_y).set_terrain(terrain)
                
    def make_coordinate_river_worm(self, start_x, start_y, min_len, max_len):
        current_x = start_x
        current_y = start_y
        worm_length = random.randrange(min_len, max_len + 1)
        terrain = 'water' #random.choice(possible_terrains)
        self.find_cell(current_x, current_y).set_terrain(terrain)
        counter = 0        
        while not counter == worm_length:           
            counter = counter + 1
            direction = random.randrange(1, 5)
            if not (((current_x == self.coordinate_width - 1) and direction == 2) or ((current_x == 0) and direction == 4) or ((current_y == self.coordinate_height - 1) and direction == 3) or ((current_y == 0) and direction == 1)):
                if direction == 3 or direction == 1:
                    current_y = current_y + 1
                if direction == 2:
                    current_x = current_x + 1
                #if direction == 1:
                #   current_y = current_y - 1
                if direction == 4:
                    current_x = current_x - 1
                self.find_cell(current_x, current_y).set_terrain(terrain)
'''
