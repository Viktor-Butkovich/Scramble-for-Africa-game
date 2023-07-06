import pygame
import time
import os
import logging
import json

import modules.scaling as scaling
import modules.images as images
import modules.game_transitions as game_transitions
import modules.data_managers as data_managers
import modules.actor_display_tools.images as actor_display_images
import modules.mouse_followers as mouse_followers
import modules.save_load_tools as save_load_tools
import modules.actor_creation_tools as actor_creation_tools
import modules.actor_utility as actor_utility
import modules.countries as countries
import modules.effects as effects

def fundamental_setup(global_manager):
    '''
    Description:
        Initializes pygame and most manager objects and defines screen size, times, fonts, and colors
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    pygame.init()
    pygame.mixer.init()
    global_manager.set('startup_complete', False)
    global_manager.set('sound_manager', data_managers.sound_manager_template(global_manager))
    #global_manager.get('sound_manager').play_music('La Marseillaise 1')
    global_manager.set('save_load_manager', save_load_tools.save_load_manager_template(global_manager))
    global_manager.set('flavor_text_manager', data_managers.flavor_text_manager_template(global_manager))
    global_manager.set('input_manager', data_managers.input_manager_template(global_manager))
    global_manager.set('actor_creation_manager', actor_creation_tools.actor_creation_manager_template())

    global_manager.set('europe_grid', 'none')
    resolution_finder = pygame.display.Info()
    global_manager.set('default_display_width', 1728) #all parts of game made to be at default_display and scaled to display
    global_manager.set('default_display_height', 972)
    global_manager.set('display_width', resolution_finder.current_w - round(global_manager.get('default_display_width')/10))
    global_manager.set('display_height', resolution_finder.current_h - round(global_manager.get('default_display_height')/10))
    
    start_time = time.time()
    global_manager.set('loading', True)
    global_manager.set('loading_start_time', start_time)
    global_manager.set('previous_turn_time', start_time)
    global_manager.set('start_time', start_time)
    global_manager.set('current_time', start_time)
    global_manager.set('last_selection_outline_switch', start_time)
    global_manager.set('mouse_moved_time', start_time)
    global_manager.set('end_turn_wait_time', 0.8)
    global_manager.set('event_manager', data_managers.event_manager_template(global_manager))

    if global_manager.get('effect_manager').effect_active('track_fps'):
        global_manager.set('fps', 0)
        global_manager.set('frames_this_second', 0)
        global_manager.set('last_fps_update', time.time())

    global_manager.set('font_name', 'times new roman')
    global_manager.set('default_font_size', 15)
    global_manager.set('font_size', scaling.scale_height(15, global_manager))
    global_manager.set('myfont', pygame.font.SysFont(global_manager.get('font_name'), global_manager.get('font_size')))

    global_manager.set('default_music_volume', 1)

    global_manager.set('game_display', pygame.display.set_mode((global_manager.get('display_width'), global_manager.get('display_height'))))

    pygame.display.set_caption('SFA')
    global_manager.set('color_dict',
        {
        'black': (0, 0, 0),
        'white': (255, 255, 255),
        'light gray': (230, 230, 230),
        'gray': (190, 190, 190),
        'dark gray': (150, 150, 150),
        'bright red': (255, 0, 0),
        'red': (200, 0, 0),
        'dark red': (150, 0, 0),
        'bright green': (0, 255, 0),
        'green': (0, 200, 0),
        'dark green': (0, 150, 0),
        'green': (0, 200, 0),
        'dark green': (0, 150, 0),
        'bright blue': (0, 0, 255),
        'blue': (0, 0, 200),
        'dark blue': (0, 0, 150),
        'yellow': (255, 255, 0),
        'brown': (85, 53, 22),
        'blonde': (188, 175, 123),
        'purple': (127, 0, 170)
        }
    )
    global_manager.set('green_screen_colors', 
        [
        (62, 82, 82),
        (70, 70, 92),
        (110, 107, 3)
        ]
    )
def misc_setup(global_manager):
    '''
    Description:
        Initializes object lists, current object variables, current status booleans, and other misc. values
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    global_manager.set('rendered_images', {})
    global_manager.get('game_display').fill(global_manager.get('color_dict')['white'])
    global_manager.set('button_list', [])
    global_manager.set('recruitment_button_list', [])
    global_manager.set('current_instructions_page', 'none')
    global_manager.set('current_dice_rolling_notification', 'none')
    global_manager.set('current_instructions_page_index', 0)
    global_manager.set('instructions_list', [])
    #page 1
    instructions_message = 'Placeholder instructions, use += to add'
    global_manager.get('instructions_list').append(instructions_message)

    global_manager.set('minister_list', [])
    global_manager.set('available_minister_list', [])
    global_manager.set('country_list', [])
    global_manager.set('flag_icon_list', [])
    global_manager.set('grid_list', [])
    global_manager.set('grid_types_list', ['strategic_map_grid', 'europe_grid', 'slave_traders_grid'])
    global_manager.set('abstract_grid_list', [])
    global_manager.set('text_list', [])
    global_manager.set('image_list', [])
    global_manager.set('free_image_list', [])
    global_manager.set('minister_image_list', [])
    global_manager.set('available_minister_portrait_list', [])
    global_manager.set('country_selection_image_list', [])
    global_manager.set('background_image_list', [])
    global_manager.set('actor_list', [])
    global_manager.set('mob_list', [])
    global_manager.set('pmob_list', [])
    global_manager.set('npmob_list', [])
    global_manager.set('beast_list', [])
    global_manager.set('village_list', [])
    global_manager.set('building_list', [])
    global_manager.set('slums_list', [])
    global_manager.set('resource_building_list', [])
    global_manager.set('officer_list', [])
    global_manager.set('worker_list', [])
    global_manager.set('loan_list', [])
    global_manager.set('attacker_queue', [])
    global_manager.set('enemy_turn_queue', [])
    global_manager.set('player_turn_queue', [])
    global_manager.set('group_list', [])
    global_manager.set('tile_list', [])
    global_manager.set('exploration_mark_list', [])
    global_manager.set('overlay_tile_list', [])
    global_manager.set('notification_list', [])
    global_manager.set('label_list', [])
    global_manager.set('ordered_collection_list', [])

    global_manager.set('displayed_mob', 'none')
    #global_manager.set('mob_ordered_label_list', [])

    global_manager.set('displayed_tile', 'none')
    #global_manager.set('tile_ordered_label_list', [])

    global_manager.set('displayed_minister', 'none')
    #global_manager.set('minister_ordered_label_list', [])

    global_manager.set('displayed_country', 'none')
    #global_manager.set('country_ordered_label_list', [])

    global_manager.set('displayed_defense', 'none')
    global_manager.set('displayed_prosecution', 'none')

    global_manager.set('dice_list', [])
    global_manager.set('dice_roll_minister_images', [])
    global_manager.set('combatant_images', [])
    pygame.key.set_repeat(300, 200)
    global_manager.set('crashed', False)
    global_manager.set('lmb_down', False)
    global_manager.set('rmb_down', False)
    global_manager.set('mmb_down', False)
    global_manager.set('typing', False)
    global_manager.set('message', '')
    #global_manager.set('show_grid_lines', True)
    global_manager.set('show_text_box', True)
    global_manager.set('show_selection_outlines', True)
    global_manager.set('show_minimap_outlines', True)
    global_manager.set('making_choice', False)
    global_manager.set('loading_save', False)
    global_manager.set('player_turn', True)
    global_manager.set('enemy_combat_phase', False)
    global_manager.set('choosing_destination', False)
    global_manager.set('choosing_destination_info_dict', {})
    global_manager.set('choosing_advertised_commodity', False)
    global_manager.set('choosing_advertised_commodity_info_dict', {})
    global_manager.set('drawing_automatic_route', False)
    global_manager.set('prosecution_bribed_judge', False)

    global_manager.set('ongoing_action', False)
    global_manager.set('ongoing_action_type', 'none')
    global_manager.set('game_over', False)

    global_manager.set('r_shift', 'up')
    global_manager.set('l_shift', 'up')
    global_manager.set('capital', False)
    global_manager.set('r_ctrl', 'up')
    global_manager.set('l_ctrl', 'up')
    global_manager.set('ctrl', 'up')
    old_mouse_x, old_mouse_y = pygame.mouse.get_pos()#used in tooltip drawing timing
    global_manager.set('old_mouse_x', old_mouse_x)
    global_manager.set('old_mouse_y', old_mouse_y)
    global_manager.set('available_minister_left_index', -2) #so that first index is in middle
    global_manager.set('loading_image', images.loading_image_template('misc/loading.png', global_manager))
    global_manager.set('current_game_mode', 'none')

    strategic_background_image = images.free_image('misc/background.png', (0, 0), global_manager.get('display_width'), global_manager.get('display_height'), ['strategic', 'europe', 'main_menu', 'ministers', 'trial', 'new_game_setup'], global_manager)
    global_manager.get('background_image_list').append(strategic_background_image)
    strategic_grid_height = 300
    strategic_grid_width = 320
    mini_grid_height = 600
    mini_grid_width = 640

    global_manager.set('minimap_grid_origin_x', global_manager.get('default_display_width') - (mini_grid_width + 100))

    global_manager.set('europe_grid_x', global_manager.get('default_display_width') - (strategic_grid_width + 100 + 120 + 25)) 
    #100 for gap on right side of screen, 120 for width of europe grid, 25 for gap between europe and strategic grids
    global_manager.set('europe_grid_y', global_manager.get('default_display_height') - (strategic_grid_height + 25))

    global_manager.set('mob_ordered_list_start_y', 0)
    global_manager.set('tile_ordered_list_start_y', 0)
    global_manager.set('minister_ordered_list_start_y', 0)

    global_manager.set('current_game_mode', 'none') #set game mode only works if current game mode is defined and not the same as the new game mode
    global_manager.set('current_country', 'none') #current country needs to be defined for music to start playing correctly on set game mode
    game_transitions.set_game_mode('main_menu', global_manager)
    global_manager.set('previous_game_mode', 'main_menu') #after set game mode, both previous and current game modes should be main_menu

    global_manager.set('mouse_follower', mouse_followers.mouse_follower(global_manager))

    global_manager.set('building_types', ['resource', 'port', 'infrastructure', 'train_station', 'trading_post', 'mission', 'fort', 'slums', 'warehouses'])

    global_manager.set('notification_manager', data_managers.notification_manager_template(global_manager))

    global_manager.set('current_advertised_commodity', 'none')
    global_manager.set('current_sound_file_index', 0)

    width = 15
    height = 16
    global_manager.set('strategic_map_width', width)
    global_manager.set('strategic_map_height', height)

    global_manager.set('SONG_END_EVENT', pygame.USEREVENT+1)
    pygame.mixer.music.set_endevent(global_manager.get('SONG_END_EVENT'))

