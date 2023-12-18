#Contains functions used when switching between parts of the game, like loading screen display

import time
from . import main_loop_utility, text_utility, actor_utility, minister_utility, scaling
from ..actor_types import tiles
import modules.constants.constants as constants
import modules.constants.status as status
import modules.constants.flags as flags

def cycle_player_turn(start_of_turn = False):
    '''
    Description:
        Selects the next unit in the turn order, or gives a message if none remain
    Input:
        boolean start_of_turn = False: Whether this is occuring automatically at the start of the turn or due to a player action during the turn
    Output:
        None
    '''
    turn_queue = status.player_turn_queue
    if len(turn_queue) == 0:
        if not start_of_turn: #print no units message if there are no units in turn queue
            text_utility.print_to_screen('There are no units left to move this turn.')
            actor_utility.calibrate_actor_info_display(status.mob_info_display, None, override_exempt=True)
    else:
        if len(turn_queue) == 1 and (not start_of_turn) and turn_queue[0] == status.displayed_mob: #only print no other units message if there is only 1 unit in turn queue and it is already selected
            text_utility.print_to_screen('There are no other units left to move this turn.')
        if constants.current_game_mode == 'europe' and not status.europe_grid in turn_queue[0].grids:
            set_game_mode('strategic')
        if turn_queue[0] != status.displayed_mob:
            turn_queue[0].selection_sound()
        else: 
            turn_queue.append(turn_queue.pop(0)) #if unit is already selected, move it to the end and shift to the next one
        actor_utility.calibrate_actor_info_display(status.mob_info_display, None, override_exempt=True)
        cycled_mob = turn_queue[0]
        cycled_mob.select()
        cycled_mob.move_to_front()
        if cycled_mob.grids[0].mini_grid != 'none':
            cycled_mob.grids[0].mini_grid.calibrate(cycled_mob.x, cycled_mob.y)
        else:
            actor_utility.calibrate_actor_info_display(status.tile_info_display, cycled_mob.images[0].current_cell.tile)
        if not start_of_turn:
            turn_queue.append(turn_queue.pop(0))

def set_game_mode(new_game_mode):
    '''
    Description:
        Changes the current game mode to the inputted game mode, changing which objects can be displayed and interacted with
    Input:
        string new_game_mode: Game mode that this switches to, like 'strategic'
    Output:
        None
    '''
    previous_game_mode = constants.current_game_mode
    if new_game_mode == previous_game_mode:
        return()
    else:
        if previous_game_mode in ['main_menu', 'new_game_setup'] and not new_game_mode in ['main_menu', 'new_game_setup']: #new_game_mode in ['strategic', 'ministers', 'europe']:
            constants.event_manager.clear()
            constants.sound_manager.play_random_music('europe')
        elif (not previous_game_mode in ['main_menu', 'new_game_setup']) and new_game_mode in ['main_menu', 'new_game_setup']: #game starts in 'none' mode so this would work on startup
            constants.event_manager.clear()
            constants.sound_manager.play_random_music('main menu')

        if not (new_game_mode == 'trial' or constants.current_game_mode == 'trial'): #the trial screen is not considered a full game mode by buttons that switch back to the previous game mode
            constants.previous_game_mode = constants.current_game_mode
        start_loading()
        constants.current_game_mode = new_game_mode
        if new_game_mode == 'strategic':
            constants.default_text_box_height = constants.font_size * 5.5
            constants.text_box_height = constants.default_text_box_height
        elif new_game_mode == 'main_menu':
            constants.default_text_box_height = constants.font_size * 5.5
            constants.text_box_height = constants.default_text_box_height
            status.text_list = [] #clear text box when going to main menu
        elif new_game_mode == 'ministers':
            actor_utility.calibrate_actor_info_display(status.tile_info_display, status.europe_grid.cell_list[0][0].tile) #calibrate tile info to Europe
        elif not new_game_mode in ['trial', 'new_game_setup']:
            constants.default_text_box_height = constants.font_size * 5.5
            constants.text_box_height = constants.default_text_box_height
        
    if previous_game_mode in ['strategic', 'europe', 'new_game_setup', 'ministers']:
        actor_utility.calibrate_actor_info_display(status.mob_info_display, None, override_exempt=True) #deselect actors/ministers and remove any actor info from display when switching screens
        actor_utility.calibrate_actor_info_display(status.tile_info_display, None, override_exempt=True)
        minister_utility.calibrate_minister_info_display(None)
        actor_utility.calibrate_actor_info_display(status.country_info_display, None)
        if new_game_mode == 'europe':
            if status.europe_grid.cell_list[0][0].contained_mobs:
                status.europe_grid.cell_list[0][0].contained_mobs[0].cycle_select()
            actor_utility.calibrate_actor_info_display(status.tile_info_display, status.europe_grid.cell_list[0][0].tile) #calibrate tile info to Europe
        elif new_game_mode == 'strategic':
            centered_cell = status.strategic_map_grid.find_cell(status.minimap_grid.center_x, status.minimap_grid.center_y)
            if centered_cell.tile != 'none':
                actor_utility.calibrate_actor_info_display(status.tile_info_display, centered_cell.tile)
                if centered_cell.visible and centered_cell.contained_mobs:
                    actor_utility.calibrate_actor_info_display(status.mob_info_display, centered_cell.contained_mobs[0])
                #calibrate tile info to minimap center
    if new_game_mode == 'ministers':
        constants.available_minister_left_index = -2
        minister_utility.update_available_minister_display()
        minister_utility.calibrate_minister_info_display(None)
        
    elif previous_game_mode == 'trial':
        minister_utility.calibrate_trial_info_display(status.defense_info_display, None)
        minister_utility.calibrate_trial_info_display(status.prosecution_info_display, None)

    if flags.startup_complete and not new_game_mode in ['main_menu', 'new_game_setup']:
        constants.notification_manager.update_notification_layout()

