#Contains miscellaneous functions relating to actor functionality

import random
import os
import pygame
import math

from . import utility

def reset_action_prices(global_manager):
    '''
    Description:
        Resets the costs of any actions that were increased during the previous turn
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    for current_action_type in global_manager.get('action_types'):
        global_manager.get('action_prices')[current_action_type] = global_manager.get('base_action_prices')[current_action_type]

def double_action_price(global_manager, action_type):
    '''
    Description:
        Doubles the price of a certain action type each time it is done, usually for ones that do not require workers
    Input:
        global_manager_template global_manager: Object that accesses shared variables
        string action_type: Type of action to double the price of
    Output:
        None
    '''
    global_manager.get('action_prices')[action_type] *= 2

def get_building_cost(global_manager, constructor, building_type, building_name = 'n/a'):
    '''
    Description:
        Returns the cost of the inputted unit attempting to construct the inputted building
    Input:
        global_manager_template global_manager: Object that accesses shared variables
        pmob/string constructor: Unit attempting to construct the building, or 'none' if no location/unit type is needed
        string building_type: Type of building to build, like 'infrastructure'
        string building_name = 'n/a': Name of building being built, used to differentiate roads from railroads
    Output:
        int: Returns the cost of the inputted unit attempting to construct the inputted building
    '''
    if building_type == 'infrastructure':
        building_type = building_name #road, railroad, road_bridge, or railroad_bridge

    if building_type == 'warehouses':
        if constructor == 'none':
            base_price = 5
        else:
            base_price = constructor.images[0].current_cell.get_warehouses_cost()
    else:
        base_price = global_manager.get('building_prices')[building_type]

    if building_type in ['train', 'steamboat']:
        cost_multiplier = 1
    elif constructor == 'none' or not global_manager.get('strategic_map_grid') in constructor.grids:
        cost_multiplier = 1
    else:
        terrain = constructor.images[0].current_cell.terrain
        cost_multiplier = global_manager.get('terrain_build_cost_multiplier_dict')[terrain]

    return(base_price * cost_multiplier)

def update_recruitment_descriptions(global_manager, target = 'all'):
    '''
    Description:
        Updates the descriptions of recruitable units for use in various parts of the program. Updates all units during setup and can target a certain unit to update prices, etc. when the information is needed later in the game.
            Creates list versions for tooltips and string versions for notifications
    Input:
        global_manager_template global_manager: Object that accesses shared variables
        string target = 'all': Targets a certain unit type, or 'all' by default, to update while minimizing unnecessary calculations
    Output:
        None
    '''
    if target == 'all':
        targets_to_update = global_manager.get('recruitment_types') + ['slums workers', 'village workers', 'slaves']
    else:
        targets_to_update = [target]

    for current_target in targets_to_update:
        recruitment_list_descriptions = global_manager.get('recruitment_list_descriptions')
        recruitment_string_descriptions = global_manager.get('recruitment_string_descriptions')
        text_list = []
        if current_target in global_manager.get('officer_types'):
            first_line = utility.capitalize(current_target) + 's are controlled by the ' + global_manager.get('officer_minister_dict')[current_target]
            if current_target == 'explorer':
                first_line += '.'
                text_list.append(first_line)
                text_list.append('When combined with workers, an explorer becomes an expedition unit that can explore new tiles and move swiftly along rivers with canoes.')
                
            elif current_target == 'hunter':
                first_line += '.'
                text_list.append(first_line)
                text_list.append('When combined with workers, a hunter becomes a safari unit that can attack and more easily detect and defend against beasts and move swiftly along rivers with canoes.')
                
            elif current_target == 'engineer':
                first_line += '.'
                text_list.append(first_line)
                text_list.append('When combined with workers, an engineer becomes a construction gang unit that can build buildings, roads, railroads, and trains.')
                
            elif current_target == 'driver':
                first_line += '.'
                text_list.append(first_line)
                text_list.append('When combined with workers, a driver becomes a porters unit that can move quickly and transport commodities.')
                
            elif current_target == 'foreman':
                first_line += '.'
                text_list.append(first_line)
                text_list.append('When combined with workers, a foreman becomes a work crew unit that can produce commodities when attached to a production facility.')
                
            elif current_target == 'merchant':
                first_line += ' and can personally search for loans and conduct advertising campaigns in Europe.'
                text_list.append(first_line)
                text_list.append('When combined with workers, a merchant becomes a caravan that can build trading posts and trade with native villages.')
                
            elif current_target == 'evangelist':
                first_line += ' and can personally conduct religious campaigns and public relations campaigns in Europe.'
                text_list.append(first_line)
                text_list.append('When combined with religious volunteers, an evangelist becomes a missionaries unit that can build missions and lower the aggressiveness of native villages.')
                
            elif current_target == 'major':
                first_line += '.'
                text_list.append(first_line)
                text_list.append('When combined with workers, a major becomes a battalion unit that has a very high combat strength, and can attack non-beast enemies, build forts, and capture slaves.')
                
        elif current_target == 'European workers':
            text_list.append('European workers have an upkeep of ' + str(global_manager.get('european_worker_upkeep')) + ' money each turn.')
            text_list.append('Officers and vehicles require an attached worker unit to perform most actions.')
            text_list.append('Each unit of European workers hired or sent as replacements may increase the upkeep of all European workers.')
            text_list.append('European workers tend to be more susceptible to attrition but are more accustomed to using modern weaponry.')
            
        elif current_target == 'slave workers':
            text_list.append('Slave workers have a constant upkeep of ' + str(global_manager.get('slave_worker_upkeep')) + ' money each turn.')
            text_list.append('Officers and vehicles require an attached worker unit to perform most actions.')
            text_list.append('Each unit of slave workers purchased or sent as replacements may increase the purchase cost of all slave workers.')
            text_list.append('African workers tend to be less susceptible to attrition but are less accustomed to using modern weaponry.')
            if global_manager.get('effect_manager').effect_active('no_slave_trade_penalty'):
                text_list.append('Your country\'s prolonged involvement with the slave trade will prevent any public opinion penalty from this morally reprehensible act.')
            else:
                text_list.append('Participating in the slave trade is a morally reprehensible act and will be faced with a public opinion penalty.')
            
        elif current_target == 'slums workers':
            text_list.append('African workers have a varying upkeep that is currently ' + str(global_manager.get('african_worker_upkeep')) + ' money each turn.')
            text_list.append('Officers and vehicles require an attached worker unit to perform most actions.')
            text_list.append('There are a limited number of African workers at villages and slums, and hiring any may increase the upkeep of all African workers.')
            text_list.append('Attracting new African workers to your colony through trading consumer goods may decrease the upkeep of all African workers.')
            text_list.append('African workers tend to be less susceptible to attrition but are less accustomed to using modern weaponry.')
            
        elif current_target == 'village workers':
            text_list.append('African workers have a varying upkeep that is currently ' + str(global_manager.get('african_worker_upkeep')) + ' money each turn.')
            text_list.append('Officers and vehicles require an attached worker unit to perform most actions.')
            text_list.append('There are a limited number of African workers at villages and slums, and hiring any may increase the upkeep of all African workers.')
            text_list.append('Attracting new African workers to your colony through trading consumer goods may decrease the upkeep of all African workers.')
            text_list.append('African workers tend to be less susceptible to attrition but are less accustomed to using modern weaponry.')
            
        elif current_target == 'steamship':
            text_list.append('While useless by itself, a steamship crewed by workers can quickly transport units and cargo through coastal waters and between theatres.')
            text_list.append('Crewing a steamship requires an advanced level of technological training, which is generally only available to European workers in this time period.')
            
        elif current_target == 'steamboat':
            text_list.append('While useless by itself, a steamboat crewed by workers can quickly transport units and cargo along rivers.')
            text_list.append('Crewing a steamboat requires a basic level of technological training, which is generally unavailable to slave workers.')
            
        elif current_target == 'train':
            text_list.append('While useless by itself, a train crewed by workers can quickly transport units and cargo through railroads between train stations.')
            text_list.append('Crewing a train requires a basic level of technological training, which is generally unavailable to slave workers.')
        recruitment_list_descriptions[current_target] = text_list

        text = ''
        for current_line in recruitment_list_descriptions[current_target]:
            text += current_line + ' /n /n' #replaces each tooltip list line with newline characters for notification descriptions
        recruitment_string_descriptions[current_target] = text
            
def spawn_beast(global_manager):
    '''
    Description:
        Attempts to spawn a beast at a random part of the map, choosing a tile and then choosing a type of animal that can spawn in that tile. The spawn attepmt fails and does nothing if the chosen tile is next to any player buildings
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    input_dict = {}
    requirements_dict = {}
    requirements_dict['ocean_allowed'] = False
    requirements_dict['allowed_terrains'] = global_manager.get('terrain_list') + ['water']
    requirements_dict['nearby_buildings_allowed'] = True
    spawn_cell = global_manager.get('strategic_map_grid').choose_cell(requirements_dict)
    if spawn_cell.adjacent_to_buildings():
        return() #cancel spawn if beast would spawn near buildings, become less common as colony develops
    terrain_type = spawn_cell.terrain
    
    input_dict['coordinates'] = (spawn_cell.x, spawn_cell.y)
    input_dict['grids'] = [global_manager.get('strategic_map_grid'), global_manager.get('strategic_map_grid').mini_grid]
    input_dict['modes'] = ['strategic']
    input_dict['animal_type'] = random.choice(global_manager.get('terrain_animal_dict')[terrain_type])
    input_dict['adjective'] = random.choice(global_manager.get('animal_adjectives'))
    input_dict['image'] = 'mobs/beasts/' + input_dict['animal_type'] + '.png'
    input_dict['init_type'] = 'beast'
    global_manager.get('actor_creation_manager').create(False, input_dict, global_manager)  

