#Contains functionality for battalions
import time
import random
from .groups import group
from ..tiles import tile
from .. import actor_utility
from .. import utility
from .. import notification_tools
from .. import text_tools

class battalion(group):
    '''
    A group with a major officer that can attack enemy units
    '''
    def __init__(self, from_save, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates on one of the game grids
                'grids': grid list value - grids in which this group's images can appear
                'image': string value - File path to the image used by this object
                'name': string value - Required if from save, this group's name
                'modes': string list value - Game modes during which this group's images can appear
                'end_turn_destination': string or int tuple value - Required if from save, 'none' if no saved destination, destination coordinates if saved destination
                'end_turn_destination_grid_type': string value - Required if end_turn_destination is not 'none', matches the global manager key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - Required if from save, how many movement points this actor currently has
                'worker': worker or dictionary value - If creating a new group, equals a worker that is part of this group. If loading, equals a dictionary of the saved information necessary to recreate the worker
                'officer': worker or dictionary value - If creating a new group, equals an officer that is part of this group. If loading, equals a dictionary of the saved information necessary to recreate the officer
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(from_save, input_dict, global_manager)
        self.set_group_type('battalion')
        self.is_battalion = True
        if self.worker.worker_type == 'European':
            self.battalion_type = 'imperial'
        else: #colonial
            self.battalion_type = 'colonial'
        self.attack_cost = self.global_manager.get('action_prices')['attack']
        self.attack_mark_list = []
        if not from_save:
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self) #updates label to show new combat strength

    def get_movement_cost(self, x_change, y_change, post_attack = False):
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
        elif x_change == 0 and y_change == 0:
            direction = 'none'
            
        if direction == 'none':
            adjacent_cell = local_cell
        else:
            adjacent_cell = local_cell.adjacent_cells[direction]
            
        if not adjacent_cell == 'none':
            if (not post_attack) and self.is_battalion and not adjacent_cell.get_best_combatant('npmob') == 'none': #if battalion attacking non-beast
                cost = 1
            elif (not post_attack) and self.is_safari and not adjacent_cell.get_best_combatant('npmob', 'beast') == 'none': #if safari attacking beast
                cost = 1
            else:
                cost = cost * self.global_manager.get('terrain_movement_cost_dict')[adjacent_cell.terrain]
            
                if self.is_pmob:
                    if local_cell.has_building('road') or local_cell.has_building('railroad'): #if not local_infrastructure == 'none':
                        if adjacent_cell.has_building('road') or adjacent_cell.has_building('railroad'): #if not adjacent_infrastructure == 'none':
                            cost = cost / 2
                    if (not adjacent_cell.visible) and self.can_explore:
                        cost = self.movement_cost
        return(cost)

    def move(self, x_change, y_change, attack_confirmed = False):
        '''
        Description:
            Moves this mob x_change to the right and y_change upward. Moving to a ship in the water automatically embarks the ship. If moving into a cell with an npmob, asks for a confirmation to attack instead of moving. If the attack
                is confirmed, move is called again to cause a combat to start
        Input:
            int x_change: How many cells are moved to the right in the movement
            int y_change: How many cells are moved upward in the movement
            boolean attack_confirmed = False: Whether an attack has already been confirmed. If an attack has been confirmed, a move into the target cell will occur and a combat will start
        Output:
            None
        '''
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
        future_cell = self.grid.find_cell(future_x, future_y)
        if self.is_battalion:
            defender = future_cell.get_best_combatant('npmob')
        elif self.is_safari:
            defender = future_cell.get_best_combatant('npmob', 'beast')
        
        if (not attack_confirmed) and (not defender == 'none'): #if enemy in destination tile and attack not confirmed yet
            if self.global_manager.get('money_tracker').get() >= self.attack_cost:
                if self.check_if_minister_appointed():
                    choice_info_dict = {'battalion': self, 'x_change': x_change, 'y_change': y_change, 'cost': self.attack_cost, 'type': 'combat'}
                    
                    message = ""

                    risk_value = -1 * self.get_combat_modifier() #should be low risk with +2/veteran, moderate with +2 or +1/veteran, high with +1
                    if self.veteran: #reduce risk if veteran
                        risk_value -= 1
                    if self.is_safari:
                        risk_value -= 1

                    if risk_value < -2:
                        message = "RISK: LOW /n /n" + message  
                    elif risk_value == -2:
                        message = "RISK: MODERATE /n /n" + message
                    elif risk_value == -1: #2/6 = high risk
                        message = "RISK: HIGH /n /n" + message
                    elif risk_value > 0:
                        message = "RISK: DEADLY /n /n" + message

                    if defender.npmob_type == 'beast':
                        notification_tools.display_choice_notification(message + "Are you sure you want to spend " + str(choice_info_dict['cost']) + " money to hunt the " + defender.name + " to the " + direction + "? /n /nRegardless of the result, the rest of this unit's movement points will be consumed.",
                            ['attack', 'stop attack'], choice_info_dict, self.global_manager) #message, choices, choice_info_dict, global_manager
                    else:
                        notification_tools.display_choice_notification(message + "Are you sure you want to spend " + str(choice_info_dict['cost']) + " money to attack the " + defender.name + " to the " + direction + "? /n /nRegardless of the result, the rest of this unit's movement points will be consumed.",
                            ['attack', 'stop attack'], choice_info_dict, self.global_manager) #message, choices, choice_info_dict, global_manager
                    self.global_manager.set('ongoing_combat', True)
                    for current_grid in self.grids:
                        coordinates = (0, 0)
                        if current_grid.is_mini_grid:
                            coordinates = current_grid.get_mini_grid_coordinates(self.x + x_change, self.y + y_change)
                        else:
                            coordinates = (self.x + x_change, self.y + y_change)
                        input_dict = {}
                        input_dict['coordinates'] = coordinates
                        input_dict['grid'] = current_grid
                        input_dict['image'] = 'misc/attack_mark/' + direction + '.png'
                        input_dict['name'] = 'exploration mark'
                        input_dict['modes'] = ['strategic']
                        input_dict['show_terrain'] = False
                        self.attack_mark_list.append(tile(False, input_dict, self.global_manager))
            else:
                if defender.npmob_type == 'beast':
                    text_tools.print_to_screen("You do not have enough money to supply a hunt.", self.global_manager)
                else:
                    text_tools.print_to_screen("You do not have enough money to supply an attack.", self.global_manager)
        elif defender == 'none' and ((self.is_battalion and not future_cell.get_best_combatant('npmob', 'beast') == 'none') or (self.is_safari and not future_cell.get_best_combatant('npmob') == 'none')): #if wrong type of defender present
            if self.is_battalion:
                text_tools.print_to_screen("Battalions can not attack beasts.", self.global_manager)
            elif self.is_safari:
                text_tools.print_to_screen("Safaris can only attack beasts.", self.global_manager)
        else: #if destination empty and 
            super().move(x_change, y_change)
            if not self.in_vehicle:
                self.attempt_local_combat()

    def attempt_local_combat(self):
        '''
        Description:
            When this unit moves, it checks if combat is possible in the cell it moved into. If combat is possible, it will immediately start a combat with the strongest local npmob and pay to supply the attack
        Input:
            None
        Output:
            None
        '''
        defender = self.images[0].current_cell.get_best_combatant('npmob')
        if not defender == 'none':
            self.global_manager.get('money_tracker').change(self.attack_cost * -1, 'attacker supplies')
            self.start_combat('attacking', defender)

    def remove_attack_marks(self):
        '''
        Description:
            Removes all of the attack marks used to show the direction of a proposed attack during its confirmation
        Input:
            None
        Output:
            None
        '''
        for attack_mark in self.attack_mark_list:
            attack_mark.remove()
        self.attack_mark_list = []

