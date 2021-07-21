import pygame

class cell():
    def __init__(self, x, y, width, height, grid, color, global_manager):
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
        self.occupied = False
        self.grid.cell_list.append(self)
        self.adjacent_list = [] #list of 4 nearby cells, used for movement
        self.diagonal_adjacent_list = [] #list of 8 nearby cells, used for melee attacks of opportunity
        self.tile = 'none'
        self.resource = 'none'
        self.terrain = 'none'
        self.set_terrain('clear')
        self.set_visibility(False)
        #self.set_visibility(True)

    def set_visibility(self, new_visibility):
        self.visible = new_visibility
        if not self.tile == 'none':
            self.tile.set_visibility(new_visibility)
    
    def set_resource(self, new_resource):
        self.resource = new_resource
        self.tile.set_resource(new_resource)

    def set_terrain(self, new_terrain):
        self.terrain = new_terrain
        if (not self.tile == 'none'):# and self.tile.show_terrain:
            self.tile.set_terrain(new_terrain)
        self.color = self.global_manager.get('terrain_colors')[new_terrain]
            
    def draw(self):
        current_color = self.color
        red = current_color[0]
        green = current_color[1]
        blue = current_color[2]
        pygame.draw.rect(self.global_manager.get('game_display'), (red, green, blue), self.Rect)
        
    def find_adjacent_cells(self):
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
