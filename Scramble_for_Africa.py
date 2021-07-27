#Scramble_for_Africa.py
#
#modules folder
#
#    actors.py
#       class actor
#           class mob
#               class explorer
#           class tile_class
#               class overlay_tile
#       def create_image_dict
#
#    button.py
#       class button_class
#
#    notification_tools.py
#       def display_notification
#       def show_tutorial_notifications
#
#    notification.py
#       class notification(label)
#           class exploration_notification
#           class dice_rolling_notification
#       def notification_to_front
#
#    main_loop.py
#       def update_display
#       def action_possible
#       def draw_loading_screen
#       def manage_tooltip_drawing
#       def draw_text_box
#       def manage_rmb_down
#       def manage_lmb_down
#
#    csv_tools.py
#       def read_csv
#
#    data_managers.py
#       class global_manager_template
#       class input_manager_template
#       class flavor_text_manager_template
#
#    cells.py
#       class cell
#
#    utility.py
#       def find_object_distance (takes objects with x and y attributes)
#       def find_coordinate_distance (takes coordinate tuples)
#       def remove_from_list
#       def toggle
#       def generate_article
#       def add_to_message
#
#    label.py
#       class label
#           class instructions_page
#
#    images.py
#       class free_image
#           class loading_image_class
#       class actor_image
#           class button_image
#           class tile_image
#
#    text_tools.py
#       def message_width
#       def get_input
#       def text
#       def manage_text_list
#       def print_to_screen
#       def print_to_previous_message
#       def clear_message
#
#    grids.py
#       class grid
#           class mini_grid
#
#    game_transitions.py
#       def set_game_mode
#       def create_strategic_map
#       def start_loading
#
#    bars.py
#       class bar
#           class actor_bar
#
#    drawing_tools.py
#       def rect_to_surface
#       def display_image
#       def display_image_angle
#
#    scaling.py
#       def scale_coordinates
#       def scale_width
#       def scale_height
#
#    dice.py
#       class die
#
#    dice_utility.py
#       def roll
#       def roll_to_list
#
#   instructions.py
#       def display_instructions_page
import pygame
import time
import random
import math

import modules.scaling as scaling
import modules.main_loop as main_loop
import modules.text_tools as text_tools
import modules.utility as utility
import modules.dice_utility as dice_utility
import modules.notification_tools as notification_tools
import modules.images as images
import modules.label as label
import modules.button as button
import modules.game_transitions as game_transitions
import modules.actors as actors
import modules.grids as grids
import modules.bars as bars
import modules.data_managers as data_managers
import modules.csv_tools as csv_tools
import modules.actor_utility as actor_utility

pygame.init()
#clock = pygame.time.Clock()

global_manager = data_managers.global_manager_template()#manager of a dictionary of what would be global variables passed between functions and classes
resolution_finder = pygame.display.Info()
global_manager.set('default_display_width', 1728)#all parts of game made to be at default and scaled to display
global_manager.set('default_display_height', 972)
global_manager.set('display_width', resolution_finder.current_w - round(global_manager.get('default_display_width')/10))
global_manager.set('display_height', resolution_finder.current_h - round(global_manager.get('default_display_height')/10))
global_manager.set('loading', True)
global_manager.set('loading_start_time', time.time())

#default
#global_manager.set('myfont', pygame.font.SysFont('Times New Roman', scaling.scale_width(15, global_manager)))

global_manager.set('myfont', pygame.font.SysFont('Times New Roman', scaling.scale_width(15, global_manager)))

global_manager.set('font_size', scaling.scale_width(15, global_manager))
global_manager.set('game_display', pygame.display.set_mode((global_manager.get('display_width'), global_manager.get('display_height'))))

pygame.display.set_caption('SFA')

color_dict = {}
color_dict['black'] = (0, 0, 0)
color_dict['white'] = (255, 255, 255)
color_dict['light gray'] = (230, 230, 230)
color_dict['gray'] = (190, 190, 190)
color_dict['dark gray'] = (150, 150, 150)
color_dict['bright red'] = (255, 0, 0)
color_dict['red'] = (200, 0, 0)
color_dict['dark red'] = (150, 0, 0)
color_dict['bright green'] = (0, 255, 0)
color_dict['green'] = (0, 200, 0)
color_dict['dark green'] = (0, 150, 0)
color_dict['bright blue'] = (0, 0, 255)
color_dict['blue'] = (0, 0, 200)
color_dict['dark blue'] = (0, 0, 150)
color_dict['yellow'] = (255, 255, 0)
color_dict['brown'] = (132, 94, 59)
global_manager.set('color_dict', color_dict)

