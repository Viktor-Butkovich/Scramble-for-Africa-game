#Contains all functionality for public relations campaigns

import pygame
from ..util import action_utility, main_loop_utility, text_utility

def execute(phase, *args):
    '''
    Description:
        Orders the action function corresponding to the inputted phase to be called with the inputted unit and global manager as inputs
            - for example, execute('start', unit1, global_manager) would call start(unit1, global_manager)
    Input:
        string phase: Start of the function name to call, like 'start' to call start_public_relations_campaign
        pmob unit: Unit controlling the action being done
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        Relays whatever the corresponding action function returned
    '''
    return(globals()[phase](*args))

def initial_setup(global_manager):
    '''
    Description:
        Completes any configuration required for this action during setup - automatically called during action_setup
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    global_manager.get('action_types').append('public_relations_campaign')
    global_manager.get('action_prices')['public_relations_campaign'] = 5
    global_manager.get('base_action_prices')['public_relations_campaign'] = 5
    global_manager.get('transaction_descriptions')['public_relations_campaign'] = 'public relations campaigning'

def button_setup(initial_input_dict, global_manager):
    '''
    Description:
        Completes the inputted input_dict with any values required to create a button linked to this action - automatically called during actor display label
            setup
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    initial_input_dict['init_type'] = 'action button'
    initial_input_dict['corresponding_action'] = execute
    initial_input_dict['image_id'] = 'buttons/public_relations_campaign_button.png'
    initial_input_dict['keybind_id'] = pygame.K_r
    return(initial_input_dict)

def update_tooltip(global_manager):
    '''
    Description:
        Sets this tooltip of a button linked to this action
    Input:
        None
    Output:
        None
    '''
    return(['Attempts to spread word of your company\'s benevolent goals and righteous deeds in Africa for ' + 
                str(global_manager.get('action_prices')['public_relations_campaign']) + ' money',
            'Can only be done in Europe', 'If successful, increases your company\'s public opinion', 'Costs all remaining movement points, at least 1',
            'Each public relations campaign attempted doubles the cost of other public relations campaigns in the same turn'
    ])

def can_show(global_manager):
    '''
    Description:
        Returns whether a button linked to this action should be drawn
    Input:
        None
    Output:
        boolean: Returns whether a button linked to this action should be drawn
    '''
    return(global_manager.get('displayed_mob').is_officer and global_manager.get('displayed_mob').officer_type == 'evangelist')

def on_click(unit, global_manager):
    '''
    Description:
        Used when the player clicks a linked action button - checks if the unit can do the action, proceeding with 'start' if applicable
    Input:
        None
    Output:
        None
    '''
    if main_loop_utility.action_possible(global_manager):
        if global_manager.get('europe_grid') in unit.grids:
            if unit.movement_points >= 1:
                if global_manager.get('money') >= global_manager.get('action_prices')['public_relations_campaign']:
                    if unit.ministers_appointed():
                        if unit.sentry_mode:
                            unit.set_sentry_mode(False)
                        execute('start', unit, global_manager)
                else:
                    text_utility.print_to_screen('You do not have the ' + str(global_manager.get('action_prices')['religious_campaign']) +
                                                    ' money needed for a public relations campaign.', global_manager)
            else:
                text_utility.print_to_screen('A religious campaign requires all remaining movement points, at least 1.', global_manager)
        else:
            text_utility.print_to_screen('Religious campaigns are only possible in Europe', global_manager)
    else:
        text_utility.print_to_screen('You are busy and cannot start a religious campaign.', global_manager)

