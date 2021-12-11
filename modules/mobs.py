#Contains functionality for mobs

import pygame
import time
from . import images
from . import text_tools
from . import utility
from . import actor_utility
from .actors import actor

class mob(actor):
    '''
    Actor that can be controlled and selected and can appear on multiple grids at once
    '''
    def __init__(self, from_save, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates on one of the game grids
                'grids': grid list value - grids in which this mob's images can appear
                'image': string value - File path to the image used by this object
                'name': string value - Required if from save, this mob's name
                'modes': string list value - Game modes during which this mob's images can appear
                'end_turn_destination': string or int tuple value - Required if from save, 'none' if no saved destination, destination coordinates if saved destination
                'end_turn_destination_grid_type': string - Required if end_turn_destination is not 'none', matches the global manager key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - Required if from save, how many movement points this actor currently has
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.selected = False
        self.in_group = False
        self.in_vehicle = False
        self.in_building = False
        self.veteran = False
        self.actor_type = 'mob'
        super().__init__(from_save, input_dict, global_manager)
        self.image_dict = {'default': input_dict['image']}
        self.selection_outline_color = 'bright green'
        self.images = []
        for current_grid in self.grids:
            self.images.append(images.mob_image(self, current_grid.get_cell_width(), current_grid.get_cell_height(), current_grid, 'default', self.global_manager))#self, actor, width, height, grid, image_description, global_manager
        global_manager.get('mob_list').append(self)
        self.set_name(input_dict['name'])
        self.can_explore = False #if can attempt to explore unexplored areas
        self.can_construct = False #if can construct buildings
        self.can_trade = False #if can trade or create trading posts
        self.can_convert = False #if can convert natives or build missions
        self.can_swim = False #if can enter water areas without ships in them
        self.can_walk = True #if can enter land areas
        self.travel_possible = False #if can switch theatres
        self.is_vehicle = False
        self.is_worker = False
        self.is_officer = False
        self.is_work_crew = False
        self.is_group = False
        
        self.max_movement_points = 1
        self.movement_cost = 1
        self.has_infinite_movement = False
        self.set_controlling_minister_type('none')
        if from_save:
            if not input_dict['end_turn_destination'] == 'none': #end turn destination is a tile and can't be pickled, need to find it again after loading
                end_turn_destination_x, end_turn_destination_y = input_dict['end_turn_destination']
                end_turn_destination_grid = self.global_manager.get(input_dict['end_turn_destination_grid_type'])
                self.end_turn_destination = end_turn_destination_grid.find_cell(end_turn_destination_x, end_turn_destination_y).tile
            else:
                self.end_turn_destination = 'none'
            self.set_movement_points(input_dict['movement_points'])
            self.update_tooltip()
        else:
            self.end_turn_destination = 'none'
            self.reset_movement_points()
            self.update_tooltip()
            actor_utility.deselect_all(self.global_manager)
            self.select()
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), self.images[0].current_cell.tile)

    def check_if_minister_appointed(self):
        '''
        Description:
            Returns whether there is currently an appointed minister to control this unit
        Input:
            None
        Output:
            boolean: Returns whether there is currently an appointed minister to control this unit
        '''
        if not self.controlling_minister == 'none':
            return(True)
        else:
            keyword = self.global_manager.get('minister_type_dict')[self.controlling_minister_type]
            text_tools.print_to_screen("", self.global_manager)
            text_tools.print_to_screen("You can not do " + keyword + " actions because a " + self.controlling_minister_type + " has not been appointed", self.global_manager)
            text_tools.print_to_screen("Press q or the button in the upper left corner of the screen to manage your ministers", self.global_manager)
            return(False)

    def set_controlling_minister_type(self, new_type):
        '''
        Description:
            Sets the type of minister that controls this unit, like "Minister of Trade"
        Input:
            Type of minister to control this unit, like "Minister of Trade"
        Output:
            None
        '''
        self.controlling_minister_type = new_type
        self.update_controlling_minister()

    def update_controlling_minister(self):
        '''
        Description:
            Sets the minister that controls this unit to the one occupying the office that has authority over this unit
        Input:
            None
        Output:
            None
        '''
        if self.controlling_minister_type == 'none':
            self.controlling_minister = 'none'
        else:
            self.controlling_minister = self.global_manager.get('current_ministers')[self.controlling_minister_type]

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
                'end_turn_destination': string or int tuple value- 'none' if no saved destination, destination coordinates if saved destination
                'end_turn_destination_grid_type': string value - Required if end_turn_destination is not 'none', matches the global manager key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - How many movement points this actor currently has
                'image': string value - File path to the image used by this object
        '''
        save_dict = super().to_save_dict()
        save_dict['movement_points'] = self.movement_points
        if self.end_turn_destination == 'none':
            save_dict['end_turn_destination'] = 'none'
        else: #end turn destination is a tile and can't be pickled, need to save its location to find it again after loading
            if self.end_turn_destination.grid == self.global_manager.get('strategic_map_grid'):
                save_dict['end_turn_destination_grid_type'] = 'strategic_map_grid'
            elif self.end_turn_destination.grid == self.global_manager.get('europe_grid'):
                save_dict['end_turn_destination_grid_type'] = 'europe_grid'
            save_dict['end_turn_destination'] = (self.end_turn_destination.x, self.end_turn_destination.y)
        save_dict['image'] = self.image_dict['default']
        return(save_dict)
        

    def get_movement_cost(self, x_change, y_change):
        '''
        Description:
            Returns the cost in movement points of moving by the inputted amounts. Only works when one inputted amount is 0 and the other is 1 or -1, with 0 and -1 representing moving 1 cell downward
        Input:
            int x_change: How many cells would be moved to the right in the hypothetical movement
            int y_change: How many cells would be moved upward in the hypothetical movement
        Output:
            double: How many movement points would be spent by moving by the inputted amount
        '''
        local_cell = self.images[0].current_cell
        if local_cell.has_road() or local_cell.has_railroad(): #if not local_infrastructure == 'none':
            direction = 'non'
            if x_change < 0:
                direction = 'left'
            elif x_change > 0:
                direction = 'right'
            elif y_change > 0:
                direction = 'up'
            elif y_change < 0:
                direction = 'down'
            adjacent_cell = self.images[0].current_cell.adjacent_cells[direction]
            if adjacent_cell.has_road() or adjacent_cell.has_railroad(): #if not adjacent_infrastructure == 'none':
                return(self.movement_cost / 2.0)
        return(self.movement_cost)

    def adjacent_to_water(self):
        '''
        Description:
            Returns whether any of the cells directly adjacent to this mob's cell has the water terrain. Otherwise, returns False
        Input:
            None
        Output:
            boolean: Returns True if any of the cells directly adjacent to this mob's cell has the water terrain. Otherwise, returns False
        '''
        for current_cell in self.images[0].current_cell.adjacent_list:
            if current_cell.terrain == 'water':
                return(True)
        return(False)

    def end_turn_move(self):
        '''
        Description:
            If this mob has any pending movement orders at the end of the turn, this executes the movement. Currently used to move ships between Africa and Europe at the end of the turn
        Input:
            None
        Output:
            None
        '''
        if not self.end_turn_destination == 'none':
            if self.grids[0] in self.end_turn_destination.grids: #if on same grid
                nothing = 0 #do later
            else: #if on different grid
                if self.can_travel():
                    self.go_to_grid(self.end_turn_destination.grids[0], (self.end_turn_destination.x, self.end_turn_destination.y))
            self.end_turn_destination = 'none'
    
    def can_travel(self): #if can move between Europe, Africa, etc.
        '''
        Description:
            Returns whether this mob can cross the ocean, like going between Africa and Europe. By default, mobs cannot cross the ocean, but subclasses like ship are able to return True
        Input:
            None
        Output:
            boolean: Returns True if this mob can cross the ocean, otherwise returns False
        '''
        return(False) #different for subclasses

    def change_movement_points(self, change):
        '''
        Description:
            Changes this mob's movement points by the inputted amount. Ensures that the mob info display is updated correctly and that whole number movement point amounts are not shown as decimals
        Input:
            None
        Output:
            None
        '''
        if not self.has_infinite_movement:
            self.movement_points += change
            if self.movement_points == round(self.movement_points): #if whole number, don't show decimal
                self.movement_points = round(self.movement_points)
            if self.global_manager.get('displayed_mob') == self: #update mob info display to show new movement points
                actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self)

    def set_movement_points(self, new_value):
        '''
        Description:
            Sets this mob's movement points to the inputted amount. Ensures that the mob info display is updated correctly and that whole number movement point amounts are not shown as decimals
        Input:
            None
        Output:
            None
        '''
        self.movement_points = new_value
        if self.movement_points == round(self.movement_points): #if whole number, don't show decimal
            self.movement_points = round(self.movement_points)
        if self.global_manager.get('displayed_mob') == self:
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self)

    def reset_movement_points(self):
        '''
        Description:
            Sets this mob's movement points to its maximum number of movement points at the end of the turn. Ensures that the mob info display is updated correctly and that whole number movement point amounts are not shown as decimals
        Input:
            None
        Output:
            None
        '''
        self.movement_points = self.max_movement_points
        if self.movement_points == round(self.movement_points): #if whole number, don't show decimal
            self.movement_points = round(self.movement_points)
        if self.global_manager.get('displayed_mob') == self:
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self)

    def set_max_movement_points(self, new_value):
        '''
        Description:
            Sets this mob's maximum number of movement points and changes its current movement points to the maximum amount
        Input:
            None
        Output:
            None
        '''
        self.max_movement_points = new_value
        self.set_movement_points(new_value)

    def change_inventory(self, commodity, change):
        '''
        Description:
            Changes the number of commodities of a certain type held by this mob. Also ensures that the mob info display is updated correctly
        Input:
            string commodity: Type of commodity to change the inventory of
            int change: Amount of commodities of the inputted type to add. Removes commodities of the inputted type if negative
        Output:
            None
        '''
        if self.can_hold_commodities:
            self.inventory[commodity] += change
            if self.global_manager.get('displayed_mob') == self:
                actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self)

    def set_inventory(self, commodity, new_value):
        '''
        Description:
            Sets the number of commodities of a certain type held by this mob. Also ensures that the mob info display is updated correctly
        Input:
            string commodity: Type of commodity to set the inventory of
            int new_value: Amount of commodities of the inputted type to set inventory to
        Output:
            None
        '''
        if self.can_hold_commodities:
            self.inventory[commodity] = new_value
            if self.global_manager.get('displayed_mob') == self:
                actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self)

    def go_to_grid(self, new_grid, new_coordinates):
        '''
        Description:
            Links this mob to a grid, causing it to appear on that grid and its minigrid at certain coordinates. Used when crossing the ocean and when a mob that was previously attached to another actor becomes independent and visible,
                like when a building's worker leaves
        Input:
            grid new_grid: grid that this mob is linked to
            int tuple new_coordinates: Two values representing x and y coordinates to start at on the inputted grid
        Output:
            None
        '''
        if new_grid == self.global_manager.get('europe_grid'):
            self.modes.append('europe')
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), 'none')
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), new_grid.cell_list[0].tile)
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
        Description:
            Selects this mob, causing this mob to be shown in the mob display and causing a selection outline to appear around it 
        Input:
            None
        Output:
            None
        '''
        actor_utility.deselect_all(self.global_manager)
        self.selected = True
        self.global_manager.set('show_selection_outlines', True)
        self.global_manager.set('last_selection_outline_switch', time.time())#outlines should be shown immediately when selected
        actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self)

    def draw_outline(self):
        '''
        Description:
            Draws a flashing outline around this mob if it is selected
        Input:
            None
        Output:
            None
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
        Description:
            Sets this mob's tooltip to what it should be whenever the player looks at the tooltip. By default, sets tooltip to this actor's name and its movement points
        Input:
            None
        Output:
            None
        '''
        tooltip_list = []
        tooltip_list.append("Name: " + self.name.capitalize())
        if not self.has_infinite_movement:
            tooltip_list.append("Movement points: " + str(self.movement_points) + "/" + str(self.max_movement_points))
        else:
            tooltip_list.append("Movement points: infinite")
        self.set_tooltip(tooltip_list)
        

    def remove(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program. Also deselects this mob and drops any commodities it is carrying
        Input:
            None
        Output:
            None
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

    def die(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program. Used instead of remove to improve consistency with groups/vehicles, whose die and remove have different
                functionalities
        Input:
            None
        Output:
            None
        '''
        self.remove()

    def can_leave(self):
        '''
        Description:
            Returns whether this mob is allowed to move away from its current cell. By default, mobs can always allowed to move away from their current cells, but subclasses like ship are able to return False
        Input:
            None
        Output:
            boolean: Returns True
        '''
        return(True) #different in subclasses, controls whether anything in starting tile would prevent leaving, while can_move sees if anything in destination would prevent entering

    def can_move(self, x_change, y_change):
        '''
        Description:
            Returns whether this mob can move to the tile x_change to the right of it and y_change above it. Movement can be prevented by not being able to move on water/land, the edge of the map, limited movement points, etc.
        Input:
            int x_change: How many cells would be moved to the right in the hypothetical movement
            int y_change: How many cells would be moved upward in the hypothetical movement
        Output:
            boolean: Returns True if this mob can move to the proposed destination, otherwise returns False
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
                            (destination_type == 'water' and (self.can_swim or (future_cell.has_vehicle('ship') and not self.is_vehicle) or (self.can_explore and not future_cell.visible)))): 
                            if self.movement_points >= self.get_movement_cost(x_change, y_change) or self.has_infinite_movement and self.movement_points > 0: #self.movement_cost:
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
        Description:
            Moves this mob x_change to the right and y_change upward. Moving to a ship in the water automatically embarks the ship
        Input:
            int x_change: How many cells are moved to the right in the movement
            int y_change: How many cells are moved upward in the movement
        Output:
            None
        '''
        self.end_turn_destination = 'none' #cancels planned movements
        self.change_movement_points(-1 * self.get_movement_cost(x_change, y_change))
        for current_image in self.images:
            current_image.remove_from_cell()
        self.x += x_change
        self.y += y_change
        self.global_manager.get('minimap_grid').calibrate(self.x, self.y)
        for current_image in self.images:
            current_image.add_to_cell()
        if self.images[0].current_cell.has_vehicle('ship') and (not self.is_vehicle) and self.images[0].current_cell.terrain == 'water': #board if moving to ship in water
            self.selected = False
            vehicle = self.images[0].current_cell.get_vehicle('ship')
            if self.is_worker and not vehicle.has_crew:
                self.crew_vehicle(vehicle)
            else:
                self.embark_vehicle(vehicle)
            vehicle.select()

    def touching_mouse(self):
        '''
        Description:
            Returns whether any of this mob's images is colliding with the mouse. Also ensures that no hidden images outside of the minimap are considered as colliding
        Input:
            None
        Output:
            boolean: True if any of this mob's images is colliding with the mouse, otherwise return False
        '''
        for current_image in self.images:
            if current_image.Rect.collidepoint(pygame.mouse.get_pos()): #if mouse is in image
                if not (current_image.grid == self.global_manager.get('minimap_grid') and not current_image.grid.is_on_mini_grid(self.x, self.y)): #do not consider as touching mouse if off-map
                    return(True)
        return(False)

    def set_name(self, new_name):
        '''
        Description:
            Sets this mob's name. Also updates the mob info display to show the new name
        Input:
            string new_name: Name to set this mob's name to
        Output:
            None
        '''
        super().set_name(new_name)
        if self.global_manager.get('displayed_mob') == self: #self.selected:
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self)

    def can_show_tooltip(self):
        '''
        Description:
            Returns whether this mob's tooltip can be shown. Along with the superclass' requirements, mob tooltips can not be shown when attached to another actor, such as when working in a building
        Input:
            None
        Output:
            None
        '''
        if self.in_vehicle or self.in_group or self.in_building:
            return(False)
        else:
            return(super().can_show_tooltip())

    def hide_images(self):
        '''
        Description:
            Hides this mob's images, allowing it to be hidden but still stored at certain coordinates when it is attached to another actor or otherwise not visible
        Input:
            None
        Output:
            None
        '''
        for current_image in self.images:
            current_image.remove_from_cell()

    def show_images(self):
        '''
        Description:
            Shows this mob's images at its stored coordinates, allowing it to be visible after being attached to another actor or otherwise not visible
        Input:
            None
        Output:
            None
        '''
        for current_image in self.images:
            current_image.add_to_cell()        

    def embark_vehicle(self, vehicle):
        '''
        Description:
            Hides this mob and embarks it on the inputted vehicle as a passenger. Any commodities held by this mob are put on the vehicle if there is cargo space, or dropped in its tile if there is no cargo space
        Input:
            vehicle vehicle: vehicle that this mob becomes a passenger of
        Output:
            None
        '''
        self.in_vehicle = True
        self.selected = False
        for current_commodity in self.get_held_commodities(): #gives inventory to ship
            num_held = self.get_inventory(current_commodity)
            for current_commodity_unit in range(num_held):
                if vehicle.get_inventory_remaining() > 0:
                    vehicle.change_inventory(current_commodity, 1)
                else:
                    self.images[0].current_cell.tile.change_inventory(current_commodity, 1)
        self.hide_images()
        vehicle.contained_mobs.append(self)
        self.inventory_setup() #empty own inventory
        vehicle.hide_images()
        vehicle.show_images() #moves vehicle images to front
        if not vehicle.initializing: #don't select vehicle if loading in at start of game
            vehicle.select()

    def disembark_vehicle(self, vehicle):
        '''
        Description:
            Shows this mob and disembarks it from the inputted vehicle after being a passenger
        Input:
            vehicle vehicle: vehicle that this mob disembarks from
        Output:
            None
        '''
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

