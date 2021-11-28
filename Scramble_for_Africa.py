import pygame
import time
import random
import os

import modules.scaling as scaling
import modules.main_loop as main_loop
import modules.images as images
import modules.buttons as buttons
import modules.game_transitions as game_transitions
import modules.data_managers as data_managers
import modules.europe_transactions as europe_transactions
import modules.labels as labels
import modules.actor_display_tools.images as actor_display_images
import modules.actor_display_tools.labels as actor_display_labels
import modules.instructions as instructions
import modules.mouse_followers as mouse_followers
import modules.save_load_tools as save_load_tools
import modules.actor_creation_tools as actor_creation_tools

pygame.init()

global_manager = data_managers.global_manager_template()#manager of a dictionary of what would be global variables passed between functions and classes
global_manager.set('save_load_manager', save_load_tools.save_load_manager_template(global_manager))
global_manager.set('europe_grid', 'none')
resolution_finder = pygame.display.Info()
global_manager.set('default_display_width', 1728)#all parts of game made to be at default and scaled to display
global_manager.set('default_display_height', 972)
global_manager.set('display_width', resolution_finder.current_w - round(global_manager.get('default_display_width')/10))
global_manager.set('display_height', resolution_finder.current_h - round(global_manager.get('default_display_height')/10))
global_manager.set('loading', True)
global_manager.set('loading_start_time', time.time())

global_manager.set('font_name', 'times new roman')
#global_manager.set('font_name', 'couriernew') monospaced
#print(pygame.font.get_fonts())
global_manager.set('font_size', scaling.scale_width(15, global_manager))
global_manager.set('myfont', pygame.font.SysFont(global_manager.get('font_name'), global_manager.get('font_size')))

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
    'brown': (132, 94, 59)
    }
)

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

global_manager.set('commodity_types', ['consumer goods', 'coffee', 'copper', 'diamond', 'exotic wood', 'fruit', 'gold', 'iron', 'ivory', 'rubber'])
global_manager.set('collectable_resources', ['coffee', 'copper', 'diamond', 'exotic wood', 'fruit', 'gold', 'iron', 'ivory', 'rubber'])
global_manager.set('commodity_prices', {})

for current_commodity in global_manager.get('commodity_types'):
    global_manager.get('commodity_prices')[current_commodity] = 0

#building type: price
global_manager.set('building_prices',
    {
    'resource': 2,
    'infrastructure': 1,
    'port': 3,
    'train_station': 2,
    'trading_post': 1,
    'mission': 1,
    'train': 1
   } 
)


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

global_manager.set('building_types', ['resource', 'port', 'infrastructure', 'train_station', 'trading_post', 'mission'])

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


global_manager.set('officer_types', ['explorer', 'engineer', 'porter_foreman', 'merchant', 'head_missionary']) #change to driver
global_manager.set('officer_group_type_dict',
    {
    'explorer': 'expedition',
    'engineer': 'construction_gang',
    'porter_foreman': 'porters',
    'merchant': 'caravan',
    'head_missionary': 'missionaries'
    }
)

type_minister_dict = global_manager.get('type_minister_dict')
global_manager.set('officer_minister_dict',
    {
    'explorer': type_minister_dict['exploration'],
    'engineer': type_minister_dict['construction'],
    'porter_foreman': type_minister_dict['transportation'],
    'merchant': type_minister_dict['trade'],
    'head_missionary': type_minister_dict['religion']
    }
)

global_manager.set('group_minister_dict',
    {
    'expedition': type_minister_dict['exploration'],
    'construction_gang': type_minister_dict['construction'],
    'porters': type_minister_dict['transportation'],
    'caravan': type_minister_dict['trade'],
    'missionaries': type_minister_dict['religion']
    }
)
global_manager.set('recruitment_types', global_manager.get('officer_types') + ['European worker', 'ship'])
global_manager.set('recruitment_costs', {'European worker': 0, 'ship': 5})
for current_officer in global_manager.get('officer_types'):
    global_manager.get('recruitment_costs')[current_officer] = 5

global_manager.get('game_display').fill(global_manager.get('color_dict')['white'])
global_manager.set('button_list', [])
global_manager.set('current_instructions_page', 'none')
global_manager.set('current_dice_rolling_notification', 'none')
global_manager.set('current_instructions_page_index', 0)
global_manager.set('instructions_list', [])
#page 1
instructions_message = "Placeholder instructions, use += to add"
global_manager.get('instructions_list').append(instructions_message)

