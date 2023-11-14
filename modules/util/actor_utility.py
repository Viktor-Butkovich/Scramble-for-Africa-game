#Contains miscellaneous functions relating to actor functionality

import random
import os
import pygame
import math
from . import utility, text_utility
import modules.constants.constants as constants
import modules.constants.status as status

def reset_action_prices():
    '''
    Description:
        Resets the costs of any actions that were increased during the previous turn
    Input:
        None
    Output:
        None
    '''
    for current_action_type in constants.action_types:
        constants.action_prices[current_action_type] = constants.base_action_prices[current_action_type]

def double_action_price(action_type):
    '''
    Description:
        Doubles the price of a certain action type each time it is done, usually for ones that do not require workers
    Input:
        string action_type: Type of action to double the price of
    Output:
        None
    '''
    constants.action_prices[action_type] *= 2

def get_building_cost(constructor, building_type, building_name = 'n/a'):
    '''
    Description:
        Returns the cost of the inputted unit attempting to construct the inputted building
    Input:
        pmob/string constructor: Unit attempting to construct the building, or 'none' if no location/unit type is needed
        string building_type: Type of building to build, like 'infrastructure'
        string building_name = 'n/a': Name of building being built, used to differentiate roads from railroads
    Output:
        int: Returns the cost of the inputted unit attempting to construct the inputted building
    '''
    if building_type == 'infrastructure':
        building_type = building_name.replace(' ', '_') #road, railroad, road_bridge, or railroad_bridge
    if building_type == 'warehouses':
        if constructor in ['none', None]:
            base_price = 5
        else:
            base_price = constructor.images[0].current_cell.get_warehouses_cost()
    else:
        base_price = constants.building_prices[building_type]

    if building_type in ['train', 'steamboat']:
        cost_multiplier = 1
    elif constructor in ['none', None] or not status.strategic_map_grid in constructor.grids:
        cost_multiplier = 1
    else:
        terrain = constructor.images[0].current_cell.terrain
        cost_multiplier = constants.terrain_build_cost_multiplier_dict[terrain]

    return(base_price * cost_multiplier)

