#Contains functionality for worker units

from .mobs import mob
from . import actor_utility
from . import utility

class worker(mob):
    '''
    Mob that is required for resource buildings to produce commodities, officers to form group, and vehicles to function
    '''
    def __init__(self, from_save, input_dict, global_manager):
        #def __init__(self, coordinates, grids, image_id, name, modes, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates on one of the game grids
            grid list grids: grids in which this mob's images can appear
            string image_id: File path to the image used by this object
            string name: This mob's name
            string list modes: Game modes during which this mob's images can appear
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(from_save, input_dict, global_manager)
        global_manager.get('worker_list').append(self)
        self.is_worker = True
        self.is_church_volunteers = False
        self.global_manager.set('num_workers', self.global_manager.get('num_workers') + 1)
        if not from_save:
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self) #updates mob info display list to account for is_worker changing

    def can_show_tooltip(self):
        '''
        Description:
            Returns whether this worker's tooltip can be shown. Along with the superclass' requirements, worker tooltips can not be shown when attached to another actor, such as when part of a group
        Input:
            None
        Output:
            None
        '''
        if not (self.in_group or self.in_vehicle):
            return(super().can_show_tooltip())
        else:
            return(False)

    def crew_vehicle(self, vehicle): #to do: make vehicle go to front of info display
        '''
        Description:
            Orders this worker to crew the inputted vehicle, attaching this worker to the vehicle and allowing the vehicle to function
        Input:
            vehicle vehicle: vehicle to which this worker is attached
        Output:
            None
        '''
        self.in_vehicle = True
        self.selected = False
        self.hide_images()
        vehicle.crew = self
        vehicle.has_crew = True
        vehicle.set_image('crewed')
        moved_mob = vehicle
        for current_image in moved_mob.images: #moves vehicle to front
            if not current_image.current_cell == 'none':
                while not moved_mob == current_image.current_cell.contained_mobs[0]:
                    current_image.current_cell.contained_mobs.append(current_image.current_cell.contained_mobs.pop(0))
        vehicle.select()

    def uncrew_vehicle(self, vehicle):
        '''
        Description:
            Orders this worker to stop crewing the inputted vehicle, making this worker independent from the vehicle and preventing the vehicle from functioning
        Input:
            vehicle vehicle: vehicle to which this worker is no longer attached
        Output:
            None
        '''
        self.in_vehicle = False
        self.x = vehicle.x
        self.y = vehicle.y
        self.show_images()
        vehicle.crew = 'none'
        vehicle.has_crew = False
        vehicle.set_image('uncrewed')
        vehicle.end_turn_destination = 'none'
        vehicle.hide_images()
        vehicle.show_images() #bring vehicle to front of tile
        actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), self.images[0].current_cell.tile)

    def join_group(self):
        '''
        Description:
            Hides this worker when joining a group, preventing it from being directly interacted with until the group is disbanded
        Input:
            None
        Output:
            None
        '''
        self.in_group = True
        self.selected = False
        self.hide_images()

    def leave_group(self, group):
        '''
        Description:
            Reveals this worker when its group is disbanded, allowing it to be directly interacted with. Does not select this worker, meaning that the officer will be selected rather than the worker when a group is disbanded
        Input:
            group group: group from which this worker is leaving
        Output:
            None
        '''
        self.in_group = False
        self.x = group.x
        self.y = group.y
        self.show_images()

    def remove(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program
        Input:
            None
        Output:
            None
        '''
        super().remove()
        self.global_manager.set('worker_list', utility.remove_from_list(self.global_manager.get('worker_list'), self))
        self.global_manager.set('num_workers', self.global_manager.get('num_workers') - 1)

    def work_building(self, building):
        '''
        Description:
            Orders this worker to work in the inputted building, attaching this worker to the building and allowing the building to function. A resource production building with an attached worker produces a commodity every turn
        Input:
            building building: building to which this worker is attached
        Output:
            None
        '''
        self.in_building = True
        self.selected = False
        self.hide_images()
        building.contained_workers.append(self)
        actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), building.images[0].current_cell.tile) #update tile ui with worked building
        actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), 'none')

    def leave_building(self, building):
        '''
        Description:
            Orders this worker to stop working in the inputted building, making this worker independent from the building and preventing the building from functioning
        Input:
            building building: building to which this worker is no longer attached
        Output:
            None
        '''
        self.in_building = False
        self.show_images()
        building.contained_workers = utility.remove_from_list(building.contained_workers, self)
        actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), self.images[0].current_cell.tile) #update tile ui with worked building
        self.select()

class church_volunteers(worker):
    '''
    Worker with no cost that can join with a head missionary to form missionaries, created through religious campaigns
    '''
    def __init__(self, from_save, input_dict, global_manager):
        #def __init__(self, coordinates, grids, image_id, name, modes, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates on one of the game grids
            grid list grids: grids in which this mob's images can appear
            string image_id: File path to the image used by this object
            string name: This mob's name
            string list modes: Game modes during which this mob's images can appear
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(from_save, input_dict, global_manager)
        self.global_manager.set('num_workers', self.global_manager.get('num_workers') - 1)
        self.is_church_volunteers = True
        