def find_closest_available_worker(destination, global_manager):
    '''
    Description:
        Finds one of the closest African workers and returns its slums or village. Weighted based on the amount available such that a village with more available workers at the same distance is more likely to be chosen
    Input:
        pmob destination: Unit that the worker will be sent to, used as a reference point for distance
    Output:
        slums/village: Returns the slums or village at which the chosen closest worker is located
    '''
    possible_sources = []
    for current_village in global_manager.get('village_list'):
        if current_village.available_workers > 0:
            possible_sources.append(current_village)
    possible_sources += global_manager.get('slums_list')
    
    min_distance = -1 #makes a list of closest sources
    min_distance_sources = []
    for possible_source in possible_sources:
        current_distance = utility.find_object_distance(destination, possible_source)
        if min_distance == -1 or current_distance < min_distance:
            min_distance_sources = [possible_source]
            min_distance = current_distance
        elif min_distance == current_distance:
            min_distance_sources.append(possible_source)

    max_workers = -1 #makes list of closest sources that have the most workers
    max_workers_sources = ['none']
    for possible_source in min_distance_sources:
        current_workers = possible_source.available_workers
        if max_workers == -1 or current_workers > max_workers:
            max_workers_sources = [possible_source]
            max_workers = current_workers
        elif max_workers == current_workers:
            max_workers_sources.append(possible_source)
            
    return(random.choice(max_workers_sources)) #randomly choose from ['none'] or the list of tied closest sources w/ most workers

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
    global_manager.set('ongoing_action', False)
    global_manager.set('ongoing_action_type', 'none')

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
    for current_building in global_manager.get('building_list'):
        if current_building.building_type == 'infrastructure':
            current_building.cell.tile.update_image_bundle()
    
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