terrain_list = ['clear', 'mountain', 'hills', 'jungle', 'swamp', 'desert']
global_manager.set('terrain_list', terrain_list)
terrain_colors = {'clear': (150, 200, 104), 'hills': (50, 205, 50), 'jungle': (0, 100, 0), 'water': (0, 0, 200), 'mountain': (100, 100, 100), 'swamp': (100, 100, 50), 'desert': (255, 248, 104), 'none': (0, 0, 0)}
global_manager.set('terrain_colors', terrain_colors)
global_manager.get('game_display').fill(global_manager.get('color_dict')['white'])
global_manager.set('button_list', [])
global_manager.set('current_instructions_page', 'none')
global_manager.set('current_dice_rolling_notification', 'none')
global_manager.set('current_instructions_page_index', 0)
global_manager.set('instructions_list', [])
#page 1
instructions_message = "Placeholder instructions, use += to add"
global_manager.get('instructions_list').append(instructions_message)

global_manager.set('grid_list', [])
global_manager.set('text_list', [])
global_manager.set('image_list', [])
global_manager.set('bar_list', [])
global_manager.set('actor_list', [])
global_manager.set('mob_list', [])
global_manager.set('officer_list', [])
global_manager.set('tile_list', [])
global_manager.set('overlay_tile_list', [])
global_manager.set('notification_list', [])
global_manager.set('label_list', [])
global_manager.set('dice_list', [])
global_manager.set('notification_queue', [])
global_manager.set('notification_type_queue', [])
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
global_manager.set('mouse_origin_x', 0)
global_manager.set('mouse_origin_y', 0)
global_manager.set('mouse_destination_x', 0)
mouse_destination_y = 0
global_manager.set('mouse_destination_y', 0)
global_manager.set('making_mouse_box', False)

global_manager.set('ongoing_exploration', False)

global_manager.set('r_shift', 'up')
global_manager.set('l_shift', 'up')
global_manager.set('capital', False)
global_manager.set('r_ctrl', 'up')
global_manager.set('l_ctrl', 'up')
global_manager.set('ctrl', 'up')
global_manager.set('start_time', time.time())
global_manager.set('current_time', time.time())
global_manager.set('last_selection_outline_switch', time.time())
#global_manager.set('last_minimap_outline_switch', time.time())
mouse_moved_time = time.time()
global_manager.set('mouse_moved_time', time.time())
old_mouse_x, old_mouse_y = pygame.mouse.get_pos()#used in tooltip drawing timing
global_manager.set('old_mouse_x', old_mouse_x)
global_manager.set('old_mouse_y', old_mouse_y)
notification_tools.show_tutorial_notifications(global_manager)
global_manager.set('loading_image', images.loading_image_class('misc/loading.png', global_manager))
global_manager.set('current_game_mode', 'none')
global_manager.set('input_manager', data_managers.input_manager_template(global_manager))
global_manager.set('flavor_text_manager', data_managers.flavor_text_manager_template(global_manager))
global_manager.set('background_image', images.free_image('misc/background.png', (0, 0), global_manager.get('display_width'), global_manager.get('display_height'), ['strategic'], global_manager))
#strategic_map_grid = grids.grid(scaling.scale_coordinates(729, 150, global_manager), scaling.scale_width(870, global_manager), scaling.scale_height(810, global_manager), 64, 60, True, color_dict['dark green'], ['strategic']) #other map sizes
#strategic_map_grid = grids.grid(scaling.scale_coordinates(729, 150, global_manager), scaling.scale_width(870, global_manager), scaling.scale_height(810, global_manager), 32, 30, True, color_dict['dark green'], ['strategic'])
#strategic_map_grid = grids.grid(scaling.scale_coordinates(695, 150, global_manager), scaling.scale_width(864, global_manager), scaling.scale_height(810, global_manager), 16, 15, color_dict['dark green'], ['strategic'], global_manager) #54 by 54
#default
#strategic_map_grid = grids.grid(scaling.scale_coordinates(global_manager.get('display_width') - (grid_width + 100), global_manager.get('display_height') - (grid_height + 25), global_manager), scaling.scale_width(grid_width, global_manager), scaling.scale_height(grid_height, global_manager), 16, 15, color_dict['dark green'], ['strategic'], True, global_manager)
grid_height = 450
grid_width = 480

