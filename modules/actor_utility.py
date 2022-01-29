#Contains miscellaneous functions relating to actor functionality

import random

from . import scaling

def stop_exploration(global_manager):
    '''
    Description:
        Stops any ongoing explorations and removes exploration destination marks, used at end of exploration
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    for current_exploration_mark in global_manager.get('exploration_mark_list'): #copy_exploration_mark_list:
        current_exploration_mark.remove()
    global_manager.set('exploration_mark_list', [])
    for current_mob in global_manager.get('mob_list'):
        if current_mob.can_explore:
            current_mob.exploration_mark_list = []
    exploration_mark_list = []
    global_manager.set('ongoing_exploration', False)

def create_image_dict(stem):
    '''
    Description:
        Creates a dictionary of image file paths for an actor to store and set its image to in different situations
    Input:
        string stem: Path to an actor's image folder
    Output:
        string/string dictionary: String image description keys and string file path values, like 'left': 'explorer/left.png'
    '''
    stem = 'mobs/' + stem
    stem += '/'
    image_dict = {}
    image_dict['default'] = stem + 'default.png'
    image_dict['right'] = stem + 'right.png'  
    image_dict['left'] = stem + 'left.png'
    return(image_dict)

def update_roads(global_manager):
    '''
    Description:
        Updates the road/railroad connections between tiles when a new one is built
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    for current_infrastructure_connection_image in global_manager.get('infrastructure_connection_list'):
        current_infrastructure_connection_image.update_roads()
    
def get_selected_list(global_manager):
    '''
    Description:
        Returns a list of all currently selected units. Currently, the game will only have 1 selected unit at a time and this should be updated
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        mob list: All mobs that are currently selected
    '''
    selected_list = []
    for current_mob in global_manager.get('mob_list'):
        if current_mob.selected:
            selected_list.append(current_mob)
    return(selected_list)

def deselect_all(global_manager):
    '''
    Description:
        Deselects all units. Currently, the game will only have 1 selected unit at a time and this should be updated.
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    for current_mob in global_manager.get('mob_list'):
        if current_mob.selected:
            current_mob.selected = False
    
def get_random_ocean_coordinates(global_manager):
    '''
    Description:
        Returns a random set of coordinates from the ocean section of the strategic map
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        int tuple: Two values representing x and y coordinates
    '''
    mob_list = global_manager.get('mob_list')
    mob_coordinate_list = []
    start_x = random.randrange(0, global_manager.get('strategic_map_grid').coordinate_width)
    start_y = 0
    return(start_x, start_y)

def calibrate_actor_info_display(global_manager, info_display_list, new_actor):
    '''
    Description:
        Updates all relevant objects to display a certain mob or tile
    Input:
        global_manager_template global_manager: Object that accesses shared variables
        button/actor list info_display_list: All buttons and actors that are updated when the displayed mob or tile changes. Can be 'tile_info_display_list' if the displayed tile is changing or 'mob_info_display_list' if the displayed
            mob is changing
        string new_actor: The new mob or tile that is displayed
    Output:
        None
    '''
    if info_display_list == global_manager.get('tile_info_display_list'):
        global_manager.set('displayed_tile', new_actor)
    elif info_display_list == global_manager.get('mob_info_display_list'):
        global_manager.set('displayed_mob', new_actor)
    for current_object in info_display_list:
        current_object.calibrate(new_actor)

def order_actor_info_display(global_manager, info_display_list, default_y): #displays actor info display labels in order, skipping hidden ones
    '''
    Description:
        Changes locations of actor display labels to put all visible labels in order
    Input:
        global_manager_template global_manager: Object that accesses shared variables
        actor_match_label list info_display_list: All actor match labels associated with either mobs or tiles to put in order
        int default_y: y coordinate that the top label is moved to
    Output:
        None
    '''
    current_y = default_y
    for current_label in info_display_list:
        if current_label.can_show():
            current_y -= 35
            scaled_y = scaling.scale_height(current_y, global_manager)
            if not current_label.y == scaled_y: #if y is not the same as last time, move it
                current_label.set_y(scaled_y)

def get_migration_destinations(global_manager): #returns cells that could have slumss and receive migration
    return_list = []
    for current_building in global_manager.get('building_list'):
        if current_building.building_type in ['port', 'train_station', 'resource']:
            if not current_building.images[0].current_cell in return_list:
                return_list.append(current_building.images[0].current_cell)
    return(return_list)

def get_migration_sources(global_manager): #returns villages from which migration could occur
    return_list = []
    for current_village in global_manager.get('village_list'):
        if current_village.available_workers > 0:
            return_list.append(current_village)
    return(return_list)

def get_num_available_workers(location_types, global_manager): #gets how many available workers there are in either all villages, all slums, or both
    num_available_workers = 0
    if not location_types == 'village': #slums or all
        for current_building in global_manager.get('building_list'):
            if current_building.building_type == 'slums':
                num_available_workers += current_building.available_workers
    if not location_types == 'slums': #village or all
        for current_village in global_manager.get('village_list'):
            num_available_workers += current_village.available_workers
    return(num_available_workers)
