#Contains functionality for actors

import pygame
from . import text_tools
from . import utility
from . import actor_utility
from . import scaling

class actor():
    '''
    Object that can exist within certain coordinates on one or more grids and can optionally be able to hold an inventory of commodities
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
                'modes': string list value - Game modes during which this actor's images can appear
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.global_manager = global_manager
        self.from_save = from_save
        global_manager.get('actor_list').append(self)
        self.modes = input_dict['modes']
        if self.from_save:
            self.grid = self.global_manager.get(input_dict['grid_type'])
            self.grids = [self.grid]
            if not self.grid.mini_grid == 'none':
                self.grids.append(self.grid.mini_grid)
            self.set_name(input_dict['name'])
        else:
            self.grids = input_dict['grids']
            self.grid = self.grids[0]
            self.set_name('placeholder')
        self.x, self.y = input_dict['coordinates']
        self.set_coordinates(self.x, self.y)
        self.selected = False
        self.can_hold_commodities = False
        self.can_hold_infinite_commodities = False
        self.inventory_capacity = 0
        self.tooltip_text = []
        self.inventory = {}

    def to_save_dict(self):
        '''
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
                'init_type': string value - Represents the type of actor this is, used to initialize the correct type of object on loading
                'coordinates': int tuple value - Two values representing x and y coordinates on one of the game grids
                'modes': string list value - Game modes during which this actor's images can appear
                'grid_type': string value - String matching the global manager key of this actor's primary grid, allowing loaded object to start in that grid
                'name': string value - This actor's name
                'inventory': string/string dictionary value - Version of this actor's inventory dictionary only containing commodity types with 1+ units held
        '''
        save_dict = {}
        init_type = ''
        if self.actor_type == 'mob':
            if self.is_worker:
                if self.is_church_volunteers:
                    init_type = 'church_volunteers'
                elif self.worker_type == 'slave':
                    init_type = 'slave'
                else:
                    init_type = 'worker'
            elif self.is_vehicle:
                init_type = self.vehicle_type
            elif self.is_officer:
                init_type = self.officer_type
            elif self.is_group:
                init_type = self.group_type
        elif self.actor_type == 'tile':
            init_type = 'tile'
        elif self.actor_type == 'building':
            init_type = self.building_type
        save_dict['init_type'] = init_type
        
        save_dict['coordinates'] = (self.x, self.y)
        save_dict['modes'] = self.modes
        for grid_type in self.global_manager.get('grid_types_list'):
            if self.global_manager.get(grid_type) == self.grid:
                save_dict['grid_type'] = grid_type
        save_dict['name'] = self.name
        saved_inventory = {}
        if self.can_hold_commodities: #only save inventory if not empty
            for current_commodity in self.global_manager.get('commodity_types'):
               if self.inventory[current_commodity] > 0:
                   saved_inventory[current_commodity] = self.inventory[current_commodity]
        save_dict['inventory'] = saved_inventory
        return(save_dict)
            
    def set_image(self, new_image):
        '''
        Description:
            Changes this actor's images to reflect the inputted image file path
        Input:
            string new_image: Image file path to change this actor's images to
        Output:
            None
        '''
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
        elif self.actor_type == 'building':
            if self.global_manager.get('displayed_tile') == self.images[0].current_cell.tile:
                actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), self.images[0].current_cell.tile)

    def load_inventory(self, inventory_dict):
        '''
        Description:
            Sets this actor's inventory to a dictionary with a string key for each commodity type and an int value for how much of that commodity is held, matching the inventory of the original saved actor
        Input:
            string/int dictionary inventory_dict: Dictionary with string keys for each commodity type saved and int values for how much of that commodity is held. No entries required for commodities with 0 units
        Output:
            None
        '''
        for current_commodity in self.global_manager.get('commodity_types'):
            if current_commodity in inventory_dict:
                self.set_inventory(current_commodity, inventory_dict[current_commodity])
            else:
                self.set_inventory(current_commodity, 0)

    def inventory_setup(self):
        '''
        Description:
            Sets this actor's inventory to a dictionary with a string key for each commodity type and an int value initially set to 0 representing the amount of the commodity held
        Input:
            None
        Output:
            None
        '''
        self.inventory = {}
        for current_commodity in self.global_manager.get('commodity_types'):
            self.inventory[current_commodity] = 0

    def drop_inventory(self):
        '''
        Description:
            Drops each commodity held in this actor's inventory into its current tile
        Input:
            None
        Output:
            None
        '''
        for current_commodity in self.get_held_commodities(): #current_commodity in self.global_manager.get('commodity_types'):
            self.images[0].current_cell.tile.change_inventory(current_commodity, self.get_inventory(current_commodity))
            self.set_inventory(current_commodity, 0)

    def get_inventory_remaining(self, possible_amount_added = 0):
        '''
        Description:
            By default, returns amount of inventory space remaining. If input received, returns amount of space remaining in inventory if the inputted number of commodities were added to it. 
        Input:
            int possible_amount_added = 0: Amount to add to the current inventory size, allowing inventory remaining after adding a certain number of commodities to be found
        Output:
            int: Amount of space remaining in inventory after possible_amount_added is added
        '''
        num_commodities = possible_amount_added #if not 0, will show how much inventory will be remaining after an inventory change
        for current_commodity in self.get_held_commodities():
            num_commodities += self.get_inventory(current_commodity)
        return(self.inventory_capacity - num_commodities)

    def get_inventory_used(self):
        '''
        Description:
            Returns the number of commodities held by this actor
        Input:
            None
        Output:
            int: Number of commodities held by this actor
        '''
        num_commodities = 0
        for current_commodity in self.get_held_commodities():
            num_commodities += self.get_inventory(current_commodity)
        return(num_commodities)

    def get_inventory(self, commodity):
        '''
        Description:
            Returns the number of commodities of the inputted type held by this actor
        Input:
            string commodity: Type of commodity to check inventory for
        Output:
            int: Number of commodities of the inputted type held by this actor
        '''
        if self.can_hold_commodities:
            return(self.inventory[commodity])
        else:
            return(0)

    def change_inventory(self, commodity, change):
        '''
        Description:
            Changes the number of commodities of a certain type held by this actor
        Input:
            string commodity: Type of commodity to change the inventory of
            int change: Amount of commodities of the inputted type to add. Removes commodities of the inputted type if negative
        Output:
            None
        '''
        if self.can_hold_commodities:
            self.inventory[commodity] += change

    def set_inventory(self, commodity, new_value):
        '''
        Description:
            Sets the number of commodities of a certain type held by this actor
        Input:
            string commodity: Type of commodity to set the inventory of
            int new_value: Amount of commodities of the inputted type to set inventory to
        Output:
            None
        '''
        if self.can_hold_commodities:
            self.inventory[commodity] = new_value

    def get_held_commodities(self):
        '''
        Description:
            Returns a list of the types of commodities held by this actor
        Input:
            None
        Output:
            string list: Types of commodities held by this actor
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
        Description:
            Sets this actor's name
        Input:
            string new_name: Name to set this actor's name to
        Output:
            None
        '''
        self.name = new_name        

    def set_coordinates(self, x, y):
        '''
        Description:
            Moves this actor to the inputted coordinates
        Input:
            int x: grid x coordinate to move this actor to
            int y: grid y coordinate to move this actor to
        Output:
            None
        '''
        self.x = x
        self.y = y
            
    def set_tooltip(self, new_tooltip):
        '''
        Description:
            Sets this actor's tooltip to the inputted list, with each item representing a line of the tooltip
        Input:
            string list new_tooltip: Lines for this actor's tooltip
        Output:
            None
        '''
        self.tooltip_text = new_tooltip
        for current_image in self.images:
            current_image.set_tooltip(new_tooltip)
    
    def update_tooltip(self):
        '''
        Description:
            Sets this actor's tooltip to what it should be whenever the player looks at the tooltip. By default, sets tooltip to this actor's name
        Input:
            None
        Output:
            None
        '''
        self.set_tooltip([self.name.capitalize()])
        
    def remove(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program
        Input:
            None
        Output:
            None
        '''
        self.global_manager.set('actor_list', utility.remove_from_list(self.global_manager.get('actor_list'), self))
        for current_image in self.images:
            self.global_manager.set('image_list', utility.remove_from_list(self.global_manager.get('image_list'), current_image))

    def touching_mouse(self):
        '''
        Description:
            Returns whether any of this actor's images is colliding with the mouse
        Input:
            None
        Output:
            boolean: Returns True if any of this actor's images is colliding with the mouse, otherwise returns False
        '''
        for current_image in self.images:
            if current_image.Rect.collidepoint(pygame.mouse.get_pos()): #if mouse is in image
                return(True)
        return(False) #return false if none touch mouse

    def can_show_tooltip(self):
        '''
        Description:
            Returns whether this actor's tooltip can be shown. By default, its tooltip can be shown when it is visible and colliding with the mouse
        Input:
            None
        Output:
            None
        '''
        if self.touching_mouse() and self.global_manager.get('current_game_mode') in self.modes: #and not targeting_ability 
            return(True)
        else:
            return(False)

    def draw_tooltip(self, below_screen, beyond_screen, height, width, y_displacement):
        '''
        Description:
            Draws this actor's tooltip when moused over. The tooltip's location may vary when the tooltip is near the edge of the screen or if multiple tooltips are being shown
        Input:
            boolean below_screen: Whether any of the currently showing tooltips would be below the bottom edge of the screen. If True, moves all tooltips up to prevent any from being below the screen
            boolean beyond_screen: Whether any of the currently showing tooltips would be beyond the right edge of the screen. If True, moves all tooltips to the left to prevent any from being beyond the screen
            int height: Combined pixel height of all tooltips
            int width: Pixel width of the widest tooltip
            int y_displacement: How many pixels below the mouse this tooltip should be, depending on the order of the tooltips
        Output:
            None
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