global_manager.set('minister_list', [])
global_manager.set('grid_list', [])
global_manager.set('abstract_grid_list', [])
global_manager.set('text_list', [])
global_manager.set('image_list', [])
global_manager.set('free_image_list', [])
global_manager.set('minister_image_list', [])
global_manager.set('background_image_list', [])
global_manager.set('actor_list', [])
global_manager.set('mob_list', [])
global_manager.set('village_list', [])
global_manager.set('building_list', [])
global_manager.set('resource_building_list', [])
global_manager.set('infrastructure_connection_list', [])
global_manager.set('officer_list', [])
global_manager.set('worker_list', [])
global_manager.set('num_workers', 0)
global_manager.set('worker_upkeep', 1)
global_manager.set('group_list', [])
global_manager.set('tile_list', [])
global_manager.set('exploration_mark_list', [])
global_manager.set('overlay_tile_list', [])
global_manager.set('notification_list', [])
global_manager.set('label_list', [])
global_manager.set('mob_info_display_list', [])
global_manager.set('mob_ordered_label_list', [])
global_manager.set('minister_info_display_list', [])
global_manager.set('minister_ordered_label_list', [])
global_manager.set('displayed_mob', 'none')
global_manager.set('displayed_minister', 'none')
global_manager.set('tile_info_display_list', [])
global_manager.set('tile_ordered_label_list', [])
global_manager.set('displayed_tile', 'none')
global_manager.set('dice_list', [])
global_manager.set('end_turn_selected_mob', 'none')
pygame.key.set_repeat(300, 200)
global_manager.set('crashed', False)
global_manager.set('lmb_down', False)
global_manager.set('rmb_down', False)
global_manager.set('mmb_down', False)
global_manager.set('typing', False)
global_manager.set('message', '')
global_manager.set('show_grid_lines', True)
global_manager.set('show_text_box', True)
global_manager.set('show_selection_outlines', True)
global_manager.set('show_minimap_outlines', True)
global_manager.set('making_choice', False)
global_manager.set('player_turn', True)
global_manager.set('choosing_destination', False)
global_manager.set('choosing_destination_info_dict', {})

global_manager.set('ongoing_exploration', False)
global_manager.set('ongoing_trade', False)
global_manager.set('ongoing_religious_campaign', False)
global_manager.set('ongoing_conversion', False)
global_manager.set('ongoing_construction', False)

global_manager.set('r_shift', 'up')
global_manager.set('l_shift', 'up')
global_manager.set('capital', False)
global_manager.set('r_ctrl', 'up')
global_manager.set('l_ctrl', 'up')
global_manager.set('ctrl', 'up')
global_manager.set('start_time', time.time())
global_manager.set('current_time', time.time())
global_manager.set('last_selection_outline_switch', time.time())
mouse_moved_time = time.time()
global_manager.set('mouse_moved_time', time.time())
old_mouse_x, old_mouse_y = pygame.mouse.get_pos()#used in tooltip drawing timing
global_manager.set('old_mouse_x', old_mouse_x)
global_manager.set('old_mouse_y', old_mouse_y)
global_manager.set('flavor_text_manager', data_managers.flavor_text_manager_template(global_manager))
global_manager.set('loading_image', images.loading_image_template('misc/loading.png', global_manager))
global_manager.set('current_game_mode', 'none')
global_manager.set('input_manager', data_managers.input_manager_template(global_manager))
global_manager.set('actor_creation_manager', actor_creation_tools.actor_creation_manager_template())


strategic_background_image = images.free_image('misc/background.png', (0, 0), global_manager.get('display_width'), global_manager.get('display_height'), ['strategic', 'europe', 'main_menu', 'ministers'], global_manager)
#europe_background_image = images.free_image('misc/europe_background.png', (0, 0), global_manager.get('display_width'), global_manager.get('display_height'), ['europe'], global_manager)
global_manager.get('background_image_list').append(strategic_background_image)
strategic_grid_height = 300#450
strategic_grid_width = 320#480
mini_grid_height = 600#450
mini_grid_width = 640#480

global_manager.set('minimap_grid_origin_x', global_manager.get('default_display_width') - (mini_grid_width + 100))

europe_grid_x = global_manager.get('default_display_width') - (strategic_grid_width + 340)
europe_grid_y = global_manager.get('default_display_height') - (strategic_grid_height + 25)

global_manager.set('mob_ordered_list_start_y', 0)
global_manager.set('tile_ordered_list_start_y', 0)
global_manager.set('minister_ordered_list_start_y', 0)

global_manager.set('current_game_mode', 'main menu') #initial previous game mode
game_transitions.set_game_mode('main_menu', global_manager)

global_manager.set('mouse_follower', mouse_followers.mouse_follower(global_manager))

global_manager.set('money_tracker', data_managers.money_tracker(100, global_manager))
labels.money_label(scaling.scale_coordinates(225, global_manager.get('default_display_height') - 30, global_manager), scaling.scale_width(10, global_manager), scaling.scale_height(30, global_manager), ['strategic', 'europe'],
    'misc/default_label.png', global_manager)

global_manager.set('turn_tracker', data_managers.value_tracker('turn', 0, global_manager))
labels.value_label(scaling.scale_coordinates(225, global_manager.get('default_display_height') - 70, global_manager), scaling.scale_width(10, global_manager), scaling.scale_height(30, global_manager), ['strategic', 'europe'],
    'misc/default_label.png', 'turn', global_manager)

strategic_to_europe_button = buttons.switch_game_mode_button(scaling.scale_coordinates(europe_grid_x - 85, europe_grid_y, global_manager), scaling.scale_width(60, global_manager), scaling.scale_height(60, global_manager), 'blue',
    pygame.K_e, 'europe', ['strategic'], 'buttons/european_hq_button.png', global_manager)

europe_to_strategic_button = buttons.switch_game_mode_button(scaling.scale_coordinates(europe_grid_x - 85, europe_grid_y, global_manager), scaling.scale_width(60, global_manager), scaling.scale_height(60, global_manager), 'blue',
    pygame.K_ESCAPE, 'strategic', ['europe'], 'buttons/exit_european_hq_button.png', global_manager)

