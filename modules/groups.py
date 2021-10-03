import time
import random
import math
from .mobs import mob
from .tiles import tile
from .tiles import veteran_icon
from .buttons import button
from . import actor_utility
from . import text_tools
from . import dice_utility
from . import utility
from . import notification_tools
from . import dice
from . import scaling
from . import main_loop_tools

class group(mob):
    '''
    Mob that is created by a combination of a worker and officer, can have unique capabilities, and restores its worker and officer upon being disbanded
    '''
    def __init__(self, coordinates, grids, image_id, name, modes, worker, officer, global_manager):
        '''
        Input:
            coordinates: tuple of two int variables representing the pixel coordinates of the bottom left of the notification
            grids: list of grid objects on which the mob's images will appear
            image_id: string representing the file path to the mob's default image
            name: string representing the mob's name
            modes: list of strings representing the game modes in which the mob can appear
            worker: worker object representing the worker that is part of this group
            officer: officer object representing the officer that is part of this group
            global_manager: global_manager_template object used to manage a dictionary of shared variables
        '''
        self.worker = worker
        self.officer = officer
        self.veteran = self.officer.veteran
        super().__init__(coordinates, grids, image_id, name, modes, global_manager)
        self.worker.join_group()
        self.officer.join_group()
        self.is_group = True
        for current_commodity in self.global_manager.get('commodity_types'): #merges individual inventory to group inventory and clears individual inventory
            self.change_inventory(current_commodity, self.worker.get_inventory(current_commodity))
            self.change_inventory(current_commodity, self.officer.get_inventory(current_commodity))
        self.worker.inventory_setup()
        self.officer.inventory_setup()
        self.select()
        if self.veteran:
            self.set_name('Veteran expedition')
        self.veteran_icons = self.officer.veteran_icons
        for current_veteran_icon in self.veteran_icons:
            current_veteran_icon.actor = self
        self.global_manager.get('group_list').append(self)
        if self.worker.movement_points > self.officer.movement_points: #a group should keep the lowest movement points out of its members
            self.set_movement_points(self.officer.movement_points)
        else:
            self.set_movement_points(self.worker.movement_points)

    def promote(self):
        self.veteran = True
        self.set_name("Veteran " + self.name.lower()) # Expedition to Veteran expedition
        self.officer.set_name("Veteran " + self.officer.name.lower()) #Explorer to Veteran explorer
        for current_grid in self.grids:
            if current_grid == self.global_manager.get('minimap_grid'):
                veteran_icon_x, veteran_icon_y = current_grid.get_mini_grid_coordinates(self.x, self.y)
            else:
                veteran_icon_x, veteran_icon_y = (self.x, self.y)
            self.veteran_icons.append(veteran_icon((veteran_icon_x, veteran_icon_y), current_grid, 'misc/veteran_icon.png', 'veteran icon', ['strategic', 'europe'], False, self, self.global_manager))
        actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self) #updates actor info display with veteran icon

    def go_to_grid(self, new_grid, new_coordinates):
        '''
        Input:
            grid object representing the grid to which the group is transferring, tuple of two int variables representing the coordinates to which the group will move on the new grid
        Output:
            Moves this group and all of its images to the inputted grid at the inputted coordinates. A group will also move its attached officer, worker, and veteran icons to the new grid.
        '''
        if self.veteran:
            for current_veteran_icon in self.veteran_icons:
                current_veteran_icon.remove()
            self.veteran_icons = []
        super().go_to_grid(new_grid, new_coordinates)
        if self.veteran:
            for current_grid in self.grids:
                if current_grid == self.global_manager.get('minimap_grid'):
                    veteran_icon_x, veteran_icon_y = current_grid.get_mini_grid_coordinates(self.x, self.y)
                else:
                    veteran_icon_x, veteran_icon_y = (self.x, self.y)
                self.veteran_icons.append(veteran_icon((veteran_icon_x, veteran_icon_y), current_grid, 'misc/veteran_icon.png', 'veteran icon', ['strategic', 'europe'], False, self, self.global_manager))
        self.officer.go_to_grid(new_grid, new_coordinates)
        self.officer.join_group() #hides images self.worker.hide_images()#
        self.worker.go_to_grid(new_grid, new_coordinates)
        self.worker.join_group() #self.worker.hide_images()#

    def update_tooltip(self): #to do: show carried commodities in tooltip
        '''
        Input:
            none
        Output:
            Sets this group's tooltip to what it should be. A group's tooltip shows the name of the group, its officer, its worker, and its movement points.
        '''
        self.set_tooltip(["Name: " + self.name, '    Officer: ' + self.officer.name, '    Worker: ' + self.worker.name, "Movement points: " + str(self.movement_points) + "/" + str(self.max_movement_points)])

    def disband(self):
        '''
        Input:
            none
        Output:
            Separates this group into its components, giving its inventory to the officer and setting their number of movement points to that of the group
        '''
        if self.can_hold_commodities:
            self.drop_inventory()
        self.remove()
        self.worker.leave_group(self)
        self.worker.set_movement_points(self.movement_points)
        self.officer.veteran_icons = self.veteran_icons
        for current_veteran_icon in self.veteran_icons:
            current_veteran_icon.actor = self.officer
        self.officer.veteran = self.veteran
        self.officer.leave_group(self)
        self.officer.set_movement_points(self.movement_points)

    def remove(self):
        '''
        Input:
            none
        Output:
            Removes the group from relevant lists and prevents it from further appearing in or affecting the program.
            However, a group will not automatically remove its officer and worker when removed, since disbanding a group removes the group but not its members - to remove the members, use the die function instead
        '''
        super().remove()
        self.global_manager.set('group_list', utility.remove_from_list(self.global_manager.get('group_list'), self))

    def die(self):
        '''
        Input:
            none
        Output:
            Removes the group and its members from relevant lists and prevents them from further appearing in or affecting the program.
        '''
        self.remove()
        self.officer.remove()
        self.worker.remove()

