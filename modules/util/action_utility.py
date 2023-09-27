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

def generate_die_input_dict(coordinates, final_result, action, global_manager):
    '''
    Description:
        Creates and returns the input dict of a die created at the inputted coordinates with the inputted final result for the inputted action
    Input:
        int tuple coordinates: Two values representing x and y coordinates for the pixel location of the element
        int final_result: Predetermined final result of roll for die to end on
        action action: Action for which die is being rolled
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        dictionary: Returns the created input dict
    '''
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
        'final_result': final_result,
        'init_type': 'die'
    }
    return(die_input_dict)

def generate_action_ordered_collection_input_dict(coordinates, global_manager, override_input_dict=None):
    '''
    Description:
        Creates and returns the input dict of an ordered collection created at the inputted coordinates with any extra overrides
    Input:
        int tuple coordinates: Two values representing x and y coordinates for the pixel location of the element
        global_manager_template global_manager: Object that accesses shared variables
        dictionary override_input_dict=None: Optional dictionary to override attributes of created input_dict
    Output:
        dictionary: Returns the created input dict
    '''
    return_dict = {
        'coordinates': coordinates,
        'width': scaling.scale_width(10, global_manager),
        'height': scaling.scale_height(30, global_manager),
        'modes': [global_manager.get('current_game_mode')],
        'init_type': 'ordered collection',
        'initial_members': [],
        'reversed': True
    }
    if override_input_dict:
        for value in override_input_dict:
            return_dict[value] = override_input_dict[value]
    return(return_dict)

def generate_minister_portrait_input_dicts(coordinates, action, global_manager):
    '''
    Description:
        Creates and returns the input dicts of a minister portrait/background pair created at the inputted coordinates for the inputted action
    Input:
        int tuple coordinates: Two values representing x and y coordinates for the pixel location of the elements
        action action: Action for which portrait is being created
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        dictionary list: Returns the created input dicts
    '''
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

def generate_risk_message(action, unit):
    '''
    Description:
        Creates and returns the risk message for the inputted unit conducting the inputted action, based on veteran status and modifiers
    Input:
        action action: Action being conducted
        pmob unit: Unit conducting action
    Output:
        dictionary list: Returns the created input dicts
    '''
    risk_value = -1 * action.current_roll_modifier #modifier of -1 means risk value of 1
    if unit.veteran: #reduce risk if veteran
        risk_value -= 1

    if risk_value < 0: #0/6 = no risk
        message = 'RISK: LOW /n /n'
    elif risk_value == 0: #1/6 death = moderate risk
        message = 'RISK: MODERATE /n /n' #puts risk message at beginning
    elif risk_value == 1: #2/6 = high risk
        message = 'RISK: HIGH /n /n'
    elif risk_value > 1: #3/6 or higher = extremely high risk
        message = 'RISK: DEADLY /n /n'
    return(message)
