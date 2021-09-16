import pygame
import time
from . import utility
from . import drawing_tools
from . import text_tools
from . import scaling

class free_image():
    '''
    Image unrelated to any actors or grids that appears on a part of the screen
    '''
    def __init__(self, image_id, coordinates, width, height, modes, global_manager, to_front = False):
        '''
        Input:
            image_id: string representing the file path to this image's image file
            coordinates: tuple of two int variables representing the pixel location of this image
            width: int representing the pixel width of this image
            height: int representing the pixel height of this image
            modes: list of strings representing the game modes in which this image can appear
            global_manager: global_manager_template object
        '''
        self.global_manager = global_manager
        self.image_type = 'free'
        self.modes = modes
        self.width = width
        self.height = height
        self.set_image(image_id)
        self.x, self.y = coordinates
        self.y = self.global_manager.get('display_height') - self.y
        self.to_front = to_front
        self.global_manager.get('image_list').append(self)
        self.global_manager.get('free_image_list').append(self)
        
    def draw(self):
        '''
        Input:
            none
        Output:
            Draws the image if the current game mode matches this image's game modes
        '''
        if self.can_show():
            drawing_tools.display_image(self.image, self.x, self.y - self.height, self.global_manager)

    def can_show(self):
        '''
        Input:
            none
        Output:
            Returns whether the image should be shown. By default, free images always show if they are meant to be shown in the current game mode.
        '''
        if self.global_manager.get('current_game_mode') in self.modes:
            return(True)
        else:
            return(False)

    def remove(self):
        '''
        Input:
            none
        Output:
            Removes the object from relevant lists and prevents it from further appearing in or affecting the program
        '''
        self.global_manager.set('image_list', utility.remove_from_list(self.global_manager.get('image_list'), self))
        self.global_manager.set('free_image_list', utility.remove_from_list(self.global_manager.get('free_image_list'), self))

    def set_image(self, new_image):
        '''
        Input:
            string representing a file path for a new image file
        Output:
            Changes this image to match the image file represented by the inputted string
        '''
        self.image_id = new_image
        self.image = pygame.image.load('graphics/' + self.image_id)
        self.image = pygame.transform.scale(self.image, (self.width, self.height))

class loading_image_template(free_image):
    '''
    Free image that covers all other objects and appears while the game is loading 
    '''
    def __init__(self, image_id, global_manager):
        '''
        Input:
            image_id: string representing the file path to this image's image file
            global_manager: global_manager_template object
        '''
        super().__init__(image_id, (0, 0), global_manager.get('display_width'), global_manager.get('display_height'), [], global_manager)
        self.global_manager.set('image_list', utility.remove_from_list(self.global_manager.get('image_list'), self))

    def draw(self):
        '''
        Input:
            none
        Output:
            Draws this image
        '''
        drawing_tools.display_image(self.image, self.x, self.y - self.height, self.global_manager)

