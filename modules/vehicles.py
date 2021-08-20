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

    def disembark(self):
        for current_mob in self.contained_mobs:
            current_mob.disembark_vehicle(self)
        first_mob = self.contained_mobs[0]
        self.contained_mobs = []
        if self.global_manager.get('minimap_grid') in self.grids:
            self.global_manager.get('minimap_grid').calibrate(self.x, self.y)
        first_mob.select()
        #actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), first_mob)

class ship(vehicle): #prevent movement when there are mobs in this tile that are not in a ship
    def __init__(self, coordinates, grids, image_dict, name, modes, crew, global_manager):
        super().__init__(coordinates, grids, image_dict, name, modes, crew, global_manager)
        self.set_max_movement_points(3)
        self.vehicle_type = 'ship'
        self.can_swim = True
        self.can_walk = False

    def can_leave(self): #can not move away if leaving behind units that can't swim in water
        if self.images[0].current_cell.terrain == 'water':
            for current_mob in self.images[0].current_cell.contained_mobs:
                if not current_mob.can_swim:
                    text_tools.print_to_screen("A " + self.vehicle_type + " can not leave without taking unaccompanied units as passengers.", self.global_manager)
                    return(False)
        return(True)

    def can_travel(self):
        if self.has_crew:
            return(True)
        else:
            return(False)

class embark_vehicle_button(button):
    def __init__(self, coordinates, width, height, color, keybind_id, modes, image_id, global_manager):
        super().__init__(coordinates, width, height, color, 'embark', keybind_id, modes, image_id, global_manager)
        
    def can_show(self):
        if actor_utility.can_embark_vehicle(self.global_manager):
            return(super().can_show())
        else:
            return(False)

    def on_click(self):
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):    
                selected_list = actor_utility.get_selected_list(self.global_manager)
                num_vehicles = 0
                vehicle = 'none'
                riders = []
                for current_mob in selected_list:
                    if current_mob.is_vehicle:
                        num_vehicles += 1
                        vehicle = current_mob
                    else:
                        riders.append(current_mob)
                if num_vehicles == 1 and len(riders) > 0:
                    same_tile = True
                    for current_rider in riders:
                        if not (vehicle.x == current_rider.x and vehicle.y == current_rider.y and current_rider.grids[0] in vehicle.grids): #if not in same tile, stop
                            same_tile = False
                    if same_tile:
                        for current_rider in riders:
                            current_rider.embark_vehicle(vehicle)
                    else:
                        text_tools.print_to_screen("You must select units in the same tile as a vehicle to embark the vehicle.", self.global_manager)

                else:
                    text_tools.print_to_screen("You must select units in the same tile as a vehicle to embark the vehicle.", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not embark a vehicle.", self.global_manager)

class disembark_vehicle_button(button):
    def __init__(self, coordinates, width, height, color, keybind_id, modes, image_id, global_manager):
        super().__init__(coordinates, width, height, color, 'disembark', keybind_id, modes, image_id, global_manager)
        
    def can_show(self):
        if actor_utility.can_disembark_vehicle(self.global_manager):
            return(super().can_show())
        else:
            return(False)

    def on_click(self):
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):         
                selected_list = actor_utility.get_selected_list(self.global_manager)
                if len(selected_list) == 1 and selected_list[0].is_vehicle and len(selected_list[0].contained_mobs) > 0:
                    selected_list[0].disembark()
                else:
                    text_tools.print_to_screen("You must select a vehicle with passengers to disembark passengers.", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not disembark from a vehicle.", self.global_manager)

class crew_vehicle_button(button):
    def __init__(self, coordinates, width, height, color, keybind_id, modes, image_id, global_manager):
        super().__init__(coordinates, width, height, color, 'crew', keybind_id, modes, image_id, global_manager)
        
    def can_show(self):
        if actor_utility.can_crew_vehicle(self.global_manager):
            return(super().can_show())
        else:
            return(False)

    def on_click(self):
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):    
                selected_list = actor_utility.get_selected_list(self.global_manager)
                if len(selected_list) == 1 and selected_list[0].is_vehicle and not selected_list[0].has_crew:
                    vehicle = selected_list[0]
                    crew = 'none'
                    for contained_mob in vehicle.images[0].current_cell.contained_mobs:
                        if contained_mob.is_worker:
                            crew = contained_mob
                    if (not (vehicle == 'none' or crew == 'none')) and (not vehicle.has_crew): #if vehicle and rider selected
                        if vehicle.x == crew.x and vehicle.y == crew.y: #ensure that this doesn't work across grids
                            crew.crew_vehicle(vehicle)
                        else:
                            text_tools.print_to_screen("You must select an uncrewed vehicle in the same tile as a worker to crew the vehicle.", self.global_manager)
                    else:
                        text_tools.print_to_screen("You must select an uncrewed vehicle in the same tile as a worker to crew the vehicle.", self.global_manager)
                else:
                    text_tools.print_to_screen("You must select an uncrewed vehicle in the same tile as a worker to crew the vehicle.", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not crew a vehicle.", self.global_manager)

class uncrew_vehicle_button(button): #later only allow uncrewing in a port
    def __init__(self, coordinates, width, height, color, keybind_id, modes, image_id, global_manager):
        super().__init__(coordinates, width, height, color, 'uncrew', keybind_id, modes, image_id, global_manager)
        
    def can_show(self):
        if actor_utility.can_uncrew_vehicle(self.global_manager):
            return(super().can_show())
        else:
            return(False)

    def on_click(self):
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):         
                selected_list = actor_utility.get_selected_list(self.global_manager)
                if len(selected_list) == 1 and selected_list[0].is_vehicle and len(selected_list[0].contained_mobs) == 0 and selected_list[0].has_crew:
                    vehicle = selected_list[0]
                    crew = vehicle.crew
                    crew.uncrew_vehicle(vehicle)
                else:
                    text_tools.print_to_screen("You must select a crewed vehicle with no passengers to remove the crew.", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not remove a vehicle's crew.", self.global_manager)