def terrains_setup(global_manager):
    '''
    Description:
        Defines terrains and beasts
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    terrain_list = ['clear', 'mountain', 'hills', 'jungle', 'swamp', 'desert']
    global_manager.set('terrain_list', terrain_list)
    global_manager.set('terrain_colors',
        {
        'clear': (150, 200, 104),
        'hills': (50, 205, 50),
        'jungle': (0, 100, 0),
        'water': (0, 0, 200),
        'mountain': (100, 100, 100),
        'swamp': (100, 100, 50),
        'desert': (255, 248, 104),
        'none': (0, 0, 0)
        }
    )
    global_manager.set('terrain_animal_dict',
        {
        'clear': ['lion', 'bull elephant', 'Cape buffalo'],
        'hills': ['gorilla', 'Cape buffalo', 'hippopotamus'],
        'jungle': ['gorilla', 'crocodile', 'leopard'],
        'water': ['crocodile', 'hippopotamus', 'leopard'],
        'mountain': ['lion', 'gorilla', 'leopard'],
        'swamp': ['bull elephant', 'crocodile', 'hippopotamus'],
        'desert': ['lion', 'bull elephant', 'Cape buffalo']
        }
    )
    global_manager.set('animal_terrain_dict',
        {
        'lion': ['clear', 'desert', 'mountain'],
        'bull elephant': ['clear', 'swamp', 'desert'],
        'Cape buffalo': ['clear', 'hills', 'desert'],
        'crocodile': ['water', 'swamp', 'jungle'],
        'hippopotamus': ['water', 'swamp', 'hills'],
        'gorilla': ['mountain', 'jungle', 'hills'],
        'leopard': ['jungle', 'mountain', 'water']
        }
    )
    global_manager.set('animal_adjectives', ['man-eating', 'bloodthirsty', 'rampaging', 'giant', 'ravenous', 'ferocious', 'king', 'lurking', 'spectral', 'infernal'])
    global_manager.set('terrain_movement_cost_dict',
        {
        'clear': 1,
        'hills': 2,
        'jungle': 3,
        'water': 1,
        'mountain': 3,
        'swamp': 3,
        'desert': 2
        }
    )
    global_manager.set('terrain_build_cost_multiplier_dict',
        {
        'clear': 1,
        'hills': 2,
        'jungle': 3,
        'water': 1,
        'mountain': 3,
        'swamp': 3,
        'desert': 2
        }
    )
    global_manager.set('terrain_variant_dict', {})
    for current_terrain in (global_manager.get('terrain_list') + ['ocean_water', 'river_water']):
        current_index = 0
        while os.path.exists('graphics/scenery/terrain/' + current_terrain + '_' + str(current_index) + '.png'):
            current_index += 1
        current_index -= 1 #back up from index that didn't work
        global_manager.get('terrain_variant_dict')[current_terrain] = current_index + 1 #number of variants, variants in format 'mountain_0', 'mountain_1', etc.

def commodities_setup(global_manager):
    '''
    Description:
        Defines commodities with associated buildings and icons, along with buildings
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    global_manager.set('commodity_types', ['consumer goods', 'coffee', 'copper', 'diamond', 'exotic wood', 'fruit', 'gold', 'iron', 'ivory', 'rubber'])
    global_manager.set('collectable_resources', ['coffee', 'copper', 'diamond', 'exotic wood', 'fruit', 'gold', 'iron', 'ivory', 'rubber'])
    global_manager.set('commodity_prices', {})
    global_manager.set('sold_commodities', {})

    for current_commodity in global_manager.get('commodity_types'):
        global_manager.get('commodity_prices')[current_commodity] = 0
        global_manager.get('sold_commodities')[current_commodity] = 0

    global_manager.set('commodities_produced', {})

    for current_commodity in global_manager.get('collectable_resources'):
        global_manager.get('commodities_produced')[current_commodity] = 0

    global_manager.set('resource_building_dict',
        {
        'coffee': 'buildings/plantation.png',
        'copper': 'buildings/mine.png',
        'diamond': 'buildings/mine.png',
        'exotic wood': 'buildings/plantation.png',
        'fruit': 'buildings/plantation.png',
        'gold': 'buildings/mine.png',
        'iron': 'buildings/mine.png',
        'ivory': 'buildings/camp.png',
        'rubber': 'buildings/plantation.png',
        }
    )
    global_manager.set('resource_building_button_dict',
        {
        'coffee': 'scenery/resources/production/coffee.png',
        'copper': 'scenery/resources/production/copper.png',
        'diamond': 'scenery/resources/production/diamond.png',
        'exotic wood': 'scenery/resources/production/exotic wood.png',
        'fruit': 'scenery/resources/production/fruit.png',
        'gold': 'scenery/resources/production/gold.png',
        'iron': 'scenery/resources/production/iron.png',
        'ivory': 'scenery/resources/production/ivory.png',
        'rubber': 'scenery/resources/production/rubber.png',
        'none': 'scenery/resources/production/none.png',
        }
    )

    for current_commodity in global_manager.get('commodity_types'):
        global_manager.set(current_commodity + ' buy button', 'none')

    global_manager.set('resource_types', global_manager.get('commodity_types') + ['natives'])

