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
# replace usages of 'none' with None
# make generic contested action type
# add minister speech bubbles
# add horizontal ordered collection for double combat dice?
# look into default tab modes, maybe with units with commodiy capacity going to inventory mode
# make sure version of game on GitHub works when cloned - missing things like Belgian music folder, save game folder
# possibly allow sections of images to appear over other images, like village names overlaying any contains mobs
# add Asian workers, maybe with starting upkeep bonus for Britain and (less so) France - 4.0 upkeep, from abstract grid, no penalty for firing, European attrition,
#   no slums, otherwise like African
# look into a procedure that prompts for text input and prevents any other actions to get things like port names, with some level of input validation
#      would need to modify text box to capture the output for a particular purpose, with a standard listen/receive function
#       when an object uses listen, it starts the typing process and captures the output when typing is cancelled or entered
#       the text box should call the receive function of the current listener
# incorrect behavior when attacked while in vehicle/resource building - includes graphical error with unit not showing afterward
# add settlement name label with indented building labels
# continue looking for steamship crew disembarking error, possibly from enemies spawning on square (like failed missionla series of ports adjacent to the river
#   would allow moving past it. Units with canoes can move through with 4 movement points (maybe same as without canoes) - implement as generic terrain
#   feature that could be ported over approximately 0.1 chance per river tile, 1-2 desired per river
# add f. lname labels under cabinet portraits in minister (and trial?) screen
# add confirmation for free all slaves button
