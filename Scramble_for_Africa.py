# Runs setup and main loop on program start

import modules.main_loop as main_loop
from modules.setup import *

try:
    setup(
        misc,
        worker_types_config,
        equipment_types_config,
        terrain_feature_types_config,
        terrains,
        commodities,
        def_ministers,
        def_countries,
        new_game_setup_screen,
        info_displays,
        transactions,
        actions,
        lore,
        value_trackers,
        buttons,
        europe_screen,
        ministers_screen,
        trial_screen,
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
# Add autosave and multiple save slots
# Performance impacts from repeated exit/load - not everything is being removed each time
# Add ambient sounds
#
# Possible issues:
# Look into special character glitch for Queiros Portuguese name, possibly font issue not having correct special character in the settlement font (but does in minister screen font)
#
#   new SFA features:
# Add notification whenever worker prices change - at start of turn or after action/hire
#   Hiring an X worker has changed X worker upkeep from A to B.
#   You now pay C per turn for your D X workers.
#       Customize start of message based on what caused the price change
# Add equip all button from top perspective - equip all from tile or from mob
# Give notification when ship fails to assign an end of turn destination
# Prompt to name a settlement when it first appears, using a default as the randomly generated name - also extend to SE
# Add label icon to slave traders and Europe abstract tiles - allows easily knowing what it is without clicking
# Number of workers not being maintained correctly
# Discover river source after entering, not on discovery - requires hiding terrain feature, etc.
# Attacking ferry incorrectly causing disorganized (if from connected tile)
# Add steamship destination tooltip to Asia grid
#   Any tile should have a tooltip when it is a destination for any unit, and for any units it is a destination for
# Add notification for failed attempt to click on end turn destination
# Buy consumer goods tooltip should explain how they are used to trade with villages
# Add achievement for building railroad bridge
# Add warehouses to trading posts
# Add achievement for selling your first commodity
# Add notification for when worker upkeep changes (start of turn and after action), with tutorial advice for African workers
