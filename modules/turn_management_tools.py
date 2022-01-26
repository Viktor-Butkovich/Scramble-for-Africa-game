#Contains functions that manage what happens at the end of each turn, like worker upkeep and price changes

import random

from . import text_tools
from . import actor_utility
from . import market_tools
from . import notification_tools

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
    #text_tools.print_to_screen("Ending turn", global_manager)
    for current_mob in global_manager.get('mob_list'):
        current_mob.end_turn_move()
    for current_cell in global_manager.get('strategic_map_grid').cell_list:
        current_tile = current_cell.tile
        while current_tile.get_inventory_used() > current_tile.inventory_capacity:
            discarded_commodity = random.choice(current_tile.get_held_commodities())
            current_tile.change_inventory(discarded_commodity, -1)
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
    text_tools.print_to_screen("", global_manager)
    text_tools.print_to_screen("Turn " + str(global_manager.get('turn') + 1), global_manager)
    if not first_turn:
        manage_production(global_manager)
        manage_subsidies(global_manager) #subsidies given before public opinion changes
        manage_public_opinion(global_manager)
        manage_upkeep(global_manager)
        manage_financial_report(global_manager)
        manage_worker_price_changes(global_manager)
    
    global_manager.set('player_turn', True)
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

def manage_production(global_manager):
    '''
    Description:
        Orders each work crew in a production building to attempt commodity production and displays a production report of commodities for which production was attempted and how much of each was produced
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    global_manager.set('attempted_commodities', [])
    for current_commodity in global_manager.get('collectable_resources'):
        global_manager.get('commodities_produced')[current_commodity] = 0
    for current_resource_building in global_manager.get('resource_building_list'):
        current_resource_building.produce()
    attempted_commodities = global_manager.get('attempted_commodities')
    displayed_commodities = []
    if not len(global_manager.get('attempted_commodities')) == 0: #if any attempted, do production report
        notification_text = "Production report: /n /n "
        while len(displayed_commodities) < len(attempted_commodities):
            max_produced = 0
            max_commodity = 'none'
            for current_commodity in attempted_commodities:
                if not current_commodity in displayed_commodities:
                    if global_manager.get('commodities_produced')[current_commodity] >= max_produced:
                        max_commodity = current_commodity
                        max_produced = global_manager.get('commodities_produced')[current_commodity]
            displayed_commodities.append(max_commodity)
            notification_text += (max_commodity.capitalize() + ": " + str(max_produced) + ' /n ')
        notification_tools.display_notification(notification_text, 'default', global_manager)       

def manage_upkeep(global_manager):
    '''
    Description:
        Pays upkeep for all units at the end of a turn. Currently, only workers cost upkeep
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    african_worker_upkeep = round(global_manager.get('num_african_workers') * global_manager.get('african_worker_upkeep'), 1)
    european_worker_upkeep = round(global_manager.get('num_european_workers') * global_manager.get('european_worker_upkeep'), 1)
    slave_worker_upkeep = round(global_manager.get('num_slave_workers') * global_manager.get('slave_worker_upkeep'), 1)
    num_workers = global_manager.get('num_african_workers') + global_manager.get('num_european_workers') + global_manager.get('num_slave_workers')
    total_upkeep = round(african_worker_upkeep + european_worker_upkeep + slave_worker_upkeep, 1)
    global_manager.get('money_tracker').change(round(-1 * total_upkeep, 1), 'worker upkeep')
    
    #text_tools.print_to_screen("You paid a total of " + str(total_upkeep) + " money to your " + str(num_workers) + " workers.", global_manager) #described in financial report

def manage_public_opinion(global_manager):
    '''
    Description:
        Changes public opinion at the end of the turn to move back toward 50
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    current_public_opinion = round(global_manager.get('public_opinion'))
    if current_public_opinion < 50:
        global_manager.get('public_opinion_tracker').change(1)
        text_tools.print_to_screen("Trending toward a neutral attitude, public opinion toward your company increased from " + str(current_public_opinion) + " to " + str(current_public_opinion + 1), global_manager)
    elif current_public_opinion > 50:
        global_manager.get('public_opinion_tracker').change(-1)
        text_tools.print_to_screen("Trending toward a neutral attitude, public opinion toward your company decreased from " + str(current_public_opinion) + " to " + str(current_public_opinion - 1), global_manager)
    
def manage_subsidies(global_manager):
    '''
    Description:
        Receives subsidies at the end of the turn based on public opinion
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    subsidies_received = round(global_manager.get('public_opinion') / 10, 1) #4.9 for 49 public opinion
    text_tools.print_to_screen("You received " + str(subsidies_received) + " money in subsidies from the government based on your public opinion and colonial efforts", global_manager)
    global_manager.get('money_tracker').change(subsidies_received, 'subsidies')


def manage_financial_report(global_manager):
    '''
    Description:
        Displays a financial report at the end of the turn, showing revenue in each area, costs in each area, and total profit from the last turn
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    financial_report_text = global_manager.get('money_tracker').prepare_financial_report()
    notification_tools.display_notification(financial_report_text, 'default', global_manager)
    global_manager.set('previous_financial_report', financial_report_text)
    global_manager.get('money_tracker').reset_transaction_history()

def manage_worker_price_changes(global_manager):
    '''
    Description:
        Randomly changes the prices of slave purchase and European worker upkeep at the end of the turn, generally trending down to compensate for increases when recruited
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    european_worker_roll = random.randrange(1, 7)
    if european_worker_roll >= 5:
        current_price = global_manager.get('european_worker_upkeep')
        changed_price = round(current_price - global_manager.get('worker_upkeep_fluctuation_amount'), 1)
        if changed_price >= global_manager.get('min_european_worker_upkeep'):
            global_manager.set('european_worker_upkeep', changed_price)
            text_tools.print_to_screen("An influx of workers from Europe has decreased the upkeep of European workers from " + str(current_price) + " to " + str(changed_price) + ".", global_manager)
    elif european_worker_roll == 1:
        current_price = global_manager.get('european_worker_upkeep')
        changed_price = round(current_price + global_manager.get('worker_upkeep_fluctuation_amount'), 1)
        global_manager.set('european_worker_upkeep', changed_price)
        text_tools.print_to_screen("An shortage of workers from Europe has increased the upkeep of European workers from " + str(current_price) + " to " + str(changed_price) + ".", global_manager)

    slave_worker_roll = random.randrange(1, 7)
    if slave_worker_roll >= 5:
        current_price = global_manager.get('recruitment_costs')['slave worker']
        changed_price = round(current_price - global_manager.get('slave_recruitment_cost_fluctuation_amount'), 1)
        if changed_price >= global_manager.get('min_slave_worker_recruitment_cost'):
            global_manager.get('recruitment_costs')['slave worker'] = changed_price
            text_tools.print_to_screen("An influx of captured slaves has decreased the purchase cost of slave workers from " + str(current_price) + " to " + str(changed_price) + ".", global_manager)
    elif slave_worker_roll == 1:
        current_price = global_manager.get('recruitment_costs')['slave worker']
        changed_price = round(current_price + global_manager.get('slave_recruitment_cost_fluctuation_amount'), 1)
        global_manager.get('recruitment_costs')['slave worker'] = changed_price
        text_tools.print_to_screen("A shortage of captured slaves has increased the purchase cost of slave workers from " + str(current_price) + " to " + str(changed_price) + ".", global_manager)
        

