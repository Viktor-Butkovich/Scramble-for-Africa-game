from modules.interface_types.grids import grid
from modules.actor_types.tiles import tile
from modules.actor_types.mobs import mob
from modules.constructs.ministers import minister
from modules.constructs.countries import country
from modules.interface_types.notifications import notification


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
