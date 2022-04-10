#Contains functionality for porters

from .groups import group
from .. import actor_utility

class battalion(group): #most battalion_unique behaviors found in pmob combat functions and get_combat_modifier
    '''
    A group with a major officer that can fight enemy units
    '''
    def __init__(self, from_save, input_dict, global_manager):
        super().__init__(from_save, input_dict, global_manager)
        self.set_group_type('battalion')
        self.is_battalion = True
        if self.worker.worker_type == 'European':
            self.battalion_type = 'imperial'
        else: #colonial
            self.battalion_type = 'colonial'

    def move(self, x_change, y_change):
        super().move(x_change, y_change)
        if not self.in_vehicle:
            self.attempt_local_combat()

    def attempt_local_combat(self):
        defender = self.images[0].current_cell.get_best_combatant('npmob')
        if not defender == 'none':
            self.start_combat('attacking', defender)
