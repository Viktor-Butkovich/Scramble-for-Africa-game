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
    Mob that is created by a combination of a worker and officer, has special capabilities depending on its officer, and separates its worker and officer upon being disbanded
    '''
    def __init__(self, coordinates, grids, image_id, name, modes, worker, officer, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates on one of the game grids
            grid list grids: grids in which this group's images can appear
            string image_id: File path to the image used by this object
            string name: this group's name
            string list modes: Game modes during which this group's images can appear
            worker worker: worker component of this group
            officer officer: officer component of this group
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.worker = worker
        self.officer = officer
        #self.veteran = self.officer.veteran
        super().__init__(coordinates, grids, image_id, name, modes, global_manager)
        self.worker.join_group()
        self.officer.join_group()
        self.is_group = True
        self.veteran = self.officer.veteran
        for current_commodity in self.global_manager.get('commodity_types'): #merges individual inventory to group inventory and clears individual inventory
            self.change_inventory(current_commodity, self.worker.get_inventory(current_commodity))
            self.change_inventory(current_commodity, self.officer.get_inventory(current_commodity))
        self.worker.inventory_setup()
        self.officer.inventory_setup()
        self.select()
        if self.veteran:
            self.set_name("Veteran " + self.name.lower())
        self.veteran_icons = self.officer.veteran_icons
        for current_veteran_icon in self.veteran_icons:
            current_veteran_icon.actor = self
        self.global_manager.get('group_list').append(self)
        if self.worker.movement_points > self.officer.movement_points: #a group should keep the lowest movement points out of its members
            self.set_movement_points(self.officer.movement_points)
        else:
            self.set_movement_points(self.worker.movement_points)

    def promote(self):
        '''
        Description:
            Promotes this group's officer to a veteran after performing various actions particularly well, improving the capabilities of groups the officer is attached to in the future. Creates a veteran star icon that follows this
                group and its officer
        Input:
            None
        Output:
            None
        '''
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
        Description:
            Links this group to a grid, causing it to appear on that grid and its minigrid at certain coordinates. Used when crossing the ocean and when a group that was previously attached to another actor becomes independent and
                visible, like when a group disembarks a ship. Also moves its officer and worker to the new grid
        Input:
            grid new_grid: grid that this group is linked to
            int tuple new_coordinates: Two values representing x and y coordinates to start at on the inputted grid
        Output:
            None
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
        Description:
            Sets this group's tooltip to what it should be whenever the player looks at the tooltip. By default, sets tooltip to this group's name, the names of its officer and worker, and its movement points
        Input:
            None
        Output:
            None
        '''
        self.set_tooltip(["Name: " + self.name, '    Officer: ' + self.officer.name, '    Worker: ' + self.worker.name, "Movement points: " + str(self.movement_points) + "/" + str(self.max_movement_points)])

    def disband(self):
        '''
        Description:
            Separates this group into its officer and worker, destroying the group
        Input:
            None
        Output:
            None
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
        Description:
            Removes this object from relevant lists, prevents it from further appearing in or affecting the program, deselects it, and drops any commodities it is carrying. Used when the group is being disbanded, since it does not
                remove its worker or officer
        Input:
            None
        Output:
            None
        '''
        super().remove()
        self.global_manager.set('group_list', utility.remove_from_list(self.global_manager.get('group_list'), self))

    def die(self):
        '''
        Description:
            Removes this object from relevant lists, prevents it from further appearing in or affecting the program, deselects it, and drops any commodities it is carrying. Unlike remove, this is used when the group dies because it
                also removes its worker and officer
        Input:
            None
        Output:
            None
        '''
        self.remove()
        self.officer.remove()
        self.worker.remove()

class porters(group):
    '''
    A group with a porter foreman officer that can hold commodities
    '''
    def __init__(self, coordinates, grids, image_id, name, modes, worker, officer, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates on one of the game grids
            grid list grids: grids in which this group's images can appear
            string image_id: File path to the image used by this object
            string name: this group's name
            string list modes: Game modes during which this group's images can appear
            worker worker: worker component of this group
            officer officer: officer component of this group
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(coordinates, grids, image_id, name, modes, worker, officer, global_manager)
        self.can_hold_commodities = True
        self.inventory_capacity = 9
        self.inventory_setup()
        actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self) #updates mob info display list to account for inventory capacity changing