def ministers_setup(global_manager):
    '''
    Description:
        Defines minister positions, backgrounds, and associated units
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    global_manager.set('background_status_dict', {
        'lowborn': 1,
        'banker': 2,
        'merchant': 2,
        'lawyer': 2,
        'army officer': 2,
        'naval officer': 2,
        'priest': 2,
        'preacher': 2,
        'natural scientist': 2, 
        'doctor': 2,
        'industrialist': 3,
        'aristocrat': 3,
        'politician': 3,
        'business magnate': 4,
        'royal heir': 4
        }
    )

    global_manager.set('background_skills_dict', {
        'lowborn': ['none'],
        'banker': ['trade'],
        'merchant': ['trade'],
        'lawyer': ['prosecution'],
        'army officer': ['military'],
        'naval officer': ['transportation'],
        'priest': ['religion'],
        'preacher': ['religion'],
        'natural scientist': ['exploration'],
        'doctor': ['random'],
        'industrialist': ['construction', 'production', 'transportation'],
        'aristocrat': ['none', 'random'],
        'politician': ['none', 'random'],
        'business magnate': ['construction', 'production', 'transportation'],
        'royal heir': ['none', 'random']
        }
    )

    global_manager.set('skill_types', ['military', 'religion', 'trade', 'exploration', 'construction', 'production', 'transportation', 'prosecution'])
    global_manager.set('minister_types', ['General', 'Bishop', 'Minister of Trade', 'Minister of Geography', 'Minister of Engineering', 'Minister of Production', 'Minister of Transportation', 'Prosecutor'])
    global_manager.set('type_minister_dict',
        {
        'military': 'General',
        'religion': 'Bishop',
        'trade': 'Minister of Trade',
        'exploration': 'Minister of Geography',
        'construction': 'Minister of Engineering',
        'production': 'Minister of Production',
        'transportation': 'Minister of Transportation',
        'prosecution': 'Prosecutor'
        }
    )
    global_manager.set('minister_type_dict',
        {
        'General': 'military',
        'Bishop': 'religion',
        'Minister of Trade': 'trade',
        'Minister of Geography': 'exploration',
        'Minister of Engineering': 'construction',
        'Minister of Production': 'production',
        'Minister of Transportation': 'transportation',
        'Prosecutor': 'prosecution'
        }
    )
    global_manager.set('current_ministers', {})
    for current_minister_type in global_manager.get('minister_types'):
        global_manager.get('current_ministers')[current_minister_type] = 'none'

    minister_portraits = [] #put all images in graphics/minister/portraits folder in list
    for file_name in os.listdir('graphics/ministers/portraits'):
        if file_name.endswith('.png'): 
            minister_portraits.append('ministers/portraits/' + file_name)
            continue
        else:
            continue
    global_manager.set('minister_portraits', minister_portraits)


    global_manager.set('officer_types', ['explorer', 'hunter', 'engineer', 'driver', 'foreman', 'merchant', 'evangelist', 'major']) #change to driver
    global_manager.set('officer_group_type_dict',
        {
        'explorer': 'expedition',
        'hunter': 'safari',
        'engineer': 'construction_gang',
        'driver': 'porters',
        'foreman': 'work_crew',
        'merchant': 'caravan',
        'evangelist': 'missionaries',
        'major': 'battalion'
        }
    )

    type_minister_dict = global_manager.get('type_minister_dict')
    global_manager.set('officer_minister_dict',
        {
        'explorer': type_minister_dict['exploration'],
        'hunter': type_minister_dict['exploration'],
        'engineer': type_minister_dict['construction'],
        'driver': type_minister_dict['transportation'],
        'foreman': type_minister_dict['production'],
        'merchant': type_minister_dict['trade'],
        'evangelist': type_minister_dict['religion'],
        'major': type_minister_dict['military']
        }
    )

    global_manager.set('group_minister_dict',
        {
        'expedition': type_minister_dict['exploration'],
        'safari': type_minister_dict['exploration'],
        'construction_gang': type_minister_dict['construction'],
        'porters': type_minister_dict['transportation'],
        'work_crew': type_minister_dict['production'],
        'caravan': type_minister_dict['trade'],
        'missionaries': type_minister_dict['religion'],
        'battalion': type_minister_dict['military']
        }
    )
    global_manager.set('minister_limit', 15)

def countries_setup(global_manager):
    '''
    Description:
        Defines countries with associated passive effects and background, name, and unit sets
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    global_manager.set('country_specific_units', ['major'])
    global_manager.set('current_country', 'none')
    global_manager.set('current_country_name', 'none')

    #25 backgrounds by default
    default_weighted_backgrounds = [
        'lowborn', 'lowborn', 'lowborn', 'lowborn', 'lowborn', 'lowborn', 'lowborn', 'lowborn', 'lowborn', 'lowborn',
        'banker',
        'merchant',
        'lawyer',
        'industrialist', 'industrialist', 'industrialist', 'industrialist', 'industrialist', 'industrialist',
        'natural scientist',
        'doctor',
        'politician', 'politician',
        'army officer',
        'naval officer',
        ]

    #each country adds 18 backgrounds for what is more common in that country - half middle, half upper class
    british_weighted_backgrounds = default_weighted_backgrounds + [
        'merchant',
        'lawyer',
        'natural scientist',
        'doctor',
        'naval officer', 'naval officer', 'naval officer',
        'preacher', 'preacher',
        'aristocrat', 'aristocrat', 'aristocrat', 'aristocrat', 'aristocrat', 'aristocrat', 'aristocrat', 'aristocrat',
        'royal heir',
        ]
    british_country_effect = effects.effect('british_country_modifier', 'advertising_campaign_plus_modifier', global_manager)
    british_input_dict = {
        'name': 'Britain',
        'adjective': 'british',
        'government_type_adjective': 'royal',
        'religion': 'protestant',
        'allow_particles': False,
        'aristocratic_particles': False,
        'allow_double_last_names': False,
        'background_set': british_weighted_backgrounds,
        'country_effect': british_country_effect,
        'music_list': ['Rule Britannia']
    }
    global_manager.set('Britain', countries.country(british_input_dict, global_manager))

    french_weighted_backgrounds = default_weighted_backgrounds + [
        'merchant',
        'lawyer',
        'natural scientist',
        'doctor', 'doctor',
        'naval officer',
        'army officer',
        'priest', 'priest',
        'politician', 'politician', 'politician', 'politician', 'politician', 'politician',
        'industrialist', 'industrialist', 
        'business magnate',
        ]
    french_country_effect = effects.effect('french_country_modifier', 'conversion_plus_modifier', global_manager)
    french_input_dict = {
        'name': 'France',
        'adjective': 'french',
        'government_type_adjective': 'national',
        'religion': 'catholic',
        'allow_particles': True,
        'aristocratic_particles': False,
        'allow_double_last_names': True,
        'background_set': french_weighted_backgrounds,
        'country_effect': french_country_effect,
        'music_list': ['La Marseillaise'],
        'has_aristocracy': False
    }
    global_manager.set('France', countries.country(french_input_dict, global_manager))

    german_weighted_backgrounds = default_weighted_backgrounds + [
        'merchant',
        'lawyer',
        'natural scientist',
        'doctor',
        'army officer', 'army officer', 'army officer',
        'preacher', 'preacher',
        'aristocrat', 'aristocrat', 'aristocrat', 'aristocrat', 'aristocrat', 'aristocrat', 'aristocrat', 'aristocrat',
        'royal heir',
        ]
    german_country_effect = effects.effect('german_country_modifier', 'attack_plus_modifier', global_manager)
    german_input_dict = {
        'name': 'Germany',
        'adjective': 'german',
        'government_type_adjective': 'imperial',
        'religion': 'protestant',
        'allow_particles': True,
        'aristocratic_particles': True,
        'allow_double_last_names': False,
        'background_set': german_weighted_backgrounds,
        'country_effect': german_country_effect,
        'music_list': ['Das lied der deutschen']
    }
    global_manager.set('Germany', countries.country(german_input_dict, global_manager))

    belgian_weighted_backgrounds = default_weighted_backgrounds + [
        'merchant',
        'lawyer',
        'natural scientist',
        'doctor',
        'army officer', 'army officer',
        'naval officer',
        'priest', 'priest',
        'aristocrat', 'aristocrat', 'aristocrat', 'aristocrat', 'aristocrat', 'aristocrat', 'aristocrat', 'aristocrat',
        'royal heir',
        ]
    belgian_country_effect = effects.effect('belgian_country_modifier', 'slave_capture_plus_modifier', global_manager)
    belgian_input_dict = {
        'name': 'Belgium',
        'adjective': 'belgian',
        'government_type_adjective': 'royal',
        'religion': 'catholic',
        'background_set': belgian_weighted_backgrounds,
        'country_effect': belgian_country_effect,
        'music_list': []
    }
    global_manager.set('Belgium', countries.hybrid_country(belgian_input_dict, global_manager)) 

    portuguese_weighted_backgrounds = default_weighted_backgrounds + [
        'merchant',
        'lawyer',
        'natural scientist', 'natural scientist',
        'doctor',
        'naval officer', 'naval officer',
        'priest', 'priest',
        'aristocrat', 'aristocrat', 'aristocrat', 'aristocrat', 'aristocrat', 'aristocrat', 'aristocrat', 'aristocrat',
        'royal heir',
        ]
    portuguese_country_effect = effects.effect('portuguese_country_modifier', 'no_slave_trade_penalty', global_manager)
    portuguese_input_dict = {
        'name': 'Portugal',
        'adjective': 'portuguese',
        'government_type_adjective': 'royal',
        'religion': 'catholic',
        'allow_particles': True,
        'aristocratic_particles': False,
        'allow_double_last_names': False,
        'background_set': portuguese_weighted_backgrounds,
        'country_effect': portuguese_country_effect,
        'music_list': ['Portuguese theme']
    }
    global_manager.set('Portugal', countries.country(portuguese_input_dict, global_manager))

    italian_weighted_backgrounds = default_weighted_backgrounds + [
        'merchant',
        'lawyer', 'lawyer',
        'natural scientist',
        'doctor',
        'army officer',
        'naval officer',
        'priest', 'priest',
        'aristocrat', 'aristocrat', 'aristocrat', 'aristocrat', 'aristocrat', 'aristocrat', 'aristocrat', 'aristocrat',
        'royal heir',
        ]
    italian_country_effect = effects.effect('italian_country_modifier', 'attack_minus_modifier', global_manager)
    italian_input_dict = {
        'name': 'Italy',
        'adjective': 'italian',
        'government_type_adjective': 'royal',
        'religion': 'catholic',
        'allow_particles': True,
        'aristocratic_particles': True,
        'allow_double_last_names': False,
        'background_set': italian_weighted_backgrounds,
        'country_effect': italian_country_effect,
        'music_list': ['Prince of Tuscany']
    }
    global_manager.set('Italy', countries.country(italian_input_dict, global_manager)) 
    
