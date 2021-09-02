import pygame
from .actors import actor
from .buttons import button
from . import utility
from . import images
from . import actor_utility
from . import text_tools

class building(actor):
    '''
    Actor that exists in cells of multiple grids in front of tiles and behind mobs that can not be clicked
    '''
    def __init__(self, coordinates, grids, image_id, name, building_type, modes, global_manager):
        self.actor_type = 'building'
        self.building_type = building_type
        super().__init__(coordinates, grids, modes, global_manager)
        self.image_dict = {'default': image_id}
        self.images = []
        for current_grid in self.grids:
            self.images.append(images.building_image(self, current_grid.get_cell_width(), current_grid.get_cell_height(), current_grid, 'default',
                self.global_manager)) #self, actor, width, height, grid, image_description, global_manager
        global_manager.get('building_list').append(self)
        self.set_name(name)
        self.worker_capacity = 0 #default
        self.contained_workers = []
        for current_image in self.images:
            current_image.current_cell.contained_buildings[self.building_type] = self
            current_image.current_cell.tile.update_resource_icon()
        self.is_port = False #used to determine if port is in a tile to move there

    def remove(self):
        for current_image in self.images:
            current_image.current_cell.contained_buildings[self.building_type] = 'none'
            current_image.remove_from_cell()
            current_image.remove()
        super().remove()
        self.global_manager.set('building_list', utility.remove_from_list(self.global_manager.get('building_list'), self))

    def update_tooltip(self): #should be shown below mob tooltips
        tooltip_text = [self.name.capitalize()]
        if self.building_type == 'resource':
            tooltip_text.append("Worker capacity: " + str(len(self.contained_workers)) + '/' + str(self.worker_capacity))
            if len(self.contained_workers) == 0:
                tooltip_text.append("Workers: none")
            else:
                tooltip_text.append("Workers: ")
            for current_worker in self.contained_workers:
                tooltip_text.append("    " + current_worker.name)
            tooltip_text.append("Produces 1 unit of " + self.resource_type + " per attached worker per turn")
        elif self.building_type == 'port':
            tooltip_text.append("Allows ships to enter this tile")
        elif self.building_type == 'infrastructure':
            tooltip_text.append("Halves movement cost for units going to another tile with a road or railroad")
            if self.is_railroad:
                tooltip_text.append("Allows trains to move from this tile to other tiles that have railroads")
            else:
                tooltip_text.append("Can be upgraded to a railroad to allow trains to move through this tile")
        self.set_tooltip(tooltip_text)

    def touching_mouse(self):
        '''
        Input:
            none
        Output:
            Returns whether any of this building's images are colliding with the mouse
        '''
        for current_image in self.images:
            if current_image.change_with_other_images: #don't show tooltips for road connection images, only the base road building images
                if current_image.Rect.collidepoint(pygame.mouse.get_pos()): #if mouse is in image
                    if not (current_image.grid == self.global_manager.get('minimap_grid') and not current_image.grid.is_on_mini_grid(self.x, self.y)): #do not consider as touching mouse if off-map
                        return(True)
        return(False)

class infrastructure_building(building):
    def __init__(self, coordinates, grids, image_id, name, infrastructure_type, modes, global_manager):
        self.infrastructure_type = infrastructure_type
        if self.infrastructure_type == 'railroad':
            self.is_road = False
            self.is_railroad = True
        elif self.infrastructure_type == 'road':
            self.is_railroad = False
            self.is_road = True
        super().__init__(coordinates, grids, image_id, name, 'infrastructure', modes, global_manager)
        self.image_dict['left_road'] = 'buildings/infrastructure/left_road.png'
        self.image_dict['right_road'] = 'buildings/infrastructure/right_road.png'
        self.image_dict['down_road'] = 'buildings/infrastructure/down_road.png'
        self.image_dict['up_road'] = 'buildings/infrastructure/up_road.png'
        self.image_dict['left_railroad'] = 'buildings/infrastructure/left_railroad.png'
        self.image_dict['right_railroad'] = 'buildings/infrastructure/right_railroad.png'
        self.image_dict['down_railroad'] = 'buildings/infrastructure/down_railroad.png'
        self.image_dict['up_railroad'] = 'buildings/infrastructure/up_railroad.png'
        self.image_dict['empty'] = 'misc/empty.png'
        for current_grid in self.grids:
            self.images.append(images.infrastructure_connection_image(self, current_grid.get_cell_width(), current_grid.get_cell_height(), current_grid, 'default', 'up', self.global_manager))
            #actor, width, height, grid, image_description, direction, global_manager
            self.images.append(images.infrastructure_connection_image(self, current_grid.get_cell_width(), current_grid.get_cell_height(), current_grid, 'default', 'down', self.global_manager))
            self.images.append(images.infrastructure_connection_image(self, current_grid.get_cell_width(), current_grid.get_cell_height(), current_grid, 'default', 'right', self.global_manager))
            self.images.append(images.infrastructure_connection_image(self, current_grid.get_cell_width(), current_grid.get_cell_height(), current_grid, 'default', 'left', self.global_manager))
        actor_utility.update_roads(self.global_manager)

class port(building):
    def __init__(self, coordinates, grids, image_id, name, modes, global_manager):
        super().__init__(coordinates, grids, image_id, name, 'port', modes, global_manager)
        self.is_port = True #used to determine if port is in a tile to move there
        for current_image in self.images:
            current_image.current_cell.tile.inventory_capacity += 5

class resource_building(building):
    def __init__(self, coordinates, grids, image_id, name, resource_type, modes, global_manager):
        self.resource_type = resource_type
        super().__init__(coordinates, grids, image_id, name, 'resource', modes, global_manager)
        global_manager.get('resource_building_list').append(self)
        self.worker_capacity = 1 #improve with upgrades

    def remove(self):
        self.global_manager.set('resource_building_list', utility.remove_from_list(self.global_manager.get('resource_building_list'), self))
        super().remove()

    def produce(self):
        for current_worker in self.contained_workers:
            self.images[0].current_cell.tile.change_inventory(self.resource_type, 1)
