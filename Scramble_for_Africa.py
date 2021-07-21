#separate files:
#main,
#classes:
#   global_manager_template
#   input_manager_template
#   button_class
#   label
#       notification
#       instructions_page
#   bar
#       actor_bar
#   grid
#   cell
#   free_image
#       loading_image_class
#   actor_image
#       button_image
#       tile_image
#   actor
#       mob
#           explorer
#       tile_class
#           overlay_tile

#functions:
#   roll
#   remove_from_list
#   get_input
#   text
#   rect_to_surface
#   message_width
#   display_image
#   display_image_angle
#   manage_text_list
#   add_to_message
#   print_to_screen
#   print_to_previous_message
#   clear_message
#   toggle
#   find_object_distance #find grid coordinate distance between two objects with x and y attributes
#   find_coordinate_distance #find grid coordinate distance between two tuples of coordinates
#   set_game_mode
#   create_strategic_map
#   draw_text_box
#   update_display
#   draw_loading_screen
#   start_loading
#   manage_tooltip_drawing
#   create_image_dict
#   display_notification
#   notification_to_front
#   show_tutorial_notifications
#   manage_rmb_down
#   manage_lmb_down
#   scale_coordinates
#   scale_width
#   scale_height
#   generate_article
#   display_instructions_page

#to do:
#create relevant actors
#review rules
#trigger button outlines when clicking, currently only works when pressing
#add more docstrings and comments
#move classes and functions to different files
#add global_manager as input to certain docstrings
#
#done since 6/15
#remove varision-specific program elements
#convert old game mode to a strategic game mode, removing other game modes
#add correct terrain types with corresponding colors and/or images
#change strategic map to correct size
#added docstring descriptions of certain classes and functions
#removed obsolete showing and can_show() variables and functions, respectively
#added images for all resources
#remove all global variables
#make better images for all resources
#add mobs
#add selecting and mouse boxes
#add movement and basic movement restrictions

import pygame
import time
import random
import math

import modules.scaling as scaling
import modules.main_loop as main_loop
import modules.text_tools as text_tools
import modules.utility as utility
import modules.dice as dice
import modules.notification_tools as notification_tools
import modules.images as images
import modules.label as label
import modules.button as button
import modules.game_transitions as game_transitions
import modules.actors as actors
import modules.grids as grids
import modules.bars as bars
import modules.data_managers as data_managers

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
color_dict = {'black': (0, 0, 0), 'white': (255, 255, 255), 'light gray': (230, 230, 230), 'dark gray': (150, 150, 150), 'red': (255, 0, 0), 'dark green': (0, 150, 0), 'green': (0, 200, 0), 'bright green': (0, 255, 0), 'blue': (0, 0, 255), 'yellow': (255, 255, 0), 'brown': (132, 94, 59)}
global_manager.set('color_dict', color_dict)
terrain_list = ['clear', 'mountain', 'hills', 'jungle', 'swamp', 'desert']
global_manager.set('terrain_list', terrain_list)
terrain_colors = {'clear': (150, 200, 104), 'hills': (50, 205, 50), 'jungle': (0, 100, 0), 'water': (0, 0, 200), 'mountain': (100, 100, 100), 'swamp': (100, 100, 50), 'desert': (255, 248, 104), 'none': (0, 0, 0)}
global_manager.set('terrain_colors', terrain_colors)
global_manager.get('game_display').fill(global_manager.get('color_dict')['white'])
global_manager.set('button_list', [])
global_manager.set('current_instructions_page', 'none')
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
global_manager.set('tile_list', [])
global_manager.set('overlay_tile_list', [])
global_manager.set('notification_list', [])
global_manager.set('label_list', [])
global_manager.set('notification_queue', [])
pygame.key.set_repeat(300, 200)
global_manager.set('crashed', False)
global_manager.set('lmb_down', False)
global_manager.set('rmb_down', False)
global_manager.set('mmb_down', False)
global_manager.set('typing', False)
global_manager.set('message', '')
global_manager.set('show_grid_lines', True)
global_manager.set('show_text_box', True)
global_manager.set('mouse_origin_x', 0)
global_manager.set('mouse_origin_y', 0)
global_manager.set('mouse_destination_x', 0)
mouse_destination_y = 0
global_manager.set('mouse_destination_y', 0)
global_manager.set('making_mouse_box', False)

