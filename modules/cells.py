import pygame

class cell():
    '''
    Represents one cell of a grid corresponding to one of its coordinates, able to contain terrain, resources, mobs, and tiles
    '''
    def __init__(self, x, y, width, height, grid, color, global_manager):
        '''
        Input:
            x: int representing the x_coordinate of this cell in its grid
            y: int representing the y_coordinate of this cell in its grid
            width: int representing the pixel width of this cell
            height: int representing the pixel height of this cell
            grid: grid object representing the grid that this cell is part of
            color: tuple of three ints that represents the RGB color of this cell
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
        #self.occupied = False
        self.grid.cell_list.append(self)
        self.adjacent_list = [] #list of 4 nearby cells, used for movement
        self.diagonal_adjacent_list = [] #list of 8 nearby cells, used for melee attacks of opportunity
        self.tile = 'none'
        self.resource = 'none'
        self.terrain = 'none'
        self.set_terrain('clear')
        self.set_visibility(False)
        self.contained_mobs = []

    def contains_vehicle(self):
        for current_mob in self.contained_mobs:
            if current_mob.is_vehicle:
                return(True)
        return(False)

    def set_visibility(self, new_visibility):
        '''
        Input:
            boolean representing the new visibility status of this cell
        Output:
            Sets the visibility status of this cell and its attached tile, if applicable, to the inputted boolean. A visible cell's terrain and resource can be seen by the player.
        '''
        self.visible = new_visibility
        if not self.tile == 'none':
            self.tile.set_visibility(new_visibility)
    
    def set_resource(self, new_resource):
        '''
        Input:
            string representing the new resource in this cell
        Output:
            Sets the resources of this cell and its tile to the inputted string
        '''
        self.resource = new_resource
        self.tile.set_resource(new_resource)

    def set_terrain(self, new_terrain):
        '''
        Input:
            string representing the new terrain in this cell
        Output:
            Sets the terrain of this cell and its tile, if applicable, to the inputted string
        '''
        self.terrain = new_terrain
        if (not self.tile == 'none'):
            self.tile.set_terrain(new_terrain)
        self.color = self.global_manager.get('terrain_colors')[new_terrain]
            
    def draw(self):
        '''
        Input:
            none
        Output:
            Draws this cell in its place in its grid with its color attribute
        '''
        current_color = self.color
        red = current_color[0]
        green = current_color[1]
        blue = current_color[2]
        pygame.draw.rect(self.global_manager.get('game_display'), (red, green, blue), self.Rect)

    def show_num_mobs(self):
        '''
        Input:
            none
        Output:
            Does nothing if there are not at least 2 mobs in this cell. If there are at least 2 mobs in this cell, this displays the number of mobs present in the bottom right corner of the cell.
        '''
        length = len(self.contained_mobs)
        if length >= 2 and not self.terrain == 'none':
            message = str(length)
            color = 'white'
            font_size = round(self.width * 0.3)
            current_font = pygame.font.SysFont('Times New Roman', font_size)
            textsurface = current_font.render(message, False, self.global_manager.get('color_dict')[color])
            text_x = self.pixel_x + self.width - (font_size * 0.5)
            text_y = self.pixel_y - font_size
            self.global_manager.get('game_display').blit(textsurface, (text_x, text_y))
        
    def find_adjacent_cells(self):
        '''
        Input:
            none
        Output:
            Records the cells that this cell is adjacent to in its grid
        '''
        adjacent_list = []
        diagonal_adjacent_list = []
        if not self.x == 0:
            adjacent_list.append(self.grid.find_cell(self.x - 1, self.y))
            diagonal_adjacent_list.append(self.grid.find_cell(self.x - 1, self.y))
            if not self.y == 0:
                diagonal_adjacent_list.append(self.grid.find_cell(self.x - 1, self.y - 1))
            elif not self.y == self.grid.coordinate_height - 1:
                diagonal_adjacent_list.append(self.grid.find_cell(self.x - 1, self.y + 1))
        if not self.x == self.grid.coordinate_width - 1:
            adjacent_list.append(self.grid.find_cell(self.x + 1, self.y))
            diagonal_adjacent_list.append(self.grid.find_cell(self.x + 1, self.y))
            if not self.y == 0:
                diagonal_adjacent_list.append(self.grid.find_cell(self.x + 1, self.y - 1))
            elif not self.y == self.grid.coordinate_height - 1:
                diagonal_adjacent_list.append(self.grid.find_cell(self.x + 1, self.y + 1))
        if not self.y == 0:
            adjacent_list.append(self.grid.find_cell(self.x, self.y - 1))
        if not self.y == self.grid.coordinate_height - 1:
            adjacent_list.append(self.grid.find_cell(self.x, self.y + 1))
        self.diagonal_adjacent_list = diagonal_adjacent_list
        self.adjacent_list = adjacent_list

    def touching_mouse(self):
        '''
        Input:
            none
        Output:
            Returns whether this cell is colliding with the mouse
        '''
        if self.Rect.collidepoint(pygame.mouse.get_pos()):
            return(True)
        else:
            return(False)

    def has_worker(self):
        '''
        Input:
            none
        Output:
            Returns whether a worker is present in this cell
        '''
        for current_mob in self.contained_mobs:
            if current_mob in self.global_manager.get('worker_list'):
                return(True)
        return(False)

    def get_worker(self):
        '''
        Input:
            none
        Output:
            Returns the first worker present in this cell, or 'none' if no workers are present
        '''
        for current_mob in self.contained_mobs:
            if current_mob in self.global_manager.get('worker_list'):
                return(current_mob)
        return('none')