def calibrate_actor_info_display(global_manager, info_display, new_actor, override_exempt=False):
    '''
    Description:
        Updates all relevant objects to display a certain mob or tile
    Input:
        global_manager_template global_manager: Object that accesses shared variables
        interface_collection info_display: Collection of interface elements to calibrate to the inputted actor
        string new_actor: The new mob or tile that is displayed
    Output:
        None
    '''
    if info_display == global_manager.get('tile_info_display'):
        for current_same_tile_icon in global_manager.get('same_tile_icon_list'):
            current_same_tile_icon.reset()
        global_manager.set('displayed_tile', new_actor)
        if new_actor != 'none':
            new_actor.select() #plays correct music based on tile selected - slave traders/village/europe music

    elif info_display == global_manager.get('mob_info_display'):
        global_manager.set('displayed_mob', new_actor)
        if new_actor != 'none' and new_actor.images[0].current_cell.tile == global_manager.get('displayed_tile'):
            for current_same_tile_icon in global_manager.get('same_tile_icon_list'):
                current_same_tile_icon.reset()

    elif info_display == global_manager.get('country_info_display'):
        global_manager.set('displayed_country', new_actor)
    info_display.calibrate(new_actor, override_exempt)

def get_migration_destinations(global_manager):
    '''
    Description:
        Gathers and returns a list of all cells to which migration could occur. Migration can occur to tiles with places of employment, like ports, train stations, and resource production facilities
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        cell list: Returns list of all cells to which migration could occur
    '''
    return_list = []
    for current_building in global_manager.get('building_list'):
        if current_building.building_type in ['port', 'train_station', 'resource']:
            if not current_building.cell in return_list:
                if not current_building.damaged:
                    return_list.append(current_building.cell)
    return(return_list)