class construction_gang(group):
    '''
    A group with an engineer officer that is able to construct buildings and trains
    '''
    def __init__(self, coordinates, grids, image_id, name, modes, worker, officer, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates on one of the game grids
            grid list grids: grids in which this group's images can appear
            string image_id: File path to the image used by this object
            string name: this group's name
            string list modes: Game modes during which this group's images can appear
            worker worker: worker component of this group
            officer officer: officer component of this group
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(coordinates, grids, image_id, name, modes, worker, officer, global_manager)
        self.can_construct = True
        actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self) #updates mob info display list to account for can_construct changing

class caravan(group):
    '''
    A group with a merchant officer that is able to establish trading posts and trade with native villages
    '''
    def __init__(self, coordinates, grids, image_id, name, modes, worker, officer, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates on one of the game grids
            grid list grids: grids in which this group's images can appear
            string image_id: File path to the image used by this object
            string name: this group's name
            string list modes: Game modes during which this group's images can appear
            worker worker: worker component of this group
            officer officer: officer component of this group
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(coordinates, grids, image_id, name, modes, worker, officer, global_manager)
        self.can_hold_commodities = True
        self.can_trade = True
        self.inventory_capacity = 9
        self.trades_remaining = 0
        self.current_trade_modifier = 0
        self.default_min_success = 4
        self.default_max_crit_fail = 1
        self.inventory_setup()
        actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self) #updates mob info display list to account for inventory capacity changing

    def start_trade(self):
        '''
        Description:
            Used when the player clicks on the trade button, displays a choice notification that allows the player to trade or not. Choosing to trade starts the trading process and
                consumes the caravan's movement points
        Input:
            None
        Output:
            None
        '''
        village = self.images[0].current_cell.village
        choice_info_dict = {'caravan': self, 'village': village, 'type': 'start trading'}
        self.global_manager.set('ongoing_trade', True)
        message = "Are you sure you want to attempt to trade with the village of " + village.name + "? /n /n"

        self.current_trade_modifier = 0
        self.current_min_success = self.default_min_success
        self.current_max_crit_fail = self.default_max_crit_fail
        #determine modifier here

        if village.cell.contained_buildings['trading_post'] == 'none': #penalty for no trading post
            self.current_trade_modifier -= 1
            message += "Without an established trading post, the merchant will have difficulty convincing villagers to trade. /n /n"
        
        aggressiveness_modifier = village.get_aggressiveness_modifier()
        if aggressiveness_modifier < 0:
            message += "The villagers are hostile and are unlikely to be willing to trade. /n /n"
        elif aggressiveness_modifier > 0:
            message += "The villagers are friendly and are likely to be willing to trade. /n /n"
        else:
            message += "The villagers are wary of the merchant but may be willing to trade. /n /n"
        self.current_trade_modifier += aggressiveness_modifier

        if self.current_trade_modifier == 0: #1/6 death = moderate risk
            message += "moderate risk message /n /n"
        elif self.current_trade_modifier > 0: #0/6 = no risk
            message += "low risk message /n /n"
        elif self.current_trade_modifier == -1: #2/6 = high risk
            message += "high risk message /n /n"
        else: #3/6 or higher = extremely high risk
            message += "extremely high risk message /n /n"
        
        self.current_min_success -= self.current_trade_modifier #positive modifier reduces number required for succcess, reduces maximum that can be crit fail
        self.current_max_crit_fail -= self.current_trade_modifier
        message += "In each trade, the merchant trades 1 of his " + str(self.get_inventory('consumer goods')) + " consumer goods for items that may or may not be valuable. /n /n"
        message += "Trading may also convince villagers to become available for hire as workers. "
        notification_tools.display_choice_notification(message, ['start trading', 'stop trading'], choice_info_dict, self.global_manager) #message, choices, choice_info_dict, global_manager

    def willing_to_trade(self, notification):
        '''
        Description:
            Used when the player decides to start trading, allows the player to roll a die to see if the villagers are willing to trade. If they are willing to trade, displays a choice notification that allows the player to start the
                transaction process or not. Otherwise, stops the trading process
        Input:
            notification notification: the current trade notification, used to access information relating to the trade such as which village is being traded with
        Output:
            None
        '''
        self.notification = notification
        self.set_movement_points(0)
        village = self.notification.choice_info_dict['village']
        text = ("The merchant attempts to convince the villagers to trade. /n /n")
        #roll_difficulty = 4
        #min_crit_success = 6
        #max_crit_fail = 0
        #difficulty_modifier = village.get_aggressiveness_modifier()
        #if difficulty_modifier == 1:
        #    text += ("The villagers are hostile and are less likely to be willing to trade. /n /n")
        #elif difficulty_modifier == -1:
        #    text += ("The villagers are friendly and more likely to be willing to trade. /n /n")
        #roll_difficulty += difficulty_modifier #modifier adds to difficulty, not roll
        if self.veteran:
            text += ("The veteran merchant can roll twice and pick the higher result /n /n")
            notification_tools.display_notification(text + "Click to roll. " + str(self.current_min_success) + "+ required on at least 1 die to succeed.", 'trade', self.global_manager)
        else:
            notification_tools.display_notification(text + "Click to roll. " + str(self.current_min_success) + "+ required to succeed.", 'trade', self.global_manager)
        notification_tools.display_notification(text + "Rolling... ", 'roll', self.global_manager)

        die_x = self.global_manager.get('notification_manager').notification_x - 140

        roll_result = 0
        if self.veteran:
                
            first_roll_list = dice_utility.roll_to_list(6, "Trade roll", self.current_min_success, 6, self.current_max_crit_fail, self.global_manager) #0 requirement for critical fail means critical fails will not occur
            self.display_trade_die((die_x, 500), first_roll_list[0], self.current_min_success, 6, self.current_max_crit_fail)
                                
            second_roll_list = dice_utility.roll_to_list(6, "second", self.current_min_success, 6, self.current_max_crit_fail, self.global_manager) #0 requirement for critical fail means critical fails will not occur
            self.display_trade_die((die_x, 380), second_roll_list[0], self.current_min_success, 6, self.current_max_crit_fail)
                                
            text += (first_roll_list[1] + second_roll_list[1]) #add strings from roll result to text
            roll_result = max(first_roll_list[0], second_roll_list[0])
            result_outcome_dict = {}
            for i in range(1, 7):
                if i <= self.current_max_crit_fail:
                    word = "CRITICAL FAILURE"
                elif i == 6:
                    word = "CRITICAL SUCCESS"
                elif i >= self.current_min_success:
                    word = "SUCCESS"
                else:
                    word = "FAILURE"
                result_outcome_dict[i] = word
            text += ("The higher result, " + str(roll_result) + ": " + result_outcome_dict[roll_result] + ", was used. /n")
        else:
            roll_list = dice_utility.roll_to_list(6, "Trade roll", self.current_min_success, 6, self.current_max_crit_fail, self.global_manager) #0 requirement for critical fail means critical fails will not occur
            self.display_trade_die((die_x, 440), roll_list[0], self.current_min_success, 6, self.current_max_crit_fail)
                            
            text += roll_list[1]
            roll_result = roll_list[0]

        self.global_manager.set('trade_result', [self, roll_result])
        notification_tools.display_notification(text + "Click to continue.", 'final_trade', self.global_manager)

        if roll_result >= self.current_min_success:
            self.trades_remaining = math.ceil(village.population / 3)
            trade_type = 'trade'
            if (not self.veteran) and roll_result >= 6: #promotion occurs when trade_promotion notification appears, in notification_to_front in notification_manager
                text += "/nThe merchant negotiated well enough to become a veteran. /n"
                trade_type = 'trade_promotion'
            notification_tools.display_notification(text + "/nThe villagers are willing to trade " + str(self.trades_remaining) + " times. /n /nThe merchant has " + str(self.get_inventory('consumer goods')) +
                " consumer goods to sell. /n /nClick to start trading. /n /n", trade_type, self.global_manager)
            choice_info_dict = {'caravan': self, 'village': village, 'type': 'willing to trade'}
            text += "/nThe villagers are willing to trade " + str(self.trades_remaining) + " times. /n /n"
            text += "The merchant has " + str(self.get_inventory('consumer goods')) + " consumer goods to sell. /n /n"
            text += "Do you want to start trading consumer goods for items that may or may not be valuable?"
            notification_tools.display_choice_notification(text, ['trade', 'stop trading'], choice_info_dict, self.global_manager) #message, choices, choice_info_dict, global_manager
        elif roll_result <= self.current_max_crit_fail:
            notification_tools.display_notification(text + "/nThe villagers are not willing to trade and are angered enough to attack the caravan. /n /nEveryone in the caravan has died. /n /nClick to close this notification. ",
                'stop_trade_attacked', self.global_manager)
        else:
            notification_tools.display_notification(text + "/nThe villagers are not willing to trade. /n /nClick to close this notification. ", 'stop_trade', self.global_manager)

    def trade(self, notification):
        '''
        Description:
            Used in each part of the transaction process, allows the player to sell a unit of consumer goods and roll a die to try to find commodities in return. After the transaction, if the villagers are able to trade more and the
                caravan has more consumer goods to sell, displays a choice notification that allows the player to start another transaction or not. Otherwise, stops the trading process
        Input:
            notification notification: the current trade notification, used to access information relating to the trade such as which village is being traded with
        Output:
            None
        '''
        self.current_trade_modifier = 0 #trading - getting good deals - is different from the willingness to trade roll and uses different modifiers
        self.current_min_success = 4
        self.current_max_crit_fail = 0 #0 requirement for critical fail means critical fails will not occur
        #determine modifier here
        self.current_min_success -= self.current_trade_modifier #positive modifier reduces number required for succcess, reduces maximum that can be crit fail
        self.current_max_crit_fail -= self.current_trade_modifier
        
        self.notification = notification
        village = self.notification.choice_info_dict['village']
        text = ("The merchant attempts to find valuable commodities in return for consumer goods. /n /n")
        if self.veteran:
            text += ("The veteran merchant can roll twice and pick the higher result /n /n")
            notification_tools.display_notification(text + "Click to roll. " + str(self.current_min_success) + "+ required on at least 1 die to succeed.", 'trade', self.global_manager)
        else:
            notification_tools.display_notification(text + "Click to roll. " + str(self.current_min_success) + "+ required to succeed.", 'trade', self.global_manager)
        notification_tools.display_notification(text + "Rolling... ", 'roll', self.global_manager)

        die_x = self.global_manager.get('notification_manager').notification_x - 140

        roll_result = 0
        if self.veteran:
            first_roll_list = dice_utility.roll_to_list(6, "Trade roll", roll_difficulty, 7, self.current_max_crit_fail, self.global_manager)
            self.display_trade_die((die_x, 500), first_roll_list[0], roll_difficulty, 7, self.current_max_crit_fail)
                                
            second_roll_list = dice_utility.roll_to_list(6, "second", roll_difficulty, 7, self.current_max_crit_fail, self.global_manager) #7 requirement for crit success - can't promote from trade deal, only willingness to trade roll
            self.display_trade_die((die_x, 380), second_roll_list[0], roll_difficulty, 7, self.current_max_crit_fail)
                                
            text += (first_roll_list[1] + second_roll_list[1]) #add strings from roll result to text
            roll_result = max(first_roll_list[0], second_roll_list[0])
            result_outcome_dict = {}
            for i in range(1, 7):
                if i <= self.current_max_crit_fail:
                    word = "CRITICAL FAILURE"
                elif i == 6:
                    word = "CRITICAL SUCCESS"
                elif i >= self.current_min_success:
                    word = "SUCCESS"
                else:
                    word = "FAILURE"
                result_outcome_dict[i] = word
            text += ("The higher result, " + str(roll_result) + ": " + result_outcome_dict[roll_result] + ", was used. /n")
        else:
            roll_list = dice_utility.roll_to_list(6, "Trade roll", roll_difficulty, 7, self.current_max_crit_fail, self.global_manager) #0 requirement for critical fail means critical fails will not occur
            self.display_trade_die((die_x, 440), roll_list[0], roll_difficulty, 7, self.current_max_crit_fail)
                            
            text += roll_list[1]
            roll_result = roll_list[0]
                
        notification_tools.display_notification(text + "Click to continue.", 'final_trade', self.global_manager)
        self.trades_remaining -= 1
        num_consumer_goods = self.get_inventory('consumer goods') - 1 #consumer goods are actually lost when clicking out of notification, so subtract 1 here to show accurate number
        commodity = 'none'
        notification_type = 'none'
        if roll_result >= self.current_min_success:
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
        
    def display_trade_die(self, coordinates, result, min_success, min_crit_success, max_crit_fail):
        '''
        Description:
            Creates a die object with preset colors and the inputted location, possible roll outcomes, and predetermined roll result to use for trade rolls
        Input:
            int tuple coordinates: Two values representing x and y pixel coordinates for the bottom left corner of the die
            int result: Predetermined result that the die will end on after rolling
            int difficulty: Minimum roll required for a success
            int min_crit_success: Minimum roll require for a critical success
            int max_crit_fail: Maximum roll required for a critical failure
        Output:
            None
        '''
        result_outcome_dict = {'min_success': min_success, 'min_crit_success': min_crit_success, 'max_crit_fail': max_crit_fail}
        outcome_color_dict = {'success': 'dark green', 'fail': 'dark red', 'crit_success': 'bright green', 'crit_fail': 'bright red', 'default': 'black'}
        new_die = dice.die(scaling.scale_coordinates(coordinates[0], coordinates[1], self.global_manager), scaling.scale_width(100, self.global_manager), scaling.scale_height(100, self.global_manager), ['strategic'], 6,
            result_outcome_dict, outcome_color_dict, result, self.global_manager)

