from modules.interface_types.grids import grid
from modules.actor_types.tiles import tile
from modules.actor_types.mobs import mob
from modules.constructs.ministers import minister
from modules.constructs.countries import country
from modules.interface_types.notifications import notification


europe_grid:grid = None
#create strategic map and slave traders grids

displayed_mob: mob = None
displayed_tile: tile = None
displayed_minister: minister = None
displayed_defense: minister = None
displayed_prosecution: minister = None
displayed_country: country = None
displayed_notification: notification = None
