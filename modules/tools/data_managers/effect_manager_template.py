import modules.constants.constants as constants

class effect_manager_template():
    '''
    Object that controls global effects
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
        self.possible_effects = []
        self.active_effects = []

    def __str__(self):
        '''
        Description:
            Returns text for a description of this object when printed
        Input:
            None
        Output:
            string: Returns text to print
        '''
        text = 'Active effects: '
        for current_effect in self.active_effects:
            text += '\n    ' + current_effect.__str__()
        return(text)

    def effect_active(self, effect_type):
        '''
        Description:
            Finds and returns whether any effect of the inputted type is active
        Input:
            string effect_type: Type of effect to check for
        Output:
            boolean: Returns whether any effect of the inputted type is active
        '''
        for current_effect in self.active_effects:
            if current_effect.effect_type == effect_type:
                return(True)
        return(False)

    def set_effect(self, effect_type, new_status):
        '''
        Description:
            Finds activates/deactivates all effects of the inputted type, based on the inputted status
        Input:
            string effect_type: Type of effect to check for
            string new_status: New activated/deactivated status for effects
        Output:
            None
        '''
        for current_effect in self.possible_effects:
            if current_effect.effect_type == effect_type:
                if new_status == True:
                    current_effect.apply()
                else:
                    current_effect.remove()

    def effect_exists(self, effect_type):
        '''
        Description:
            Checks whether any effects of the inputted type exist
        Input:
            string effect_type: Type of effect to check for
        Output:
            boolean: Returns whether any effects of the inputted type exist
        '''
        for current_effect in self.possible_effects:
            if current_effect.effect_type == effect_type:
                return(True)
        return(False)