global_manager.set('r_shift', 'up')
global_manager.set('l_shift', 'up')
global_manager.set('capital', False)
global_manager.set('r_ctrl', 'up')
global_manager.set('l_ctrl', 'up')
global_manager.set('ctrl', 'up')
global_manager.set('start_time', time.time())
global_manager.set('current_time', time.time())
mouse_moved_time = time.time()
global_manager.set('mouse_moved_time', time.time())
old_mouse_x, old_mouse_y = pygame.mouse.get_pos()#used in tooltip drawing timing
global_manager.set('old_mouse_x', old_mouse_x)
global_manager.set('old_mouse_y', old_mouse_y)
notification_tools.show_tutorial_notifications(global_manager)
global_manager.set('loading_image', images.loading_image_class('misc/loading.png', global_manager))
global_manager.set('current_game_mode', 'none')
global_manager.set('input_manager', data_managers.input_manager_template(global_manager))
global_manager.set('background_image', images.free_image('misc/background.png', (0, 0), global_manager.get('display_width'), global_manager.get('display_height'), ['strategic'], global_manager))
#strategic_map_grid = grids.grid(scaling.scale_coordinates(729, 150, global_manager), scaling.scale_width(870, global_manager), scaling.scale_height(810, global_manager), 64, 60, True, color_dict['dark green'], ['strategic']) #other map sizes
#strategic_map_grid = grids.grid(scaling.scale_coordinates(729, 150, global_manager), scaling.scale_width(870, global_manager), scaling.scale_height(810, global_manager), 32, 30, True, color_dict['dark green'], ['strategic'])
#strategic_map_grid = grids.grid(scaling.scale_coordinates(695, 150, global_manager), scaling.scale_width(864, global_manager), scaling.scale_height(810, global_manager), 16, 15, color_dict['dark green'], ['strategic'], global_manager) #54 by 54
#default
#strategic_map_grid = grids.grid(scaling.scale_coordinates(695, 50, global_manager), scaling.scale_width(960, global_manager), scaling.scale_height(900, global_manager), 16, 15, color_dict['dark green'], ['strategic'], global_manager) #60 by 60
grid_height = 450
grid_width = 480
strategic_map_grid = grids.grid(scaling.scale_coordinates(global_manager.get('display_width') - (grid_width + 100), global_manager.get('display_height') - (grid_height + 25), global_manager), scaling.scale_width(grid_width, global_manager), scaling.scale_height(grid_height, global_manager), 16, 15, color_dict['dark green'], ['strategic'], True, global_manager) #60 by 60
global_manager.set('strategic_map_grid', strategic_map_grid)

minimap_grid = grids.mini_grid(scaling.scale_coordinates(global_manager.get('display_width') - (grid_width + 100), global_manager.get('display_height') - (2 * (grid_height + 25)), global_manager), scaling.scale_width(grid_width, global_manager), scaling.scale_height(grid_height, global_manager), 5, 5, color_dict['dark green'], ['strategic'], global_manager, global_manager.get('strategic_map_grid')) #60 by 60

global_manager.set('minimap_grid', minimap_grid)
game_transitions.set_game_mode('strategic', global_manager)
roll_label = label.label(scaling.scale_coordinates(580, global_manager.get('default_display_height') - 50, global_manager), scaling.scale_width(90, global_manager), scaling.scale_height(50, global_manager), ['strategic'], 'misc/small_label.png', 'Roll: ', global_manager) #coordinates, ideal_width, minimum_height, modes, image_id, message, global_manager
global_manager.set('roll_label', roll_label)

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
toggle_grid_lines_button = button.button_class(scaling.scale_coordinates(global_manager.get('default_display_width') - 50, global_manager.get('default_display_height') - 50, global_manager), scaling.scale_width(50, global_manager), scaling.scale_height(50, global_manager), 'blue', 'toggle grid lines', pygame.K_g, ['strategic'], 'misc/grid_line_button.png', global_manager)
instructions_button = button.button_class(scaling.scale_coordinates(global_manager.get('default_display_width') - 50, global_manager.get('default_display_height') - 170, global_manager), scaling.scale_width(50, global_manager), scaling.scale_height(50, global_manager), 'blue', 'instructions', pygame.K_i, ['strategic'], 'misc/instructions.png', global_manager)
toggle_text_box_button = button.button_class(scaling.scale_coordinates(75, global_manager.get('default_display_height') - 50, global_manager), scaling.scale_width(50, global_manager), scaling.scale_height(50, global_manager), 'blue', 'toggle text box', pygame.K_t, ['strategic'], 'misc/toggle_text_box_button.png', global_manager)
while True: #to do: prevent 2nd row from the bottom of the map grid from ever being completely covered with water due to unusual river RNG, causing infinite loop here, or start increasing y until land is found
    start_x = random.randrange(0, global_manager.get('strategic_map_grid').coordinate_width)
    start_y = 1
    if not(global_manager.get('strategic_map_grid').find_cell(start_x, start_y).terrain == 'water'): #if there is land at that coordinate, break and allow explorer to spawn there
        break