class porters(group):
    '''
    A group with a porter foreman officer that can hold commodities
    '''
    def __init__(self, coordinates, grids, image_id, name, modes, worker, officer, global_manager):
        super().__init__(coordinates, grids, image_id, name, modes, worker, officer, global_manager)
        self.can_hold_commodities = True
        self.inventory_capacity = 9
        self.inventory_setup()
        actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self) #updates mob info display list to account for inventory capacity changing

class construction_gang(group):
    '''
    A group with an engineer officer that is able to construct buildings
    '''
    def __init__(self, coordinates, grids, image_id, name, modes, worker, officer, global_manager):
        '''
        Input:
            same as superclass
        '''
        super().__init__(coordinates, grids, image_id, name, modes, worker, officer, global_manager)
        self.can_construct = True
        actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self) #updates mob info display list to account for can_construct changing

class caravan(group):
    def __init__(self, coordinates, grids, image_id, name, modes, worker, officer, global_manager):
        '''
        Input:
            same as superclass
        '''
        super().__init__(coordinates, grids, image_id, name, modes, worker, officer, global_manager)
        self.can_hold_commodities = True
        self.can_trade = True
        self.inventory_capacity = 9
        self.trades_remaining = 0
        self.inventory_setup()
        actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self) #updates mob info display list to account for inventory capacity changing

    def start_trade(self):
        village = self.images[0].current_cell.village
        choice_info_dict = {'caravan': self, 'village': village, 'type': 'start trading'}
        self.global_manager.set('ongoing_trade', True)
        message = "Are you sure you want to attempt to trade with the village of " + village.name + "? /n /n"
        difficulty_modifier = village.get_aggressiveness_modifier()
        if difficulty_modifier == 1:
            message += "The villagers are hostile and are unlikely to be willing to trade. /n /n"
        elif difficulty_modifier == 0:
            message += "The villagers are wary of the merchant but may be willing to trade. /n /n"
        elif difficulty_modifier == -1:
            message += "The villagers are friendly and are likely to be willing to trade. /n /n"
        message += "The merchant has " + str(self.get_inventory('consumer goods')) + " consumer goods to sell. /n /n"
        message += "In each trade, the merchant trades consumer goods for items that may or may not be valuable. /n /n"
        message += "Trading may also convince villagers to become available for hire as workers. "
        notification_tools.display_choice_notification(message, ['start trading', 'stop trading'], choice_info_dict, self.global_manager) #message, choices, choice_info_dict, global_manager

    def willing_to_trade(self, notification):
        self.notification = notification
        self.set_movement_points(0)
        village = self.notification.choice_info_dict['village']
        text = ("The merchant attempts to convince the villagers to trade. /n /n")
        roll_difficulty = 4
        min_crit_success = 6
        max_crit_fail = 0
        difficulty_modifier = village.get_aggressiveness_modifier()
        if difficulty_modifier == 1:
            text += ("The villagers are hostile and are less likely to be willing to trade. /n /n")
        elif difficulty_modifier == -1:
            text += ("The villagers are friendly and more likely to be willing to trade. /n /n")
        roll_difficulty += difficulty_modifier #modifier adds to difficulty, not roll
        if self.veteran:
            text += ("The veteran merchant can roll twice and pick the higher result /n /n")
            notification_tools.display_notification(text + "Click to roll. " + str(roll_difficulty) + "+ required on at least 1 die to succeed.", 'trade', self.global_manager)
        else:
            notification_tools.display_notification(text + "Click to roll. " + str(roll_difficulty) + "+ required to succeed.", 'trade', self.global_manager)
        notification_tools.display_notification(text + "Rolling... ", 'roll', self.global_manager)

        die_x = self.global_manager.get('notification_manager').notification_x - 140

        roll_result = 0
        if self.veteran:
                
            first_roll_list = dice_utility.roll_to_list(6, "Trade roll", roll_difficulty, min_crit_success, max_crit_fail, self.global_manager) #0 requirement for critical fail means critical fails will not occur
            self.display_trade_die((die_x, 500), first_roll_list[0], roll_difficulty, min_crit_success, max_crit_fail)
                                
            second_roll_list = dice_utility.roll_to_list(6, "second", roll_difficulty, min_crit_success, max_crit_fail, self.global_manager) #0 requirement for critical fail means critical fails will not occur
            self.display_trade_die((die_x, 380), second_roll_list[0], roll_difficulty, min_crit_success, max_crit_fail)
                                
            text += (first_roll_list[1] + second_roll_list[1]) #add strings from roll result to text
            roll_result = max(first_roll_list[0], second_roll_list[0])
            result_outcome_dict = {}
            for i in range(1, 7):
                if i >= min_crit_success:
                    result_outcome_dict[i] = "CRITICAL SUCCESS"
                elif i >= roll_difficulty:
                    result_outcome_dict[i] = "SUCCESS"
                elif i <= max_crit_fail:
                    result_outcome_dict[i] = "CRITICAL FAILURE"
                else:
                    result_outcome_dict[i] = "FAILURE"
            text += ("The higher result, " + str(roll_result) + ": " + result_outcome_dict[roll_result] + ", was used. /n")
        else:
            roll_list = dice_utility.roll_to_list(6, "Trade roll", roll_difficulty, min_crit_success, max_crit_fail, self.global_manager) #0 requirement for critical fail means critical fails will not occur
            self.display_trade_die((die_x, 440), roll_list[0], roll_difficulty, min_crit_success, max_crit_fail)
                            
            text += roll_list[1]
            roll_result = roll_list[0]

        self.global_manager.set('trade_result', [self, roll_result])
        notification_tools.display_notification(text + "Click to continue.", 'final_trade', self.global_manager)

        if roll_result >= roll_difficulty:
            self.trades_remaining = math.ceil(village.population / 3)
            trade_type = 'trade'
            if (not self.veteran) and roll_result >= min_crit_success:
                text += "/nThe merchant negotiated well enough to become a veteran. /n"
                trade_type = 'trade_promotion'
            notification_tools.display_notification(text + "/nThe villagers are willing to trade " + str(self.trades_remaining) + " times. /n /nThe merchant has " + str(self.get_inventory('consumer goods')) +
                " consumer goods to sell. /n /nClick to start trading. /n /n", trade_type, self.global_manager)
            choice_info_dict = {'caravan': self, 'village': village, 'type': 'willing to trade'}
            text += "/nThe villagers are willing to trade " + str(self.trades_remaining) + " times. /n /n"
            text += "The merchant has " + str(self.get_inventory('consumer goods')) + " consumer goods to sell. /n /n"
            text += "Do you want to start trading consumer goods for items that may or may not be valuable?"
            notification_tools.display_choice_notification(text, ['trade', 'stop trading'], choice_info_dict, self.global_manager) #message, choices, choice_info_dict, global_manager
        else:
            notification_tools.display_notification(text + "/nThe villagers are not willing to trade. /n /nClick to close this notification. ", 'stop_trade', self.global_manager)

    def trade(self, notification):
        self.notification = notification
        village = self.notification.choice_info_dict['village']
        text = ("The merchant attempts to find valuable commodities in return for consumer goods. /n /n")
        roll_difficulty = 4
        if self.veteran:
            text += ("The veteran merchant can roll twice and pick the higher result /n /n")
            notification_tools.display_notification(text + "Click to roll. " + str(roll_difficulty) + "+ required on at least 1 die to succeed.", 'trade', self.global_manager)
        else:
            notification_tools.display_notification(text + "Click to roll. " + str(roll_difficulty) + "+ required to succeed.", 'trade', self.global_manager)
        notification_tools.display_notification(text + "Rolling... ", 'roll', self.global_manager)

        die_x = self.global_manager.get('notification_manager').notification_x - 140

        roll_result = 0
        if self.veteran:
            first_roll_list = dice_utility.roll_to_list(6, "Trade roll", roll_difficulty, 7, 0, self.global_manager) #0 requirement for critical fail means critical fails will not occur
            self.display_trade_die((die_x, 500), first_roll_list[0], roll_difficulty, 7, 0)
                                
            second_roll_list = dice_utility.roll_to_list(6, "second", roll_difficulty, 7, 0, self.global_manager) #0 requirement for critical fail means critical fails will not occur
            self.display_trade_die((die_x, 380), second_roll_list[0], roll_difficulty, 7, 0)
                                
            text += (first_roll_list[1] + second_roll_list[1]) #add strings from roll result to text
            roll_result = max(first_roll_list[0], second_roll_list[0])
            result_outcome_dict = {1: "CRITICAL FAILURE", 2: "FAILURE", 3: "FAILURE", 4: "SUCCESS", 5: "SUCCESS", 6: "CRITICAL SUCCESS"}
            text += ("The higher result, " + str(roll_result) + ": " + result_outcome_dict[roll_result] + ", was used. /n")
        else:
            roll_list = dice_utility.roll_to_list(6, "Trade roll", roll_difficulty, 7, 0, self.global_manager) #0 requirement for critical fail means critical fails will not occur
            self.display_trade_die((die_x, 440), roll_list[0], roll_difficulty, 7, 0)
                            
            text += roll_list[1]
            roll_result = roll_list[0]
                
        notification_tools.display_notification(text + "Click to continue.", 'final_trade', self.global_manager)
        self.trades_remaining -= 1
        num_consumer_goods = self.get_inventory('consumer goods') - 1 #consumer goods are actually lost when clicking out of notification, so subtract 1 here to show accurate number
        commodity = 'none'
        notification_type = 'none'
        if roll_result >= roll_difficulty:
            commodity = random.choice(self.global_manager.get('collectable_resources'))
            text += "/n The merchant managed to buy a unit of " + commodity + ". /n /n"
            notification_type = 'successful_commodity_trade'
        else:
            text += "/n The merchant bought items that turned out to be worthless. /n /n"
            notification_type = 'failed_commodity_trade'
        if not self.trades_remaining == 0:
            text += "The villagers are willing to trade " + str(self.trades_remaining) + " more times /n /n"
            text += "The merchant has " + str(num_consumer_goods) + " more consumer goods to sell /n /n"
        notification_tools.display_notification(text, notification_type, self.global_manager)
        if self.trades_remaining > 0 and num_consumer_goods > 0:
            choice_info_dict = {'caravan': self, 'village': village, 'type': 'trade'}
            message = "The villagers are willing to trade " + str(self.trades_remaining) + " more times /n /n"
            message += "Do you want to trade consumer goods for items that may or may not be valuable?"
            notification_tools.display_choice_notification(message, ['trade', 'stop trading'], choice_info_dict, self.global_manager) #message, choices, choice_info_dict, global_manager
        else:
            if self.trades_remaining == 0:
                text += "The villagers are not willing to trade any more this turn. /n /n"
            if num_consumer_goods <= 0: #consumer goods are actually lost when user clicks out of
                text += "The merchant does not have any more consumer goods to sell. /n /n"
            notification_tools.display_notification(text + "Click to close this notification. ", 'stop_trade', self.global_manager)
        self.global_manager.set('trade_result', [self, roll_result, commodity]) #allows notification to give random commodity when clicked
        
    def display_trade_die(self, coordinates, result, difficulty, min_crit_success, max_crit_fail):
        '''
        Input:
            tuple of two int variables representing the pixel coordinates at which to display the die, int representing the final result that the die will roll
        Output:
            Creates a die object at the inputted coordinates that will roll, eventually stopping displaying the inputted result with an outline depending on the outcome.
            If multiple dice are present, only the die with the highest result will be outlined, showing that it was chosen.
        '''
        result_outcome_dict = {'min_success': difficulty, 'min_crit_success': min_crit_success, 'max_crit_fail': max_crit_fail}
        outcome_color_dict = {'success': 'dark green', 'fail': 'dark red', 'crit_success': 'bright green', 'crit_fail': 'bright red', 'default': 'black'}
        new_die = dice.die(scaling.scale_coordinates(coordinates[0], coordinates[1], self.global_manager), scaling.scale_width(100, self.global_manager), scaling.scale_height(100, self.global_manager), ['strategic'], 6,
            result_outcome_dict, outcome_color_dict, result, self.global_manager)

