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

    def remove(self):
        for current_image in self.images:
            current_image.current_cell.contained_buildings[self.building_type] = 'none'
            current_image.remove_from_cell()
        super().remove()
        self.global_manager.set('building_list', utility.remove_from_list(self.global_manager.get('building_list'), self))

    def update_tooltip(self): #should be shown below mob tooltips
        tooltip_text = [self.name.capitalize()]
        tooltip_text.append("Worker capacity: " + str(len(self.contained_workers)) + '/' + str(self.worker_capacity))
        if len(self.contained_workers) == 0:
            tooltip_text.append("Workers: none")
        else:
            tooltip_text.append("Workers: ")
        for current_worker in self.contained_workers:
            tooltip_text.append("    " + current_worker.name)
        self.set_tooltip(tooltip_text)

    def touching_mouse(self):
        '''
        Input:
            none
        Output:
            Returns whether any of this building's images are colliding with the mouse
        '''
        for current_image in self.images:
            if current_image.Rect.collidepoint(pygame.mouse.get_pos()): #if mouse is in image
                if not (current_image.grid == self.global_manager.get('minimap_grid') and not current_image.grid.is_on_mini_grid(self.x, self.y)): #do not consider as touching mouse if off-map
                    return(True)
        return(False)

class resource_building(building):
    def __init__(self, coordinates, grids, image_id, name, resource_type, modes, global_manager):
        super().__init__(coordinates, grids, image_id, name, 'resource', modes, global_manager)
        global_manager.get('resource_building_list').append(self)
        self.resource_type = resource_type
        self.worker_capacity = 1 #improve with upgrades

    def remove(self):
        self.global_manager.set('resource_building_list', utility.remove_from_list(self.global_manager.get('resource_building_list'), self))
        super().remove()

    def produce(self):
        for current_worker in self.contained_workers:
            self.images[0].current_cell.tile.change_inventory(self.resource_type, 1)
