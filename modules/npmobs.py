#Contains functionality for non-player mobs

from ..mobs import mob

class npmob(mob):
    '''
    Short for non-player-mob, mob not controlled by the player
    '''
    def __init__(self, from_save, input_dict, global_manager):
        super().__init__(from_save, input_dict, global_manager)
        self.global_manager.get('npmob_list').append(self)
        self.is_npmob = True
        self.is_pmob = False

