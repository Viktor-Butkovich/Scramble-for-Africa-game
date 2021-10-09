import random

from . import village_name_generator

class village():
    '''
    Object that represents a native village in a cell on the strategic map grid
    '''
    def __init__(self, cell):
        '''
        Description:
            Initializes this object
        Input:
            cell cell: cell on strategic map grid in which this village exists
        Output:
            None
        '''
        self.aggressiveness = random.randrange(1, 10) #1-9
        self.population = random.randrange(1, 10) #1-9
        self.available_workers = 0
        self.attempted_trades = 0
        self.cell = cell
        self.name = village_name_generator.create_village_name()
            
    def get_tooltip(self):
        '''
        Description:
            Returns this village's tooltip. Its tooltip describes its name, population, how many of its population are willing to become workers, and aggressiveness
        Input:
            None
        Output:
            string list: list with each item representing a line of this village's tooltip
        '''
        tooltip_text = []
        tooltip_text.append("Village name: " + self.name)
        tooltip_text.append("    Total population: " + str(self.population))
        tooltip_text.append("    Available workers: " + str(self.available_workers))
        tooltip_text.append("    Aggressiveness: " + str(self.aggressiveness))
        return(tooltip_text)

    def get_aggressiveness_modifier(self): #modifier affects roll difficulty, not roll result
        '''
        Description:
            Returns a modifier corresponding to this village's aggressiveness, with higher aggressiveness causing lower modifiers. These modifiers affect the difficulty of actions relating to this village
        Input:
            None
        Output:
            int: Returns -1 if this village's aggressiveness is between 0 and 3, returns 0 if this village's aggressiveness if between 4 and 6, otherwise returns 1
        '''
        if self.aggressiveness <= 3: #1-3
            return(-1)
        elif self.aggressiveness <= 6: #4 - 6
            return(0)
        else: #7 - 9
            return(1)
