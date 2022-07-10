#Contains functionality for wild beasts

import random
from .npmobs import npmob
from .. import utility

class beast(npmob):
    '''
    Beasts that wander the map hidden, prefer certain terrains, attack/demoralize nearby units, and can be tracked down by a safari
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
                'image': string value - File path to the image used by this object
                'name': string value - Required if from save, this mob's name
                'modes': string list value - Game modes during which this mob's images can appear
                'movement_points': int value - Required if from save, how many movement points this actor currently has
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.hidden = False
        global_manager.get('beast_list').append(self)
        super().__init__(from_save, input_dict, global_manager)
        self.npmob_type = 'beast'
        self.hostile = True
        if from_save:
            self.set_hidden(input_dict['hidden'])
        else:
            self.hidden = True

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
        return(save_dict) 

    def end_turn_move(self):
        self.set_hidden(random.choice([True, False]))
        if not self.hidden:
            super().end_turn_move()
        

    def set_hidden(self, new_hidden):
        self.hidden = new_hidden
        if new_hidden == True:
            self.hide_images()
        else:
            self.show_images()
    
    def check_despawn(self):
        #if random.randrange(1, 7) == 1 and random.randrange(1, 7) <= 2:
        #    self.remove()
        nothing = 0
            
    def hide_images(self):
        '''
        Description:
            Hides this mob's images, allowing it to be hidden but still stored at certain coordinates when it is attached to another actor or otherwise not visible
        Input:
            None
        Output:
            None
        '''
        #print('hiding')
        #if self.hidden:

        #cells = []
        #for current_image in self.images:
        #    cells.append(current_image.current_cell)

        for current_image in self.images:
            current_image.remove_from_cell()
            
        #for current_cell in cells:
        #    if not current_cell == 'none':
        #        print(current_cell.contained_mobs)

    def show_images(self):
        '''
        Description:
            Shows this mob's images at its stored coordinates, allowing it to be visible after being attached to another actor or otherwise not visible
        Input:
            None
        Output:
            None
        '''
        #print('showing')
        #if not self.hidden:
        for current_image in self.images:
            current_image.add_to_cell()   

    def remove(self):
        super().remove()
        self.global_manager.set('beast_list', utility.remove_from_list(self.global_manager.get('beast_list'), self))
