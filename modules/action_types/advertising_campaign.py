#Contains all functionality for advertising campaigns

import pygame
import random
from . import action
from ..util import action_utility, text_utility, market_utility, scaling, game_transitions

class advertising_campaign(action.campaign):
    '''
    Action for merchant in Europe to increase the price of a particular commodity while lowering a random other
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
        self.global_manager.get('transaction_descriptions')[self.action_type] = 'advertising'
        self.name = 'advertising campaign'
        self.target_commodity = 'none'

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
        return(['Attempts to advertise a chosen commodity and increase its price for ' + str(self.global_manager.get('action_prices')[self.action_type]) + ' money',
                'Can only be done in Europe',
                'If successful, increases the price of a chosen commodity while randomly decreasing the price of another',
                'Costs all remaining movement points, at least 1',
                'Each ' + self.name + ' attempted doubles the cost of other advertising campaigns in the same turn'
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
            text = 'Are you sure you want to start an advertising campaign for ' + self.target_commodity + '? If successful, the price of ' + self.target_commodity + ' will increase, decreasing the price of another random commodity. /n /n'
            text += 'The campaign will cost ' + str(self.global_manager.get('action_prices')[self.action_type]) + ' money. /n /n '
        elif subject == 'initial':
            text += 'The merchant attempts to increase public demand for ' + self.target_commodity + '. /n /n'
            advertising_message, index = self.global_manager.get('flavor_text_manager').generate_substituted_indexed_flavor_text('advertising_campaign', '_', self.target_commodity)
            self.success_audio = [{'sound_id': 'voices/advertising/messages/' + str(index), 'dampen_music': True, 'dampen_time_interval': 0.75},
                                  {'sound_id': 'voices/advertising/commodities/' + self.target_commodity, 'in_sequence': True}]
            text += advertising_message + ' /n /n'
        elif subject in ['success', 'critical_success']:
            increase = 1
            if subject == 'critical_success':
                increase += 1
            advertised_original_price = self.global_manager.get('commodity_prices')[self.target_commodity]
            unadvertised_original_price = self.global_manager.get('commodity_prices')[self.target_unadvertised_commodity]
            unadvertised_final_price = unadvertised_original_price - increase
            if unadvertised_final_price < 1:
                unadvertised_final_price = 1
            text += 'The merchant successfully advertised for ' + self.target_commodity + ', increasing its price from ' + str(advertised_original_price) + ' to '
            text += str(advertised_original_price + increase) + '. The price of ' + self.target_unadvertised_commodity + ' decreased from ' + str(unadvertised_original_price) + ' to ' + str(unadvertised_final_price) + '. /n /n'
            if subject == 'critical_success':
                text += 'The advertising campaign was so popular that the value of ' + self.target_commodity + ' increased by 2 instead of 1. /n /n'
        elif subject == 'failure':
            text += 'The merchant failed to increase the popularity of ' + self.target_unadvertised_commodity + '. /n /n'
        elif subject == 'critical_failure':
            text += self.generate_notification_text('failure')
            text += 'Embarassed by this utter failure, the merchant quits your company. /n /n' 
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
        return_list = super().generate_attached_interface_elements(subject)
        if subject in ['success', 'critical_success']:
            return_list.append(
                action_utility.generate_free_image_input_dict(
                    ['scenery/resources/' + self.target_unadvertised_commodity + '.png',
                     {'image_id': 'scenery/resources/minus.png', 'size': 0.5, 'x_offset': -0.2, 'y_offset': 0.2},
                    ],
                    200,
                    self.global_manager,
                    override_input_dict={'member_config': {'order_x_offset': scaling.scale_width(-75, self.global_manager), 'second_dimension_alignment': 'left'}}
            ))
            return_list.append(
                action_utility.generate_free_image_input_dict(
                    ['scenery/resources/' + self.target_commodity + '.png',
                     {'image_id': 'scenery/resources/plus.png', 'size': 0.5, 'x_offset': -0.2, 'y_offset': 0.2},
                    ],
                    200,
                    self.global_manager,
                    override_input_dict={'member_config': {'order_x_offset': scaling.scale_width(-75, self.global_manager), 'second_dimension_alignment': 'leftmost'}}
            ))
        return(return_list)

    def generate_audio(self, subject):
        '''
        Description:
            Returns list of audio dicts of sounds to play when notification appears, based on the inputted subject and other current circumstances
        Input:
            string subject: Determines sound dicts
        Output:
            dictionary list: Returns list of sound dicts for inputted subject
        '''
        audio = super().generate_audio(subject)
        if subject == 'roll_finished':
            if self.roll_result >= self.current_min_success:
                audio += self.success_audio
        return(audio)

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
               self.global_manager.get('displayed_mob').officer_type == 'merchant'
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
                if not self.global_manager.get('current_game_mode') == 'europe':
                    game_transitions.set_game_mode('europe', self.global_manager)
                    unit.select()
                text_utility.print_to_screen('Select a commodity to advertise, or click elsewhere to cancel: ', self.global_manager)
                self.global_manager.set('choosing_advertised_commodity', True)
            else:
                text_utility.print_to_screen(self.name.capitalize() + 's are only possible in Europe', self.global_manager)

    def start(self, unit, commodity):
        '''
        Description:
            Used when the player clicks on the start PR campaign button, displays a choice notification that allows the player to campaign or not. Choosing to campaign starts the campaign process and consumes the unit's
                movement points
        Input:
            pmob unit: Unit selected when the linked button is clicked
        Output:
            None
        '''
        self.global_manager.set('choosing_advertised_commodity', False)
        self.target_commodity = commodity
        self.target_unadvertised_commodity = random.choice(self.global_manager.get('commodity_types'))
        while self.target_unadvertised_commodity == 'consumer goods' or self.target_unadvertised_commodity == self.target_commodity or self.global_manager.get('commodity_prices')[self.target_unadvertised_commodity] == 1:
            self.target_unadvertised_commodity = random.choice(self.global_manager.get('commodity_types'))

        self.pre_start(unit)

        self.global_manager.get('notification_manager').display_notification({
            'message': action_utility.generate_risk_message(self, unit) + self.generate_notification_text('confirmation'),
            'choices': [
                {
                'on_click': (self.middle, []),
                'tooltip': ['Starts an ' + self.name + ' for ' + self.target_commodity],
                'message': 'Start campaign'
                },
                {
                'on_click': (action_utility.cancel_ongoing_actions, [self.global_manager]),
                'tooltip': ['Stop ' + self.name],
                'message': 'Stop campaign'
                }
            ],
        })

    def complete(self):
        '''
        Description:
            Used when the player finishes rolling for a PR campaign, shows the campaign's results and making any changes caused by the result
        Input:
            None
        Output:
            None
        '''
        if self.roll_result >= self.current_min_success:
            increase = 1
            if self.roll_result >= self.current_min_crit_success:
                increase += 1
            market_utility.change_price(self.target_commodity, increase, self.global_manager)
            market_utility.change_price(self.target_unadvertised_commodity, -1 * increase, self.global_manager)
        elif self.roll_result <= self.current_max_crit_fail:
            self.current_unit.die('quit')
        super().complete()