to_main_menu_button = buttons.switch_game_mode_button(scaling.scale_coordinates(global_manager.get('default_display_width') - 50, global_manager.get('default_display_height') - 125, global_manager),
    scaling.scale_width(50, global_manager), scaling.scale_height(50, global_manager), 'blue', 'none', 'main menu', ['strategic', 'europe', 'ministers'], 'buttons/exit_european_hq_button.png', global_manager)

to_ministers_button = buttons.switch_game_mode_button(scaling.scale_coordinates(0, global_manager.get('default_display_height') - 50, global_manager), scaling.scale_width(50, global_manager), scaling.scale_height(50, global_manager), 'blue', pygame.K_q, 'ministers',
    ['strategic', 'europe'], 'buttons/european_hq_button.png', global_manager)

from_ministers_button = buttons.switch_game_mode_button(scaling.scale_coordinates(0, global_manager.get('default_display_height') - 50, global_manager), scaling.scale_width(50, global_manager), scaling.scale_height(50, global_manager), 'blue', pygame.K_ESCAPE, 'previous',
    ['ministers'], 'buttons/exit_european_hq_button.png', global_manager)

end_turn_button = buttons.button(scaling.scale_coordinates(round(global_manager.get('default_display_width') * 0.4), global_manager.get('default_display_height') - 50,
    global_manager), scaling.scale_width(round(global_manager.get('default_display_width') * 0.2), global_manager), scaling.scale_height(50, global_manager), 'blue', 'start end turn', pygame.K_SPACE, ['strategic', 'europe'],
    'buttons/end_turn_button.png', global_manager)

new_game_button = buttons.button(scaling.scale_coordinates(round(global_manager.get('default_display_width') * 0.4), global_manager.get('default_display_height') / 2 - 50, global_manager),
    scaling.scale_width(round(global_manager.get('default_display_width') * 0.2), global_manager), scaling.scale_height(50, global_manager), 'blue', 'new game', pygame.K_n, ['main_menu'], 'buttons/new_game_button.png', global_manager)

load_game_button = buttons.button(scaling.scale_coordinates(round(global_manager.get('default_display_width') * 0.4), global_manager.get('default_display_height') / 2 - 125, global_manager),
    scaling.scale_width(round(global_manager.get('default_display_width') * 0.2), global_manager), scaling.scale_height(50, global_manager), 'blue', 'load game', pygame.K_l, ['main_menu'], 'buttons/load_game_button.png', global_manager)



button_start_x = 500#x position of leftmost button
button_separation = 60#x separation between each button
current_button_number = 0#tracks current button to move each one farther right

left_arrow_button = buttons.button(scaling.scale_coordinates(button_start_x + (current_button_number * button_separation), 20, global_manager), scaling.scale_width(50, global_manager), scaling.scale_height(50, global_manager), 'blue',
    'move left', pygame.K_a, ['strategic', 'europe'], 'buttons/left_button.png', global_manager)
current_button_number += 1

down_arrow_button = buttons.button(scaling.scale_coordinates(button_start_x + (current_button_number * button_separation), 20, global_manager), scaling.scale_width(50, global_manager), scaling.scale_height(50, global_manager), 'blue',
    'move down', pygame.K_s, ['strategic', 'europe'], 'buttons/down_button.png', global_manager)#movement buttons should be usable in any mode with a grid


up_arrow_button = buttons.button(scaling.scale_coordinates(button_start_x + (current_button_number * button_separation), 80, global_manager), scaling.scale_width(50, global_manager), scaling.scale_height(50, global_manager), 'blue',
    'move up', pygame.K_w, ['strategic', 'europe'], 'buttons/up_button.png', global_manager)
current_button_number += 1

right_arrow_button = buttons.button(scaling.scale_coordinates(button_start_x + (current_button_number * button_separation), 20, global_manager), scaling.scale_width(50, global_manager), scaling.scale_height(50, global_manager), 'blue',
    'move right', pygame.K_d, ['strategic', 'europe'], 'buttons/right_button.png', global_manager)


expand_text_box_button = buttons.button(scaling.scale_coordinates(75, global_manager.get('default_display_height') - 50, global_manager), scaling.scale_width(50, global_manager), scaling.scale_height(50, global_manager), 'black',
    'expand text box', pygame.K_j, ['strategic', 'europe'], 'buttons/text_box_size_button.png', global_manager) #'none' for no keybind

instructions_button = instructions.instructions_button(scaling.scale_coordinates(global_manager.get('default_display_width') - 50, global_manager.get('default_display_height') - 50, global_manager), scaling.scale_width(50, global_manager),
    scaling.scale_height(50, global_manager), 'blue', 'instructions', pygame.K_i, ['strategic', 'europe'], 'buttons/instructions.png', global_manager)

save_game_button = buttons.button(scaling.scale_coordinates(global_manager.get('default_display_width') - 50, global_manager.get('default_display_height') - 200, global_manager), scaling.scale_width(50, global_manager),
    scaling.scale_height(50, global_manager), 'blue', 'save game', 'none', ['strategic', 'europe'], 'buttons/save_game_button.png', global_manager)

