#Runs setup and main loop on program start

import modules.main_loop as main_loop
from modules.setup import *

try:
    setup(debug_tools, misc, terrains, commodities, def_ministers, def_countries, transactions, actions, lore, value_trackers, buttons, europe_screen,
            ministers_screen, trial_screen, new_game_setup_screen, mob_interface, tile_interface, unit_organization_interface, inventory_interface, minister_interface,
            country_interface
    )
    main_loop.main_loop()

except Exception: #displays error message and records error message in crash log file
    manage_crash(Exception)

# tasks:
# look into adding text on map, such as village names - should be a generalizable procedure that works similarly to tile images or cell icons, with some way to easily
#   create a rendered text object with a string message and offset parameters
# look into a procedure that prompts for text input and prevents any other actions to get things like port names, with some level of input validation
# make generic contested action type
# add horizontal ordered collection for double combat dice?
# look into default tab modes, maybe with units with commodiy capacity going to inventory mode
# add Asian workers, maybe with starting upkeep bonus for Britain and (less so) France - 4.0 upkeep, from abstract grid, no penalty for firing, European attrition,
#   no slums, otherwise like African
# make sure version of game on GitHub works when cloned - missing things like Belgian music folder, save game folder
