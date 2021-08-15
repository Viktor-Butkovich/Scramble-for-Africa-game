import pygame
from .actors import actor
from . import utility
from . import images

class building(actor):
    '''
    Actor that exists in cells of multiple grids in front of tiles and behind mobs that can not be clicked
    '''
    def __init__(self, coordinates, grids, image_id, name, modes, global_manager):
        self.actor_type = 'building'
        super().__init__(coordinates, grids, modes, global_manager)
        self.image_dict = {'default': image_id}
        self.images = []
        for current_grid in self.grids:
            self.images.append(images.building_image(self, current_grid.get_cell_width(), current_grid.get_cell_height(), current_grid, 'default',
                self.global_manager)) #self, actor, width, height, grid, image_description, global_manager
            
        global_manager.get('building_list').append(self)
        self.set_name(name)

    def remove(self):
        for current_image in self.images:
            current_image.remove_from_cell()
        super().remove()
        self.global_manager.set('building_list', utility.remove_from_list(self.global_manager.get('building_list'), self))

    def update_tooltip(self): #should be shown below mob tooltips
        self.set_tooltip([self.name])

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