def update_descriptions(target = 'all'):
    '''
    Description:
        Updates the descriptions of recruitable units for use in various parts of the program. Updates all units during setup and can target a certain unit to update prices, etc. when the information is needed later in the game.
            Creates list versions for tooltips and string versions for notifications
    Input:
        string target = 'all': Targets a certain unit type, or 'all' by default, to update while minimizing unnecessary calculations
    Output:
        None
    '''
    if target == 'all':
        targets_to_update = constants.recruitment_types + ['slums workers', 'village workers', 'slaves']
        targets_to_update += constants.building_types + ['road', 'railroad', 'road_bridge', 'railroad_bridge']
        targets_to_update += constants.upgrade_types
    else:
        targets_to_update = [target]

    for current_target in targets_to_update:
        list_descriptions = constants.list_descriptions
        string_descriptions = constants.string_descriptions
        text_list = []
        if current_target in constants.officer_types:
            first_line = utility.capitalize(current_target) + 's are controlled by the ' + constants.officer_minister_dict[current_target]
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
            text_list.append('European workers have an upkeep of ' + str(constants.european_worker_upkeep) + ' money each turn.')
            text_list.append('Officers and vehicles require an attached worker unit to perform most actions.')
            text_list.append('Each unit of European workers hired or sent as replacements may increase the upkeep of all European workers.')
            text_list.append('European workers tend to be more susceptible to attrition but are more accustomed to using modern weaponry.')
            
        elif current_target == 'slave workers':
            text_list.append('Slave workers have a constant upkeep of ' + str(constants.slave_worker_upkeep) + ' money each turn.')
            text_list.append('Officers and vehicles require an attached worker unit to perform most actions.')
            text_list.append('Each unit of slave workers purchased or sent as replacements may increase the purchase cost of all slave workers.')
            text_list.append('African workers tend to be less susceptible to attrition but are less accustomed to using modern weaponry.')
            if constants.effect_manager.effect_active('no_slave_trade_penalty'):
                text_list.append('Your country\'s prolonged involvement with the slave trade will prevent any public opinion penalty from this morally reprehensible act.')
            else:
                text_list.append('Participating in the slave trade is a morally reprehensible act and will be faced with a public opinion penalty.')
            
        elif current_target == 'slums workers':
            text_list.append('African workers have a varying upkeep that is currently ' + str(constants.african_worker_upkeep) + ' money each turn.')
            text_list.append('Officers and vehicles require an attached worker unit to perform most actions.')
            text_list.append('There are a limited number of African workers at villages and slums, and hiring any may increase the upkeep of all African workers.')
            text_list.append('Attracting new African workers to your colony through trading consumer goods may decrease the upkeep of all African workers.')
            text_list.append('African workers tend to be less susceptible to attrition but are less accustomed to using modern weaponry.')
            
        elif current_target == 'village workers':
            text_list.append('African workers have a varying upkeep that is currently ' + str(constants.african_worker_upkeep) + ' money each turn.')
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

        elif current_target == 'resource':
            if current_target in status.actions:
                building_name = status.actions[current_target].building_name
                if building_name == 'none':
                    building_name = 'resource production facility'
            else:
                building_name = 'resource production facility'
            text_list.append('A ' + building_name + ' expands the tile\'s warehouse capacity, and each work crew attached to it attempts to produce resources each turn.')
            text_list.append('Upgrades to the facility can increase the maximum number of attached work crews and the number of production attempts each work crew can make. ')

        elif current_target == 'road':
            text_list.append('A road halves movement cost when moving to another tile that has a road or railroad and can later be upgraded to a railroad.')

        elif current_target == 'railroad':
            text_list.append('A railroad, like a road, halves movement cost when moving to another tile that has a road or railroad.')
            text_list.append('It is also required for trains to move and for a train station to be built.')

        elif current_target == 'road_bridge':
            text_list.append('A bridge built on a river tile between 2 land tiles allows movement across the river.')
            text_list.append('A road bridge acts as a road between the tiles it connects and can later be upgraded to a railroad bridge.')

        elif current_target == 'railroad_bridge':
            text_list.append('A bridge built on a river tile between 2 land tiles allows movement across the river.')
            text_list.append('A railroad bridge acts as a railroad between the tiles it connects.')

        elif current_target == 'port':
            text_list.append('A port allows steamboats and steamships to enter the tile, expands the tile\'s warehouse capacity, and attracts local labor brokers.')
            text_list.append('A port adjacent to the ocean allows entry by steamships, while a port adjacent to a river allows entry by and assembly of steamboats.')

        elif current_target == 'train_station':
            text_list.append('A train station is required for a train to exchange cargo and passengers, expands the tile\'s warehouse capacity, and allows assembly of trains.')

        elif current_target == 'trading_post':
            text_list.append('A trading post increases the likelihood that the natives of the local village will be willing to trade and reduces the risk of hostile interactions when trading.')

        elif current_target == 'mission':
            text_list.append('A mission decreases the difficulty of converting the natives of the local village and reduces the risk of hostile interactions when converting.')

        elif current_target == 'fort':
            text_list.append('A fort increases the combat effectiveness of your units standing in this tile.')

        elif current_target == 'scale':
            text_list.append('A resource production facility can have a number of attached work crews equal to its scale')

        elif current_target == 'efficiency':
            text_list.append('A resource production facility\'s attached work crews each make a number of production attempts per turn equal to its efficiency.')

        elif current_target == 'warehouse_level':
            text_list.append('Each of a tile\'s warehouse levels corresponds to 9 inventory capacity.')

        list_descriptions[current_target] = text_list

        text = ''
        for current_line in list_descriptions[current_target]:
            text += current_line + ' /n /n' #replaces each tooltip list line with newline characters for notification descriptions
        string_descriptions[current_target] = text
            
