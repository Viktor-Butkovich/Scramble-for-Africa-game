#Contains functions that manage what happens at the end of each turn, like worker upkeep and price changes

import random

from . import text_tools
from . import actor_utility
from . import market_tools

def end_turn(global_manager):
    '''
    Description:
        Ends the turn, completing any pending movements, removing any commodities that can't be stored, and doing resource production
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    global_manager.set('end_turn_selected_mob', global_manager.get('displayed_mob'))
    global_manager.set('player_turn', False)
    text_tools.print_to_screen("Ending turn", global_manager)
    for current_mob in global_manager.get('mob_list'):
        current_mob.end_turn_move()
    for current_cell in global_manager.get('strategic_map_grid').cell_list:
        current_tile = current_cell.tile
        while current_tile.get_inventory_used() > current_tile.inventory_capacity:
            discarded_commodity = random.choice(current_tile.get_held_commodities())
            current_tile.change_inventory(discarded_commodity, -1)
    for current_resource_building in global_manager.get('resource_building_list'):
        current_resource_building.produce()
    manage_upkeep(global_manager)
    start_turn(global_manager, False)

def start_turn(global_manager, first_turn):
    '''
    Description:
        Starts the turn, giving all units their maximum movement points and adjusting market prices
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    global_manager.set('player_turn', True)
    text_tools.print_to_screen("", global_manager)
    text_tools.print_to_screen("Starting turn", global_manager)
    global_manager.get('turn_tracker').change(1)
    for current_mob in global_manager.get('mob_list'):
        current_mob.reset_movement_points()
    if not first_turn:
        market_tools.adjust_prices(global_manager)#adjust_prices(global_manager)
    for current_village in global_manager.get('village_list'):
        roll = random.randrange(1, 7)
        if roll <= 2: #1-2
            current_village.change_aggressiveness(-1)
        #3-4 does nothing
        elif roll >= 5: #5-6
            current_village.change_aggressiveness(1)

        roll = random.randrange(1, 7)
        second_roll = random.randrange(1, 7)
        if roll == 6 and second_roll == 6:
            current_village.change_population(1)
            
    end_turn_selected_mob = global_manager.get('end_turn_selected_mob')
    if not end_turn_selected_mob == 'none':
        end_turn_selected_mob.select()
        actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('tile_info_display_list'), end_turn_selected_mob.images[0].current_cell.tile)
    else: #if no mob selected at end of turn, calibrate to minimap tile to show any changes
        if not global_manager.get('displayed_tile') == 'none':
            actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('tile_info_display_list'), global_manager.get('displayed_tile'))

def manage_upkeep(global_manager):
    '''
    Description:
        Pays upkeep for all units at the beginning of the turn
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    num_workers = global_manager.get('num_workers')
    worker_upkeep = global_manager.get('worker_upkeep')
    total_upkeep = num_workers * worker_upkeep
    global_manager.get('money_tracker').change(-1 * total_upkeep)
    text_tools.print_to_screen("You paid " + str(worker_upkeep) + " money for each of your " + str(num_workers) + " workers, totaling to " + str(total_upkeep) + " money", global_manager)

