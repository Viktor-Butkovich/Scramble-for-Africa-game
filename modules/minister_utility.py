#from . import ministers

def check_corruption(minister_type, global_manager):
    return(global_manager.get('current_ministers')[minister_type].check_corruption)

def get_skill_modifier(minister_type, global_manager):
    return(global_manager.get('current_ministers')[minister_type].get_skill_modifier)

def calibrate_minister_info_display(global_manager, new_minister):
    global_manager.set('displayed_minister', new_minister)
    for current_object in global_manager.get('minister_info_display_list'):
        current_object.calibrate(new_minister)

def update_available_minister_display(global_manager):
    available_minister_portrait_list = global_manager.get('available_minister_portrait_list')
    available_minister_left_index = global_manager.get('available_minister_left_index')
    available_minister_list = global_manager.get('available_minister_list')
    for current_index in range(len(available_minister_portrait_list)):
        minister_index = available_minister_left_index + current_index
        if minister_index < len(available_minister_list) and minister_index >= 0:
            available_minister_portrait_list[current_index].calibrate(available_minister_list[minister_index])
        else:
            available_minister_portrait_list[current_index].calibrate('none')
