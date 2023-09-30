#Contains functionality for evangelist officers

import random
from ..officers import officer
from ....util import actor_utility, scaling

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
                'image': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
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
        
        minister_position_icon = self.global_manager.get('actor_creation_manager').create_interface_element({
            'coordinates': minister_icon_coordinates,
            'width': scaling.scale_width(100, self.global_manager),
            'height': scaling.scale_height(100, self.global_manager),
            'modes': self.modes,
            'attached_minister': self.controlling_minister,
            'minister_image_type': 'position',
            'init_type': 'dice roll minister image'
        }, self.global_manager)

        minister_portrait_icon = self.global_manager.get('actor_creation_manager').create_interface_element({
            'coordinates': minister_icon_coordinates,
            'width': scaling.scale_width(100, self.global_manager),
            'height': scaling.scale_height(100, self.global_manager),
            'modes': self.modes,
            'attached_minister': self.controlling_minister,
            'minister_image_type': 'portrait',
            'init_type': 'dice roll minister image'
        }, self.global_manager)
        
        message = 'Are you sure you want to search for a 100 money loan? A loan will always be available, but the merchant\'s success will determine the interest rate found. /n /n'
        message += 'The search will cost ' + str(self.global_manager.get('action_prices')['loan_search']) + ' money. /n /n '

        self.global_manager.get('notification_manager').display_notification({
            'message': message,
            'choices': ['start loan search', 'stop loan search'],
            'extra_parameters': choice_info_dict
        })

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
            self.global_manager.get('notification_manager').display_notification({
                'message': 'The merchant negotiated the loan offer well enough to become a veteran.',
                'num_dice': num_dice
            })
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

        self.global_manager.get('notification_manager').display_notification({
            'message': message,
            'choices': ['accept loan offer', 'decline loan offer'],
            'extra_parameters': choice_info_dict
        })
