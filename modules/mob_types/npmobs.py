#Contains functionality for non-player mobs

import random
from ..mobs import mob
from .. import utility

class npmob(mob):
    '''
    Short for non-player-mob, mob not controlled by the player
    '''
    def __init__(self, from_save, input_dict, global_manager):
        super().__init__(from_save, input_dict, global_manager)
        self.hostile = False
        self.controllable = False
        self.is_npmob = True
        
        self.selection_outline_color = 'bright red'
        
    def remove(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program. Also deselects this mob and drops any commodities it is carrying
        Input:
            None
        Output:
            None
        '''
        super().remove()
        self.global_manager.set('npmob_list', utility.remove_from_list(self.global_manager.get('npmob_list'), self)) #make a version of npmob_list without self and set npmob_list to it
        
