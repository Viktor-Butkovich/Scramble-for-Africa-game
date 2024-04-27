# Runs setup and main loop on program start

import modules.main_loop as main_loop
from modules.setup import *

try:
    setup(
        debug_tools,
        misc,
        worker_types_config,
        equipment_types_config,
        terrain_feature_types_config,
        terrains,
        commodities,
        def_ministers,
        def_countries,
        transactions,
        actions,
        lore,
        value_trackers,
        buttons,
        europe_screen,
        ministers_screen,
        trial_screen,
        new_game_setup_screen,
        mob_interface,
        tile_interface,
        unit_organization_interface,
        settlement_interface,
        inventory_interface,
        minister_interface,
        country_interface,
    )
    main_loop.main_loop()

except Exception:  # displays error message and records error message in crash log file
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
# Add ambient resource production facility, settlement, and village sounds
# Replace placeholder images
#   Especially for Maxim gun
# Add cosmetic flag to minister screen
# Add victory conditions - 10,000 money, all lore missions completed, all map squares explored, improve production tile to 6/6, African worker price to 0.5
#   Add achievement to main menu
#   Possibly include stealing from company directly
# Add cannibals
# Add lore mission trophy screen/notification
# Add wait until full/wait until anything/wait for nothing toggle for automated routes - either a toggled button or a yes/no choice notification when route is drawn