strategic_map_grid = grids.grid(scaling.scale_coordinates(global_manager.get('default_display_width') - (grid_width + 100), global_manager.get('default_display_height') - (grid_height + 25), global_manager), scaling.scale_width(grid_width, global_manager), scaling.scale_height(grid_height, global_manager), 16, 15, 'black', 'black', ['strategic'], True, 2, global_manager)
global_manager.set('strategic_map_grid', strategic_map_grid)

minimap_grid = grids.mini_grid(scaling.scale_coordinates(global_manager.get('default_display_width') - (grid_width + 100), global_manager.get('default_display_height') - (2 * (grid_height + 25)), global_manager), scaling.scale_width(grid_width, global_manager), scaling.scale_height(grid_height, global_manager), 5, 5, 'black', 'bright red', ['strategic'], global_manager.get('strategic_map_grid'), 3, global_manager) #60 by 60

global_manager.set('minimap_grid', minimap_grid)
game_transitions.set_game_mode('strategic', global_manager)
#roll_label = label.label(scaling.scale_coordinates(580, global_manager.get('default_display_height') - 50, global_manager), scaling.scale_width(90, global_manager), scaling.scale_height(50, global_manager), ['strategic'], 'misc/small_label.png', 'Roll: ', global_manager) #coordinates, ideal_width, minimum_height, modes, image_id, message, global_manager
#global_manager.set('roll_label', roll_label)

button_start_x = 500#600#x position of leftmost button
button_separation = 60#x separation between each button
current_button_number = 0#tracks current button to move each one farther right

left_arrow_button = button.button_class(scaling.scale_coordinates(button_start_x + (current_button_number * button_separation), 20, global_manager), scaling.scale_width(50, global_manager), scaling.scale_height(50, global_manager), 'blue', 'move left', pygame.K_a, ['strategic'], 'misc/left_button.png', global_manager)
current_button_number += 1
down_arrow_button = button.button_class(scaling.scale_coordinates(button_start_x + (current_button_number * button_separation), 20, global_manager), scaling.scale_width(50, global_manager), scaling.scale_height(50, global_manager), 'blue', 'move down', pygame.K_s, ['strategic'], 'misc/down_button.png', global_manager)#movement buttons should be usable in any mode with a grid

up_arrow_button = button.button_class(scaling.scale_coordinates(button_start_x + (current_button_number * button_separation), 80, global_manager), scaling.scale_width(50, global_manager), scaling.scale_height(50, global_manager), 'blue', 'move up', pygame.K_w, ['strategic'], 'misc/up_button.png', global_manager)
current_button_number += 1
right_arrow_button = button.button_class(scaling.scale_coordinates(button_start_x + (current_button_number * button_separation), 20, global_manager), scaling.scale_width(50, global_manager), scaling.scale_height(50, global_manager), 'blue', 'move right', pygame.K_d, ['strategic'], 'misc/right_button.png', global_manager)
current_button_number += 2#move more when switching categories

current_button_number += 1

