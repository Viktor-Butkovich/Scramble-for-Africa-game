import pygame
from modules.tools.data_managers.global_manager_template import global_manager_template
from modules.tools.data_managers.sound_manager_template import sound_manager_template
from modules.tools.data_managers.save_load_manager_template import save_load_manager_template
from modules.tools.data_managers.flavor_text_manager_template import flavor_text_manager_template
from modules.tools.data_managers.input_manager_template import input_manager_template
from modules.tools.data_managers.actor_creation_manager_template import actor_creation_manager_template
from modules.tools.data_managers.event_manager_template import event_manager_template
from modules.tools.data_managers.effect_manager_template import effect_manager_template
from modules.tools.data_managers.value_tracker_template import value_tracker_template, public_opinion_tracker_template, money_tracker_template
from modules.interface_types.labels import money_label_template

from typing import Dict, List

pygame.init()
pygame.mixer.init()
pygame.display.set_icon(pygame.image.load('graphics/misc/SFA.png'))

global_manager:global_manager_template = global_manager_template()
sound_manager:sound_manager_template = sound_manager_template(global_manager)
save_load_manager:save_load_manager_template = save_load_manager_template(global_manager)
flavor_text_manager:flavor_text_manager_template = flavor_text_manager_template(global_manager)
input_manager:input_manager_template = input_manager_template(global_manager)
actor_creation_manager:actor_creation_manager_template = actor_creation_manager_template()
event_manager:event_manager_template = event_manager_template(global_manager)
effect_manager:effect_manager_template = effect_manager_template(global_manager)

turn: int = 0
turn_tracker: value_tracker_template = None
public_opinion: int = 0
public_opinion_tracker: public_opinion_tracker_template = None
money: float = 0
money_tracker: money_tracker_template = None
money_label: money_label_template = None
evil: int = 0
evil_tracker: value_tracker_template = None
fear: int = 0
fear_tracker: value_tracker_template = None
fps: int = 0
fps_tracker: value_tracker_template = None
frames_this_second: int = 0
last_fps_update: float = 0.0

loading: bool = True
loading_start_time: float = 0.0
previous_turn_time: float = 0.0
current_time: float = 0.0
last_selection_outline_switch: float = 0.0
show_selection_outlines: bool = False
show_minimap_outlines: bool = False
mouse_moved_time: float = 0.0
end_turn_wait_time: float = 0.8

default_display_width: int = 1728 #all parts of game made to be at default_display and scaled to display
default_display_height: int = 972
resolution_finder = pygame.display.Info()
display_width: float = resolution_finder.current_w - round(default_display_width/10)
display_height: float = resolution_finder.current_h - round(default_display_height/10)

startup_complete: bool = False
creating_new_game: bool = False

building_prices: Dict[str, int] = {
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

base_action_prices: Dict[str, int] = {
    'trade': 0,
    'slave_capture': 5,
    'trial': 5,
    'active_investigation': 5,
    'rumor_search': 5,
    'artifact_search': 5,
    'track_beasts': 0
}
action_types: List[str] = [current_key for current_key in base_action_prices]
action_prices: Dict[str, float] = {}

transaction_descriptions: Dict[str, str] = {
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
transaction_types: List[str] = [current_key for current_key in transaction_descriptions]

color_dict: Dict[str, tuple[int, int, int]] = {
    'black': (0, 0, 0),
    'white': (255, 255, 255),
    'light gray': (230, 230, 230),
    'gray': (190, 190, 190),
    'dark gray': (150, 150, 150),
    'bright red': (255, 0, 0),
    'red': (200, 0, 0),
    'dark red': (150, 0, 0),
    'bright green': (0, 255, 0),
    'green': (0, 200, 0),
    'dark green': (0, 150, 0),
    'green': (0, 200, 0),
    'dark green': (0, 150, 0),
    'bright blue': (0, 0, 255),
    'blue': (0, 0, 200),
    'dark blue': (0, 0, 150),
    'yellow': (255, 255, 0),
    'brown': (85, 53, 22),
    'blonde': (188, 175, 123),
    'purple': (127, 0, 170),
    'transparent': (1, 1, 1)
}
