#Runs setup and main loop on program start

import modules.main_loop as main_loop
import modules.data_managers as data_managers
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

#find some solution to reorganization interface overlap, especially with construction gang
#fix overlapping voicelines for 0 evidence trials - court in session and not guilty playing simultaneously
#exploration direction icons not showing correctly, probably for not being an interface element - same issue probably for attack icons