def transactions_setup(global_manager):
    '''
    Description:
        Defines recruitment, upkeep, building, and action costs, along with action and financial transaction types
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    global_manager.set('recruitment_types', global_manager.get('officer_types') + ['European workers', 'steamship'])
    global_manager.set('recruitment_costs', {'European workers': 0, 'steamship': 10, 'officer': 5})
    for current_officer in global_manager.get('officer_types'):
        global_manager.get('recruitment_costs')[current_officer] = global_manager.get('recruitment_costs')['officer']

    global_manager.set('num_african_workers', 0)
    global_manager.set('african_worker_upkeep', 0) #placeholder for labels, set to initial values on load/new game
    global_manager.set('initial_african_worker_upkeep', 4)
    global_manager.set('min_african_worker_upkeep', 0.5)

    global_manager.set('num_european_workers', 0)
    global_manager.set('european_worker_upkeep', 0)
    global_manager.set('initial_european_worker_upkeep', 6)
    global_manager.set('min_european_worker_upkeep', 0.5)

    global_manager.set('num_slave_workers', 0)
    global_manager.set('initial_slave_worker_upkeep', 2)
    global_manager.set('slave_worker_upkeep', 0)
    global_manager.set('base_slave_recruitment_cost', 5)
    global_manager.get('recruitment_costs')['slave workers'] = global_manager.get('base_slave_recruitment_cost')
    global_manager.set('min_slave_worker_recruitment_cost', 2)

    global_manager.set('num_wandering_workers', 0)
    global_manager.set('num_church_volunteers', 0)

    global_manager.set('recruitment_list_descriptions', {})
    global_manager.set('recruitment_string_descriptions', {})
    actor_utility.update_recruitment_descriptions(global_manager)

    global_manager.set('worker_upkeep_fluctuation_amount', 0.25)
    global_manager.set('slave_recruitment_cost_fluctuation_amount', 1)
    global_manager.set('base_upgrade_price', 20) #20 for 1st upgrade, 40 for 2nd, 80 for 3rd, etc.
    global_manager.set('consumer_goods_starting_price', 1)

    global_manager.set('building_prices',
        {
        'resource': 10,
        'road': 5,
        'railroad': 15,
        'road_bridge': 50,
        'railroad_bridge': 150,
        'port': 15,
        'train_station': 10,
        'trading_post': 5,
        'mission': 5,
        'fort': 5,
        'warehouses': 5,
        'train': 10,
        'steamboat': 10
       } 
    )
    
    global_manager.set('base_action_prices',
        {
        'exploration': 5,
        'conversion': 5,
        'religious_campaign': 5,
        'public_relations_campaign': 5,
        'advertising_campaign': 5,
        'loan_search': 5,
        'trade': 0,
        'loan': 5,
        'attack': 5,
        'slave_capture': 5,
        'suppress_slave_trade': 5,
        'trial': 5,
        'hunting': 5,
        'rumor_search': 5,
        'artifact_search': 5,
        'track_beasts': 0
        }
    )
    action_types = []
    for current_key in global_manager.get('base_action_prices'):
        action_types.append(current_key)
    global_manager.set('action_types', action_types)
    global_manager.set('action_prices', {})
    actor_utility.reset_action_prices(global_manager)

    global_manager.set('transaction_descriptions',
        {
        'exploration': 'exploration',
        'conversion': 'religious conversion',
        'religious_campaign': 'religious campaigning',
        'public_relations_campaign': 'public relations campaigning',
        'advertising_campaign': 'advertising',
        'loan_search': 'loan searches',
        'trade': 'trading with natives',
        'loan': 'loans',
        'attack': 'combat supplies',
        'slave_capture': 'capturing slaves',
        'suppress_slave_trade': 'slave trade suppression',
        'trial': 'trial fees',
        'hunting': 'hunting supplies',
        'rumor_search': 'artifact rumor searches',
        'artifact_search': 'artifact searches',
        'construction': 'construction',
        'production': 'production',
        'bribery': 'bribery',
        'loan_interest': 'loan interest',
        'inventory_attrition': 'missing commodities',
        'sold_commodities': 'commodity sales',
        'worker_upkeep': 'worker upkeep',
        'subsidies': 'subsidies',
        'trial_compensation': 'trial compensation',
        'fabricated_evidence': 'fabricated evidence',
        'consumer_goods': 'consumer goods',
        'unit_recruitment': 'unit recruitment',
        'attrition_replacements': 'attrition replacements',
        'misc_revenue': 'misc',
        'misc_expenses': 'misc',
        'none': 'miscellaneous company activities',
        }
    )
    transaction_types = []
    for current_key in global_manager.get('transaction_descriptions'):
        transaction_types.append(current_key)
    global_manager.set('transaction_types', transaction_types)
    global_manager.set('slave_traders_natural_max_strength', 0) #regenerates to natural strength, can increase indefinitely when slaves are purchased
    actor_utility.set_slave_traders_strength(0, global_manager)

def lore_setup(global_manager):
    '''
    Description:
        Defines the types of lore missions, artifacts within each one, and the current lore mission
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    global_manager.set('lore_types', ['zoology', 'botany', 'archaeology', 'anthropology', 'paleontology', 'theology'])
    global_manager.set('lore_types_artifact_dict',
        {
        'zoology': ['Monkey', 'Serpent', 'Beetle', 'Hawk', 'Panther', 'Spider'],
        'botany': ['Orchid', 'Vine', 'Root', 'Bark', 'Stalk', 'Fruit'],
        'archaeology': ['Tomb', 'Stele', 'Mask', 'Statue', 'City', 'Temple'],
        'anthropology': ['Urn', 'Skull', 'Totem', 'Headdress', 'Spear', 'Idol'],
        'paleontology': ['saurus Fossil', 'tops Fossil', 'don Fossil', 'raptor Fossil', 'nyx Fossil', 'mut Fossil'],
        'theology': ['Grail', 'Ark', 'Bone', 'Crown', 'Shroud', 'Blood']
        }
    )
    global_manager.set('lore_types_adjective_dict', 
        {
        'zoology': ['Albino ', 'Devil ', 'Royal ', 'Vampire ', 'Assassin ', 'Storm '],
        'botany': ['Blood ', 'Midnight ', 'Thorny ', 'Strangler ', 'Carnivorous ', 'Ghost '],
        'archaeology': ['Emperor\'s ', 'Golden ', 'Lost ', 'Antediluvian ', 'Ancient ', 'Forbidden '],
        'anthropology': ['Crystal ', 'Golden ', 'Great Chief\'s ', 'Sky ', 'Moon ', 'Volcano '],
        'paleontology': ['Tyranno', 'Bronto', 'Stego', 'Tricera', 'Pterano', 'Dimetro'],
        'theology': ['Lost ', 'Holy ', 'Prester John\'s ', 'Mary\'s ', 'True ', 'Sacred ']
        }
    )
    global_manager.set('lore_types_effects_dict',
        {
        'zoology': effects.effect('zoology_completion_effect', 'hunting_plus_modifier', global_manager),
        'botany': effects.effect('botany_completion_effect', 'health_attrition_plus_modifier', global_manager),
        'archaeology': effects.effect('archaeology_completion_effect', 'attack_plus_modifier', global_manager),
        'anthropology': effects.effect('anthropology_completion_effect', 'conversion_plus_modifier', global_manager),
        'paleontology': effects.effect('paleontology_completion_effect', 'public_relations_campaign_modifier', global_manager),
        'theology': effects.effect('theology_completion_effect', 'religious_campaign_plus_modifier', global_manager)
        }
    )
    global_manager.set('lore_types_effect_descriptions_dict',
        {
        'zoology': 'chance of a positive modifier for hunting rolls',
        'botany': 'lower chance of unit attrition death',
        'archaeology': 'chance of a positive modifier for attacking rolls against native warriors',
        'anthropology': 'chance of a positive modifier for native conversion rolls',
        'paleontology': 'chance of a positive modifier for public relations campaign rolls',
        'theology': 'chance of a positive modifier for religious campaign rolls'
        }
    )
    global_manager.set('current_lore_mission', 'none') #lore mission should be an object type with attributes for type, location, leads, etc.
    global_manager.set('lore_mission_list', [])
    global_manager.set('completed_lore_mission_types', [])

