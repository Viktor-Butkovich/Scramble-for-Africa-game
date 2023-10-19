from modules.tools.data_managers.global_manager_template import global_manager_template
from modules.tools.data_managers.sound_manager_template import sound_manager_template
from modules.tools.data_managers.save_load_manager_template import save_load_manager_template
from modules.tools.data_managers.flavor_text_manager_template import flavor_text_manager_template

global_manager:global_manager_template = global_manager_template()
sound_manager:sound_manager_template = sound_manager_template(global_manager)
save_load_manager:save_load_manager_template = save_load_manager_template(global_manager)
flavor_text_manager:flavor_text_manager_template = flavor_text_manager_template(global_manager)

building_prices = {
    'resource': 10,
    'road': 5,
    'railroad': 15,
    'road_bridge': 50,
    'railroad_bridge': 150,
    'port': 15,
    'train_station': 10,
    'trading_post': 5,
    'mission': 5,
    'fort': 5,
    'warehouses': 5,
    'train': 10,
    'steamboat': 10
} 

base_action_prices = {
    'trade': 0,
    'slave_capture': 5,
    'trial': 5,
    'active_investigation': 5,
    'rumor_search': 5,
    'artifact_search': 5,
    'track_beasts': 0
}
action_types = [current_key for current_key in base_action_prices]
action_prices = {}

transaction_descriptions = {
    'trade': 'trading with natives',
    'loan': 'loans',
    'slave_capture': 'capturing slaves',
    'trial': 'trial fees',
    'active_investigation': 'investigations',
    'rumor_search': 'artifact rumor searches',
    'artifact_search': 'artifact searches',
    'production': 'production',
    'bribery': 'bribery',
    'loan_interest': 'loan interest',
    'inventory_attrition': 'missing commodities',
    'sold_commodities': 'commodity sales',
    'worker_upkeep': 'worker upkeep',
    'subsidies': 'subsidies',
    'trial_compensation': 'trial compensation',
    'fabricated_evidence': 'fabricated evidence',
    'consumer_goods': 'consumer goods',
    'unit_recruitment': 'unit recruitment',
    'attrition_replacements': 'attrition replacements',
    'misc_revenue': 'misc',
    'misc_expenses': 'misc',
    'none': 'miscellaneous company activities'
}
transaction_types = [current_key for current_key in transaction_descriptions]
