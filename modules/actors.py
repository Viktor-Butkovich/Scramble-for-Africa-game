import pygame
import time
from . import images
from . import text_tools
from . import dice_utility
from . import utility
from . import notification_tools
#from . import label
from . import dice
from . import scaling

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
        for current_image in self.images:
            current_image.set_tooltip(new_tooltip)
    
    def update_tooltip(self):
        self.set_tooltip(['Name: ' + self.name])
        
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
            
class mob(actor):
    '''a mobile and selectable actor'''
    def __init__(self, coordinates, grids, image_id, name, modes, global_manager):
        super().__init__(coordinates, grids, modes, global_manager)
        self.image_dict = {'default': image_id}
        #self.grids = grids #for things like drawing images on each grid, go through each grid on which the mob can appear # moved to actor class
        #self.grid = grids[0] #for things like detecting if moving is possible, use the first grid, which will be the main map
        self.selection_outline_color = 'bright green'
        self.images = []
        for current_grid in self.grids:
            self.images.append(images.actor_image(self, current_grid.get_cell_width(), current_grid.get_cell_height(), current_grid, 'default', self.global_manager))#self, actor, width, height, grid, image_description, global_manager
        global_manager.get('mob_list').append(self)
        self.set_name(name)

    def draw_outline(self):
        if self.global_manager.get('show_selection_outlines'):
            for current_image in self.images: #dark gray
                pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')[self.selection_outline_color], (current_image.outline), current_image.outline_width)

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
    def __init__(self, coordinates, grids, image_id, name, modes, global_manager):
        super().__init__(coordinates, grids, image_id, name, modes, global_manager)
        self.grid.find_cell(self.x, self.y).set_visibility(True)
        self.veteran = False
        self.veteran_icons = []
        self.exploration_mark_list = []
        
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

    def display_exploration_die(self, coordinates, result):
        result_outcome_dict = {'min_success': 4, 'min_crit_success': 6, 'max_crit_fail': 1}
        outcome_color_dict = {'success': 'dark green', 'fail': 'dark red', 'crit_success': 'bright green', 'crit_fail': 'bright red', 'default': 'black'}
        new_die = dice.die(scaling.scale_coordinates(coordinates[0], coordinates[1], self.global_manager), scaling.scale_width(100, self.global_manager), scaling.scale_height(100, self.global_manager), ['strategic'], 6, result_outcome_dict, outcome_color_dict, result, self.global_manager)

    def move(self, x_change, y_change): #to do: add directions to default movement
        self.global_manager.set('show_selection_outlines', True)
        self.global_manager.set('show_minimap_outlines', True)
        self.global_manager.set('last_selection_outline_switch', time.time())#outlines should be shown immediately when selected
        self.global_manager.set('last_minimap_outline_switch', time.time())
        future_x = self.x + x_change
        future_y = self.y + y_change
        roll_result = 0
        if x_change > 0:
            direction = 'east'
        elif x_change < 0:
            direction = 'west'
        elif y_change > 0:
            direction = 'north'
        elif y_change < 0:
            direction = 'south'
        else:
            direction = 'none'
        #died = False
        future_cell = self.grid.find_cell(future_x, future_y)
        if future_cell.visible == False: #if moving to unexplored area, try to explore it
            for current_grid in self.grids:
                coordinates = (0, 0)
                if current_grid.is_mini_grid:
                    coordinates = current_grid.get_mini_grid_coordinates(self.x + x_change, self.y + y_change)
                else:
                    coordinates = (self.x + x_change, self.y + y_change)
                self.exploration_mark_list.append(tile_class(coordinates, current_grid, 'misc/exploration_x/' + direction + '_x.png', 'exploration mark', ['strategic'], False, self.global_manager))
            text = ""
            text += "The expedition heads towards the " + direction + ". /n"
            text += (self.global_manager.get('flavor_text_manager').generate_flavor_text('explorer') + " /n")
            
            notification_tools.display_exploration_notification(text + "Click to roll.", self.global_manager)
            
            notification_tools.display_dice_rolling_notification(text + "Rolling... ", self.global_manager)
            
            text += "/n"

        #new_die = label.die(300, 300, 100, 100, ['strategic'], 6, result_outcome_dict, outcome_color_dict, 7, result, global_manager)
            if self.veteran:
                text += ("The veteran explorer can roll twice and pick the higher result /n")
                
                first_roll_list = dice_utility.roll_to_list(6, "Exploration roll", 4, 6, 1, self.global_manager)
                self.display_exploration_die((500, 500), first_roll_list[0])
                #new_die = label.die(scaling.scale_coordinates(500, 500, self.global_manager), scaling.scale_width(100, self.global_manager), scaling.scale_height(100, self.global_manager), ['strategic'], 6, result_outcome_dict, outcome_color_dict, 7, first_roll_list[0], self.global_manager)
                
                second_roll_list = dice_utility.roll_to_list(6, "Exploration roll", 4, 6, 1, self.global_manager)
                self.display_exploration_die((500, 380), second_roll_list[0])
                #other_new_die = label.die(scaling.scale_coordinates(500, 380), scaling.scale_width(100, self.global_manager), scaling.scale_height(100, self.global_manager), ['strategic'], 6, result_outcome_dict, outcome_color_dict, 7, second_roll_list[0], self.global_manager)
                
                text += (first_roll_list[1] + second_roll_list[1]) #add strings from roll result to text
                roll_result = max(first_roll_list[0], second_roll_list[0])#(dice.roll(6, "Exploration roll", 4, self.global_manager), dice.roll(6, "Exploration roll", 4, self.global_manager))
                text += ("The higher result, " + str(roll_result) + ", was used. /n")
                #self.global_manager.get('roll_label').set_label("Roll: " + str(roll_result)) #label should show the roll that was used
            else:
                roll_list = dice_utility.roll_to_list(6, "Exploration roll", 4, 6, 1, self.global_manager)
                #new_die = label.die(scaling.scale_coordinates(500, 500, self.global_manager), scaling.scale_width(100, self.global_manager), scaling.scale_height(100), ['strategic'], 6, result_outcome_dict, outcome_color_dict, 7, roll_list[0], self.global_manager)
                self.display_exploration_die((500, 440), roll_list[0])
                
                text += roll_list[1]
                roll_result = roll_list[0]
                #if roll_result == 6:
                #    self.veteran = True
                #    text += "This explorer has become a veteran explorer. /n"
                #    self.set_name("Veteran explorer")
                    #for current_grid in self.grids:
                    #    self.veteran_icons.append(tile_class((self.x, self.y), current_grid, 'misc/veteran_icon.png', 'veteran icon', ['strategic'], False, self.global_manager))
                    
            notification_tools.display_exploration_notification(text + "Click to continue.", self.global_manager)
            
            text += "/n"
            if roll_result >= 4: #4+ required on D6 for exploration
                if not future_cell.resource == 'none':
                    text += "You discovered a " + future_cell.terrain + " tile with a " + future_cell.resource + " resource. /n"
                else:
                    text += "You discovered a " + future_cell.terrain + " tile. /n"
                #future_cell.set_visibility(True)
                #if not future_cell.terrain == 'water':
                #    super().move(x_change, y_change)
                #else: #if discovered a water tile, update minimap but don't move there
                #    self.global_manager.get('minimap_grid').calibrate(self.x, self.y)
            else:
                text += "You were not able to explore the tile. /n"
            if roll_result == 1:
                text += "This explorer has died. /n" #actual death occurs when exploration completes

            if (not self.veteran) and roll_result == 6:
                self.veteran = True
                text += "This explorer has become a veteran explorer. /n"
                self.set_name("Veteran explorer")
                
            notification_tools.display_exploration_notification(text + "Click to remove this notification.", self.global_manager)
                
        else: #if moving to explored area, move normally
            super().move(x_change, y_change)
        #if not died and self.veteran:
        #    for current_veteran_icon in self.veteran_icons:
        #        if current_veteran_icon.grid.is_mini_grid:
        #            current_veteran_icon.x, current_veteran_icon.y = current_veteran_icon.grid.get_mini_grid_coordinates(self.x, self.y)
        #        else:
        #            current_veteran_icon.x = self.x
        #            current_veteran_icon.y = self.y
        self.global_manager.set('exploration_result', [self, roll_result, x_change, y_change])

    def complete_exploration(self): #roll_result, x_change, y_change
        exploration_result = self.global_manager.get('exploration_result')
        roll_result = exploration_result[1]
        x_change = exploration_result[2]
        y_change = exploration_result[3]
        future_cell = self.grid.find_cell(x_change + self.x, y_change + self.y)
        died = False
        if roll_result >= 4:
            future_cell.set_visibility(True)
            if not future_cell.terrain == 'water':
                super().move(x_change, y_change)
            else: #if discovered a water tile, update minimap but don't move there
                self.global_manager.get('minimap_grid').calibrate(self.x, self.y)
        if roll_result == 6:
            for current_grid in self.grids:
                self.veteran_icons.append(tile_class((self.x, self.y), current_grid, 'misc/veteran_icon.png', 'veteran icon', ['strategic'], False, self.global_manager))
        elif roll_result == 1:
            self.remove()
            died = True
        if not died and self.veteran:
            for current_veteran_icon in self.veteran_icons:
                if current_veteran_icon.grid.is_mini_grid:
                    current_veteran_icon.x, current_veteran_icon.y = current_veteran_icon.grid.get_mini_grid_coordinates(self.x, self.y)
                else:
                    current_veteran_icon.x = self.x
                    current_veteran_icon.y = self.y
        #dice_list = self.global_manager.get('dice_list')
        #while len(dice_list) > 0:
        #    dice_list[0].remove()
        copy_dice_list = self.global_manager.get('dice_list')
        for current_die in copy_dice_list:
            current_die.remove()
        copy_exploration_mark_list = self.exploration_mark_list
        for current_exploration_mark in copy_exploration_mark_list:
            current_exploration_mark.remove()
        self.exploration_mark_list = []
            
    def remove(self):
        super().remove()
        for current_veteran_icon in self.veteran_icons:
            current_veteran_icon.remove()

