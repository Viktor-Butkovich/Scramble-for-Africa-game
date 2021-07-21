import pygame
from . import images
from . import text_tools
from . import dice
from . import utility

class actor():
    def __init__(self, coordinates, grid, modes, global_manager):
        self.global_manager = global_manager
        global_manager.get('actor_list').append(self)
        self.modes = modes
        self.grid = grid
        self.x, self.y = coordinates
        self.name = ''
        self.set_name('placeholder')
        self.set_coordinates(self.x, self.y, False)
        #self.controllable = False# obsolete but possibly usable later
        self.selected = False
    
    def set_name(self, new_name):
        self.name = new_name        
       
    def is_clear(self, x, y):
        return self.grid.is_clear(x, y)
    
    def set_coordinates(self, x, y, able_to_print):
        if self.is_clear(x, y):
            self.grid.find_cell(self.x, self.y).occupied = False
            self.x = x
            self.y = y
            self.grid.find_cell(self.x, self.y).occupied = True
        else:#elif able_to_print:
            text_tools.print_to_screen('This cell is blocked.', self.global_manager)
            
    def set_tooltip(self, new_tooltip):
        self.image.set_tooltip(new_tooltip)
    
    def update_tooltip(self):
        self.set_tooltip(['Name: ' + self.name])
        
    def remove(self):
        self.global_manager.set('actor_list', utility.remove_from_list(self.global_manager.get('actor_list'), self))
        self.global_manager.set('image_list', utility.remove_from_list(self.global_manager.get('image_list'), self.image))

    def interact(self, other):
        if other == None:
            text_tools.print_to_screen(self.name + ' has nothing to interact with.')
        else:
            text_tools.print_to_screen(self.name + ' is interacting with ' + other.name)

    def touching_mouse(self):
        if self.image.Rect.collidepoint(pygame.mouse.get_pos()): #if mouse is in button
            return(True)
        else:
            return(False)

    def can_show_tooltip(self): #moved to actor
        if self.touching_mouse() and self.global_manager.get('current_game_mode') in self.modes: #and not targeting_ability 
            return(True)
        else:
            return(False)

    def draw_tooltip(self, y_displacement):
        self.update_tooltip()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_y += y_displacement
        if (mouse_x + self.image.tooltip_box.width) > self.global_manager.get('display_width'):
            mouse_x = self.global_manager.get('display_width') - self.image.tooltip_box.width
        if (self.global_manager.get('display_height') - mouse_y) - (len(self.image.tooltip_text) * self.global_manager.get('font_size') + 5 + self.image.tooltip_outline_width) < 0:
            mouse_y = self.global_manager.get('display_height') - self.image.tooltip_box.height
        self.image.tooltip_box.x = mouse_x
        self.image.tooltip_box.y = mouse_y
        self.image.tooltip_outline.x = self.image.tooltip_box.x - self.image.tooltip_outline_width
        self.image.tooltip_outline.y = self.image.tooltip_box.y - self.image.tooltip_outline_width
        pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')['black'], self.image.tooltip_outline)
        pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')['white'], self.image.tooltip_box)
        for text_line_index in range(len(self.image.tooltip_text)):
            text_line = self.image.tooltip_text[text_line_index]
            self.global_manager.get('game_display').blit(text_tools.text(text_line, self.global_manager.get('myfont'), self.global_manager), (self.image.tooltip_box.x + 10, self.image.tooltip_box.y + (text_line_index * self.global_manager.get('font_size'))))
            
class mob(actor):
    '''a mobile and selectable actor'''
    def __init__(self, coordinates, grid, image_id, name, modes, global_manager):
        super().__init__(coordinates, grid, modes, global_manager)
        self.image_dict = {'default': image_id}
        self.image = images.actor_image(self, self.grid.get_cell_width(), self.grid.get_cell_height(), self.grid, 'default', self.global_manager)#self, actor, width, height, grid, image_description, global_manager
        global_manager.get('mob_list').append(self)
        self.set_name(name)

    def draw_outline(self):
        pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')['dark gray'], (self.image.outline), self.image.outline_width)

    def update_tooltip(self):
        self.set_tooltip([self.name])

    def remove(self):
        super().remove()
        self.global_manager.set('mob_list', utility.remove_from_list(self.global_manager.get('mob_list'), self)) #make a version of mob_list without self and set mob_list to it

    def can_move(self, x_change, y_change):
        future_x = self.x + x_change
        future_y = self.y + y_change
        if future_x >= 0 and future_x < self.grid.coordinate_width and future_y >= 0 and future_y < self.grid.coordinate_height:
            if self.grid.find_cell(future_x, future_y).visible:
                if not self.grid.find_cell(future_x, future_y).terrain == 'water':
                    return(True)
                else:
                    if self.grid.find_cell(future_x, future_y).visible:
                        text_tools.print_to_screen("You can't move into the water.", self.global_manager) #to do: change this when boats are added
                        return(False)
            else:
                text_tools.print_to_screen("You can't move into an unexplored tile.", self.global_manager)
                return(False)

        else:
            text_tools.print_to_screen("You can't move off of the map.", self.global_manager)
            return(False)

    def move(self, x_change, y_change):
        self.x += x_change
        self.y += y_change
        self.global_manager.get('minimap_grid').calibrate(self.x, self.y)


