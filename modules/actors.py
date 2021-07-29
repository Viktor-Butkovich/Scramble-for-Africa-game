import pygame
from . import text_tools
from . import utility

class actor():
    def __init__(self, coordinates, grids, modes, global_manager):
        self.global_manager = global_manager
        global_manager.get('actor_list').append(self)
        self.modes = modes
        self.grids = grids
        self.grid = grids[0]
        self.x, self.y = coordinates
        self.name = ''
        self.set_name('placeholder')
        self.set_coordinates(self.x, self.y)
        #self.controllable = False# obsolete but possibly usable later
        self.selected = False
    
    def set_name(self, new_name):
        self.name = new_name        
       
    #def is_clear(self, x, y):
    #    return self.grid.is_clear(x, y)
    
    def set_coordinates(self, x, y):
        #if self.is_clear(x, y):
        #self.grid.find_cell(self.x, self.y).occupied = False
        self.x = x
        self.y = y
        #self.grid.find_cell(self.x, self.y).occupied = True
        #else:#elif able_to_print:
        #    text_tools.print_to_screen('This cell is blocked.', self.global_manager)
            
    def set_tooltip(self, new_tooltip):
        for current_image in self.images:
            current_image.set_tooltip(new_tooltip)
    
    def update_tooltip(self):
        self.set_tooltip([self.name])
        
    def remove(self):
        self.global_manager.set('actor_list', utility.remove_from_list(self.global_manager.get('actor_list'), self))
        for current_image in self.images:
            self.global_manager.set('image_list', utility.remove_from_list(self.global_manager.get('image_list'), current_image))

    def interact(self, other):
        if other == None:
            text_tools.print_to_screen(self.name + ' has nothing to interact with.')
        else:
            text_tools.print_to_screen(self.name + ' is interacting with ' + other.name)

    def touching_mouse(self):
        for current_image in self.images:
            if current_image.Rect.collidepoint(pygame.mouse.get_pos()): #if mouse is in image
                return(True)
        return(False) #return false if none touch mouse

    def can_show_tooltip(self): #moved to actor
        if self.touching_mouse() and self.global_manager.get('current_game_mode') in self.modes: #and not targeting_ability 
            return(True)
        else:
            return(False)

    def draw_tooltip(self, y_displacement):
        self.update_tooltip()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        tooltip_image = self.images[0]
        for current_image in self.images: #only draw tooltip from the image that the mouse is touching
            if current_image.Rect.collidepoint((mouse_x, mouse_y)):
                tooltip_image = current_image
        mouse_y += y_displacement
        if (mouse_x + tooltip_image.tooltip_box.width) > self.global_manager.get('display_width'):
            mouse_x = self.global_manager.get('display_width') - tooltip_image.tooltip_box.width
        if (self.global_manager.get('display_height') - mouse_y) - (len(tooltip_image.tooltip_text) * self.global_manager.get('font_size') + 5 + tooltip_image.tooltip_outline_width) < 0:
            mouse_y = self.global_manager.get('display_height') - tooltip_image.tooltip_box.height
        tooltip_image.tooltip_box.x = mouse_x
        tooltip_image.tooltip_box.y = mouse_y
        tooltip_image.tooltip_outline.x = tooltip_image.tooltip_box.x - tooltip_image.tooltip_outline_width
        tooltip_image.tooltip_outline.y = tooltip_image.tooltip_box.y - tooltip_image.tooltip_outline_width
        pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')['black'], tooltip_image.tooltip_outline)
        pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')['white'], tooltip_image.tooltip_box)
        for text_line_index in range(len(tooltip_image.tooltip_text)):
            text_line = tooltip_image.tooltip_text[text_line_index]
            self.global_manager.get('game_display').blit(text_tools.text(text_line, self.global_manager.get('myfont'), self.global_manager), (tooltip_image.tooltip_box.x + 10, tooltip_image.tooltip_box.y + (text_line_index * self.global_manager.get('font_size'))))