expand_text_box_button = button.button_class(scaling.scale_coordinates(0, global_manager.get('default_display_height') - 50, global_manager), scaling.scale_width(50, global_manager), scaling.scale_height(50, global_manager), 'black', 'expand text box', pygame.K_j, ['strategic'], 'misc/text_box_size_button.png', global_manager) #'none' for no keybind
#toggle_grid_lines_button = button.button_class(scaling.scale_coordinates(global_manager.get('default_display_width') - 50, global_manager.get('default_display_height') - 170, global_manager), scaling.scale_width(50, global_manager), scaling.scale_height(50, global_manager), 'blue', 'toggle grid lines', pygame.K_g, ['strategic'], 'misc/grid_line_button.png', global_manager)
instructions_button = button.button_class(scaling.scale_coordinates(global_manager.get('default_display_width') - 50, global_manager.get('default_display_height') - 50, global_manager), scaling.scale_width(50, global_manager), scaling.scale_height(50, global_manager), 'blue', 'instructions', pygame.K_i, ['strategic'], 'misc/instructions.png', global_manager)
toggle_text_box_button = button.button_class(scaling.scale_coordinates(75, global_manager.get('default_display_height') - 50, global_manager), scaling.scale_width(50, global_manager), scaling.scale_height(50, global_manager), 'blue', 'toggle text box', pygame.K_t, ['strategic'], 'misc/toggle_text_box_button.png', global_manager)
merge_button = button.merge_button(scaling.scale_coordinates(global_manager.get('default_display_width') - 50, global_manager.get('default_display_height') - 220, global_manager), scaling.scale_width(50, global_manager), scaling.scale_height(50, global_manager), 'blue', pygame.K_m, ['strategic'], 'misc/merge_button.png', global_manager)

for i in range(0, 5):
    selected_icon = button.selected_icon(scaling.scale_coordinates(global_manager.get('default_display_width') - 50, global_manager.get('default_display_height') - (280 + 60 * i), global_manager), scaling.scale_width(50, global_manager), scaling.scale_height(50, global_manager), 'gray', ['strategic'], 'misc/default_button.png', i, global_manager)
#selected_icon_1 = button.selected_icon(scaling.scale_coordinates(global_manager.get('default_display_width') - 50, global_manager.get('default_display_height') - 270, global_manager), scaling.scale_width(50, global_manager), scaling.scale_height(50, global_manager), 'gray', ['strategic'], 'misc/default_button.png', 0, global_manager)#coordinates, width, height, color, modes, image_id, selection_index, global_manager

#while True: #to do: prevent 2nd row from the bottom of the map grid from ever being completely covered with water due to unusual river RNG, causing infinite loop here, or start increasing y until land is found
#    start_x = random.randrange(0, global_manager.get('strategic_map_grid').coordinate_width)
#    start_y = 1
#    if not(global_manager.get('strategic_map_grid').find_cell(start_x, start_y).terrain == 'water'): #if there is land at that coordinate, break and allow explorer to spawn there
#        break
new_explorer = actors.explorer(actor_utility.get_start_coordinates(global_manager), [global_manager.get('strategic_map_grid'), global_manager.get('minimap_grid')], 'mobs/explorer/default.png', 'Explorer', ['strategic'], global_manager)#self, coordinates, grid, image_id, name, modes, global_manager
new_mob = actors.mob(actor_utility.get_start_coordinates(global_manager), [global_manager.get('strategic_map_grid'), global_manager.get('minimap_grid')], 'mobs/default/default.png', 'Mob', ['strategic'], global_manager)

global_manager.get('minimap_grid').calibrate(new_explorer.x, new_explorer.y)

#while True: 
#    start_x = random.randrange(0, global_manager.get('strategic_map_grid').coordinate_width)
#    start_y = 1
#    if not(global_manager.get('strategic_map_grid').find_cell(start_x, start_y).terrain == 'water'): #if there is land at that coordinate, break and allow explorer to spawn there
#        break
#new_worker = actors.mob((start_x, start_y), global_manager.get('strategic_map_grid'), 'mobs/default/default.png', 'Worker', ['strategic'], global_manager)#self, coordinates, grid, image_id, name, modes, global_manager

