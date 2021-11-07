#Contains functions used when switching between parts of the game, like loading screen display

import time
from . import main_loop_tools
from . import text_tools
from . import tiles
from . import actor_utility

def set_game_mode(new_game_mode, global_manager):
    '''
    Description:
        Changes the current game mode to the inputted game mode, changing which objects can be displayed and interacted with
    Input:
        string new_game_mode: Game mode that this switches to, like 'strategic', global_manager_template object
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    text_list = []
    previous_game_mode = global_manager.get('current_game_mode')
    if new_game_mode == previous_game_mode:
        return()
    else:
        start_loading(global_manager)
        if new_game_mode == 'strategic':
            global_manager.set('current_game_mode', 'strategic')
            global_manager.set('default_text_box_height', 185)
            global_manager.set('text_box_height', global_manager.get('default_text_box_height'))
            text_tools.print_to_screen("Entering strategic map", global_manager)
            centered_cell_x, centered_cell_y = global_manager.get('minimap_grid').center_x, global_manager.get('minimap_grid').center_y
            actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('tile_info_display_list'), global_manager.get('strategic_map_grid').find_cell(centered_cell_x, centered_cell_y).tile)
                #calibrate tile info to minimap center
        elif new_game_mode == 'europe':
            global_manager.set('current_game_mode', 'europe')
            text_tools.print_to_screen("Entering European Company Headquarters", global_manager)
            actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('tile_info_display_list'), global_manager.get('europe_grid').cell_list[0].tile) #calibrate tile info to Europe
        elif new_game_mode == 'main menu':
            global_manager.set('current_game_mode', 'main_menu')
        else:
            global_manager.set('default_text_box_height', 185)
            global_manager.set('text_box_height', global_manager.get('default_text_box_height'))
            global_manager.set('current_game_mode', new_game_mode)
    for current_mob in global_manager.get('mob_list'):
        current_mob.selected = False
    actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('mob_info_display_list'), 'none') #remove any actor info from display when deselecting
    
def create_strategic_map(global_manager):
    '''
    Description:
        Creates a tile attached to each cell of each grid and randomly sets resources and villages when applicable
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    text_tools.print_to_screen('Creating map...', global_manager)
    main_loop_tools.update_display(global_manager)

    for current_grid in global_manager.get('grid_list'):
        if current_grid in global_manager.get('abstract_grid_list'): #if europe grid
            new_terrain = tiles.abstract_tile(current_grid, current_grid.tile_image_id, current_grid.name, ['strategic', 'europe'], global_manager)
        else:
            for current_cell in current_grid.cell_list:
                new_terrain = tiles.tile((current_cell.x, current_cell.y), current_grid, 'misc/empty.png', 'default', ['strategic'], True, global_manager)
            current_grid.set_resources()

def start_loading(global_manager):
    '''
    Description:
        Records when loading started and displays a loading screen when the program is launching or switching between game modes
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    global_manager.set('loading', True)
    global_manager.set('loading_start_time', time.time())
    main_loop_tools.update_display(global_manager)