class tile_class(actor): #to do: make terrain tiles a subclass
    '''like an obstacle without a tooltip or movement blocking'''
    def __init__(self, coordinates, grid, image, name, modes, show_terrain, global_manager): #show_terrain is like a subclass, true is terrain tile, false is non-terrain tile
        super().__init__(coordinates, [grid], modes, global_manager)
        self.set_name(name)
        self.global_manager.get('tile_list').append(self)
        self.image_dict = {'default': image}
        self.image = images.tile_image(self, self.grid.get_cell_width(), self.grid.get_cell_height(), grid, 'default', global_manager)
        self.images = [self.image] #tiles only appear on 1 grid, have images defined to be more consistent with other actor subclasses
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
        self.global_manager.set('image_list', utility.remove_from_list(self.global_manager.get('image_list'), self.image)) #to do: see if this can be removed, should already be in actor
        #self.global_manager.set('image_list', utility.remove_from_list(self.global_manager.get('image_list'), self.shader))
        #print('removing')
        #self.cell.tile = 'none'
        #to do: this remove function is being called incorrectly at some point in the program, causing tiles to be removed

    def can_show_tooltip(self): #tiles don't have tooltips, except for terrain tiles
        if self.show_terrain == True:
            if self.touching_mouse() and self.global_manager.get('current_game_mode') in self.modes: #and not targeting_ability
                if self.cell.terrain == 'none':
                    return(False)
                else:
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