def value_trackers_setup(global_manager):
    '''
    Description:
        Defines important global values and initializes associated tracker labels
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    input_dict = {
        'coordinates': scaling.scale_coordinates(300, global_manager.get('default_display_height') - 70, global_manager),
        'minimum_width': scaling.scale_width(10, global_manager),
        'height': scaling.scale_height(30, global_manager),
        'modes': ['strategic', 'europe', 'ministers'],
        'image_id': 'misc/default_label.png',
        'value_name': 'public_opinion',
        'init_type': 'value label'
    }
    global_manager.set('public_opinion_tracker', data_managers.public_opinion_tracker('public_opinion', 0, 0, 100, global_manager))
    global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)
    
    input_dict['coordinates'] = (input_dict['coordinates'][0], scaling.scale_height(global_manager.get('default_display_height') - 30, global_manager))
    input_dict['modes'] = ['strategic', 'europe', 'ministers', 'trial']
    input_dict['init_type'] = 'money label'
    del input_dict['value_name']
    global_manager.set('money_tracker', data_managers.money_tracker(100, global_manager))
    global_manager.set('money_label', global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager))

    input_dict['coordinates'] = (scaling.scale_width(575, global_manager), input_dict['coordinates'][1])
    input_dict['modes'] = ['strategic', 'europe', 'ministers']
    input_dict['value_name'] = 'turn'
    input_dict['init_type'] = 'value label'
    global_manager.set('turn_tracker', data_managers.value_tracker('turn', 0, 'none', 'none', global_manager))
    global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

    if global_manager.get('effect_manager').effect_active('track_fps'):
        input_dict['coordinates'] = scaling.scale_coordinates(300, global_manager.get('default_display_height') - 110, global_manager)
        input_dict['value_name'] = 'fps'
        input_dict['modes'] = ['strategic', 'europe', 'ministers', 'trial', 'main_menu', 'new_game_setup']
        global_manager.set('fps_tracker', data_managers.value_tracker('fps', 0, 0, 'none', global_manager))
        global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

    global_manager.set('previous_financial_report', 'none')
    input_dict = {
        'coordinates': scaling.scale_coordinates(270, global_manager.get('default_display_height') - 30, global_manager),
        'width': scaling.scale_width(30, global_manager),
        'height': scaling.scale_height(30, global_manager),
        'modes': ['strategic', 'europe', 'ministers', 'trial'],
        'image_id': 'buttons/instructions.png',
        'init_type': 'show previous financial report button'
    }
    global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)
    
    global_manager.set('evil_tracker', data_managers.value_tracker('evil', 0, 0, 100, global_manager))
    
    global_manager.set('fear_tracker', data_managers.value_tracker('fear', 1, 1, 6, global_manager))

def buttons_setup(global_manager):
    '''
    Description:
        Initializes static buttons
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    #Could implement switch game mode buttons based on state machine logic for different modes
    europe_button_width = 150
    europe_button_height = 100
    input_dict = {
        'coordinates': scaling.scale_coordinates(global_manager.get('europe_grid_x') - europe_button_width - 25, global_manager.get('europe_grid_y') + 10, global_manager),
        'width': scaling.scale_width(europe_button_width, global_manager),
        'height': scaling.scale_height(europe_button_height, global_manager),
        'keybind_id': pygame.K_e,
        'modes': ['strategic'],
        'image_id': 'buttons/european_hq_button.png',
        'to_mode': 'europe',
        'init_type': 'switch game mode button'
    }
    strategic_to_europe_button = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)
    global_manager.get('flag_icon_list').append(strategic_to_europe_button) #sets button image to update to flag icon when country changes

    europe_button_width = 60
    europe_button_height = 60
    input_dict['coordinates'] = (input_dict['coordinates'][0], scaling.scale_height(global_manager.get('europe_grid_y'), global_manager))
    input_dict['width'] = scaling.scale_width(europe_button_width, global_manager)
    input_dict['height'] = scaling.scale_height(europe_button_height, global_manager)
    input_dict['modes'] = ['europe']
    input_dict['keybind_id'] = pygame.K_ESCAPE
    input_dict['to_mode'] = 'strategic'
    input_dict['image_id'] = 'buttons/exit_european_hq_button.png'
    europe_to_strategic_button = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

    input_dict['coordinates'] = scaling.scale_coordinates(global_manager.get('default_display_width') - 50, global_manager.get('default_display_height') - 50, global_manager)
    input_dict['width'] = scaling.scale_width(50, global_manager)
    input_dict['height'] = scaling.scale_height(50, global_manager)
    input_dict['modes'] = ['strategic', 'europe', 'ministers']
    input_dict['keybind_id'] = 'none'
    input_dict['to_mode'] = 'main_menu'
    to_main_menu_button = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

    input_dict['coordinates'] = scaling.scale_coordinates(0, global_manager.get('default_display_height') - 50, global_manager)
    input_dict['modes'] = ['new_game_setup']
    input_dict['keybind_id'] = pygame.K_ESCAPE
    new_game_setup_to_main_menu_button = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

    input_dict['coordinates'] = scaling.scale_coordinates(0, global_manager.get('default_display_height') - 50, global_manager)
    input_dict['modes'] = ['strategic', 'europe']
    input_dict['keybind_id'] = pygame.K_q
    input_dict['image_id'] = 'buttons/european_hq_button.png'
    input_dict['to_mode'] = 'ministers'
    to_ministers_button = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

    input_dict['modes'] = ['ministers']
    input_dict['keybind_id'] = pygame.K_ESCAPE
    input_dict['image_id'] = 'buttons/exit_european_hq_button.png'
    input_dict['to_mode'] = 'previous'
    from_ministers_button = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

    input_dict['modes'] = ['trial']
    input_dict['to_mode'] = 'ministers'
    from_trial_button = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

    input_dict = {
        'coordinates': scaling.scale_coordinates(round(global_manager.get('default_display_width') * 0.4), global_manager.get('default_display_height') - 50,
        global_manager),
        'width': scaling.scale_width(round(global_manager.get('default_display_width') * 0.2), global_manager),
        'height': scaling.scale_height(50, global_manager),
        'modes': ['strategic', 'europe'],
        'keybind_id': pygame.K_SPACE,
        'image_id': 'buttons/end_turn_button.png',
        'init_type': 'end turn button'
    }
    end_turn_button = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

    input_dict['coordinates'] = (input_dict['coordinates'][0], scaling.scale_height(global_manager.get('default_display_height') / 2 - 50, global_manager))
    input_dict['modes'] = ['main_menu']
    input_dict['keybind_id'] = pygame.K_n
    input_dict['image_id'] = 'buttons/new_game_button.png'
    input_dict['init_type'] = 'new game button'
    main_menu_new_game_button = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

    input_dict['coordinates'] = (input_dict['coordinates'][0], scaling.scale_height(global_manager.get('default_display_height') / 2 - 300, global_manager))
    input_dict['modes'] = ['new_game_setup']
    input_dict['keybind_id'] = pygame.K_n
    setup_new_game_button = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

    input_dict['coordinates'] = (input_dict['coordinates'][0], scaling.scale_height(global_manager.get('default_display_height') / 2 - 125, global_manager))
    input_dict['modes'] = ['main_menu']
    input_dict['keybind_id'] = pygame.K_l
    input_dict['image_id'] = 'buttons/load_game_button.png'
    input_dict['init_type'] = 'load game button'
    load_game_button = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

    button_start_x = 750 #x position of leftmost button
    button_separation = 60 #x separation between each button
    current_button_number = 0 #tracks current button to move each one farther right
    input_dict = {
        'coordinates': scaling.scale_coordinates(button_start_x + (current_button_number * button_separation), 20, global_manager),
        'width': scaling.scale_width(50, global_manager),
        'height': scaling.scale_height(50, global_manager),
        'modes': ['strategic'],
        'keybind_id': pygame.K_a,
        'image_id': 'buttons/left_button.png',
        'init_type': 'move left button'
    }
    left_arrow_button = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)
    current_button_number += 1

    input_dict['coordinates'] = scaling.scale_coordinates(button_start_x + (current_button_number * button_separation), 20, global_manager)
    input_dict['keybind_id'] = pygame.K_s
    input_dict['image_id'] = 'buttons/down_button.png'
    input_dict['init_type'] = 'move down button'
    down_arrow_button = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

    input_dict['coordinates'] = scaling.scale_coordinates(button_start_x + (current_button_number * button_separation), 80, global_manager)
    input_dict['keybind_id'] = pygame.K_w
    input_dict['image_id'] = 'buttons/up_button.png'
    input_dict['init_type'] = 'move up button'
    up_arrow_button = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)
    current_button_number += 1

    input_dict['coordinates'] = scaling.scale_coordinates(button_start_x + (current_button_number * button_separation), 20, global_manager)
    input_dict['keybind_id'] = pygame.K_d
    input_dict['image_id'] = 'buttons/right_button.png'
    input_dict['init_type'] = 'move right button'
    right_arrow_button = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

    input_dict = {
        'coordinates': scaling.scale_coordinates(global_manager.get('default_display_width') - 50, global_manager.get('default_display_height') - 125, global_manager),
        'width': scaling.scale_width(50, global_manager),
        'height': scaling.scale_height(50, global_manager),
        'modes': ['strategic', 'europe', 'ministers'],
        'image_id': 'buttons/save_game_button.png',
        'init_type': 'save game button'
    }
    save_game_button = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

    input_dict['coordinates'] = (input_dict['coordinates'][0], scaling.scale_height(global_manager.get('default_display_height') - 200, global_manager))
    input_dict['modes'] = ['strategic']
    input_dict['image_id'] = 'buttons/grid_line_button.png'
    input_dict['init_type'] = 'toggle grid lines button'
    toggle_grid_lines_button = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

    input_dict['coordinates'] = (input_dict['coordinates'][0], scaling.scale_height(global_manager.get('default_display_height') - 275, global_manager))
    input_dict['modes'] = ['strategic', 'europe', 'ministers']
    input_dict['keybind_id'] = pygame.K_j
    input_dict['image_id'] = 'buttons/text_box_size_button.png'
    input_dict['init_type'] = 'expand text box button'
    expand_text_box_button = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

    input_dict['coordinates'] = scaling.scale_coordinates(110, global_manager.get('default_display_height') - 50, global_manager)
    input_dict['modes'] = ['strategic', 'europe']
    input_dict['keybind_id'] = pygame.K_TAB
    input_dict['image_id'] = 'buttons/cycle_units_button.png'
    input_dict['init_type'] = 'cycle units button'
    cycle_units_button = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

    input_dict['coordinates'] = (scaling.scale_width(55, global_manager), input_dict['coordinates'][1])
    input_dict['modes'] = ['strategic']
    del input_dict['keybind_id']
    input_dict['image_id'] = 'buttons/free_slaves_button.png'
    input_dict['init_type'] = 'free all button'
    free_all_slaves_button = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

    input_dict['coordinates'] = (scaling.scale_width(165, global_manager), input_dict['coordinates'][1])
    input_dict['modes'] = ['strategic', 'europe']
    input_dict['image_id'] = 'buttons/disable_sentry_mode_button.png'
    input_dict['init_type'] = 'wake up all button'
    wake_up_all_button = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

    input_dict['coordinates'] = (scaling.scale_width(220, global_manager), input_dict['coordinates'][1])
    input_dict['image_id'] = 'buttons/execute_movement_routes_button.png'
    input_dict['init_type'] = 'execute movement routes button'
    execute_movement_routes_button = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

    input_dict['coordinates'] = scaling.scale_coordinates(global_manager.get('default_display_width') - 50, 0, global_manager)
    input_dict['modes'] = ['main_menu']
    input_dict['image_id'] = ['buttons/exit_european_hq_button.png']
    input_dict['init_type'] = 'generate crash button'
    generate_crash_button = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

