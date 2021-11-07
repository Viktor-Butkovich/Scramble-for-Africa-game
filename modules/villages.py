#Contains functionality for villages

import random

from . import village_name_generator
from . import actor_utility

class village():
    '''
    Object that represents a native village in a cell on the strategic map grid
    '''
    def __init__(self, cell, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            cell cell: cell on strategic map grid in which this village exists
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.set_initial_population()
        self.set_initial_aggressiveness()
        self.available_workers = 0
        self.attempted_trades = 0
        self.cell = cell
        self.name = village_name_generator.create_village_name()
        self.global_manager = global_manager
        self.global_manager.get('village_list').append(self)

    def set_initial_population(self):
        '''
        Description:
            Sets this village's population to a random number between 1 and 9
        Input:
            None
        Output:
            None
        '''
        self.population = random.randrange(1, 10)
    
    def set_initial_aggressiveness(self):
        '''
        Description:
            Sets this village's population to its aggressiveness changed randomly. Change based on 9 rolls of D6, decrease on 1-2, increase on 5-6, roll again on 1 or 6
        Input:
            None
        Output:
            None
        '''
        self.aggressiveness = self.population
        remaining_rolls = 9
        while remaining_rolls > 0:
            remaining_rolls -= 1
            roll = random.randrange(1, 7)
            if roll <= 2: #1-2
                self.aggressiveness -= 1
                if roll == 1:
                    remaining_rolls += 1
            #3-4 does nothing
            elif roll >= 5: #5-6
                self.aggressiveness += 1
                if roll == 6:
                    remaining_rolls += 1
            if self.aggressiveness < 1:
                self.aggressiveness = 1
            elif self.aggressiveness > 9:
                self.aggressiveness = 9
            
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
            int: Returns 1 if this village's aggressiveness is between 0 and 3, returns 0 if this village's aggressiveness if between 4 and 6, otherwise returns -1
        '''
        if self.aggressiveness <= 3: #1-3
            return(1)
        elif self.aggressiveness <= 6: #4 - 6
            return(0)
        else: #7 - 9
            return(-1)

    def get_population_modifier(self): #modifier affects roll difficulty, not roll result
        '''
        Description:
            Returns a modifier corresponding to this village's population with higher population causing lower modifiers. These modifiers affect the difficulty and reward level of actions relating to this village
        Input:
            None
        Output:
            int: Returns 1 if this village's aggressiveness is between 0 and 3, returns 0 if this village's aggressiveness if between 4 and 6, otherwise returns -1
        '''
        if self.population <= 3: #1-3
            return(1)
        elif self.population <= 6: #4 - 6
            return(0)
        else: #7 - 9
            return(-1)

    def change_population(self, change):
        '''
        Description:
            Changes this village's population by the inputted amount. Prevents the value from exiting the allowed range of 1-9 and updates the tile info display as applicable
        Input:
            int change: amount this village's population is changed by
        Output:
            None
        '''
        self.population += change
        if self.population > 9:
            self.population = 9
        elif self.population < 1:
            self.population = 1
        if self.cell.tile == self.global_manager.get('displayed_tile'): #if being displayed, change displayed population value
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), self.cell.tile)

    def change_aggressiveness(self, change):
        '''
        Description:
            Changes this village's aggressiveness by the inputted amount. Prevents the value from exiting the allowed range of 1-9 and updates the tile info display as applicable
        Input:
            int change: amount this village's aggressivness is changed by
        Output:
            None
        '''
        self.aggressiveness += change
        if self.aggressiveness > 9:
            self.aggressiveness = 9
        elif self.aggressiveness < 1:
            self.aggressiveness = 1
        if self.cell.tile == self.global_manager.get('displayed_tile'): #if being displayed, change displayed aggressiveness value
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), self.cell.tile)
