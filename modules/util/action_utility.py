#Contains miscellaneous functions relating to action functionality
from . import scaling
def cancel_ongoing_actions(global_manager):
    '''
    Description:
        Cancels any ongoing actions and frees the player to take other actions
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    global_manager.set('ongoing_action', False)
    global_manager.set('ongoing_action_type', 'none')

def generate_die_input_dicts(coordinates, result, action, global_manager):
    result_outcome_dict = {'min_success': action.current_min_success, 'min_crit_success': action.current_min_crit_success, 'max_crit_fail': action.current_max_crit_fail}
    outcome_color_dict = {'success': 'dark green', 'fail': 'dark red', 'crit_success': 'bright green', 'crit_fail': 'bright red', 'default': 'black'}

    die_input_dict = {
        'coordinates': scaling.scale_coordinates(coordinates[0], coordinates[1], global_manager),
        'width': scaling.scale_width(100, global_manager),
        'height': scaling.scale_height(100, global_manager),
        'modes': [global_manager.get('current_game_mode')],
        'num_sides': 6,
        'result_outcome_dict': result_outcome_dict,
        'outcome_color_dict': outcome_color_dict,
        'final_result': result,
        'init_type': 'die'
    }
    return([die_input_dict])
    #attached_dice_list.append(new_die)

def generate_action_ordered_collection_input_dict(coordinates, action, global_manager):
    return({
        'coordinates': coordinates,
        'width': scaling.scale_width(10, global_manager),
        'height': scaling.scale_height(30, global_manager),
        'modes': [global_manager.get('current_game_mode')],
        'init_type': 'ordered collection',
        'initial_members': [],
        'reversed': True
    })

def generate_minister_portrait_input_dicts(coordinates, action, global_manager):
    if global_manager.get('ongoing_action_type') == 'combat': #combat has a different dice layout
        minister_icon_coordinates = (coordinates[0] - 120, coordinates[1] + 5)
    else:
        minister_icon_coordinates = (coordinates[0], coordinates[1] + 120)

    portrait_background_input_dict = {
        'coordinates': scaling.scale_coordinates(minister_icon_coordinates[0], minister_icon_coordinates[1], global_manager),
        'width': scaling.scale_width(100, global_manager),
        'height': scaling.scale_height(100, global_manager),
        'modes': [global_manager.get('current_game_mode')],
        'attached_minister': action.current_unit.controlling_minister,
        'minister_image_type': 'position',
        'init_type': 'dice roll minister image'
    }
    
    portrait_front_input_dict = {
        'coordinates': scaling.scale_coordinates(minister_icon_coordinates[0], minister_icon_coordinates[1], global_manager),
        'width': scaling.scale_width(100, global_manager),
        'height': scaling.scale_height(100, global_manager),
        'modes': [global_manager.get('current_game_mode')],
        'attached_minister': action.self.current_unit.controlling_minister,
        'minister_image_type': 'portrait',
        'init_type': 'dice roll minister image',
        'member_config': {'order_overlap': True}
    }
    return([portrait_background_input_dict, portrait_front_input_dict])
#unit.display_die((die_x, 500), first_roll_list[0], unit.current_min_success, unit.current_min_crit_success, unit.current_max_crit_fail)
