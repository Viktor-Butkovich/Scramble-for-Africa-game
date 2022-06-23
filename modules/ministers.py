#Contains functionality for ministers

import random

from . import utility
from . import actor_utility
from . import minister_utility
from . import notification_tools
from . import images
from . import scaling

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
            self.stolen_money = input_dict['stolen_money']
            self.corruption_evidence = input_dict['corruption_evidence']
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
            self.stolen_money = 0
            self.corruption_evidence = 0
            minister_utility.update_available_minister_display(self.global_manager)
        self.fabricated_evidence = 0
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

    def display_message(self, text):
        minister_icon_coordinates = (self.global_manager.get('notification_manager').notification_x - 140, 440 + 120)
        minister_position_icon = images.dice_roll_minister_image(minister_icon_coordinates, scaling.scale_width(100, self.global_manager), scaling.scale_height(100, self.global_manager), ['strategic', 'ministers', 'europe'],
            self, 'position', self.global_manager)
        minister_portrait_icon = images.dice_roll_minister_image(minister_icon_coordinates, scaling.scale_width(100, self.global_manager), scaling.scale_height(100, self.global_manager), ['strategic', 'ministers', 'europe'],
            self, 'portrait', self.global_manager)
        notification_tools.display_notification(text, 'minister', self.global_manager, 0)

    def steal_money(self, value, theft_type = 'none'):
        prosecutor = self.global_manager.get('current_ministers')['Prosecutor']
        if not prosecutor == 'none':
            if self.global_manager.get('DEBUG_show_minister_stealing'):
                print(self.current_position + " " + self.name + " stole " + str(value) + " money from " + theft_type + ".") 
            difficulty = self.no_corruption_roll(6)
            result = prosecutor.no_corruption_roll(6)
            if result >= difficulty: #caught by prosecutor if prosecutor succeeds skill contest roll
                if prosecutor.check_corruption(): #if prosecutor takes bribe, split money
                    prosecutor.stolen_money += (value / 2)
                    self.stolen_money += (value / 2)
                    if self.global_manager.get('DEBUG_show_minister_stealing'):
                        print("The theft was caught by the prosecutor, who accepted a bribe to not create evidence.") 
                else: #if prosecutor refuses bribe, still keep money but create evidence
                    self.stolen_money += value
                    self.corruption_evidence += 1
                    evidence_message = ""
                    #evidence_message += "To the governor, /n"
                    #evidence_message += "It has come to my attention that ..."
                    evidence_message += "Prosecutor " + prosecutor.name + " suspects that " + self.current_position + " " + self.name + " just engaged in corrupt activity and has filed a piece of evidence against him. /n /n"
                    evidence_message += "There are now " + str(self.corruption_evidence) + " piece" + utility.generate_plural(self.corruption_evidence) + " of evidence against " + self.name + ". /n /n"
                    evidence_message += "Each piece of evidence can help in a trial to remove a corrupt minister from office. /n /n"
                    prosecutor.display_message(evidence_message)
                    if self.global_manager.get('DEBUG_show_minister_stealing'):
                        print("The theft was caught by the prosecutor, who chose to create evidence.") 
            else: #if not caught, keep money
                self.stolen_money += value
                if self.global_manager.get('DEBUG_show_minister_stealing'):
                    print("The theft was not caught by the prosecutor.")
        if self.global_manager.get('DEBUG_show_minister_stealing'):
            print(self.name + " has now stolen a total of " + str(self.stolen_money) + " money.")
            print('')
                

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
        save_dict['stolen_money'] = self.stolen_money
        save_dict['corruption_evidence'] = self.corruption_evidence
        return(save_dict)

    def roll(self, num_sides, min_success, max_crit_fail, value, roll_type, predetermined_corruption = False):
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
        if random.randrange(1, 3) == 1: #1/2
            result += self.get_skill_modifier()

        if predetermined_corruption or self.check_corruption(): #true if stealing
            self.steal_money(value, roll_type)
            result = random.randrange(max_crit_fail + 1, min_success) #if crit fail on 1 and success on 4+, do random.randrange(2, 4), pick between 2 and 3

        if result < min_result:
            result = min_result
        elif result > max_result:
            result = max_result

        #if corrupt, chance to choose random non-critical failure result
            
        return(result)

    def no_corruption_roll(self, num_sides):
        '''
        Description:
            Rolls and returns the result of a die with the inputted number of sides, modifying the result based on skill with the assumption that corruption has already failed to occur
        Input:
            int num_sides: Number of sides on the die rolled

        Output:
            int: Returns the roll's modified result
        '''
        min_result = 1
        max_result = num_sides
        result = random.randrange(1, num_sides + 1)
        if random.randrange(1, 3) == 1: #1/2
            result += self.get_skill_modifier()

        if result < min_result:
            result = min_result
        elif result > max_result:
            result = max_result
            
        return(result)

    def roll_to_list(self, num_sides, min_success, max_crit_fail, value, roll_type, num_dice): #use when multiple dice are being rolled, makes corruption independent of dice
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
            self.steal_money(value, roll_type)
            corrupt_index = random.randrange(0, num_dice)
            for i in range(num_dice):
                if i == corrupt_index: #if rolling multiple dice, choose one of the dice randomly and make it the corrupt result, making it a non-critical failure
                    results.append(self.roll(num_sides, min_success, max_crit_fail, True))
                else: #for dice that are not chosen, can be critical or non-critical failure because higher will be chosen in case of critical failure, no successes allowed
                    results.append(self.roll(num_sides, min_success, 0, True)) #0 for max_crit_fail allows critical failure numbers to be chosen
        else: #if not corrupt, just roll with minister modifier
            for i in range(num_dice):
                results.append(self.no_corruption_roll(num_sides))
        return(results)
            
    def attack_roll_to_list(self, modifier, value, roll_type, num_dice):
        '''
        Description:
            Rolls and returns the result of the inputted number of 6-sided dice along with the enemy unit's roll in combat, modifying the results based on skill and possibly lying about the result based on corruption
        Input:
            int modifier: Modifier added to the friendly unit's roll, used to create realistic inconclusive results when corrupt
            int num_dice: number of dice rolled by the friendly unit, not including the one die rolled by the enemy unit
        Output:
            int list: Returns a list of the rolls' modified results, with the first item being the enemy roll
        '''
        results = []
        if self.check_corruption():
            self.steal_money(value, roll_type)
            for i in range(num_dice):
                results.append(0)
            difference = 10
            while difference >= 2: #keep rolling until a combination of attacker and defender rolls with an inconclusive result is found
                own_roll = random.randrange(1, 7) + modifier
                enemy_roll = random.randrange(1, 7)
                difference = abs(own_roll - enemy_roll)
            corrupt_index = random.randrange(0, num_dice)
            for i in range(num_dice):
                if i == corrupt_index: #if rolling multiple dice, choose one of the dice randomly to be the chosen result, with the others being lower
                    results[i] = own_roll
                else:
                    results[i] = random.randrange(1, own_roll + 1) # if own_roll is 1, range is 1-2 non-inclusive, always chooses 1
            results = [enemy_roll] + results #inserts enemy roll at beginning

        else: #if not corrupt, just roll with minister modifier
            for i in range(num_dice):
                results.append(self.no_corruption_roll(6))
            enemy_roll = random.randrange(1, 7)
            results = [enemy_roll] + results
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
        for current_pmob in self.global_manager.get('pmob_list'):
            current_pmob.update_controlling_minister()
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
        
        if not self.global_manager.get('minister_appointment_tutorial_completed'):
            completed = True
            for current_position in self.global_manager.get('minister_types'):
                if self.global_manager.get('current_ministers')[current_position] == 'none':
                    completed = False
            if completed:
                self.global_manager.set('minister_appointment_tutorial_completed', True)
                notification_tools.show_tutorial_notifications(self.global_manager)

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

    def get_roll_modifier(self):
        '''
        Description:
            Returns the modifier this minister will apply to a given roll. As skill has only a half chance of applying to a given roll, the returned value may vary
        Input:
            None
        Output:
            int: Returns the modifier this minister will apply to a given roll. As skill has only a half chance of applying to a given roll, the returned value may vary
        '''
        if random.randrange(1, 3) == 1: #half chance to apply skill modifier, otherwise return 0
            return(self.get_skill_modifier())
        else:
            return(0)

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