class actor_image():
    '''
    Image that is attached to an actor and a grid, representing the actor on a certain grid. An actor will have a different actor_image for each grid on which it appears
    '''
    def __init__(self, actor, width, height, grid, image_description, global_manager):
        '''
        Input:
            actor: actor object representing the actor to which this actor is attached
            width: int representing the pixel width of this image
            height: int representing the pixel height of this image
            grid: grid object representing the grid to which this actor image is attached
            image_description: string representing the file path to this image's image file
            global_manager: global_manager_template object
        '''
        self.global_manager = global_manager
        self.image_type = 'actor'
        self.last_image_switch = 0
        self.previous_idle_image = 'default'
        self.actor = actor
        self.modes = actor.modes
        self.width = width
        self.height = height
        self.Rect = pygame.Rect(self.actor.x, self.actor.y - self.height, self.width, self.height) #(left, top, width, height), bottom left on coordinates
        self.set_image(image_description)
        self.image_description == image_description
        self.global_manager.get('image_list').append(self)
        self.grid = grid
        self.outline_width = self.grid.grid_line_width + 1#3#2
        self.outline = pygame.Rect(self.actor.x, self.global_manager.get('display_height') - (self.actor.y + self.height), self.width, self.height)
        self.x, self.y = self.grid.convert_coordinates((self.actor.x, self.actor.y))
        if self.grid.is_mini_grid: #if on minimap and within its smaller range of coordinates, convert actor's coordinates to minimap coordinates and draw image there
            grid_x, grid_y = self.grid.get_mini_grid_coordinates(self.actor.x, self.actor.y)
        else:
            grid_x = self.actor.x
            grid_y = self.actor.y
        self.go_to_cell((grid_x, grid_y))
        self.set_tooltip('')
        self.change_with_other_images = True #determines whether set_image function of actor affects this image

    def get_center_coordinates(self):
        '''
        Input:
            none
        Output:
            Returns a tuple of two int variables representing the pixel coordinates at the center of this image's cell
        '''
        cell_width = self.grid.get_cell_width()
        cell_height = self.grid.get_cell_height()
        return((self.x + round(cell_width / 2), display_height -(self.y + round(cell_height / 2))))
        
    def set_image(self, new_image_description):
        '''
        Input:
            string representing a the name of an image file, without the file path or .png
        Output:
            Changes this image to match the image represented by the value of the inputted key to this image's actor's image dictionary
        '''
        self.last_image_switch = time.time()
        #if new_image_description == 'default' or new_image_description == 'right' or new_image_description == 'left':
        self.previous_idle_image = new_image_description
        self.image_description = new_image_description
        self.image_id = self.actor.image_dict[new_image_description]
        try: #use if there are any image path issues to help with file troubleshooting, does not prevent an error from occuring
            self.image = pygame.image.load('graphics/' + self.image_id)
        except:
            print('graphics/' + self.image_id)
            self.image = pygame.image.load('graphics/' + self.image_id)
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        
    def draw(self):
        '''
        Input:
            none
        Output:
            Draws this image at its cell location if it currently supposed to be shown
        '''
        if self.can_show():
            if self.grid.is_mini_grid: #if on minimap and within its smaller range of coordinates, convert actor's coordinates to minimap coordinates and draw image there
                if(self.grid.is_on_mini_grid(self.actor.x, self.actor.y)):
                    grid_x, grid_y = self.grid.get_mini_grid_coordinates(self.actor.x, self.actor.y)
                    self.go_to_cell((grid_x, grid_y))
                    drawing_tools.display_image(self.image, self.x, self.y - self.height, self.global_manager)
            else:
                self.go_to_cell((self.actor.x, self.actor.y))
                drawing_tools.display_image(self.image, self.x, self.y - self.height, self.global_manager)
        
    def go_to_cell(self, coordinates):
        '''
        Input:
            tuple of two int variables representing the grid coordinates of the cell to move to
        Output:
            Moves this image to the pixel coordinates corresponding to the inputted grid coordinates
        '''
        self.x, self.y = self.grid.convert_coordinates(coordinates)
        self.Rect.x = self.x
        self.Rect.y = self.y - self.height
        self.outline.x = self.x
        self.outline.y = self.y - self.height
                
    def set_tooltip(self, tooltip_text):
        '''
        Input:
            list of strings representing new tooltip text for this image, with each item being a separate line
        Output:
            Changes this image's tooltip to match the inputted list
        '''
        self.tooltip_text = tooltip_text
        tooltip_width = 10 #minimum tooltip width
        font_size = self.global_manager.get('font_size')
        font_name = self.global_manager.get('font_name')
        for text_line in tooltip_text:
            if text_tools.message_width(text_line, font_size, font_name) + scaling.scale_width(10, self.global_manager) > tooltip_width:
                tooltip_width = text_tools.message_width(text_line, font_size, font_name) + scaling.scale_width(10, self.global_manager)
        tooltip_height = (font_size * len(tooltip_text)) + scaling.scale_height(5, self.global_manager)
        self.tooltip_box = pygame.Rect(self.actor.x, self.actor.y, tooltip_width, tooltip_height)
        self.actor.tooltip_box = self.tooltip_box
        self.tooltip_outline_width = 1
        self.tooltip_outline = pygame.Rect(self.actor.x - self.tooltip_outline_width, self.actor.y + self.tooltip_outline_width, tooltip_width + (2 * self.tooltip_outline_width), tooltip_height + (self.tooltip_outline_width * 2))

    def touching_mouse(self):
        '''
        Input:
            none
        Output:
            Returns whether this image is colliding with the mouse
        '''
        if self.Rect.collidepoint(pygame.mouse.get_pos()):
            return(True)
        else:
            return(False)

    def can_show(self):
        '''
        Input:
            none
        Output:
            Returns whether this image should currently be shown
        '''
        if self.global_manager.get('current_game_mode') in self.modes:
            return(True)
        else:
            return(False)

    def remove(self): #different in subclasses
        nothing = 0