class missionaries(group):
    '''
    A group with a head missionary officer and church volunteer workers that can build churches and convert native villages
    '''
    def __init__(self, coordinates, grids, image_id, name, modes, worker, officer, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates on one of the game grids
            grid list grids: grids in which this group's images can appear
            string image_id: File path to the image used by this object
            string name: this group's name
            string list modes: Game modes during which this group's images can appear
            worker worker: worker component of this group
            officer officer: officer component of this group
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(coordinates, grids, image_id, name, modes, worker, officer, global_manager)
        self.can_convert = True
        self.current_convert_modifier = 0
        self.default_min_success = 4
        self.default_max_crit_fail = 1

    def start_converting(self):
        village = self.images[0].current_cell.village
        self.current_convert_modifier = 0
        self.current_min_success = self.default_min_success
        self.current_max_crit_fail = self.default_max_crit_fail
        message = "Are you sure you want to start converting natives? /n /n"
        
        if village.cell.contained_buildings['mission'] == 'none': #penalty for no mission
            self.current_convert_modifier -= 1
            message += "no mission penalty message /n"
            
        aggressiveness_modifier = village.get_aggressiveness_modifier()
        if aggressiveness_modifier < 0:
            message += "high aggressiveness penalty message /n"
        elif aggressiveness_modifier > 0:
            message += "low aggressiveness bonus message /n"
        self.current_convert_modifier += aggressiveness_modifier

        population_modifier = village.get_population_modifier()
        if population_modifier < 0:
            message += "high population penalty message /n"
        elif population_modifier > 0:
            message += "low population bonus message /n"
        self.current_convert_modifier += population_modifier

        if self.current_convert_modifier == 0: #1/6 death = moderate risk
            message += "moderate risk message /n"
        elif self.current_convert_modifier > 0: #0/6 = no risk
            message += "low risk message /n"
        elif self.current_convert_modifier == -1: #2/6 = high risk
            message += "high risk message /n"
        else: #3/6 or higher = extremely high risk
            message += "extremely high risk message"
            
            
        self.current_min_success -= self.current_convert_modifier #positive modifier reduces number required for succcess, reduces maximum that can be crit fail
        self.current_max_crit_fail -= self.current_convert_modifier
        
        choice_info_dict = {'head missionary': self,'type': 'start converting'}
        self.current_convert_modifier = 0
        self.global_manager.set('ongoing_conversion', True)
        notification_tools.display_choice_notification(message, ['start converting', 'stop converting'], choice_info_dict, self.global_manager) #message, choices, choice_info_dict, global_manager+

    def convert(self):
        roll_result = 0
        self.just_promoted = False
        self.set_movement_points(0)
        village = self.images[0].current_cell.village
        text = ""
        text += "The missionaries try to convert the natives to reduce their aggressiveness. /n /n"

        if not self.veteran:    
            notification_tools.display_notification(text + "Click to roll. " + str(self.current_min_success) + "+ required to succeed.", 'convert', self.global_manager)
        else:
            text += ("The veteran head missionary can roll twice and pick the higher result /n /n")
            notification_tools.display_notification(text + "Click to roll. " + str(self.current_min_success) + "+ required on at least 1 die to succeed.", 'convert', self.global_manager)

        notification_tools.display_notification(text + "Rolling... ", 'roll', self.global_manager)

        die_x = self.global_manager.get('notification_manager').notification_x - 140

        if self.veteran:
            first_roll_list = dice_utility.roll_to_list(6, "Conversion roll", self.current_min_success, 6, self.current_max_crit_fail, self.global_manager)
            self.display_conversion_die((die_x, 500), first_roll_list[0])
                                
            second_roll_list = dice_utility.roll_to_list(6, "second", self.current_min_success, 6, self.current_max_crit_fail, self.global_manager)
            self.display_conversion_die((die_x, 380), second_roll_list[0])
                                
            text += (first_roll_list[1] + second_roll_list[1]) #add strings from roll result to text
            roll_result = max(first_roll_list[0], second_roll_list[0])
            result_outcome_dict = {}
            for i in range(1, 7):
                if i <= self.current_max_crit_fail:
                    word = "CRITICAL FAILURE"
                elif i == 6:
                    word = "CRITICAL SUCCESS"
                elif i >= self.current_min_success:
                    word = "SUCCESS"
                else:
                    word = "FAILURE"
                result_outcome_dict[i] = word
            text += ("The higher result, " + str(roll_result) + ": " + result_outcome_dict[roll_result] + ", was used. /n")
        else:
            roll_list = dice_utility.roll_to_list(6, "Conversion roll", self.current_min_success, 6, self.current_max_crit_fail, self.global_manager)
            self.display_conversion_die((die_x, 440), roll_list[0])
                
            text += roll_list[1]
            roll_result = roll_list[0]

        notification_tools.display_notification(text + "Click to continue.", 'conversion', self.global_manager)
            
        text += "/n"
        if roll_result >= self.current_min_success: #4+ required on D6 for exploration
            text += "Natives converted message - aggressiveness reduced from " + str(village.aggressiveness) + " to " + str(village.aggressiveness - 1) + " /n"
        else:
            text += "Natives not converted message /n"
        if roll_result <= self.current_max_crit_fail:
            text += "/nThe natives attack you message /n" #actual 'death' occurs when religious campaign completes

        if (not self.veteran) and roll_result == 6:
            self.just_promoted = True
            text += "The head missionary did well enough to become a veteran message /n"
        if roll_result >= self.current_min_success:
            notification_tools.display_notification(text + "Click to remove this notification.", 'final_conversion', self.global_manager)
        else:
            notification_tools.display_notification(text, 'default', self.global_manager)
        self.global_manager.set('conversion_result', [self, roll_result, village])

    def complete_conversion(self):
        roll_result = self.global_manager.get('conversion_result')[1]
        if roll_result >= self.current_min_success: #if campaign succeeded
            self.global_manager.get('conversion_result')[2].change_aggressiveness(-1) #village
            if roll_result == 6 and not self.veteran:
                self.promote()
            self.select()
            for current_image in self.images: #move mob to front of each stack it is in - also used in button.same_tile_icon.on_click(), make this a function of all mobs to move to front of tile
                if not current_image.current_cell == 'none':
                    while not self == current_image.current_cell.contained_mobs[0]:
                        current_image.current_cell.contained_mobs.append(current_image.current_cell.contained_mobs.pop(0))
        if roll_result <= self.current_max_crit_fail:
            self.die()
        self.global_manager.set('ongoing_conversion', False)
        
    def display_conversion_die(self, coordinates, result):
        result_outcome_dict = {'min_success': self.current_min_success, 'min_crit_success': 6, 'max_crit_fail': self.current_max_crit_fail}
        outcome_color_dict = {'success': 'dark green', 'fail': 'dark red', 'crit_success': 'bright green', 'crit_fail': 'bright red', 'default': 'black'}
        new_die = dice.die(scaling.scale_coordinates(coordinates[0], coordinates[1], self.global_manager), scaling.scale_width(100, self.global_manager), scaling.scale_height(100, self.global_manager), self.modes, 6,
            result_outcome_dict, outcome_color_dict, result, self.global_manager)

class expedition(group):
    '''
    A group with an explorer officer that is able to explore
    '''
    def __init__(self, coordinates, grids, image_id, name, modes, worker, officer, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates on one of the game grids
            grid list grids: grids in which this group's images can appear
            string image_id: File path to the image used by this object
            string name: this group's name
            string list modes: Game modes during which this group's images can appear
            worker worker: worker component of this group
            officer officer: officer component of this group
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(coordinates, grids, image_id, name, modes, worker, officer, global_manager)
        self.exploration_mark_list = []
        self.exploration_cost = 2
        self.can_explore = True
        self.current_exploration_modifier = 0
        self.default_min_success = 4
        self.default_max_crit_fail = 1

    def display_exploration_die(self, coordinates, result):
        '''
        Description:
            Creates a die object with preset colors and possible roll outcomes and the inputted location and predetermined roll result to use for exploration rolls
        Input:
            int tuple coordinates: Two values representing x and y pixel coordinates for the bottom left corner of the die
            int result: Predetermined result that the die will end on after rolling
        Output:
            None
        '''
        result_outcome_dict = {'min_success': self.current_min_success, 'min_crit_success': 6, 'max_crit_fail': self.current_max_crit_fail}
        outcome_color_dict = {'success': 'dark green', 'fail': 'dark red', 'crit_success': 'bright green', 'crit_fail': 'bright red', 'default': 'black'}
        new_die = dice.die(scaling.scale_coordinates(coordinates[0], coordinates[1], self.global_manager), scaling.scale_width(100, self.global_manager), scaling.scale_height(100, self.global_manager), ['strategic'], 6,
            result_outcome_dict, outcome_color_dict, result, self.global_manager)

    def move(self, x_change, y_change):
        '''
        Description:
            Moves this mob x_change to the right and y_change upward. Moving to a ship in the water automatically embarks the ship. Also allows exploration when moving into unexplored areas. Attempting an exploration starts the
                exploration process, which requires various dice rolls to succeed and can also result in the death of the expedition or the promotion of its explorer. A successful exploration uncovers the area and units to move into it
                normally in the future
        Input:
            int x_change: How many cells are moved to the right in the movement
            int y_change: How many cells are moved upward in the movement
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
        '''
        Description:
            Used when the player issues a move order into an unexplored area with an expedition, displays a choice notification that allows the player to explore or not. Choosing to explore starts the exploration process. This function
                also determines the expedition's result, but the results are only shown to the player after a dice roll and the complete_exploration function
        Input:
            None
        Output:
            None
        '''
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

        self.current_exploration_modifier = 0
        self.current_min_success = self.default_min_success
        self.current_max_crit_fail = self.default_max_crit_fail
        #determine modifier here
        self.current_min_success -= self.current_exploration_modifier #positive modifier reduces number required for succcess, reduces maximum that can be crit fail
        self.current_max_crit_fail -= self.current_exploration_modifier
        
        self.just_promoted = False
        text = ""
        text += "The expedition heads towards the " + direction + ". /n /n"
        text += (self.global_manager.get('flavor_text_manager').generate_flavor_text('explorer') + " /n /n")
        
        if not self.veteran:    
            notification_tools.display_notification(text + "Click to roll. " + str(self.current_min_success) + "+ required to succeed.", 'exploration', self.global_manager)
        else:
            text += ("The veteran explorer can roll twice and pick the higher result /n /n")
            notification_tools.display_notification(text + "Click to roll. " + str(self.current_min_success) + "+ required on at least 1 die to succeed.", 'exploration', self.global_manager)

        notification_tools.display_notification(text + "Rolling... ", 'roll', self.global_manager)

        die_x = self.global_manager.get('notification_manager').notification_x - 140

        if self.veteran:
                
            first_roll_list = dice_utility.roll_to_list(6, "Exploration roll", self.current_min_success, 6, self.current_max_crit_fail, self.global_manager)
            self.display_exploration_die((die_x, 500), first_roll_list[0])
                                
            second_roll_list = dice_utility.roll_to_list(6, "second", self.current_min_success, 6, self.current_max_crit_fail, self.global_manager)
            self.display_exploration_die((die_x, 380), second_roll_list[0])
                                
            text += (first_roll_list[1] + second_roll_list[1]) #add strings from roll result to text
            roll_result = max(first_roll_list[0], second_roll_list[0])
            result_outcome_dict = {}
            for i in range(1, 7):
                if i <= self.current_max_crit_fail:
                    word = "CRITICAL FAILURE"
                elif i == 6:
                    word = "CRITICAL SUCCESS"
                elif i >= self.current_min_success:
                    word = "SUCCESS"
                else:
                    word = "FAILURE"
                result_outcome_dict[i] = word
            text += ("The higher result, " + str(roll_result) + ": " + result_outcome_dict[roll_result] + ", was used. /n")
        else:
            roll_list = dice_utility.roll_to_list(6, "Exploration roll", self.current_min_success, 6, self.current_max_crit_fail, self.global_manager)
            self.display_exploration_die((die_x, 440), roll_list[0])
                
            text += roll_list[1]
            roll_result = roll_list[0]

        notification_tools.display_notification(text + "Click to continue.", 'exploration', self.global_manager)
            
        text += "/n"
        if roll_result >= self.current_min_success: #4+ required on D6 for exploration by default
            if not future_cell.resource == 'none':
                text += "You discovered a " + future_cell.terrain.upper() + " tile with a " + future_cell.resource.upper() + " resource. /n"
            else:
                text += "You discovered a " + future_cell.terrain.upper() + " tile. /n"
        else:
            text += "You were not able to explore the tile. /n"
        if roll_result <= self.current_max_crit_fail:
            text += "Everyone in the expedition has died. /n" #actual death occurs when exploration completes

        if (not self.veteran) and roll_result == 6:
            self.veteran = True
            self.just_promoted = True
            text += "This explorer is now a veteran. /n"
        if roll_result >= self.current_min_success:
            self.destination_cell = future_cell
            notification_tools.display_notification(text + "Click to remove this notification.", 'final_exploration', self.global_manager)
        else:
            notification_tools.display_notification(text, 'default', self.global_manager)
        self.global_manager.set('exploration_result', [self, roll_result, x_change, y_change])

    def complete_exploration(self): #roll_result, x_change, y_change
        '''
        Description:
            Used when the player finishes rolling for an exploration, showing the exploration's results and making any changes caused by the result. If successful, the expedition moves into the explored area, consumes its movement
                points, promotes its explorer to a veteran on critical success. If not successful, the expedition consumes its movement points and dies on critical failure
        Input:
            None
        Output:
            None
        '''
        exploration_result = self.global_manager.get('exploration_result')
        roll_result = exploration_result[1]
        x_change = exploration_result[2]
        y_change = exploration_result[3]
        future_cell = self.grid.find_cell(x_change + self.x, y_change + self.y)
        died = False
        if roll_result >= self.current_min_success:
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
        elif roll_result == self.current_max_crit_fail:
            self.die()
            died = True
        copy_dice_list = self.global_manager.get('dice_list')
        for current_die in copy_dice_list:
            current_die.remove()
        actor_utility.stop_exploration(self.global_manager) #make function that sets ongoing exploration to false and destroys exploration marks

def create_group(worker, officer, global_manager):
    '''
    Description:
        Creates a group out of the inputted worker and officer. The type of group formed depends on the officer's type. Upon joining a group, the component officer and worker will not be able to be seen or interacted with
            independently until the group is disbanded
    Input:
        worker worker: worker to create a group out of
        officer officer: officer to create a group out of
    Output:
        None
    '''
    if officer.officer_type == 'explorer':
        new_group = expedition((officer.x, officer.y), officer.grids, 'mobs/explorer/expedition.png', 'Expedition', officer.modes, worker, officer, global_manager)
    elif officer.officer_type == 'engineer':
        new_group = construction_gang((officer.x, officer.y), officer.grids, 'mobs/engineer/construction_gang.png', 'Construction gang', officer.modes, worker, officer, global_manager)
    elif officer.officer_type == 'porter foreman':
        new_group = porters((officer.x, officer.y), officer.grids, 'mobs/porter foreman/porters.png', 'Porters', officer.modes, worker, officer, global_manager)
    elif officer.officer_type == 'merchant':
        new_group = caravan((officer.x, officer.y), officer.grids, 'mobs/merchant/caravan.png', 'Caravan', officer.modes, worker, officer, global_manager)
    elif officer.officer_type == 'head missionary':
        new_group = missionaries((officer.x, officer.y), officer.grids, 'mobs/head missionary/missionaries.png', 'Missionaries', officer.modes, worker, officer, global_manager)
    else:
        new_group = group((officer.x, officer.y), officer.grids, 'mobs/default/default.png', 'Expedition', officer.modes, worker, officer, global_manager)