def europe_screen_setup(global_manager):
    '''
    Description:
        Initializes static interface of Europe screen
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    #Europe screen buttons setup
    #max of 8 in column
    buy_button_y = 0#140
    input_dict = {
        'width': scaling.scale_width(100, global_manager),
        'height': scaling.scale_height(100, global_manager),
        'modes': ['europe'],
        'init_type': 'recruitment button'
    }
    for recruitment_index in range(len(global_manager.get('recruitment_types'))):
        input_dict['coordinates'] = scaling.scale_coordinates(1500 - (recruitment_index // 8) * 125, buy_button_y + (120 * (recruitment_index % 8)), global_manager)
        input_dict['recruitment_type'] = global_manager.get('recruitment_types')[recruitment_index]
        new_recruitment_button = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

    input_dict = {
        'coordinates': scaling.scale_coordinates(1500 - ((recruitment_index + 1) // 8) * 125, buy_button_y + (120 * ((recruitment_index + 1) % 8)), global_manager),
        'width': scaling.scale_width(100, global_manager),
        'height': scaling.scale_height(100, global_manager),
        'modes': ['europe'],
        'init_type': 'buy commodity button',
        'commodity_type': 'consumer goods'
    }
    new_consumer_goods_buy_button = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

def ministers_screen_setup(global_manager):
    '''
    Description:
        Initializes static interface of ministers screen
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    #minister table setup
    table_width = 400
    table_height = 800
    minister_table = images.free_image('misc/minister_table.png', scaling.scale_coordinates((global_manager.get('default_display_width') / 2) - (table_width / 2), 55, global_manager), scaling.scale_width(table_width, global_manager),
        scaling.scale_height(table_height, global_manager), ['ministers'], global_manager)

    position_icon_width = 125
    input_dict = {
        'width': scaling.scale_width(position_icon_width, global_manager),
        'height': scaling.scale_height(position_icon_width, global_manager),
        'modes': ['ministers'],
        'color': 'gray',
        'init_type': 'minister portrait image'
    }
    for current_index in range(0, 8): #creates an office icon and a portrait at a section of the table for each minister
        input_dict['minister_type'] = global_manager.get('minister_types')[current_index]
        if current_index <= 3: #left side
            images.minister_type_image(scaling.scale_coordinates((global_manager.get('default_display_width') / 2) - (table_width / 2) + 10, current_index * 200 + 95, global_manager),
                scaling.scale_width(position_icon_width, global_manager), scaling.scale_height(position_icon_width, global_manager), ['ministers'], global_manager.get('minister_types')[current_index], 'none', global_manager)
            input_dict['coordinates'] = scaling.scale_coordinates((global_manager.get('default_display_width') / 2) - (table_width / 2) - position_icon_width - 10, current_index * 200 + 95, global_manager)
            global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)
        else:
            images.minister_type_image(scaling.scale_coordinates((global_manager.get('default_display_width') / 2) + (table_width / 2) - position_icon_width - 10, (current_index - 4) * 200 + 95, global_manager),
                scaling.scale_width(position_icon_width, global_manager), scaling.scale_height(position_icon_width, global_manager), ['ministers'], global_manager.get('minister_types')[current_index], 'none', global_manager)
            input_dict['coordinates'] = scaling.scale_coordinates((global_manager.get('default_display_width') / 2) + (table_width / 2) - position_icon_width + position_icon_width + 10, (current_index - 4) * 200 + 95, global_manager)
            global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

    available_minister_display_x = global_manager.get('default_display_width')
    available_minister_display_y = 770
    cycle_input_dict = {
        'coordinates': scaling.scale_coordinates(available_minister_display_x - (position_icon_width / 2) - 25, available_minister_display_y, global_manager),
        'width': scaling.scale_width(50, global_manager),
        'height': scaling.scale_height(50, global_manager),
        'keybind_id': pygame.K_w,
        'modes': ['ministers'],
        'image_id': 'buttons/cycle_ministers_up_button.png',
        'init_type': 'cycle available ministers button',
        'direction': 'left'
    }
    cycle_left_button = global_manager.get('actor_creation_manager').create_interface_element(cycle_input_dict, global_manager)

    for i in range(0, 5):
        available_minister_display_y -= (position_icon_width + 10)
        input_dict = {
            'coordinates': scaling.scale_coordinates(available_minister_display_x - position_icon_width, available_minister_display_y, global_manager),
            'width': scaling.scale_width(position_icon_width, global_manager),
            'height': scaling.scale_height(position_icon_width, global_manager),
            'modes': ['ministers'],
            'init_type': 'minister portrait image',
            'color': 'gray',
            'minister_type': 'none'
        }
        current_portrait = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

    available_minister_display_y -= 60                     
    cycle_input_dict['coordinates'] = (cycle_input_dict['coordinates'][0], scaling.scale_height(available_minister_display_y, global_manager))
    cycle_input_dict['keybind_id'] = pygame.K_s
    cycle_input_dict['image_id'] = 'buttons/cycle_ministers_down_button.png'
    cycle_input_dict['direction'] = 'right'
    cycle_right_button = global_manager.get('actor_creation_manager').create_interface_element(cycle_input_dict, global_manager)