class building_image(actor_image):
    '''
    actor_image attached to a building rather than an actor, gaining the ability to manage the cells in which this building is considered to be
    '''
    def __init__(self, actor, width, height, grid, image_description, global_manager):
        '''
        Input:
            actor: actor object representing the actor to which this actor is attached
            width: int representing the pixel width of this image
            height: int representing the pixel height of this image
            grid: grid object representing the grid to which this mob image is attached
            image_description: string representing the file path to this image's image file
            global_manager: global_manager_template object
        '''
        super().__init__(actor, width, height, grid, image_description, global_manager)
        self.current_cell = 'none'
        self.image_type = 'building'
        self.add_to_cell()

    def remove_from_cell(self):
        '''
        Input:
            none
        Output:
            Remove's this image's mob from its cell, causing it to not be considered in the cell anymore. Does nothing if the image's mob is not already in a cell.
        '''
        if not self.current_cell == 'none':
            self.current_cell.contained_buildings[self.actor.building_type] = 'none'# = utility.remove_from_list(self.current_cell.contained_buildings, self.actor)
        self.current_cell = 'none'

    def add_to_cell(self):
        '''
        Input:
            none
        Output:
            Adds this image's mob to the front of a cell, causing it to be considered as being in the cell and causing it to be drawn on top of other mobs in that cell. This automatically removes this image's mob from other cells.
        '''
        if self.grid.is_mini_grid: #if on minimap and within its smaller range of coordinates, convert actor's coordinates to minimap coordinates and draw image there
            mini_x, mini_y = self.grid.get_mini_grid_coordinates(self.actor.x, self.actor.y)
            if(self.grid.is_on_mini_grid(self.actor.x, self.actor.y)):
                old_cell = self.current_cell
                self.current_cell = self.grid.find_cell(mini_x, mini_y)
                if not old_cell == self.current_cell and not self.actor in self.current_cell.contained_buildings:
                    self.current_cell.contained_buildings[self.actor.building_type] = self.actor #self.current_cell.contained_buildings.insert(0, self.actor)
            else:
                self.remove_from_cell()
            self.go_to_cell((mini_x, mini_y))
        else:
            self.remove_from_cell()
            self.current_cell = self.grid.find_cell(self.actor.x, self.actor.y)
            if not self.actor in self.current_cell.contained_buildings:
                self.current_cell.contained_buildings[self.actor.building_type] = self.actor#self.current_cell.contained_buildings.insert(0, self.actor)
            self.go_to_cell((self.current_cell.x, self.current_cell.y))
            
    def can_show(self):
        if (not self.current_cell == 'none') and self.global_manager.get('current_game_mode') in self.modes:
            return(True)
        else:
            return(False)


class infrastructure_connection_image(building_image):
    def __init__(self, actor, width, height, grid, image_description, direction, global_manager):
        super().__init__(actor, width, height, grid, image_description, global_manager)
        self.showing_connection = False
        self.direction = direction
        self.global_manager.get('infrastructure_connection_list').append(self)
        self.change_with_other_images = False #determines whether set_image function of actor affects this image
        #self.removed = False

    def update_roads(self):
        #if not self.removed: #prevents images from previous infrastructure versions from causing errors, non-ideal solution
        own_tile_infrastructure_type = self.actor.infrastructure_type
        adjacent_cell = 'none'
        #if not self.grid.is_mini_grid:
        adjacent_cell = self.actor.images[0].current_cell.adjacent_cells[self.direction]
        #else: #if on mini grid, use adjacent cell of main grid to get connection correct
        #    adjacent_cell = self.actor.images[0].current_cell.tile.get_equivalent_tile().cell.adjacent_cells[self.direction]
        if not adjacent_cell == 'none': #check if adjacent cell exists
            adjacent_tile_infrastructure = adjacent_cell.contained_buildings['infrastructure']
            if not adjacent_tile_infrastructure == 'none': #if adjacent tile has infrastructure
                adjacent_tile_infrastructure_type = adjacent_tile_infrastructure.infrastructure_type
                if own_tile_infrastructure_type == 'railroad' and own_tile_infrastructure_type == adjacent_tile_infrastructure_type: #if both railroads, draw railroad
                    self.set_image(self.direction + '_railroad') #up_railroad
                    self.actor.set_image('empty') #if connecting to other railroad, hide railroad cross
                else: #if both have infrastructure and at least 1 is not a railroad, draw road
                    self.set_image(self.direction + '_road')
                    if own_tile_infrastructure_type == 'road': #hide center cross if adjacent tiles have same type
                        self.actor.set_image('empty')
                    else:
                        self.actor.set_image('default') #if not same, show cross
                self.showing_connection = True
            else:
                self.showing_connection = False
        else:
            self.showing_connection = False #do not show if adjacent cell does not exist 
            
    def remove(self):
        self.global_manager.set('infrastructure_connection_list', utility.remove_from_list(self.global_manager.get('infrastructure_connection_list'), self))
        #self.removed = True
        super().remove()

    def can_show(self):
        if self.showing_connection:
            return(super().can_show())
        return(False)
        
        