cycle_units_button = buttons.button(scaling.scale_coordinates(150, global_manager.get('default_display_height') - 50, global_manager), scaling.scale_width(50, global_manager), scaling.scale_height(50, global_manager), 'blue',
    'cycle units', pygame.K_TAB, ['strategic', 'europe'], 'buttons/cycle_units_button.png', global_manager)


minister_display_top_y = global_manager.get('default_display_height') - 205
minister_display_current_y = minister_display_top_y
global_manager.set('minister_ordered_list_start_y', minister_display_current_y)

#minister background image
minister_free_image_background = actor_display_images.mob_background_image('misc/mob_background.png', scaling.scale_coordinates(0, minister_display_current_y, global_manager), scaling.scale_width(125, global_manager),
    scaling.scale_height(125, global_manager), ['ministers'], global_manager)
global_manager.get('minister_info_display_list').append(minister_free_image_background)

#minister background image's tooltip
minister_free_image_background_tooltip = actor_display_labels.actor_display_label(scaling.scale_coordinates(0, minister_display_current_y, global_manager), scaling.scale_width(125, global_manager), scaling.scale_height(125, global_manager),
    ['ministers'], 'misc/empty.png', 'tooltip', 'minister', global_manager) #coordinates, minimum_width, height, modes, image_id, actor_label_type, actor_type, global_manager
global_manager.get('minister_info_display_list').append(minister_free_image_background_tooltip)

#minister image
minister_free_image = actor_display_images.actor_display_free_image(scaling.scale_coordinates(5, minister_display_current_y + 5, global_manager), scaling.scale_width(115, global_manager),
    scaling.scale_height(115, global_manager), ['ministers'], 'minister_default', global_manager) #coordinates, width, height, modes, global_manager
global_manager.get('minister_info_display_list').append(minister_free_image)

minister_display_current_y -= 35

#minister name label
minister_name_label = actor_display_labels.actor_display_label(scaling.scale_coordinates(0, minister_display_current_y, global_manager), scaling.scale_width(10, global_manager), scaling.scale_height(30, global_manager),
    ['ministers'], 'misc/default_label.png', 'minister_name', 'minister', global_manager) #coordinates, ideal_width, minimum_height, modes, image_id, mob_label_type, global_manager
global_manager.get('minister_info_display_list').append(minister_name_label)

#minister office label
minister_office_label = actor_display_labels.actor_display_label(scaling.scale_coordinates(0, minister_display_current_y, global_manager), scaling.scale_width(10, global_manager), scaling.scale_height(30, global_manager),
    ['ministers'], 'misc/default_label.png', 'minister_office', 'minister', global_manager) #coordinates, ideal_width, minimum_height, modes, image_id, mob_label_type, global_manager
global_manager.get('minister_info_display_list').append(minister_office_label)


actor_display_top_y = global_manager.get('default_display_height') - 205
actor_display_current_y = actor_display_top_y
global_manager.set('mob_ordered_list_start_y', actor_display_current_y)

#mob background image
mob_free_image_background = actor_display_images.mob_background_image('misc/mob_background.png', scaling.scale_coordinates(0, actor_display_current_y, global_manager), scaling.scale_width(125, global_manager),
    scaling.scale_height(125, global_manager), ['strategic', 'europe'],global_manager)
global_manager.get('mob_info_display_list').append(mob_free_image_background)

#mob background image's tooltip
mob_free_image_background_tooltip = actor_display_labels.actor_display_label(scaling.scale_coordinates(0, actor_display_current_y, global_manager), scaling.scale_width(125, global_manager), scaling.scale_height(125, global_manager),
    ['strategic', 'europe'], 'misc/empty.png', 'tooltip', 'mob', global_manager) #coordinates, minimum_width, height, modes, image_id, actor_label_type, actor_type, global_manager
global_manager.get('mob_info_display_list').append(mob_free_image_background_tooltip)

#mob image
mob_free_image = actor_display_images.actor_display_free_image(scaling.scale_coordinates(5, actor_display_current_y + 5, global_manager), scaling.scale_width(115, global_manager),
    scaling.scale_height(115, global_manager), ['strategic', 'europe'], 'default', global_manager) #coordinates, width, height, modes, global_manager
global_manager.get('mob_info_display_list').append(mob_free_image)

#veteran icon image
mob_free_image = actor_display_images.actor_display_free_image(scaling.scale_coordinates(5, actor_display_current_y + 5, global_manager), scaling.scale_width(115, global_manager),
    scaling.scale_height(115, global_manager), ['strategic', 'europe'], 'veteran_icon', global_manager) #coordinates, width, height, modes, global_manager
global_manager.get('mob_info_display_list').append(mob_free_image)

#mob name label
mob_name_label = actor_display_labels.actor_display_label(scaling.scale_coordinates(0, actor_display_current_y, global_manager), scaling.scale_width(10, global_manager), scaling.scale_height(30, global_manager),
    ['strategic', 'europe'], 'misc/default_label.png', 'name', 'mob', global_manager) #coordinates, ideal_width, minimum_height, modes, image_id, mob_label_type, global_manager
global_manager.get('mob_info_display_list').append(mob_name_label)

