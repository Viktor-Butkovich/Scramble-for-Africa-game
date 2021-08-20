from .mobs import mob
from . import actor_utility
from . import utility

class worker(mob):
    '''
    Mob that is considered a worker and can join groups
    '''
    def __init__(self, coordinates, grids, image_id, name, modes, global_manager):
        '''
        Input:
            same as superclass 
        '''
        super().__init__(coordinates, grids, image_id, name, modes, global_manager)
        global_manager.get('worker_list').append(self)
        self.is_worker = True
        self.global_manager.set('num_workers', self.global_manager.get('num_workers') + 1)

    def can_show_tooltip(self):
        '''
        Input:
            none
        Output:
            Same as superclass but only returns True if not part of a group
        '''
        if not (self.in_group or self.in_vehicle):
            return(super().can_show_tooltip())
        else:
            return(False)

    def crew_vehicle(self, vehicle):
        self.in_vehicle = True
        self.selected = False
        self.hide_images()
        vehicle.crew = self
        vehicle.has_crew = True
        vehicle.set_image('crewed')
        actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), vehicle)

    def uncrew_vehicle(self, vehicle):
        self.in_vehicle = False
        self.x = vehicle.x
        self.y = vehicle.y
        self.show_images()
        vehicle.crew = 'none'
        vehicle.has_crew = False
        vehicle.set_image('uncrewed')
        vehicle.end_turn_destination = 'none'
        #self.select()
        vehicle.hide_images()
        vehicle.show_images() #bring vehicle to front of tile
        actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), self.images[0].current_cell.tile)

    def join_group(self):
        '''
        Input:
            none
        Output:
            Prevents this worker from being seen and interacted with, storing it as part of a group
        '''
        self.in_group = True
        self.selected = False
        self.hide_images()

    def leave_group(self, group):
        '''
        Input:
            group object from which this worker is leaving
        Output:
            Allows this worker to be seen and interacted with, moving it to where the group was disbanded
        '''
        self.in_group = False
        self.x = group.x
        self.y = group.y
        self.show_images()
        #for current_image in self.images:
        #    current_image.add_to_cell()

    def remove(self):
        '''
        Input:
            none
        Output:
            Removes the object from relevant lists and prevents it from further appearing in or affecting the program
        '''
        super().remove()
        self.global_manager.set('worker_list', utility.remove_from_list(self.global_manager.get('worker_list'), self))
        self.global_manager.set('num_workers', self.global_manager.get('num_workers') - 1)

    def work_building(self, building):
        self.in_building = True
        self.selected = False
        self.hide_images()
        building.contained_workers.append(self)
        actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), building.images[0].current_cell.tile) #update tile ui with worked building
        actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), 'none')

    def leave_building(self, building):
        self.in_building = False
        self.show_images()
        building.contained_workers = utility.remove_from_list(building.contained_workers, self)
        actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), self.images[0].current_cell.tile) #update tile ui with worked building
        #actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), 'none')
        self.select()
        #for current_image in self.images:
        #    current_image.add_to_cell()
