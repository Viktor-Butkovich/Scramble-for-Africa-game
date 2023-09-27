#Contains all functionality for public relations campaigns

import pygame
import random
from ..util import action_utility, main_loop_utility, text_utility, dice_utility, actor_utility, scaling

class public_relations_campaign():
    '''
    Action for evangelist in Europe to increase public opinion
    '''
    def __init__(self, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.global_manager = global_manager
        self.action_type = 'public_relations_campaign'
        self.initial_setup()

    def initial_setup(self):
        '''
        Description:
            Completes any configuration required for this action during setup - automatically called during action_setup
        Input:
            None
        Output:
            None
        '''
        self.global_manager.get('action_obj_list').append(self)
        self.current_unit = 'none'
        self.global_manager.get('action_types').append(self.action_type)
        self.global_manager.get('action_prices')[self.action_type] = 5
        self.global_manager.get('base_action_prices')[self.action_type] = 5
        self.global_manager.get('transaction_descriptions')[self.action_type] = 'public relations campaigning'
        self.global_manager.get('transaction_types').append(self.action_type)

    def button_setup(self, initial_input_dict):
        '''
        Description:
            Completes the inputted input_dict with any values required to create a button linked to this action - automatically called during actor display label
                setup
        Input:
            None
        Output:
            None
        '''
        initial_input_dict['init_type'] = 'action button'
        initial_input_dict['corresponding_action'] = self
        initial_input_dict['image_id'] = 'buttons/' + self.action_type + '_button.png'
        initial_input_dict['keybind_id'] = pygame.K_r
        return(initial_input_dict)

    def update_tooltip(self):
        '''
        Description:
            Sets this tooltip of a button linked to this action
        Input:
            None
        Output:
            None
        '''
        return(['Attempts to spread word of your company\'s benevolent goals and righteous deeds in Africa for ' + 
                    str(self.global_manager.get('action_prices')[self.action_type]) + ' money',
                'Can only be done in Europe', 'If successful, increases your company\'s public opinion', 'Costs all remaining movement points, at least 1',
                'Each public relations campaign attempted doubles the cost of other public relations campaigns in the same turn'
        ])

    def can_show(self):
        '''
        Description:
            Returns whether a button linked to this action should be drawn
        Input:
            None
        Output:
            boolean: Returns whether a button linked to this action should be drawn
        '''
        return(self.global_manager.get('displayed_mob').is_officer and self.global_manager.get('displayed_mob').officer_type == 'evangelist')

    def on_click(self, unit):
        '''
        Description:
            Used when the player clicks a linked action button - checks if the unit can do the action, proceeding with 'start' if applicable
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            if self.global_manager.get('europe_grid') in unit.grids:
                if unit.movement_points >= 1:
                    if self.global_manager.get('money') >= self.global_manager.get('action_prices')[self.action_type]:
                        if unit.ministers_appointed():
                            if unit.sentry_mode:
                                unit.set_sentry_mode(False)
                            self.start(unit)
                    else:
                        text_utility.print_to_screen('You do not have the ' + str(self.global_manager.get('action_prices')['religious_campaign']) +
                                                        ' money needed for a public relations campaign.', self.global_manager)
                else:
                    text_utility.print_to_screen('A religious campaign requires all remaining movement points, at least 1.', self.global_manager)
            else:
                text_utility.print_to_screen('Religious campaigns are only possible in Europe', self.global_manager)
        else:
            text_utility.print_to_screen('You are busy and cannot start a religious campaign.', self.global_manager)

    def start(self, unit):
        '''
        Description:
            Used when the player clicks on the start PR campaign button, displays a choice notification that allows the player to campaign or not. Choosing to campaign starts the campaign process and consumes the evangelist's
                movement points
        Input:
            None
        Output:
            None
        '''
        current_roll_modifier = 0
        self.current_min_success = 4 #default_min_success
        self.current_max_crit_fail = 1 #default_max_crit_fail
        self.current_min_crit_success = 6 #default_min_crit_success
        
        self.current_min_success -= current_roll_modifier #positive modifier reduces number required for succcess, reduces maximum that can be crit fail
        self.current_max_crit_fail -= current_roll_modifier
        if self.current_min_success > self.current_min_crit_success:
            self.current_min_crit_success = self.current_min_success #if 6 is a failure, should not be critical success. However, if 6 is a success, it will always be a critical success

        choice_info_dict = {'evangelist': unit, 'type': 'start public relations campaign'}
        self.global_manager.set('ongoing_action', True)
        self.global_manager.set('ongoing_action_type', self.action_type)
        message = 'Are you sure you want to start a public relations campaign? /n /nIf successful, your company\'s public opinion will increase by between 1 and 6 /n /n'
        message += 'The campaign will cost ' + str(self.global_manager.get('action_prices')[self.action_type]) + ' money. /n /n'
        risk_value = -1 * current_roll_modifier #modifier of -1 means risk value of 1
        if unit.veteran: #reduce risk if veteran
            risk_value -= 1

        if risk_value < 0: #0/6 = no risk
            message = 'RISK: LOW /n /n' + message  
        elif risk_value == 0: #1/6 death = moderate risk
            message = 'RISK: MODERATE /n /n' + message #puts risk message at beginning
        elif risk_value == 1: #2/6 = high risk
            message = 'RISK: HIGH /n /n' + message
        elif risk_value > 1: #3/6 or higher = extremely high risk
            message = 'RISK: DEADLY /n /n' + message
        self.current_unit = unit
        self.global_manager.get('notification_manager').display_notification({
            'message': message,
            'choices': [
                {
                'on_click': (self.middle, []),
                'tooltip': ['Starts a public relations campaign, possibly improving your company\'s public opinion'],
                'message': 'Start campaign'
                },
                {
                'on_click': (action_utility.cancel_ongoing_actions, [self.global_manager]),
                'tooltip': ['Stop public relations campaign'],
                'message': 'Stop campaign'
                }
            ],
            'extra_parameters': choice_info_dict
        })

    def middle(self):
        '''
        Description:
            Controls the PR campaign process, determining and displaying its result through a series of notifications
        Input:
            None
        Output:
            None
        '''
        self.global_manager.get('notification_manager').set_lock(True)
        roll_result = 0
        self.current_unit = self.current_unit
        self.current_unit.just_promoted = False
        self.current_unit.set_movement_points(0)

        #generic for campaigns given action type
        price = self.global_manager.get('action_prices')[self.action_type]
        self.global_manager.get('money_tracker').change(self.global_manager.get('action_prices')[self.action_type] * -1, self.action_type)
        actor_utility.double_action_price(self.global_manager, self.action_type)

        roll_lists = []
        if self.current_unit.veteran:
            num_dice = 2
        else:
            num_dice = 1

        results = self.current_unit.controlling_minister.roll_to_list(6, self.current_min_success, self.current_max_crit_fail, price, 'public_relations_campaign', num_dice)
        roll_types = ('Public relations campaign roll', 'second')
        for index in range(len(results)):
            result = results[index]
            roll_type = roll_types[index]
            roll_lists.append(dice_utility.roll_to_list(6, roll_type, self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, result))

        attached_interface_elements = []
        roll_result = 0
        for roll_list in roll_lists:
            attached_interface_elements.append(action_utility.generate_die_input_dict((0, 0), roll_list[0], self, self.global_manager))
            roll_result = max(roll_list[0], roll_result)

        text = ''

        #pre-roll notification
        #specific, action description
        text += 'The evangelist campaigns to increase your company\'s public opinion with word of your company\'s benevolent goals and righteous deeds in Africa. /n /n'
        roll_message = 'Click to roll. ' + str(self.current_min_success) + '+ required '
        officer_name = self.current_unit.name
        #generic given officer name
        if self.current_unit.veteran:
            text += 'The ' + officer_name + ' can roll twice and pick the higher result. /n /n'
            roll_message += 'on at least 1 die to succeed.'
            num_dice = 2
        else:
            roll_message += 'to succeed.'
            num_dice = 1

        #generic given action type
        self.global_manager.get('notification_manager').display_notification({
            'message': text + roll_message,
            'num_dice': num_dice,
            'notification_type': 'action',
            'attached_interface_elements': attached_interface_elements,
            'transfer_interface_elements': True
        }, insert_index=0)

        #generic
        self.global_manager.get('notification_manager').display_notification({
            'message': text + 'Rolling... ',
            'num_dice': num_dice,
            'notification_type': 'roll',
            'transfer_interface_elements': True
        }, insert_index=1)

        self.global_manager.get('notification_manager').set_lock(False) #locks notifications so that corruption messages will occur after the roll notification

        for roll_list in roll_lists:
            text += roll_list[1]
        #generic
        if len(roll_lists) > 1:
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

        if roll_result >= self.current_min_crit_success and (not self.current_unit.veteran): #not self.current_unit.veteran: #(not self.current_unit.veteran) and
            audio = 'trumpet_1'
        else:
            audio = 'none'

        self.global_manager.get('notification_manager').display_notification({
            'message': text + 'Click to continue.',
            'num_dice': num_dice,
            'notification_type': 'action',
            'transfer_interface_elements': True,
            'on_remove': self.complete,
            'audio': audio
        })

        text += '/n'
        public_relations_change = 0
        if roll_result >= self.current_min_success: #4+ required on D6 for exploration
            public_relations_change = random.randrange(1, 7)
            text += 'Met with gullible and enthusiastic audiences, the evangelist successfully improves your company\'s public opinion by ' + str(public_relations_change) + '. /n /n'
        else:
            text += 'Whether by a lack of charisma, a reluctant audience, or a doomed cause, the evangelist fails to improve your company\'s public opinion. /n /n'
        if roll_result <= self.current_max_crit_fail:
            text += 'The evangelist is deeply embarassed by this public failure and decides to abandon your company. /n /n' #actual 'death' occurs when religious campaign completes

        if (not self.current_unit.veteran) and roll_result >= self.current_min_crit_success:
            self.current_unit.just_promoted = True
            text += 'With fiery word and true belief in his cause, the evangelist becomes a veteran and will be more successful in future ventures. /n /n'

        self.global_manager.get('notification_manager').display_notification({
            'message': text + 'Click to remove this notification.',
            'notification_type': 'action',
        })
        self.result = (roll_result, public_relations_change)

    def complete(self):
        '''
        Description:
            Used when the player finishes rolling for a PR campaign, shows the campaign's results and making any changes caused by the result. If successful, increases public opinion by random amount, promotes evangelist to a veteran on
                critical success. Evangelist dies on critical failure
        Input:
            None
        Output:
            None
        '''
        roll_result, public_relations_change = self.result
        if roll_result >= self.current_min_success: #if campaign succeeded
            #non-generic campaign effect
            self.global_manager.get('public_opinion_tracker').change(public_relations_change)

            #generic effect
            if roll_result >= self.current_min_crit_success and not self.current_unit.veteran:
                self.current_unit.promote()
            self.current_unit.select()

        elif roll_result <= self.current_max_crit_fail:
            #non-generic campaign effect
            self.current_unit.die('quit')
        action_utility.cancel_ongoing_actions(self.global_manager)
