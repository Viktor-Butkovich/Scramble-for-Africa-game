import pygame
from typing import Dict, List, Any
from modules.actor_types.tiles import tile
from modules.actor_types.mobs import mob
from modules.constructs.ministers import minister
from modules.constructs.countries import country
from modules.constructs.worker_types import worker_type
from modules.constructs.equipment_types import equipment_type
from modules.constructs.terrain_feature_types import terrain_feature_type
from modules.constructs.images import image, free_image
from modules.interface_types.interface_elements import (
    interface_collection,
    tabbed_collection,
    ordered_collection,
)
from modules.interface_types.inventory_interface import inventory_grid
from modules.interface_types.grids import grid, mini_grid, abstract_grid
from modules.interface_types.panels import safe_click_panel
from modules.interface_types.notifications import notification
from modules.interface_types.buttons import button, same_tile_icon
from modules.interface_types.inventory_interface import item_icon
from modules.interface_types.instructions import instructions_page
from modules.interface_types.dice import die
from modules.interface_types.labels import commodity_prices_label_template
from modules.actor_types.actors import actor
from modules.actor_types.buildings import building, slums, resource_building
from modules.actor_types.mobs import mob
from modules.actor_types.mob_types.pmobs import pmob
from modules.actor_types.mob_types.npmobs import npmob
from modules.actor_types.mob_types.npmob_types.beasts import beast
from modules.constructs.villages import village
from modules.constructs.settlements import settlement
from modules.constructs.lore_missions import lore_mission
from modules.util.market_utility import loan
from modules.action_types.action import action
from modules.tools.effects import effect

strategic_map_grid: grid = None
minimap_grid: mini_grid = None
europe_grid: abstract_grid = None
slave_traders_grid: abstract_grid = None

Britain: country = None
France: country = None
Germany: country = None
Belgium: country = None
Portugal: country = None
Italy: country = None

actions: Dict[str, action] = {}

displayed_mob: mob = None
displayed_mob_inventory: item_icon = None
displayed_tile: tile = None
displayed_tile_inventory: item_icon = None
displayed_minister: minister = None
displayed_defense: minister = None
displayed_prosecution: minister = None
displayed_country: country = None
displayed_notification: notification = None

rendered_images: Dict[str, pygame.Surface] = {}
button_list: List[button] = []
recruitment_button_list: List[button] = []
instructions_list: List[str] = []
minister_list: List[minister] = []
available_minister_list: List[minister] = []
country_list: List[country] = []
worker_types: Dict[str, worker_type] = {}
equipment_types: Dict[str, equipment_type] = {}
terrain_feature_types: Dict[str, terrain_feature_type] = {}
flag_icon_list: List[button] = []
grid_list: List[grid] = []
text_list: List[str] = []
free_image_list: List[free_image] = []
minister_image_list: List[Any] = []
available_minister_portrait_list: List[button] = []

actor_list: List[actor] = []
mob_list: List[mob] = []
pmob_list: List[pmob] = []
npmob_list: List[npmob] = []
beast_list: List[beast] = []
village_list: List[village] = []
settlement_list: List[settlement] = []
building_list: List[building] = []
slums_list: List[slums] = []
resource_building_list: List[resource_building] = []
loan_list: List[loan] = []
attacker_queue: List[npmob] = []
enemy_turn_queue: List[npmob] = []
player_turn_queue: List[pmob] = []
independent_interface_elements: List[Any] = []
dice_list: List[die] = []
draw_list: List[Any] = []
lore_mission_list: List[lore_mission] = []
same_tile_icon_list: List[same_tile_icon] = []

loading_image: image = None
safe_click_area: safe_click_panel = None
info_displays_collection: interface_collection = None
grids_collection: interface_collection = None
mob_info_display: ordered_collection = None
mob_inventory_info_display: ordered_collection = None
mob_inventory_grid: inventory_grid = None
tile_info_display: ordered_collection = None
tile_inventory_info_display: ordered_collection = None
tile_inventory_grid: inventory_grid = None
minister_info_display: ordered_collection = None
country_info_display: ordered_collection = None
prosecution_info_display: ordered_collection = None
defense_info_display: ordered_collection = None
mob_tabbed_collection: tabbed_collection = None
tile_tabbed_collection: tabbed_collection = None
mob_inventory_collection: ordered_collection = None
mob_reorganization_collection: ordered_collection = None
tile_inventory_collection: ordered_collection = None
commodity_prices_label: commodity_prices_label_template = None
reorganize_unit_left_button: button = None
reorganize_unit_right_button: button = None
free_unit_slaves_button: button = None
cursor_image: pygame.image = None
next_boarded_vehicle: pmob = None
text_box_destination: callable = None

current_instructions_page: instructions_page = None
current_country: country = None
current_country_name: str = None
current_lore_mission: lore_mission = None
current_ministers: Dict[str, minister] = {}
lore_types_effects_dict: Dict[str, effect] = {}
previous_production_report: str = None
previous_sales_report: str = None
previous_financial_report: str = None
transaction_history: Dict[str, float] = {}

minister_appointment_tutorial_completed: bool = False
exit_minister_screen_tutorial_completed: bool = False