#mob controlling minister label
mob_minister_label = actor_display_labels.actor_display_label(scaling.scale_coordinates(40, actor_display_current_y, global_manager), scaling.scale_width(10, global_manager), scaling.scale_height(30, global_manager),
    ['strategic', 'europe'], 'misc/default_label.png', 'minister', 'mob', global_manager)
global_manager.get('mob_info_display_list').append(mob_minister_label)

#mob group officer label
mob_name_label = actor_display_labels.actor_display_label(scaling.scale_coordinates(0, actor_display_current_y, global_manager), scaling.scale_width(10, global_manager), scaling.scale_height(30, global_manager),
    ['strategic', 'europe'], 'misc/default_label.png', 'officer', 'mob', global_manager) #coordinates, ideal_width, minimum_height, modes, image_id, mob_label_type, global_manager
global_manager.get('mob_info_display_list').append(mob_name_label)

#mob group worker label
mob_name_label = actor_display_labels.actor_display_label(scaling.scale_coordinates(0, actor_display_current_y, global_manager), scaling.scale_width(10, global_manager), scaling.scale_height(30, global_manager),
    ['strategic', 'europe'], 'misc/default_label.png', 'worker', 'mob', global_manager) #coordinates, ideal_width, minimum_height, modes, image_id, mob_label_type, global_manager
global_manager.get('mob_info_display_list').append(mob_name_label)

#mob movement points label
mob_movement_label = actor_display_labels.actor_display_label(scaling.scale_coordinates(0, actor_display_current_y, global_manager), scaling.scale_width(10, global_manager),
    scaling.scale_height(30, global_manager), ['strategic', 'europe'], 'misc/default_label.png', 'movement', 'mob', global_manager) #coordinates, ideal_width, minimum_height, modes, image_id, mob_label_type, global_manager

global_manager.get('mob_info_display_list').append(mob_movement_label)

#mob vehicle crew label
mob_crew_label = actor_display_labels.actor_display_label(scaling.scale_coordinates(0, actor_display_current_y, global_manager), scaling.scale_width(10, global_manager),
    scaling.scale_height(30, global_manager), ['strategic', 'europe'], 'misc/default_label.png', 'crew', 'mob', global_manager) #coordinates, ideal_width, minimum_height, modes, image_id, mob_label_type, global_manager
global_manager.get('mob_info_display_list').append(mob_crew_label)

#mob vehicle passengers list label
mob_passengers_label = actor_display_labels.actor_display_label(scaling.scale_coordinates(0, actor_display_current_y, global_manager), scaling.scale_width(10, global_manager),
    scaling.scale_height(30, global_manager), ['strategic', 'europe'], 'misc/default_label.png', 'passengers', 'mob', global_manager) #coordinates, ideal_width, minimum_height, modes, image_id, mob_label_type, global_manager
global_manager.get('mob_info_display_list').append(mob_passengers_label)

for i in range(0, 3): #0, 1, 2
    #mob vehicle label for each passenger
    current_passenger_label = actor_display_labels.list_item_label(scaling.scale_coordinates(25, actor_display_current_y, global_manager), scaling.scale_width(10, global_manager), scaling.scale_height(30, global_manager),
        ['strategic', 'europe'], 'misc/default_label.png', 'current passenger', i, 'ship', 'mob', global_manager) #coordinates, minimum_width, height, modes, image_id, actor_label_type, list_index, list_type, global_manager
    global_manager.get('mob_info_display_list').append(current_passenger_label)

#tile background image
actor_display_current_y = global_manager.get('default_display_height') - 580
global_manager.set('tile_ordered_list_start_y', actor_display_current_y)
tile_free_image_background = actor_display_images.mob_background_image('misc/tile_background.png', scaling.scale_coordinates(0, actor_display_current_y, global_manager), scaling.scale_width(125, global_manager),
    scaling.scale_height(125, global_manager), ['strategic', 'europe'], global_manager)
global_manager.get('tile_info_display_list').append(tile_free_image_background)

cycle_same_tile_button = buttons.cycle_same_tile_button(scaling.scale_coordinates(162, actor_display_current_y + 95, global_manager),
        scaling.scale_width(30, global_manager), scaling.scale_height(30, global_manager), 'gray', ['strategic', 'europe'], 'buttons/cycle_passengers_down.png', global_manager)
for i in range(0, 3): #add button to cycle through
    same_tile_icon = buttons.same_tile_icon(scaling.scale_coordinates(130, actor_display_current_y + 95 - (32 * i), global_manager),
        scaling.scale_width(30, global_manager), scaling.scale_height(30, global_manager), 'gray', ['strategic', 'europe'], 'buttons/default_button.png', i, False, global_manager)
same_tile_icon = buttons.same_tile_icon(scaling.scale_coordinates(130, actor_display_current_y + 95 - (32 * (i + 1)), global_manager),
    scaling.scale_width(30, global_manager), scaling.scale_height(30, global_manager), 'gray', ['strategic', 'europe'], 'buttons/default_button.png', i + 1, True, global_manager)

