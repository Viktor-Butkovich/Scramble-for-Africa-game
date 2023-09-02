import pygame

import modules.main_loop as main_loop
import modules.data_managers as data_managers
import modules.setup as setup

try:
    global_manager = data_managers.global_manager_template() #manages a dictionary of what would be global variables passed between functions and classes
    setup.debug_tools_setup(global_manager)
    setup.fundamental_setup(global_manager)
    setup.misc_setup(global_manager)
    setup.terrains_setup(global_manager)
    setup.commodities_setup(global_manager)
    setup.ministers_setup(global_manager)
    setup.countries_setup(global_manager)
    setup.transactions_setup(global_manager)
    setup.lore_setup(global_manager)

    setup.value_trackers_setup(global_manager)
    setup.buttons_setup(global_manager)

    setup.europe_screen_setup(global_manager)
    setup.ministers_screen_setup(global_manager)
    setup.trial_screen_setup(global_manager)
    setup.new_game_setup_screen_setup(global_manager)

    setup.mob_interface_setup(global_manager)
    setup.tile_interface_setup(global_manager)
    setup.unit_organization_interface_setup(global_manager)
    setup.inventory_interface_setup(global_manager)
    setup.minister_interface_setup(global_manager)
    setup.country_interface_setup(global_manager)

    global_manager.set('startup_complete', True)
    global_manager.set('creating_new_game', False)
    main_loop.main_loop(global_manager)
    pygame.quit()

except Exception: #displays error message and records error message in crash log file
    setup.manage_crash(Exception)
#add label that just shows "working skill" for skill in current job
#now need to add cycle/remove cell buttons - make sure they are greyed out for dummy units