def spawn_beast():
    '''
    Description:
        Attempts to spawn a beast at a random part of the map, choosing a tile and then choosing a type of animal that can spawn in that tile. The spawn attepmt fails and does nothing if the chosen tile is next to any player buildings
    Input:
        None
    Output:
        None
    '''
    spawn_cell = status.strategic_map_grid.choose_cell({
        'ocean_allowed': False,
        'allowed_terrains': constants.terrain_list + ['water'],
        'nearby_buildings_allowed': True
    })
    if spawn_cell.adjacent_to_buildings():
        return() #cancel spawn if beast would spawn near buildings, become less common as colony develops
    terrain_type = spawn_cell.terrain
    animal_type = random.choice(constants.terrain_animal_dict[terrain_type])

    constants.actor_creation_manager.create(False, {
        'coordinates': (spawn_cell.x, spawn_cell.y),
        'grids': [status.strategic_map_grid, status.strategic_map_grid.mini_grid],
        'modes': ['strategic'],
        'animal_type': animal_type,
        'adjective': random.choice(constants.animal_adjectives),
        'image': 'mobs/beasts/' + animal_type + '.png',
        'init_type': 'beast'
    })  

def find_closest_available_worker(destination):
    '''
    Description:
        Finds one of the closest African workers and returns its slums or village. Weighted based on the amount available such that a village with more available workers at the same distance is more likely to be chosen
    Input:
        pmob destination: Unit that the worker will be sent to, used as a reference point for distance
    Output:
        slums/village: Returns the slums or village at which the chosen closest worker is located
    '''
    possible_sources = []
    for current_village in status.village_list:
        if current_village.available_workers > 0:
            possible_sources.append(current_village)
    possible_sources += status.slums_list
    
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

def update_roads():
    '''
    Description:
        Updates the road/railroad connections between tiles when a new one is built
    Input:
        None
    Output:
        None
    '''
    for current_building in status.building_list:
        if current_building.building_type == 'infrastructure':
            current_building.cell.tile.update_image_bundle()

def deselect_all():
    '''
    Description:
        Deselects all units. Currently, the game will only have 1 selected unit at a time and this should be updated.
    Input:
        None
    Output:
        None
    '''
    for current_mob in status.mob_list:
        if current_mob.selected:
            current_mob.selected = False
    
def get_random_ocean_coordinates():
    '''
    Description:
        Returns a random set of coordinates from the ocean section of the strategic map
    Input:
        None
    Output:
        int tuple: Two values representing x and y coordinates
    '''
    start_x = random.randrange(0, status.strategic_map_grid.coordinate_width)
    start_y = 0
    return(start_x, start_y)

def calibrate_actor_info_display(info_display, new_actor, override_exempt=False):
    '''
    Description:
        Updates all relevant objects to display a certain mob or tile
    Input:
        interface_collection info_display: Collection of interface elements to calibrate to the inputted actor
        actor new_actor: The new mob or tile that is displayed
        boolean override_exempt=False: Whether to calibrate interface elements that are normally exempt, such as the reorganization interface
    Output:
        None
    '''
    if new_actor == 'none':
        print(0/0)
    if info_display == status.tile_info_display:
        for current_same_tile_icon in status.same_tile_icon_list:
            current_same_tile_icon.reset()
        status.displayed_tile = new_actor
        if new_actor:
            new_actor.select() #plays correct music based on tile selected - slave traders/village/europe music

    elif info_display == status.mob_info_display:
        status.displayed_mob = new_actor
        if new_actor and new_actor.images[0].current_cell.tile == status.displayed_tile:
            for current_same_tile_icon in status.same_tile_icon_list:
                current_same_tile_icon.reset()

    elif info_display == status.country_info_display:
        status.displayed_country = new_actor

    target = 'none'
    if new_actor:
        target = new_actor
    info_display.calibrate(target, override_exempt)