class mob_image(actor_image):
    '''
    actor_image attached to a mob rather than an actor, gaining the ability to manage the cells in which this mob is considered to be
    '''
    def __init__(self, actor, width, height, grid, image_description, global_manager):
        '''
        Input:
            actor: actor object representing the actor to which this actor is attached
            width: int representing the pixel width of this image
            height: int representing the pixel height of this image
            grid: grid object representing the grid to which this mob image is attached
            image_description: string representing the file path to this image's image file
            global_manager: global_manager_template object
        '''
        super().__init__(actor, width, height, grid, image_description, global_manager)
        self.current_cell = 'none'
        self.image_type = 'mob'
        self.add_to_cell()
        
    def remove_from_cell(self):
        '''
        Input:
            none
        Output:
            Remove's this image's mob from its cell, causing it to not be considered in the cell anymore. Does nothing if the image's mob is not already in a cell.
        '''
        if not self.current_cell == 'none':
            self.current_cell.contained_mobs = utility.remove_from_list(self.current_cell.contained_mobs, self.actor)
        self.current_cell = 'none'

    def add_to_cell(self):
        '''
        Input:
            none
        Output:
            Adds this image's mob to the front of a cell, causing it to be considered as being in the cell and causing it to be drawn on top of other mobs in that cell. This automatically removes this image's mob from other cells.
        '''
        if self.grid.is_mini_grid: #if on minimap and within its smaller range of coordinates, convert actor's coordinates to minimap coordinates and draw image there
            mini_x, mini_y = self.grid.get_mini_grid_coordinates(self.actor.x, self.actor.y)
            if(self.grid.is_on_mini_grid(self.actor.x, self.actor.y)):
                old_cell = self.current_cell
                self.current_cell = self.grid.find_cell(mini_x, mini_y)
                if not old_cell == self.current_cell and not self.actor in self.current_cell.contained_mobs and not (self.actor.in_group or self.actor.in_vehicle or self.actor.in_building): #last part new
                    self.current_cell.contained_mobs.insert(0, self.actor)
            else:
                self.remove_from_cell()
            self.go_to_cell((mini_x, mini_y))
        else:
            self.remove_from_cell()
            self.current_cell = self.grid.find_cell(self.actor.x, self.actor.y)
            if not self.actor in self.current_cell.contained_mobs and not (self.actor.in_group or self.actor.in_vehicle or self.actor.in_building): #last part new
                self.current_cell.contained_mobs.insert(0, self.actor)
            self.go_to_cell((self.current_cell.x, self.current_cell.y))
            
    def can_show(self):
        '''
        Input:
            none
        Output:
            Returns whether this image should be shown. If it is attached to an officer or worker that is part of a group, it should not be shown.
            If it is not attached to an officer or worker in a group and it is at the front of a cell, it should be shown. Otherwise, it should not be shown.
        '''
        #if (self.actor in self.global_manager.get('officer_list') or self.actor in self.global_manager.get('worker_list')) and self.actor.in_group:
        #    return(False)
        if self.actor.in_vehicle or self.actor.in_group or self.actor.in_building:
            return(False)
        if (not self.current_cell == 'none') and self.current_cell.contained_mobs[0] == self.actor and self.global_manager.get('current_game_mode') in self.modes:
            return(True)
        else:
            return(False)