class mission(group):
    def __init__(self, coordinates, grids, image_id, name, modes, worker, officer, global_manager):
        '''
        Input:
            same as superclass
        '''
        super().__init__(coordinates, grids, image_id, name, modes, worker, officer, global_manager)

class expedition(group):
    '''
    A group with an explorer officer that is able to explore
    '''
    def __init__(self, coordinates, grids, image_id, name, modes, worker, officer, global_manager):
        '''
        Input:
            same as superclass
        '''
        super().__init__(coordinates, grids, image_id, name, modes, worker, officer, global_manager)
        self.exploration_mark_list = []
        self.exploration_cost = 2
        self.can_explore = True

    def display_exploration_die(self, coordinates, result):
        '''
        Input:
            tuple of two int variables representing the pixel coordinates at which to display the die, int representing the final result that the die will roll
        Output:
            Creates a die object at the inputted coordinates that will roll, eventually stopping displaying the inputted result with an outline depending on the outcome.
            If multiple dice are present, only the die with the highest result will be outlined, showing that it was chosen.
        '''
        result_outcome_dict = {'min_success': 4, 'min_crit_success': 6, 'max_crit_fail': 1}
        outcome_color_dict = {'success': 'dark green', 'fail': 'dark red', 'crit_success': 'bright green', 'crit_fail': 'bright red', 'default': 'black'}
        new_die = dice.die(scaling.scale_coordinates(coordinates[0], coordinates[1], self.global_manager), scaling.scale_width(100, self.global_manager), scaling.scale_height(100, self.global_manager), ['strategic'], 6,
            result_outcome_dict, outcome_color_dict, result, self.global_manager)

    def move(self, x_change, y_change):
        '''
        Input:
            Same as superclass
        Output:
            Same as superclass when moving into explored areas.
            When moving into explored areas, the expedition will attempt to explore there, showing a series of notifications and dice rolls.
            An exploration will result in the death of the expedition, no change, exploring the area, or exploring the area and promoting to the expedition's officer to a veteran, depending on the dice roll's result.
            Within the move function, an exploration's result will be determined. However, its outcome will not be shown until the last of the exploration notifications is shown, at which point the outcome is
            shown through the complete_exploration function.
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
        if future_cell.visible == False: #if moving to unexplored area, try to explore it
            if self.global_manager.get('money_tracker').get() >= self.exploration_cost:
                choice_info_dict = {'expedition': self, 'x_change': x_change, 'y_change': y_change, 'cost': self.exploration_cost, 'type': 'exploration'}
                notification_tools.display_choice_notification('Are you sure you want to spend ' + str(choice_info_dict['cost']) + ' money to attempt an exploration to the ' + direction + '?', ['exploration', 'stop exploration'],
                    choice_info_dict, self.global_manager) #message, choices, choice_info_dict, global_manager
                self.global_manager.set('ongoing_exploration', True)
                for current_grid in self.grids:
                    coordinates = (0, 0)
                    if current_grid.is_mini_grid:
                        coordinates = current_grid.get_mini_grid_coordinates(self.x + x_change, self.y + y_change)
                    else:
                        coordinates = (self.x + x_change, self.y + y_change)
                    self.global_manager.get('exploration_mark_list').append(tile(coordinates, current_grid, 'misc/exploration_x/' + direction + '_x.png', 'exploration mark', ['strategic'], False, self.global_manager))
            else:
                text_tools.print_to_screen("You do not have enough money to attempt an exploration.", self.global_manager)
        else: #if moving to explored area, move normally
            super().move(x_change, y_change)

    def start_exploration(self, x_change, y_change):
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
        self.just_promoted = False
        text = ""
        text += "The expedition heads towards the " + direction + ". /n /n"
        text += (self.global_manager.get('flavor_text_manager').generate_flavor_text('explorer') + " /n /n")
        
        if not self.veteran:    
            notification_tools.display_notification(text + "Click to roll. 4+ required to succeed.", 'exploration', self.global_manager)
        else:
            text += ("The veteran explorer can roll twice and pick the higher result /n /n")
            notification_tools.display_notification(text + "Click to roll. 4+ required on at least 1 die to succeed.", 'exploration', self.global_manager)

        notification_tools.display_notification(text + "Rolling... ", 'roll', self.global_manager)

        die_x = self.global_manager.get('notification_manager').notification_x - 140

        if self.veteran:
                
            first_roll_list = dice_utility.roll_to_list(6, "Exploration roll", 4, 6, 1, self.global_manager)
            self.display_exploration_die((die_x, 500), first_roll_list[0])
                                
            second_roll_list = dice_utility.roll_to_list(6, "second", 4, 6, 1, self.global_manager)
            self.display_exploration_die((die_x, 380), second_roll_list[0])
                                
            text += (first_roll_list[1] + second_roll_list[1]) #add strings from roll result to text
            roll_result = max(first_roll_list[0], second_roll_list[0])
            result_outcome_dict = {1: "CRITICAL FAILURE", 2: "FAILURE", 3: "FAILURE", 4: "SUCCESS", 5: "SUCCESS", 6: "CRITICAL SUCCESS"}
            text += ("The higher result, " + str(roll_result) + ": " + result_outcome_dict[roll_result] + ", was used. /n")
        else:
            roll_list = dice_utility.roll_to_list(6, "Exploration roll", 4, 6, 1, self.global_manager)
            self.display_exploration_die((die_x, 440), roll_list[0])
                
            text += roll_list[1]
            roll_result = roll_list[0]

        notification_tools.display_notification(text + "Click to continue.", 'exploration', self.global_manager)
            
        text += "/n"
        if roll_result >= 4: #4+ required on D6 for exploration
            if not future_cell.resource == 'none':
                text += "You discovered a " + future_cell.terrain.upper() + " tile with a " + future_cell.resource.upper() + " resource. /n"
            else:
                text += "You discovered a " + future_cell.terrain.upper() + " tile. /n"
        else:
            text += "You were not able to explore the tile. /n"
        if roll_result == 1:
            text += "Everyone in the expedition has died. /n" #actual death occurs when exploration completes

        if (not self.veteran) and roll_result == 6:
            self.veteran = True
            self.just_promoted = True
            text += "This explorer has become a veteran explorer. /n"
        if roll_result >= 4:
            self.destination_cell = future_cell
            notification_tools.display_notification(text + "Click to remove this notification.", 'final_exploration', self.global_manager)
        else:
            notification_tools.display_notification(text, 'default', self.global_manager)
        self.global_manager.set('exploration_result', [self, roll_result, x_change, y_change])

    def complete_exploration(self): #roll_result, x_change, y_change
        '''
        Input:
            none
        Output:
            Shows the outcome of an exploration attempt, which was previously determined in the move function
        '''
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
                self.change_movement_points(-1 * self.get_movement_cost(x_change, y_change)) #when exploring, movement points should be consumed regardless of exploration success or destination
        else:
            self.change_movement_points(-1 * self.get_movement_cost(x_change, y_change)) #when exploring, movement points should be consumed regardless of exploration success or destination
        if self.just_promoted:
            self.promote()
        elif roll_result == 1:
            self.die()
            died = True
        copy_dice_list = self.global_manager.get('dice_list')
        for current_die in copy_dice_list:
            current_die.remove()
        actor_utility.stop_exploration(self.global_manager) #make function that sets ongoing exploration to false and destroys exploration marks

def create_group(worker, officer, global_manager):
    '''
    Input:
        worker object representing the worker that will join the group, officer object representing the officer that will join the group, global_manager_template object
    Output:
        Causes the inputted officer to form a group with inputted worker.
        The type of group formed will depend on the type of officer. An explorer officer will create an expedition, which is able to explore.
        The formed group's inventory will be the combination of the inventories of the officer and the worker.
        Upon joining a group, the worker and officer will be stored by the group and will not be able to be seen or selected.
        Upon the disbanding of a group, its worker and officer will be restored and placed in the same tile as the group, with the officer being given the group's inventory.
    '''
    if officer.officer_type == 'explorer':
        new_group = expedition((officer.x, officer.y), officer.grids, 'mobs/explorer/expedition.png', 'Expedition', officer.modes, worker, officer, global_manager)
    elif officer.officer_type == 'engineer':
        new_group = construction_gang((officer.x, officer.y), officer.grids, 'mobs/engineer/construction_gang.png', 'Construction gang', officer.modes, worker, officer, global_manager)
    elif officer.officer_type == 'porter foreman':
        new_group = porters((officer.x, officer.y), officer.grids, 'mobs/porter foreman/porters.png', 'Porters', officer.modes, worker, officer, global_manager)
    elif officer.officer_type == 'merchant':
        new_group = caravan((officer.x, officer.y), officer.grids, 'mobs/merchant/caravan.png', 'Caravan', officer.modes, worker, officer, global_manager)
    elif officer.officer_type == 'missionary':
        new_group = mission((officer.x, officer.y), officer.grids, 'mobs/missionary/mission.png', 'Mission', officer.modes, worker, officer, global_manager)
    else:
        new_group = group((officer.x, officer.y), officer.grids, 'mobs/default/default.png', 'Expedition', officer.modes, worker, officer, global_manager)
