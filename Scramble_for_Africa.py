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
