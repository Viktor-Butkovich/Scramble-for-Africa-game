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

# tasks:
# fix reorganization interface overlap, especially with construction gang
# fix overlapping voicelines for 0 evidence trials - court is in session and not guilty playing simultaneously
# it would be better practice to implement resource frequencies as an external .json file rather than being hardcoded in grid
# workers uncrewing steamship are incorrectly only spending the normal movement for the tile entered, rather than using all of their movement - probably checking the origin
#   cell and seeing there are no crewed ships, or possibly related to the new canoe/can_swim changes
# the safe-click panel on the lhs of the screen should have an image to make it clearer where the player can click to deselect/not deselect the current unit
# need an alternative to cell icons that are intrinsically linked to the tile and show up with it on the lhs and for exploration images, rather than acting as an
#   independent interface element - like lore mission locations, similar to a tile but part of the image_id_list instead
#   Maybe tiles can have an attached object list with objects that they will include in their image id lists and can be removed by the object's owner
#   lore mission would create an attached location object for the relevant main grid tile, which would include it in its image id list - when calibrating, mini grid tiles
#   will copy the other tile's attached images