def get_migration_destinations():
    '''
    Description:
        Gathers and returns a list of all cells to which migration could occur. Migration can occur to tiles with places of employment, like ports, train stations, and resource production facilities
    Input:
        None
    Output:
        cell list: Returns list of all cells to which migration could occur
    '''
    return_list = []
    for current_building in status.building_list:
        if current_building.building_type in ['port', 'train_station', 'resource']:
            if not current_building.cell in return_list:
                if not current_building.damaged:
                    return_list.append(current_building.cell)
    return(return_list)

def get_migration_sources():
    '''
    Description:
        Gathers and returns a list of all villages from which migration could occur. Migration can occur from villages with at least 1 available worker
    Input:
        None
    Output:
        village list: Returns list of all villages from which migration could occur
    '''
    return_list = []
    for current_village in status.village_list:
        if current_village.available_workers > 0:
            return_list.append(current_village)
    return(return_list)

def get_num_available_workers(location_types):
    '''
    Description:
        Calculates and returns the number of workers currently available in the inputted location type, like how many workers are in slums
    Input:
        string location_types: Types of locations to count workers from, can be 'village', 'slums', or 'all'
    Output:
        int: Returns number of workers currently available in the inputted location type
    '''
    num_available_workers = 0
    if not location_types == 'village': #slums or all
        for current_slums in status.slums_list:
            #if current_building.building_type == 'slums':
            num_available_workers += current_slums.available_workers
    if not location_types == 'slums': #village or all
        for current_village in status.village_list:
            num_available_workers += current_village.available_workers
    return(num_available_workers)

def generate_resource_icon(tile):
    '''
    Description:
        Generates and returns the correct string image file path based on the resource/village and buildings built in the inputted tile
    Input:
        tile tile: Tile to generate a resource icon for
    Output:
        string/list: Returns string or list image id for tile's resource icon
    '''
    small = False
    for building_type in constants.building_types:
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

def get_slave_traders_strength_modifier():
    '''
    Description:
        Calculates and returns the inverse difficulty modifier for actions related to the slave traders, with a positive modifier making rolls easier
    Input:
        None
    Output:
        string/int: Returns slave traders inverse difficulty modifier, or 'none' if the strength is 0
    '''
    strength = constants.slave_traders_strength
    if strength == 0:
        strength_modifier = 'none'
    elif strength >= constants.slave_traders_natural_max_strength * 2: #>= 20
        strength_modifier = -1
    elif strength >= constants.slave_traders_natural_max_strength: #>= 10
        strength_modifier = 0
    else: # < 10
        strength_modifier = 1
    return(strength_modifier)

def set_slave_traders_strength(new_strength):
    '''
    Description:
        Sets the strength of the slave traders
    Input:
        int new_strength: New slave traders strength value
    Output:
        None
    '''
    if new_strength < 0:
        new_strength = 0
    constants.slave_traders_strength = new_strength
    if status.slave_traders_grid != None:
        slave_traders_tile = status.slave_traders_grid.cell_list[0][0].tile
        slave_traders_tile.update_image_bundle()

def generate_unit_component_image_id(base_image, component, to_front=False):
    '''
    Description:
        Generates and returns an image id dict for the inputted base_image moved to the inputted section of the frame, like 'group left' for a group's left worker
    Input:
        string base_image: Base image file path to display
        string component: Section of the frame to display base image in, like 'group left'
        boolean to_front=False: Whether image level/layer should be a positive or negative
    Output:
        dict: Returns generated image id dict
    '''
    return_dict = {}
    if component in ['group left', 'group right']:
        return_dict = {
            'image_id': base_image,
            'size': 0.8,
            'x_offset': -0.28,
            'y_offset': 0.05,
            'level': -2
        }
    elif component in ['left', 'right']:
        return_dict = {
            'image_id': base_image,
            'size': 0.85,
            'x_offset': -0.25,
            'y_offset': 0,
            'level': -1
        }
    else:
        return_dict = {
            'image_id': base_image,
            'size': 0.85,
            'x_offset': 0,
            'y_offset': -0.05,
            'level': -1
        }
    if component.endswith('right'):
        return_dict['x_offset'] *= -1
    if to_front:
        return_dict['level'] *= -1
    return(return_dict)