while not global_manager.get('crashed'):
    if len(global_manager.get('notification_list')) == 0:
        stopping = False
    global_manager.get('input_manager').update_input()
    if global_manager.get('input_manager').taking_input:
        typing = True
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            global_manager.set('crashed', True)
        if global_manager.get('r_shift') == 'down' or global_manager.get('l_shift') == 'down':
            global_manager.set('capital', True)
        else:
            global_manager.set('capital', False)
        if global_manager.get('r_ctrl') == 'down' or global_manager.get('l_ctrl') == 'down':
            global_manager.set('ctrl', True)
        else:
            global_manager.set('ctrl', False)
        if event.type == pygame.KEYDOWN:
            for button in global_manager.get('button_list'):
                if global_manager.get('current_game_mode') in button.modes and not global_manager.get('typing'):
                    if button.has_keybind:
                        if event.key == button.keybind_id:
                            if button.has_released:
                                button.on_click()
                                button.has_released = False
                        else:#stop confirming an important button press if user starts doing something else
                            button.confirming = False
                    else:
                        button.confirming = False
            if event.key == pygame.K_RSHIFT:
                global_manager.set('r_shift', 'down')
            if event.key == pygame.K_LSHIFT:
                global_manager.set('l_shift', 'down')
            if event.key == pygame.K_RCTRL:
                global_manager.set('r_ctrl', 'down')
            if event.key == pygame.K_LCTRL:
                global_manager.set('l_ctrl', 'down')
            if event.key == pygame.K_ESCAPE:
                global_manager.set('typing', False)
                global_manager.set('message', '')
            if event.key == pygame.K_SPACE:
                if global_manager.get('typing'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), ' ')) #add space to message and set message to it
            if event.key == pygame.K_BACKSPACE:
                if global_manager.get('typing'):
                    global_manager.set('message', global_manager.get('message')[:-1]) #remove last character from message and set message to it

            key_codes = [pygame.K_a, pygame.K_b, pygame.K_c, pygame.K_d, pygame.K_e, pygame.K_f, pygame.K_g, pygame.K_h, pygame.K_i, pygame.K_j, pygame.K_k, pygame.K_l, pygame.K_m, pygame.K_n, pygame.K_o, pygame.K_p]
            key_codes += [pygame.K_q, pygame.K_r, pygame.K_s, pygame.K_t, pygame.K_u, pygame.K_v, pygame.K_w, pygame.K_x, pygame.K_y, pygame.K_z]
            key_codes += [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_0]
            lowercase_key_values = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
            uppercase_key_values = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')']

            for key_index in range(len(key_codes)):
                correct_key = False
                if event.key == key_codes[key_index]:
                    correct_key = True
                    if global_manager.get('typing') and not global_manager.get('capital'):
                        global_manager.set('message', utility.add_to_message(global_manager.get('message'), lowercase_key_values[key_index]))
                    elif global_manager.get('typing') and global_manager.get('capital'):
                        global_manager.set('message', utility.add_to_message(global_manager.get('message'), uppercase_key_values[key_index]))
                if correct_key:
                    break
                    
        if event.type == pygame.KEYUP:
            for button in global_manager.get('button_list'):
                if not global_manager.get('typing') or button.keybind_id == pygame.K_TAB or button.keybind_id == pygame.K_e:
                    if button.has_keybind:
                        if event.key == button.keybind_id:
                            button.on_release()
                            button.has_released = True
            if event.key == pygame.K_RSHIFT:
                global_manager.set('r_shift', 'up')
            if event.key == pygame.K_LSHIFT:
                global_manager.set('l_shift', 'up')
            if event.key == pygame.K_LCTRL:
                global_manager.set('l_ctrl', 'up')
            if event.key == pygame.K_RCTRL:
                global_manager.set('r_ctrl', 'up')
            if event.key == pygame.K_RETURN:
                if global_manager.get('typing'):
                    if global_manager.get('input_manager').taking_input:
                        #input_response = message
                        global_manager.get('input_manager').taking_input = False
                        text_tools.print_to_screen('Response: ' + global_manager.get('message'), global_manager)
                        input_manager.receive_input(global_manager.get('message'))
                        check_pointer_removal('not typing')
                    else:
                        text_tools.print_to_screen(global_manager.get('message'), global_manager)
                    global_manager.set('typing', False)
                    global_manager.set('message', '')
                else:
                    global_manager.set('typing', True)
    global_manager.set('old_lmb_down', global_manager.get('lmb_down'))
    global_manager.set('old_rmb_down', global_manager.get('rmb_down'))
    global_manager.set('old_mmb_down', global_manager.get('mmb_down'))
    lmb_down, mmb_down, rmb_down = pygame.mouse.get_pressed()
    global_manager.set('lmb_down', lmb_down)
    global_manager.set('mmb_down', mmb_down)
    global_manager.set('rmb_down', rmb_down)

    if not global_manager.get('old_rmb_down') == global_manager.get('rmb_down'): #if rmb changes
        if not global_manager.get('rmb_down'): #if user just released rmb
            clicked_button = False
            stopping = False
            if global_manager.get('current_instructions_page') == 'none':
                for button in global_manager.get('button_list'):
                    if button.touching_mouse() and global_manager.get('current_game_mode') in button.modes and button in global_manager.get('notification_list') and not stopping:
                        button.on_rmb_click()#prioritize clicking buttons that appear above other buttons and don't press the ones 
                        button.on_rmb_release()
                        clicked_button = True
                        stopping = True
            else:
                if global_manager.get('current_instructions_page').touching_mouse() and global_manager.get('current_game_mode') in global_manager.get('current_instructions_page').modes:
                    global_manager.get('current_instructions_page').on_rmb_click()
                    clicked_button = True
                    stopping = True
            if not stopping:
                for button in global_manager.get('button_list'):
                    if button.touching_mouse() and global_manager.get('current_game_mode') in button.modes:
                        button.on_rmb_click()
                        button.on_rmb_release()
                        clicked_button = True
            main_loop.manage_rmb_down(clicked_button, global_manager)

        #else:#if user just clicked rmb
            #mouse_origin_x, mouse_origin_y = pygame.mouse.get_pos()
            #global_manager.set('mouse_origin_x', mouse_origin_x)
            #global_manager.set('mouse_origin_y', mouse_origin_y)
            #global_manager.set('making_mouse_box', True)
            
    if not global_manager.get('old_lmb_down') == global_manager.get('lmb_down'):#if lmb changes
        if not global_manager.get('lmb_down'):#if user just released lmb
            clicked_button = False
            stopping = False
            if global_manager.get('current_instructions_page') == 'none':
                for button in global_manager.get('button_list'):
                    if button.touching_mouse() and global_manager.get('current_game_mode') in button.modes and (button in global_manager.get('notification_list')) and not stopping:
                        button.on_click()#prioritize clicking buttons that appear above other buttons and don't press the ones 
                        button.on_release()
                        clicked_button = True
                        stopping = True
            else:
                if global_manager.get('current_instructions_page').touching_mouse() and global_manager.get('current_game_mode') in global_manager.get('current_instructions_page').modes:
                    global_manager.get('current_instructions_page').on_click()
                    clicked_button = True
                    stopping = True
            if not stopping:
                for button in global_manager.get('button_list'):
                    if button.touching_mouse() and global_manager.get('current_game_mode') in button.modes:
                        button.on_click()
                        button.on_release()
                        clicked_button = True
            main_loop.manage_lmb_down(clicked_button, global_manager)#whether button was clicked or not determines whether characters are deselected
            
        else:#if user just clicked lmb
            mouse_origin_x, mouse_origin_y = pygame.mouse.get_pos()
            global_manager.set('mouse_origin_x', mouse_origin_x)
            global_manager.set('mouse_origin_y', mouse_origin_y)
            global_manager.set('making_mouse_box', True)

    if not global_manager.get('loading'):
        main_loop.update_display(global_manager)
    else:
        main_loop.draw_loading_screen(global_manager)
    current_time = time.time()
    global_manager.set('current_time', current_time)
    if global_manager.get('current_time') - global_manager.get('last_selection_outline_switch') > 1:
        global_manager.set('show_selection_outlines', utility.toggle(global_manager.get('show_selection_outlines')))
        global_manager.set('last_selection_outline_switch', time.time())
    #if global_manager.get('current_time') - global_manager.get('last_minimap_outline_switch') > 1:
    #    global_manager.set('show_minimap_outlines', utility.toggle(global_manager.get('show_minimap_outlines')))
    #    global_manager.set('last_minimap_outline_switch', time.time())
        
    for actor in global_manager.get('actor_list'):
        for current_image in actor.images:
            if not current_image.image_description == current_image.previous_idle_image and time.time() >= current_image.last_image_switch + 0.6:
                current_image.set_image(current_image.previous_idle_image)
    start_time = time.time()
    global_manager.set('start_time', start_time)

global_manager.set('current_time', time.time())
global_manager.set('last_selection_outline_switch', time.time())
    
pygame.quit()
