#Contains functionality for evangelist officers

import random
from ..officers import officer
from ... import actor_utility
from ... import notification_tools
from ... import dice_utility


class evangelist(officer):
    '''
    Officer that can start religious and public relations campaigns and can merge with church volunteers to form missionaries
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
        input_dict['officer_type'] = 'evangelist'
        super().__init__(from_save, input_dict, global_manager)
        self.current_roll_modifier = 0
        self.default_min_success = 4
        self.default_max_crit_fail = 1
        self.default_min_crit_success = 6

    def start_religious_campaign(self): 
        '''
        Description:
            Used when the player clicks on the start religious campaign button, displays a choice notification that allows the player to campaign or not. Choosing to campaign starts the campaign process and consumes the evangelist's
                movement points
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
        choice_info_dict = {'evangelist': self,'type': 'start religious campaign'}
        self.global_manager.set('ongoing_religious_campaign', True)
        message = 'Are you sure you want to start a religious campaign? /n /nIf successful, a religious campaign will convince church volunteers to join you, allowing the formation of groups of missionaries that can convert native '
        message += 'villages. /n /n The campaign will cost ' + str(self.global_manager.get('action_prices')['religious_campaign']) + ' money. /n /n'
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
            
        notification_tools.display_choice_notification(message, ['start religious campaign', 'stop religious campaign'], choice_info_dict, self.global_manager) #message, choices, choice_info_dict, global_manager

    def religious_campaign(self): #called when start religious campaign clicked in choice notification
        '''
        Description:
            Controls the religious campaign process, determining and displaying its result through a series of notifications
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

        price = self.global_manager.get('action_prices')['religious_campaign']
        self.global_manager.get('money_tracker').change(self.global_manager.get('action_prices')['religious_campaign'] * -1, 'religious_campaign')
        actor_utility.double_action_price(self.global_manager, 'religious_campaign')
        text = ''
        text += 'The evangelist campaigns for the support of church volunteers to join him in converting the African natives. /n /n'
        if not self.veteran:    
            notification_tools.display_notification(text + 'Click to roll. ' + str(self.current_min_success) + '+ required to succeed.', 'religious_campaign', self.global_manager, num_dice)
        else:
            text += ('The veteran evangelist can roll twice and pick the higher result. /n /n')
            notification_tools.display_notification(text + 'Click to roll. ' + str(self.current_min_success) + '+ required on at least 1 die to succeed.', 'religious_campaign', self.global_manager, num_dice)

        notification_tools.display_notification(text + 'Rolling... ', 'roll', self.global_manager, num_dice)

        die_x = self.global_manager.get('notification_manager').notification_x - 140

        if self.veteran:
            results = self.controlling_minister.roll_to_list(6, self.current_min_success, self.current_max_crit_fail, price, 'religious_campaign', 2)
            #result = self.controlling_minister.roll(6, self.current_min_success, self.current_max_crit_fail)
            first_roll_list = dice_utility.roll_to_list(6, 'Religous campaign roll', self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, results[0])
            self.display_die((die_x, 500), first_roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)

            #result = self.controlling_minister.roll(6, self.current_min_success, self.current_max_crit_fail)
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
            result = self.controlling_minister.roll(6, self.current_min_success, self.current_max_crit_fail, price, 'religious_campaign')
            roll_list = dice_utility.roll_to_list(6, 'Religious campaign roll', self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, result)
            self.display_die((die_x, 440), roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)
                
            text += roll_list[1]
            roll_result = roll_list[0]

        notification_tools.display_notification(text + 'Click to continue.', 'religious_campaign', self.global_manager, num_dice)
            
        text += '/n'
        if roll_result >= self.current_min_success: #4+ required on D6 for exploration
            text += 'Inspired by the evangelist\'s message to save the heathens from their own ignorance, a group of church volunteers joins you. /n /n'
        else:
            text += 'Whether by a lack of charisma, a reluctant audience, or a doomed cause, the evangelist fails to gather any volunteers. /n /n'
        if roll_result <= self.current_max_crit_fail:
            text += 'The evangelist is disturbed by the lack of faith of your country\'s people and decides to abandon your company. /n /n' #actual 'death' occurs when religious campaign completes

        if (not self.veteran) and roll_result >= self.current_min_crit_success:
            self.just_promoted = True
            text += 'With fiery word and true belief in his cause, the evangelist becomes a veteran and will be more successful in future ventures. /n /n'
        if roll_result >= 4:
            success = True
            notification_tools.display_notification(text + 'Click to remove this notification.', 'final_religious_campaign', self.global_manager)
        else:
            success = False
            notification_tools.display_notification(text, 'default', self.global_manager)
        self.global_manager.set('religious_campaign_result', [self, roll_result, success])

    def complete_religious_campaign(self):
        '''
        Description:
            Used when the player finishes rolling for a religious campaign, shows the campaign's results and making any changes caused by the result. If successful, recruits church volunteers, promotes evangelist to a veteran on
                critical success. If not successful, the evangelist consumes its movement points and dies on critical failure
        Input:
            None
        Output:
            None
        '''
        roll_result = self.global_manager.get('religious_campaign_result')[1]
        if roll_result >= self.current_min_success: #if campaign succeeded
            input_dict = {}
            input_dict['coordinates'] = (0, 0)
            input_dict['grids'] = [self.global_manager.get('europe_grid')]
            input_dict['image'] = 'mobs/church_volunteers/default.png'
            input_dict['name'] = 'church volunteers'
            input_dict['modes'] = ['strategic', 'europe']
            input_dict['init_type'] = 'church_volunteers'
            input_dict['worker_type'] = 'religious' #not european - doesn't count as a European worker for upkeep
            church_volunteers = self.global_manager.get('actor_creation_manager').create(False, input_dict, self.global_manager)
            if roll_result >= self.current_min_crit_success and not self.veteran:
                self.promote()
            self.global_manager.get('actor_creation_manager').create_group(church_volunteers, self, self.global_manager)
            #for current_image in self.images: #move mob to front of each stack it is in - also used in button.same_tile_icon.on_click(), make this a function of all mobs to move to front of tile
            #    if not current_image.current_cell == 'none':
            #        while not self == current_image.current_cell.contained_mobs[0]:
            #            current_image.current_cell.contained_mobs.append(current_image.current_cell.contained_mobs.pop(0))
        elif roll_result <= self.current_max_crit_fail:
            self.die('quit')
        self.global_manager.set('ongoing_religious_campaign', False)

    def start_public_relations_campaign(self):
        '''
        Description:
            Used when the player clicks on the start PR campaign button, displays a choice notification that allows the player to campaign or not. Choosing to campaign starts the campaign process and consumes the evangelist's
                movement points
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
        choice_info_dict = {'evangelist': self,'type': 'start public relations campaign'}
        self.global_manager.set('ongoing_public_relations_campaign', True)
        message = 'Are you sure you want to start a public relations campaign? /n /nIf successful, your company\'s public opinion will increase by between 1 and 6 /n /n'
        message += 'The campaign will cost ' + str(self.global_manager.get('action_prices')['public_relations_campaign']) + ' money. /n /n'
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
            
        notification_tools.display_choice_notification(message, ['start public relations campaign', 'stop public relations campaign'], choice_info_dict, self.global_manager) #message, choices, choice_info_dict, global_manager

    def public_relations_campaign(self):
        '''
        Description:
            Controls the PR campaign process, determining and displaying its result through a series of notifications
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

        price = self.global_manager.get('action_prices')['public_relations_campaign']
        self.global_manager.get('money_tracker').change(self.global_manager.get('action_prices')['public_relations_campaign'] * -1, 'public_relations_campaign')
        actor_utility.double_action_price(self.global_manager, 'public_relations_campaign')
        text = ''
        text += 'The evangelist campaigns to increase your company\'s public opinion with word of your company\'s benevolent goals and righteous deeds in Africa. /n /n'
        if not self.veteran:    
            notification_tools.display_notification(text + 'Click to roll. ' + str(self.current_min_success) + '+ required to succeed.', 'public_relations_campaign', self.global_manager, num_dice)
        else:
            text += ('The veteran evangelist can roll twice and pick the higher result. /n /n')
            notification_tools.display_notification(text + 'Click to roll. ' + str(self.current_min_success) + '+ required on at least 1 die to succeed.', 'public_relations_campaign', self.global_manager, num_dice)

        notification_tools.display_notification(text + 'Rolling... ', 'roll', self.global_manager, num_dice)

        die_x = self.global_manager.get('notification_manager').notification_x - 140

        if self.veteran:
            results = self.controlling_minister.roll_to_list(6, self.current_min_success, self.current_max_crit_fail, price, 'public relations campaign', 2)
            first_roll_list = dice_utility.roll_to_list(6, 'Public relations campaign roll', self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, results[0])
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
            result = self.controlling_minister.roll(6, self.current_min_success, self.current_max_crit_fail, price, 'public relations campaign')
            roll_list = dice_utility.roll_to_list(6, 'Public relations campaign roll', self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, result)
            self.display_die((die_x, 440), roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)
                
            text += roll_list[1]
            roll_result = roll_list[0]

        notification_tools.display_notification(text + 'Click to continue.', 'public_relations_campaign', self.global_manager, num_dice)
            
        text += '/n'
        public_relations_change = 0
        if roll_result >= self.current_min_success: #4+ required on D6 for exploration
            public_relations_change = random.randrange(1, 7)
            text += 'Met with gullible and enthusiastic audiences, the evangelist successfully improves your company\'s public opinion by ' + str(public_relations_change) + '. /n /n'
        else:
            text += 'Whether by a lack of charisma, a reluctant audience, or a doomed cause, the evangelist fails to improve your company\'s public opinion. /n /n'
        if roll_result <= self.current_max_crit_fail:
            text += 'The evangelist is deeply embarassed by this public failure and decides to abandon your company. /n /n' #actual 'death' occurs when religious campaign completes

        if (not self.veteran) and roll_result >= self.current_min_crit_success:
            self.just_promoted = True
            text += 'With fiery word and true belief in his cause, the evangelist becomes a veteran and will be more successful in future ventures. /n /n'
        if roll_result >= 4:
            notification_tools.display_notification(text + 'Click to remove this notification.', 'final_public_relations_campaign', self.global_manager)
        else:
            notification_tools.display_notification(text, 'default', self.global_manager)
        self.global_manager.set('public_relations_campaign_result', [self, roll_result, public_relations_change])

    def complete_public_relations_campaign(self):
        '''
        Description:
            Used when the player finishes rolling for a PR campaign, shows the campaign's results and making any changes caused by the result. If successful, increases public opinion by random amount, promotes evangelist to a veteran on
                critical success. Evangelist dies on critical failure
        Input:
            None
        Output:
            None
        '''
        roll_result = self.global_manager.get('public_relations_campaign_result')[1]
        if roll_result >= self.current_min_success: #if campaign succeeded
            self.global_manager.get('public_opinion_tracker').change(self.global_manager.get('public_relations_campaign_result')[2])
            if roll_result >= self.current_min_crit_success and not self.veteran:
                self.promote()
            self.select()
        elif roll_result <= self.current_max_crit_fail:
            self.die('quit')
        self.global_manager.set('ongoing_public_relations_campaign', False)
