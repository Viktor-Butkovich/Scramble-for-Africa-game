#Contains functionality for global effects

from ..util import utility
import modules.constants.constants as constants

class effect():
    def __init__(self, effect_id, effect_type):
        '''
        Description:
            Initializes this object
        Input:
            string effect_id: Name of effect, like 'british_country_modifier'
            string effect_type: Type of effect produced by this effect, like 'advertising_plus_modifier'
        Output:
            None
        '''
        self.effect_manager = constants.effect_manager
        self.effect_manager.possible_effects.append(self)
        
        self.effect_id = effect_id
        self.effect_type = effect_type
        #eventually add int/string duration: Duration of effect in turns, or 'none' if infinite/conditional

    def __str__(self):
        '''
        Description:
            Returns text for a description of this object when printed
        Input:
            None
        Output:
            string: Returns text to print
        '''
        text = self.effect_id + ': ' + self.effect_type
        return(text)

    def apply(self):
        '''
        Description:
            Causes this effect to become active
        Input:
            None
        Output:
            None
        '''
        if not self in self.effect_manager.active_effects:
            self.effect_manager.active_effects.append(self)

    def remove(self):
        '''
        Description:
            Causes this effect to become unactive
        Input:
            None
        Output:
            None
        '''
        if self in self.effect_manager.active_effects:
            self.effect_manager.active_effects = utility.remove_from_list(self.effect_manager.active_effects, self)
