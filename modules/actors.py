import pygame
from . import text_tools
from . import utility
from . import actor_utility
from . import scaling

class actor():
    '''
    Object that can exist within certain coordinates on one or more grids and can optionally be able to hold an inventory of commodities
    '''
    def __init__(self, coordinates, grids, modes, global_manager):
        '''
        Input:
            coordinates: tuple of two int variables representing the pixel coordinates of the bottom left of the notification
            grids: list of grid objects on which the mob's images will appear
            modes: list of strings representing the game modes in which the mob can appear
            global_manager: global_manager_template object used to manage a dictionary of shared variables
        '''
        self.global_manager = global_manager
        global_manager.get('actor_list').append(self)
        self.modes = modes
        self.grids = grids
        self.grid = grids[0]
        self.x, self.y = coordinates
        self.name = ''
        self.set_name('placeholder')
        self.set_coordinates(self.x, self.y)
        self.selected = False
        self.can_hold_commodities = False
        self.can_hold_infinite_commodities = False
        self.inventory_capacity = 0
        self.tooltip_text = []
        if self.can_hold_commodities:
            self.inventory_setup()
        #self.removed = False
            
    def set_image(self, new_image):
        for current_image in self.images:
            if current_image.change_with_other_images:
                current_image.set_image(new_image)
        self.image_dict['default'] = self.image_dict[new_image]
        if self.actor_type == 'mob':
            if self.global_manager.get('displayed_mob') == self:
                actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self)
        elif self.actor_type == 'tile':
            if self.global_manager.get('displayed_tile') == self:
                actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), self)

    def inventory_setup(self):
        '''
        Input:
            none
        Output:
            Sets this actor's inventory to a dictionary with a string key for each commodity type corresponding to an int representing the amount of the commodity held, which is initially set to 0
        '''
        self.inventory = {}
        for current_commodity in self.global_manager.get('commodity_types'):
            self.inventory[current_commodity] = 0

    def drop_inventory(self):
        for current_commodity in self.global_manager.get('commodity_types'):
            self.images[0].current_cell.tile.change_inventory(current_commodity, self.get_inventory(current_commodity))
            self.set_inventory(current_commodity, 0)

    def get_inventory_remaining(self, possible_amount_added = 0):
        num_commodities = possible_amount_added #if not 0, will show how much inventory will be remaining after an inventory change
        for current_commodity in self.global_manager.get('commodity_types'):
            num_commodities += self.get_inventory(current_commodity)
        return(self.inventory_capacity - num_commodities)

    def get_inventory_used(self):
        num_commodities = 0
        for current_commodity in self.global_manager.get('commodity_types'):
            num_commodities += self.get_inventory(current_commodity)
        return(num_commodities)

    def get_inventory(self, commodity):
        '''
        Input:
            string representing the type of commodity to get the amount of
        Output:
            Returns the number of the inputted commodity held by this actor
        '''
        if self.can_hold_commodities:
            return(self.inventory[commodity])
        else:
            return(0)

    def change_inventory(self, commodity, change):
        '''
        Input:
            string representing the type of commodity to change the amount of, int representing the amount of the commodity to add or remove
        Output:
            Changes the number of the inputted commodity held by this actor by the inputted int
        '''
        if self.can_hold_commodities:
            self.inventory[commodity] += change

    def set_inventory(self, commodity, new_value):
        '''
        Input:
            string representing the type of commodity to set the amount of, int representing the amount to set the commodity to
        Output:
            Sets the number of the inputted commodity held by this actor to the inputted int
        '''
        if self.can_hold_commodities:
            self.inventory[commodity] = new_value

    def get_held_commodities(self):
        '''
        Input:
            none
        Output:
            Returns a list of string variables representing each commodity of which this actor holds more than 0 units
        '''
        if self.can_hold_commodities:
            held_commodities = []
            for current_commodity in self.global_manager.get('commodity_types'):
                if self.get_inventory(current_commodity) > 0:
                    held_commodities.append(current_commodity)
            return(held_commodities)
        else:
            return([])
    
    def set_name(self, new_name):
        '''
        Input:
            string representing what this actor's name will be set to
        Output:
            Sets this actor's name to the inputted string
        '''
        self.name = new_name        

    def set_coordinates(self, x, y):
        '''
        Input:
            int representing the x coordinate to move this actor to, int representing the y coordinate to move this actor to
        Output:
            Sets this actor's x and y coordinates to the inputted int values
        '''
        self.x = x
        self.y = y
            
    def set_tooltip(self, new_tooltip):
        '''
        Input:
            list of string variables to set this actor's tooltip to
        Output:
            Sets this actor's tooltip to the inputted list of string variables, with each string representing a line of tooltip text
        '''
        self.tooltip_text = new_tooltip
        for current_image in self.images:
            current_image.set_tooltip(new_tooltip)
    
    def update_tooltip(self):
        '''
        Input:
            none
        Output:
            Sets this actor's tooltip to what it should currently be. By default, an actor's tooltip will be its name.
        '''
        self.set_tooltip([self.name])
        
    def remove(self):
        '''
        Input:
            none
        Output:
            Removes the object from relevant lists and prevents it from further appearing in or affecting the program
        '''
        self.global_manager.set('actor_list', utility.remove_from_list(self.global_manager.get('actor_list'), self))
        for current_image in self.images:
            self.global_manager.set('image_list', utility.remove_from_list(self.global_manager.get('image_list'), current_image))
        #self.removed = True

    def touching_mouse(self):
        '''
        Input:
            none
        Output:
            Returns whether any of this actor's images are colliding with the mouse
        '''
        for current_image in self.images:
            if current_image.Rect.collidepoint(pygame.mouse.get_pos()): #if mouse is in image
                return(True)
        return(False) #return false if none touch mouse

    def can_show_tooltip(self):
        '''
        Input:
            none
        Output:
            Returns whether this actor's tooltip should be shown. By default, an actor's tooltip should be shown when one of its images is colliding with the mouse and the game mode is correct.
        '''
        if self.touching_mouse() and self.global_manager.get('current_game_mode') in self.modes: #and not targeting_ability 
            return(True)
        else:
            return(False)

    def draw_tooltip(self, below_screen, beyond_screen, height, width, y_displacement):
        '''
        Input:
            y_displacement: int describing how far the tooltip should be moved along the y axis to avoid blocking other tooltips
        Output:
            Draws the button's tooltip when the button is visible and colliding with the mouse. If multiple tooltips are showing, tooltips beyond the first will be moved down to avoid blocking other tooltips.
        '''
        self.update_tooltip()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if below_screen:
            mouse_y = self.global_manager.get('display_height') + 10 - height
        if beyond_screen:
            mouse_x = self.global_manager.get('display_width') - width
        mouse_y += y_displacement
        tooltip_image = self.images[0]
        for current_image in self.images: #only draw tooltip from the image that the mouse is touching
            if current_image.Rect.collidepoint((mouse_x, mouse_y)):
                tooltip_image = current_image

        if (mouse_x + tooltip_image.tooltip_box.width) > self.global_manager.get('display_width'):
            mouse_x = self.global_manager.get('display_width') - tooltip_image.tooltip_box.width
        #if (self.global_manager.get('display_height') - mouse_y) - (len(tooltip_image.tooltip_text) * self.global_manager.get('font_size') + 5 + tooltip_image.tooltip_outline_width) < 0:
        #    mouse_y = self.global_manager.get('display_height') - tooltip_image.tooltip_box.height
        tooltip_image.tooltip_box.x = mouse_x
        tooltip_image.tooltip_box.y = mouse_y
        tooltip_image.tooltip_outline.x = tooltip_image.tooltip_box.x - tooltip_image.tooltip_outline_width
        tooltip_image.tooltip_outline.y = tooltip_image.tooltip_box.y - tooltip_image.tooltip_outline_width
        pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')['black'], tooltip_image.tooltip_outline)
        pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')['white'], tooltip_image.tooltip_box)
        for text_line_index in range(len(tooltip_image.tooltip_text)):
            text_line = tooltip_image.tooltip_text[text_line_index]
            self.global_manager.get('game_display').blit(text_tools.text(text_line, self.global_manager.get('myfont'), self.global_manager), (tooltip_image.tooltip_box.x + scaling.scale_width(10, self.global_manager),
                tooltip_image.tooltip_box.y + (text_line_index * self.global_manager.get('font_size'))))


