#Contains functionality for caravans

import random
import math
from ..groups import group
from ....util import utility, actor_utility, dice_utility, market_utility
import modules.constants.constants as constants
import modules.constants.status as status
import modules.constants.flags as flags

class caravan(group):
    '''
    A group with a merchant officer that is able to establish trading posts and trade with native villages
    '''
    def __init__(self, from_save, input_dict):
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
                'end_turn_destination_grid_type': string value - Required if end_turn_destination is not 'none', matches the status key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - Required if from save, how many movement points this actor currently has
                'max_movement_points': int value - Required if from save, maximum number of movement points this mob can have
                'worker': worker or dictionary value - If creating a new group, equals a worker that is part of this group. If loading, equals a dictionary of the saved information necessary to recreate the worker
                'officer': worker or dictionary value - If creating a new group, equals an officer that is part of this group. If loading, equals a dictionary of the saved information necessary to recreate the officer
        Output:
            None
        '''
        super().__init__(from_save, input_dict)
        self.can_hold_commodities = True
        self.can_trade = True
        self.inventory_capacity = 9
        self.trades_remaining = 0
        if not from_save:
            self.inventory_setup()
            actor_utility.calibrate_actor_info_display(status.mob_info_display, self) #updates mob info display list to account for inventory capacity changing
        else:
            self.load_inventory(input_dict['inventory'])
        self.set_group_type('caravan')

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
        village = self.images[0].current_cell.get_building('village')
        choice_info_dict = {'caravan': self, 'village': village, 'type': 'start trading'}
        flags.ongoing_action = True
        status.ongoing_action_type = 'trade'
        message = 'Are you sure you want to attempt to trade with the village of ' + village.name + '? /n /n'

        self.current_roll_modifier = 0
        self.current_min_success = self.default_min_success
        self.current_max_crit_fail = self.default_max_crit_fail
        self.current_min_crit_success = self.default_min_crit_success

        if not village.cell.has_intact_building('trading_post'): #penalty for no trading post
            self.current_roll_modifier -= 1
            message += 'Without an established trading post, the merchant will have difficulty convincing villagers to trade. /n /n'
        
        aggressiveness_modifier = village.get_aggressiveness_modifier()
        if aggressiveness_modifier < 0:
            message += 'The villagers are hostile and are unlikely to be willing to trade. /n /n'
        elif aggressiveness_modifier > 0:
            message += 'The villagers are friendly and are likely to be willing to trade. /n /n'
        else:
            message += 'The villagers are wary of the merchant but may be willing to trade. /n /n'
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
        message += 'In each trade, the merchant trades 1 of his ' + str(self.get_inventory('consumer goods')) + ' consumer goods for items that may or may not be valuable. /n /n'
        message += 'Trading may also convince villagers to become available for hire as workers. '

        constants.notification_manager.display_notification({
            'message': message,
            'choices': ['start trading', 'stop trading'],
            'extra_parameters': choice_info_dict
        })

    def willing_to_trade(self, notification):
        '''
        Description:
            Used when the player decides to start trading, allows the player to roll a die to see if the villagers are willing to trade. If they are willing to trade, displays a choice notification that allows the player to start the
                transaction process or not. Otherwise, stops the trading process. Native warriors spawn on critical failure
        Input:
            notification notification: the current trade notification, used to access information relating to the trade such as which village is being traded with
        Output:
            None
        '''
        self.notification = notification
        self.set_movement_points(0)

        if self.veteran: #tells notifications how many of the currently selected mob's dice to show while rolling
            num_dice = 2
        else:
            num_dice = 1
        
        village = self.notification.choice_info_dict['village']
        text = ('The merchant attempts to convince the villagers to trade. /n /n')
        if self.veteran:
            text += ('The veteran merchant can roll twice and pick the higher result. /n /n')
            constants.notification_manager.display_notification({
                'message': text + 'Click to roll. ' + str(self.current_min_success) + '+ required on at least 1 die to succeed.',
                'num_dice': num_dice,
                'notification_type': 'trade'
            })
        else:
            constants.notification_manager.display_notification({
                'message': text + 'Click to roll. ' + str(self.current_min_success) + '+ required to succeed.',
                'num_dice': num_dice,
                'notification_type': 'trade'
            })
        constants.notification_manager.display_notification({
            'message': text + 'Rolling... ',
            'num_dice': num_dice,
            'notification_type': 'roll'
        })

        die_x = constants.notification_manager.notification_x - 140

        roll_result = 0
        if self.veteran:
            #results = self.controlling_minister.roll_to_list(6, self.current_min_success, self.current_max_crit_fail, 2)
            results = [self.controlling_minister.no_corruption_roll(6), self.controlling_minister.no_corruption_roll(6)]
            
            #result = self.controlling_minister.roll(6, self.current_min_success, self.current_max_crit_fail)
            first_roll_list = dice_utility.roll_to_list(6, 'Trade roll', self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, results[0]) #0 requirement for critical fail means critical fails will not occur
            self.display_die((die_x, 500), first_roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)

            #result = self.controlling_minister.roll(6, self.current_min_success, self.current_max_crit_fail)         
            second_roll_list = dice_utility.roll_to_list(6, 'second', self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, results[1]) #0 requirement for critical fail means critical fails will not occur
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
            #result = self.controlling_minister.roll(6, self.current_min_success, self.current_max_crit_fail)
            result = self.controlling_minister.no_corruption_roll(6)
            roll_list = dice_utility.roll_to_list(6, 'Trade roll', self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, result) #0 requirement for critical fail means critical fails will not occur
            self.display_die((die_x, 440), roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)
                            
            text += roll_list[1]
            roll_result = roll_list[0]

        #trade_result = [self, roll_result]
        constants.notification_manager.display_notification({
            'message': text + 'Click to continue.',
            'num_dice': num_dice,
            'notification_type': 'final_trade'
        })

        if roll_result >= self.current_min_success:
            self.trades_remaining = math.ceil(village.population / 3)
            trade_type = 'trade'
            if (not self.veteran) and roll_result >= self.current_min_crit_success: #promotion occurs when trade_promotion notification appears, in notification_to_front in notification_manager
                text += '/nThe merchant negotiated well enough to become a veteran. /n'
                trade_type = 'trade_promotion'

            constants.notification_manager.display_notification({
                'message': text + '/nThe villagers are willing to trade ' + str(self.trades_remaining) + ' time' + utility.generate_plural(self.trades_remaining) + ' with this caravan. /n /nThe merchant has ' + str(self.get_inventory('consumer goods')) +
                ' consumer goods to sell. /n /nClick to start trading. /n /n',
                'notification_type': trade_type
            })

            choice_info_dict = {'caravan': self, 'village': village, 'type': 'willing to trade'}
            text += '/nThe villagers are willing to trade ' + str(self.trades_remaining) + ' time' + utility.generate_plural(self.trades_remaining) + ' with this caravan. /n /n'
            text += 'The merchant has ' + str(self.get_inventory('consumer goods')) + ' consumer goods to sell. /n /n'
            text += 'Do you want to start trading consumer goods for items that may or may not be valuable?'

            constants.notification_manager.display_notification({
                'message': text,
                'choices': ['trade', 'stop trading'],
                'extra_parameters': choice_info_dict
            })

        else:
            text += '/nThe villagers are not willing to trade with this caravan. /n'
            if roll_result <= self.current_max_crit_fail:
                text += ' /nBelieving that the merchant seeks to trick them out of their valuables, the villagers attack the caravan. /n /n'
                constants.notification_manager.display_notification({
                    'message': text + ' /nClick to close this notification. ',
                    'notification_type': 'stop_trade_attacked'
                })
            else:
                constants.notification_manager.display_notification({
                    'message': text + ' /nClick to close this notification. ',
                    'notification_type': 'stop_trade'
                })

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

        if self.veteran: #tells notifications how many of the currently selected mob's dice to show while rolling
            num_dice = 2
        else:
            num_dice = 1
        
        self.current_roll_modifier = 0 #trading - getting good deals - is different from the willingness to trade roll and uses different modifiers
        self.current_min_success = 4
        self.current_max_crit_fail = 0 #0 requirement for critical fail means critical fails will not occur
        self.current_min_crit_success = 7 #no critical successes
        
        self.current_min_success -= self.current_roll_modifier #positive modifier reduces number required for succcess, reduces maximum that can be crit fail
        self.current_max_crit_fail -= self.current_roll_modifier
        if self.current_min_success > self.current_min_crit_success:
            self.current_min_crit_success = self.current_min_success #if 6 is a failure, should not be critical success. However, if 6 is a success, it will always be a critical success
        
        self.notification = notification
        village = self.notification.choice_info_dict['village']
        text = ('The merchant attempts to find valuable commodities in return for consumer goods. /n /n')
        if self.veteran:
            text += ('The veteran merchant can roll twice and pick the higher result. /n /n')
            constants.notification_manager.display_notification({
                'message': text + 'Click to roll. ' + str(self.current_min_success) + '+ required on at least 1 die to succeed.',
                'num_dice': num_dice,
                'notification_type': 'trade'
            })
        else:
            constants.notification_manager.display_notification({
                'message': text + 'Click to roll. ' + str(self.current_min_success) + '+ required to succeed.',
                'num_dice': num_dice,
                'notification_type': 'trade'
            })

        constants.notification_manager.display_notification({
            'message': text + 'Rolling... ',
            'num_dice': num_dice,
            'notification_type': 'roll'
        })

        die_x = constants.notification_manager.notification_x - 140

        roll_result = 0
        if self.veteran:
            results = self.controlling_minister.roll_to_list(6, self.current_min_success, self.current_max_crit_fail, constants.commodity_prices['consumer goods'], 'trade', 2)
            first_roll_list = dice_utility.roll_to_list(6, 'Trade roll', self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, results[0])
            self.display_die((die_x, 500), first_roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)
    
            second_roll_list = dice_utility.roll_to_list(6, 'second', self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, results[1]) #7 requirement for crit success - can't promote from trade deal, only willingness to trade roll
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
            result = self.controlling_minister.roll(6, self.current_min_success, self.current_max_crit_fail, constants.commodity_prices['consumer goods'], 'trade')
            roll_list = dice_utility.roll_to_list(6, 'Trade roll', self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, result) #0 requirement for critical fail means critical fails will not occur
            self.display_die((die_x, 440), roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)
                            
            text += roll_list[1]
            roll_result = roll_list[0]

        constants.notification_manager.display_notification({
            'message': text + 'Click to continue.',
            'num_dice': num_dice,
            'notification_type': 'final_trade'
        })
        self.trades_remaining -= 1
        num_consumer_goods = self.get_inventory('consumer goods') - 1 #consumer goods are actually lost when clicking out of notification, so subtract 1 here to show accurate number
        commodity = 'none'
        notification_type = 'none'
        if roll_result >= self.current_min_success:
            commodity = random.choice(constants.collectable_resources)
            text += '/n The merchant managed to buy a unit of ' + commodity + ' (currently worth ' + str(constants.commodity_prices[commodity]) + ' money). /n /n'
            notification_type = 'successful_commodity_trade'
        else:
            text += '/n The merchant bought items that turned out to be worthless. /n /n'
            notification_type = 'failed_commodity_trade'
        gets_worker = False
        if (not village.population == village.available_workers) and random.randrange(1, 7) >= 4: #half chance of getting worker
            text += 'Drawn to the Western lifestyle by consumer goods, some of the villagers are now available to be hired by your company. /n /n'
            gets_worker = True
        if not self.trades_remaining == 0:
            text += 'The villagers are willing to trade ' + str(self.trades_remaining) + ' more time' + utility.generate_plural(self.trades_remaining) + ' with this caravan. /n /n'
            text += 'The merchant has ' + str(num_consumer_goods) + ' more consumer goods to sell /n /n'

        constants.notification_manager.display_notification({
            'message': text,
            'notification_type': 'notification_type'
        })

        text = ''
        if self.trades_remaining > 0 and num_consumer_goods > 0:
            choice_info_dict = {'caravan': self, 'village': village, 'type': 'trade'}
            text += 'The villagers are willing to trade ' + str(self.trades_remaining) + ' more time' + utility.generate_plural(self.trades_remaining) + ' with this caravan. /n /n'
            text += 'Do you want to trade consumer goods for items that may or may not be valuable?'
            constants.notification_manager.display_notification({
                'message': text,
                'choices': ['trade', 'stop trading'],
                'extra_parameters': choice_info_dict
            })
        else:
            if self.trades_remaining == 0:
                text += 'The villagers are not willing to trade any more with this caravan this turn. /n /n'
            if num_consumer_goods <= 0: #consumer goods are actually lost when user clicks out of
                text += 'The merchant does not have any more consumer goods to sell. /n /n'

            constants.notification_manager.display_notification({
                'message': text + 'Click to close this notification. ',
                'notification_type': 'stop_trade'
            })

        #trade_result = self, roll_result, commodity, gets_worker]) #allows notification to give random commodity when clicked

    def complete_trade(self, gives_commodity, trade_result):
        '''
        Description:
            Used when the player finishes rolling for a transaction with a village, shows the transaction's results and makes any changes caused by the result. Consumes one of the caravan's consumer goods and has a chance to convert a
                villager into an available worker. If successful, gives a commodity in return for the consumer goods 
        Input:
            None
        Output:
            None
        '''
        if trade_result[3]: #if gets worker
            self.notification.choice_info_dict['village'].change_available_workers(1)
            market_utility.attempt_worker_upkeep_change('decrease', 'African')
        self.change_inventory('consumer goods', -1)
        if gives_commodity:
            commodity_gained = trade_result[2]
            if not commodity_gained == 'none':
                self.change_inventory(commodity_gained, 1) #caravan gains unit of random commodity
