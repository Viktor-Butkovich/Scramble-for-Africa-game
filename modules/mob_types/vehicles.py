#Contains functionality for vehicle units

from .. import text_tools
from .. import utility
from .. import actor_utility
from .. import main_loop_tools
from ..mobs import mob
from ..buttons import button

class vehicle(mob):
    '''
    Mob that requires an attached worker to function and can carry other mobs as passengers
    '''
    def __init__(self, from_save, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates on one of the game grids
                'grids': grid list value - grids in which this mob's images can appear
                'image_dict': string/string dictionary value - dictionary of image type keys and file path values to the images used by this object in various situations, such as 'crewed': 'crewed_ship.png'
                'name': string value - Required if from save, this mob's name
                'modes': string list value - Game modes during which this mob's images can appear
                'end_turn_destination': string or int tuple value - Required if from save, 'none' if no saved destination, destination coordinates if saved destination
                'end_turn_destination_grid_type': string value - Required if end_turn_destination is not 'none', matches the global manager key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - Required if from save, how many movement points this actor currently has
                'crew': worker, string, or dictionary value - If no crew, equals 'none'. Otherwise, if creating a new vehicle, equals a worker that serves as crew. If loading, equals a dictionary of the saved information necessary to
                    recreate the worker to serve as crew
                'passenger_dicts': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each of this vehicle's passengers
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.initializing = True #when mobs embark a vehicle, the vehicle is selected if the vehicle is not initializing
        self.vehicle_type = 'vehicle'
        self.has_crew = False
        input_dict['image'] = input_dict['image_dict']['default']
        self.contained_mobs = []
        super().__init__(from_save, input_dict, global_manager)
        self.image_dict = input_dict['image_dict'] #should have default and uncrewed
        self.is_vehicle = True
        if not from_save:
            self.crew = input_dict['crew']
            if self.crew == 'none':
                self.has_crew = False
                self.set_image('uncrewed')
            else:
                self.has_crew = True
                self.set_image('uncrewed')
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self) #updates mob info display list to account for is_vehicle changing
        else: #create crew and passengers through recruitment_manager and embark them
            if input_dict['crew'] == 'none':
                self.crew = 'none'
            else:
                self.global_manager.get('actor_creation_manager').create(True, input_dict['crew'], self.global_manager).crew_vehicle(self) #creates worker and merges it as crew
            for current_passenger in input_dict['passenger_dicts']:
                self.global_manager.get('actor_creation_manager').create(True, current_passenger, self.global_manager).embark_vehicle(self) #create passengers and merge as passengers
        self.initializing = False
        self.set_controlling_minister_type(self.global_manager.get('type_minister_dict')['transportation'])

    def die(self):
        '''
        Description:
            Removes this object from relevant lists, prevents it from further appearing in or affecting the program, deselects it, and drops any commodities it is carrying. Also removes all of this vehicle's passengers
        Input:
            None
        Output:
            None
        '''
        super().die()
        for current_passenger in self.contained_mobs:
            current_passenger.die()
        if not self.crew == 'none':
            self.crew.die()

    def fire(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program. Also fires this vehicle's crew and passengers
        Input:
            None
        Output:
            None
        '''
        super().fire()
        for current_passenger in self.contained_mobs:
            current_passenger.fire()
        if not self.crew == 'none':
            self.crew.fire()

    def to_save_dict(self):
        '''
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
                'init_type': string value - Represents the type of actor this is, used to initialize the correct type of object on loading
                'coordinates': int tuple value - Two values representing x and y coordinates on one of the game grids
                'modes': string list value - Game modes during which this actor's images can appear
                'grid_type': string value - String matching the global manager key of this actor's primary grid, allowing loaded object to start in that grid
                'name': string value - This actor's name
                'inventory': string/string dictionary value - Version of this actor's inventory dictionary only containing commodity types with 1+ units held
                'end_turn_destination': string or int tuple value- 'none' if no saved destination, destination coordinates if saved destination
                'end_turn_destination_grid_type': string value - Required if end_turn_destination is not 'none', matches the global manager key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - How many movement points this actor currently has
                'image_dict': string value - dictionary of image type keys and file path values to the images used by this object in various situations, such as 'crewed': 'crewed_ship.png'
                'crew': string or dictionary value - If no crew, equals 'none'. Otherwise, equals a dictionary of the saved information necessary to recreate the worker to serve as crew
                'passenger_dicts': dictionary list value - list of dictionaries of saved information necessary to recreate each of this vehicle's passengers
        '''
        save_dict = super().to_save_dict()
        save_dict['image_dict'] = self.image_dict
        if self.crew == 'none':
            save_dict['crew'] = 'none'
        else:
            save_dict['crew'] = self.crew.to_save_dict()
        save_dict['passenger_dicts'] = [] #list of dictionaries for each passenger, on load a vehicle creates all of its passengers and embarks them
        for current_mob in self.contained_mobs:
            save_dict['passenger_dicts'].append(current_mob.to_save_dict())
        return(save_dict)

    def can_move(self, x_change, y_change):
        '''
        Description:
            Returns whether this mob can move to the tile x_change to the right of it and y_change above it. Movement can be prevented by not being able to move on water/land, the edge of the map, limited movement points, etc. Vehicles
                are not able to move without a crew
        Input:
            int x_change: How many cells would be moved to the right in the hypothetical movement
            int y_change: How many cells would be moved upward in the hypothetical movement
        Output:
            boolean: Returns True if this mob can move to the proposed destination, otherwise returns False
        '''
        if self.has_crew:
            return(super().can_move(x_change, y_change))
        else:
            text_tools.print_to_screen("A " + self.vehicle_type + " can not move without crew.", self.global_manager)
            return(False)
    
    def update_tooltip(self):
        '''
        Description:
            Sets this vehicle's tooltip to what it should be whenever the player looks at the tooltip. By default, sets tooltip to this vehicle's name, a description of its crew and each of its passengers, and its movement points
        Input:
            None
        Output:
            None
        '''
        tooltip_list = ["Name: " + self.name.capitalize()]
        if self.has_crew:
            tooltip_list.append("Crew: " + self.crew.name.capitalize())
        else:
            tooltip_list.append("Crew: None")
            tooltip_list.append("A " + self.vehicle_type + " can not move or take passengers or cargo without crew")
            
        if len(self.contained_mobs) > 0:
            tooltip_list.append("Passengers: ")
            for current_mob in self.contained_mobs:
                tooltip_list.append('    ' + current_mob.name.capitalize())
        else:
            tooltip_list.append("No passengers")

        if not self.has_infinite_movement:
            tooltip_list.append("Movement points: " + str(self.movement_points) + "/" + str(self.max_movement_points))
        else:
            tooltip_list.append("Movement points: infinite")
        self.set_tooltip(tooltip_list)

    def go_to_grid(self, new_grid, new_coordinates):
        '''
        Description:
            Links this vehicle to a grid, causing it to appear on that grid and its minigrid at certain coordinates. Used when crossing the ocean. Also moves this vehicle's crew and its passengers
        Input:
            grid new_grid: grid that this vehicle is linked to
            int tuple new_coordinates: Two values representing x and y coordinates to start at on the inputted grid
        Output:
            None
        '''
        super().go_to_grid(new_grid, new_coordinates)
        for current_mob in (self.contained_mobs + [self.crew]): #make list of all mobs in vehicle
            current_mob.go_to_grid(new_grid, new_coordinates)
            current_mob.in_vehicle = True
            current_mob.selected = False
            current_mob.hide_images()

class train(vehicle):
    '''
    Vehicle that can only move along railroads, has normal inventory capacity, and has 10 movement points
    '''
    def __init__(self, from_save, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates on one of the game grids
                'grids': grid list value - grids in which this mob's images can appear
                'image_dict': string/string dictionary value - dictionary of image type keys and file path values to the images used by this object in various situations, such as 'crewed': 'crewed_ship.png'
                'name': string value - Required if from save, this mob's name
                'modes': string list value - Game modes during which this mob's images can appear
                'end_turn_destination': string or int tuple value - Required if from save, 'none' if no saved destination, destination coordinates if saved destination
                'end_turn_destination_grid_type': string value - Required if end_turn_destination is not 'none', matches the global manager key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - Required if from save, how many movement points this actor currently has
                'crew': worker, string, or dictionary value - If no crew, equals 'none'. Otherwise, if creating a new vehicle, equals a worker that serves as crew. If loading, equals a dictionary of the saved information necessary to
                    recreate the worker to serve as crew
                'passenger_dicts': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each of this vehicle's passengers
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(from_save, input_dict, global_manager)
        self.set_max_movement_points(10)
        self.has_infinite_movement = True
        self.vehicle_type = 'train'
        self.can_swim = False
        self.can_walk = True
        self.can_hold_commodities = True
        self.inventory_capacity = 9
        if not from_save:
            self.inventory_setup()
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self)
        else:
            self.load_inventory(input_dict['inventory'])

    def can_move(self, x_change, y_change):
        '''
        Description:
            Returns whether this mob can move to the tile x_change to the right of it and y_change above it. Movement can be prevented by not being able to move on water/land, the edge of the map, limited movement points, etc. Vehicles
                are not able to move without a crew. Trains can only move along railroads
        Input:
            int x_change: How many cells would be moved to the right in the hypothetical movement
            int y_change: How many cells would be moved upward in the hypothetical movement
        Output:
            boolean: Returns True if this mob can move to the proposed destination, otherwise returns False
        '''
        result = super().can_move(x_change, y_change)
        if result:
            if not (self.images[0].current_cell.has_railroad() and self.grids[0].find_cell(self.x + x_change, self.y + y_change).has_railroad()):
                text_tools.print_to_screen("Trains can only move along railroads.", self.global_manager)
                return(False)
        return(result)

class ship(vehicle):
    '''
    Vehicle that can only move in the water and into ports, can cross the ocean, has large inventory capacity, and has infinite movement points
    '''
    def __init__(self, from_save, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates on one of the game grids
                'grids': grid list value - grids in which this mob's images can appear
                'image_dict': string/string dictionary value - dictionary of image type keys and file path values to the images used by this object in various situations, such as 'crewed': 'crewed_ship.png'
                'name': string value - Required if from save, this mob's name
                'modes': string list value - Game modes during which this mob's images can appear
                'end_turn_destination': string or int tuple value - Required if from save, 'none' if no saved destination, destination coordinates if saved destination
                'end_turn_destination_grid_type': string value - Required if end_turn_destination is not 'none', matches the global manager key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - Required if from save, how many movement points this actor currently has
                'crew': worker, string, or dictionary value - If no crew, equals 'none'. Otherwise, if creating a new vehicle, equals a worker that serves as crew. If loading, equals a dictionary of the saved information necessary to
                    recreate the worker to serve as crew
                'passenger_dicts': dictionary list value - Required if from save, list of dictionaries of saved information necessary to recreate each of this vehicle's passengers
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(from_save, input_dict, global_manager)
        self.set_max_movement_points(10)
        self.has_infinite_movement = True
        self.vehicle_type = 'ship'
        self.can_swim = True
        self.can_walk = False
        self.travel_possible = True #if this mob would ever be able to travel
        self.can_hold_commodities = True
        self.inventory_capacity = 27
        if not from_save:
            self.inventory_setup()
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self) #updates mob info display list to account for travel_possible changing
        else:
            self.load_inventory(input_dict['inventory'])

    def can_leave(self):
        '''
        Description:
            Returns whether this mob is allowed to move away from its current cell. A ship can not move away when there are any mobs in its tile that can not move on water and are not in a ship, preventing ships from leaving behind
                disembarking passengers
        Input:
            None
        Output:
            boolean: Returns False if this ship is in a water tile and there are any mobs in its tile that can not move on water and are not in a ship, otherwise returns True
        '''
        if self.images[0].current_cell.terrain == 'water':
            for current_mob in self.images[0].current_cell.contained_mobs:
                if not current_mob.can_swim:
                    text_tools.print_to_screen("A " + self.vehicle_type + " can not leave without taking unaccompanied units as passengers.", self.global_manager)
                    return(False)
        return(True)

    def can_travel(self): 
        '''
        Description:
            Returns whether this ship can cross the ocean, like going between Africa and Europe. Ships can only cross the ocean when they have a crew
        Input:
            None
        Output:
            boolean: Returs True if this ship has any crew, otherwise returns False
        '''
        if self.has_crew:
            return(True)
        else:
            return(False)