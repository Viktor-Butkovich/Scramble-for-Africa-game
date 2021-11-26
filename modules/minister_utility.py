from . import ministers

def check_corruption(minister_type, global_manager):
    return(global_manager.get('current_ministers')[minister_type].check_corruption)

def get_skill_modifier(minister_type, global_manager):
    return(global_manager.get('current_ministers')[minister_type].get_skill_modifier)

def create_placeholder_ministers(global_manager):
    for current_minister_type in global_manager.get('minister_types'):
        new_minister = ministers.minister(False, {}, global_manager)
        new_minister.appoint(current_minister_type)
    calibrate_minister_info_display(global_manager, global_manager.get('current_ministers')['General']) #placeholder

def load_minister(input_dict, global_manager):
    new_minister = ministers.minister(True, input_dict, global_manager)

def calibrate_minister_info_display(global_manager, new_minister):
    global_manager.set('displayed_minister', new_minister)
    for current_object in global_manager.get('minister_info_display_list'):
        current_object.calibrate(new_minister)