def get_migration_sources(global_manager):
    '''
    Description:
        Gathers and returns a list of all villages from which migration could occur. Migration can occur from villages with at least 1 available worker
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        village list: Returns list of all villages from which migration could occur
    '''
    return_list = []
    for current_village in global_manager.get('village_list'):
        if current_village.available_workers > 0:
            return_list.append(current_village)
    return(return_list)

def get_num_available_workers(location_types, global_manager):
    '''
    Description:
        Calculates and returns the number of workers currently available in the inputted location type, like how many workers are in slums
    Input:
        string location_types: Types of locations to count workers from, can be 'village', 'slums', or 'all'
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        int: Returns number of workers currently available in the inputted location type
    '''
    num_available_workers = 0
    if not location_types == 'village': #slums or all
        for current_slums in global_manager.get('slums_list'):
            #if current_building.building_type == 'slums':
            num_available_workers += current_slums.available_workers
    if not location_types == 'slums': #village or all
        for current_village in global_manager.get('village_list'):
            num_available_workers += current_village.available_workers
    return(num_available_workers)

def generate_resource_icon(tile, global_manager):
    '''
    Description:
        Generates and returns the correct string image file path based on the resource/village and buildings built in the inputted tile
    Input:
        tile tile: Tile to generate a resource icon for
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        string: Returns string image file path for tile's resource icon
    '''
    small = False
    for building_type in global_manager.get('building_types'):
        if tile.cell.has_building(building_type): #if any building present - villages are buildings but not a building type
            small = True
    if tile.cell.resource == 'natives':
        attached_village = tile.cell.get_building('village')
        if attached_village.population == 0: #0
            key = '0'
        elif attached_village.population <= 3: #1-3
            key = '1'
        elif attached_village.population <= 6: #4-6
            key = '2'
        else: #7-10
            key = '3'
        if attached_village.aggressiveness <= 3: #1-3
            key += '1'
        elif attached_village.aggressiveness <= 6: #4-6
            key += '2'
        else: #7-10
            key += '3'
        if small:
            image_id = 'scenery/resources/natives/small/' + key + '.png'
        else:
            image_id = 'scenery/resources/natives/' + key + '.png'
    else:
        if small:
            image_id = 'scenery/resources/small/' + tile.cell.resource + '.png'
        else:
            image_id = 'scenery/resources/' + tile.cell.resource + '.png'
    return(image_id)

def get_image_variants(base_path, keyword = 'default'):
    '''
    Description:
        Finds and returns a list of all images with the same name format in the same folder, like 'folder/default.png' and 'folder/default1.png'
    Input:
        string base_path: File path of base image, like 'folder/default.png'
        string keyword = 'default': Name format to look for
    Output:
        string list: Returns list of all images with the same name format in the same folder
    '''
    variants = []
    if base_path.endswith('default.png'):
        folder_path = base_path.removesuffix('default.png')
        for file_name in os.listdir('graphics/' + folder_path):
            if file_name.startswith(keyword):
                variants.append(folder_path + file_name)
                continue
            else:
                continue
    else:
        variants.append(base_path)
    return(variants)

