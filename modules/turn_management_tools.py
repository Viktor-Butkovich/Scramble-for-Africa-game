#Contains functions that manage what happens at the end of each turn, like worker upkeep and price changes

import random

from . import text_tools
from . import actor_utility
from . import market_tools
from . import notification_tools
from . import utility
from . import game_transitions

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
    for current_pmob in global_manager.get('pmob_list'):
        current_pmob.end_turn_move()
    for current_cell in global_manager.get('strategic_map_grid').cell_list:
        current_tile = current_cell.tile
        while current_tile.get_inventory_used() > current_tile.inventory_capacity:
            discarded_commodity = random.choice(current_tile.get_held_commodities())
            current_tile.change_inventory(discarded_commodity, -1)
            
    start_enemy_turn(global_manager)

def start_enemy_turn(global_manager):
    '''
    Description:
        Starts the ai's turn, resetting their units to maximum movement points, spawning warriors, etc.
    Input:
        global_manager_template global_manager: Object that accesses shared variables
        first_turn = False: Whether this is the first turn - do not pay upkeep, etc. when the game first starts
    Output:
        None
    '''
    manage_villages(global_manager)
    reset_mobs('npmobs', global_manager)
    manage_enemy_movement(global_manager)
    manage_combat(global_manager) #should probably do reset_mobs, manage_production, etc. after combat completed in a separate function
    #the manage_combat function starts the player turn
    
def start_player_turn(global_manager, first_turn = False):
    '''
    Description:
        Starts the player's turn, resetting their units to maximum movement points, adjusting prices, paying upkeep, etc.
    Input:
        global_manager_template global_manager: Object that accesses shared variables
        first_turn = False: Whether this is the first turn - do not pay upkeep, etc. when the game first starts
    Output:
        None
    '''
    text_tools.print_to_screen("", global_manager)
    text_tools.print_to_screen("Turn " + str(global_manager.get('turn') + 1), global_manager)
    if not first_turn:
        reset_mobs('pmobs', global_manager)
        
        manage_production(global_manager)
        manage_subsidies(global_manager) #subsidies given before public opinion changes
        manage_public_opinion(global_manager)
        manage_upkeep(global_manager)
        manage_loans(global_manager)
        manage_financial_report(global_manager)
        manage_worker_price_changes(global_manager)
        manage_worker_migration(global_manager)

    global_manager.set('player_turn', True)
    global_manager.get('turn_tracker').change(1)
        
    if not first_turn:
        market_tools.adjust_prices(global_manager)#adjust_prices(global_manager)
            
    end_turn_selected_mob = global_manager.get('end_turn_selected_mob')
    if (not end_turn_selected_mob == 'none') and end_turn_selected_mob in global_manager.get('mob_list'): #do not attempt to select if none selected or has been removed since end of turn
        end_turn_selected_mob.select()
        actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('tile_info_display_list'), end_turn_selected_mob.images[0].current_cell.tile)
    else: #if no mob selected at end of turn, calibrate to minimap tile to show any changes
        if not global_manager.get('displayed_tile') == 'none':
            actor_utility.calibrate_actor_info_display(global_manager, global_manager.get('tile_info_display_list'), global_manager.get('displayed_tile'))

def reset_mobs(mob_type, global_manager):
    '''
    Description:
        Starts the turn for mobs of the inputed type, resetting their movement points and removing the disorganized status
    Input:
        string mob_type: Can be pmob or npmob, determines which mobs' turn starts
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    if mob_type == 'pmobs':
        for current_pmob in global_manager.get('pmob_list'):
            current_pmob.reset_movement_points()
            current_pmob.set_disorganized(False) 
    elif mob_type == 'npmobs':
        for current_npmob in global_manager.get('npmob_list'):
            current_npmob.reset_movement_points()
            current_npmob.set_disorganized(False) 
    else:
        for current_mob in global_manager.get('mob_list'):
            current_mob.reset_movement_points()
            current_mob.set_disorganized(False)

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

def manage_loans(global_manager):
    '''
    Description:
        Pays interest on all current loans at the end of a turn
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    for current_loan in global_manager.get('loan_list'):
        current_loan.make_payment()

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
        
