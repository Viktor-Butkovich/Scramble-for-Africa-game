import pygame
import time
from . import utility
from . import drawing_tools
from . import text_tools

class free_image():
    def __init__(self, image_id, coordinates, width, height, modes, global_manager):
        self.global_manager = global_manager
        self.modes = modes
        self.width = width
        self.height = height
        self.set_image(image_id)
        self.x, self.y = coordinates
        self.y = self.global_manager.get('display_height') - self.y
        self.global_manager.get('image_list').append(self)
        
    def draw(self):
        if self.global_manager.get('current_game_mode') in self.modes:
            drawing_tools.display_image(self.image, self.x, self.y - self.height, self.global_manager)

    def remove(self):
        self.global_manager.get('image_list').remove(self)

    def set_image(self, new_image):
        self.image_id = new_image
        self.image = pygame.image.load('graphics/' + self.image_id)
        self.image = pygame.transform.scale(self.image, (self.width, self.height))

class loading_image_class(free_image):
    def __init__(self, image_id, global_manager):
        super().__init__(image_id, (0, 0), global_manager.get('display_width'), global_manager.get('display_height'), [], global_manager)
        self.global_manager.set('image_list', utility.remove_from_list(self.global_manager.get('image_list'), self))

    def draw(self):
        drawing_tools.display_image(self.image, self.x, self.y - self.height, self.global_manager)

class actor_image():
    def __init__(self, actor, width, height, grid, image_description, global_manager):
        self.global_manager = global_manager
        self.last_image_switch = 0
        self.previous_idle_image = 'default'
        self.actor = actor
        self.modes = actor.modes
        self.width = width
        self.height = height
        self.set_image(image_description)
        self.image_description == image_description
        self.global_manager.get('image_list').append(self)
        self.grid = grid
        self.Rect = pygame.Rect(self.actor.x, self.actor.y - self.height, self.width, self.height) #(left, top, width, height), bottom left on coordinates
        self.outline_width = 3#2
        self.outline = pygame.Rect(self.actor.x - self.outline_width, self.global_manager.get('display_height') - (self.actor.y + self.height + self.outline_width), self.width + (2 * self.outline_width), self.height + (self.outline_width * 2))
        self.x, self.y = self.grid.convert_coordinates((self.actor.x, self.actor.y))

    def get_center_coordinates(self):
        cell_width = self.grid.get_cell_width()
        cell_height = self.grid.get_cell_height()
        return((self.x + round(cell_width / 2), display_height -(self.y + round(cell_height / 2))))
        
    def set_image(self, new_image_description):
        self.last_image_switch = time.time()
        if new_image_description == 'default' or new_image_description == 'right' or new_image_description == 'left':
            self.previous_idle_image = new_image_description
        self.image_description = new_image_description
        self.image_id = self.actor.image_dict[new_image_description]
        try: #use if there are any image path issues to help with file troubleshooting
            self.image = pygame.image.load('graphics/' + self.image_id)
        except:
            print('graphics/' + self.image_id)
            self.image = pygame.image.load('graphics/' + self.image_id)
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        
    def draw(self):
        if self.grid.is_mini_grid: #if on minimap and within its smaller range of coordinates, convert actor's coordinates to minimap coordinates and draw image there
            if(self.grid.is_on_mini_grid(self.actor.x, self.actor.y)):
                self.grid_x, self.grid_y = self.grid.get_mini_grid_coordinates(self.actor.x, self.actor.y)
                self.go_to_cell((self.grid_x, self.grid_y))
                drawing_tools.display_image(self.image, self.x, self.y - self.height, self.global_manager)
        else:
            self.grid_x = self.actor.x
            self.grid_y = self.actor.y
            self.go_to_cell((self.grid_x, self.grid_y))
            drawing_tools.display_image(self.image, self.x, self.y - self.height, self.global_manager)
        #if self.actor.selected:
        #    pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')['light gray'], (self.outline), self.outline_width)
        #if show_selected:
        #    if self.actor.selected:
        #        pygame.draw.rect(game_display, color_dict['light gray'], (self.outline), self.outline_width)
        #    elif self.actor.targeted:
        #        pygame.draw.rect(game_display, color_dict['red'], (self.outline), self.outline_width)
        
    def go_to_cell(self, coordinates):
        self.x, self.y = self.grid.convert_coordinates(coordinates)
        self.Rect.x = self.x
        self.Rect.y = self.y - self.height
        self.outline.x = self.x - self.outline_width
        self.outline.y = self.y - (self.height + self.outline_width)
                
    def set_tooltip(self, tooltip_text):
        self.tooltip_text = tooltip_text
        tooltip_width = 50
        for text_line in tooltip_text:
            if text_tools.message_width(text_line, self.global_manager.get('font_size'), 'Times New Roman') + 10 > tooltip_width:
                tooltip_width = text_tools.message_width(text_line, self.global_manager.get('font_size'), 'Times New Roman') + 10
        tooltip_height = (self.global_manager.get('font_size') * len(tooltip_text)) + 5
        self.tooltip_box = pygame.Rect(self.actor.x, self.actor.y, tooltip_width, tooltip_height)   
        self.tooltip_outline_width = 1
        self.tooltip_outline = pygame.Rect(self.actor.x - self.tooltip_outline_width, self.actor.y + self.tooltip_outline_width, tooltip_width + (2 * self.tooltip_outline_width), tooltip_height + (self.tooltip_outline_width * 2))