def extract_folder_colors(folder_path):
    '''
    Description:
        Iterates through a folder's files and finds the first color in each image, returning that colors RGB values
    Input:
        string folder_path: Folder path to search through, like 'ministers/portraits/hair/colors'
    Output:
        int tuple list: Returns list of (red, green, blue) items, with red, green, and blue being the RGB values of the first color in each respective file
    '''
    colors = []
    for file_name in os.listdir('graphics/' + folder_path):
        current_image = pygame.image.load('graphics/' + folder_path + file_name)
        red, green, blue, alpha = current_image.get_at((0, 0))
        colors.append((red, green, blue))
    return(colors)

def get_slave_traders_strength_modifier(global_manager):
    '''
    Description:
        Calculates and returns the inverse difficulty modifier for actions related to the slave traders, with a positive modifier making rolls easier
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        string/int: Returns slave traders inverse difficulty modifier, or 'none' if the strength is 0
    '''
    strength = global_manager.get('slave_traders_strength')
    if strength == 0:
        strength_modifier = 'none'
    elif strength >= global_manager.get('slave_traders_natural_max_strength') * 2: #>= 20
        strength_modifier = -1
    elif strength >= global_manager.get('slave_traders_natural_max_strength'): #>= 10
        strength_modifier = 0
    else: # < 10
        strength_modifier = 1
    return(strength_modifier)

def set_slave_traders_strength(new_strength, global_manager):
    '''
    Description:
        Sets the strength of the slave traders
    Input:
        int new_strength: New slave traders strength value
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    if new_strength < 0:
        new_strength = 0
    global_manager.set('slave_traders_strength', new_strength)
    if global_manager.has('slave_traders_grid'):
        slave_traders_tile = global_manager.get('slave_traders_grid').cell_list[0].tile
        slave_traders_tile.update_image_bundle()

def generate_group_image_id_list(worker, officer, global_manager):
    left_worker_dict = {
        'image_id': worker.image_dict['default'],
        'size': 0.8,
        'x_offset': -0.28,
        'y_offset': 0.05,
        'level': -2
    }

    right_worker_dict = left_worker_dict.copy()
    right_worker_dict['image_id'] = worker.image_variants[worker.second_image_variant]
    right_worker_dict['x_offset'] *= -1

    if officer.officer_type == 'major':
        if 'soldier' in worker.image_dict:
            soldier = worker.image_dict['soldier']
        else:
            soldier = worker.image_dict['default']
        left_worker_dict['image_id'] = soldier
        left_worker_dict['green_screen'] = global_manager.get('current_country').colors
        right_worker_dict['image_id'] = soldier
        right_worker_dict['green_screen'] = global_manager.get('current_country').colors
    elif officer.officer_type in ['merchant', 'driver']:
        if 'porter' in worker.image_dict:
            porter = worker.image_dict['porter']
        else:
            porter = worker.image_dict['default']
        left_worker_dict['image_id'] = porter
        right_worker_dict['image_id'] = porter

    officer_dict = {
        'image_id': officer.image_dict['default'],
        'size': 0.85,
        'x_offset': 0,
        'y_offset': -0.05,
        'level': -1
    }

    return([left_worker_dict, right_worker_dict, officer_dict])

def generate_group_name(worker, officer, global_manager, add_veteran=False):
    if not officer.officer_type == 'major':
        name = ''
        for character in global_manager.get('officer_group_type_dict')[officer.officer_type]:
            if not character == '_':
                name += character
            else:
                name += ' '
    else: #battalions have special naming convention based on worker type
        if worker.worker_type == 'European':
            name = 'imperial battalion'
        else:
            name = 'colonial battalion'
    if add_veteran and officer.veteran:
        name = 'veteran ' + name
    return(name)

def generate_group_movement_points(worker, officer, global_manager, generate_max=False):
    if generate_max:
        max_movement_points = officer.max_movement_points
        if officer.officer_type == 'driver' and officer.veteran:
            max_movement_points = 6
        return(max_movement_points)
    else:
        max_movement_points = generate_group_movement_points(worker, officer, global_manager, generate_max=True)
        worker_movement_ratio_remaining = worker.movement_points / worker.max_movement_points
        officer_movement_ratio_remaining = officer.movement_points / officer.max_movement_points
        if worker_movement_ratio_remaining > officer_movement_ratio_remaining:
            return(math.floor(max_movement_points * officer_movement_ratio_remaining))
        else:
            return(math.floor(max_movement_points * worker_movement_ratio_remaining))
