import random

from . import utility

class minister(): #general, bishop, merchant, explorer, engineer, factor, prosecutor
    def __init__(self, from_save, input_dict, global_manager):
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
        else:
            self.name = self.global_manager.get('flavor_text_manager').generate_flavor_text('minister_names')
            self.skill_setup()
            self.corruption_setup()
            self.current_position = 'none'

    def to_save_dict(self):
        save_dict = {}
        save_dict['name'] = self.name
        save_dict['current_position'] = self.current_position
        save_dict['general_skill'] = self.general_skill
        save_dict['specific_skills'] = self.specific_skills
        save_dict['corruption'] = self.corruption
        return(save_dict)

    def appoint(self, new_position):
        if not self.current_position == 'none':
            self.global_manager.get('current_ministers')[self.current_position] = 'none'
        self.current_position = new_position
        self.global_manager.get('current_ministers')[new_position] = self

    def skill_setup(self):
        self.general_skill = random.randrange(1, 4) #1-3, general skill as in all fields, not military
        self.specific_skills = {}
        for current_minister_type in self.global_manager.get('minister_types'):
            self.specific_skills[current_minister_type] = random.randrange(0, 4) #0-3

    def corruption_setup(self):
        self.corruption = random.randrange(1, 7) #1-7
        self.corruption_threshold = 10 - self.corruption #minimum roll on D6 required for corruption to occur
            
    def check_corruption(self):
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
