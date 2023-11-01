#Contains all functionality for minister investigations

import random
from . import action
from ..util import action_utility
import modules.constants.constants as constants
import modules.constants.status as status

class active_investigation(action.campaign):
    '''
    Action for merchant in Europe to search for a loan offer
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
        constants.transaction_descriptions[self.action_type] = 'investigations'
        self.name = 'active investigation'
        self.actor_type = 'minister'

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
        initial_input_dict['modes'] = ['ministers']
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
        if status.displayed_minister:
            return(['Orders your Prosecutor to conduct an active investigation against ' + status.displayed_minister.name + ' for ' + str(self.get_price()) + ' money',
                    'If successful, information may be uncovered regarding this minister\'s loyalty, skills, or past crimes',
                    'Each ' + self.name + ' attempted doubles the cost of other active investigations in the same turn'
            ])
        else:
            return([])

    def generate_notification_text(self, subject):
        '''
        Description:
            Returns text regarding a particular subject for this action
        Input:
            string subject: Determines type of text to return
        Output:
            string: Returns text for the inputted subject
        '''
        text = super().generate_notification_text(subject)
        if subject == 'confirmation':
            text += 'Are you sure you want to conduct an active investigation against ' + status.displayed_minister.name
            if status.displayed_minister.current_position != 'none':
                text += ', your ' + status.displayed_minister.current_position
            text += '? /n /n'
            text += 'This may uncover information regarding ' + status.displayed_minister.name + '\'s loyalty, skills, or past crimes. /n /n'
            text += 'The investigation will cost ' + str(self.get_price()) + ' money. /n /n '
        return(text)

    def generate_attached_interface_elements(self, subject):
        '''
        Description:
            Returns list of input dicts of interface elements to attach to a notification regarding a particular subject for this action
        Input:
            string subject: Determines input dicts
        Output:
            dictionary list: Returns list of input dicts for inputted subject
        '''
        if subject == 'dice':
            return_list = self.current_unit.generate_icon_input_dicts(alignment='left')
        return(return_list)

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
               status.displayed_minister.current_position != 'Prosecutor'
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
            self.start(unit)

    def start(self, unit):
        '''
        Description:
            Used when the player clicks on the start action button, displays a choice notification that allows the player to start or not
        Input:
            pmob unit: Unit selected when the linked button is clicked
        Output:
            None
        '''
        if super().start(unit):
            constants.notification_manager.display_notification({
                'message': self.generate_notification_text('confirmation'),
                'transfer_interface_elements': True,
                'choices': [
                    {
                    'on_click': (self.middle, []),
                    'tooltip': ['Starts an active investigation'],
                    'message': 'Start investigation'
                    },
                    {
                    'on_click': (action_utility.cancel_ongoing_actions, []),
                    'tooltip': ['Do nothing'],
                    'message': 'Do nothing'
                    }
                ],
            })

    def middle(self):
        '''
        Description:
            Controls the campaign process, determining and displaying its result through a series of notifications
        Input:
            None
        Output:
            None
        '''
        prosecutor = status.current_ministers['Prosecutor']
        previous_values = {}
        new_values = {}
        roll_result = prosecutor.roll(6, 4, 0, self.process_payment(), self.action_type)
        if roll_result >= 4:
            for category in constants.minister_types + ['loyalty']:
                if category == 'loyalty' or category == self.current_unit.current_position: #simplify this
                    if random.randrange(1, 7) >= 4:
                        if category == 'loyalty':
                            previous_values[category] = self.current_unit.apparent_corruption_description
                        else:
                            previous_values[category] = self.current_unit.apparent_skill_descriptions[category]
                        self.current_unit.attempt_rumor(category, prosecutor)
                        if category == 'loyalty':
                            if self.current_unit.apparent_corruption_description != previous_values[category]:
                                new_values[category] = self.current_unit.apparent_corruption_description
                        else:
                            if self.current_unit.apparent_skill_descriptions[category] != previous_values[category]:
                                new_values[category] = self.current_unit.apparent_skill_descriptions[category]
                else:
                    if random.randrange(1, 7) == 1:
                        if category == 'loyalty':
                            previous_values[category] = self.current_unit.apparent_corruption_description
                        else:
                            previous_values[category] = self.current_unit.apparent_skill_descriptions[category]
                        self.current_unit.attempt_rumor(category, prosecutor)
                        if category == 'loyalty':
                            if self.current_unit.apparent_corruption_description != previous_values[category]:
                                new_values[category] = self.current_unit.apparent_corruption_description
                        else:
                            if self.current_unit.apparent_skill_descriptions[category] != previous_values[category]:
                                new_values[category] = self.current_unit.apparent_skill_descriptions[category]

        message = ''
        if new_values:
            message = 'The investigation resulted in the following discoveries: /n /n'
            for category in new_values:
                if category == 'loyalty':
                    category_name = category
                else:
                    category_name = constants.minister_type_dict[category]
                message += '    ' + category_name.capitalize() + ': ' + new_values[category]
                if previous_values[category] == 'unknown': #if unknown
                    message += ' /n'
                else:
                    message += ' (formerly ' + previous_values[category] + ') /n'

        else:
            message = 'The investigation failed to make any significant discoveries. /n'
        message += ' /n'
        constants.notification_manager.display_notification({
            'message': message,
        })
        self.complete()
