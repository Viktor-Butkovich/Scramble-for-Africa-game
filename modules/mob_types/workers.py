#Contains functionality for worker units
import random

from .pmobs import pmob
from .. import actor_utility
from .. import utility
from .. import market_tools
from .. import text_tools

class worker(pmob):
    '''
    pmob that is required for resource buildings to produce commodities, officers to form group, and vehicles to function
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
                'image': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'name': string value - Required if from save, this mob's name
                'modes': string list value - Game modes during which this mob's images can appear
                'end_turn_destination': string or int tuple value - Required if from save, 'none' if no saved destination, destination coordinates if saved destination
                'end_turn_destination_grid_type': string value - Required if end_turn_destination is not 'none', matches the global manager key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - Required if from save, how many movement points this actor currently has
                'max_movement_points': int value - Required if from save, maximum number of movement points this mob can have
                'worker_type': string value - Type of worker this is, like 'European'. Each type of worker has a separate upkeep, labor pool, and abilities
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(from_save, input_dict, global_manager)
        self.number = 2 #workers is plural
        global_manager.get('worker_list').append(self)
        self.is_worker = True
        self.is_church_volunteers = False
        self.worker_type = input_dict['worker_type'] #European, African, religious, slave
        
        if self.worker_type == 'European': #European church volunteers don't count for this because they have no upkeep
            self.global_manager.set('num_european_workers', self.global_manager.get('num_european_workers') + 1)
            if not from_save:
                market_tools.attempt_worker_upkeep_change('increase', self.worker_type, self.global_manager)
            
        elif self.worker_type == 'African':
            self.global_manager.set('num_african_workers', self.global_manager.get('num_african_workers') + 1)
            if not from_save:
                market_tools.attempt_worker_upkeep_change('increase', self.worker_type, self.global_manager)
                
        self.set_controlling_minister_type(self.global_manager.get('type_minister_dict')['production'])
        if not from_save:
            self.second_image_variant = random.randrange(0, len(self.image_variants))
            if ('select_on_creation' in input_dict) and input_dict['select_on_creation']:
                actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display'), self) #updates mob info display list to account for is_worker changing
                self.selection_sound()
        self.global_manager.get('money_label').check_for_updates()
        self.update_image_bundle()

    def replace(self, attached_group = 'none'):
        '''
        Description:
            Replaces this unit for a new version of itself when it dies from attrition, removing all experience and name modifications. Also finds a nearby worker to replace with if possible, such as recruiting an available African
                worker from a nearby village if any exist, incurring the usual recruitment costs/upkeep increases
        Input:
            None
        Output:
            None
        '''
        super().replace()
        if attached_group == 'none':
            destination = self
        else:
            destination = attached_group
        destination_message = ' for the ' + destination.name + ' at (' + str(destination.x) + ', ' + str(destination.y) + ')'
        if self.worker_type in ['European', 'African']: #increase relevant costs as if recruiting new worker
            if self.worker_type == 'African': #get worker from nearest slum or village
                new_worker_source = actor_utility.find_closest_available_worker(destination, self.global_manager)
                if not new_worker_source == 'none':
                    market_tools.attempt_worker_upkeep_change('increase', self.worker_type, self.global_manager)
                    if new_worker_source in self.global_manager.get('village_list'): #both village and slum have change_population, but slum change population automatically changes number of workers while village does not
                        new_worker_source.available_workers -= 1
                    new_worker_source.change_population(-1)

                    if new_worker_source in self.global_manager.get('village_list'):
                        text_tools.print_to_screen('Replacement workers have been automatically hired from ' + new_worker_source.name + ' village at (' + str(new_worker_source.x) + ', ' + str(new_worker_source.y) + ')' + destination_message + '.',
                            self.global_manager)
                    elif new_worker_source in self.global_manager.get('slums_list'):
                        text_tools.print_to_screen('Replacement workers have been automatically hired from the slums at (' + str(new_worker_source.x) + ', ' + str(new_worker_source.y) + ')' + destination_message + '.', self.global_manager)
                    
                else: #if no villages or slums with available workers, recruit abstract African workers and give bigger upkeep penalty to compensate
                    market_tools.attempt_worker_upkeep_change('increase', self.worker_type, self.global_manager)
                    market_tools.attempt_worker_upkeep_change('increase', self.worker_type, self.global_manager)
                    text_tools.print_to_screen('As there were no available workers in nearby slums and villages, replacement workers were automatically hired from a nearby colony' + destination_message + ', incurring an increased penalty on African worker upkeep.',
                        self.global_manager)
                    
            elif self.worker_type == 'European':
                market_tools.attempt_worker_upkeep_change('increase', self.worker_type, self.global_manager)
                text_tools.print_to_screen('Replacement workers have been automatically hired from Europe' + destination_message + '.', self.global_manager)
                
        elif self.worker_type == 'slave':
            self.global_manager.get('money_tracker').change(self.global_manager.get('recruitment_costs')['slave workers'] * -1, 'attrition_replacements')
            actor_utility.set_slave_traders_strength(self.global_manager.get('slave_traders_strength') + 1, self.global_manager)
            #self.global_manager.set('slave_traders_strength', self.global_manager.get('slave_traders_strength') + 1)
            text_tools.print_to_screen('Replacement slave workers were automatically purchased' + destination_message + ', costing ' + str(self.global_manager.get('recruitment_costs')['slave workers']) + ' money.', self.global_manager)
            market_tools.attempt_slave_recruitment_cost_change('increase', self.global_manager)

            if self.global_manager.get('effect_manager').effect_active('no_slave_trade_penalty'):
                text_tools.print_to_screen('Your country\'s prolonged involvement with the slave trade prevented any public opinion penalty.', self.global_manager)
            else:
                public_opinion_penalty = 5 + random.randrange(-3, 4) #2-8
                current_public_opinion = self.global_manager.get('public_opinion_tracker').get()
                self.global_manager.get('public_opinion_tracker').change(-1 * public_opinion_penalty)
                resulting_public_opinion = self.global_manager.get('public_opinion_tracker').get()
                if not resulting_public_opinion == current_public_opinion:
                    text_tools.print_to_screen('Participating in the slave trade has decreased your public opinion from ' + str(current_public_opinion) + ' to ' + str(resulting_public_opinion) + '.', self.global_manager)

        elif self.worker_type == 'religious':
            text_tools.print_to_screen('Replacement religious volunteers have been automatically found among nearby colonists.', self.global_manager)

    def to_save_dict(self):
        '''
        Description:
            Uses this object's values to create a dictionary that can be saved and used as input to recreate it on loading
        Input:
            None
        Output:
            dictionary: Returns dictionary that can be saved and used as input to recreate it on loading
                Along with superclass outputs, also saves the following values:
                'worker_type': string value - Type of worker this is, like 'European'. Each type of worker has a separate upkeep, labor pool, and abilities
        '''
        save_dict = super().to_save_dict()
        save_dict['worker_type'] = self.worker_type
        return(save_dict)

    def fire(self, wander = True):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program. Additionally has a chance to decrease the upkeep of other workers of this worker's type by increasing the size of
                the labor pool
        Input:
            None
        Output:
            None
        '''
        super().fire()
        if self.worker_type in ['African', 'European']: #not religious volunteers
            market_tools.attempt_worker_upkeep_change('decrease', self.worker_type, self.global_manager)
        if self.worker_type == 'African' and wander:
            text_tools.print_to_screen('These fired workers will wander and eventually settle down in one of your slums.', self.global_manager)
            self.global_manager.set('num_wandering_workers', self.global_manager.get('num_wandering_workers') + 1)
        elif self.worker_type in ['European', 'religious']:
            current_public_opinion = self.global_manager.get('public_opinion')
            self.global_manager.get('public_opinion_tracker').change(-1)
            resulting_public_opinion = self.global_manager.get('public_opinion')
            if not current_public_opinion == resulting_public_opinion:
                text_tools.print_to_screen('Firing ' + self.name + ' reflected poorly on your company and reduced your public opinion from ' + str(current_public_opinion) + ' to ' + str(resulting_public_opinion) + '.', self.global_manager)

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
        vehicle.set_crew(self)
        moved_mob = vehicle
        for current_image in moved_mob.images: #moves vehicle to front
            if not current_image.current_cell == 'none':
                while not moved_mob == current_image.current_cell.contained_mobs[0]:
                    current_image.current_cell.contained_mobs.append(current_image.current_cell.contained_mobs.pop(0))
        self.remove_from_turn_queue()
        vehicle.add_to_turn_queue()
        if not vehicle.initializing: #don't select vehicle if loading in at start of game
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display'), 'none', override_exempt=True)
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
        if self.images[0].current_cell.get_intact_building('port') == 'none':
            self.set_disorganized(True)
        vehicle.set_crew('none')
        vehicle.end_turn_destination = 'none'
        vehicle.hide_images()
        vehicle.show_images() #bring vehicle to front of tile
        vehicle.remove_from_turn_queue()
        actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display'), 'none', override_exempt=True)
        vehicle.select()
        self.add_to_turn_queue()
        self.update_image_bundle()
        actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display'), self.images[0].current_cell.tile)

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
        self.remove_from_turn_queue()

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
        self.disorganized = group.disorganized
        self.go_to_grid(self.images[0].current_cell.grid, (self.x, self.y))
        if self.movement_points > 0:
            self.add_to_turn_queue()
        self.update_image_bundle()

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
        if self.worker_type == 'European': #European church volunteers don't count for this because they have no upkeep
            self.global_manager.set('num_european_workers', self.global_manager.get('num_european_workers') - 1)
        elif self.worker_type == 'African':
            self.global_manager.set('num_african_workers', self.global_manager.get('num_african_workers') - 1)
        self.global_manager.get('money_label').check_for_updates()

    def image_variants_setup(self, from_save, input_dict):
        '''
        Description:
            Sets up this unit's image variants
        Input:
            boolean from_save: True if this object is being recreated from a save file, False if it is being newly created
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
        Output:
            None
        '''
        if not input_dict['worker_type'] == 'religious':
            for variant_type in ['soldier', 'porter']: #adds image_dict['soldier']: '.../soldier.png' and image_dict['porter']: '.../porter.png' if any are present in folders
                variants = actor_utility.get_image_variants(self.image_dict['default'], keyword = variant_type)
                if len(variants) > 0:
                    self.image_dict[variant_type] = random.choice(variants)
        super().image_variants_setup(from_save, input_dict)

    def get_image_id_list(self, override_values={}):
        '''
        Description:
            Generates and returns a list this actor's image file paths and dictionaries that can be passed to any image object to display those images together in a particular order and 
                orientation
        Input:
            None
        Output:
            list: Returns list of string image file paths, possibly combined with string key dictionaries with extra information for offset images
        '''
        image_id_list = super().get_image_id_list(override_values)
        image_id_list.remove(self.image_dict['default']) #remove default middle worker
        left_worker_dict = {
            'image_id': self.image_dict['default'],
            'size': 0.85,
            'x_offset': -0.25,
            'y_offset': 0,
            'level': -1
        }
        image_id_list.append(left_worker_dict)

        right_worker_dict = left_worker_dict.copy()
        right_worker_dict['image_id'] = self.image_variants[self.second_image_variant]
        right_worker_dict['x_offset'] *= -1
        image_id_list.append(right_worker_dict)
        return(image_id_list)

