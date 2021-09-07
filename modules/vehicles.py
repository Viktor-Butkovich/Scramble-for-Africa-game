from . import text_tools
from . import utility
from . import actor_utility
from . import main_loop_tools
from .mobs import mob
from .buttons import button

class vehicle(mob): #maybe reduce movement points of both vehicle and crew to the lower of the two
    def __init__(self, coordinates, grids, image_dict, name, modes, crew, global_manager):
        self.contained_mobs = []
        self.vehicle_type = 'vehicle'
        self.has_crew = False
        super().__init__(coordinates, grids, image_dict['default'], name, modes, global_manager)
        self.image_dict = image_dict #should have default and uncrewed
        self.is_vehicle = True
        self.crew = crew
        if self.crew == 'none':
            self.has_crew = False
            self.set_image('uncrewed')
        else:
            self.has_crew = True
            self.set_image('uncrewed')
        actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self) #updates mob info display list to account for is_vehicle changing

    def can_move(self, x_change, y_change):
        if self.has_crew:
            return(super().can_move(x_change, y_change))
        else:
            text_tools.print_to_screen("A " + self.vehicle_type + " can not move without crew.", self.global_manager)
            return(False)
    
    def update_tooltip(self):
        tooltip_list = ["Name: " + self.name]
        if self.has_crew:
            tooltip_list.append("Crew: " + self.crew.name)
        else:
            tooltip_list.append("Crew: none")
            tooltip_list.append("A " + self.vehicle_type + " can not move or take passengers or cargo without crew")
            
        if len(self.contained_mobs) > 0:
            tooltip_list.append("Passengers: ")
            for current_mob in self.contained_mobs:
                tooltip_list.append('    ' + current_mob.name)
        else:
            tooltip_list.append("No passengers")
            
        tooltip_list.append("Movement points: " + str(self.movement_points) + "/" + str(self.max_movement_points))
        self.set_tooltip(tooltip_list)

    def go_to_grid(self, new_grid, new_coordinates):
        super().go_to_grid(new_grid, new_coordinates)
        for current_mob in (self.contained_mobs + [self.crew]): #make list of all mobs in vehicle
            current_mob.go_to_grid(new_grid, new_coordinates)
            current_mob.in_vehicle = True
            current_mob.selected = False
            current_mob.hide_images()

    #def disembark(self, disembarker):
        #for current_mob in self.contained_mobs:
        #    current_mob.disembark_vehicle(self)
        #first_mob = self.contained_mobs[0]
        #self.contained_mobs = []
        #if self.global_manager.get('minimap_grid') in self.grids:
        #    self.global_manager.get('minimap_grid').calibrate(self.x, self.y)
        #first_mob.select()
        #disembarker.select()
        #actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), first_mob)

class train(vehicle):
    def __init__(self, coordinates, grids, image_dict, name, modes, crew, global_manager):
        super().__init__(coordinates, grids, image_dict, name, modes, crew, global_manager)
        self.set_max_movement_points(10)
        self.has_infinite_movement = True
        self.vehicle_type = 'train'
        self.can_swim = False
        self.can_walk = True
        self.can_hold_commodities = True
        self.inventory_capacity = 50
        self.inventory_setup()
        actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self)

    def can_move(self, x_change, y_change):
        result = super().can_move(x_change, y_change)
        if result:
            if not (self.images[0].current_cell.has_railroad() and self.grids[0].find_cell(self.x + x_change, self.y + y_change).has_railroad()):
                text_tools.print_to_screen("Trains can only move along railroads.", self.global_manager)
                return(False)
        return(result)

class ship(vehicle): #prevent movement when there are mobs in this tile that are not in a ship
    def __init__(self, coordinates, grids, image_dict, name, modes, crew, global_manager):
        super().__init__(coordinates, grids, image_dict, name, modes, crew, global_manager)
        self.set_max_movement_points(10)
        self.has_infinite_movement = True
        self.vehicle_type = 'ship'
        self.can_swim = True
        self.can_walk = False
        self.travel_possible = True #if this mob would ever be able to travel
        self.can_hold_commodities = True
        self.inventory_capacity = 50
        self.inventory_setup()
        actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self) #updates mob info display list to account for travel_possible changing

    def can_leave(self): #can not move away if leaving behind units that can't swim in water
        if self.images[0].current_cell.terrain == 'water':
            for current_mob in self.images[0].current_cell.contained_mobs:
                if not current_mob.can_swim:
                    text_tools.print_to_screen("A " + self.vehicle_type + " can not leave without taking unaccompanied units as passengers.", self.global_manager)
                    return(False)
        return(True)

    def can_travel(self): #if this mob is currently able to travel
        if self.has_crew:
            return(True)
        else:
            return(False)
