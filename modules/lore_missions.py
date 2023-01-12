#Contains functionality for lore missions

import random
from . import utility
from . import notification_tools

class lore_mission():
    '''
    Mission from geographic society for an artifact that can be searched for at locations based on leads from villages, artifact gives permanent positive effect modifier and other bonuses when 
        found
    '''
    def __init__(self, from_save, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'lore_type': string value - Required if from save, type of lore this mission is associated with, like 'botany'
                'artifact_type': string value - Required if from save, type of artifact this mission is for, like 'orchid'
                'adjective': string adjective - Required if from save, adjective attached to this mission's artifact, like 'crimson'
                'possible_artifact_location_dicts': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each of this mission's 
                    possible artifact locations
                'confirmed_all_locations_revealed': boolean value - Required if from save, whether an expedition has already searched for rumors at a village and confirmed that all locations 
                    have been revealed
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.global_manager = global_manager
        self.global_manager.get('lore_mission_list').append(self)
        self.global_manager.set('current_lore_mission', self)
        self.possible_artifact_locations = []
        if from_save:
            self.lore_type = input_dict['lore_type']
            self.artifact_type = input_dict['artifact_type']
            self.adjective = input_dict['adjective']
            self.name = self.adjective + self.artifact_type
            for current_save_dict in input_dict['possible_artifact_location_dicts']:
                current_save_dict['lore_mission'] = self
                new_possible_artifact_location = possible_artifact_location(True, current_save_dict, self.global_manager)
                if current_save_dict['coordinates'] == input_dict['artifact_coordinates']:
                    self.artifact_location = new_possible_artifact_location
            self.confirmed_all_locations_revealed = input_dict['confirmed_all_locations_revealed']
        else:
            self.lore_type = random.choice(global_manager.get('lore_types'))
            self.artifact_type = random.choice(global_manager.get('lore_types_artifact_dict')[self.lore_type])
            self.adjective = random.choice(global_manager.get('lore_types_adjective_dict')[self.lore_type])
            self.name = self.adjective + self.artifact_type
            num_possible_artifact_locations = random.randrange(1, 7)
            while len(self.possible_artifact_locations) < num_possible_artifact_locations:
                input_dict = {
                    'lore_mission': self,
                    'coordinates': self.generate_possible_artifact_coordinates(),
                    'revealed': False
                }
                new_possible_artifact_location = possible_artifact_location(False, input_dict, self.global_manager)
            for current_village in self.global_manager.get('village_list'):
                current_village.revealed = False
            self.confirmed_all_locations_revealed = False
            self.artifact_location = random.choice(self.possible_artifact_locations)
            text = 'A new ' + self.lore_type + ' mission has been issued by the ' + self.global_manager.get('current_country').government_type_adjective.capitalize() + ' Geographical Society'
            text += ' to find the ' + self.name + '. /n /n'
            notification_tools.display_notification(text, 'none', self.global_manager)

        if self.global_manager.get('effect_manager').effect_active('show_lore_mission_locations'):
            print('new mission for ' + self.name)
            for current_possible_artifact_location in self.possible_artifact_locations:
                print('possible location at (' + str(current_possible_artifact_location.x) + ', ' + str(current_possible_artifact_location.y) + ')')
            print('actual location at (' + str(self.artifact_location.x) + ', ' + str(self.artifact_location.y) + ')')

    def to_save_dict(self):
        '''
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
                'lore_type': string value - Type of lore this mission is associated with, like 'botany'
                'artifact_type': string value - Type of artifact this mission is for, like 'orchid'
                'adjective': string value - Adjective attached to this mission's artifact, like 'crimson'
                'possible_artifact_location_dicts': dictionary list value - List of dictionaries of saved information necessary to recreate each of this mission's possible artifact locations
                'artifact_coordinates': int tuple value - Two values representing this mission's artifact's x and y coordinates on the strategic grid
        '''    
        save_dict = {}
        save_dict['lore_type'] = self.name
        save_dict['artifact_type'] = self.artifact_type
        save_dict['adjective'] = self.adjective
        save_dict['possible_artifact_location_dicts'] = []
        save_dict['artifact_coordinates'] = (self.artifact_location.x, self.artifact_location.y)
        for current_possible_artifact_location in self.possible_artifact_locations:
            save_dict['possible_artifact_location_dicts'].append(current_possible_artifact_location.to_save_dict())
        save_dict['confirmed_all_locations_revealed'] = self.confirmed_all_locations_revealed
        return(save_dict)

    def generate_possible_artifact_coordinates(self):
        '''
        Description:
            Generates and returns coordinates for a possible artifact location that are not already used by another one of this mission's locations
        Input:
            None
        Output:
            int tuple: Returns coordinates for a possible artifact location that are not already used by another one of this mission's locations
        '''
        used_coordinates = []
        for current_possible_artifact_location in self.possible_artifact_locations:
            used_coordinates.append((current_possible_artifact_location.x, current_possible_artifact_location.y))
        possible_coordinates = (random.randrange(0, self.global_manager.get('strategic_map_width')), random.randrange(1, self.global_manager.get('strategic_map_height')))
        while possible_coordinates in used_coordinates: #would cause infinite loop if too many possible locations existed
            possible_coordinates = (random.randrange(0, self.global_manager.get('strategic_map_width')), random.randrange(1, self.global_manager.get('strategic_map_height')))
        return(possible_coordinates)

    def remove(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program
        Input:
            None
        Output:
            None
        '''
        self.global_manager.set('current_lore_mission', 'none')
        self.global_manager.set('lore_mission_list', utility.remove_from_list(self.global_manager.get('lore_mission_list'), self))

    def get_num_revealed_possible_artifact_locations(self):
        '''
        Description:
            Finds and returns the number of this lore mission's possible artifact locations that have been revealed
        Input:
            None
        Output:
            int: Returns the number of this lore mission's possible artifact locations that have been revealed
        '''
        num_revealed = 0
        for current_possible_artifact_location in self.possible_artifact_locations:
            if current_possible_artifact_location.revealed:
                num_revealed += 1
        return(num_revealed)

    def get_random_unrevealed_possible_artifact_location(self):
        '''
        Description:
            Finds and returns a random one of this lore mission's possible artifact locations that has not been revealed yet, or 'none' if all have been revealed
        Input:
            None
        Output:
            Returns a random one of this lore mission's possible artifact locations that has not been revealed yet, or 'none' if all have been revealed
        '''
        if self.get_num_revealed_possible_artifact_locations() == len(self.possible_artifact_locations):
            return('none')
        current_possible_artifact_location = random.choice(self.possible_artifact_locations)
        while current_possible_artifact_location.revealed:
            current_possible_artifact_location = random.choice(self.possible_artifact_locations)
        return(current_possible_artifact_location)

class possible_artifact_location():
    '''
    Possible location for a lore mission's artifact that can be located from village rumors and investigated
    '''
    def __init__(self, from_save, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'lore_mission': lore_mission value - The lore mission this artifact is attached to
                'coordinates': int tuple value - Two values representing this location's x and y coordinates on the strategic grid
                'revealed': boolean value - Whether rumors of this location have been revealed yet
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.global_manager = global_manager
        self.lore_mission = input_dict['lore_mission']
        self.lore_mission.possible_artifact_locations.append(self)
        self.x, self.y = input_dict['coordinates']
        self.revealed = input_dict['revealed']

    def to_save_dict(self):
        '''
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
                'coordinates': int tuple value - Two values representing this location's x and y coordinates on the strategic grid
                'revealed': boolean value - Whether rumors of this location have been revealed yet
        '''    
        save_dict = {}
        save_dict['coordinates'] = (self.x, self.y)
        save_dict['revealed'] = self.revealed
        return(save_dict)
