#Contains functionality for expeditions

import random
from ..groups import group
from ....util import actor_utility, dice_utility
import modules.constants.constants as constants
import modules.constants.status as status

class expedition(group):
    '''
    A group with an explorer officer that is able to explore and move on water
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
                'image': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'name': string value - Required if from save, this group's name
                'modes': string list value - Game modes during which this group's images can appear
                'end_turn_destination': string or int tuple value - Required if from save, 'none' if no saved destination, destination coordinates if saved destination
                'end_turn_destination_grid_type': string value - Required if end_turn_destination is not 'none', matches the global manager key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - Required if from save, how many movement points this actor currently has
                'max_movement_points': int value - Required if from save, maximum number of movement points this mob can have
                'worker': worker or dictionary value - If creating a new group, equals a worker that is part of this group. If loading, equals a dictionary of the saved information necessary to recreate the worker
                'officer': worker or dictionary value - If creating a new group, equals an officer that is part of this group. If loading, equals a dictionary of the saved information necessary to recreate the officer
                'canoes_image': string value - File path tothe image used by this object when it is in a river
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(from_save, input_dict, global_manager)
        self.can_explore = True
        self.set_has_canoes(True)
        
        self.set_group_type('expedition')
        self.destination_cells = [] #used for off tile exploration, like when seeing nearby tiles when on water
        self.public_opinion_increases = []
        if not self.images[0].current_cell == 'none': #if did not just board vehicle
            self.resolve_off_tile_exploration()

    def move(self, x_change, y_change):
        '''
        Description:
            Moves this mob x_change to the right and y_change upward. Moving to a ship in the water automatically embarks the ship. Also allows exploration when moving into unexplored areas. Attempting an exploration starts the
                exploration process, which requires various dice rolls to succeed and can also result in the death of the expedition or the promotion of its explorer. A successful exploration uncovers the area and units to move into it
                normally in the future. As expeditions move, they automatically discover adjacent water tiles, and they also automatically discover all adjacent tiles when looking from a water tile
        Input:
            int x_change: How many cells are moved to the right in the movement
            int y_change: How many cells are moved upward in the movement
        Output:
            None
        '''
        constants.show_selection_outlines = True
        constants.show_minimap_outlines = True
        constants.last_selection_outline_switch = constants.current_time
        
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
        if future_cell.visible == False: #if moving to unexplored area, try to explore it
            self.global_manager.get('actions')['exploration'].on_click(self, on_click_info_dict={'x_change': x_change, 'y_change': y_change, 'direction': direction})
        else: #if moving to explored area, move normally
            super().move(x_change, y_change)
            if self.images[0].current_cell != 'none': #if not in vehicle
                self.destination_cells = [] #used for off tile exploration, like when seeing nearby tiles when on water
                self.public_opinion_increases = []
                self.resolve_off_tile_exploration()

    def disembark_vehicle(self, vehicle):
        '''
        Description:
            Shows this mob and disembarks it from the inputted vehicle after being a passenger. Also automatically explores nearby tiles when applicable, as if this expedition had moved
        Input:
            vehicle vehicle: vehicle that this mob disembarks from
        Output:
            None
        '''
        super().disembark_vehicle(vehicle)
        self.destination_cells = [] #used for off tile exploration, like when seeing nearby tiles when on water
        self.public_opinion_increases = []
        self.resolve_off_tile_exploration()

    def resolve_off_tile_exploration(self):
        '''
        Description:
            Whenever an expedition arrives in a tile for any reason, they automatically discover any adjacent water tiles. Additionally, when standing on water, they automatically discover all adjacent tiles
        Input:
            None
        Output:
            None
        '''
        self.current_action_type = 'exploration' #used in action notification to tell whether off tile notification should explore tile or not
        cardinal_directions = {'up': 'north', 'down': 'south', 'right': 'east', 'left': 'west'}
        current_cell = self.images[0].current_cell
        for current_direction in ['up', 'down', 'left', 'right']:
            target_cell = current_cell.adjacent_cells[current_direction]
            if target_cell and not target_cell.visible:
                if current_cell.terrain == 'water' or target_cell.terrain == 'water': #if on water, discover all adjacent undiscovered tiles. Also, discover all adjacent water tiles, regardless of if currently on water
                    if current_cell.terrain == 'water':
                        text = 'From the water, the expedition has discovered a '
                    elif target_cell.terrain == 'water':
                        text = 'The expedition has discovered a '
                    public_opinion_increase = random.randrange(0, 3)
                    if not target_cell.resource == 'none':
                        if target_cell.resource == 'natives':
                            text += target_cell.terrain.upper() + ' tile to the ' + cardinal_directions[current_direction] + ' that contains the village of ' + target_cell.village.name + '. /n /n'
                        else:
                            text += target_cell.terrain.upper() + ' tile with a ' + target_cell.resource.upper() + ' resource (currently worth ' + str(self.global_manager.get('commodity_prices')[target_cell.resource]) + ' money each) to the ' + cardinal_directions[current_direction] + '. /n /n'
                        public_opinion_increase += 3
                    else:
                        text += target_cell.terrain.upper() + ' tile to the ' + cardinal_directions[current_direction] + '. /n /n'

                    if public_opinion_increase > 0: #Royal/National/Imperial
                        text += 'The ' + self.global_manager.get('current_country').government_type_adjective.capitalize() + ' Geographical Society is pleased with these findings, increasing your public opinion by ' + str(public_opinion_increase) + '. /n /n'
                    
                    self.destination_cells.append(target_cell)
                    self.public_opinion_increases.append(public_opinion_increase)
                    self.global_manager.set('ongoing_action', True)
                    self.global_manager.set('ongoing_action_type', 'exploration')
                    self.global_manager.get('notification_manager').display_notification({
                        'message': text,
                        'notification_type': 'off_tile_exploration'
                    })

    def start_rumor_search(self):
        '''
        Description:
            Used when the player clicks on the start rumor search button, displays a choice notification that allows the player to search or not. Choosing to search starts the rumor search process and consumes the missionaries'
                movement points
        Input:
            None
        Output:
            None
        '''
        village = self.images[0].current_cell.get_building('village')
        self.current_roll_modifier = 0
        self.current_min_success = self.default_min_success
        self.current_max_crit_fail = self.default_max_crit_fail
        self.current_min_crit_success = self.default_min_crit_success
        message = 'Are you sure you want to attempt to search for artifact rumors? If successful, the coordinates of a possible location for the ' + self.global_manager.get('current_lore_mission').name + ' will be revealed. /n /n'
        message += 'The search will cost ' + str(constants.action_prices['rumor_search']) + ' money. /n /n'
            
        aggressiveness_modifier = village.get_aggressiveness_modifier()
        if aggressiveness_modifier < 0:
            message += 'The villagers are hostile and unlikely to cooperate. /n /n'
        elif aggressiveness_modifier > 0:
            message += 'The villagers are friendly and likely to provide useful information. /n /n'
        else:
            message += 'The villagers are wary but may cooperate with sufficient persuasion. /n /n'
        self.current_roll_modifier += aggressiveness_modifier

        risk_value = -1 * self.current_roll_modifier #modifier of -1 means risk value of 1
        if self.veteran: #reduce risk if veteran
            risk_value -= 1

        if risk_value < 0: #0/6 = no risk
            message = 'RISK: LOW /n /n' + message  
        elif risk_value == 0: #1/6 death = moderate risk
            message = 'RISK: MODERATE /n /n' + message #puts risk message at beginning
        elif risk_value == 1: #2/6 = high risk
            message = 'RISK: HIGH /n /n' + message
        elif risk_value > 1: #3/6 or higher = extremely high risk
            message = 'RISK: DEADLY /n /n' + message
            
        self.current_min_success -= self.current_roll_modifier #positive modifier reduces number required for succcess, reduces maximum that can be crit fail
        self.current_max_crit_fail -= self.current_roll_modifier
        if self.current_min_success > self.current_min_crit_success:
            self.current_min_crit_success = self.current_min_success #if 6 is a failure, should not be critical success. However, if 6 is a success, it will always be a critical success
        
        choice_info_dict = {'expedition': self,'type': 'start rumor search'}
        self.current_roll_modifier = 0
        if self.current_min_success > 6:
            message += 'As a ' + str(self.current_min_success) + '+ would be required to succeed this roll, it is impossible and may not be attempted. Decrease the village\'s aggressiveness to decrease the roll\'s difficulty. /n /n'
            self.global_manager.get('notification_manager').display_notification({
                'message': message,
            })
        else:
            self.global_manager.set('ongoing_action', True)
            self.global_manager.set('ongoing_action_type', 'rumor_search')

            self.global_manager.get('notification_manager').display_notification({
                'message': message,
                'choices': ['start rumor search', 'stop rumor search'],
                'extra_parameters': choice_info_dict
            })

    def rumor_search(self):
        '''
        Description:
            Controls the rumor search process, determining and displaying its result through a series of notifications
        Input:
            None
        Output:
            None
        '''
        self.current_action_type = 'rumor_search' #used in action notification to tell whether off tile notification should explore tile or not
        roll_result = 0
        self.just_promoted = False
        self.set_movement_points(0)

        if self.veteran: #tells notifications how many of the currently selected mob's dice to show while rolling
            num_dice = 2
        else:
            num_dice = 1
        
        self.global_manager.get('money_tracker').change(constants.action_prices['rumor_search'] * -1, 'rumor_search')
        village = self.images[0].current_cell.get_building('village')
        text = ''
        text += 'The expedition tries to find information regarding the location of the ' + self.global_manager.get('current_lore_mission').name + '. /n /n'

        if not self.veteran:
            self.global_manager.get('notification_manager').display_notification({
                'message': text + 'Click to roll. ' + str(self.current_min_success) + '+ required to succeed.',
                'num_dice': num_dice,
                'notification_type': 'rumor_search'
            })
        else:
            text += ('The veteran explorer can roll twice and pick the higher result. /n /n')
            self.global_manager.get('notification_manager').display_notification({
                'message': text + 'Click to roll. ' + str(self.current_min_success) + '+ required on at least 1 die to succeed.',
                'num_dice': num_dice,
                'notification_type': 'rumor_search'
            })

        self.global_manager.get('notification_manager').display_notification({
            'message': text + 'Rolling... ',
            'num_dice': num_dice,
            'notification_type': 'roll'
        })

        die_x = self.global_manager.get('notification_manager').notification_x - 140

        if self.veteran:
            results = self.controlling_minister.roll_to_list(6, self.current_min_success, self.current_max_crit_fail, constants.action_prices['rumor_search'], 'rumor_search', 2)
            first_roll_list = dice_utility.roll_to_list(6, 'Rumor search roll', self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, results[0])
            self.display_die((die_x, 500), first_roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)
           
            second_roll_list = dice_utility.roll_to_list(6, 'second', self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, results[1])
            self.display_die((die_x, 380), second_roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, False)
                                
            text += (first_roll_list[1] + second_roll_list[1]) #add strings from roll result to text
            roll_result = max(first_roll_list[0], second_roll_list[0])
            result_outcome_dict = {}
            for i in range(1, 7):
                if i <= self.current_max_crit_fail:
                    word = 'CRITICAL FAILURE'
                elif i >= self.current_min_crit_success:
                    word = 'CRITICAL SUCCESS'
                elif i >= self.current_min_success:
                    word = 'SUCCESS'
                else:
                    word = 'FAILURE'
                result_outcome_dict[i] = word
            text += ('The higher result, ' + str(roll_result) + ': ' + result_outcome_dict[roll_result] + ', was used. /n')
        else:
            result = self.controlling_minister.roll(6, self.current_min_success, self.current_max_crit_fail, constants.action_prices['rumor_search'], 'rumor_search')
            roll_list = dice_utility.roll_to_list(6, 'Rumor search roll', self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, result)
            self.display_die((die_x, 440), roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)
                
            text += roll_list[1]
            roll_result = roll_list[0]

        self.global_manager.get('notification_manager').display_notification({
            'message': text + 'Click to continue.',
            'num_dice': num_dice,
            'notification_type': 'rumor_search'
        })
        
        location = 'none'
        text += '/n'
        if roll_result >= self.current_min_success: #4+ required on D6 for exploration
            if self.global_manager.get('current_lore_mission').get_num_revealed_possible_artifact_locations() == len(self.global_manager.get('current_lore_mission').possible_artifact_locations):
                village.found_rumors = True
                self.global_manager.get('current_lore_mission').confirmed_all_locations_revealed = True
                text += 'While the villagers have proven cooperative, the expedition has concluded that all rumors about the ' + self.global_manager.get('current_lore_mission').name + ' have been found. /n /n'
            else:
                location = self.global_manager.get('current_lore_mission').get_random_unrevealed_possible_artifact_location() #random.choice(self.global_manager.get('current_lore_mission').possible_artifact_locations)
                text += 'The villagers have proven cooperative and the expedition found valuable new rumors regarding the location of the ' + self.global_manager.get('current_lore_mission').name + '. /n /n'
        else:
            text += 'The expedition failed to find any useful information from the natives. /n /n'
        if roll_result <= self.current_max_crit_fail:
            text += 'Angered by the expedition\'s intrusive attempts to extract information, the natives attack the expedition. /n /n'

        if (not self.veteran) and roll_result >= self.current_min_crit_success:
            self.just_promoted = True
            text += ' /nThe explorer is now a veteran and will be more successful in future ventures. /n'
            
        if roll_result >= self.current_min_success:
            self.global_manager.get('notification_manager').display_notification({
                'message': text + '/nClick to remove this notification.',
                'notification_type': 'final_rumor_search'
            })
            success = True
        else:
            self.global_manager.get('notification_manager').display_notification({
                'message': text,
            })
            success = False

        self.global_manager.set('rumor_search_result', [self, roll_result, village, success, location])

    def complete_rumor_search(self):
        '''
        Description:
            Used when the player finishes rolling for a rumor search, shows the search's results and makes any changes caused by the result. If successful, reveals a possible artifact location, 
                promotes explorer to a veteran on critical success. Native warriors spawn on critical failure
        Input:
            None
        Output:
            None
        '''
        roll_result = self.global_manager.get('rumor_search_result')[1]
        village = self.global_manager.get('rumor_search_result')[2]
        success = self.global_manager.get('rumor_search_result')[3]
        location = self.global_manager.get('rumor_search_result')[4]
        if success: #if campaign succeeded
            if not location == 'none':
                coordinates = (location.x, location.y)
                self.destination_cells = [self.global_manager.get('strategic_map_grid').find_cell(coordinates[0], coordinates[1])]
                self.public_opinion_increases = [0]
                location.set_revealed(True)
                village.found_rumors = True

                text = 'The villagers tell rumors that the ' + self.global_manager.get('current_lore_mission').name + ' may be located at (' + str(coordinates[0]) + ', ' + str(coordinates[1]) + '). /n /n'
                self.global_manager.set('ongoing_action', True)
                self.global_manager.set('ongoing_action_type', 'rumor_search')
                self.global_manager.get('notification_manager').display_notification({
                    'message': text,
                    'notification_type': 'off_tile_exploration'
                })

            if roll_result >= self.current_min_crit_success and not self.veteran:
                self.promote()
        elif roll_result <= self.current_max_crit_fail:
            warrior = village.spawn_warrior()
            warrior.show_images()
            warrior.attack_on_spawn()
        else:
            self.global_manager.set('ongoing_action', False)
            self.global_manager.set('ongoing_action_type', 'none')

    def start_artifact_search(self):
        '''
        Description:
            Used when the player clicks on the start rumor search button, displays a choice notification that allows the player to search or not. Choosing to search starts the rumor search process and consumes the missionaries'
                movement points
        Input:
            None
        Output:
            None
        '''
        #village = self.images[0].current_cell.get_building('village')
        self.current_roll_modifier = 0
        self.current_min_success = self.default_min_success
        self.current_max_crit_fail = self.default_max_crit_fail
        self.current_min_crit_success = self.default_min_crit_success
        message = 'Are you sure you want to attempt to search for the ' + self.global_manager.get('current_lore_mission').name + '? '
        message += 'If successful, the ' + self.global_manager.get('current_lore_mission').name + ' will be found if it is at this location. /n /n'
        message += 'The search will cost ' + str(constants.action_prices['artifact_search']) + ' money. /n /n'

        risk_value = -1 * self.current_roll_modifier #modifier of -1 means risk value of 1
        if self.veteran: #reduce risk if veteran
            risk_value -= 1

        if risk_value < 0: #0/6 = no risk
            message = 'RISK: LOW /n /n' + message  
        elif risk_value == 0: #1/6 death = moderate risk
            message = 'RISK: MODERATE /n /n' + message #puts risk message at beginning
        elif risk_value == 1: #2/6 = high risk
            message = 'RISK: HIGH /n /n' + message
        elif risk_value > 1: #3/6 or higher = extremely high risk
            message = 'RISK: DEADLY /n /n' + message
            
        self.current_min_success -= self.current_roll_modifier #positive modifier reduces number required for succcess, reduces maximum that can be crit fail
        self.current_max_crit_fail -= self.current_roll_modifier
        if self.current_min_success > self.current_min_crit_success:
            self.current_min_crit_success = self.current_min_success #if 6 is a failure, should not be critical success. However, if 6 is a success, it will always be a critical success
        
        choice_info_dict = {'expedition': self,'type': 'start rumor search'}
        self.current_roll_modifier = 0
        if self.current_min_success > 6:
            message += 'As a ' + str(self.current_min_success) + '+ would be required to succeed this roll, it is impossible and may not be attempted. /n /n'
            self.global_manager.get('notification_manager').display_notification({
                'message': message,
            })
        else:
            self.global_manager.set('ongoing_action', True)
            self.global_manager.set('ongoing_action_type', 'artifact_search')
            self.global_manager.get('notification_manager').display_notification({
                'message': message,
                'choices': ['start artifact search', 'stop artifact search'],
                'extra_parameters': choice_info_dict
            })

    def artifact_search(self):
        '''
        Description:
            Controls the rumor search process, determining and displaying its result through a series of notifications
        Input:
            None
        Output:
            None
        '''
        roll_result = 0
        self.just_promoted = False
        self.set_movement_points(0)

        if self.veteran: #tells notifications how many of the currently selected mob's dice to show while rolling
            num_dice = 2
        else:
            num_dice = 1
        
        self.global_manager.get('money_tracker').change(constants.action_prices['artifact_search'] * -1, 'artifact_search')
        #village = self.images[0].current_cell.get_building('village')
        text = ''
        text += 'The expedition tries to locate the ' + self.global_manager.get('current_lore_mission').name + '. /n /n'

        if not self.veteran:
            self.global_manager.get('notification_manager').display_notification({
                'message': text + 'Click to roll. ' + str(self.current_min_success) + '+ required to succeed.',
                'num_dice': num_dice,
                'notification_type': 'artifact_search'
            })
        else:
            text += ('The veteran explorer can roll twice and pick the higher result. /n /n')
            self.global_manager.get('notification_manager').display_notification({
                'message': text + 'Click to roll. ' + str(self.current_min_success) + '+ required on at least 1 die to succeed.',
                'num_dice': num_dice,
                'notification_type': 'artifact_search'
            })

        self.global_manager.get('notification_manager').display_notification({
            'message': text + 'Rolling... ',
            'num_dice': num_dice,
            'notification_type': 'roll'
        })

        die_x = self.global_manager.get('notification_manager').notification_x - 140

        if self.veteran:
            results = self.controlling_minister.roll_to_list(6, self.current_min_success, self.current_max_crit_fail, constants.action_prices['artifact_search'], 'artifact_search', 2)
            first_roll_list = dice_utility.roll_to_list(6, 'Artifact search roll', self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, results[0])
            self.display_die((die_x, 500), first_roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)
           
            second_roll_list = dice_utility.roll_to_list(6, 'second', self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, results[1])
            self.display_die((die_x, 380), second_roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, False)
                                
            text += (first_roll_list[1] + second_roll_list[1]) #add strings from roll result to text
            roll_result = max(first_roll_list[0], second_roll_list[0])
            result_outcome_dict = {}
            for i in range(1, 7):
                if i <= self.current_max_crit_fail:
                    word = 'CRITICAL FAILURE'
                elif i >= self.current_min_crit_success:
                    word = 'CRITICAL SUCCESS'
                elif i >= self.current_min_success:
                    word = 'SUCCESS'
                else:
                    word = 'FAILURE'
                result_outcome_dict[i] = word
            text += ('The higher result, ' + str(roll_result) + ': ' + result_outcome_dict[roll_result] + ', was used. /n')
        else:
            result = self.controlling_minister.roll(6, self.current_min_success, self.current_max_crit_fail, constants.action_prices['artifact_search'], 'artifact_search')
            roll_list = dice_utility.roll_to_list(6, 'Artifact search roll', self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, result)
            self.display_die((die_x, 440), roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)
                
            text += roll_list[1]
            roll_result = roll_list[0]

        self.global_manager.get('notification_manager').display_notification({
            'message': text + 'Click to continue.',
            'num_dice': num_dice,
            'notification_type': 'artifact_search'
        })

        location = 'none'
        text += '/n'
        if roll_result >= self.current_min_success: #4+ required on D6 for exploration
            location = self.global_manager.get('current_lore_mission').get_possible_artifact_location(self.x, self.y)
            if location == self.global_manager.get('current_lore_mission').artifact_location:
                text += 'The expedition successfully found the ' + self.global_manager.get('current_lore_mission').name + '! /n /n'
                text += 'These findings will be reported to the ' + self.global_manager.get('current_country').government_type_adjective.capitalize() + ' Geographical Society as soon as possible. /n /n'
            else:
                text += 'The expedition successfully verified that the ' + self.global_manager.get('current_lore_mission').name + ' is not at this location. /n /n'

        else:
            text += 'The expedition failed to find whether the ' + self.global_manager.get('current_lore_mission').name + ' is at this location. /n /n'

        if roll_result <= self.current_max_crit_fail:
            text += 'With neither trace nor logical explanation, the entire expedition seems to have vanished. /n /n'

        if (not self.veteran) and roll_result >= self.current_min_crit_success:
            self.just_promoted = True
            text += ' /nThe explorer is now a veteran and will be more successful in future ventures. /n'
            
        if roll_result >= self.current_min_success:
            self.global_manager.get('notification_manager').display_notification({
                'message': text + '/nClick to remove this notification.',
                'notification_type': 'final_artifact_search'
            })
            success = True
        else:
            self.global_manager.get('notification_manager').display_notification({
                'message': text,
            })
            success = False

        self.global_manager.set('artifact_search_result', [self, roll_result, success, location])

    def complete_artifact_search(self):
        '''
        Description:
            Used when the player finishes rolling for a rumor search, shows the search's results and makes any changes caused by the result. If successful, reveals a possible artifact location, 
                promotes explorer to a veteran on critical success. Native warriors spawn on critical failure
        Input:
            None
        Output:
            None
        '''
        roll_result = self.global_manager.get('artifact_search_result')[1]
        success = self.global_manager.get('artifact_search_result')[2]
        location = self.global_manager.get('artifact_search_result')[3]
        if success: #if campaign succeeded
            if location == self.global_manager.get('current_lore_mission').artifact_location:
                prize_money = random.randrange(25, 51) * 10
                public_opinion_increase = random.randrange(30, 61)
                text = 'The ' + self.global_manager.get('current_country').government_type_adjective.capitalize() + ' Geographical Society awarded ' + str(prize_money) + ' money for finding the ' + self.global_manager.get('current_lore_mission').name + '. /n /n'
                text += 'Additionally, public opinion has increased by ' + str(public_opinion_increase) + '. /n /n'
                lore_type = self.global_manager.get('current_lore_mission').lore_type
                if not lore_type in self.global_manager.get('completed_lore_mission_types'):
                    text += 'Completing a mission in the ' + lore_type + ' category has given your company a permanent ' + self.global_manager.get('lore_types_effect_descriptions_dict')[lore_type] + '. /n /n'
                    self.global_manager.get('completed_lore_mission_types').append(lore_type)
                    self.global_manager.get('lore_types_effects_dict')[lore_type].apply()
                self.global_manager.get('notification_manager').display_notification({
                    'message': text,
                })
                self.global_manager.get('money_tracker').change(prize_money)
                self.global_manager.get('public_opinion_tracker').change(public_opinion_increase)
                self.global_manager.get('current_lore_mission').remove_complete()
            else:
                location.set_proven_false(True)
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display'), status.displayed_tile) #updates tile display without question mark
            if roll_result >= self.current_min_crit_success and not self.veteran:
                self.promote()
        elif roll_result <= self.current_max_crit_fail:
            self.die()
        self.global_manager.set('ongoing_action', False)
        self.global_manager.set('ongoing_action_type', 'none')
