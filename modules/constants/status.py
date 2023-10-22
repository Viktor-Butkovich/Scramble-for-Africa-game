import pygame
from typing import Dict, List, Any
from modules.interface_types.grids import grid
from modules.actor_types.tiles import tile
from modules.actor_types.mobs import mob
from modules.constructs.ministers import minister
from modules.constructs.countries import country
from modules.interface_types.notifications import notification
from modules.interface_types.buttons import button
from modules.interface_types.instructions import instructions_page
from modules.interface_types.dice import die
from modules.constructs.images import free_image
from modules.actor_types.actors import actor
from modules.actor_types.buildings import building, slums, resource_building
from modules.actor_types.mobs import mob
from modules.actor_types.mob_types.pmobs import pmob
from modules.actor_types.mob_types.npmobs import npmob
from modules.actor_types.mob_types.npmob_types.beasts import beast
from modules.constructs.villages import village
from modules.util.market_utility import loan

strategic_map_grid:grid = None
minimap_grid:grid = None
europe_grid:grid = None
slave_traders_grid:grid = None

displayed_mob: mob = None
displayed_tile: tile = None
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

current_instructions_page: instructions_page = None
ongoing_action_type: str = None
