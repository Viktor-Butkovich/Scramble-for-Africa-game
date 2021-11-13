from . import actors
from . import mobs
from . import workers
from . import officers
from . import groups
from . import vehicles
from . import buildings

class actor_creation_manager_template(): #can get instance from anywhere and create actors with it without importing respective actor module
    def __init__(self):
        nothing = 0
        
    def create(self, from_save, input_dict, global_manager):
        init_type = input_dict['init_type']

        #mobs
        if init_type == 'mob':
            new_actor = mobs.mob(from_save, input_dict, global_manager)
        elif init_type == 'worker':
            new_actor = workers.worker(from_save, input_dict, global_manager)
        elif init_type == 'church_volunteers':
            new_actor = workers.church_volunteers(from_save, input_dict, global_manager)
        elif init_type == 'train':
            new_actor = vehicles.train(from_save, input_dict, global_manager)
        elif init_type == 'ship':
            new_actor = vehicles.ship(from_save, input_dict, global_manager)
        elif init_type in global_manager.get('officer_types'):
            if init_type == 'head_missionary':
                new_actor = officers.head_missionary(from_save, input_dict, global_manager)
            else:
                new_actor = officers.officer(from_save, input_dict, global_manager)
        elif init_type == 'porters':
            new_actor = groups.porters(from_save, input_dict, global_manager)
        elif init_type == 'construction_gang':
            new_actor = groups.construction_gang(from_save, input_dict, global_manager)
        elif init_type == 'caravan':
            new_actor = groups.caravan(from_save, input_dict, global_manager)
        elif init_type == 'missionaries':
            new_actor = groups.missionaries(from_save, input_dict, global_manager)
        elif init_type == 'expedition':
            new_actor = groups.expedition(from_save, input_dict, global_manager)

        #buildings
        elif init_type == 'infrastructure':
            new_actor = buildings.infrastructure_building(from_save, input_dict, global_manager)
        elif init_type == 'trading_post':
            new_actor = buildings.trading_post(from_save, input_dict, global_manager)
        elif init_type == 'mission':
            new_actor = buildings.mission(from_save, input_dict, global_manager)
        elif init_type == 'train_station':
            new_actor = buildings.train_station(from_save, input_dict, global_manager)
        elif init_type == 'port':
            new_actor = buildings.port(from_save, input_dict, global_manager)
        elif init_type == 'resource':
            new_actor = buildings.resource_building(from_save, input_dict, global_manager)
        return(new_actor)

    def create_group(self, worker, officer, global_manager): #use when merging groups. At beginning of game, instead of using this, create a group which creates its worker and officer and merges them
        '''
        Description:
            Creates a group out of the inputted worker and officer. The type of group formed depends on the officer's type. Upon joining a group, the component officer and worker will not be able to be seen or interacted with
                independently until the group is disbanded
        Input:
            worker worker: worker to create a group out of
            officer officer: officer to create a group out of
        Output:
            None
        '''
        input_dict = {}
        input_dict['coordinates'] = (officer.x, officer.y)
        input_dict['grids'] = officer.grids
        input_dict['worker'] = worker
        input_dict['officer'] = officer
        input_dict['modes'] = ['strategic', 'europe']
        input_dict['init_type'] = global_manager.get('officer_group_type_dict')[officer.officer_type]
        input_dict['image'] = 'mobs/' + officer.officer_type + '/' + input_dict['init_type'] + '.png' #mobs/merchant/caravan.png
        name = ''
        for character in input_dict['init_type']:
            if not character == '_':
                name += character
            else:
                name += ' '
        input_dict['name'] = name
        return(self.create(False, input_dict, global_manager))
        '''
        if officer.officer_type == 'explorer':
            input_dict['image'] = 'mobs/explorer/expedition.png'
            input_dict['name'] = 'expedition'
            new_group = expedition(False, input_dict, global_manager)
        elif officer.officer_type == 'engineer':
            input_dict['image'] = 'mobs/engineer/construction_gang.png'
            input_dict['name'] = 'construction gang'
            new_group = construction_gang(False, input_dict, global_manager)
        elif officer.officer_type == 'porter_foreman':
            input_dict['image'] = 'mobs/porter foreman/porters.png'
            input_dict['name'] = 'porters'
            new_group = porters(False, input_dict, global_manager)
        elif officer.officer_type == 'merchant':
            input_dict['image'] = 'mobs/merchant/caravan.png'
            input_dict['name'] = 'caravan'
            new_group = caravan(False, input_dict, global_manager)
        elif officer.officer_type == 'head_missionary':
            input_dict['image'] = 'mobs/head missionary/missionaries.png'
            input_dict['name'] = 'missionaries'
            new_group = missionaries(False, input_dict, global_manager)
        else:
            input_dict['image'] = 'mobs/default/default.png'
            input_dict['name'] = 'expedition'
            new_group = group(False, input_dict, global_manager)
        '''
