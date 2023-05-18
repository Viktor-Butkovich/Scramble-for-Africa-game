#Contains functionality for evangelist officers

import random
from ..officers import officer
from ... import actor_utility
from ... import notification_tools
from ... import dice_utility
from ... import market_tools
from ... import scaling
from ... import images

class merchant(officer):
    '''
    Officer that can start advertising campaigns and merge with workers to form a caravan
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
                'end_turn_destination': string or int tuple - Required if from save, 'none' if no saved destination, destination coordinates if saved destination
                'end_turn_destination_grid_type': string - Required if end_turn_destination is not 'none', matches the global manager key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - Required if from save, how many movement points this actor currently has
                'max_movement_points': int value - Required if from save, maximum number of movement points this mob can have
                'veteran': boolean value - Required if from save, whether this officer is a veteran
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['officer_type'] = 'merchant'
        super().__init__(from_save, input_dict, global_manager)
        self.current_roll_modifier = 0
        self.default_min_success = 5
        self.default_max_crit_fail = 1
        self.default_min_crit_success = 6

    def start_loan_search(self):
        '''
        Description:
            Used when the player clicks on the start loan search button, displays a choice notification that asks that allows the player to search or not. Starts the loan search process and consumes the merchant's movement points.
                Also shows a picture of the minister controlling the roll.
        Input:
            None
        Output:
            None
        '''
        self.current_roll_modifier = 0
        self.current_min_success = self.default_min_success
        self.current_max_crit_fail = self.default_max_crit_fail
        self.current_min_crit_success = self.default_min_crit_success
        
        self.current_min_success -= self.current_roll_modifier #positive modifier reduces number required for succcess, reduces maximum that can be crit fail
        self.current_max_crit_fail -= self.current_roll_modifier
        if self.current_min_success > self.current_min_crit_success:
            self.current_min_crit_success = self.current_min_success #if 6 is a failure, should not be critical success. However, if 6 is a success, it will always be a critical success
        choice_info_dict = {'merchant': self, 'type': 'start loan'}
        self.global_manager.set('ongoing_action', True)
        self.global_manager.set('ongoing_action_type', 'loan_search')

        minister_icon_coordinates = (440, self.global_manager.get('notification_manager').notification_x - 140) #show minister in start loan search notification, remove on start/stop loan search
        minister_position_icon = images.dice_roll_minister_image(minister_icon_coordinates, scaling.scale_width(100, self.global_manager), scaling.scale_height(100, self.global_manager), self.modes, self.controlling_minister,
            'position', self.global_manager)
        minister_portrait_icon = images.dice_roll_minister_image(minister_icon_coordinates, scaling.scale_width(100, self.global_manager), scaling.scale_height(100, self.global_manager), self.modes, self.controlling_minister,
            'portrait', self.global_manager)
        
        message = 'Are you sure you want to search for a 100 money loan? A loan will always be available, but the merchant\'s success will determine the interest rate found. /n /n'
        message += 'The search will cost ' + str(self.global_manager.get('action_prices')['loan_search']) + ' money. /n /n '
        notification_tools.display_choice_notification(message, ['start loan search', 'stop loan search'], choice_info_dict, self.global_manager) #message, choices, choice_info_dict, global_manager

    def loan_search(self):
        '''
        Description:
            Controls the process of searching for a loan. Unlike most actions, this action uses hidden dice rolls - starting the search immediately shows the resulting interest cost of the loan found and the controlling minister's
                position and portrait. Allows the player to choose whether to accept the loan after seeing the interest cost.
        Input:
            None
        Output:
            None
        '''
        just_promoted = False
        self.set_movement_points(0)

        num_dice = 0 #don't show dice roll for loan

        self.global_manager.get('money_tracker').change(self.global_manager.get('action_prices')['loan_search'] * -1, 'loan_search')
        actor_utility.double_action_price(self.global_manager, 'loan_search')
        
        principal = 100
        initial_interest = 11
        interest = initial_interest
        found_loan = False
        while not found_loan: #doesn't account for corruption yet, fix this
            if self.veteran: 
                roll = max(random.randrange(1, 7) + self.controlling_minister.get_roll_modifier(), random.randrange(1, 7) + self.controlling_minister.get_roll_modifier())
            else:
                roll = random.randrange(1, 7) + self.controlling_minister.get_roll_modifier()
            if roll >= 5: #increase interest on 1-4, stop on 5-6
                found_loan = True
            else:
                interest += 1
        corrupt = False
        if self.controlling_minister.check_corruption():
            interest += 2 #increase interest by 20% if corrupt
            corrupt = True
            #self.controlling_minister.steal_money(20, 'loan interest') #money stolen once loan actually accepted
            
        if roll == 6 and interest == initial_interest and not self.veteran: #if rolled 6 on first try, promote
            just_promoted = True
                    
        if just_promoted:
            notification_tools.display_notification('The merchant negotiated the loan offer well enough to become a veteran.', 'default', self.global_manager, num_dice)
            self.promote()
            
        choice_info_dict = {}
        choice_info_dict['principal'] = principal
        choice_info_dict['interest'] = interest
        choice_info_dict['corrupt'] = corrupt

        total_paid = interest * 10 #12 interest -> 120 paid
        interest_percent = (interest - 10) * 10 #12 interest -> 20%
        message = ''
        message += 'Loan offer: /n /n'
        message += 'The company will be provided an immediate sum of ' + str(principal) + ' money, which it may spend as it sees fit. /n'
        message += 'In return, the company will be obligated to pay back ' + str(interest) + ' money per turn for 10 turns, for a total of ' + str(total_paid) + ' money. /n /n'
        message += 'Do you accept this exchange? /n'
        notification_tools.display_choice_notification(message, ['accept loan offer', 'decline loan offer'], choice_info_dict, self.global_manager)

    def start_advertising_campaign(self, target_commodity):
        '''
        Description:
            Used when the player clicks on the start advertising campaign button and then clicks a commodity button, displays a choice notification that allows the player to campaign or not. Choosing to campaign starts the campaign
                process and consumes the merchant's movement points
        Input:
            string target_commodity: Name of commodity that advertising campaign is targeting
        Output:
            None
        '''
        self.current_roll_modifier = 0
        self.current_min_success = self.default_min_success
        self.current_max_crit_fail = self.default_max_crit_fail
        self.current_min_crit_success = self.default_min_crit_success
        
        self.current_min_success -= self.current_roll_modifier #positive modifier reduces number required for succcess, reduces maximum that can be crit fail
        self.current_max_crit_fail -= self.current_roll_modifier
        if self.current_min_success > self.current_min_crit_success:
            self.current_min_crit_success = self.current_min_success #if 6 is a failure, should not be critical success. However, if 6 is a success, it will always be a critical success
        choice_info_dict = {'merchant': self, 'type': 'start advertising campaign', 'commodity': target_commodity}
        self.global_manager.set('ongoing_action', True)
        self.global_manager.set('ongoing_action_type', 'advertising_campaign')
        message = 'Are you sure you want to start an advertising campaign for ' + target_commodity + '? If successful, the price of ' + target_commodity + ' will increase, decreasing the price of another random commodity. /n /n'
        message += 'The campaign will cost ' + str(self.global_manager.get('action_prices')['advertising_campaign']) + ' money. /n /n '
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

        self.current_advertised_commodity = target_commodity
        self.current_unadvertised_commodity = random.choice(self.global_manager.get('commodity_types'))
        while (self.current_unadvertised_commodity == 'consumer goods') or (self.current_unadvertised_commodity == self.current_advertised_commodity) or (self.global_manager.get('commodity_prices')[self.current_unadvertised_commodity] == 1):
            self.current_unadvertised_commodity = random.choice(self.global_manager.get('commodity_types'))
        notification_tools.display_choice_notification(message, ['start advertising campaign', 'stop advertising campaign'], choice_info_dict, self.global_manager) #message, choices, choice_info_dict, global_manager

    def advertising_campaign(self): #called when start commodity icon clicked
        '''
        Description:
            Controls the advertising campaign process, determining and displaying its result through a series of notifications
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

        price = self.global_manager.get('action_prices')['advertising_campaign']
        self.global_manager.get('money_tracker').change(self.global_manager.get('action_prices')['advertising_campaign'] * -1, 'advertising_campaign')
        actor_utility.double_action_price(self.global_manager, 'advertising_campaign')
        
        text = ''
        text += 'The merchant attempts to increase public demand for ' + self.current_advertised_commodity + '. /n /n'
        advertising_message, index = self.global_manager.get('flavor_text_manager').generate_substituted_indexed_flavor_text('advertising_campaign', '_', self.current_advertised_commodity)
        self.global_manager.set('current_advertised_commodity', self.current_advertised_commodity)
        self.global_manager.set('current_sound_file_index', index)
        text += advertising_message + ' /n /n'
        if not self.veteran:    
            notification_tools.display_notification(text + 'Click to roll. ' + str(self.current_min_success) + '+ required to succeed.', 'advertising_campaign', self.global_manager, num_dice)
        else:
            text += ('The veteran merchant can roll twice and pick the higher result. /n /n')
            notification_tools.display_notification(text + 'Click to roll. ' + str(self.current_min_success) + '+ required on at least 1 die to succeed.', 'advertising_campaign', self.global_manager, num_dice)

        notification_tools.display_notification(text + 'Rolling... ', 'roll', self.global_manager, num_dice)

        die_x = self.global_manager.get('notification_manager').notification_x - 140

        if self.veteran:
            results = self.controlling_minister.roll_to_list(6, self.current_min_success, self.current_max_crit_fail, price, 'advertising_campaign', 2)
            first_roll_list = dice_utility.roll_to_list(6, 'Advertising campaign roll', self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, results[0])
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
            result = self.controlling_minister.roll(6, self.current_min_success, self.current_max_crit_fail, price, 'advertising_campaign')
            roll_list = dice_utility.roll_to_list(6, 'Advertising campaign roll', self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, result)
            self.display_die((die_x, 440), roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)
                
            text += roll_list[1]
            roll_result = roll_list[0]

        notification_tools.display_notification(text + 'Click to continue.', 'advertising_campaign', self.global_manager, num_dice)
            
        text += '/n'
        if roll_result >= self.current_min_success: #4+ required on D6 for exploration
            increase = 1
            if roll_result >= self.current_min_crit_success:
                increase += 1
            advertised_original_price = self.global_manager.get('commodity_prices')[self.current_advertised_commodity]
            unadvertised_original_price = self.global_manager.get('commodity_prices')[self.current_unadvertised_commodity]
            text += 'The merchant successfully advertised for ' + self.current_advertised_commodity + ', increasing its price from ' + str(advertised_original_price) + ' to '
            unadvertised_final_price = unadvertised_original_price - increase
            if unadvertised_final_price < 1:
                unadvertised_final_price = 1
            text += str(advertised_original_price + increase) + '. The price of ' + self.current_unadvertised_commodity + ' decreased from ' + str(unadvertised_original_price) + ' to ' + str(unadvertised_final_price) + '. /n /n'
        else:
            text += 'The merchant failed to increase the popularity of ' + self.current_advertised_commodity + '. /n /n'
        if roll_result <= self.current_max_crit_fail:
            text += 'Embarassed by this utter failure, the merchant quits your company. /n /n' 

        if roll_result >= self.current_min_crit_success:
            if not self.veteran:
                self.just_promoted = True
            text += 'This merchant is now a veteran. /n /n'
            text += 'The advertising campaign was so popular that the value of ' + self.current_advertised_commodity + ' increased by 2 instead of 1. /n /n'
        if roll_result >= self.current_min_success:
            success = True
            notification_tools.display_notification(text + 'Click to remove this notification.', 'final_advertising_campaign', self.global_manager)
        else:
            success = False
            notification_tools.display_notification(text, 'default', self.global_manager)
        self.global_manager.set('advertising_campaign_result', [self, roll_result, success])

    def complete_advertising_campaign(self):
        '''
        Description:
            Used when the player finishes rolling for an advertising, shows the campaign's results and making any changes caused by the result. If successful, increases target commodity price and decreases other commodity price,
                promotes merchant to veteran and increasing more on critical success. If not successful, the evangelist consumes its movement points and dies on critical failure
        Input:
            None
        Output:
            None
        '''
        roll_result = self.global_manager.get('advertising_campaign_result')[1]
        if roll_result >= self.current_min_success: #if campaign succeeded
            #change prices
            increase = 1
            if roll_result >= self.current_min_crit_success:
                increase += 1
            market_tools.change_price(self.current_advertised_commodity, increase, self.global_manager)
            market_tools.change_price(self.current_unadvertised_commodity, -1 * increase, self.global_manager)
            if roll_result >= self.current_min_crit_success and not self.veteran:
                self.promote()
            self.select()
        elif roll_result <= self.current_max_crit_fail:
            self.die('quit')
        self.global_manager.set('ongoing_action', False)
        self.global_manager.set('ongoing_action_type', 'none')