class button_image(actor_image):
    def __init__(self, button, width, height, image_id, global_manager):
        self.global_manager = global_manager
        self.button = button
        self.width = width
        self.height = height
        self.x = self.button.x
        self.y = self.global_manager.get('display_height') - (self.button.y + self.height) - self.height
        self.last_image_switch = 0
        self.modes = button.modes
        self.image_id = image_id
        self.set_image(image_id)
        self.global_manager.get('image_list').append(self)
        #self.grid = grid
        self.Rect = self.button.Rect
        self.outline_width = 2
        self.outline = pygame.Rect(self.x - self.outline_width, self.global_manager.get('display_height') - (self.y + self.height + self.outline_width), self.width + (2 * self.outline_width), self.height + (self.outline_width * 2))

    def update_state(self, new_x, new_y, new_width, new_height):
        self.Rect = self.button.Rect
        self.outline.x = new_x - self.outline_width
        self.outline.y = display_height - (new_y + new_height + self.outline_width)
        self.outline.width = new_width + (2 * self.outline_width)
        self.outline.height = new_height + (self.outline_width * 2)
        self.set_image(self.image_id)
        
    def set_image(self, new_image_id):
        self.image_id = new_image_id
        try:
            self.image = pygame.image.load('graphics/' + self.image_id)#.convert()
        except:
            print('graphics/' + self.image_id)
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        
    def draw(self):
        if self.global_manager.get('current_game_mode') in self.button.modes:
            self.x = self.button.x
            self.y = self.global_manager.get('display_height') - (self.button.y + self.height) + self.height
            drawing_tools.display_image(self.image, self.x, self.y - self.height, self.global_manager)
        
    def draw_tooltip(self): #button has tooltip already, so image doesn't need a new tooltip
        i = 0
        
    def set_tooltip(self, tooltip_text):
        i = 0

class tile_image(actor_image):
    def __init__(self, actor, width, height, grid, image_description, global_manager):
        super().__init__(actor, width, height, grid, image_description, global_manager)
        self.grid_x = self.actor.x
        self.grid_y = self.actor.y
        self.go_to_cell((self.grid_x, self.grid_y))

    def go_to_cell(self, coordinates):
        self.x, self.y = self.grid.convert_coordinates(coordinates)
        self.Rect.x = self.x
        self.Rect.y = self.y - self.height
        self.outline.x = self.x - self.outline_width
        self.outline.y = self.y - (self.height + self.outline_width)
        
    def draw(self):
        self.grid_x = self.actor.x
        self.grid_y = self.actor.y
        self.go_to_cell((self.grid_x, self.grid_y))
        drawing_tools.display_image(self.image, self.x, self.y - self.height, self.global_manager)