def trial_screen_setup(global_manager):
    '''
    Description:
        Initializes static interface of trial screen
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    trial_display_default_y = 500
    button_separation = 100
    distance_to_center = 300
    distance_to_notification = 100
    
    defense_y = trial_display_default_y
    defense_x = (global_manager.get('default_display_width') / 2) + (distance_to_center - button_separation) + distance_to_notification
    defense_current_y = 0
    input_dict = {
        'coordinates': (defense_x, defense_y),
        'width': 10,
        'height': 10,
        'modes': ['trial'],
        'init_type': 'ordered collection',
        'is_info_display': True,
        'actor_type': 'defense'
    }
    defense_info_display = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

    defense_type_image = images.minister_type_image(scaling.scale_coordinates(0, defense_current_y, global_manager),
        scaling.scale_width(button_separation * 2 - 5, global_manager), scaling.scale_height(button_separation * 2 - 5, global_manager), ['trial'], 'none', 'none', global_manager)
    defense_info_display.add_member(defense_type_image)

    defense_current_y -= button_separation * 2
    input_dict = {
        'coordinates': scaling.scale_coordinates(0, defense_current_y, global_manager),
        'width': scaling.scale_width(button_separation * 2 - 5, global_manager),
        'height': scaling.scale_height(button_separation * 2 - 5, global_manager),
        'init_type': 'minister portrait image',
        'minister_type': 'none',
        'color': 'gray',
        'parent_collection': defense_info_display
    }
    defense_portrait_image = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

    defense_current_y -= 35
    input_dict = {
        'coordinates': scaling.scale_coordinates(0, defense_current_y, global_manager),
        'minimum_width': scaling.scale_width(10, global_manager),
        'height': scaling.scale_height(30, global_manager),
        'image_id': 'misc/default_label.png',
        'message': 'Defense',
        'init_type': 'label',
        'parent_collection': defense_info_display
    }
    defense_label = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

    input_dict['actor_type'] = 'minister'
    del input_dict['message']
    input_dict['init_type'] = 'actor display label'
    defense_info_display_labels = ['minister_name', 'minister_office', 'evidence']
    for current_actor_label_type in defense_info_display_labels:
        defense_current_y -= 35
        input_dict['coordinates'] = scaling.scale_coordinates(0, defense_current_y, global_manager)
        input_dict['actor_label_type'] = current_actor_label_type
        global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

    prosecution_y = trial_display_default_y
    prosecution_x = (global_manager.get('default_display_width') / 2) - (distance_to_center + button_separation) - distance_to_notification
    prosecution_current_y = 0

    input_dict = {
        'coordinates': (prosecution_x, prosecution_y),
        'width': 10,
        'height': 10,
        'modes': ['trial'],
        'init_type': 'ordered collection',
        'is_info_display': True,
        'actor_type': 'prosecution'
    }
    prosecution_info_display = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

    prosecution_type_image = images.minister_type_image(scaling.scale_coordinates(0, prosecution_current_y, global_manager),
        scaling.scale_width(button_separation * 2 - 5, global_manager), scaling.scale_height(button_separation * 2 - 5, global_manager), ['trial'], 'none', 'none', global_manager)
    prosecution_info_display.add_member(prosecution_type_image)

    prosecution_current_y -= button_separation * 2
    input_dict = {
        'coordinates': scaling.scale_coordinates(0, prosecution_current_y, global_manager),
        'width': scaling.scale_width(button_separation * 2 - 5, global_manager),
        'height': scaling.scale_height(button_separation * 2 - 5, global_manager),
        'init_type': 'minister portrait image',
        'minister_type': 'none',
        'color': 'gray',
        'parent_collection': prosecution_info_display
    }
    prosecution_portrait_image = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

    prosecution_current_y -= 35
    input_dict = {
        'coordinates': scaling.scale_coordinates(0, prosecution_current_y, global_manager),
        'minimum_width': scaling.scale_width(10, global_manager),
        'height': scaling.scale_height(30, global_manager),
        'image_id': 'misc/default_label.png',
        'message': 'Prosecution',
        'init_type': 'label',
        'parent_collection': prosecution_info_display
    }
    prosecution_label = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

    input_dict['actor_type'] = 'minister'
    del input_dict['message']
    input_dict['init_type'] = 'actor display label'
    input_dict['parent_collection'] = prosecution_info_display
    prosecution_info_display_labels = ['minister_name', 'minister_office']
    for current_actor_label_type in prosecution_info_display_labels:
        prosecution_current_y -= 35
        input_dict['coordinates'] = scaling.scale_coordinates(0, prosecution_current_y, global_manager)
        input_dict['actor_label_type'] = current_actor_label_type 
        global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

    launch_trial_button_width = 150
    input_dict = {
        'coordinates': scaling.scale_coordinates((global_manager.get('default_display_width') / 2) - (launch_trial_button_width / 2), trial_display_default_y - 300, global_manager),
        'width': scaling.scale_width(launch_trial_button_width, global_manager),
        'height': scaling.scale_height(launch_trial_button_width, global_manager),
        'modes': ['trial'],
        'image_id': 'buttons/to_trial_button.png',
        'init_type': 'launch trial button'
    }
    launch_trial_button = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

    bribed_judge_indicator = images.indicator_image('misc/bribed_judge.png', scaling.scale_coordinates((global_manager.get('default_display_width') / 2) - ((button_separation * 2 - 5) / 2), trial_display_default_y + 200, global_manager),
        scaling.scale_width(button_separation * 2 - 5, global_manager), scaling.scale_height(button_separation * 2 - 5, global_manager), ['trial'], 'prosecution_bribed_judge', global_manager)
    non_bribed_judge_indicator = images.indicator_image('misc/non_bribed_judge.png', scaling.scale_coordinates((global_manager.get('default_display_width') / 2) - ((button_separation * 2 - 5) / 2), trial_display_default_y + 200, global_manager),
        scaling.scale_width(button_separation * 2 - 5, global_manager), scaling.scale_height(button_separation * 2 - 5, global_manager), ['trial'], 'not prosecution_bribed_judge', global_manager)
        #image_id, coordinates, width, height, modes, indicator_type, global_manager

    global_manager.set('evidence_just_found', False)

def new_game_setup_screen_setup(global_manager):
    '''
    Description:
        Initializes new game setup screen interface
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    current_country_index = 0
    country_image_width = 300
    country_image_height = 200
    country_separation = 50
    countries_per_row = 3
    input_dict = {
        'width': scaling.scale_width(country_image_width, global_manager),
        'height': scaling.scale_height(country_image_height, global_manager),
        'modes': ['new_game_setup'],
        'init_type': 'country selection image'
    }
    for current_country in global_manager.get('country_list'):
        input_dict['coordinates'] = scaling.scale_coordinates((global_manager.get('default_display_width') / 2) - (countries_per_row * (country_image_width + country_separation) / 2) + (country_image_width + country_separation) * (current_country_index % countries_per_row) + country_separation / 2, global_manager.get('default_display_height') / 2 + 50 - ((country_image_height + country_separation) * (current_country_index // countries_per_row)), global_manager)
        input_dict['country'] = current_country
        global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)
        current_country_index += 1

def mob_interface_setup(global_manager):
    '''
    Description:
        Initializes mob selection interface
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    actor_display_top_y = global_manager.get('default_display_height') - 205 + 125
    actor_display_current_y = actor_display_top_y
    global_manager.set('mob_ordered_list_start_y', actor_display_current_y)

    input_dict = {
        'coordinates': (0, actor_display_current_y),
        'width': 10,
        'height': 10,
        'modes': ['strategic', 'europe'],
        'init_type': 'ordered collection',
        'is_info_display': True,
        'actor_type': 'mob'
    }
    mob_info_display = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

    input_dict = {
        'coordinates': scaling.scale_coordinates(0, 0, global_manager),
        'minimum_width': scaling.scale_width(125, global_manager),
        'height': scaling.scale_height(125, global_manager),
        'image_id': 'misc/empty.png',
        'actor_label_type': 'tooltip',
        'actor_type': 'mob',
        'init_type': 'actor display label',
        'parent_collection': mob_info_display,
        'member_config': {'order_overlap': True}
    }
    #mob background image's tooltip
    mob_free_image_background_tooltip = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

    #mob image
    mob_free_image = actor_display_images.actor_display_free_image(scaling.scale_coordinates(0, 0, global_manager), scaling.scale_width(115, global_manager),
        scaling.scale_height(115, global_manager), ['strategic', 'europe'], 'default', global_manager) #coordinates, width, height, modes, global_manager
    global_manager.get('mob_info_display').add_member(mob_free_image, {'order_overlap': False})

    input_dict = {
        'coordinates': scaling.scale_coordinates(130, actor_display_current_y, global_manager),
        'width': scaling.scale_width(35, global_manager),
        'height': scaling.scale_height(35, global_manager),
        'modes': ['strategic', 'europe'],
        'image_id': 'buttons/remove_minister_button.png',
        'init_type': 'fire unit button'
    }
    fire_unit_button = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)
    
    input_dict['coordinates'] = (input_dict['coordinates'][0], scaling.scale_height(actor_display_current_y + 40, global_manager))
    input_dict['image_id'] = 'buttons/free_slaves_button.png'
    input_dict['init_type'] = 'free unit slaves button'
    free_unit_slaves_button = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)


    #mob info labels setup
    mob_info_display_labels = ['name', 'minister', 'officer', 'workers', 'movement', 'canoes', 'combat_strength', 'preferred_terrains', 'attitude', 'controllable', 'crew', 'passengers', 'current passenger'] #order of mob info display labels
    for current_actor_label_type in mob_info_display_labels:
        if current_actor_label_type == 'minister': #how far from edge of screen
            x_displacement = 40
        elif current_actor_label_type == 'current passenger':
            x_displacement = 30
        else:
            x_displacement = 0
        input_dict = { #should declare here to reinitialize dict and prevent extra parameters from being incorrectly retained between iterations
            'coordinates': scaling.scale_coordinates(0, 0, global_manager),
            'minimum_width': scaling.scale_width(10, global_manager),
            'height': scaling.scale_height(30, global_manager),
            'image_id': 'misc/default_label.png',
            'actor_label_type': current_actor_label_type,
            'actor_type': 'mob',
            'parent_collection': mob_info_display,
            'member_config': {'order_x_offset': x_displacement}
        }
        if not current_actor_label_type == 'current passenger':
            input_dict['init_type'] = 'actor display label'
            global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)
        else:
            input_dict['init_type'] = 'list item label'
            input_dict['list_type'] = 'ship'
            for i in range(0, 3): #0, 1, 2
                #label for each passenger
                input_dict['list_index'] = i
                global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

def tile_interface_setup(global_manager):
    '''
    Description:
        Initializes tile selection interface
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        int actor_display_current_y: Value that tracks the location of interface as it is created, used by other setup functions
    '''
    #tile info images setup
    #tile background image
    actor_display_current_y = global_manager.get('default_display_height') - (580 + 35 + 35) + 125
    global_manager.set('tile_ordered_list_start_y', actor_display_current_y)

    input_dict = {
        'coordinates': (0, global_manager.get('tile_ordered_list_start_y')), #actor_display_current_y
        'width': 10,
        'height': 10,
        'modes': ['strategic', 'europe'],
        'init_type': 'ordered collection',
        'is_info_display': True,
        'actor_type': 'tile'
    }
    tile_info_display = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

    input_dict = {
        'coordinates': scaling.scale_coordinates(130, 0, global_manager),
        'width': 10,
        'height': 10,
        'init_type': 'ordered collection',
        'parent_collection': tile_info_display,
        'member_config': {'order_exempt': True},
        'separation': 4
    }
    same_tile_ordered_collection = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

    input_dict = {
        'coordinates': scaling.scale_coordinates(0, input_dict['separation'], global_manager),
        'width': scaling.scale_width(30, global_manager),
        'height': scaling.scale_height(30, global_manager),
        'modes': ['strategic', 'europe'],
        'image_id': 'buttons/cycle_passengers_down_button.png',
        'init_type': 'cycle same tile button', #add to collection but exempt from order
        'parent_collection': same_tile_ordered_collection,
        'member_config': {'order_exempt': True}
    }
    cycle_same_tile_button = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager) #not in tile info display list should add to collection but have exception to not sort
    del input_dict['member_config']
    input_dict['coordinates'] = (0, 0)
    global_manager.set('same_tile_icon_list', [])
    input_dict['init_type'] = 'same tile icon'
    input_dict['image_id'] = 'buttons/default_button.png'
    input_dict['is_last'] = False
    input_dict['color'] = 'gray'
    for i in range(0, 3): #add button to cycle through
        #input_dict['coordinates'] = scaling.scale_coordinates(130, actor_display_current_y + 95 - (32 * i), global_manager)
        input_dict['index'] = i
        same_tile_icon = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)
    #input_dict['coordinates'] = scaling.scale_coordinates(130, actor_display_current_y + 95 - (32 * (i + 1)), global_manager)
    input_dict['index'] = i + 1
    input_dict['is_last'] = True
    same_tile_icon = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

    input_dict = {
        'coordinates': scaling.scale_coordinates(0, 0, global_manager),
        'minimum_width': scaling.scale_width(125, global_manager),
        'height': scaling.scale_height(125, global_manager),
        'image_id': 'misc/empty.png',
        'actor_label_type': 'tooltip',
        'actor_type': 'tile',
        'init_type': 'actor display label',
        'parent_collection': tile_info_display,
        'member_config': {'order_overlap': True}
    }
    #tile background image's tooltip
    tile_free_image_background_tooltip = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

    tile_image = actor_display_images.actor_display_free_image(scaling.scale_coordinates(5, actor_display_current_y + 5, global_manager), scaling.scale_width(115, global_manager),
        scaling.scale_height(115, global_manager), ['strategic', 'europe'], 'default', global_manager)
    tile_info_display.add_member(tile_image, {'order_overlap': False})

    #tile info labels setup
    tile_info_display_labels = ['coordinates', 'terrain', 'resource', 'slums',
                                'resource building', 'building efficiency', 'building work crews', 'current building work crew',
                                'village', 'native population', 'native available workers', 'native aggressiveness',
                                'slave_traders_strength']
    for current_actor_label_type in tile_info_display_labels:
        if current_actor_label_type == 'current building work crew':
            x_displacement = 50
        elif current_actor_label_type in ['building efficiency', 'building work crews', 'native population', 'native available workers', 'native aggressiveness']:
            x_displacement = 25
        else:
            x_displacement = 0
        input_dict = { #should declare here to reinitialize dict and prevent extra parameters from being incorrectly retained between iterations
            'coordinates': scaling.scale_coordinates(x_displacement, 0, global_manager),
            'minimum_width': scaling.scale_width(10, global_manager),
            'height': scaling.scale_height(30, global_manager),
            'image_id': 'misc/default_label.png',
            'actor_label_type': current_actor_label_type,
            'actor_type': 'tile',
            'parent_collection': tile_info_display
        }
        if not current_actor_label_type in ['building efficiency', 'building work crews', 'current building work crew', 'native population', 'native available workers', 'native aggressiveness']:
            input_dict['init_type'] = 'actor display label'
            global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)
        elif current_actor_label_type == 'building efficiency':
            input_dict['init_type'] = 'building efficiency label'
            input_dict['building_type'] = 'resource'
            global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)
        elif current_actor_label_type == 'building work crews':
            input_dict['init_type'] = 'building work crews label'
            input_dict['building_type'] = 'resource'
            global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)
        elif current_actor_label_type == 'current building work crew':
            input_dict['init_type'] = 'list item label'
            input_dict['list_type'] = 'building'
            for i in range(0, 3):
                input_dict['list_index'] = i
                global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)
        elif current_actor_label_type in ['native population', 'native available workers', 'native aggressiveness']:
            input_dict['init_type'] = current_actor_label_type + ' label'
            global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)
    return(actor_display_current_y)

def inventory_interface_setup(actor_display_current_y, global_manager):
    '''
    Description:
        Initializes both tile and mob inventory interface
    Input:
        global_manager_template global_manager: Object that accesses shared variables
        int actor_display_current_y: Value that tracks the location of interface as it is created, given by previous setup functions
    Output:
        None
    '''
    actor_display_current_y -= 35

    commodity_prices_x, commodity_prices_y = (870, 100)
    commodity_prices_height = 30 + (30 * len(global_manager.get('commodity_types')))
    commodity_prices_width = 200
    input_dict = {
        'coordinates':scaling.scale_coordinates(commodity_prices_x, commodity_prices_y, global_manager),
        'minimum_width':scaling.scale_width(commodity_prices_width, global_manager),
        'height': scaling.scale_height(commodity_prices_height, global_manager),
        'modes': ['europe'],
        'image_id': 'misc/commodity_prices_label.png',
        'init_type': 'commodity prices label'
    }
    global_manager.set('commodity_prices_label', global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager))
    input_dict = {
        'width': scaling.scale_width(30, global_manager),
        'height': scaling.scale_height(30, global_manager),
        'modes': ['europe'],
        'init_type': 'commodity button'
    }
    for current_index in range(len(global_manager.get('commodity_types'))): #commodity prices in Europe
        input_dict['coordinates'] = scaling.scale_coordinates(commodity_prices_x - 35, commodity_prices_y + commodity_prices_height - 65 - (30 * current_index), global_manager)
        input_dict['image_id'] = 'scenery/resources/large/' + global_manager.get('commodity_types')[current_index] + '.png'
        input_dict['commodity'] = global_manager.get('commodity_types')[current_index]
        new_commodity_button = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

    inventory_collection_relative_coordinates = (450, 0)

    input_dict = {
        'coordinates': scaling.scale_coordinates(inventory_collection_relative_coordinates[0], inventory_collection_relative_coordinates[1], global_manager), #remember member element coordinates are relative to parent
        'width': scaling.scale_width(10, global_manager),
        'height': scaling.scale_height(30, global_manager),
        'init_type': 'ordered collection',
        'parent_collection': global_manager.get('mob_info_display'),
        'member_config': {'order_exempt': True}
    }
    mob_inventory_collection = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

    input_dict = {
        'minimum_width': scaling.scale_width(10, global_manager),
        'height': scaling.scale_height(30, global_manager),
        'image_id': 'misc/default_label.png',
        'actor_label_type': 'mob inventory capacity',
        'actor_type': 'mob',
        'init_type': 'actor display label',
        'parent_collection': mob_inventory_collection
    }
    mob_inventory_capacity_label = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)
    
    del input_dict['actor_label_type']
    for current_index in range(len(global_manager.get('commodity_types'))): #commodities held in selected mob
        input_dict['commodity_index'] = current_index
        input_dict['init_type'] = 'commodity display label'
        new_commodity_display_label = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

    input_dict = {
        'coordinates': scaling.scale_coordinates(inventory_collection_relative_coordinates[0], inventory_collection_relative_coordinates[1] + 50, global_manager), #remember member element coordinates are relative to parent
        'width': scaling.scale_width(10, global_manager),
        'height': scaling.scale_height(30, global_manager),
        'init_type': 'ordered collection',
        'parent_collection': global_manager.get('tile_info_display'),
        'member_config': {'order_exempt': True}
    }
    tile_inventory_collection = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

    input_dict = {
        'minimum_width': scaling.scale_width(10, global_manager),
        'height': scaling.scale_height(30, global_manager),
        'image_id': 'misc/default_label.png',
        'actor_label_type': 'tile inventory capacity',
        'actor_type': 'tile',
        'init_type': 'actor display label',
        'parent_collection': tile_inventory_collection,
    }
    tile_inventory_capacity_label = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

    del input_dict['actor_label_type']
    for current_index in range(len(global_manager.get('commodity_types'))): #commodities held in selected tile
        input_dict['commodity_index'] = current_index
        input_dict['init_type'] = 'commodity display label'
        new_commodity_display_label = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

def minister_interface_setup(global_manager):
    '''
    Description:
        Initializes minister selection interface
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        int actor_display_current_y: Value that tracks the location of interface as it is created, used by other setup functions
    '''
    #minister info images setup
    minister_display_top_y = global_manager.get('default_display_height') - 205
    global_manager.set('minister_ordered_list_start_y', minister_display_top_y)
    minister_display_current_y = 0

    input_dict = {
        'coordinates': (0, minister_display_top_y),
        'width': 10,
        'height': 10,
        'modes': ['ministers'],
        'init_type': 'ordered collection',
        'is_info_display': True,
        'actor_type': 'minister'
    }
    minister_info_display = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

    #minister background image
    minister_free_image_background = actor_display_images.minister_background_image('misc/mob_background.png', scaling.scale_coordinates(0, 0, global_manager), scaling.scale_width(125, global_manager),
        scaling.scale_height(125, global_manager), ['ministers'], global_manager)
    minister_info_display.add_member(minister_free_image_background, {'order_overlap': True})
    

    input_dict = {
        'coordinates': scaling.scale_coordinates(0, minister_display_current_y, global_manager),
        'minimum_width': scaling.scale_width(125, global_manager),
        'height': scaling.scale_height(125, global_manager),
        'image_id': 'misc/empty.png',
        'actor_label_type': 'tooltip',
        'actor_type': 'minister',
        'init_type': 'actor display label',
        'parent_collection': minister_info_display,
        'member_config': {'order_overlap': True}
    }
    #minister background image's tooltip
    minister_free_image_background_tooltip = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

    #minister image
    minister_free_image = actor_display_images.actor_display_free_image(scaling.scale_coordinates(0, 0, global_manager), scaling.scale_width(115, global_manager),
        scaling.scale_height(115, global_manager), ['ministers'], 'minister_default', global_manager) #coordinates, width, height, modes, global_manager
    minister_info_display.add_member(minister_free_image, {'order_overlap': True, 'order_x_offset': 5, 'order_y_offset': 5})

    minister_display_current_y -= 35
    #minister info images setup

    input_dict = {
        'minimum_width': scaling.scale_width(10, global_manager),
        'height': scaling.scale_height(30, global_manager),
        'image_id': 'misc/default_label.png',
        'actor_type': 'minister',
        'init_type': 'actor display label',
        'parent_collection': minister_info_display
    }
    #minister info labels setup
    minister_info_display_labels = ['minister_name', 'minister_office', 'background', 'social status', 'interests', 'evidence']
    for current_actor_label_type in minister_info_display_labels:
        x_displacement = 0
        input_dict['coordinates'] = scaling.scale_coordinates(x_displacement, minister_display_current_y, global_manager)
        input_dict['actor_label_type'] = current_actor_label_type
        global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)
    #minister info labels setup

def country_interface_setup(global_manager):
    '''
    Description:
        Initializes country selection interface
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        int actor_display_current_y: Value that tracks the location of interface as it is created, used by other setup functions
    '''

    input_dict = {
        'coordinates': (0, global_manager.get('tile_ordered_list_start_y')),
        'width': 10,
        'height': 10,
        'modes': ['new_game_setup'],
        'init_type': 'ordered collection',
        'is_info_display': True,
        'actor_type': 'country'
    }
    country_info_display = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

    #country background image
    country_free_image_background = actor_display_images.mob_background_image('misc/mob_background.png', scaling.scale_coordinates(0, 0, global_manager), scaling.scale_width(125, global_manager),
        scaling.scale_height(125, global_manager), ['new_game_setup'], global_manager) #mob and country background images would have the same functionality
    country_info_display.add_member(country_free_image_background, {'order_overlap': True})

    input_dict = {
        'coordinates': scaling.scale_coordinates(0, 0, global_manager),
        'minimum_width': scaling.scale_width(125, global_manager),
        'height': scaling.scale_height(125, global_manager),
        'image_id': 'misc/empty.png',
        'actor_label_type': 'tooltip',
        'actor_type': 'country',
        'init_type': 'actor display label',
        'parent_collection': country_info_display,
        'member_config': {'order_overlap': True}
    }
    #country background image's tooltip
    country_free_image_background_tooltip = global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

    #country image
    country_free_image = actor_display_images.actor_display_free_image(scaling.scale_coordinates(0, 0, global_manager), scaling.scale_width(115, global_manager),
        scaling.scale_height(115, global_manager), ['new_game_setup'], 'country_default', global_manager) #coordinates, width, height, modes, global_manager
    country_info_display.add_member(country_free_image, {'order_overlap': True, 'order_x_offset': 5, 'order_y_offset': 5})

    #country_display_current_y -= 35

    input_dict = {
        'minimum_width': scaling.scale_width(10, global_manager),
        'height': scaling.scale_height(30, global_manager),
        'modes':['new_game_setup'],
        'image_id': 'misc/default_label.png',
        'actor_type': 'country',
        'init_type': 'actor display label',
        'parent_collection': country_info_display
    }
    #country info labels setup
    country_info_display_labels = ['country_name', 'country_effect']
    for current_actor_label_type in country_info_display_labels:
        x_displacement = 0
        input_dict['coordinates'] = scaling.scale_coordinates(x_displacement, 0, global_manager)
        input_dict['actor_label_type'] = current_actor_label_type
        global_manager.get('actor_creation_manager').create_interface_element(input_dict, global_manager)

def debug_tools_setup(global_manager):
    '''
    Description:
        Initializes toggleable effects for debugging
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    global_manager.set('effect_manager', data_managers.effect_manager_template(global_manager))

    #for release, official version of config file with only intended user settings
    file = open('configuration/release_config.json')

    # returns JSON object as a dictionary
    debug_config = json.load(file)
    # Iterating through the json list
    for current_effect in debug_config['effects']:
        effects.effect('DEBUG_' + current_effect, current_effect, global_manager)

    try: #for testing/development, use active effects of local version of config file that is not uploaded to GitHub
        file = open('configuration/dev_config.json')
        active_effects_config = json.load(file)
    except:
        active_effects_config = debug_config
    for current_effect in active_effects_config['active_effects']:
        if global_manager.get('effect_manager').effect_exists(current_effect):
            global_manager.get('effect_manager').set_effect(current_effect, True)
        else:
            print('Invalid effect: ' + current_effect)

def manage_crash(exception):
    '''
    Description: 
        Uses an exception to write a crash log and exit the game
    Input:
        Exception exception: Exception that caused the crash
    Output:
        None
    '''
    crash_log_file = open('notes/Crash Log.txt', 'w')
    crash_log_file.write('') #clears crash report file
    console = logging.StreamHandler() #sets logger to go to both console and crash log file
    logging.basicConfig(filename = 'notes/Crash Log.txt')
    logging.getLogger('').addHandler(console)
    
    logging.error(exception, exc_info = True) #sends error message to console and crash log file
    
    crash_log_file.close()
    pygame.quit()