class explorer(mob):
    '''mob that can explore tiles'''
    def __init__(self, coordinates, grid, image_id, name, modes, global_manager):
        super().__init__(coordinates, grid, image_id, name, modes, global_manager)
        self.grid.find_cell(self.x, self.y).set_visibility(True)
        self.veteran = False
        self.veteran_icon = 'none'
        
    def can_move(self, x_change, y_change):
        future_x = self.x + x_change
        future_y = self.y + y_change
        if future_x >= 0 and future_x < self.grid.coordinate_width and future_y >= 0 and future_y < self.grid.coordinate_height:
            if not self.grid.find_cell(future_x, future_y).terrain == 'water':
                return(True)
            else:
                if self.grid.find_cell(future_x, future_y).visible:
                    text_tools.print_to_screen("You can't move into the water.", self.global_manager) #to do: change this when boats are added
                    return(False)
                else:
                    return(True) #will attempt to move there and discover it and discover it
        else:
            text_tools.print_to_screen("You can't move off of the map.", self.global_manager)
            return(False)

    def move(self, x_change, y_change):
        future_x = self.x + x_change
        future_y = self.y + y_change
        died = False
        future_cell = self.grid.find_cell(future_x, future_y)
        if future_cell.visible == False: #if moving to unexplored area, try to explore it
            if self.veteran:
                text_tools.print_to_screen("The veteran explorer can roll twice and pick the higher result.", self.global_manager)
                roll_result = max(dice.roll(6, "Exploration roll", 4, self.global_manager), dice.roll(6, "Exploration roll", 4, self.global_manager))
                text_tools.print_to_screen("The higher result, " + str(roll_result) + ", was used.", self.global_manager)
                self.global_manager.get('roll_label').set_label("Roll: " + str(roll_result)) #label should show the roll that was used
            else:
                roll_result = dice.roll(6, "Exploration roll", 4, self.global_manager)
                if roll_result == 6:
                    self.veteran = True
                    text_tools.print_to_screen("This explorer has become a veteran explorer.", self.global_manager)
                    self.set_name("Veteran explorer")
                    self.veteran_icon = tile_class((self.x, self.y), self.grid, 'misc/veteran_icon.png', 'veteran icon', ['strategic'], False, self.global_manager)
            if roll_result > 4: #4+ required on D6 for exploration
                if not future_cell.resource == 'none':
                    text_tools.print_to_screen("You discovered a " + future_cell.terrain + " tile with a " + future_cell.resource + " resource.", self.global_manager)
                else:
                    text_tools.print_to_screen("You discovered a " + future_cell.terrain + " tile.", self.global_manager)
                future_cell.set_visibility(True)
                if not future_cell.terrain == 'water':
                    super().move(x_change, y_change)
                    #self.x += x_change
                    #self.y += y_change
            else:
                text_tools.print_to_screen("You were not able to explore the tile.", self.global_manager)
            if roll_result == 1:
                text_tools.print_to_screen("This explorer has died.", self.global_manager)
                self.remove()
                died = True
                
        else: #if moving to explored area, move normally
            super().move(x_change, y_change)
            #self.x += x_change
            #self.y += y_change
        if not died and self.veteran:
            self.veteran_icon.x = self.x
            self.veteran_icon.y = self.y

    def remove(self):
        super().remove()
        if not self.veteran_icon == 'none':
            self.veteran_icon.remove()

