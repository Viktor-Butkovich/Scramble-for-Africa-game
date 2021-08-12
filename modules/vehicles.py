from . import text_tools
from . import utility
from . import actor_utility
from . import main_loop_tools
from .mobs import mob
from .buttons import button


class vehicle(mob):
    def __init__(self, coordinates, grids, image_id, name, modes, global_manager):
        self.contained_mobs = []
        super().__init__(coordinates, grids, image_id, name, modes, global_manager)
        self.is_vehicle = True
        self.can_travel = True

    def update_tooltip(self):
        tooltip_list = ["Name: " + self.name]
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
        for current_mob in self.contained_mobs:
            current_mob.go_to_grid(new_grid, new_coordinates)
            
            current_mob.in_vehicle = True
            current_mob.selected = False
            current_mob.hide_images()
            #current_mob.in_group = True
            #current_mob.join_group() #remove this
            #current_mob.hide_images() #hides images self.worker.hide_images()#
            #current_mob.in_vehicle = True

    def disembark(self):
        for current_mob in self.contained_mobs:
            current_mob.disembark_vehicle(self)
        self.contained_mobs = []

class ship(vehicle):
    def __init__(self, coordinates, grids, image_id, name, modes, global_manager):
        super().__init__(coordinates, grids, image_id, name, modes, global_manager)
        self.can_swim = True
        self.can_walk = False

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
                if len(selected_list) == 2:
                    vehicle = 'none'
                    rider = 'none'
                    if selected_list[0].is_vehicle and not selected_list[1].is_vehicle:
                        vehicle = selected_list[0]
                        rider = selected_list[1]
                    elif selected_list[1].is_vehicle and not selected_list[0].is_vehicle:
                        vehicle = selected_list[1]
                        rider = selected_list[0]
                    if not (vehicle == 'none' or rider == 'none'): #if vehicle and rider selected
                        if vehicle.x == rider.x and vehicle.y == rider.y: #ensure that this doesn't work across grids
                            rider.embark_vehicle(vehicle)
                        else:
                            text_tools.print_to_screen("You must select a unit in the same tile as a vehicle to embark the vehicle.", self.global_manager)
                    else:
                        text_tools.print_to_screen("You must select a unit in the same tile as a vehicle to embark the vehicle.", self.global_manager)
                else:
                    text_tools.print_to_screen("You must select a unit in the same tile as a vehicle to embark the vehicle.", self.global_manager)
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
                    text_tools.print_to_screen("You must have a vehicle with passengers selected to disembark passengers.", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not disembark from a vehicle.", self.global_manager)
