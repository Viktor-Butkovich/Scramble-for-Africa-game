import random
from . import text_tools
from . import actor_utility

def end_turn(global_manager):
    for current_mob in global_manager.get('mob_list'):
        current_mob.selected = False
    actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('mob_info_display_list'), 'none')
    actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('tile_info_display_list'), 'none')
    global_manager.set('player_turn', False)
    text_tools.print_to_screen("Ending turn", global_manager)
    for current_mob in global_manager.get('mob_list'):
        current_mob.end_turn_move()
    for current_resource_building in global_manager.get('resource_building_list'):
        current_resource_building.produce()
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
        adjust_prices(global_manager)

def adjust_prices(global_manager):
    num_increased = 2
    num_decreased = 1
    
    for i in range(2):
        changed_commodity = random.choice(global_manager.get('commodity_types'))
        while changed_commodity == 'consumer goods':
            changed_commodity = random.choice(global_manager.get('commodity_types'))
        global_manager.get('commodity_prices')[changed_commodity] += 1
        
    for i in range(1):
        changed_commodity = random.choice(global_manager.get('commodity_types'))
        while changed_commodity == 'consumer goods':
            changed_commodity = random.choice(global_manager.get('commodity_types'))
        if global_manager.get('commodity_prices')[changed_commodity] > 1:
            global_manager.get('commodity_prices')[changed_commodity] -= 1

    consumer_goods_roll = random.randrange(1, 7)
    if consumer_goods_roll == 1:
        global_manager.get('commodity_prices')['consumer goods'] += 1
    elif consumer_goods_roll >= 5:
        if global_manager.get('commodity_prices')['consumer goods'] > 1:
            global_manager.get('commodity_prices')['consumer goods'] -= 1

    global_manager.get('commodity_prices_label').update_label()
