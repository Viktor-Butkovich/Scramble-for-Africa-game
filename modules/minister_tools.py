from . import ministers

def check_corruption(minister_type, global_manager):
    return(global_manager.get('current_ministers')[minister_type].check_corruption)

def get_skill_modifier(minister_type, global_manager):
    return(global_manager.get('current_ministers')[minister_type].get_skill_modifier)

def create_placeholder_ministers(global_manager):
    for current_minister_type in global_manager.get('minister_types'):
        new_minister = ministers.minister(False, {}, global_manager)
        new_minister.appoint(current_minister_type)

def load_minister(input_dict, global_manager):
    new_minister = ministers.minister(True, input_dict, global_manager)
