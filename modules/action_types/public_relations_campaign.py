#Contains all functionality for public relations campaigns

import pygame
from . import action
from ..util import action_utility, text_utility

class public_relations_campaign(action.action):
    '''
    Action for evangelist in Europe to increase public opinion
    '''
    def initial_setup(self):
        '''
        Description:
            Completes any configuration required for this action during setup - automatically called during action_setup
        Input:
            None
        Output:
            None
        '''
        super().initial_setup()
        self.global_manager.get('transaction_descriptions')[self.action_type] = 'public relations campaigning'
        self.name = 'public relations campaign'

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
        initial_input_dict['keybind_id'] = pygame.K_r
        return(super().button_setup(initial_input_dict))

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

    def generate_notification_text(self, subject):
        '''
        Description:
            Returns text regarding a particular subject for this action
        Input:
            string subject: Determines type of text to return
        Output:
            string: Returns text for the inputted subject
        '''
        text = ''
        if subject == 'confirmation':
            text += 'Are you sure you want to start a public relations campaign? /n /nIf successful, your company\'s public opinion will increase by between 1 and 6 /n /n'
            text += 'The campaign will cost ' + str(self.global_manager.get('action_prices')[self.action_type]) + ' money. /n /n'
        if subject == 'initial':
            text += 'The evangelist campaigns to increase your company\'s public opinion with word of your company\'s benevolent goals and righteous deeds in Africa. /n /n'
        elif subject == 'success':
            text += 'Met with gullible and enthusiastic audiences, the evangelist successfully improves your company\'s public opinion by ' + str(self.public_relations_change) + '. /n /n'
        elif subject == 'failure':
            text += 'Whether by a lack of charisma, a reluctant audience, or a doomed cause, the evangelist fails to improve your company\'s public opinion. /n /n'
        elif subject == 'critical_failure':
            text += 'The evangelist is deeply embarassed by this public failure and decides to abandon your company. /n /n' #actual 'death' occurs when religious campaign completes
        elif subject == 'promotion':
            text += 'With fiery word and true belief in his cause, the evangelist becomes a veteran and will be more successful in future ventures. /n /n'
        return(text)

    def can_show(self):
        '''
        Description:
            Returns whether a button linked to this action should be drawn
        Input:
            None
        Output:
            boolean: Returns whether a button linked to this action should be drawn
        '''
        return(super().can_show() and 
               self.global_manager.get('displayed_mob').is_officer and
               self.global_manager.get('displayed_mob').officer_type == 'evangelist'
        )

    def on_click(self, unit):
        '''
        Description:
            Used when the player clicks a linked action button - checks if the unit can do the action, proceeding with 'start' if applicable
        Input:
            pmob unit: Unit selected when the linked button is clicked
        Output:
            None
        '''
        if super().on_click(unit):
            if self.global_manager.get('europe_grid') in unit.grids:
                self.start(unit)
            else:
                text_utility.print_to_screen(self.name.capitalize() + 's are only possible in Europe', self.global_manager)

    def start(self, unit):
        '''
        Description:
            Used when the player clicks on the start PR campaign button, displays a choice notification that allows the player to campaign or not. Choosing to campaign starts the campaign process and consumes the evangelist's
                movement points
        Input:
            pmob unit: Unit selected when the linked button is clicked
        Output:
            None
        '''
        self.pre_start(unit)
        self.global_manager.get('notification_manager').display_notification({
            'message': action_utility.generate_risk_message(self, unit) + self.generate_notification_text('confirmation'),
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
        })

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
        if self.roll_result >= self.current_min_success:
            self.global_manager.get('public_opinion_tracker').change(self.public_relations_change)
        elif self.roll_result <= self.current_max_crit_fail:
            self.current_unit.die('quit')
        super().complete()
