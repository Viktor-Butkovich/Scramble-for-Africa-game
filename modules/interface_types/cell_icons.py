from ..actor_types.actors import actor

class cell_icon(actor):
    '''
    An actor that exists in a tile while also acting as an interface element
    '''
    def __init__(self, from_save, input_dict, global_manager):
        super().__init__(from_save, input_dict, global_manager)