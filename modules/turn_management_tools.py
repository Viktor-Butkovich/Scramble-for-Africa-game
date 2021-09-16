import random

from . import text_tools
from . import actor_utility
from . import market_tools

def end_turn(global_manager):
    #for current_mob in global_manager.get('mob_list'):
    #    current_mob.selected = False
    #actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('mob_info_display_list'), 'none')
    #actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('tile_info_display_list'), 'none')
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
    #do things that happen at end of turn
    start_turn(global_manager, False)

def start_turn(global_manager, first_turn):
    global_manager.set('player_turn', True)
    text_tools.print_to_screen("", global_manager)
    text_tools.print_to_screen("Starting turn", global_manager)
    global_manager.get('turn_tracker').change(1)
    for current_mob in global_manager.get('mob_list'):
        current_mob.reset_movement_points()
    if not first_turn:
        market_tools.adjust_prices(global_manager)#adjust_prices(global_manager)
    end_turn_selected_mob = global_manager.get('end_turn_selected_mob')
    if not end_turn_selected_mob == 'none':
        end_turn_selected_mob.select()
    else: #if no mob selected at end of turn, calibrate to minimap tile to show any changes
        if not global_manager.get('displayed_tile') == 'none':
            actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('tile_info_display_list'), global_manager.get('displayed_tile'))
    #actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('mob_info_display_list'), global_manager.get('displayed_mob')) #update any tile/mob info that changed
    #actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('tile_info_display_list'), global_manager.get('displayed_tile'))

def manage_upkeep(global_manager):
    num_workers = global_manager.get('num_workers')
    worker_upkeep = global_manager.get('worker_upkeep')
    total_upkeep = num_workers * worker_upkeep
    global_manager.get('money_tracker').change(-1 * total_upkeep)
    text_tools.print_to_screen("You paid " + str(worker_upkeep) + " money for each of your " + str(num_workers) + " workers, totaling to " + str(total_upkeep) + " money", global_manager)

