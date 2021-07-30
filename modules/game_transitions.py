import time
from . import main_loop
from . import text_tools
from . import tiles

def set_game_mode(new_game_mode, global_manager):
    '''
    Input:
        string representing the game mode to switch to, global_manager_template object
    Output:
        Changes the game mode to the inputted game mode, changing which objects can be displayed and interacted with
    '''
    text_list = []
    previous_game_mode = global_manager.get('current_game_mode')
    if new_game_mode == previous_game_mode:
        return()
    elif new_game_mode == 'strategic':
        start_loading(global_manager)
        global_manager.set('current_game_mode', 'strategic')
        global_manager.set('default_text_box_height', 185)
        global_manager.set('text_box_height', global_manager.get('default_text_box_height'))
        #copy_tile_list = global_manager.get('tile_list')
        #for current_tile in copy_tile_list:
        #    current_tile.remove()
        #create_strategic_map(global_manager)
        text_tools.print_to_screen("Entering strategic map", global_manager)
    elif new_game_mode == 'europe':
        start_loading(global_manager)
        global_manager.set('current_game_mode', 'europe')
        text_tools.print_to_screen("Entering European Company Headquarters", global_manager)
    else:
        global_manager.set('current_game_mode', new_game_mode)
    for current_mob in global_manager.get('mob_list'):
        current_mob.selected = False

def create_strategic_map(global_manager):
    '''
    Input:
        global_manager_template object
    Output:
        Creates a tile object for each grid cell and randomly sets their resources
    '''
    text_tools.print_to_screen('Creating map...', global_manager)
    main_loop.update_display(global_manager)

    for current_grid in global_manager.get('grid_list'):
        if current_grid in global_manager.get('abstract_grid_list'):
            new_terrain = tiles.abstract_tile(current_grid, current_grid.tile_image_id, current_grid.name, ['strategic', 'europe'], global_manager)
        else:
            for current_cell in current_grid.cell_list:
                new_terrain = tiles.tile((current_cell.x, current_cell.y), current_grid, 'misc/empty.png', 'default', ['strategic'], True, global_manager)
            current_grid.set_resources()

def start_loading(global_manager):
    '''
    Input:
        global_manager_template object
    Output:
        Records when loading started and start loading the game
    '''
    global_manager.set('loading', True)
    global_manager.set('loading_start_time', time.time())
    main_loop.update_display(global_manager)#draw_loading_screen()
