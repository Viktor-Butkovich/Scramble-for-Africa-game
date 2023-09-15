#Runs setup and main loop on program start

import modules.main_loop as main_loop
import modules.tools.data_managers as data_managers
from modules.setup import *

try:
    global_manager = data_managers.global_manager_template() #manages a dictionary of what would be global variables passed between functions and classes
    setup(global_manager, debug_tools, fundamental, misc, terrains, commodities, def_ministers, def_countries, transactions, lore, value_trackers, buttons, europe_screen,
            ministers_screen, trial_screen, new_game_setup_screen, mob_interface, tile_interface, unit_organization_interface, inventory_interface, minister_interface,
            country_interface
    )
    main_loop.main_loop(global_manager)

except Exception: #displays error message and records error message in crash log file   
    manage_crash(Exception)

# find some solution to reorganization interface overlap, especially with construction gang
# fix overlapping voicelines for 0 evidence trials - court in session and not guilty playing simultaneously
# exploration direction icons not showing correctly, probably for not being an interface element - same issue probably for attack icons
# ^ exploration marks are currently implemented as tiles that exist in cells but are only accessed through the owning expedition - this means that they are not interface elements
# it is useful to implement it as a tile so that it appears on both grids at once, but the current implementation as a hardcoded global exploration_mark_list is definitely
# not ideal - maybe make a special grid free image that can exist in all versions of a tile? Should not have to edit the tile's get_image_id_list, as the exploration mark
# list isn't a characteristic of the tile
# continue work on cell_icons
#change resource frequencies to be an external .json file rather than hardcoded in grid
#modify can_show recursion to not go through each element if the controlling collection's can_show is false and stayed false
#workers uncrewing steamship and going onto shore incorrectly only spending 1 movement point, probably checking origin cell and seeing there are no crewed ships