#Contains functionality for ministers

import random

from . import utility
from . import actor_utility
from . import minister_utility

class minister():
    '''
    Person that can be appointed to control a certain part of the company and will affect actions based on how skilled and corrupt they are
    '''
    def __init__(self, from_save, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'name': string value - Required if from save, this minister's name
                'current_position': string value - Office that this minister is currently occupying, or 'none' if no office occupied
                'general_skill': int value - Value from 1 to 3 that changes what is added to or subtracted from dice rolls
                'specific_skills': dictionary value - String keys corresponding to int values to record skill values for each minister office
                'corruption': int value - Measure of how corrupt a minister is, with 6 having a 1/2 chance to steal, 5 having 1/3 chance, etc.
                'image_id': string value - File path to the image used by this minister
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.actor_type = 'minister' #used for actor display labels and images
        self.global_manager = global_manager
        self.global_manager.get('minister_list').append(self)
        self.tooltip_text = []
        if from_save:
            self.name = input_dict['name']
            self.current_position = input_dict['current_position']
            self.general_skill = input_dict['general_skill']
            self.specific_skills = input_dict['specific_skills']
            self.corruption = input_dict['corruption']
            self.corruption_threshold = 10 - self.corruption
            self.image_id = input_dict['image_id']
            if not self.current_position == 'none':
                self.appoint(self.current_position)
            else:
                self.global_manager.get('available_minister_list').append(self)
                minister_utility.update_available_minister_display(self.global_manager)
        else:
            self.name = self.global_manager.get('flavor_text_manager').generate_minister_name()
            self.skill_setup()
            self.corruption_setup()
            self.current_position = 'none'
            self.global_manager.get('available_minister_list').append(self)
            self.image_id = random.choice(self.global_manager.get('minister_portraits'))
            minister_utility.update_available_minister_display(self.global_manager)
        self.update_tooltip()

    def update_tooltip(self):
        '''
        Description:
            Sets this minister's tooltip to what it should be whenever the player looks at the tooltip. By default, sets tooltip to this minister's name and current office
        Input:
            None
        Output:
            None
        '''
        self.tooltip_text = []
        if not self.current_position == 'none':
            keyword = self.global_manager.get('minister_type_dict')[self.current_position] #type, like military
            self.tooltip_text.append('This is ' + self.name + ', your ' + self.current_position + '.')
        else:
            self.tooltip_text.append('This is ' + self.name + ', a recruitable minister.')

    def to_save_dict(self):
        '''
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
                'name': string value - This minister's name
                'current_position': string value - Office that this minister is currently occupying, or 'none' if no office occupied
                'general_skill': int value - Value from 1 to 3 that changes what is added to or subtracted from dice rolls
                'specific_skills': dictionary value - String keys corresponding to int values to record skill values for each minister office
                'corruption': int value - Measure of how corrupt a minister is, with 6 having a 1/2 chance to steal, 5 having 1/3 chance, etc.
                'image_id': string value - File path to the image used by this minister
        '''
        save_dict = {}
        save_dict['name'] = self.name
        save_dict['current_position'] = self.current_position
        save_dict['general_skill'] = self.general_skill
        save_dict['specific_skills'] = self.specific_skills
        save_dict['corruption'] = self.corruption
        save_dict['image_id'] = self.image_id
        return(save_dict)

    def roll(self, num_sides, min_success, max_crit_fail, predetermined_corruption = False):
        '''
        Description:
            Rolls and returns the result of a die with the inputted number of sides, modifying the result based on skill and possibly lying about the result based on corruption
        Input:
            int num_sides: Number of sides on the die rolled
            int min_success: Minimum roll required for a success
            int max_crit_fail: Maximum roll required for a critical failure
        Output:
            int: Returns the roll's modified result
        '''
        min_result = 1
        max_result = num_sides
        result = random.randrange(1, num_sides + 1)
        #print('rolling')
        #print('default result: ' + str(result))
        if random.randrange(1, 3) == 1: #1/2
            result += self.get_skill_modifier()
        #print('skill modified result: ' + str(result))

        if predetermined_corruption or self.check_corruption(): #true if stealing
            #print('stealing')
            result = random.randrange(max_crit_fail + 1, min_success) #if crit fail on 1 and success on 4+, do random.randrange(2, 4), pick between 2 and 3
            #print('reported result: ' + str(result))
        #else:
            #print('not stealing')

        if result < min_result:
            result = min_result
        elif result > max_result:
            result = max_result

        #if corrupt, chance to choose random non-critical failure result
            
        return(result)

    def roll_to_list(self, num_sides, min_success, max_crit_fail, num_dice): #use when multiple dice are being rolled, makes corruption independent of dice
        '''
        Description:
            Rolls and returns the result of the inputted number of dice each with the inputted number of sides, modifying the results based on skill and possibly lying about the result based on corruption
        Input:
            int num_sides: Number of sides on the die rolled
            int min_success: Minimum roll required for a success
            int max_crit_fail: Maximum roll required for a critical failure
            int num_dice: How many dice to roll
        Output:
            int list: Returns a list of the rolls' modified results
        '''
        results = []
        if self.check_corruption():
            corrupt_index = random.randrange(0, num_dice)
            for i in range(num_dice):
                if i == corrupt_index: #if rolling multiple dice, choose one of the dice randomly and make it the corrupt result, making it a non-critical failure
                    results.append(self.roll(num_sides, min_success, max_crit_fail, True))
                else: #for dice that are not chosen, can be critical or non-critical failure because higher will be chosen in case of critical failure, no successes allowed
                    results.append(self.roll(num_sides, min_success, 0, True)) #0 for max_crit_fail allows critical failure numbers to be chosen
        else: #if not corrupt, just roll twice
            for i in range(num_dice):
                results.append(self.roll(num_sides, min_success, max_crit_fail))
        return(results)
            

    def appoint(self, new_position):
        '''
        Description:
            Appoints this minister to a new office, putting it in control of relevant units. If the new position is 'none', removes the minister from their current office
        Input:
            string new_position: Office to appoint this minister to, like 'Minister of Trade'. If this equals 'none', fires this minister
        Output:
            None
        '''
        old_position = self.current_position
        if not self.current_position == 'none': #if removing, set old position to none
            self.global_manager.get('current_ministers')[self.current_position] = 'none'
        self.current_position = new_position
        self.global_manager.get('current_ministers')[new_position] = self
        for current_mob in self.global_manager.get('mob_list'):
            current_mob.update_controlling_minister()
        if not new_position == 'none': #if appointing
            self.global_manager.set('available_minister_list', utility.remove_from_list(self.global_manager.get('available_minister_list'), self))
            if self.global_manager.get('available_minister_left_index') >= len(self.global_manager.get('available_minister_list')) - 2:
                self.global_manager.set('available_minister_left_index', len(self.global_manager.get('available_minister_list')) - 2) #move available minister display up because available minister was removed
        else:
            self.global_manager.get('available_minister_list').append(self)
            self.global_manager.set('available_minister_left_index', len(self.global_manager.get('available_minister_list')) - 2) #move available minister display to newly fired minister
        for current_minister_type_image in self.global_manager.get('minister_image_list'):
            if current_minister_type_image.minister_type == new_position:
                current_minister_type_image.calibrate(self)
            elif current_minister_type_image.minister_type == old_position:
                current_minister_type_image.calibrate('none')
        if self.global_manager.get('displayed_minister') == self:
            minister_utility.calibrate_minister_info_display(self.global_manager, self) #update minister label
        minister_utility.update_available_minister_display(self.global_manager)

    def skill_setup(self):
        '''
        Description:
            Sets up the general and specific skills for this minister when it is created
        Input:
            None
        Output:
            None
        '''
        self.general_skill = random.randrange(1, 4) #1-3, general skill as in all fields, not military
        self.specific_skills = {}
        for current_minister_type in self.global_manager.get('minister_types'):
            self.specific_skills[current_minister_type] = random.randrange(0, 4) #0-3

    def corruption_setup(self):
        '''
        Description:
            Sets up the corruption level for this minister when it is created
        Input:
            None
        Output:
            None
        '''
        self.corruption = random.randrange(1, 7) #1-7
        self.corruption_threshold = 10 - self.corruption #minimum roll on D6 required for corruption to occur
            
    def check_corruption(self): #returns true if stealing for this roll
        '''
        Description:
            Checks and returns whether this minister will steal funds and lie about the dice roll results on a given roll
        Input:
            None
        Output:
            boolean: Returns True if this minister will be corrupt for the roll
        '''
        if random.randrange(1, 7) >= self.corruption_threshold:
            return(True)
        else:
            return(False)

    def get_skill_modifier(self):
        '''
        Description:
            Checks and returns the dice roll modifier for this minister's current office. A combined general and specific skill of <= 2 gives a -1 modifier, >5 5 gives a +1 modifier and other give a 0 modifier
        Input:
            None
        Output:
            int: Returns the dice roll modifier for this minister's current office
        '''
        if not self.current_position == 'none':
            skill = self.general_skill + self.specific_skills[self.current_position]
        else:
            skill = self.general_skill
        if skill <= 2: #1-2
            return(-1)
        elif skill <= 4: #3-4
            return(0)
        else: #5-6
            return(1)

    def remove(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program
        Input:
            None
        Output:
            None
        '''
        if not self.current_position == 'none':
            self.global_manager.get('current_ministers')[self.current_position] = 'none'
            for current_minister_image in self.global_manager.get('minister_image_list'):
                if current_minister_image.minister_type == self.current_position:
                    current_minister_image.calibrate('none')
            self.current_position = 'none'
        self.global_manager.set('minister_list', utility.remove_from_list(self.global_manager.get('minister_list'), self))
        self.global_manager.set('available_minister_list', utility.remove_from_list(self.global_manager.get('available_minister_list'), self))
        minister_utility.update_available_minister_display(self.global_manager)