class safari(battalion): #specialized battalion led by hunter that fights beasts
    def __init__(self, from_save, input_dict, global_manager):
        super().__init__(from_save, input_dict, global_manager)    
        self.set_group_type('safari')
        self.is_battalion = False
        self.is_safari = True
        self.can_swim = True
        self.can_swim_river = True
        self.can_swim_ocean = False
        
        self.has_canoes = True
        self.image_dict['canoes'] = input_dict['canoes_image']
        self.image_dict['no_canoes'] = self.image_dict['default']
        self.update_canoes()
        
        self.battalion_type = 'none'
        self.attack_cost = self.global_manager.get('action_prices')['hunt']
        if not from_save:
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self) #updates label to show new combat strength

    def attempt_local_combat(self):
        defender = self.images[0].current_cell.get_best_combatant('npmob', 'beast')
        if not defender == 'none':
            self.global_manager.get('money_tracker').change(self.attack_cost * -1, 'hunting supplies')
            self.start_combat('attacking', defender)

    def track_beasts(self):
        result = self.controlling_minister.no_corruption_roll(6)
        beasts_found = []
        ambush_list = []
        if result >= 4:
            for current_beast in self.global_manager.get('beast_list'):
                if current_beast.hidden:
                    if utility.find_grid_distance(self, current_beast) <= 1: #if different by 1 in x or y or at same coordinates
                        beast_cell = self.grids[0].find_cell(current_beast.x, current_beast.y)
                        if beast_cell.visible: #if beasts's cell has been discovered
                            current_beast.set_hidden(False)
                            beasts_found.append(current_beast)
        text = ""
        if len(beasts_found) == 0:
            text += "Though beasts may still be hiding nearby, the safari was not able to successfully track any beasts. /n /n"
        else:
            text = ""
            for current_beast in beasts_found:
                if current_beast.x == self.x and current_beast.y == self.y:
                    text += "As the safari starts searching for their quarry, they soon realize that the " + current_beast.name + " had been stalking them the whole time. They have only moments to prepare for the ambush. /n /n"
                    ambush_list.append(current_beast)
                elif current_beast.x > self.x:
                    text += "The safari finds signs of " + utility.generate_article(current_beast.name) + " " + current_beast.name + " to the east. /n /n"
                elif current_beast.x < self.x:
                    text += "The safari finds signs of " + utility.generate_article(current_beast.name) + " " + current_beast.name + " to the west. /n /n"
                elif current_beast.y > self.y:
                    text += "The safari finds signs of " + utility.generate_article(current_beast.name) + " " + current_beast.name + " to the north. /n /n"
                elif current_beast.y < self.y:
                    text += "The safari finds signs of " + utility.generate_article(current_beast.name) + " " + current_beast.name + " to the south. /n /n"
                current_beast.set_hidden(False)
                current_beast.just_revealed = True
            if result == 6 and not self.veteran:
                text += "This safari's hunter tracked the " + random.choice(beasts_found).name + " well enough to become a veteran. /n /n"
                self.promote()

        self.controlling_minister.display_message(text)
        for current_beast in ambush_list:
            current_beast.attempt_local_combat()
        self.change_movement_points(-1)
