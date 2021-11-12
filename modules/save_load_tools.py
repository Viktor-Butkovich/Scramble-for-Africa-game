import random
import pickle

from . import scaling
from . import notification_tools
from . import game_transitions
from . import grids
from . import data_managers
from . import turn_management_tools
from . import text_tools
from . import market_tools

class save_load_manager():
    def __init__(self, global_manager):
        self.global_manager = global_manager
        self.set_copied_elements()

    def set_copied_elements(self):
        self.copied_elements = []
        #self.copied_elements.append('strategic_map_grid')
        #self.copied_elements.append('minimap_grid')
        #self.copied_elements.append('europe_grid')
        self.copied_elements.append('money')
        self.copied_elements.append('turn')
        self.copied_elements.append('commodity_prices')
        #self.copied_elements.append('grid_list')
        #self.copied_elements.append('abstract_grid_list')
        #self.copied_elements.append('actor_list')
        #self.copied_elements.append('mob_list')
        #self.copied_elements.append('village_list')
        #self.copied_elements.append('building_list')
        #self.copied_elements.append('resource_building_list')
        #self.copied_elements.append('infrastructure_connection_list')
        #self.copied_elements.append('worker_list')
        #self.copied_elements.append('group_list')
        #self.copied_elements.append('tile_list')
        self.copied_elements.append('num_workers')
        self.copied_elements.append('worker_upkeep')
        
    def new_game(self):
        strategic_grid_height = 300#450
        strategic_grid_width = 320#480
        mini_grid_height = 600#450
        mini_grid_width = 640#480

        strategic_map_grid = grids.grid(scaling.scale_coordinates(self.global_manager.get('default_display_width') - (strategic_grid_width + 100), self.global_manager.get('default_display_height') - (strategic_grid_height + 25),
            self.global_manager), scaling.scale_width(strategic_grid_width, self.global_manager), scaling.scale_height(strategic_grid_height, self.global_manager), 16, 15, 'black', 'black', ['strategic'], True, 2, self.global_manager)
        self.global_manager.set('strategic_map_grid', strategic_map_grid)

        minimap_grid = grids.mini_grid(scaling.scale_coordinates(self.global_manager.get('default_display_width') - (mini_grid_width + 100),
            self.global_manager.get('default_display_height') - (strategic_grid_height + mini_grid_height + 50), self.global_manager), scaling.scale_width(mini_grid_width, self.global_manager), scaling.scale_height(mini_grid_height,
            self.global_manager), 5, 5, 'black', 'bright red',['strategic'], self.global_manager.get('strategic_map_grid'), 3, self.global_manager)
        self.global_manager.set('minimap_grid', minimap_grid)

        self.global_manager.set('notification_manager', data_managers.notification_manager_template(self.global_manager))
        notification_tools.show_tutorial_notifications(self.global_manager)

        europe_grid_x = self.global_manager.get('default_display_width') - (strategic_grid_width + 340)
        europe_grid_y = self.global_manager.get('default_display_height') - (strategic_grid_height + 25)

        europe_grid = grids.abstract_grid(scaling.scale_coordinates(europe_grid_x, europe_grid_y, self.global_manager), scaling.scale_width(120, self.global_manager), scaling.scale_height(120, self.global_manager), 'black',
            'black', ['strategic', 'europe'], 3, 'locations/europe.png', 'Europe', self.global_manager)
        self.global_manager.set('europe_grid', europe_grid)

        game_transitions.set_game_mode('strategic', self.global_manager)
        game_transitions.create_strategic_map(self.global_manager)

        self.global_manager.get('minimap_grid').calibrate(2, 2)

        for current_commodity in self.global_manager.get('commodity_types'):
            if not current_commodity == 'consumer goods':
                market_tools.set_price(current_commodity, random.randrange(2, 6), self.global_manager) #2-5
            else:
                market_tools.set_price(current_commodity, 2, self.global_manager)

        self.global_manager.get('money_tracker').set(100)
        self.global_manager.get('turn_tracker').set(0)

        self.global_manager.set('player_turn', True)

        turn_management_tools.start_turn(self.global_manager, True)
        
    def save_game(self, file_path): #name.pickle file
        file_path = 'save_games/' + file_path
        saved_global_manager = data_managers.global_manager_template()
        for current_element in self.copied_elements: #save necessary data into new global manager
            #print(self.global_manager.get(current_element))
            #print(current_element)
            saved_global_manager.set(current_element, self.global_manager.get(current_element))
        #print(saved_global_manager.global_dict)

        #still need to save grid cell contents with inventories, terrain, and resource/village info, should be saved and loaded in before actors
            
        saved_actor_dicts = []
        for current_mob in self.global_manager.get('mob_list'):
            saved_actor_dicts.append(current_mob.to_save_dict())
        for current_building in self.global_manager.get('building_list'):
            saved_actor_dicts.append(current_building.to_save_dict())

        print(saved_actor_dicts)

        with open(file_path, 'wb') as handle: #write wb, read rb
            pickle.dump(saved_global_manager, handle) #saves new global manager with only necessary information to file
            pickle.dump(saved_actor_dicts, handle)
        text_tools.print_to_screen("Game successfully saved to " + file_path, self.global_manager)

    def load_game(self, file_path):
        try:
            file_path = 'save_games/' + file_path
            with open(file_path, 'rb') as handle:
                new_global_manager = pickle.load(handle)
                saved_actor_dicts = pickle.load(handle)
        except:
            text_tools.print_to_screen("The " + file_path + " file does not exist.", self.global_manager)
            return()
        for current_element in self.copied_elements:
            self.global_manager.set(current_element, new_global_manager.get(current_element))


        game_transitions.set_game_mode('strategic', self.global_manager)
        self.global_manager.get('minimap_grid').calibrate(2, 2)
        #turn_management_tools.start_turn(self.global_manager, True)

'''
To save grid:
save contents of each grid cell in a list of dictionaries: for each cell, have a dictionary with terrain, resource, village pop/aggressiveness/available_workers if applicable
make version of grid init function that takes cell list and creates that cell at the correct location and with the correct terrain and resource. If there is a village, record village attributes and make one

to save buildings:
make list of dictionaries with building type, location

to save mobs:
make list of dictionaries with unit type, location, veteran status, if group/in vehicle/in building make them first and attach upon creation somehow

Save these lists in the dictionary dumped into file and retrive them while loading

these should cover everything: each of these object types will need changes to initialization to allow feeding a dictionary and setting up initial state as alternative to normal initialization
Maybe change initialization for actors and grids to take a list of inputs and an initialization type string: depending on initialization type, call different init function with input list, within each init function set relevant values
to different list items
consider making input lists dictionaries instead
'''
