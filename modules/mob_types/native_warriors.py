#Contains functionality for native warriors units

import random
from .npmobs import npmob
from .. import utility

class native_warriors(npmob):
    def __init__(self, from_save, input_dict, global_manager):
        super().__init__(from_save, input_dict, global_manager)
        self.hostile = True
        self.saves_normally = False #saves as part of village
        self.origin_village = input_dict['origin_village']
        self.origin_village.attached_warriors.append(self)
        self.npmob_type = 'native_warriors'
        if self.combat_possible(): #attack any player-controlled units in tile when spawning
            available_directions = [(0, 1), (0, -1), (1, 0), (-1, 0)] #all directions
            possible_directions = [] #only directions that can be retreated in
            for direction in available_directions:
                cell = self.images[0].current_cell.grid.find_cell(self.x - direction[0], self.y - direction[0])
                if not cell == 'none':
                    if not cell.has_pmob() and not cell.terrain == 'water':
                        possible_directions.append(direction)
            if len(possible_directions) > 0:
                self.last_move_direction = random.choice(possible_directions)
                self.global_manager.get('attacker_queue').append(self)
            else:
                self.remove()
                self.origin_village.change_population(1) #despawn if pmob on tile and can't retreat anywhere

    def remove(self):
        super().remove()
        self.origin_village.attached_warriors = utility.remove_from_list(self.origin_village.attached_warriors, self)

    def check_despawn(self):
        if random.randrange(1, 7) == 1:
            self.remove()
            self.origin_village.change_population(1)
