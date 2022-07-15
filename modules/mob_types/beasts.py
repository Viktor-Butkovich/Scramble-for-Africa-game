#Contains functionality for wild beasts
'''
beast notes:
lion - clear and hills
elephant - clear and swamp
gorilla - jungle and mountain
Cape buffalo - clear and hills
crocodile - water and swamp
hippo - water and swamp
leopard - jungle and mountain
'''
import random
from .npmobs import npmob
from .. import utility

class beast(npmob):
    '''
    Beasts that wander the map hidden, prefer certain terrains, attack/demoralize nearby units, and can be tracked down by a safari
    '''
    def __init__(self, from_save, input_dict, global_manager):
        self.hidden = False
        global_manager.get('beast_list').append(self)
        self.animal_type = input_dict['animal_type']
        self.adjective = input_dict['adjective']
        if self.adjective == 'king':
            input_dict['name'] = self.animal_type + ' ' + self.adjective + ' '
        else:
            input_dict['name'] = self.adjective + ' ' + self.animal_type
        super().__init__(from_save, input_dict, global_manager)
        
        self.npmob_type = 'beast'
        self.hostile = True
        self.preferred_terrains = global_manager.get('animal_terrain_dict')[self.animal_type]
        if from_save:
            self.set_hidden(input_dict['hidden'])
        else:
            #self.set_hidden(True)
            self.set_hidden(False)
            self.set_max_movement_points(2)

    def to_save_dict(self):
        '''
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
                'init_type': string value - Represents the type of actor this is, used to initialize the correct type of object on loading
                'coordinates': int tuple value - Two values representing x and y coordinates on one of the game grids
                'modes': string list value - Game modes during which this actor's images can appear
                'grid_type': string value - String matching the global manager key of this actor's primary grid, allowing loaded object to start in that grid
                'name': string value - This actor's name
                'inventory': string/string dictionary value - Version of this actor's inventory dictionary only containing commodity types with 1+ units held
                'end_turn_destination': string or int tuple value- 'none' if no saved destination, destination coordinates if saved destination
                'end_turn_destination_grid_type': string value - Required if end_turn_destination is not 'none', matches the global manager key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - How many movement points this actor currently has
                'image': string value - File path to the image used by this object
                'creation_turn': int value - Turn number on which this unit was created
                'disorganized': boolean value - Whether this unit is currently disorganized
        '''
        save_dict = super().to_save_dict()
        save_dict['hidden'] = self.hidden
        save_dict['preferred_terrains'] = self.preferred_terrains
        save_dict['adjective'] = self.adjective
        save_dict['animal_type'] = self.animal_type
        return(save_dict) 

    def find_closest_target(self):
        target_list = []
        current_cell = self.grids[0].find_cell(self.x, self.y)
        possible_cells = current_cell.adjacent_list + [current_cell]
        enemy_found = False
        for current_cell in possible_cells:
            if current_cell.terrain in self.preferred_terrains:
                if not enemy_found:
                    if current_cell.has_pmob():
                        target_list = [current_cell]
                        enemy_found = True
                    else:
                        target_list.append(current_cell)
                else:
                    if current_cell.has_pmob():
                        target_list.append(current_cell)
        if len(target_list) == 0:
            target_list.append(self.images[0].current_cell)
        return(random.choice(target_list))

    def end_turn_move(self):
        #self.set_hidden(random.choice([True, False]))
        #self.set_hidden(False)
        #if not self.hidden:
        super().end_turn_move()
        if self.grids[0].find_cell(self.x, self.y).has_pmob():
            self.set_hidden(False)
        #else:
        #    self.set_hidden(True)
        

    def set_hidden(self, new_hidden):
        self.hidden = new_hidden
        if new_hidden == True:
            self.hide_images()
        else:
            self.show_images()
    
    def check_despawn(self):
        if random.randrange(1, 7) == 1 and random.randrange(1, 7) == 1:
            self.remove()  

    def remove(self):
        super().remove()
        self.global_manager.set('beast_list', utility.remove_from_list(self.global_manager.get('beast_list'), self))