class slave_worker(worker):
    '''
    Worker that is captured or bought from slave traders, reduces public opinion, and has a low, unvarying upkeep and a varying recruitment cost
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
                'image': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'name': string value - Required if from save, this mob's name
                'modes': string list value - Game modes during which this mob's images can appear
                'end_turn_destination': string or int tuple value - Required if from save, 'none' if no saved destination, destination coordinates if saved destination
                'end_turn_destination_grid_type': string value - Required if end_turn_destination is not 'none', matches the global manager key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - Required if from save, how many movement points this actor currently has
                'purchased': boolean value - Value set to true if the slaves were bought or false if they were captured, determining effects on public opinion and slave recruitment costs
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['worker_type'] = 'slave'
        super().__init__(from_save, input_dict, global_manager)
        if not from_save:
            if input_dict['purchased']: #as opposed to captured
                if not self.global_manager.get('effect_manager').effect_active('no_slave_trade_penalty'):
                    public_opinion_penalty = 5 + random.randrange(-3, 4) #2-8
                    current_public_opinion = self.global_manager.get('public_opinion_tracker').get()
                    self.global_manager.get('public_opinion_tracker').change(-1 * public_opinion_penalty)
                    resulting_public_opinion = self.global_manager.get('public_opinion_tracker').get()
                    if not resulting_public_opinion == current_public_opinion:
                        text_tools.print_to_screen('Participating in the slave trade has decreased your public opinion from ' + str(current_public_opinion) + ' to ' + str(resulting_public_opinion) + '.', self.global_manager)
                market_tools.attempt_slave_recruitment_cost_change('increase', self.global_manager)
                self.global_manager.get('evil_tracker').change(6)
                actor_utility.set_slave_traders_strength(self.global_manager.get('slave_traders_strength') + 1, self.global_manager)
            else:
                public_opinion_penalty = 5 + random.randrange(-3, 4) #2-8
                current_public_opinion = self.global_manager.get('public_opinion_tracker').get()
                self.global_manager.get('public_opinion_tracker').change(-1 * public_opinion_penalty)
                resulting_public_opinion = self.global_manager.get('public_opinion_tracker').get()
                if not resulting_public_opinion == current_public_opinion:
                    text_tools.print_to_screen('Your use of captured slaves has decreased your public opinion from ' + str(current_public_opinion) + ' to ' + str(resulting_public_opinion) + '.', self.global_manager)
                self.global_manager.get('evil_tracker').change(6)
        self.global_manager.set('num_slave_workers', self.global_manager.get('num_slave_workers') + 1)
        self.set_controlling_minister_type(self.global_manager.get('type_minister_dict')['production'])
        if not from_save:
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display'), self) #updates mob info display list to account for is_worker changing
        self.global_manager.get('money_label').check_for_updates()
        if self.global_manager.get('slave_traders_strength') <= 0:
            self.automatically_replace = False

    def fire(self, wander = True):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program. Firing a slave worker unit also frees them, increasing public opinion and adding them to the labor pool
        Input:
            None
        Output:
            None
        '''
        super().fire(wander)
        self.free(wander)

    def free(self, wander = True):
        '''
        Description:
            Frees this slave, increasing public opinion and adding them to the labor pool, followed by either re-recruiting them as African workers or allowing them to wander and settle in 
                slums
        '''
        market_tools.attempt_worker_upkeep_change('decrease', 'African', self.global_manager)
        public_opinion_bonus = 4 + random.randrange(-3, 4) #1-7, less bonus than penalty for buying slaves on average
        current_public_opinion = self.global_manager.get('public_opinion_tracker').get()
        self.global_manager.get('public_opinion_tracker').change(public_opinion_bonus)
        resulting_public_opinion = self.global_manager.get('public_opinion_tracker').get()
        if not resulting_public_opinion == current_public_opinion:
            text_tools.print_to_screen('Freeing slaves has increased your public opinion from ' + str(current_public_opinion) + ' to ' + str(resulting_public_opinion) + '.', self.global_manager)
        if wander:
            text_tools.print_to_screen('These freed slaves will wander and eventually settle down in one of your slums', self.global_manager)
            self.global_manager.set('num_wandering_workers', self.global_manager.get('num_wandering_workers') + 1)
        self.global_manager.get('evil_tracker').change(-2)

    def free_and_replace(self):
        '''
        Description:
            Frees this slave and immediately recruits them as an African worker, only usable when not in a group
        '''
        input_dict = {}
        input_dict['coordinates'] = (self.x, self.y)
        input_dict['grids'] = self.grids
        input_dict['modes'] = self.modes
        input_dict['image'] = 'mobs/African workers/default.png'
        input_dict['name'] = 'African workers'
        input_dict['init_type'] = 'workers'
        input_dict['worker_type'] = 'African'
        input_dict['select_on_creation'] = self.selected
        new_worker = self.global_manager.get('actor_creation_manager').create(False, input_dict, self.global_manager)
        new_worker.set_automatically_replace(self.automatically_replace)
        if self.in_vehicle:
            new_worker.embark_vehicle(self.vehicle, focus = False)
            self.disembark_vehicle(self.vehicle, focus = False)
        self.fire(wander = False)
        
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
        self.global_manager.set('num_slave_workers', self.global_manager.get('num_slave_workers') - 1)
        self.global_manager.set('worker_list', utility.remove_from_list(self.global_manager.get('worker_list'), self))
        self.global_manager.get('money_label').check_for_updates()

class church_volunteers(worker):
    '''
    Worker with no cost that can join with a head missionary to form missionaries, created through religious campaigns
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
                'image': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'name': string value - Required if from save, this mob's name
                'modes': string list value - Game modes during which this mob's images can appear
                'end_turn_destination': string or int tuple value - Required if from save, 'none' if no saved destination, destination coordinates if saved destination
                'end_turn_destination_grid_type': string value - Required if end_turn_destination is not 'none', matches the global manager key of the end turn destination grid, allowing loaded object to have that grid as a destination
                'movement_points': int value - Required if from save, how many movement points this actor currently has
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['worker_type'] = 'religious'
        super().__init__(from_save, input_dict, global_manager)
        self.set_controlling_minister_type(self.global_manager.get('type_minister_dict')['religion'])
        self.global_manager.set('num_church_volunteers', self.global_manager.get('num_church_volunteers') + 1)

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
        self.global_manager.set('num_church_volunteers', self.global_manager.get('num_church_volunteers') - 1)
        self.global_manager.get('money_label').check_for_updates()
