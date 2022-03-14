#Contains functionality for porters

from .groups import group
from .. import actor_utility

class battalion(group):
    '''
    A group with a major officer that can fight enemy units
    '''
    def __init__(self, from_save, input_dict, global_manager):
        super().__init__(from_save, input_dict, global_manager)
        self.set_group_type('battalion')
