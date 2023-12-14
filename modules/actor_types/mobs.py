#Contains functionality for mobs

import pygame, random
from ..constructs import images
from ..util import utility, actor_utility, main_loop_utility, text_utility
from .actors import actor
import modules.constants.constants as constants
import modules.constants.status as status
import modules.constants.flags as flags
from typing import List

class mob(actor):
    '''
    Actor that can be selected and move within and between grids, but cannot necessarily controlled
    '''
    def __init__(self, from_save, input_dict):
        '''
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates on one of the game grids
                'grids': grid list value - grids in which this mob's images can appear
                'image': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'name': string value - Required if from save, this mob's name
                'modes': string list value - Game modes during which this mob's images can appear
                'movement_points': int value - Required if from save, how many movement points this actor currently has
                'max_movement_points': int value - Required if from save, maximum number of movement points this mob can have
        Output:
            None
        '''
        self.is_dummy = False
        self.in_group = False
        self.in_vehicle = False
        self.in_building = False
        self.veteran = False
        self.disorganized = False
        self.is_vehicle = False
        self.is_worker = False
        self.is_officer = False
        self.is_work_crew = False
        self.is_battalion = False
        self.is_safari = False
        self.is_group = False
        self.is_npmob = False
        self.is_pmob = False
        self.can_explore = False #if can attempt to explore unexplored areas
        self.can_construct = False #if can construct buildings
        self.can_trade = False #if can trade or create trading posts
        self.can_convert = False #if can convert natives or build missions
        self.number = 1 #how many entities are in a unit, used for verb conjugation
        self.actor_type = 'mob'
        self.end_turn_destination = 'none'
        super().__init__(from_save, input_dict)
        if isinstance(input_dict['image'], str):
            self.image_dict = {'default': input_dict['image']}
        else:
            self.image_dict = {'default': input_dict['image']['image_id']}
        self.image_variants_setup(from_save, input_dict)
        self.images = []
        self.status_icons = []
        for current_grid in self.grids:
            self.images.append(images.mob_image(self, current_grid.get_cell_width(), current_grid.get_cell_height(), current_grid, 'default'))
        status.mob_list.append(self)
        self.set_name(input_dict['name'])
        self.can_swim = False #if can enter water areas without ships in them
        self.can_swim_river = False
        self.can_swim_ocean = False
        self.can_walk = True #if can enter land areas
        self.set_has_canoes(False)
        self.max_movement_points = 1
        self.movement_points = self.max_movement_points
        self.movement_cost = 1
        self.has_infinite_movement = False
        self.temp_movement_disabled = False
        #self.default_interface_tab = 'reorganization'
        if from_save:
            self.set_max_movement_points(input_dict['max_movement_points'])
            self.set_movement_points(input_dict['movement_points'])
            self.update_tooltip()
            self.creation_turn = input_dict['creation_turn']
            if input_dict['disorganized']:
                self.set_disorganized(True)
        else:
            self.reset_movement_points()
            self.update_tooltip()
            if flags.creating_new_game:
                self.creation_turn = 0
            else:
                self.creation_turn = constants.turn

    def image_variants_setup(self, from_save, input_dict):
        '''
        Description:
            Sets up this unit's image variants
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
        Output:
            None
        '''
        self.image_variants = actor_utility.get_image_variants(self.image_dict['default'])
        if self.image_dict['default'].endswith('default.png') and not from_save:
            if not from_save:
                self.image_variant = random.randrange(0, len(self.image_variants))
                self.image_dict['default'] = self.image_variants[self.image_variant]
        elif from_save and 'image_variant' in input_dict:
            self.image_variant = input_dict['image_variant']
            self.image_dict['default'] = self.image_variants[self.image_variant]
            if 'second_image_variant' in input_dict:
                self.second_image_variant = input_dict['second_image_variant']

    def to_save_dict(self):
        '''
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
                Along with superclass outputs, also saves the following values:
                'movement_points': int value - How many movement points this mob currently has
                'max_movement_points': int value - Maximum number of movement points this mob can have
                'image': string value - File path to the image used by this mob
                'creation_turn': int value - Turn number on which this mob was created
                'disorganized': boolean value - Whether this unit is currently disorganized
                'canoes_image': string value - Only saved if this unit has canoes, file path to the image used by this mob when it is in river water
                'image_variant': int value - Optional variants of default image to use from same file, applied to get_image_id_list but not default image path
        '''
        save_dict = super().to_save_dict()
        save_dict['movement_points'] = self.movement_points
        save_dict['max_movement_points'] = self.max_movement_points
        save_dict['image'] = self.image_dict['default'] #self.image_dict['default']
        save_dict['creation_turn'] = self.creation_turn
        save_dict['disorganized'] = self.disorganized
        if hasattr(self, 'image_variant'):
            save_dict['image'] = self.image_variants[0]
            save_dict['image_variant'] = self.image_variant
            if hasattr(self, 'second_image_variant'):
                save_dict['second_image_variant'] = self.second_image_variant
        return(save_dict)        

    def temp_disable_movement(self):
        '''
        Description:
            Sets this unit's movement to 0 for the next turn, preventing it from taking its usual actions
        Input:
            None
        Output:
            None
        '''
        self.temp_movement_disabled = True
    
    def get_image_id_list(self, override_values={}):
        '''
        Description:
            Generates and returns a list this actor's image file paths and dictionaries that can be passed to any image object to display those images together in a particular order and 
                orientation
        Input:
            None
        Output:
            list: Returns list of string image file paths, possibly combined with string key dictionaries with extra information for offset images
        '''
        if 'disorganized' in override_values:
            disorganized = override_values['disorganized']
        else:
            disorganized = self.disorganized
        if 'has_canoes' in override_values:
            has_canoes = override_values['has_canoes']
        else:

            has_canoes = self.has_canoes

        image_id_list = super().get_image_id_list(override_values)
        if disorganized:
            if self.is_npmob and self.npmob_type == 'beast':
                image_id_list.append('misc/injured_icon.png')
            else:
                image_id_list.append('misc/disorganized_icon.png')
        if has_canoes and self.in_canoes:
            image_id_list.append('misc/canoes.png')
        return(image_id_list)

    def set_disorganized(self, new_value):
        '''
        Description:
            Sets this unit to be disorganized or not. Setting it to be disorganized gives a temporary combat debuff and an icon that follows the unit, while removing the disorganized status removes the debuff and the icon
        Input:
            boolean new_value: Represents new disorganized status
        Output:
            None
        '''
        self.disorganized = new_value
        self.update_image_bundle()

    def get_combat_modifier(self, opponent=None, include_tile=False):
        '''
        Description:
            Calculates and returns the modifier added to this unit's combat rolls
        Input:
            None
        Output:
            int: Returns the modifier added to this unit's combat rolls
        '''
        modifier = 0
        if self.is_pmob:
            if self.is_group and self.group_type == 'battalion':
                modifier += 1
                if self.battalion_type == 'imperial':
                    modifier += 1
            else:
                modifier -= 1
                if self.is_officer:
                    modifier -= 1
            if opponent and opponent.npmob_type == 'beast':
                if self.is_group and self.group_type == 'safari':
                    modifier += 3
                else:
                    modifier -= 1
            if include_tile and self.images[0].current_cell.has_intact_building('fort'):
                modifier += 1
        if self.disorganized:
            modifier -= 1
        return(modifier)

    def get_combat_strength(self):
        '''
        Description:
            Calculates and returns this unit's combat strength. While combat strength has no role in combat calculations, it serves as an estimate for the player of the unit's combat capabilities
        Input:
            None
        Output:
            int: Returns this unit's combst strength
        '''
        #A unit with 0 combat strength cannot fight
        #combat modifiers range from -3 (disorganized lone officer) to +2 (imperial battalion), and veteran status should increase strength by 1: range from 0 to 6
        #add 3 to modifier and add veteran bonus to get strength
        #0: lone officer, vehicle
        #1: disorganized workers/civilian group
        #2: veteran lone officer, workers/civilian group, disorganized native warriors
        #3: veteran civilian group, disorganized colonial battalion, native warriors
        #4: colonial battalion, disorganized imperial battalion
        #5: imperial battalion, veteran colonial battalion, disorganized veteran imperial battalion
        #6: veteran imperial battalion
        base = self.get_combat_modifier()
        result = base + 3
        if self.veteran:
            result += 1
        if self.is_officer or (self.is_vehicle and self.crew == 'none'):
            result = 0
        return(result)

    def combat_possible(self):
        '''
        Description:
            Returns whether this unit can start any combats in its current cell. A pmob can start combats with npmobs in its cell, and a hostile npmob can start combats with pmobs in its cell
        Input:
            None
        Output:
            boolean: Returns whether this unit can start any combats in its current cell
        '''
        if self.is_npmob:
            if self.hostile:
                if self.images[0].current_cell == 'none':
                    if self.grids[0].find_cell(self.x, self.y).has_pmob(): #if hidden and in same tile as pmob
                        return(True)
                elif self.images[0].current_cell.has_pmob(): #if visible and in same tile as pmob
                    return(True)
        elif self.is_pmob:
            if self.images[0].current_cell.has_npmob():
                return(True)
        return(False)

    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this unit can be shown. By default, it can be shown when it is in a discovered cell during the correct game mode and is not attached to any other units or buildings
        Input:
            None
        Output:
            boolean: Returns True if this image can appear during the current game mode, otherwise returns False
        '''
        if not (self.in_vehicle or self.in_group or self.in_building):
            if self.images[0].current_cell != 'none' and self.images[0].current_cell.contained_mobs[0] == self and constants.current_game_mode in self.modes:
                if self.images[0].current_cell.visible:
                    return(True)
        return(False)

    def can_show_tooltip(self):
        '''
        Description:
            Returns whether this unit's tooltip can be shown. Along with superclass conditions, requires that it is in a discovered cell
        Input:
            None
        Output:
            None
        '''
        if super().can_show_tooltip():
            if self.images[0].current_cell != 'none':
                if self.images[0].current_cell.visible:
                    return(True)
        return(False)

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
        cost = self.movement_cost
        if not (self.is_npmob and not self.visible()):
            local_cell = self.images[0].current_cell
        else:
            local_cell = self.grids[0].find_cell(self.x, self.y)

        
        direction = 'none'
        if x_change < 0:
            direction = 'left'
        elif x_change > 0:
            direction = 'right'
        elif y_change > 0:
            direction = 'up'
        elif y_change < 0:
            direction = 'down'

        if direction == 'none':
            adjacent_cell = local_cell
        else:
            adjacent_cell = local_cell.adjacent_cells[direction]
            
        if adjacent_cell:
            cost = cost * constants.terrain_movement_cost_dict[adjacent_cell.terrain]
            if self.is_pmob:
                local_infrastructure = local_cell.get_intact_building('infrastructure')
                adjacent_infrastructure = adjacent_cell.get_intact_building('infrastructure')
                #if local_cell.has_building('road') or local_cell.has_building('railroad'): #if not local_infrastructure == 'none':
                #    if adjacent_cell.has_building('road') or adjacent_cell.has_building('railroad'): #if not adjacent_infrastructure == 'none':
                if local_cell.has_walking_connection(adjacent_cell): 
                    if not (local_infrastructure == 'none' or adjacent_infrastructure == 'none'): #if both have infrastructure and connected by land or bridge, use discount
                        cost = cost / 2
                    #otherwise, use default cost but not full no canoe penalty cost
                elif adjacent_cell.terrain == 'water' and adjacent_cell.y > 0 and self.can_walk and not self.can_swim_river: #elif river w/o canoes
                    cost = self.max_movement_points

                if (not adjacent_cell.visible) and self.can_explore:
                    cost = self.movement_cost
        return(cost)

    def can_leave(self):
        '''
        Description:
            Returns whether this mob is allowed to move away from its current cell. By default, mobs are always allowed to move away from their current cells, but subclasses like ship are able to return False
        Input:
            None
        Output:
            boolean: Returns True
        '''
        return(True) #different in subclasses, controls whether anything in starting tile would prevent leaving, while can_move sees if anything in destination would prevent entering

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
            if current_cell.terrain == 'water' and current_cell.visible:
                return(True)
        return(False)

    def adjacent_to_river(self):
        '''
        Description:
            Returns whether any of the cells directly adjacent to this mob's cell has the water terrain above y == 0. Otherwise, returns False
        Input:
            None
        Output:
            boolean: Returns True if any of the cells directly adjacent to this mob's cell has the water terrain above y == 0. Otherwise, returns False
        '''
        for current_cell in self.images[0].current_cell.adjacent_list:
            if current_cell.terrain == 'water' and current_cell.visible and not current_cell.y == 0:
                return(True)
        return(False)

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
            if self.is_pmob and self.movement_points <= 0:
                self.remove_from_turn_queue()
            if status.displayed_mob == self: #update mob info display to show new movement points
                actor_utility.calibrate_actor_info_display(status.mob_info_display, self)

    def set_movement_points(self, new_value):
        '''
        Description:
            Sets this mob's movement points to the inputted amount. Ensures that the mob info display is updated correctly and that whole number movement point amounts are not shown as decimals
        Input:
            None
        Output:
            None
        '''
        if new_value < 0:
            new_value = 0
        self.movement_points = new_value
        if self.movement_points == round(self.movement_points): #if whole number, don't show decimal
            self.movement_points = round(self.movement_points)
        if self.is_pmob and self.movement_points <= 0:
            self.remove_from_turn_queue()
        if status.displayed_mob == self:
            actor_utility.calibrate_actor_info_display(status.mob_info_display, self)

    def reset_movement_points(self):
        '''
        Description:
            Sets this mob's movement points to its maximum number of movement points at the end of the turn. Ensures that the mob info display is updated correctly and that whole number movement point amounts are not shown as decimals
        Input:
            None
        Output:
            None
        '''
        if self.temp_movement_disabled:
            self.temp_movement_disabled = False
            self.movement_points = 0
        else:
            self.movement_points = self.max_movement_points
            if self.movement_points == round(self.movement_points): #if whole number, don't show decimal
                self.movement_points = round(self.movement_points)
            if self.is_pmob and (not self.images[0].current_cell == 'none') and not (self.is_vehicle and self.crew == 'none'):
                self.add_to_turn_queue()
            if status.displayed_mob == self:
                actor_utility.calibrate_actor_info_display(status.mob_info_display, self)

    def set_max_movement_points(self, new_value, initial_setup = True):
        '''
        Description:
            Sets this mob's maximum number of movement points and changes its current movement points by the amount increased or to the maximum, based on the input boolean
        Input:
            boolean initial_setup: Whether to set this current movement points to the max (on recruitment) or change by the amount increased (when increased after recruitment)
        Output:
            None
        '''
        if not initial_setup:
            increase = new_value - self.max_movement_points
        self.max_movement_points = new_value
        if initial_setup:
            self.set_movement_points(new_value)
        else:
            self.set_movement_points(self.movement_points + increase)

    def go_to_grid(self, new_grid, new_coordinates):
        '''
        Description:
            Links this mob to a grid, causing it to appear on that grid and its minigrid at certain coordinates. Used when crossing the ocean and when a mob that was previously attached to another actor becomes independent and visible,
                like when a building's worker leaves. Also moves this unit's status icons as necessary
        Input:
            grid new_grid: grid that this mob is linked to
            int tuple new_coordinates: Two values representing x and y coordinates to start at on the inputted grid
        Output:
            None
        '''
        if new_grid == status.europe_grid:
            self.modes.append('europe')
            actor_utility.calibrate_actor_info_display(status.tile_info_display, None)
            actor_utility.calibrate_actor_info_display(status.tile_info_display, new_grid.cell_list[0][0].tile)
        else: #if mob was spawned in Europe, make it so that it does not appear in the Europe screen after leaving
            self.modes = utility.remove_from_list(self.modes, 'europe')
        self.x, self.y = new_coordinates
        
        old_image_id = self.images[0].image_id
        for current_image in self.images:
            current_image.remove_from_cell()
        self.grids = [new_grid]
        self.grid = new_grid
        if not new_grid.mini_grid == 'none':
            new_grid.mini_grid.calibrate(new_coordinates[0], new_coordinates[1])
            self.grids.append(new_grid.mini_grid)
        self.images = []
        for current_grid in self.grids:
            self.images.append(images.mob_image(self, current_grid.get_cell_width(), current_grid.get_cell_height(), current_grid, old_image_id))
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
        flags.show_selection_outlines = True
        constants.last_selection_outline_switch = constants.current_time
        actor_utility.calibrate_actor_info_display(status.mob_info_display, self)

    def cycle_select(self):
        '''
        Description:
            Selects this mob while also moving it to the front of the tile and playing its selection sound - should be used when unit is clicked on
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible():
            if status.displayed_mob != self:
                self.select()
                if self.is_pmob:
                    self.selection_sound()
                for current_image in self.images: #move mob to front of each stack it is in
                    if current_image.current_cell != 'none':
                        while not self == current_image.current_cell.contained_mobs[0]:
                            current_image.current_cell.contained_mobs.append(current_image.current_cell.contained_mobs.pop(0))
        else:
            text_utility.print_to_screen('You are busy and cannot select a different unit')

    def move_to_front(self):
        '''
        Description:
            Moves the image of this unit to the front of the cell, making it visible and selected first when the cell is clicked
        Input:
            None
        Output:
            None
        '''
        for current_image in self.images:
            current_cell = self.images[0].current_cell
            while not current_cell.contained_mobs[0] == self: #move to front of tile
                current_cell.contained_mobs.append(current_cell.contained_mobs.pop(0))

    def draw_outline(self):
        '''
        Description:
            Draws a flashing outline around this mob if it is selected
        Input:
            None
        Output:
            None
        '''
        if flags.show_selection_outlines:
            for current_image in self.images:
                if not current_image.current_cell == 'none' and self == current_image.current_cell.contained_mobs[0]: #only draw outline if on top of stack
                    pygame.draw.rect(constants.game_display, constants.color_dict[self.selection_outline_color], (current_image.outline), current_image.outline_width)
        
    def update_tooltip(self):
        '''
        Description:
            Sets this mob's tooltip to what it should be whenever the player mouses over one of its images
        Input:
            None
        Output:
            None
        '''
        tooltip_list = []
        
        tooltip_list.append('Name: ' + self.name[:1].capitalize() + self.name[1:]) #capitalizes first letter while keeping rest the same
        
        if self.is_pmob:
            if self.is_group:
                tooltip_list.append('    Officer: ' + self.officer.name.capitalize())
                tooltip_list.append('    Workers: ' + self.worker.name.capitalize())
            elif self.is_vehicle:
                if self.has_crew:
                    tooltip_list.append('    Crew: ' + self.crew.name.capitalize())
                else:
                    tooltip_list.append('    Crew: None')
                    tooltip_list.append('    A ' + self.name + ' cannot move or take passengers or cargo without crew')
                    
                if len(self.contained_mobs) > 0:
                    tooltip_list.append('    Passengers: ')
                    for current_mob in self.contained_mobs:
                        tooltip_list.append('        ' + current_mob.name.capitalize())
                else:
                    tooltip_list.append('    Passengers: None')
            
            if (not self.has_infinite_movement) and not (self.is_vehicle and not self.has_crew):
                tooltip_list.append('Movement points: ' + str(self.movement_points) + '/' + str(self.max_movement_points))
            elif self.temp_movement_disabled or self.is_vehicle and not self.has_crew:
                tooltip_list.append('No movement')
            else:
                tooltip_list.append('Movement points: Infinite')

        else:
            tooltip_list.append('Movement points: ???')
        
        tooltip_list.append('Combat strength: ' + str(self.get_combat_strength()))    
        if self.disorganized:
            if self.is_npmob and self.npmob_type == 'beast':
                tooltip_list.append('This unit is currently injured, giving a combat penalty until its next turn')
            else:
                tooltip_list.append('This unit is currently disorganized, giving a combat penalty until its next turn')

        if not self.end_turn_destination == 'none':
            if self.end_turn_destination.cell.grid == status.strategic_map_grid:
                tooltip_list.append('This unit has been issued an order to travel to (' + str(self.end_turn_destination.cell.x) + ', ' + str(self.end_turn_destination.cell.y) + ') in Africa at the end of the turn')
            elif self.end_turn_destination.cell.grid == status.europe_grid:
                tooltip_list.append('This unit has been issued an order to travel to Europe at the end of the turn')
            elif self.end_turn_destination.cell.grid == status.slave_traders_grid:
                tooltip_list.append('This unit has been issued an order to travel to the slave traders at the end of the turn')
                
        if self.is_npmob and self.npmob_type == 'beast':
            tooltip_list.append('This beast tends to live in ' + self.preferred_terrains[0] + ', ' + self.preferred_terrains[1] + ', and ' + self.preferred_terrains[2] + ' terrain ')
            
        if self.is_npmob:
            if self.hostile:
                tooltip_list.append('Attitude: Hostile')
            else:
                tooltip_list.append('Attitude: Neutral')
            tooltip_list.append('You do not control this unit')
        elif self.is_pmob and self.sentry_mode:
            tooltip_list.append('This unit is in sentry mode')

        if self.is_pmob:
            held_commodities = self.get_held_commodities()
            if held_commodities:
                tooltip_list.append('Inventory:')
                for commodity in held_commodities:
                    tooltip_list.append('    ' + commodity + ': ' + str(self.get_inventory(commodity)))
            if len(self.base_automatic_route) > 1:
                start_coordinates = self.base_automatic_route[0]
                end_coordinates = self.base_automatic_route[-1]
                tooltip_list.append('This unit has a designated movement route of length ' + str(len(self.base_automatic_route)) + ', picking up commodities at (' + str(start_coordinates[0]) + ', ' + str(start_coordinates[1]) + ') and dropping them off at (' + str(end_coordinates[0]) + ', ' + str(end_coordinates[1]) + ')') 
            
        self.set_tooltip(tooltip_list)
        
    def remove(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program. Also deselects this mob
        Input:
            None
        Output:
            None
        '''
        if status.displayed_mob == self:
            actor_utility.calibrate_actor_info_display(status.mob_info_display, None, override_exempt=True)
        for current_image in self.images:
            current_image.remove_from_cell()
        super().remove()
        status.mob_list = utility.remove_from_list(status.mob_list, self)
        for current_status_icon in self.status_icons:
            current_status_icon.remove_complete()
        self.status_icons = []

    def die(self, death_type = 'violent'):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program. Used instead of remove to improve consistency with groups/vehicles, whose die and remove have different
                functionalities
        Input:
            string death_type == 'violent': Type of death for this unit, determining the type of sound played
        Output:
            None
        '''
        if self.is_pmob:
            self.death_sound(death_type)
        self.remove_complete()

    def death_sound(self, death_type: str = 'violent'):
        '''
        Description:
            Makes a sound when this unit dies, depending on the type of death
        Input:
        string death_type == 'violent': Type of death for this unit, determining the type of sound played
        Output:
            None
        '''
        possible_sounds: List[str] = []
        if death_type == 'fired':
            possible_sounds = []
        elif death_type == 'quit':
            possible_sounds = ['quit 1', 'quit 2', 'quit 3']
        elif death_type == 'violent':
            possible_sounds = ['dead 1', 'dead 2', 'dead 3', 'dead 4', 'dead 5', 'dead 6', 'dead 7', 'dead 8', 'dead 9']
        if len(possible_sounds) > 0:
            constants.sound_manager.play_sound('voices/' + random.choice(possible_sounds), 0.5)

    def can_move(self, x_change, y_change): #same logic as pmob without print statements
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
            if not self.grid.is_abstract_grid:
                if future_x >= 0 and future_x < self.grid.coordinate_width and future_y >= 0 and future_y < self.grid.coordinate_height:
                    future_cell = self.grid.find_cell(future_x, future_y)
                    if future_cell.visible or self.can_explore or self.is_npmob:
                        destination_type = 'land'
                        if future_cell.terrain == 'water':
                            destination_type = 'water' #if can move to destination, possible to move onto ship in water, possible to 'move' into non-visible water while exploring
                        if ((destination_type == 'land' and (self.can_walk or self.can_explore or (future_cell.has_intact_building('port') and self.images[0].current_cell.terrain == 'water'))) or
                            (destination_type == 'water' and (self.can_swim or (future_cell.has_vehicle('ship') and not self.is_vehicle) or (self.can_explore and not future_cell.visible)))):
                            if destination_type == 'water':
                                if future_y == 0 and not self.can_swim_ocean:
                                    return(False)
                                elif future_y > 0 and (not self.can_swim_river) and self.can_walk:
                                    return(True) #can walk through river with max movement points while becoming disorganized
                            if self.movement_points >= self.get_movement_cost(x_change, y_change) or self.has_infinite_movement and self.movement_points > 0: #self.movement_cost:
                                return(True)
                            else:
                                return(False)
                        elif destination_type == 'land' and not self.can_walk: #if trying to walk on land and can't
                            #if future_cell.visible or self.can_explore: #already checked earlier
                            return(False)
                        else: #if trying to swim in water and can't 
                            return(False)
                    else:
                        return(False)
                else:
                    return(False)
            else:
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
        if self.is_pmob and self.sentry_mode:
            self.set_sentry_mode(False)
        self.end_turn_destination = 'none' #cancels planned movements
        self.change_movement_points(-1 * self.get_movement_cost(x_change, y_change))
        if self.is_pmob:
            previous_cell = self.images[0].current_cell
        for current_image in self.images:
            current_image.remove_from_cell()
        self.x += x_change
        self.y += y_change
        status.minimap_grid.calibrate(self.x, self.y)
        for current_image in self.images:
            current_image.add_to_cell()

        if (self.is_vehicle and self.vehicle_type == 'ship') or self.images[0].current_cell.terrain == 'water': #do terrain check before embarking on ship
            constants.sound_manager.play_sound('water')
        else:
            constants.sound_manager.play_sound('footsteps')

        if self.images[0].current_cell.has_vehicle('ship', self.is_worker) and (not self.is_vehicle): #test this logic
            previous_infrastructure = previous_cell.get_intact_building('infrastructure')
            if self.images[0].current_cell.terrain == 'water' and not (previous_infrastructure != 'none' and previous_infrastructure.is_bridge):
                if (not self.can_swim) or (self.y == 0 and not self.can_swim_ocean) or (self.y > 0 and not self.can_swim_river): #board if moving to ship in water
                    vehicle = self.images[0].current_cell.get_vehicle('ship', self.is_worker)
                    if self.is_worker and not vehicle.has_crew:
                        self.crew_vehicle(vehicle)
                        self.set_movement_points(0)
                    else:
                        self.embark_vehicle(vehicle)
                        self.set_movement_points(0)
                    vehicle.select()
        if (self.can_construct or self.can_trade or self.can_convert or self.is_battalion) and self == status.displayed_mob: #if can build any type of building, update mob display to show new building possibilities in new tile
            actor_utility.calibrate_actor_info_display(status.mob_info_display, self)

        if self.is_pmob: #do an inventory attrition check when moving, using the destination's terrain
            self.manage_inventory_attrition()
            if previous_cell.terrain == 'water' and ((previous_cell.y > 0 and not self.can_swim_river) or (previous_cell.y == 0 and not self.can_swim_ocean)): #if landing without port, use all of movement points
                previous_infrastructure = previous_cell.get_intact_building('infrastructure')
                if not (previous_infrastructure != 'none' and previous_infrastructure.is_bridge): #if from bridge, act as if moving from land
                    if previous_cell.y == 0 and not (self.can_swim and self.can_swim_ocean): #if came from ship in ocean
                        self.set_movement_points(0)
                    elif previous_cell.y > 0 and not (self.can_swim and self.can_swim_river): #if came from boat in river
                        self.set_movement_points(0)
            if self.can_show() and self.images[0].current_cell.terrain == 'water' and self.images[0].current_cell.y > 0 and not self.can_swim_river and not previous_cell.has_walking_connection(self.images[0].current_cell): #if entering river w/o canoes, spend maximum movement and become disorganized
                self.set_disorganized(True)
            if not (self.images[0].current_cell == 'none' or self.images[0].current_cell.terrain == 'water' or self.is_vehicle):
                possible_sounds = ['voices/forward march 1', 'voices/forward march 2']
                if status.current_country.name == 'Germany':
                    possible_sounds.append('voices/german forward march 1')
                constants.sound_manager.play_sound(random.choice(possible_sounds))

        if self.has_canoes:
            self.update_canoes()
        self.last_move_direction = (x_change, y_change)

    def can_swim_at(self, current_cell):
        '''
        Description: 
            Calculates and returns whether this unit is able to swim in the inputted cell
        Input:
            cell current_cell: Cell where this unit checks its ability to swim
        Output:
            boolean: Returns whether this unit is able to swim in the inputted cell
        '''
        if not current_cell.terrain == 'water':
            return(True)
        if current_cell.y > 0:
            return(True)
        if not self.can_swim:
            return(False)
        if current_cell.y == 0 and self.can_swim_ocean:
            return(True)
        return(False)

    def set_has_canoes(self, new_canoes):
        '''
        Description:
            Sets this unit to have canoes, automatically updating its in_canoes, swimming capabilities, and images
        Input:
            boolean new_canoes: New canoes value
        Output:
            None
        '''
        self.has_canoes = new_canoes
        self.can_swim = self.has_canoes
        self.can_swim_ocean = False
        self.can_swim_river = self.has_canoes
        if new_canoes:
            self.update_canoes()

    def update_canoes(self):
        '''
        Description:
            If this unit is visible to the player, updates its image to include canoes or not depending on if the unit is in river water
        Input:
            None
        Output:
            None
        '''
        current_cell = self.images[0].current_cell

        if current_cell != 'none' and current_cell.terrain == 'water' and self.y > 0:
            self.in_canoes = self.has_canoes
        else:
            self.in_canoes = False
        self.update_image_bundle()
            
    def retreat(self):
        '''
        Description:
            Causes a free movement to the last cell this unit moved from, following a failed attack
        Input:
            None
        Output:
            None
        '''
        original_movement_points = self.movement_points
        self.move(-1 * self.last_move_direction[0], -1 * self.last_move_direction[1])
            
        self.set_movement_points(original_movement_points) #retreating is free
        
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
                if not (current_image.grid == status.minimap_grid and not current_image.grid.is_on_mini_grid(self.x, self.y)): #do not consider as touching mouse if off-map
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
        if status.displayed_mob == self:
            actor_utility.calibrate_actor_info_display(status.mob_info_display, self)

    def hide_images(self):
        '''
        Description:
            Hides this mob's images, allowing it to be hidden but still stored at certain coordinates when it is attached to another actor or otherwise not visible
        Input:
            None
        Output:
            None
        '''
        if status.displayed_mob == self:
            actor_utility.calibrate_actor_info_display(status.mob_info_display, None)
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
