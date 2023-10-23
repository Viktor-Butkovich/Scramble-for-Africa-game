import random
import modules.constants.constants as constants
import modules.constants.status as status
from ...util import csv_utility

class flavor_text_manager_template():
    '''
    Object that reads flavor text from .csv files and distributes it to other parts of the program when requested
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
        self.subject_dict = {}
        self.set_flavor_text('exploration', 'text/explorer.csv')
        self.set_flavor_text('advertising_campaign', 'text/advertising.csv')
        self.set_flavor_text('minister_first_names', 'text/default.csv')
        self.set_flavor_text('minister_particles', 'text/default.csv')
        self.set_flavor_text('minister_last_names', 'text/default.csv')
        self.allow_particles = False
                
    def set_flavor_text(self, topic, file):
        '''
        Description:
            Sets this flavor text manager's list of flavor text for the inputted topic to the contents of the inputted csv file
        Input:
            string topic: Topic for the flavor text to set, like 'minister_first_names'
            string file: File to set flavor text to, like 'text/flavor_minister_first_names.csv'
        Output:
            None
        '''
        flavor_text_list = []
        current_flavor_text = csv_utility.read_csv(file)
        for line in current_flavor_text: #each line is a list
            flavor_text_list.append(line[0])
        self.subject_dict[topic] = flavor_text_list

    def generate_substituted_flavor_text(self, subject, replace_char, replace_with):
        '''
        Description:
            Returns a random flavor text statement based on the inputted string, with all instances of replace_char replaced with replace_with
        Input:
            string subject: Represents the type of flavor text to return
        Output:
            string: Random flavor text statement of the inputted subject
        '''
        base_text = random.choice(self.subject_dict[subject])
        return_text = ''
        for current_character in base_text:
            if current_character == replace_char:
                return_text += replace_with
            else:
                return_text += current_character
        return(return_text)

    def generate_substituted_indexed_flavor_text(self, subject, replace_char, replace_with):
        '''
        Description:
            Returns a random flavor text statement based on the inputted string, with all instances of replace_char replaced with replace_with
        Input:
            string subject: Represents the type of flavor text to return
        Output:
            string, int tuple: Random flavor text statement of the inputted subject, followed by the index in the flavor text list of the outputted flavor text
        '''
        base_text = random.choice(self.subject_dict[subject])
        index = self.subject_dict[subject].index(base_text)
        return_text = ''
        for current_character in base_text:
            if current_character == replace_char:
                return_text += replace_with
            else:
                return_text += current_character
        return((return_text, index))


    def generate_flavor_text(self, subject):
        '''
        Description:
            Returns a random flavor text statement based on the inputted string
        Input:
            string subject: Represents the type of flavor text to return
        Output:
            string: Random flavor text statement of the inputted subject
        '''
        return(random.choice(self.subject_dict[subject]))

    def generate_minister_name(self, background):
        '''
        Description:
            Generates and returns a random combination of minister first and last names
        Input:
            None
        Output:
            string: Returns a random combination of minister first and last names
        '''
        if status.current_country == status.Belgium:
            self.allow_particles = True
            if random.randrange(1, 7) >= 4:
                self.set_flavor_text('minister_first_names', 'text/names/dutch_first_names.csv')
                self.set_flavor_text('minister_last_names', 'text/names/dutch_last_names.csv')
                self.set_flavor_text('minister_particles', 'text/names/dutch_particles.csv')
                self.allow_double_last_names = False
            else:
                self.set_flavor_text('minister_first_names', 'text/names/french_first_names.csv')
                self.set_flavor_text('minister_last_names', 'text/names/french_last_names.csv')
                self.set_flavor_text('minister_particles', 'text/names/french_particles.csv')
                self.allow_double_last_names = True

        first_name = self.generate_flavor_text('minister_first_names')
        titles = ['Duke', 'Marquess', 'Earl', 'Viscount', 'Baron', 'Sir', 'Prince', 'Lord', 
                    'Duc', 'Marquis', 'Count', 'Vicomte', 'Chevalier', 'Écuyer',
                    'Duque', 'Marquês', 'Infante', 'Visconde', 'Barão', 'Conde', 'Dom', 'Fidalgo',
                    'Herzog', 'Markgraf', 'Landgraf', 'Pfalzgraf', 'Reichsgraf', 'Burggraf', 'Reichsfürst', 'Graf', 'Freiherr', 'Herr',
                    'Principe', 'Duca', 'Marchese', 'Conte', 'Visconte', 'Barone', 'Nobile', 'Cavaliere', 'Patrizio'                  
                ]
        if status.current_country == status.Germany: #Most German nobility had von particle but no inherited title
            if background == 'royal heir' or (background == 'aristocrat' and random.randrange(1, 7) >= 5):
                while not first_name in titles:
                    first_name = self.generate_flavor_text('minister_first_names')
                    if background != 'royal heir':
                        while first_name in ['Prince', 'Infante', 'Reichsfürst', 'Principe']: #only allow prince titles for royal heir
                            first_name = self.generate_flavor_text('minister_first_names')
            else:
                while first_name in titles:
                    first_name = self.generate_flavor_text('minister_first_names')
        else:
            if background in ['royal heir', 'aristocrat']:
                while not first_name in titles:
                    first_name = self.generate_flavor_text('minister_first_names')
                    if background != 'royal heir':
                        while first_name in ['Prince', 'Infante', 'Reichsfürst', 'Principe']: #only allow prince titles for royal heir
                            first_name = self.generate_flavor_text('minister_first_names')
            else:
                while first_name in titles:
                    first_name = self.generate_flavor_text('minister_first_names')

        name = first_name + ' '
        if self.allow_particles:
            if self.aristocratic_particles:
                if background in ['royal heir', 'aristocrat'] and self.aristocratic_particles:
                    name += self.generate_flavor_text('minister_particles')
            elif random.randrange(1, 7) >= 4:
                name += self.generate_flavor_text('minister_particles')
        last_name = self.generate_flavor_text('minister_last_names')

        name += last_name
        if self.allow_double_last_names and random.randrange(1, 7) >= 5:
            second_last_name = self.generate_flavor_text('minister_last_names')
            while second_last_name == last_name:
                second_last_name = self.generate_flavor_text('minister_last_names')
            name += '-' + second_last_name
        return(name)