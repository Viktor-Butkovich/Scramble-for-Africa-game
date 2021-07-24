import time
from . import main_loop
from . import text_tools
from . import actors
from . import label

def set_game_mode(new_game_mode, global_manager):
    text_list = []
    previous_game_mode = global_manager.get('current_game_mode')
    if new_game_mode == previous_game_mode:
        return()
    elif new_game_mode == 'strategic':
        start_loading(global_manager)
        global_manager.set('current_game_mode', 'strategic')
        global_manager.set('default_text_box_height', 185)
        global_manager.set('text_box_height', global_manager.get('default_text_box_height'))
        copy_tile_list = global_manager.get('tile_list')
        for current_tile in copy_tile_list:
            current_tile.remove()
        create_strategic_map(global_manager)
        text_tools.print_to_screen("Entering strategic map", global_manager)
    else:
        global_manager.set('current_game_mode', new_game_mode)

def create_strategic_map(global_manager):
    text_tools.print_to_screen('Creating map...', global_manager)
    main_loop.update_display(global_manager)
    #for current_cell in global_manager.get('strategic_map_grid').cell_list: #recreates the tiles that were deleted upon switching modes, tiles match the stored cell terrain types
    #    new_terrain = actors.tile_class((current_cell.x, current_cell.y), current_cell.grid, 'misc/empty.png', 'default', ['strategic'], True, global_manager) #creates a terrain tile that will be modified to the grid cell's terrain type
    #global_manager.get('strategic_map_grid').set_resources()
    #for current_cell in global_manager.get('minimap_grid').cell_list:
    #    new_terrain = actors.tile_class((current_cell.x, current_cell.y), current_cell.grid, 'misc/empty.png', 'default', ['strategic'], True, global_manager)
    #global_manager.get('minimap_grid').set_resources()

    for current_grid in global_manager.get('grid_list'):
        for current_cell in current_grid.cell_list:
            new_terrain = actors.tile_class((current_cell.x, current_cell.y), current_grid, 'misc/empty.png', 'default', ['strategic'], True, global_manager)
            #if(current_cell.tile == 'none'):
            #    print(str(current_cell.x) + ', ' + str(current_cell.y))
        current_grid.set_resources()

def start_loading(global_manager):
    global_manager.set('loading', True)
    global_manager.set('loading_start_time', time.time())
    main_loop.update_display(global_manager)#draw_loading_screen()
