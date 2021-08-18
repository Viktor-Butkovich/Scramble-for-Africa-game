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

class construction_button(button):
    def __init__(self, coordinates, width, height, building_type, modes, global_manager):
        self.building_type = building_type
        self.attached_mob = 'none'
        self.attached_tile = 'none'
        self.building_name = 'none'
        if self.building_type == 'resource':
            self.attached_resource = 'none'
        super().__init__(coordinates, width, height, 'blue', 'construction', 'none', modes, 'misc/default_button.png', global_manager)#coordinates, width, height, color, button_type, keybind_id, modes, image_id, global_manager

    def update_info(self):
        selected_list = actor_utility.get_selected_list(self.global_manager)
        if len(selected_list) == 1:
            new_attached_mob = selected_list[0] #new_attached_mob.images[0].current_cell.tile == self.attached_tile
            #if not (new_attached_mob == self.attached_mob and new_attached_mob.x == self.attached_mob.x and new_attached_mob.y == self.attached_mob.y): #if selected mob changes or if tile changes, update building options
            self.attached_mob = new_attached_mob
            self.attached_tile = self.attached_mob.images[0].current_cell.tile
            if self.attached_mob.can_construct:
                if self.building_type == 'resource':
                    if self.attached_tile.cell.resource in self.global_manager.get('collectable_resources'):
                        self.attached_resource = self.attached_tile.cell.resource
                        self.image.set_image(self.global_manager.get('resource_building_button_dict')[self.attached_resource])
                        if self.attached_resource in ['gold', 'iron', 'copper', 'diamond']: #'coffee', 'copper', 'diamond', 'exotic wood', 'fruit', 'gold', 'iron', 'ivory', 'rubber'
                            self.building_name = self.attached_resource + ' mine'
                        elif self.attached_resource in ['exotic wood', 'fruit', 'rubber', 'coffee']:
                            self.building_name = self.attached_resource + ' plantation'
                        elif self.attached_resource == 'ivory':
                            self.building_name = 'ivory hunting area'
                    else:
                        self.attached_resource = 'none'
                        self.building_name = 'none'
                #self.image.set_image(self.attached_tile.image.image_id)
        else:
            self.image.set_image('misc/empty.png')
            self.attached_mob = 'none'
            self.attached_tile = 'none'
            if self.building_type == 'resource':
                self.attached_resource = 'none'

    def draw(self):
        self.update_info()
        super().draw()

    def can_show(self):
        if not (self.attached_mob == 'none' or self.attached_tile == 'none'):
            if self.attached_mob.can_construct:
                if self.building_type == 'resource':
                    if not self.attached_resource == 'none': #not self.attached_mob.images[0].current_cell.resource == 'none':
                        return(super().can_show())
                else:
                    return(super().can_show())
        return(False)

    def update_tooltip(self):
        if self.building_type == 'resource':
            self.set_tooltip(['Builds a ' + self.building_name + ' that produces ' + self.attached_resource + ' over time.'])
        else:
            self.set_tooltip(['placeholder'])

    def on_click(self):
        if self.can_show():
            self.showing_outline = True
            if self.attached_mob.movement_points >= 1:
                if self.building_type == 'resource':
                    if self.attached_tile.cell.contained_buildings[self.building_type] == 'none':
                        self.construct()
                    else:
                        text_tools.print_to_screen("This tile already contains a " + self.building_type + " building.", self.global_manager)
            else:
                text_tools.print_to_screen("You do not have enough movement points to construct a building.", self.global_manager)
                text_tools.print_to_screen("You have " + str(self.attached_mob.movement_points) + " movement points while 1 is required.", self.global_manager)

    def construct(self): #move stuff from on click here
        self.attached_mob.set_movement_points(0)
        if self.building_type == 'resource':
            new_building = resource_building((self.attached_mob.x, self.attached_mob.y), self.attached_mob.grids, self.global_manager.get('resource_building_dict')[self.attached_resource], self.building_name, self.attached_resource,
                ['strategic'], self.global_manager)#coordinates, grids, image_id, name, resource, modes, global_manager
        else:
            new_building = building((self.attached_mob.x, self.attached_mob.y), self.attached_mob.grids, self.global_manager.get('resource_building_dict')[self.attached_resource], self.building_name, self.building_type,
                ['strategic'], self.global_manager)#coordinates, grids, image_id, name, building_type, modes, global_manager
        actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), self.attached_mob.images[0].current_cell.tile)
    
class worker_to_building_button(button):
    def __init__(self, coordinates, width, height, building_type, modes, image_id, global_manager):
        self.building_type = building_type
        self.attached_worker = 'none'
        self.attached_building = 'none'
        self.building_type = building_type
        super().__init__(coordinates, width, height, 'blue', 'worker to resource', 'none', modes, image_id, global_manager)#coordinates, width, height, color, button_type, keybind_id, modes, image_id, global_manager

    def update_info(self):
        selected_list = actor_utility.get_selected_list(self.global_manager)
        if len(selected_list) == 1 and selected_list[0].is_worker:
            possible_attached_worker = selected_list[0]
            possible_attached_building = possible_attached_worker.images[0].current_cell.contained_buildings[self.building_type]
            if (not possible_attached_building == 'none'): #and building has capacity
                #attach to worker and building if worker selected and building of correct type present in same tile
                self.attached_worker = possible_attached_worker
                self.attached_building = possible_attached_building
            else:
                self.attached_worker = 'none'
                self.attached_building = 'none'
        else:
            self.attached_worker = 'none'
            self.attached_building = 'none'

    def draw(self):
        self.update_info()
        super().draw()

    def can_show(self):
        if not (self.attached_worker == 'none' or self.attached_building == 'none'):
            return(super().can_show())
        return(False)

    def update_tooltip(self): #make sure that attached building is not none
        if not (self.attached_worker == 'none' or self.attached_building == 'none'):
            if self.building_type == 'resource':
                self.set_tooltip(['Assigns the selected worker to the ' + self.attached_building.name + ', producing ' + self.attached_building.resource_type + ' over time.'])
            else:
                self.set_tooltip(['placeholder'])
        else:
            self.set_tooltip(['placeholder'])

    def on_click(self):
        if self.can_show():
            if self.attached_building.worker_capacity > len(self.attached_building.contained_workers): #if has extra space
                self.showing_outline = True
                self.attached_worker.work_building(self.attached_building)
            else:
                text_tools.print_to_screen("This building is at its worker capacity.", self.global_manager)
                text_tools.print_to_screen("Upgrade the building to add more worker capacity.", self.global_manager)