#tile background image's tooltip
tile_free_image_background_tooltip = actor_display_labels.actor_display_label(scaling.scale_coordinates(0, actor_display_current_y, global_manager), scaling.scale_width(125, global_manager), scaling.scale_height(125, global_manager),
    ['strategic', 'europe'], 'misc/empty.png', 'tooltip', 'tile', global_manager) #coordinates, minimum_width, height, modes, image_id, actor_label_type, actor_type, global_manager
global_manager.get('tile_info_display_list').append(tile_free_image_background_tooltip)

#tile terrain image
tile_free_image = actor_display_images.actor_display_free_image(scaling.scale_coordinates(5, actor_display_current_y + 5, global_manager), scaling.scale_width(115, global_manager),
    scaling.scale_height(115, global_manager), ['strategic', 'europe'], 'terrain', global_manager) #coordinates, width, height, modes, global_manager
global_manager.get('tile_info_display_list').append(tile_free_image)

#tile infrastructure image
tile_free_infrastructure_image = actor_display_images.actor_display_free_image(scaling.scale_coordinates(5, actor_display_current_y + 5, global_manager), scaling.scale_width(115, global_manager),
    scaling.scale_height(115, global_manager), ['strategic'], 'infrastructure_middle', global_manager) #coordinates, width, height, modes, global_manager
global_manager.get('tile_info_display_list').append(tile_free_infrastructure_image)

#tile infrastructure connection up image
tile_free_infrastructure_up_image = actor_display_images.actor_display_infrastructure_connection_image(scaling.scale_coordinates(5, actor_display_current_y + 5, global_manager), scaling.scale_width(115, global_manager),
    scaling.scale_height(115, global_manager), ['strategic'], 'infrastructure_connection', 'up', global_manager) #coordinates, width, height, modes, global_manager
global_manager.get('tile_info_display_list').append(tile_free_infrastructure_up_image)
#tile infrastructure connection down image
tile_free_infrastructure_down_image = actor_display_images.actor_display_infrastructure_connection_image(scaling.scale_coordinates(5, actor_display_current_y + 5, global_manager), scaling.scale_width(115, global_manager),
    scaling.scale_height(115, global_manager), ['strategic'], 'infrastructure_connection', 'down', global_manager) #coordinates, width, height, modes, global_manager
global_manager.get('tile_info_display_list').append(tile_free_infrastructure_down_image)
#tile infrastructure connection right image
tile_free_infrastructure_right_image = actor_display_images.actor_display_infrastructure_connection_image(scaling.scale_coordinates(5, actor_display_current_y + 5, global_manager), scaling.scale_width(115, global_manager),
    scaling.scale_height(115, global_manager), ['strategic'], 'infrastructure_connection', 'right', global_manager) #coordinates, width, height, modes, global_manager
global_manager.get('tile_info_display_list').append(tile_free_infrastructure_right_image)
#tile infrastructure connection left image
tile_free_infrastructure_left_image = actor_display_images.actor_display_infrastructure_connection_image(scaling.scale_coordinates(5, actor_display_current_y + 5, global_manager), scaling.scale_width(115, global_manager),
    scaling.scale_height(115, global_manager), ['strategic'], 'infrastructure_connection', 'left', global_manager) #coordinates, width, height, modes, global_manager
global_manager.get('tile_info_display_list').append(tile_free_infrastructure_left_image)

#tile resource image
tile_free_resource_image = actor_display_images.actor_display_free_image(scaling.scale_coordinates(5, actor_display_current_y + 5, global_manager), scaling.scale_width(115, global_manager),
    scaling.scale_height(115, global_manager), ['strategic'], 'resource', global_manager) #coordinates, width, height, modes, global_manager
global_manager.get('tile_info_display_list').append(tile_free_resource_image)

#tile resource building image
tile_free_resource_building_image = actor_display_images.actor_display_free_image(scaling.scale_coordinates(5, actor_display_current_y + 5, global_manager), scaling.scale_width(115, global_manager),
    scaling.scale_height(115, global_manager), ['strategic'], 'resource building', global_manager) #coordinates, width, height, modes, global_manager
global_manager.get('tile_info_display_list').append(tile_free_resource_building_image)

#tile port image
tile_free_port_image = actor_display_images.actor_display_free_image(scaling.scale_coordinates(5, actor_display_current_y + 5, global_manager), scaling.scale_width(115, global_manager),
    scaling.scale_height(115, global_manager), ['strategic'], 'port', global_manager) #coordinates, width, height, modes, global_manager
global_manager.get('tile_info_display_list').append(tile_free_port_image)

#tile train station image
tile_free_train_station_image = actor_display_images.actor_display_free_image(scaling.scale_coordinates(5, actor_display_current_y + 5, global_manager), scaling.scale_width(115, global_manager),
    scaling.scale_height(115, global_manager), ['strategic'], 'train_station', global_manager) #coordinates, width, height, modes, global_manager
global_manager.get('tile_info_display_list').append(tile_free_train_station_image)

#tile trading post image
tile_free_trading_post_image = actor_display_images.actor_display_free_image(scaling.scale_coordinates(5, actor_display_current_y + 5, global_manager), scaling.scale_width(115, global_manager),
    scaling.scale_height(115, global_manager), ['strategic'], 'trading_post', global_manager) #coordinates, width, height, modes, global_manager
global_manager.get('tile_info_display_list').append(tile_free_trading_post_image)

