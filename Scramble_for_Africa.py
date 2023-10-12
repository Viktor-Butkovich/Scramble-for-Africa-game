#Runs setup and main loop on program start

import modules.main_loop as main_loop
import modules.tools.data_managers.global_manager_template as global_manager_template
from modules.setup import *

try:
    global_manager = global_manager_template.global_manager_template() #manages a dictionary of what would be global variables passed between functions and classes
    setup(global_manager, debug_tools, fundamental, misc, terrains, commodities, def_ministers, def_countries, transactions, actions, lore, value_trackers, buttons, europe_screen,
            ministers_screen, trial_screen, new_game_setup_screen, mob_interface, tile_interface, unit_organization_interface, inventory_interface, minister_interface,
            country_interface
    )
    main_loop.main_loop(global_manager)

except Exception: #displays error message and records error message in crash log file
    manage_crash(Exception)

# tasks:
# look into adding text on map, such as village names - should be a generalizable procedure that works similarly to tile images or cell icons, with some way to easily
#   create a rendered text object with a string message and offset parameters
# look into a procedure that prompts for text input and prevents any other actions to get things like port names, with some level of input validation
# fix notification scaling issues - possibly an issue with font size scaling in notification_manager.notification_to_front
# verify that country bonuses are still applying to actions like advertising - they should, as the bonuses are applied when a minister makes a roll
# later test conversion with 0 population villages, combat, and villages with missions - relies on other actions working
# make generic contested action type
# change all notification interface to automatically be centered
# test hunting/beast defense combat
# verify that forts work as intended
# add horizontal ordered collection for double combat dice
# switching to Europe screen should select top unit in Europe, rather than just deselecting all
# modify notification or inventory spacing to not show tile inventory commodity icon just past left edge of notification
# financial report notification should say click to remove, possibly also production report
# look into default tab modes, maybe with units with commodiy capacity going to inventory mode
# maybe automatically navigate to minister screen if attempting to do action that requires minister, but allow leaving minister screen w/o appointing
# error with movement from river - railroad bridge to road in desert cost 4, it should cost 1 - also verify that movement from river has normal cost for terrain 
#   entered - calculated correctly as 1.0 by movement tooltip but actually sets to 0 - probably thinks it is landing f
# errors with multiple combats occurring simulateously - make sure notification manager can only display 1 at a time
# add Asian workers, maybe with starting upkeep bonus for Britain and (less so) France - 4.0 upkeep, from abstract grid, no penalty for firing, European attrition,
#   no slums, otherwise like African
# verify bridge issue has been fixed once construction is functional
# make sure version of game on GitHub works when cloned - missing things like Belgian music folder, save game folder
# multiple combat error is persisting, fix ASAP - probably related to interface trying to transfer between, confirmed not from inserts or lock
# construction: add infrastructure/resource building update info functionality, upgrades, repairs