class tile_class(actor): #to do: make terrain tiles a subclass
    '''like an obstacle without a tooltip or movement blocking'''
    def __init__(self, coordinates, grid, image, name, modes, show_terrain, global_manager): #show_terrain is like a subclass, true is terrain tile, false is non-terrain tile
        super().__init__(coordinates, grid, modes, global_manager)
        self.set_name(name)
        self.global_manager.get('tile_list').append(self)
        self.image_dict = {'default': image}
        self.image = images.tile_image(self, self.grid.get_cell_width(), self.grid.get_cell_height(), grid, 'default', global_manager)
        #self.shader = tile_shader(self, self.grid.get_cell_width(), self.grid.get_cell_height(), grid, 'default', global_manager)
        self.show_terrain = show_terrain
        self.cell = self.grid.find_cell(self.x, self.y)
        #if self.cell.tile == 'none':
        #    self.cell.tile = self
        if self.show_terrain: #to do: make terrain tiles a subclass
            self.cell.tile = self
            self.resource_icon = 'none' #the resource icon is appearance, making it a property of the tile rather than the cell
            self.set_terrain(self.cell.terrain) #terrain is a property of the cell, being stored information rather than appearance, same for resource, set these in cell
            self.image_dict['hidden'] = 'scenery/paper_hidden.png'#'scenery/hidden.png'
            self.set_visibility(self.cell.visible)
        elif self.name == 'resource icon':
            self.image_dict['hidden'] = 'misc/empty.png'
        else:
            self.terrain = 'floor'
    def set_visibility(self, new_visibility):
        if new_visibility == True:
            image_name = 'default'
        else:
            image_name = 'hidden'
            
        self.image.set_image(image_name)
        self.image.previous_idle_image = image_name
        if not self.resource_icon == 'none':
            self.resource_icon.image.set_image(image_name)
            self.resource_icon.image.previous_idle_image = image_name
            
    def set_resource(self, new_resource):
        #if self.show_terrain: #only do something if a terrain tile
            if not self.resource_icon == 'none':
                self.resource_icon.remove()
                self.resource_icon = 'none'
            self.resource = new_resource
            #if not self.cell.resource == 'none':
            self.resource_icon = tile_class((self.x, self.y), self.grid, 'scenery/resources/' + self.cell.resource + '.png', 'resource icon', ['strategic'], False, self.global_manager)
            self.set_visibility(self.cell.visible)
            
    def set_terrain(self, new_terrain): #to do, add variations like grass to all terrains
        #print(self.cell.terrain + ' ' + new_terrain)
        if new_terrain == 'clear':
            #random_grass = random.randrange(1, 3) #clear, hills, jungle, water, mountain, swamp, desert
            #self.image_dict['default'] = 'scenery/terrain/clear' + str(random_grass) + '.png'
            self.image_dict['default'] = 'scenery/terrain/clear.png'
            
        elif new_terrain == 'hills':
            self.image_dict['default'] = 'scenery/terrain/hills.png'
            
        elif new_terrain == 'jungle':
            self.image_dict['default'] = 'scenery/terrain/jungle.png'
            
        elif new_terrain == 'water':
            self.image_dict['default'] = 'scenery/terrain/water.png'
            
        elif new_terrain == 'mountain':
            self.image_dict['default'] = 'scenery/terrain/mountain.png'
            
        elif new_terrain == 'swamp':
            self.image_dict['default'] = 'scenery/terrain/swamp.png'
            
        elif new_terrain == 'desert':
            self.image_dict['default'] = 'scenery/terrain/desert.png'

        elif new_terrain == 'none':
            self.image_dict['default'] = 'scenery/hidden.png'

        self.image.set_image('default')

    def update_tooltip(self):
        if self.show_terrain: #if is terrain, show tooltip
            tooltip_message = []
            if self.cell.visible:
                tooltip_message.append('This is a ' + self.cell.terrain + ' tile.')
                if not self.cell.resource == 'none':
                    tooltip_message.append('This tile has a ' + self.cell.resource + ' resource.')
            else:
                tooltip_message .append('This tile has not been explored.')
            self.set_tooltip(tooltip_message)
        else:
            self.set_tooltip([])

    def set_coordinates(self, x, y, able_to_print):
        my_cell = self.grid.find_cell(self.x, self.y)
        #if self.is_clear(x, y):
        #my_cell.occupied = False
        self.x = x
        self.y = y
        my_cell = self.grid.find_cell(self.x, self.y)
        #my_cell.occupied = False
        #else:
        #    if self.controllable and able_to_print:
        #        text_tools.print_to_screen("You can't move to an occupied cell.")
                
    def remove(self):
        super().remove()
        self.global_manager.set('tile_list', utility.remove_from_list(self.global_manager.get('tile_list'), self))
        self.global_manager.set('image_list', utility.remove_from_list(self.global_manager.get('image_list'), self.image))
        #self.global_manager.set('image_list', utility.remove_from_list(self.global_manager.get('image_list'), self.shader))
        #print('removing')
        #self.cell.tile = 'none'
        #to do: this remove function is being called incorrectly at some point in the program, causing tiles to be removed

    def can_show_tooltip(self): #tiles don't have tooltips, except for terrain tiles
        if self.show_terrain == True:
            if self.touching_mouse() and self.global_manager.get('current_game_mode') in self.modes: #and not targeting_ability 
                return(True)
            else:
                return(False)
        else:
            return(False)
        
class overlay_tile(tile_class):
    '''kind of tile, preferably transparent, that appears in front of obstacles. Good for darkness and such'''
    def __init__(self, actor, width, height, grid, image_id, show_terrain, global_manager):
        super().__init__(actor, width, height, grid, image_id, show_terrain, global_manager)
        self.global_manager.get('overlay_tile_list').append(self)
        
    def remove(self):
        super().remove()
        self.global_manager.set('overlay_tile_list', utility.remove_from_list(self.global_manager.get('overlay_tile_list'), self))

            
def create_image_dict(stem):
    '''if stem is a certain value, add extra ones, such as special combat animations: only works for images in graphics/mobs'''
    stem = 'mobs/' + stem
    stem += '/'#goes to that folder
    image_dict = {}
    image_dict['default'] = stem + 'default.png'
    image_dict['right'] = stem + 'right.png'  
    image_dict['left'] = stem + 'left.png'
    return(image_dict)