#tile trading post image
tile_free_mission_image = actor_display_images.actor_display_free_image(scaling.scale_coordinates(5, actor_display_current_y + 5, global_manager), scaling.scale_width(115, global_manager),
    scaling.scale_height(115, global_manager), ['strategic'], 'mission', global_manager) #coordinates, width, height, modes, global_manager
global_manager.get('tile_info_display_list').append(tile_free_mission_image)

#tile terrain label
tile_terrain_label = actor_display_labels.actor_display_label(scaling.scale_coordinates(0, actor_display_current_y, global_manager), scaling.scale_width(10, global_manager),
    scaling.scale_height(30, global_manager), ['strategic', 'europe'], 'misc/default_label.png', 'terrain', 'tile', global_manager) #coordinates, ideal_width, minimum_height, modes, image_id, mob_label_type, global_manager
global_manager.get('tile_info_display_list').append(tile_terrain_label)

#tile resource label
tile_resource_label = actor_display_labels.actor_display_label(scaling.scale_coordinates(0, actor_display_current_y, global_manager), scaling.scale_width(10, global_manager),
    scaling.scale_height(30, global_manager), ['strategic'], 'misc/default_label.png', 'resource', 'tile', global_manager) #coordinates, ideal_width, minimum_height, modes, image_id, mob_label_type, global_manager
global_manager.get('tile_info_display_list').append(tile_resource_label)

#tile resource building workers label
building_workers_label = actor_display_labels.building_workers_label(scaling.scale_coordinates(25, actor_display_current_y, global_manager), scaling.scale_width(10, global_manager), scaling.scale_height(30, global_manager),
    ['strategic'], 'misc/default_label.png', 'resource', 'tile', global_manager)
global_manager.get('tile_info_display_list').append(building_workers_label)

for i in range(0, 3): #0, 1, 2
    building_worker_label = actor_display_labels.list_item_label(scaling.scale_coordinates(50, actor_display_current_y, global_manager), scaling.scale_width(10, global_manager), scaling.scale_height(30, global_manager),
        ['strategic'], 'misc/default_label.png', 'building worker', i, 'resource building', 'tile', global_manager) #coordinates, minimum_width, height, modes, image_id, actor_label_type, list_index, list_type, global_manager
    global_manager.get('tile_info_display_list').append(building_worker_label)
    #if i == 0: #available workers, at same level as first current worker label

#tile village population label
native_population_label = actor_display_labels.native_info_label(scaling.scale_coordinates(25, actor_display_current_y, global_manager), scaling.scale_width(10, global_manager), scaling.scale_height(30, global_manager),
    ['strategic'], 'misc/default_label.png', 'native population', 'tile', global_manager)
global_manager.get('tile_info_display_list').append(native_population_label) #at same level as workers label

native_available_workers_label = actor_display_labels.native_info_label(scaling.scale_coordinates(25, actor_display_current_y, global_manager), scaling.scale_width(10, global_manager), scaling.scale_height(30, global_manager),
    ['strategic'], 'misc/default_label.png', 'native available workers', 'tile', global_manager)
global_manager.get('tile_info_display_list').append(native_available_workers_label)

native_aggressiveness_label = actor_display_labels.native_info_label(scaling.scale_coordinates(25, actor_display_current_y, global_manager), scaling.scale_width(10, global_manager), scaling.scale_height(30, global_manager),
    ['strategic'], 'misc/default_label.png', 'native aggressiveness', 'tile', global_manager)
global_manager.get('tile_info_display_list').append(native_aggressiveness_label)

actor_display_current_y -= 35

commodity_prices_x, commodity_prices_y = (870, 100)
commodity_prices_height = 30 + (30 * len(global_manager.get('commodity_types')))
commodity_prices_width = 200
global_manager.set('commodity_prices_label', labels.commodity_prices_label(scaling.scale_coordinates(commodity_prices_x, commodity_prices_y, global_manager), scaling.scale_width(200, global_manager),
    scaling.scale_height(commodity_prices_height, global_manager), ['europe'], 'misc/commodity_prices_label.png', global_manager))
for current_index in range(len(global_manager.get('commodity_types'))): #commodity prices in Europe
    new_commodity_image = images.free_image('scenery/resources/' + global_manager.get('commodity_types')[current_index] + '.png', scaling.scale_coordinates(commodity_prices_x - 35,
        commodity_prices_y + commodity_prices_height - 65 - (30 * current_index), global_manager), scaling.scale_width(40, global_manager), scaling.scale_height(40, global_manager), ['europe'], global_manager)

mob_inventory_capacity_label = actor_display_labels.actor_display_label(scaling.scale_coordinates(300, global_manager.get('default_display_height') - 115, global_manager), scaling.scale_width(10, global_manager),
    scaling.scale_height(30, global_manager), ['strategic', 'europe'], 'misc/default_label.png', 'mob inventory capacity', 'mob', global_manager)
global_manager.get('mob_info_display_list').append(mob_inventory_capacity_label)
for current_index in range(len(global_manager.get('commodity_types'))): #commodities held in selected mob
    new_commodity_display_label = actor_display_labels.commodity_display_label(scaling.scale_coordinates(300, global_manager.get('default_display_height') - (150 + (35 * (current_index))), global_manager),
        scaling.scale_width(10, global_manager), scaling.scale_height(30, global_manager), ['strategic', 'europe'], 'misc/default_label.png', current_index, 'mob', global_manager)
    global_manager.get('mob_info_display_list').append(new_commodity_display_label)