new_explorer = actors.explorer((start_x, start_y), global_manager.get('strategic_map_grid'), 'mobs/explorer/default.png', 'Explorer', ['strategic'], global_manager)#self, coordinates, grid, image_id, name, modes, global_manager
global_manager.get('minimap_grid').calibrate(start_x, start_y)
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
            if event.key == pygame.K_a:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'a'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'A'))
            if event.key == pygame.K_b:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'b'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'B'))
            if event.key == pygame.K_c:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'c'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'C'))
            if event.key == pygame.K_d:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'd'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'D'))
            if event.key == pygame.K_e:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'e'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'E'))
            if event.key == pygame.K_f:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'f'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'F'))
            if event.key == pygame.K_g:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'g'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'G'))
            if event.key == pygame.K_h:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'h'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'H'))
            if event.key == pygame.K_i:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'i'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'I'))
            if event.key == pygame.K_j:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'j'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'J'))
            if event.key == pygame.K_k:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'k'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'K'))
            if event.key == pygame.K_l:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'l'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'L'))
            if event.key == pygame.K_m:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'm'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'M'))
            if event.key == pygame.K_n:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'n'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'N'))
            if event.key == pygame.K_o:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'o'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'O'))
            if event.key == pygame.K_p:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'p'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'P'))
            if event.key == pygame.K_q:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'q'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'Q'))
            if event.key == pygame.K_r:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'r'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'R'))
            if event.key == pygame.K_s:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 's'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'S'))
            if event.key == pygame.K_t:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 't'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'T'))
            if event.key == pygame.K_u:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'u'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'U'))
            if event.key == pygame.K_v:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'v'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'V'))
            if event.key == pygame.K_w:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'w'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'W'))
            if event.key == pygame.K_x:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'x'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'X'))
            if event.key == pygame.K_y:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'y'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'Y'))
            if event.key == pygame.K_z:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'z'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), 'Z'))

            if event.key == pygame.K_1:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), '1'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), '!'))
            if event.key == pygame.K_2:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), '2'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), '@'))
            if event.key == pygame.K_3:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), '3'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), '#'))
            if event.key == pygame.K_4:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), '4'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), '$'))
            if event.key == pygame.K_5:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), '5'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), '%'))
            if event.key == pygame.K_6:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), '6'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), '^'))
            if event.key == pygame.K_7:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), '7'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), '&'))
            if event.key == pygame.K_8:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), '8'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), '*'))
            if event.key == pygame.K_9:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), '9'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), '('))
            if event.key == pygame.K_0:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), '0'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', utility.add_to_message(global_manager.get('message'), ')'))
                    
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

        else:#if user just clicked rmb
            mouse_origin_x, mouse_origin_y = pygame.mouse.get_pos()
            global_manager.set('mouse_origin_x', mouse_origin_x)
            global_manager.set('mouse_origin_y', mouse_origin_y)
            global_manager.set('making_mouse_box', True)
            
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
    for actor in global_manager.get('actor_list'):
        if not actor.image.image_description == actor.image.previous_idle_image and time.time() >= actor.image.last_image_switch + 0.6:
            actor.image.set_image(actor.image.previous_idle_image)
    start_time = time.time()
    global_manager.set('start_time', start_time)
pygame.quit()
