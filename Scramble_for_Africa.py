#Runs setup and main loop on program start

import modules.main_loop as main_loop
from modules.setup import *

try:
    setup(debug_tools, misc, worker_types_config, equipment_types_config, terrains, commodities, def_ministers, def_countries, transactions, actions, lore,
          value_trackers, buttons, europe_screen, ministers_screen, trial_screen, new_game_setup_screen, mob_interface, tile_interface, unit_organization_interface,
          settlement_interface, inventory_interface, minister_interface, country_interface
    )
    main_loop.main_loop()

except Exception: #displays error message and records error message in crash log file
    manage_crash(Exception)

# tasks:
#   general (game-agnostic):
# replace usages of 'none' with None
# Add type hints on sight - gradual process
# add minister speech bubbles
# Add random events
# Add debug settings menu within game, rather than needing to edit .json out of game
# Change game to be fullscreen by default, along with debug setting to make it windowed
# Add autosave and multiple save slots
# Performance impacts from repeated exit/load - not everything is being removed each time
#
#   new SFA features:
# look into default tab modes, maybe with units with commodiy capacity going to inventory mode
# Add cataracts
#   Steamboats treat cataracts like land
#   Other units treat cataracts as river water where canoes do not function
#   Approximately 0.1 chance per river tile, 1-2 desired per river
# Add ambient resource production facility, settlement, and village sounds
# Allow some inventory attrition to occur in Europe
# Add direct attack on native villages action
# Add cannibals
# Replace resource production facility images
# Add equipment (canoes)
# Add cosmetic flag to minister screen
# Add victory conditions - 10,000 money, all lore missions completed, all map squares explored, improve production tile to 6/6, African worker price to 0.5
#   Add achievement to main menu
#   Possibly include stealing from company directly
# Give 1/36 chance for off-tile exploration to grant veteran status (1/6 chance of doing minister roll, promote on 6)
# Add lore mission trophy screen
# Add river sources, with bonuses for discovery
