import random

from . import scaling
from . import notification_tools
from . import game_transitions
from . import grids
from . import data_managers
from . import turn_management_tools

class save_load_manager():
    def __init__(self, global_manager):
        self.global_manager = global_manager
        
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
                self.global_manager.get('commodity_prices')[current_commodity] = random.randrange(2, 6) #2-5
            else:
                self.global_manager.get('commodity_prices')[current_commodity] = 2

        self.global_manager.get('money_tracker').set(100)
        self.global_manager.get('turn_tracker').set(0)

        self.global_manager.set('player_turn', True)

        turn_management_tools.start_turn(self.global_manager, True)
                
