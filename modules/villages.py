import random

from . import village_name_generator

class village():
    def __init__(self, cell):
        self.aggressiveness = random.randrange(1, 10) #1-9
        self.population = random.randrange(1, 10) #1-9
        self.available_workers = 0
        self.attempted_trades = 0
        self.cell = cell
        self.name = village_name_generator.create_village_name()
            
    def get_tooltip(self):
        tooltip_text = []
        tooltip_text.append("Village name: " + self.name)
        tooltip_text.append("    Total population: " + str(self.population))
        tooltip_text.append("    Available workers: " + str(self.available_workers))
        tooltip_text.append("    Aggressiveness: " + str(self.aggressiveness))
        return(tooltip_text)