class button_image(actor_image):
    '''
    actor_image attached to a button rather than an actor, causing it to be located at a pixel coordinate location rather than within a grid cell
    '''
    def __init__(self, button, width, height, image_id, global_manager):
        '''
        Input:
            button: button object representing the button to which this image is attached
            width: int representing the pixel width of this image
            height: int representing the pixel height of this image
            image_id: string representing the file path to this image's image file
            global_manager: global_manager_template object
        '''
        self.global_manager = global_manager
        self.image_type = 'button'
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
        self.Rect = self.button.Rect
        self.outline_width = 2
        self.outline = pygame.Rect(self.x - self.outline_width, self.global_manager.get('display_height') - (self.y + self.height + self.outline_width), self.width + (2 * self.outline_width), self.height + (self.outline_width * 2))

    def update_state(self, new_x, new_y, new_width, new_height):
        '''
        Input:
            new_x: int representing the new pixel x coordinate of this image
            new_y: int representing the new pixel y coordinate of this image
            new_width: int representing the new pixel width of this image
            new_height: int representing the new pixel height of this image
        Output:
            Moves this image to the new location and changes its size based on the new width and height
        '''
        self.Rect = self.button.Rect
        self.outline.x = new_x - self.outline_width
        self.outline.y = display_height - (new_y + new_height + self.outline_width)
        self.outline.width = new_width + (2 * self.outline_width)
        self.outline.height = new_height + (self.outline_width * 2)
        self.set_image(self.image_id)
        
    def set_image(self, new_image_id):
        '''
        Input:
            string representing a file path for a new image file
        Output:
            Changes this image to match the image file represented by the inputted string
        '''
        self.image_id = new_image_id
        try:
            self.image = pygame.image.load('graphics/' + self.image_id)#.convert()
        except:
            print('graphics/' + self.image_id)
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        #self.Rect.width = self.width
        
    def draw(self):
        '''
        Input:
            none
        Output:
            Draws this image where its button is located if its button is supposed to be shown and if the game mode is correct
        '''
        if self.button.can_show(): #self.global_manager.get('current_game_mode') in self.button.modes should be in button.can_show()
            self.x = self.button.x
            self.y = self.global_manager.get('display_height') - (self.button.y + self.height) + self.height
            drawing_tools.display_image(self.image, self.x, self.y - self.height, self.global_manager)
        
    def draw_tooltip(self): #button has tooltip already, so image doesn't need a new tooltip
        '''
        Input:
            none
        Output:
            none, unlike superclass: while actor_images manage tooltips because actors do not manage tooltips, buttons do manage tooltips so button_images do not have to manage tooltips
        '''
        i = 0
        
    def set_tooltip(self, tooltip_text):
        '''
        Input:
            none
        Output:
            none, unlike superclass: while actor_images manage tooltips because actors do not manage tooltips, buttons do manage tooltips so button_images do not have to manage tooltips
        '''
        i = 0

class tile_image(actor_image):
    '''
    actor_image attached to a tile rather than an actor, causing it to use file paths rather than an image-dictionary-based image description system
    '''
    def __init__(self, actor, width, height, grid, image_description, global_manager):
        '''
        Input:
            same as superclass
        '''
        super().__init__(actor, width, height, grid, image_description, global_manager)
        self.go_to_cell((self.actor.x, self.actor.y))
        #self.outline = pygame.Rect(self.actor.x + 10, self.global_manager.get('display_height') - (self.actor.y + self.height) + 10, self.width, self.height)

    def go_to_cell(self, coordinates):
        '''
        Input:
            tuple of two int variables representing the grid coordinates of the cell to move to
        Output:
            Moves this image to the pixel coordinates corresponding to the inputted grid coordinates
        '''
        self.x, self.y = self.grid.convert_coordinates(coordinates)
        self.Rect.x = self.x
        self.Rect.y = self.y - self.height
        self.outline.x = self.x - self.outline_width
        self.outline.y = self.y - (self.height + self.outline_width)
        
    def draw(self):
        '''
        Input:
            none
        Output:
            Draws this image at its cell location
        '''
        self.go_to_cell((self.actor.x, self.actor.y))
        drawing_tools.display_image(self.image, self.x, self.y - self.height, self.global_manager)

class veteran_icon_image(tile_image):
    '''
    tile_image attached to a veteran_icon rather than a tile_image, allowing it to move around and follow an actor
    '''
    def __init__(self, actor, width, height, grid, image_description, global_manager):
        '''
        Input:
            same as superclass
        '''
        super().__init__(actor, width, height, grid, image_description, global_manager)

    def draw(self):
        '''
        Input:
            none
        Output:
            If not outside of this image's grid area and this image's actor can be shown, draw this image 
        '''
        if self.actor.actor.images[0].can_show() and self.can_show():
            if self.grid.is_mini_grid:
                self.actor.x, self.actor.y = self.grid.get_mini_grid_coordinates(self.actor.actor.x, self.actor.actor.y)
            else:
                self.actor.x = self.actor.actor.x
                self.actor.y = self.actor.actor.y
            self.go_to_cell((self.actor.x, self.actor.y))
            drawing_tools.display_image(self.image, self.x, self.y - self.height, self.global_manager)

    def can_show(self):
        '''
        Input:
            none
        Output:
            If this image is part of a minimap and its coordinates are outside of the minimap's area, do not show it. Otherwise, use the same output as superclass.
        '''
        if self.grid == self.global_manager.get('minimap_grid') and not self.grid.is_on_mini_grid(self.actor.actor.x, self.actor.actor.y): #do not show if mob (veteran icon's actor) is off map
            return(False)
        else:
            return(super().can_show())
