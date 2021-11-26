import random

from . import utility
from . import actor_utility

class minister(): #general, bishop, merchant, explorer, engineer, factor, prosecutor
    def __init__(self, from_save, input_dict, global_manager):
        self.actor_type = 'minister' #used for actor display labels and images
        self.global_manager = global_manager
        self.global_manager.get('minister_list').append(self)
        if from_save:
            self.name = input_dict['name']
            self.current_position = input_dict['current_position']
            if not self.current_position == 'none':
                self.global_manager.get('current_ministers')[self.current_position] = self
            self.general_skill = input_dict['general_skill']
            self.specific_skills = input_dict['specific_skills']
            self.corruption = input_dict['corruption']
            self.corruption_threshold = 10 - self.corruption
            self.image_id = input_dict['image_id']
        else:
            self.name = self.global_manager.get('flavor_text_manager').generate_flavor_text('minister_names')
            self.skill_setup()
            self.corruption_setup()
            self.current_position = 'none'
            self.image_id = random.choice(self.global_manager.get('minister_portraits'))
        self.update_tooltip()

    def update_tooltip(self):
        self.tooltip_text = []
        if not self.current_position == 'none':
            keyword = self.global_manager.get('minister_type_dict')[self.current_position] #type, like military
            self.tooltip_text.append('This is ' + self.name + ', your ' + self.current_position + '.')
            self.tooltip_text.append('Whenever you command a ' + keyword + '-oriented unit to do an action, the ' + self.current_position + ' is responsible for executing the action.')
        else:
            self.tooltip_text.append('This is ' + self.name + ', a recruitable minister.')

    def to_save_dict(self):
        save_dict = {}
        save_dict['name'] = self.name
        save_dict['current_position'] = self.current_position
        save_dict['general_skill'] = self.general_skill
        save_dict['specific_skills'] = self.specific_skills
        save_dict['corruption'] = self.corruption
        save_dict['image_id'] = self.image_id
        return(save_dict)

    def roll(self, num_sides, min_success, max_crit_fail, predetermined_corruption = False):
        min_result = 1
        max_result = num_sides
        result = random.randrange(1, num_sides + 1)
        print('rolling')
        print('default result: ' + str(result))
        if random.randrange(1, 3) == 1: #1/2
            result += self.get_skill_modifier()
        print('skill modified result: ' + str(result))

        if predetermined_corruption or self.check_corruption(): #true if stealing
            print('stealing')
            result = random.randrange(max_crit_fail + 1, min_success) #if crit fail on 1 and success on 4+, do random.randrange(2, 4), pick between 2 and 3
            print('reported result: ' + str(result))
        else:
            print('not stealing')

        if result < min_result:
            result = min_result
        elif result > max_result:
            result = max_result

        #if corrupt, chance to choose random non-critical failure result
            
        return(result)

    def roll_to_list(self, num_sides, min_success, max_crit_fail, num_dice): #use when multiple dice are being rolled, makes corruption independent of dice
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
        if not self.current_position == 'none':
            self.global_manager.get('current_ministers')[self.current_position] = 'none'
        self.current_position = new_position
        self.global_manager.get('current_ministers')[new_position] = self
        for current_minister_type_image in self.global_manager.get('minister_type_image_list'):
            if current_minister_type_image.minister_type == new_position:
                current_minister_type_image.calibrate(self)
        if not self.global_manager.get('displayed_mob') == 'none':
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self.global_manager.get('displayed_mob')) #update minister label

    def skill_setup(self):
        self.general_skill = random.randrange(1, 4) #1-3, general skill as in all fields, not military
        self.specific_skills = {}
        for current_minister_type in self.global_manager.get('minister_types'):
            self.specific_skills[current_minister_type] = random.randrange(0, 4) #0-3

    def corruption_setup(self):
        self.corruption = random.randrange(1, 7) #1-7
        self.corruption_threshold = 10 - self.corruption #minimum roll on D6 required for corruption to occur
            
    def check_corruption(self): #returns true if stealing for this roll
        if random.randrange(1, 7) >= self.corruption_threshold:
            return(True)
        else:
            return(False)

    def get_skill_modifier(self):
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
        if not self.current_position == 'none':
            self.global_manager.get('current_ministers')[self.current_position] = 'none'
            self.current_position = 'none'
        self.global_manager.set('minister_list', utility.remove_from_list(self.global_manager.get('minister_list'), self))