def generate_group_image_id_list(worker, officer):
    '''
    Description:
        Generates and returns an image id list that a group formed from the inputted worker and officer would have
    Input:
        worker worker: Worker to use for group image
        officer officer: Officer to use for group image
    Output:
        list: Returns image id list of dictionaries for each part of the group image
    '''
    left_worker_dict = generate_unit_component_image_id(worker.image_dict['default'], 'group left')
    right_worker_dict = generate_unit_component_image_id(worker.image_variants[worker.second_image_variant], 'group right')

    if officer.officer_type == 'major':
        if 'soldier' in worker.image_dict:
            soldier = worker.image_dict['soldier']
        else:
            soldier = worker.image_dict['default']
        left_worker_dict['image_id'] = soldier
        left_worker_dict['green_screen'] = status.current_country.colors
        right_worker_dict['image_id'] = soldier
        right_worker_dict['green_screen'] = status.current_country.colors
    elif officer.officer_type in ['merchant', 'driver']:
        if 'porter' in worker.image_dict:
            porter = worker.image_dict['porter']
        else:
            porter = worker.image_dict['default']
        left_worker_dict['image_id'] = porter
        right_worker_dict['image_id'] = porter

    officer_dict = generate_unit_component_image_id(officer.image_dict['default'], 'center')

    return([left_worker_dict, right_worker_dict, officer_dict])

def generate_group_name(worker, officer, add_veteran=False):
    '''
    Description:
        Generates and returns the name that a group formed from the inputted worker and officer would have
    Input:
        worker worker: Worker to use for group name
        officer officer: Officer to use for group name
        boolean add_veteran=False: Whether veteran should be added to the start of the name if the officer is a veteran - while a mock group needs veteran to be added, a
            group actually being created will add veteran to its name automatically when it promotes
    Output:
        list: Returns image id list of dictionaries for each part of the group image
    '''
    if not officer.officer_type == 'major':
        name = ''
        for character in constants.officer_group_type_dict[officer.officer_type]:
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

def generate_group_movement_points(worker, officer, generate_max=False):
    '''
    Description:
        Generates and returns either the current or maximum movement points that a group created from the inputted worker and officer would have
    Input:
        worker worker: Worker to use for group
        officer officer: Officer to use for group
        boolean generate_max=False: Whether to return the group's current or maximum number of movement points
    Output:
        list: Returns image id list of dictionaries for each part of the group image
    '''
    if generate_max:
        max_movement_points = officer.max_movement_points
        if officer.officer_type == 'driver' and officer.veteran:
            max_movement_points = 6
        return(max_movement_points)
    else:
        max_movement_points = generate_group_movement_points(worker, officer, generate_max=True)
        worker_movement_ratio_remaining = worker.movement_points / worker.max_movement_points
        officer_movement_ratio_remaining = officer.movement_points / officer.max_movement_points
        if worker_movement_ratio_remaining > officer_movement_ratio_remaining:
            return(math.floor(max_movement_points * officer_movement_ratio_remaining))
        else:
            return(math.floor(max_movement_points * worker_movement_ratio_remaining))

def select_interface_tab(tabbed_collection, target_tab):
    '''
    Description:
        Selects the inputted interface tab from the inputted tabbed collection, such as selecting the inventory tab from the mob tabbed collection
    Input:
        interface_collection tabbed_collection: Tabbed collection to select from
        interface_collection target_tab: Tab to select
    Output:
        None
    '''
    if not target_tab.showing:
        for tab_button in tabbed_collection.tabs_collection.members:
            if tab_button.linked_element == target_tab:
                tab_button.on_click()
                continue
