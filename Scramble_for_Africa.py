#Runs setup and main loop on program start

import modules.main_loop as main_loop
from modules.setup import *

try:
    setup(debug_tools, misc, worker_types_config, terrains, commodities, def_ministers, def_countries, transactions, actions, lore, value_trackers, buttons, europe_screen,
            ministers_screen, trial_screen, new_game_setup_screen, mob_interface, tile_interface, unit_organization_interface, inventory_interface, minister_interface,
            country_interface
    )
    main_loop.main_loop()

except Exception: #displays error message and records error message in crash log file
    manage_crash(Exception)

# tasks:
#   general:
# make sure version of game on GitHub works when cloned - missing things like Belgian music folder, save game folder
# replace usages of 'none' with None
# Add type hints on sight - gradual process
#
#   new features:
# make generic contested action type
# add minister speech bubbles
# look into default tab modes, maybe with units with commodiy capacity going to inventory mode
# add Asian workers, maybe with starting upkeep bonus for Britain and (less so) France - 4.0 upkeep, from abstract grid, no penalty for firing, European attrition,
#   no slums, otherwise like African
#       Have grids in configuration
#           flag  Asia               Africa
#           Europe Slave Traders     Africa
# look into a procedure that prompts for text input and prevents any other actions to get things like port names, with some level of input validation
#      would need to modify text box to capture the output for a particular purpose, with a standard listen/receive function
#       when an object uses listen, it starts the typing process and captures the output when typing is cancelled or entered
#       the text box should call the receive function of the current listener
# add settlement name label with indented building labels
#Allow ship moving through series of ports adjacent to the river
#   would allow moving past it. Units with canoes can move through with 4 movement points (maybe same as without canoes) - implement as generic terrain
#   feature that could be ported over approximately 0.1 chance per river tile, 1-2 desired per river
# Add cataracts
# Add confirmation for free all slaves button
# Add boarding pending state - unit can enter pending state if attempting to board with 0 or 2+ crewed vehicles present, then a vehicle can pick up any
#   pending units - pending is a state like sentry mode
# Change slums to be based around settlements rather than buildings, and use settlement name in migration description
# Maybe have special corruption event involving Minister of Geography attempting to steal an artifact
# Add ambient resource production facility, settlement, and village sounds
# Allow some inventory attrition to occur in Europe
# Add direct attack on native villages action
# Allow water exploration for steamboat/train with expedition on board
# Add cannibals
# Add notification when village goes from 0 to 1 population
# Add train/ship sounds
# Change visual size of porter boxes
# Replace resource production facility images
# Add equipment
#   Battalions should be 1 weaker, and rifles should give a +1 to combat strength - soldiers without rifles should have uniforms but no rifles in the image
# Add random events
# Add debug settings menu within game, rather than needing to edit .json out of game
# Add cosmetic flag to minister screen
# Fix scaling issue with inventory interface - going over edge of safe click panel
# Add transfer all button to inventory that ignores which commodities are involved, as well as a sell all button in Europe
# Change game to be fullscreen by default, along with debug setting to make it windowed
# Put __init__ file in each subfolder to organize module imports
# Add autosave and multiple save slots
# Add victory conditions - 10,000 money, all lore missions completed, all map squares explored, improve production tile to 6/6, African worker price to 0.5
# When steamship/steamboat moves to non-port land from water, disembark and move all passengers - any passengers w/o enough movement should stay on vehicle, and can't move
#   into npmobs
# Should only select 1st unit at start of turn after getting through initial notifications - currently causing tile/building zoom notifications to be overridden by the
#    start of turn cycle
#
#   bugfixes
# continue looking for steamship crew disembarking error, possibly from enemies spawning on square (like failed missionaries) - occurs after combat
# Find some solution to overlapping 3rd work crew and text box
# incorrect behavior when attacked while in vehicle/resource building - includes graphical error with unit not showing afterward
# Sell commodities button should go to minister screen if not all ministers appointed

# Notes: Possibly allow choosing minister but not confirming yet
#   Don't allow any actions while any notifications are visible, even purely informational ones
#   Make sure movement buttons move the selected unit
#   Possibly add way to repeatedly do action every turn, especially for advertising/public opinion