tile_inventory_capacity_label = actor_display_labels.actor_display_label(scaling.scale_coordinates(300, global_manager.get('default_display_height') - 455, global_manager), scaling.scale_width(10, global_manager),
    scaling.scale_height(30, global_manager), ['strategic', 'europe'], 'misc/default_label.png', 'tile inventory capacity', 'tile', global_manager)
global_manager.get('tile_info_display_list').append(tile_inventory_capacity_label)
for current_index in range(len(global_manager.get('commodity_types'))): #commodities held in selected tile
    new_commodity_display_label = actor_display_labels.commodity_display_label(scaling.scale_coordinates(300, global_manager.get('default_display_height') - (490 + (35 * (current_index))), global_manager),
        scaling.scale_width(10, global_manager), scaling.scale_height(30, global_manager), ['strategic', 'europe'], 'misc/default_label.png', current_index, 'tile', global_manager)
        #coordinates, ideal_width, minimum_height, modes, image_id, commodity_index, global_manager
    
    global_manager.get('tile_info_display_list').append(new_commodity_display_label)

buy_button_y = 0#140
for recruitment_index in range(len(global_manager.get('recruitment_types'))):
    new_recruitment_button = europe_transactions.recruitment_button(scaling.scale_coordinates(1500, buy_button_y + (120 * (recruitment_index + 1)), global_manager), scaling.scale_width(100, global_manager),
        scaling.scale_height(100, global_manager), 'blue', global_manager.get('recruitment_types')[recruitment_index], 'none', ['europe'], global_manager)

new_consumer_goods_buy_button = europe_transactions.buy_commodity_button(scaling.scale_coordinates(1500, buy_button_y, global_manager), scaling.scale_width(100, global_manager),
    scaling.scale_height(100, global_manager), 'blue', 'consumer goods', ['europe'], global_manager)#coordinates, width, height, color, commodity_type, modes, global_manager

table_width = 400
table_height = 800
minister_table = images.free_image('misc/minister_table.png', scaling.scale_coordinates((global_manager.get('default_display_width') / 2) - (table_width / 2), 0, global_manager), scaling.scale_width(table_width, global_manager),
    scaling.scale_height(table_height, global_manager), ['ministers'], global_manager)

position_icon_width = 125
for current_index in range(0, 8): #creates an icon at each part of the table for the minister
    if current_index <= 3: #left side
        images.minister_type_image(scaling.scale_coordinates((global_manager.get('default_display_width') / 2) - (table_width / 2) + 10, current_index * 200, global_manager),
            scaling.scale_width(position_icon_width, global_manager), scaling.scale_height(position_icon_width, global_manager), ['ministers'], global_manager.get('minister_types')[current_index], 'none', global_manager)
        buttons.minister_portrait_image(scaling.scale_coordinates((global_manager.get('default_display_width') / 2) - (table_width / 2) - position_icon_width - 10, current_index * 200, global_manager),
            scaling.scale_width(position_icon_width, global_manager), scaling.scale_height(position_icon_width, global_manager), ['ministers'], global_manager.get('minister_types')[current_index], global_manager)
    else:
        images.minister_type_image(scaling.scale_coordinates((global_manager.get('default_display_width') / 2) + (table_width / 2) - position_icon_width - 10, (current_index - 4) * 200, global_manager),
            scaling.scale_width(position_icon_width, global_manager), scaling.scale_height(position_icon_width, global_manager), ['ministers'], global_manager.get('minister_types')[current_index], 'none', global_manager)
        buttons.minister_portrait_image(scaling.scale_coordinates((global_manager.get('default_display_width') / 2) + (table_width / 2) - position_icon_width + position_icon_width + 10, (current_index - 4) * 200, global_manager),
            scaling.scale_width(position_icon_width, global_manager), scaling.scale_height(position_icon_width, global_manager), ['ministers'], global_manager.get('minister_types')[current_index], global_manager)

minister_description_message = "Each minister controls a certain part of your company operations and has hidden skill and corruption levels."
minister_description_message += "A particularly skilled or unskilled minister will achieve higher or lower results than average on dice rolls."
minister_description_message += "A corrupt minister may choose not to execute your orders, instead keeping the money and reporting a failing dice roll."
minister_description_message += "If a minister reports many unusual dice rolls, you may be able to predict their skill or corruption levels."
minister_description_width = 800
minister_description_label = labels.multi_line_label(scaling.scale_coordinates(global_manager.get('default_display_width') / 2 - (minister_description_width / 2), table_height + 10, global_manager),
    minister_description_width, 0, ['ministers'], 'misc/default_notification.png', minister_description_message, global_manager) #coordinates, ideal_width, minimum_height, modes, image, message, global_manager
main_loop.main_loop(global_manager)

#actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('tile_info_display_list'), tile) to calibrate actor display to a tile
#actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('mob_info_display_list'), mob) to calibrate actor display to a tile
#minister_utility.calibrate_minister_info_display(global_manager, minister) to calibrate minister display to a minister
pygame.quit()