def manage_worker_migration(global_manager): 
    '''
    Description:
        Checks if a workerm migration event occurs and resolves it if it does occur
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    num_village_workers = actor_utility.get_num_available_workers('village', global_manager) + global_manager.get('num_wandering_workers')
    num_slums_workers = actor_utility.get_num_available_workers('slums', global_manager)
    if num_village_workers > num_slums_workers and random.randrange(1, 7) >= 5: #1/3 chance of activating
        resolve_worker_migration(global_manager)

def resolve_worker_migration(global_manager): #resolves migration if it occurs
    '''
    Description:
        When a migration event occurs, about half of available workers in villages and all wandering workers move to a slum around a colonial port, train station, or resource production facility. The chance to move to a slum on a tile
            is weighted by the number of people already in that tile's slum and the number of employment buildings on that tile. Also displays a report of the movements that occurred
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    possible_source_village_list = actor_utility.get_migration_sources(global_manager) #list of villages that could have migration
    destination_cell_list = actor_utility.get_migration_destinations(global_manager)
    if not len(destination_cell_list) == 0:
        weighted_destination_cell_list = create_weighted_migration_destinations(destination_cell_list)
        village_destination_dict = {}
        village_destination_coordinates_dict = {}
        village_num_migrated_dict = {}
        source_village_list = [] #list of villages that actually had migration occur
        any_migrated = False
        #resolve village worker migration
        for source_village in possible_source_village_list:
            num_migrated = 0
            for available_worker in range(source_village.available_workers):
                if random.randrange(1, 7) >= 4:
                    num_migrated += 1
                    
            if num_migrated > 0:
                any_migrated = True
                
                source_village_list.append(source_village)
                destination = random.choice(weighted_destination_cell_list) #random.choice(destination_cell_list)
                if not destination.has_slums():
                    destination.create_slums()
                source_village.change_available_workers(-1 * num_migrated)
                source_village.change_population(-1 * num_migrated)
                destination.contained_buildings['slums'].change_population(num_migrated)
                if not destination.contained_buildings['port'] == 'none':
                    destination_type = 'port'
                elif not destination.contained_buildings['resource'] == 'none':
                    destination_type = destination.contained_buildings['resource'].name
                elif not destination.contained_buildings['train_station'] ==  'none':
                    destination_type = 'train station'
                village_destination_dict[source_village] = destination_type
                village_destination_coordinates_dict[source_village] = (destination.x, destination.y)
                village_num_migrated_dict[source_village] = num_migrated

        
        #resolve wandering worker migration
        wandering_destinations = []
        wandering_destination_dict = {}
        wandering_destination_coordinates_dict = {}
        wandering_num_migrated_dict = {}
        num_migrated = global_manager.get('num_wandering_workers')
        if num_migrated > 0:
            any_migrated = True
            for i in range(num_migrated):
                destination = random.choice(weighted_destination_cell_list) #random.choice(destination_cell_list)
                if not destination.has_slums():
                    destination.create_slums()
                destination.contained_buildings['slums'].change_population(1) #num_migrated
                global_manager.set('num_wandering_workers', global_manager.get('num_wandering_workers') - 1)
                if not destination.contained_buildings['port'] == 'none':
                    destination_type = 'port'
                elif not destination.contained_buildings['resource'] == 'none':
                    destination_type = destination.contained_buildings['resource'].name
                elif not destination.contained_buildings['train_station'] ==  'none':
                    destination_type = 'train station'
                wandering_destination_dict[destination] = destination_type #destination 0: port
                wandering_destination_coordinates_dict[destination] = (destination.x, destination.y) #destination 0: (2, 2)
                if destination in wandering_destinations:
                    wandering_num_migrated_dict[destination] += 1
                else:
                    wandering_num_migrated_dict[destination] = 1
                    wandering_destinations.append(destination)
                
        if any_migrated:        
            migration_report_text = 'A wave of migration from villages to your colony has occured as African workers search for employment. /n'
            for source_village in source_village_list: #1 worker migrated from villageName village to the slums surrounding your iron mine at (0, 0). /n
                current_line = str(village_num_migrated_dict[source_village]) + ' worker' + utility.generate_plural(village_num_migrated_dict[source_village]) + ' migrated from ' + source_village.name
                current_line += " village to the slums surrounding your " + village_destination_dict[source_village]
                current_line += " at (" + str(village_destination_coordinates_dict[source_village][0]) + ', ' + str(village_destination_coordinates_dict[source_village][1]) + ').'
                migration_report_text += current_line + ' /n'
            for wandering_destination in wandering_destinations:
                current_line = str(wandering_num_migrated_dict[wandering_destination]) + ' wandering worker' + utility.generate_plural(wandering_num_migrated_dict[wandering_destination]) + ' settled in the slums surrounding your '
                current_line += wandering_destination_dict[wandering_destination] + " at (" + str(wandering_destination_coordinates_dict[wandering_destination][0]) + ', ' + str(wandering_destination_coordinates_dict[wandering_destination][1]) + ').'
                migration_report_text += current_line + ' /n'
            notification_tools.display_notification(migration_report_text, 'default', global_manager)
    
def create_weighted_migration_destinations(destination_cell_list):
    '''
    Description:
        Analyzes a list of destinations for a migration event and creates a weighted list from which cells with more employment buildings and lower slum populations are more likely to be chosen
    Input:
        cell list destination_cell_list: list of cells that have employment buildings to migrate to
    Output:
        cell list: Returns a weighted list of cells in which cells with more employment buildings and lower slum populations appear a greater number of times
    '''
    weighted_cell_list = []
    for current_cell in destination_cell_list:
        num_poi = 0 #points of interest
        if not current_cell.contained_buildings['port'] == 'none':
            num_poi += 1
        if not current_cell.contained_buildings['train_station'] == 'none':
            num_poi += 1
        if not current_cell.contained_buildings['resource'] == 'none':
            num_poi += 1
        max_population_weight = 5
        if current_cell.contained_buildings['slums'] == 'none': #0
            population_weight = max_population_weight
        elif current_cell.contained_buildings['slums'].available_workers < max_population_weight: #1-4
            population_weight = max_population_weight - current_cell.contained_buildings['slums'].available_workers
        else: #5+
            population_weight = 1
        total_weight = population_weight * num_poi
        for i in range(total_weight):
            weighted_cell_list.append(current_cell)
    return(weighted_cell_list)


def manage_villages(global_manager):
    '''
    Description:
        Controls the aggressiveness and population changes of villages and native warrior spawning/despawning
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
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

        current_village.manage_warriors()

def manage_enemy_movement(global_manager):
    '''
    Description:
        Moves npmobs at the end of the turn towards player-controlled mobs/buildings
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    for current_npmob in global_manager.get('npmob_list'):
        if not current_npmob.creation_turn == global_manager.get('turn'): #if not created this turn
            current_npmob.end_turn_move()

def manage_combat(global_manager):
    '''
    Description:
        Resolves, in order, each possible combat that was triggered by npmobs moving into cells with pmobs. When a possible combat is resolved, it should call the next possible combat until all are resolved
    Input:
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    if len(global_manager.get('attacker_queue')) > 0:
        global_manager.get('attacker_queue').pop(0).attempt_local_combat()
    else:
        start_player_turn(global_manager)
