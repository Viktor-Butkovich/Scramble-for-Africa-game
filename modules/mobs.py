import pygame
import time
#import random #test showing how to add to inventory
from . import images
from . import text_tools
from . import utility
from . import actor_utility
from .actors import actor
from .tiles import veteran_icon

class mob(actor):
    '''
    Actor that can be controlled and selected and can appear on multiple grids at once
    '''
    def __init__(self, coordinates, grids, image_id, name, modes, global_manager):
        '''
        Input:
            coordinates: tuple of two int variables representing the pixel coordinates of the bottom left of the notification
            grids: list of grid objects on which the mob's images will appear
            image_id: string representing the file path to the mob's default image
            name: string representing the mob's name
            modes: list of strings representing the game modes in which the mob can appear
            global_manager: global_manager_template object used to manage a dictionary of shared variables
        '''
        self.selected = False
        self.in_group = False
        self.in_vehicle = False
        self.in_building = False
        self.actor_type = 'mob'
        super().__init__(coordinates, grids, modes, global_manager)
        self.image_dict = {'default': image_id}
        self.selection_outline_color = 'bright green'
        self.images = []
        for current_grid in self.grids:
            self.images.append(images.mob_image(self, current_grid.get_cell_width(), current_grid.get_cell_height(), current_grid, 'default', self.global_manager))#self, actor, width, height, grid, image_description, global_manager
        global_manager.get('mob_list').append(self)
        self.set_name(name)
        self.can_explore = False #if can attempt to explore unexplored areas
        self.can_construct = False #if can construct buildings
        self.can_swim = False #if can enter water areas without ships in them
        self.can_walk = True #if can enter land areas
        self.travel_possible = False #if can switch theatres
        self.is_vehicle = False
        self.is_worker = False
        self.is_officer = False
        self.is_group = False
        self.end_turn_destination = 'none'
        self.max_movement_points = 1
        self.movement_cost = 1
        self.reset_movement_points()
        self.update_tooltip()
        actor_utility.deselect_all(self.global_manager)
        self.select()
        actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), self.images[0].current_cell.tile)

    def get_movement_cost(self, x_change, y_change):
        local_infrastructure = self.images[0].current_cell.contained_buildings['infrastructure']
        if not local_infrastructure == 'none':
            direction = 'non'
            if x_change < 0:
                direction = 'left'
            elif x_change > 0:
                direction = 'right'
            elif y_change > 0:
                direction = 'up'
            elif y_change < 0:
                direction = 'down'
            adjacent_infrastructure = self.images[0].current_cell.adjacent_cells[direction].contained_buildings['infrastructure']
            if not adjacent_infrastructure == 'none':
                return(self.movement_cost / 2.0)
        return(self.movement_cost)

    def adjacent_to_water(self):
        for current_cell in self.images[0].current_cell.adjacent_list:
            if current_cell.terrain == 'water':
                return(True)
        return(False)

    def end_turn_move(self):
        if not self.end_turn_destination == 'none':
            if self.grids[0] in self.end_turn_destination.grids: #if on same grid
                nothing = 0 #do later
            else: #if on different grid
                if self.can_travel():
                    self.go_to_grid(self.end_turn_destination.grids[0], (self.end_turn_destination.x, self.end_turn_destination.y))
            self.end_turn_destination = 'none'
    
    def can_travel(self): #if can move between Europe, Africa, etc.
        return(False) #different for subclasses

    def change_movement_points(self, change):
        self.movement_points += change
        if self.movement_points == round(self.movement_points): #if whole number, don't show decimal
            self.movement_points = round(self.movement_points)
        if self.global_manager.get('displayed_mob') == self: #update mob info display to show new movement points
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self)

    def set_movement_points(self, new_value):
        self.movement_points = new_value
        if self.movement_points == round(self.movement_points): #if whole number, don't show decimal
            self.movement_points = round(self.movement_points)
        if self.global_manager.get('displayed_mob') == self:
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self)

    def reset_movement_points(self):
        self.movement_points = self.max_movement_points
        if self.movement_points == round(self.movement_points): #if whole number, don't show decimal
            self.movement_points = round(self.movement_points)
        if self.global_manager.get('displayed_mob') == self:
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self)

    def set_max_movement_points(self, new_value):
        self.max_movement_points = new_value
        self.set_movement_points(new_value)

    def change_inventory(self, commodity, change):
        '''
        Input:
            same as superclass
        Output:
            same as superclass, except, if currently being shown in the mob info display, updates the displayed commodities to reflect the change
        '''
        if self.can_hold_commodities:
            self.inventory[commodity] += change
            if self.global_manager.get('displayed_mob') == self:
                actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self)

    def set_inventory(self, commodity, new_value):
        '''
        Input:
            same as superclass
        Output:
            same as superclass, except, if currently being shown in the mob info display, updates the displayed commodities to reflect the change
        '''
        if self.can_hold_commodities:
            self.inventory[commodity] = new_value
            if self.global_manager.get('displayed_mob') == self:
                actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self)

    def go_to_grid(self, new_grid, new_coordinates):
        '''
        Input:
            grid object representing the grid to which the mob is transferring, tuple of two int variables representing the coordinates to which the mob will move on the new grid
        Output:
            Moves this mob and all of its images to the inputted grid at the inputted coordinates
        '''
        if new_grid == self.global_manager.get('europe_grid'):
            self.modes.append('europe')
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), 'none')
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), new_grid.cell_list[0].tile)
            #actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), new_grid.cell_list[0].tile)
        else: #if mob was spawned in Europe, make it so that it does not appear in the Europe screen after leaving
            self.modes = utility.remove_from_list(self.modes, 'europe')
        self.x, self.y = new_coordinates
        for current_image in self.images:
            current_image.remove_from_cell()
            self.global_manager.set('image_list', utility.remove_from_list(self.global_manager.get('image_list'), current_image))
        self.grids = [new_grid]
        self.grid = new_grid
        if not new_grid.mini_grid == 'none':
            new_grid.mini_grid.calibrate(new_coordinates[0], new_coordinates[1])
            self.grids.append(new_grid.mini_grid)
        self.images = []
        for current_grid in self.grids:
            self.images.append(images.mob_image(self, current_grid.get_cell_width(), current_grid.get_cell_height(), current_grid, 'default', self.global_manager))
            self.images[-1].add_to_cell()

    def select(self):
        '''
        Input:
            none
        Output:
            Causes this mob to be selected and causes the selection outline timer to be reset, displaying it immediately
        '''
        actor_utility.deselect_all(self.global_manager)
        self.selected = True
        self.global_manager.set('show_selection_outlines', True)
        self.global_manager.set('last_selection_outline_switch', time.time())#outlines should be shown immediately when selected
        #if self.images[0].current_cell.contained_mobs[0] == self: #only calibrate actor info if top of stack
        actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self)
            #actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), self.images[0].current_cell.tile)

    def draw_outline(self):
        '''
        Input:
            none
        Output:
            If selection outlines are currently allowed to appear and if this mob is showing, draw a selection outline around each of its images
        '''
        if self.global_manager.get('show_selection_outlines'):
            for current_image in self.images:
                if not current_image.current_cell == 'none' and self == current_image.current_cell.contained_mobs[0]: #only draw outline if on top of stack
                    pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')[self.selection_outline_color], (current_image.outline), current_image.outline_width)
            if (not self.end_turn_destination == 'none') and self.end_turn_destination.images[0].can_show(): #only show outline if tile is showing
                self.end_turn_destination.draw_destination_outline()
                equivalent_tile = self.end_turn_destination.get_equivalent_tile()
                if not equivalent_tile == 'none':
                    equivalent_tile.draw_destination_outline()
        
    def update_tooltip(self):
        '''
        Input:
            none
        Output:
            Sets this mob's tooltip to its name and movement points
        '''
        self.set_tooltip(["Name: " + self.name, "Movement points: " + str(self.movement_points) + "/" + str(self.max_movement_points)])
        

    def remove(self):
        '''
        Input:
            none
        Output:
            Removes the object from relevant lists and prevents it from further appearing in or affecting the program
        '''
        if (not self.images[0].current_cell == 'none') and (not self.images[0].current_cell.tile == 'none'): #drop inventory on death
            current_tile = self.images[0].current_cell.tile
            for current_commodity in self.global_manager.get('commodity_types'):
                current_tile.change_inventory(current_commodity, self.get_inventory(current_commodity))
        if self.selected:
            self.selected = False
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), 'none')
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), 'none')
        for current_image in self.images:
            current_image.remove_from_cell()
        super().remove()
        self.global_manager.set('mob_list', utility.remove_from_list(self.global_manager.get('mob_list'), self)) #make a version of mob_list without self and set mob_list to it

    def can_leave(self):
        return(True) #different in subclasses, controls whether anything in starting tile would prevent leaving, while can_move sees if anything in destination would prevent entering

    def can_move(self, x_change, y_change):
        '''
        Input:
            int representing the distance moved to the right from a proposed movement, int representing the distance moved upward from a proposed movement
        Output:
            Returns whether the proposed movement would be possible
        '''
        future_x = self.x + x_change
        future_y = self.y + y_change
        if self.can_leave():
            if not self.grid in self.global_manager.get('abstract_grid_list'):
                if future_x >= 0 and future_x < self.grid.coordinate_width and future_y >= 0 and future_y < self.grid.coordinate_height:
                    future_cell = self.grid.find_cell(future_x, future_y)
                    if future_cell.visible or self.can_explore:
                        destination_type = 'land'
                        if future_cell.terrain == 'water':
                            destination_type = 'water' #if can move to destination, possible to move onto ship in water, possible to 'move' into non-visible water while exploring
                        if ((destination_type == 'land' and (self.can_walk or self.can_explore or (future_cell.has_port() and self.images[0].current_cell.terrain == 'water'))) or
                            (destination_type == 'water' and (self.can_swim or future_cell.has_vehicle() or (self.can_explore and not future_cell.visible)))): 
                            if self.movement_points >= self.get_movement_cost(x_change, y_change): #self.movement_cost:
                                return(True)
                            else:
                                text_tools.print_to_screen("You do not have enough movement points to move.", self.global_manager)
                                text_tools.print_to_screen("You have " + str(self.movement_points) + " movement points while " + str(self.get_movement_cost(x_change, y_change)) + " are required.", self.global_manager)
                                return(False)
                        elif destination_type == 'land' and not self.can_walk: #if trying to walk on land and can't
                            #if future_cell.visible or self.can_explore: #already checked earlier
                            text_tools.print_to_screen("You can not move on land with this unit unless there is a port.", self.global_manager)
                            return(False)
                        else: #if trying to swim in water and can't 
                            #if future_cell.visible or self.can_explore: #already checked earlier
                            text_tools.print_to_screen("You can not move on water with this unit.", self.global_manager)
                            return(False)
                    else:
                        text_tools.print_to_screen("You can not move into an unexplored tile.", self.global_manager)
                        return(False)
                else:
                    text_tools.print_to_screen("You can not move off of the map.", self.global_manager)
                    return(False)
            else:
                text_tools.print_to_screen("You can not move while in this area.", self.global_manager)
                return(False)

    def move(self, x_change, y_change):
        '''
        Input:
            int representing the distance moved to the right, int representing the distance moved upward
        Output:
            Moves this mob x_change tiles to the right and y_change tiles upward
        '''
        self.end_turn_destination = 'none' #cancels planned movements
        self.change_movement_points(-1 * self.get_movement_cost(x_change, y_change))
        for current_image in self.images:
            current_image.remove_from_cell()
        self.x += x_change
        self.y += y_change
        #self.inventory['coffee'] += 1 #test showing how to add to inventory
        self.global_manager.get('minimap_grid').calibrate(self.x, self.y)
        for current_image in self.images:
            current_image.add_to_cell()
        if self.images[0].current_cell.has_vehicle() and (not self.is_vehicle) and self.images[0].current_cell.terrain == 'water': #board if moving to ship in water
            self.selected = False
            vehicle = self.images[0].current_cell.get_vehicle()
            if self.is_worker and not vehicle.has_crew:
                self.crew_vehicle(vehicle)
            else:
                self.embark_vehicle(vehicle)
            vehicle.select()
            
        #self.change_inventory(random.choice(self.global_manager.get('commodity_types')), 1) #test showing how to add to inventory

    def touching_mouse(self):
        '''
        Input:
            none
        Output:
            Returns whether any of this mob's images are colliding with the mouse
        '''
        for current_image in self.images:
            if current_image.Rect.collidepoint(pygame.mouse.get_pos()): #if mouse is in image
                if not (current_image.grid == self.global_manager.get('minimap_grid') and not current_image.grid.is_on_mini_grid(self.x, self.y)): #do not consider as touching mouse if off-map
                    return(True)
        return(False) #return false if none touch mouse

    def set_name(self, new_name):
        '''
        Input:
            same as superclass
        Output:
            same as superclass, except, if currently being shown in the mob info display, updates the displayed name 
        '''
        super().set_name(new_name)
        if self.global_manager.get('displayed_mob') == self: #self.selected:
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self)

    def can_show_tooltip(self):
        if self.in_vehicle or self.in_group or self.in_building:
            return(False)
        else:
            return(super().can_show_tooltip())

    def hide_images(self):
        for current_image in self.images:
            current_image.remove_from_cell()

    def show_images(self):
        for current_image in self.images:
            current_image.add_to_cell()        

    def embark_vehicle(self, vehicle):
        self.in_vehicle = True
        self.selected = False
        self.hide_images()
        vehicle.contained_mobs.append(self)
        for current_commodity in self.global_manager.get('commodity_types'): #gives inventory to ship
            vehicle.change_inventory(current_commodity, self.get_inventory(current_commodity))
        self.inventory_setup() #empty own inventory
        vehicle.hide_images()
        vehicle.show_images() #moves vehicle images to front
        actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), vehicle)

    def disembark_vehicle(self, vehicle):
        vehicle.contained_mobs = utility.remove_from_list(vehicle.contained_mobs, self)
        self.in_vehicle = False
        self.x = vehicle.x
        self.y = vehicle.y
        for current_image in self.images:
            current_image.add_to_cell()
        vehicle.selected = False
        self.select()
        if self.global_manager.get('minimap_grid') in self.grids:
            self.global_manager.get('minimap_grid').calibrate(self.x, self.y)
        actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), self.images[0].current_cell.tile)
        #vehicle.contained_mobs = utility.remove_from_list(vehicle.contained_mobs, self)