def start(unit, global_manager):
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
    current_min_success = 4 #default_min_success
    current_max_crit_fail = 1 #default_max_crit_fail
    current_min_crit_success = 6 #default_min_crit_success
    
    current_min_success -= current_roll_modifier #positive modifier reduces number required for succcess, reduces maximum that can be crit fail
    current_max_crit_fail -= current_roll_modifier
    if current_min_success > current_min_crit_success:
        current_min_crit_success = current_min_success #if 6 is a failure, should not be critical success. However, if 6 is a success, it will always be a critical success

    choice_info_dict = {'evangelist': unit, 'type': 'start public relations campaign'}
    global_manager.set('ongoing_action', True)
    global_manager.set('ongoing_action_type', 'public_relations_campaign')
    message = 'Are you sure you want to start a public relations campaign? /n /nIf successful, your company\'s public opinion will increase by between 1 and 6 /n /n'
    message += 'The campaign will cost ' + str(global_manager.get('action_prices')['public_relations_campaign']) + ' money. /n /n'
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

    global_manager.get('notification_manager').display_notification({
        'message': message,
        'choices': [
            {
            'on_click': (execute, ['middle', unit, global_manager]),
            'tooltip': ['Starts a public relations campaign, possibly improving your company\'s public opinion'],
            'message': 'Start campaign'
            },
            {
            'on_click': (action_utility.cancel_ongoing_actions, [global_manager]),
            'tooltip': ['Stop public relations campaign'],
            'message': 'Stop campaign'
            }
        ],
        'extra_parameters': choice_info_dict
    })

def middle(unit, global_manager):
    '''
    Description:
        Controls the PR campaign process, determining and displaying its result through a series of notifications
    Input:
        None
    Output:
        None
    '''
    #Implementation in progress - currently correctly called when start campaign button is clicked
    action_utility.cancel_ongoing_actions(global_manager)
    return
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
        self.global_manager.get('notification_manager').display_notification({
            'message': text + 'Click to roll. ' + str(self.current_min_success) + '+ required to succeed.',
            'num_dice': num_dice,
            'notification_type': 'public_relations_campaign'
        })
    else:
        text += ('The veteran evangelist can roll twice and pick the higher result. /n /n')
        self.global_manager.get('notification_manager').display_notification({
            'message': text + 'Click to roll. ' + str(self.current_min_success) + '+ required on at least 1 die to succeed.',
            'num_dice': num_dice,
            'notification_type': 'public_relations_campaign'
        })

    self.global_manager.get('notification_manager').display_notification({
        'message': text + 'Rolling... ',
        'num_dice': num_dice,
        'notification_type': 'roll'
    })

    die_x = self.global_manager.get('notification_manager').notification_x - 140

    if self.veteran:
        results = self.controlling_minister.roll_to_list(6, self.current_min_success, self.current_max_crit_fail, price, 'public_relations_campaign', 2)
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
        result = self.controlling_minister.roll(6, self.current_min_success, self.current_max_crit_fail, price, 'public_relations_campaign')
        roll_list = dice_utility.roll_to_list(6, 'Public relations campaign roll', self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail, self.global_manager, result)
        self.display_die((die_x, 440), roll_list[0], self.current_min_success, self.current_min_crit_success, self.current_max_crit_fail)
            
        text += roll_list[1]
        roll_result = roll_list[0]

    self.global_manager.get('notification_manager').display_notification({
        'message': text + 'Click to continue.',
        'num_dice': num_dice,
        'notification_type': 'public_relations_campaign'
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

    if (not self.veteran) and roll_result >= self.current_min_crit_success:
        self.just_promoted = True
        text += 'With fiery word and true belief in his cause, the evangelist becomes a veteran and will be more successful in future ventures. /n /n'
    if roll_result >= 4:
        self.global_manager.get('notification_manager').display_notification({
            'message': text + 'Click to remove this notification.',
            'notification_type': 'final_public_relations_campaign'
        })
    else:
        self.global_manager.get('notification_manager').display_notification({
            'message': text,
        })
    self.global_manager.set('public_relations_campaign_result', [self, roll_result, public_relations_change])
    '''

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
    self.global_manager.set('ongoing_action', False)
    self.global_manager.set('ongoing_action_type', 'none')
