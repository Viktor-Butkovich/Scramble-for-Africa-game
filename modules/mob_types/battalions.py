#Contains functionality for battalions
import time
from .groups import group
from ..tiles import tile
from .. import actor_utility
from .. import notification_tools

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
        defender = future_cell.get_best_combatant('npmob')
        
        if (not attack_confirmed) and (not defender == 'none'): #if enemy in destination tile and attack not confirmed yet
            if self.global_manager.get('money_tracker').get() >= self.attack_cost:
                if self.check_if_minister_appointed():
                    choice_info_dict = {'battalion': self, 'x_change': x_change, 'y_change': y_change, 'cost': self.attack_cost, 'type': 'combat'}
                    
                    message = ""

                    risk_value = -1 * self.get_combat_modifier() #should be low risk with +2/veteran, moderate with +2 or +1/veteran, high with +1
                    if self.veteran: #reduce risk if veteran
                        risk_value -= 1

                    if risk_value < -2:
                        message = "RISK: LOW /n /n" + message  
                    elif risk_value == -2:
                        message = "RISK: MODERATE /n /n" + message
                    elif risk_value == -1: #2/6 = high risk
                        message = "RISK: HIGH /n /n" + message
                    elif risk_value > 0:
                        message = "RISK: DEADLY /n /n" + message
                    
                    notification_tools.display_choice_notification(message + "Are you sure you want to spend " + str(choice_info_dict['cost']) + " money to attack the " + defender.name + " to the " + direction + "?",
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
                text_tools.print_to_screen("You do not have enough money to supply an attack.", self.global_manager)
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