def create_strategic_map(from_save=False):
    '''
    Description:
        Generates grid terrains/resources/villages if not from save, and sets up tiles attached to each grid cell
    Input:
        None
    Output:
        None
    '''
    #text_tools.print_to_screen('Creating map...')
    main_loop_utility.update_display()

    for current_grid in status.grid_list:
        if current_grid.is_abstract_grid: #if europe/slave traders grid
            tiles.abstract_tile(False, {
                'grid': current_grid,
                'image': current_grid.tile_image_id,
                'name': current_grid.name,
                'modes': current_grid.modes
            })
        else:
            input_dict = {
                'grid': current_grid,
                'image': 'misc/empty.png',
                'name': 'default',
                'modes': ['strategic'],
                'show_terrain': True,
            }
            if (not from_save) and current_grid == status.strategic_map_grid:
                current_grid.generate_terrain()
            for cell in current_grid.get_flat_cell_list():
                if (not from_save) and current_grid == status.strategic_map_grid and (cell.y == 0 or cell.y == 1):
                    cell.set_visibility(True)
                input_dict['coordinates'] = (cell.x, cell.y)
                tiles.tile(False, input_dict)
            if current_grid == status.strategic_map_grid:
                current_grid.set_resources()

def start_loading():
    '''
    Description:
        Records when loading started and displays a loading screen when the program is launching or switching between game modes
    Input:
        None
    Output:
        None
    '''
    flags.loading = True
    flags.loading_start_time = time.time()
    main_loop_utility.update_display()

def to_main_menu(override = False):
    '''
    Description:
        Exits the game to the main menu without saving
    Input:
        boolean override = False: If True, forces game to exit to main menu regardless of current game circumstances
    Output:
        None
    '''
    actor_utility.calibrate_actor_info_display(status.mob_info_display, None, override_exempt=True)
    actor_utility.calibrate_actor_info_display(status.tile_info_display, None)
    minister_utility.calibrate_minister_info_display(None)
    for current_actor in status.actor_list:
        current_actor.remove_complete()
    for current_grid in status.grid_list:
        current_grid.remove_complete()
    for current_village in status.village_list:
        current_village.remove_complete()
    for current_minister in status.minister_list:
        current_minister.remove_complete()
    for current_lore_mission in status.lore_mission_list:
        current_lore_mission.remove_complete()
    for current_die in status.dice_list:
        current_die.remove_complete()
    status.loan_list = []
    status.displayed_mob = None
    status.displayed_tile = None
    constants.message = ''
    status.player_turn_queue = []
    status.current_lore_mission = None
    if status.current_instructions_page:
        status.current_instructions_page.remove_complete()
        status.current_instructions_page = None
    if status.current_country:
        status.current_country.deselect()
    for current_completed_lore_type in constants.completed_lore_mission_types:
        status.lore_types_effects_dict[current_completed_lore_type].remove()
    set_game_mode('main_menu')

def force_minister_appointment():
    '''
    Description:
        Navigates to the ministers mode and instructs player to fill all minister positions when an action has been prevented due to not having all positions
            filled
    Input:
        None
    Output:
        None
    '''
    set_game_mode('ministers')
    constants.notification_manager.display_notification({
        'message': 'You cannot do that until all minister positions have been appointed. /n /n',
        'notification_type': 'default'
    })
