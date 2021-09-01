import pygame

from .images import free_image
from .labels import label
from .buttons import button
from . import buildings
from . import main_loop_tools
from . import scaling
from . import actor_utility
from . import text_tools
from . import groups

class actor_match_free_image(free_image):
    '''
    Free image that changes its appearance to match selected mobs or tiles
    '''
    def __init__(self, coordinates, width, height, modes, actor_image_type, global_manager):
        '''
        Input:
            coordinates: tuple of two int variables representing the pixel location of this image
            width: int representing the pixel width of this image
            height: int representing the pixel height of this image
            modes: list of strings representing the game modes in which this image can appear
            actor_image_type: string representing the type of actor whose appearance will be copied by this image
            global_manager: global_manager_template object
        '''
        self.actor_image_type = actor_image_type
        self.actor = 'none'
        super().__init__('misc/empty.png', coordinates, width, height, modes, global_manager)

    def calibrate(self, new_actor):
        '''
        Input:
            new_actor: actor object or string representing the actor whose appearance will be copied by this image. If resetting to an empty image, new_actor will equal 'none'.
        Output:
            Sets this image to match the inputted actor or string. If the input is 'none', it will be reset to an empty image. Otherwise, it will use the default appearance of the inputted actor.
        '''
        self.actor = new_actor
        if not new_actor == 'none':
            if self.actor_image_type == 'resource':
                if new_actor.cell.visible:
                    if not new_actor.resource_icon == 'none':
                        self.set_image(new_actor.resource_icon.image_dict['default'])
                    else: #show nothing if no resource
                        self.set_image('misc/empty.png')
                else: #show nothing if cell not visible
                    self.set_image('misc/empty.png')
            elif self.actor_image_type == 'terrain' and not new_actor.cell.visible:
                self.set_image(new_actor.image_dict['hidden'])
            elif self.actor_image_type == 'resource building':
                if not new_actor.cell.contained_buildings['resource'] == 'none':
                    self.set_image(new_actor.cell.contained_buildings['resource'].image_dict['default']) #matches resource building
                else:
                    self.set_image('misc/empty.png')
            elif self.actor_image_type == 'port':
                if not new_actor.cell.contained_buildings['port'] == 'none':
                    self.set_image('buildings/port.png') #matches resource building
                else:
                    self.set_image('misc/empty.png')
            else:
                self.set_image(new_actor.image_dict['default'])
        else:
            self.set_image('misc/empty.png')

    def can_show(self):
        if self.actor == 'none':
            return(False)
        else:
            return(super().can_show())

class actor_match_background_image(free_image):
    def __init__(self, image_id, coordinates, width, height, modes, global_manager):
        super().__init__(image_id, coordinates, width, height, modes, global_manager)
        self.actor = 'none'
        #self.outline_Rect = pygame.Rect(self.x - 2, self.y - self.height - 2, self.width + 4, self.height + 4)

    def calibrate(self, new_actor):
        self.actor = new_actor

    def can_show(self):
        if self.actor == 'none':
            return(False)
        else:
            return(super().can_show())

    def update_tooltip(self):
        if not self.actor == 'none':
            tooltip_text = self.actor.tooltip_text
            self.set_tooltip(tooltip_text)
        else:
            super().update_tooltip()

class label_image(free_image):
    '''
    Free image that is attached to a label and will only show when the label is showing
    '''
    def __init__(self, coordinates, width, height, modes, attached_label, global_manager):
        '''
        Input:
            coordinates: tuple of two int variables representing the pixel location of this image
            width: int representing the pixel width of this image
            height: int representing the pixel height of this image
            modes: list of strings representing the game modes in which this image can appear
            attached_label: label object representing the label to which this image is attached.
            global_manager: global_manager_template object
        '''
        self.attached_label = attached_label
        super().__init__('misc/empty.png', coordinates, width, height, modes, global_manager)

    def can_show(self):
        '''
        Input:
            none
        Output:
            Controls whether this image should be shown. This image is shown only when its attached label is shown. 
        '''
        if self.attached_label.can_show():
            return(super().can_show())
        else:
            return(False)

class actor_match_label(label):
    '''
    Label that changes its text to match the information of selected mobs or tiles
    '''
    def __init__(self, coordinates, minimum_width, height, modes, image_id, actor_label_type, actor_type, global_manager):
        '''
        Input:
            coordinates: tuple of 2 integers for initial coordinate x and y values
            minimum_width: int representing the minimum width in pixels of the button. As the length of its message increases, the label's width will increase to accomodate it. 
            height: int representing the height in pixels of the button
            modes: list of strings representing the game modes in which this button is visible, such as 'strategic' for a button appearing when on the strategic map
            image_id: string representing the address of the button's image within the graphics folder such as 'misc/left_button.png' to represent SFA/graphics/misc/left_button.png
            actor_image_type: string representing the type of information of a selected mob or tile that will be shown
            global_manager: global_manager_template object
        '''
        message = ''#'default'
        self.attached_buttons = []
        self.actor = 'none'
        self.actor_label_type = actor_label_type #name, terrain, resource, etc
        self.actor_type = actor_type #mob or tile, none if does not scale with shown labels, like tooltip labels
        super().__init__(coordinates, minimum_width, height, modes, image_id, message, global_manager)
        if not self.actor_label_type in ['tooltip', 'commodity', 'mob inventory capacity', 'tile inventory capacity']: #except for certain types, all actor match labels should be in mob/tile_ordered_label_list
            if self.actor_type == 'mob':
                self.global_manager.get('mob_ordered_label_list').append(self)
            elif self.actor_type == 'tile':
                self.global_manager.get('tile_ordered_label_list').append(self)
        if self.actor_label_type == 'name':
            self.message_start = 'Name: '
            self.attached_buttons.append(merge_button((self.x, self.y), self.height, self.height, 'none', self.modes, 'misc/merge_button.png', self, global_manager))
            self.attached_buttons.append(split_button((self.x, self.y), self.height, self.height, 'none', self.modes, 'misc/split_button.png', self, global_manager))
            self.attached_buttons.append(embark_vehicle_button((self.x, self.y), self.height, self.height, 'none', self.modes, 'misc/embark_vehicle_button.png', self, global_manager))
            self.attached_buttons.append(worker_crew_vehicle_button((self.x, self.y), self.height, self.height, 'none', self.modes, 'misc/crew_vehicle_button.png', self, global_manager))
            self.attached_buttons.append(worker_to_building_button((self.x, self.y), self.height, self.height, 'none', 'resource', self.modes, 'misc/worker_to_building_button.png', self, global_manager))
            self.attached_buttons.append(switch_theatre_button((self.x, self.y), self.height, self.height, 'none', self.modes, 'misc/switch_theatre_button.png', self, global_manager))
            self.attached_buttons.append(construction_button((self.x, self.y), self.height, self.height, 'none', self.modes, self, 'resource', global_manager))
            self.attached_buttons.append(construction_button((self.x, self.y), self.height, self.height, 'none', self.modes, self, 'port', global_manager))
        elif self.actor_label_type == 'resource':
            self.message_start = 'Resource: '
        elif self.actor_label_type == 'terrain':
            self.message_start = 'Terrain: '
        elif self.actor_label_type == 'movement':
            self.message_start = 'Movement points: '
        elif self.actor_label_type == 'building worker':
            self.message_start = ''
            self.attached_building = 'none'
            self.attached_buttons.append(remove_worker_button((self.x, self.y), self.height, self.height, 'none', self.modes, 'misc/remove_worker_button.png', self, 'resource', global_manager))
        elif self.actor_label_type == 'crew':
            self.message_start = 'Crew: '
            self.attached_buttons.append(crew_vehicle_button((self.x, self.y), self.height, self.height, 'none', self.modes, 'misc/crew_vehicle_button.png', self, global_manager))
            self.attached_buttons.append(uncrew_vehicle_button((self.x, self.y), self.height, self.height, 'none', self.modes, 'misc/uncrew_vehicle_button.png', self, global_manager))
        elif self.actor_label_type == 'passengers':
            self.message_start = 'Passengers: '
            self.attached_buttons.append(cycle_passengers_button((self.x, self.y), self.height, self.height, 'none', self.modes, 'misc/cycle_passengers_down.png', self, global_manager))
        elif self.actor_label_type == 'current passenger':
            self.message_start = ''
            self.attached_buttons.append(disembark_vehicle_button((self.x, self.y), self.height, self.height, 'none', self.modes, 'misc/disembark_vehicle_button.png', self, global_manager))
        elif self.actor_label_type == 'tooltip':
            self.message_start = ''
        elif self.actor_label_type == 'native aggressiveness':
            self.message_start = 'Aggressiveness: '
        elif self.actor_label_type == 'native population':
            self.message_start = 'Total population: '
        elif self.actor_label_type == 'native available workers':
            self.message_start = 'Available workers: '
        elif self.actor_label_type in ['mob inventory capacity', 'tile inventory capacity']:
            self.message_start = 'Inventory: '
        else:
            self.message_start = 'none'
        self.calibrate('none')

    def update_tooltip(self):
        if self.actor_label_type in ['building worker', 'current passenger']:
            if len(self.attached_list) > self.list_index:
                self.attached_list[self.list_index].update_tooltip()
                tooltip_text = self.attached_list[self.list_index].tooltip_text
                self.set_tooltip(tooltip_text)
            else:
                super().update_tooltip()
        elif self.actor_label_type == 'passengers':
            if (not self.actor == 'none'):
                if self.actor.has_crew:
                    name_list = [self.message_start]
                    for current_passenger in self.actor.contained_mobs:
                        name_list.append("    " + current_passenger.name)
                    if len(name_list) == 1:
                        name_list[0] = self.message_start + ' none'
                    self.set_tooltip(name_list)
                else:
                    super().update_tooltip()
        elif self.actor_label_type == 'crew':
            if (not self.actor == 'none') and self.actor.has_crew:
                self.actor.crew.update_tooltip()
                tooltip_text = self.actor.crew.tooltip_text
                self.set_tooltip(tooltip_text)
            else:
                super().update_tooltip()
        elif self.actor_label_type == 'tooltip':
            if not self.actor == 'none':
                self.actor.update_tooltip()
                tooltip_text = self.actor.tooltip_text
                self.set_tooltip(tooltip_text)
        elif self.actor_label_type in ['native aggressiveness', 'native population', 'native available workers']:
            tooltip_text = [self.message]
            if self.actor_label_type == 'native aggressiveness':
                tooltip_text.append('Corresponds to the chance that the people of this village will attack nearby company units')
            elif self.actor_label_type == 'native population':
                tooltip_text.append('The total population of this village, which grows over time unless attacked or if willing villagers leave to become company workers')
            elif self.actor_label_type == 'native available workers':
                tooltip_text.append("The portion of this village's population that would be willing to work for your company")
            self.set_tooltip(tooltip_text)
        elif self.actor_label_type in ['mob inventory capacity', 'tile inventory capacity']:
            tooltip_text = [self.message]
            if self.actor_label_type == 'mob inventory capacity':
                if not self.actor == 'none':
                    tooltip_text.append("This unit is currently holding " + str(self.actor.get_inventory_used()) + " commodities")
                    tooltip_text.append("This unit can hold a maximum of " + str(self.actor.inventory_capacity) + " commodities.")
            elif self.actor_label_type == 'tile inventory capacity':
                if not self.actor == 'none':
                    if self.actor.can_hold_infinite_commodities:
                        tooltip_text.append("This tile can hold infinite commodities.")
                    else:
                        tooltip_text.append("This tile currently contains " + str(self.actor.get_inventory_used()) + " commodities")
                        tooltip_text.append("This tile can retain a maximum of " + str(self.actor.inventory_capacity) + " commodities.")
                        tooltip_text.append("If this tile is holding commodities exceeding its capacity before resource production at the end of the turn, extra commodities will be lost.")
            self.set_tooltip(tooltip_text)
        else:
            super().update_tooltip()

    def calibrate(self, new_actor):
        '''
        Input:
            new_actor: actor object or string representing the actor whose information will be shown by this label. If resetting to a default message, new_actor will equal 'none'.
        Output:
            Sets this label's text to match the information of the inputted actor or string. If the input is 'none', it will be reset to a default message. Otherwise, it will show the information of the inputted actor.
        '''
        self.actor = new_actor
        if not new_actor == 'none':
            if self.actor_label_type == 'name':
                self.set_label(self.message_start + str(new_actor.name))
            elif self.actor_label_type == 'terrain':
                if new_actor.grid.is_abstract_grid:
                    self.set_label('Europe')
                elif self.actor.cell.visible:
                    self.set_label(self.message_start + str(new_actor.cell.terrain))
                else:
                    self.set_label(self.message_start + 'unknown')
            elif self.actor_label_type == 'resource':
                if new_actor.grid.is_abstract_grid:
                    self.set_label(self.message_start + 'n/a')
                elif new_actor.cell.visible:
                    if (not new_actor.cell.village == 'none') and new_actor.cell.visible:
                        self.set_label('Village name: ' + new_actor.cell.village.name)
                    elif new_actor.cell.contained_buildings[self.actor_label_type] == 'none': #if no building built, show resource: name
                        self.set_label(self.message_start + new_actor.cell.resource)
                    else:
                        self.set_label('Resource building: ' + new_actor.cell.contained_buildings[self.actor_label_type].name) #if resource building built, show it
                else:
                    self.set_label(self.message_start + 'unknown')
            elif self.actor_label_type == 'movement':
                self.set_label(self.message_start + str(new_actor.movement_points) + '/' + str(new_actor.max_movement_points))
            elif self.actor_label_type == 'building worker':
                if self.list_type == 'resource building':
                    if not new_actor.cell.contained_buildings['resource'] == 'none':
                        self.attached_building = new_actor.cell.contained_buildings['resource']
                        self.attached_list = self.attached_building.contained_workers
                        if len(self.attached_list) > self.list_index:
                            self.set_label(self.message_start + self.attached_list[self.list_index].name)
                    else:
                        self.attached_building = 'none'
                        self.attached_list = []
            elif self.actor_label_type == 'crew':
                if self.actor.is_vehicle:
                    if self.actor.has_crew:
                        self.set_label(self.message_start + self.actor.crew.name)
                    else:
                        self.set_label(self.message_start + 'none')
            elif self.actor_label_type == 'passengers':
                if self.actor.is_vehicle:
                    if not self.actor.has_crew:
                        self.set_label("A ship requires crew to function")
                    else:
                        if len(self.actor.contained_mobs) == 0:
                            self.set_label(self.message_start + 'none')
                        else:
                            self.set_label(self.message_start)
            elif self.actor_label_type == 'current passenger':
                if self.actor.is_vehicle:
                    if len(self.actor.contained_mobs) > 0:
                        self.attached_list = new_actor.contained_mobs
                        if len(self.attached_list) > self.list_index:
                            self.set_label(self.message_start + self.attached_list[self.list_index].name)
            elif self.actor_label_type in ['native aggressiveness', 'native population', 'native available workers']:
                if (not self.actor.cell.village == 'none') and self.actor.cell.visible: #if village present
                    if self.actor_label_type == 'native aggressiveness':
                        self.set_label(self.message_start + str(self.actor.cell.village.aggressiveness))
                    elif self.actor_label_type == 'native population':
                        self.set_label(self.message_start + str(self.actor.cell.village.population))
                    elif self.actor_label_type == 'native available workers':
                        self.set_label(self.message_start + str(self.actor.cell.village.available_workers))
            elif self.actor_label_type in ['mob inventory capacity', 'tile inventory capacity']:
                if self.actor.can_hold_infinite_commodities:
                    self.set_label(self.message_start + 'unlimited')
                else:
                    self.set_label(self.message_start + str(self.actor.get_inventory_used()) + '/' + str(self.actor.inventory_capacity))
        elif self.actor_label_type == 'tooltip':
            nothing = 0 #do not set text for tooltip label
        else:
            self.set_label(self.message_start + 'n/a')

    def set_label(self, new_message):
        super().set_label(new_message)
        x_displacement = 0
        for current_button_index in range(len(self.attached_buttons)):
            current_button = self.attached_buttons[current_button_index]
            if current_button.can_show():
                current_button.x = self.x + self.width + 5 + x_displacement
                current_button.Rect.x = current_button.x
                current_button.outline.x = current_button.x - current_button.outline_width
                x_displacement += (current_button.width + 5)

    def set_y(self, new_y):
        self.y = new_y
        self.image.y = self.y
        #self.Rect.y = self.y
        self.image.Rect = self.Rect    
        for current_button in self.attached_buttons:
            current_button.y = self.y
            current_button.Rect.y = self.global_manager.get('display_height') - (current_button.y + current_button.height)
            current_button.outline.y = current_button.Rect.y - current_button.outline_width

    def can_show(self):
        result = super().can_show()
        if self.actor == 'none':
            return(False)
        elif self.actor_label_type == 'tile inventory capacity' and not self.actor.cell.visible:
            return(False)
        elif self.actor_label_type == 'resource' and self.actor.grid.is_abstract_grid:
            return(False)
        elif self.actor_label_type in ['crew', 'passengers'] and not self.actor.is_vehicle:
            return(False)
        elif self.actor.actor_type == 'mob' and (self.actor.in_vehicle or self.actor.in_group or self.actor.in_building):
            return(False)
        else:
            return(result)

class list_item_label(actor_match_label): #attached to a certain list based on list type, has index of list that it shows
    def __init__(self, coordinates, minimum_width, height, modes, image_id, actor_label_type, list_index, list_type, actor_type, global_manager):
        self.list_index = list_index
        self.list_type = list_type
        self.attached_list = []
        super().__init__(coordinates, minimum_width, height, modes, image_id, actor_label_type, actor_type, global_manager)

    def calibrate(self, new_actor):
        self.attached_list = []
        super().calibrate(new_actor)

    def can_show(self):
        if len(self.attached_list) > self.list_index:
            return(super().can_show())
        return(False)

class building_workers_label(actor_match_label):
    def __init__(self, coordinates, minimum_width, height, modes, image_id, building_type, actor_type, global_manager):
        self.remove_worker_button = 'none'
        super().__init__(coordinates, minimum_width, height, modes, image_id, 'building workers', actor_type, global_manager)
        self.building_type = building_type
        self.attached_building = 'none'
        self.showing = False

    def calibrate(self, new_actor):
        self.actor = new_actor
        self.showing = False
        if not new_actor == 'none':
            self.attached_building = new_actor.cell.contained_buildings[self.building_type]
            if not self.attached_building == 'none':
                self.set_label("Workers: " + str(len(self.attached_building.contained_workers)) + '/' + str(self.attached_building.worker_capacity))
                self.showing = True

    def can_show(self):
        if self.showing:
            return(super().can_show())
        else:
            return(False)

class native_info_label(actor_match_label): #possible actor_label_types: native aggressiveness, native population, native available workers
    def __init__(self, coordinates, minimum_width, height, modes, image_id, actor_label_type, actor_type, global_manager):
        super().__init__(coordinates, minimum_width, height, modes, image_id, actor_label_type, actor_type, global_manager)

    def can_show(self):
        result = super().can_show()
        if result:
            if (not self.actor.cell.village == 'none') and self.actor.cell.visible: #only show if village present and discovered
                return(True)
        return(False)
        

class commodity_match_label(actor_match_label):
    '''
    Label that changes its text and attached image and button to match the commodity in a certain part of a currently selected actor's inventory    
    '''
    def __init__(self, coordinates, minimum_width, height, modes, image_id, commodity_index, matched_actor_type, global_manager):
        '''
        Input:
            coordinates: tuple of 2 integers for initial coordinate x and y values
            minimum_width: int representing the minimum width in pixels of the button. As the length of its message increases, the label's width will increase to accomodate it. 
            height: int representing the height in pixels of the button
            modes: list of strings representing the game modes in which this button is visible, such as 'strategic' for a button appearing when on the strategic map
            image_id: string representing the address of the button's image within the graphics folder such as 'misc/left_button.png' to represent SFA/graphics/misc/left_button.png
            commodity_index: int representing the part of an actor's inventory shown by this label. A commodity index of 0 would cause this label to match the first item in a selected actor's inventory.
            matched_actor_type: string representing whether this label should match selected mobs or tiles
            global_manager: global_manager_template object
        '''
        #self.actor = 'none'
        self.current_commodity = 'none'
        super().__init__(coordinates, minimum_width, height, modes, image_id, 'commodity', matched_actor_type, global_manager)
        self.showing_commodity = False
        self.commodity_index = commodity_index
        self.commodity_image = label_image((self.x - self.height, self.y), self.height, self.height, self.modes, self, self.global_manager) #self, coordinates, width, height, modes, attached_label, global_manager
        #self.attached_buttons = []
        if matched_actor_type == 'mob':
            self.attached_buttons.append(label_button((self.x, self.y), self.height, self.height, 'drop commodity', 'none', self.modes, 'misc/commodity_drop_button.png', self, global_manager))
            self.attached_buttons.append(label_button((self.x + (self.height + 5), self.y), self.height, self.height, 'drop all commodity', 'none', self.modes, 'misc/commodity_drop_all_button.png', self, global_manager))
        elif matched_actor_type == 'tile':
            self.attached_buttons.append(label_button((self.x, self.y), self.height, self.height, 'pick up commodity', 'none', self.modes, 'misc/commodity_pick_up_button.png', self, global_manager))
            self.attached_buttons.append(label_button((self.x + (self.height + 5), self.y), self.height, self.height, 'pick up all commodity', 'none', self.modes, 'misc/commodity_pick_up_all_button.png', self, global_manager))
            self.attached_buttons.append(label_button((self.x + ((self.height + 5) * 2), self.y), self.height, self.height, 'sell commodity', 'none', ['europe'], 'misc/commodity_sell_button.png', self, global_manager))
            self.attached_buttons.append(label_button((self.x + ((self.height + 5) * 3), self.y), self.height, self.height, 'sell all commodity', 'none', ['europe'], 'misc/commodity_sell_all_button.png', self, global_manager))

    def set_label(self, new_message):
        super().set_label(new_message)
        if not self.actor == 'none': #self.setup_complete: #if not new_message == 'n/a':
            commodity_list = self.actor.get_held_commodities()
            if len(commodity_list) > self.commodity_index:
                commodity = commodity_list[self.commodity_index]
                self.commodity_image.set_image('scenery/resources/' + commodity + '.png')
            

    def calibrate(self, new_actor):
        '''
        Input:
            new_actor: actor object or string representing the actor whose inventory will be shown by this label.
        Output:
            Sets this label's text, image, and button to match a certain index of new_actor's inventory. If new_actor is 'none', the label and its attached image and button will not be shown.
        '''
        self.actor = new_actor
        if not new_actor == 'none':
            commodity_list = new_actor.get_held_commodities()
            if len(commodity_list) - 1 >= self.commodity_index: #if index in commodity list
                self.showing_commodity = True
                commodity = commodity_list[self.commodity_index]
                self.current_commodity = commodity
                self.set_label(commodity + ': ' + str(new_actor.get_inventory(commodity))) #format - commodity_name: how_many
            else:
                self.showing_commodity = False
                self.set_label('n/a')
        else:
            self.showing_commodity = False
            self.set_label('n/a')

    def can_show(self):
        '''
        Input:
            none
        Output:
            Controls whether this label should be shown. This button is shown only when it is calibrated to an actor with an inventory size that includes this label's commodity index.
        '''
        if not self.showing_commodity:
            return(False)
        else:
            return(super().can_show())

class label_button(button):
    '''
    Button that is attached to a label, has have behavior related to the label, will only show when the label is showing
    '''
    def __init__(self, coordinates, width, height, button_type, keybind_id, modes, image_id, attached_label, global_manager):
        '''
        Input:
            coordinates: tuple of 2 integers for initial coordinate x and y values
            width: int representing the width in pixels of the button
            height: int representing the height in pixels of the button
            button_type: string representing a subtype of button, such as a 'move up' button, determining its tooltip and behavior
            modes: list of strings representing the game modes in which this button is visible, such as 'strategic' for a button appearing when on the strategic map
            image_id: string representing the address of the button's image within the graphics folder such as 'misc/left_button.png' to represent SFA/graphics/misc/left_button.png
            attached_label: label object representing the label to which this button is attached.
            global_manager: global_manager_template object used to manage a dictionary of shared variables
        '''
        self.attached_label = attached_label
        super().__init__(coordinates, width, height, 'blue', button_type, keybind_id, modes, image_id, global_manager)#coordinates, width, height, color, button_type, keybind_id, modes, image_id, global_manager

    def can_show(self):
        '''
        Input:
            none
        Output:
            Controls whether this button should be shown. This button is shown only when its attached label is shown. 
        '''
        if self.attached_label.can_show():
            if not ((self.button_type == 'sell commodity' or self.button_type == 'sell all commodity') and self.attached_label.current_commodity == 'consumer goods'):
                return(super().can_show())
        return(False)


class worker_crew_vehicle_button(label_button): #appears on worker, finds ship to attach as crew
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, global_manager):
        super().__init__(coordinates, width, height, 'worker to crew', keybind_id, modes, image_id, attached_label, global_manager)

    def on_click(self):
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):    
                selected_list = actor_utility.get_selected_list(self.global_manager)
                vehicle = self.attached_label.actor.images[0].current_cell.get_uncrewed_vehicle()
                crew = self.attached_label.actor
                if (not (vehicle == 'none' or crew == 'none')) and (not vehicle.has_crew): #if vehicle and rider selected
                    if vehicle.x == crew.x and vehicle.y == crew.y: #ensure that this doesn't work across grids
                        crew.crew_vehicle(vehicle)
                    else:
                        text_tools.print_to_screen("You must select a worker in the same tile as an uncrewed ship to crew the ship.", self.global_manager)
                else:
                    text_tools.print_to_screen("You must select a worker in the same tile as an uncrewed ship to crew the ship.", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not crew a vehicle.", self.global_manager)

    def can_show(self):
        result = super().can_show()
        if result:
            if (not self.attached_label.actor.is_worker) or (not self.attached_label.actor.images[0].current_cell.has_uncrewed_vehicle()):
                return(False)
        return(result)

class crew_vehicle_button(label_button): #appears on ship, finds worker to attach as crew
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, global_manager):
        super().__init__(coordinates, width, height, 'crew', keybind_id, modes, image_id, attached_label, global_manager)

    def on_click(self):
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):    
                vehicle = self.attached_label.actor
                crew = 'none'
                for contained_mob in vehicle.images[0].current_cell.contained_mobs:
                    if contained_mob.is_worker:
                        crew = contained_mob
                if (not (vehicle == 'none' or crew == 'none')) and (not vehicle.has_crew): #if vehicle and rider selected
                    if vehicle.x == crew.x and vehicle.y == crew.y: #ensure that this doesn't work across grids
                        crew.crew_vehicle(vehicle)
                    else:
                        text_tools.print_to_screen("You must select an uncrewed ship in the same tile as a worker to crew the ship.", self.global_manager)
                else:
                    text_tools.print_to_screen("You must select an uncrewed ship in the same tile as a worker to crew the ship.", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not crew a ship.", self.global_manager)

    def can_show(self):
        result = super().can_show()
        if result:
            if self.attached_label.actor.has_crew:
                return(False)
        return(result)

class uncrew_vehicle_button(label_button): #later only allow uncrewing in a port
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, global_manager):
        super().__init__(coordinates, width, height, 'uncrew', keybind_id, modes, image_id, attached_label, global_manager)
        
    def can_show(self):
        result = super().can_show()
        if result:
            if not self.attached_label.actor.has_crew:
                return(False)
        return(result)

    def on_click(self):
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):
                vehicle = self.attached_label.actor
                crew = vehicle.crew
                if len(vehicle.contained_mobs) == 0 and len(vehicle.get_held_commodities()) == 0:
                    crew.uncrew_vehicle(vehicle)
                else:
                    text_tools.print_to_screen("You can not remove the crew from a ship with passengers or cargo.", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not remove a ship's crew.", self.global_manager)

class merge_button(label_button):
    '''
    Button that, when pressed, merges a selected officer with a worker in the same tile
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, global_manager):
        super().__init__(coordinates, width, height, 'merge', keybind_id, modes, image_id, attached_label, global_manager)
        
    def can_show(self):
        result = super().can_show()
        if result:
            if not self.attached_label.actor.is_officer:
                return(False)
        return(result)

    def on_click(self):
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):    
                selected_list = actor_utility.get_selected_list(self.global_manager)
                if len(selected_list) == 1:
                    officer = 'none'
                    worker = 'none'
                    for current_selected in selected_list:
                        if current_selected in self.global_manager.get('officer_list'):
                            officer = current_selected
                            worker = officer.images[0].current_cell.get_worker()
                    if not (officer == 'none' or worker == 'none'): #if worker and officer selected
                        if officer.x == worker.x and officer.y == worker.y:
                            groups.create_group(officer.images[0].current_cell.get_worker(), officer, self.global_manager)
                        else:
                            text_tools.print_to_screen("You must select an officer in the same tile as a worker to create a group.", self.global_manager)
                    else:
                        text_tools.print_to_screen("You must select an officer in the same tile as a worker to create a group.", self.global_manager)
                else:
                    text_tools.print_to_screen("You must select an officer in the same tile as a worker to create a group.", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not form a group.", self.global_manager)


class split_button(label_button):
    '''
    Button that, when pressed, splits a selected group into its officer and worker
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, global_manager):
        super().__init__(coordinates, width, height, 'split', keybind_id, modes, image_id, attached_label, global_manager)
        
    def can_show(self):
        result = super().can_show()
        if result:
            if not self.attached_label.actor.is_group:
                return(False)
        return(result)

    def on_click(self):
        '''
        Input:
            none
        Output:
            Controls the button's behavior when clicked. The merge button requires that only a group is selected, and will cause the selected group to split into its officer and worker, destroying the group.
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):         
                displayed_mob = self.global_manager.get('displayed_mob')#selected_list = actor_utility.get_selected_list(self.global_manager)
                if (not displayed_mob == 'none') and displayed_mob.is_group:
                    if not (displayed_mob.can_hold_commodities and len(displayed_mob.get_held_commodities()) > 0): #do not disband if trying to disband a porter who is carrying commodities
                        displayed_mob.disband()
                    else:
                        text_tools.print_to_screen("You can not split a group of porters that is carrying commodities.", self.global_manager)
                else:
                    text_tools.print_to_screen("Only a group can be split it into a worker and an officer.", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not split a group.", self.global_manager)

class remove_worker_button(label_button):
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, building_type, global_manager):
        super().__init__(coordinates, width, height, 'remove worker', keybind_id, modes, image_id, attached_label, global_manager)
        self.building_type = building_type
        
    def can_show(self):
        result = super().can_show()
        if result:
            if not self.attached_label.attached_list[self.attached_label.list_index].in_building:
                return(False)
        return(result)

    def on_click(self):
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):         
                #if len(self.attached_label.actor.cell.contained_mobs) > 0:
                self.attached_label.attached_list[self.attached_label.list_index].leave_building(self.attached_label.actor.cell.contained_buildings[self.building_type])
                #else:
                #    text_tools.print_to_screen("You must select a building with workers to remove workers.", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not remove a worker from a building.", self.global_manager)

class disembark_vehicle_button(label_button):
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, global_manager):
        super().__init__(coordinates, width, height, 'disembark', keybind_id, modes, image_id, attached_label, global_manager)
        
    def can_show(self):
        result = super().can_show()
        if result:
            if not self.attached_label.attached_list[self.attached_label.list_index].in_vehicle:
                return(False)
        return(result)

    def on_click(self):
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):         
                if len(self.attached_label.actor.contained_mobs) > 0:
                    self.attached_label.attached_list[self.attached_label.list_index].disembark_vehicle(self.attached_label.actor)
                    #label is attached to ship and has an attached list of its passengers - tells passenger of index to disembark ship
                else:
                    text_tools.print_to_screen("You must select a ship with passengers to disembark passengers.", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not disembark from a ship.", self.global_manager)

class embark_vehicle_button(label_button):
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, global_manager):
        super().__init__(coordinates, width, height, 'embark', keybind_id, modes, image_id, attached_label, global_manager)
        
    def can_show(self):
        result = super().can_show()
        if result:
            if self.attached_label.actor.in_vehicle or self.attached_label.actor.is_vehicle:
                return(False)
        return(result)
    
    def on_click(self):
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):
                if self.attached_label.actor.images[0].current_cell.has_vehicle():
                    selected_list = actor_utility.get_selected_list(self.global_manager)
                    num_vehicles = 0
                    vehicle = self.attached_label.actor.images[0].current_cell.get_vehicle()
                    rider = self.attached_label.actor
                    rider.embark_vehicle(vehicle)
                else:
                    text_tools.print_to_screen("You must select a unit in the same tile as a crewed ship to embark.", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not embark a ship.", self.global_manager)

class cycle_passengers_button(label_button):
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, global_manager):
        super().__init__(coordinates, width, height, 'cycle passengers', keybind_id, modes, image_id, attached_label, global_manager)
        
    def can_show(self):
        result = super().can_show()
        if result:
            if not self.attached_label.actor.is_vehicle:
                return(False)
            elif not len(self.attached_label.actor.contained_mobs) > 3: #only show if vehicle with 3+ passengers
                return(False)
        return(result)
    
    def on_click(self):
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):
                moved_mob = self.attached_label.actor.contained_mobs.pop(0)
                self.attached_label.actor.contained_mobs.append(moved_mob)
                actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self.attached_label.actor) #updates mob info display list to show changed passenger order
            else:
                text_tools.print_to_screen("You are busy and can not cycle passengers.", self.global_manager)

class worker_to_building_button(label_button):
    def __init__(self, coordinates, width, height, keybind_id, building_type, modes, image_id, attached_label, global_manager):
        self.building_type = building_type
        self.attached_worker = 'none'
        self.attached_building = 'none'
        self.building_type = building_type
        super().__init__(coordinates, width, height, 'worker to resource', keybind_id, modes, image_id, attached_label, global_manager)#coordinates, width, height, color, button_type, keybind_id, modes, image_id, global_manager

    def update_info(self):
        self.attached_worker = self.attached_label.actor #selected_list[0]
        if (not self.attached_worker == 'none') and self.attached_worker.is_worker:
            possible_attached_building = self.attached_worker.images[0].current_cell.contained_buildings[self.building_type]
            if (not possible_attached_building == 'none'): #and building has capacity
                #attach to building if building of correct type present in same tile
                self.attached_building = possible_attached_building
            else:
                self.attached_building = 'none'
        else:
            self.attached_building = 'none'
        
    def draw(self):
        #self.update_info()
        super().draw()
    
    def can_show(self):
        result = super().can_show()
        self.update_info()
        if result:
            if (not self.attached_worker == 'none') and not (self.attached_worker.is_worker): #if selected but not worker, return false
                return(False)
        return(result)
    
    def update_tooltip(self): #make sure that attached building is not none
        if not (self.attached_worker == 'none' or self.attached_building == 'none'):
            if self.building_type == 'resource':
                self.set_tooltip(['Assigns the selected worker to the ' + self.attached_building.name + ', producing ' + self.attached_building.resource_type + ' over time.'])
            else:
                self.set_tooltip(['placeholder'])
        elif not self.attached_worker == 'none':
            if self.building_type == 'resource':
                self.set_tooltip(['Assigns the selected worker to a resource building, producing resources over time.'])
        else:
            self.set_tooltip(['placeholder'])

    def on_click(self):
        if self.can_show():
            if not self.attached_building == 'none':
                if self.attached_building.worker_capacity > len(self.attached_building.contained_workers): #if has extra space
                    self.showing_outline = True
                    self.attached_worker.work_building(self.attached_building)
                else:
                    text_tools.print_to_screen("This building is at its worker capacity.", self.global_manager)
                    text_tools.print_to_screen("Upgrade the building to add more worker capacity.", self.global_manager)
            else:
                text_tools.print_to_screen("This worker must be in the same tile as a resource production building to work in it", self.global_manager)

class switch_theatre_button(label_button):
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, global_manager):
        super().__init__(coordinates, width, height, 'switch theatre', keybind_id, modes, image_id, attached_label, global_manager)

    def on_click(self):      
        '''
        Input:
            none
        Output:
            Controls the button's behavior when left clicked. Grid switching buttons require one mob to be selected and outside of this button's destination grid to be used, and move the selected mob to the destination grid when used.
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):
                current_mob = self.attached_label.actor
                if current_mob.movement_points == current_mob.max_movement_points:
                    if not (self.global_manager.get('strategic_map_grid') in current_mob.grids and (current_mob.y > 1 or (current_mob.y == 1 and not current_mob.images[0].current_cell.has_port()))): #can leave if in ocean or if in coastal port
                        if current_mob.can_leave(): #not current_mob.grids[0] in self.destination_grids and
                            if self.global_manager.get('current_game_mode') == 'strategic':
                                current_mob.end_turn_destination = 'none'
                                self.global_manager.set('choosing_destination', True)
                                self.global_manager.set('choosing_destination_info_dict', {'chooser': current_mob}) #, 'destination_grids': self.destination_grids
                            else:
                                text_tools.print_to_screen("You can not switch theatres from the European HQ screen.", self.global_manager)
                    else:
                        text_tools.print_to_screen("You are inland and can not cross the ocean.", self.global_manager) 
                else:
                    text_tools.print_to_screen("Crossing the ocean requires an entire turn of movement points.", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not move.", self.global_manager)

    def can_show(self):
        '''
        Input:
            none
        Output:
            Returns whether the button can currently be shown. A grid switching button is only shown when there is one mob selected and that mob is not on this button's destination grid.
        '''
        result = super().can_show()
        if result:
            if (not self.attached_label.actor.travel_possible): #if selected but not worker, return false
                return(False)
        return(result) 

class construction_button(label_button): #coordinates, width, height, keybind_id, modes, image_id, attached_label, global_manager
    def __init__(self, coordinates, width, height, keybind_id, modes, attached_label, building_type, global_manager):
        self.building_type = building_type
        self.attached_mob = 'none'
        self.attached_tile = 'none'
        self.building_name = 'none'
        image_id = 'misc/default_button.png'
        if self.building_type == 'resource':
            self.attached_resource = 'none'
            image_id = global_manager.get('resource_building_button_dict')['none']
        elif self.building_type == 'port':
            image_id = 'buildings/buttons/port.png'
            self.building_name = 'port'
        super().__init__(coordinates, width, height, 'construction', keybind_id, modes, image_id, attached_label, global_manager)#coordinates, width, height, color, button_type, keybind_id, modes, image_id, global_manager
    def update_info(self):
        self.attached_mob = self.attached_label.actor #new_attached_mob
        if (not self.attached_mob == 'none') and (not self.attached_mob.images[0].current_cell == 'none'):
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
                            self.building_name = 'ivory camp'
                    else:
                        self.attached_resource = 'none'
                        self.building_name = 'none'
                        self.image.set_image(self.global_manager.get('resource_building_button_dict')['none'])
                #elif self.building_type == 'port': #port info never changes
                #    self.building_name = 'port'
                #    self.image.set_image('misc/

    def can_show(self):
        result = super().can_show()
        if result:
            self.update_info()
            if (not self.attached_label.actor.can_construct): #if selected but not worker, return false
                return(False)
        return(result) 

    def update_tooltip(self):
        if self.building_type == 'resource':
            if self.attached_resource == 'none':
                self.set_tooltip(['Builds a building that produces commodities over time.', 'Requires that this unit is in the same tile as a resource', 'Costs 1 movement point'])
            else:
                self.set_tooltip(['Builds a ' + self.building_name + ' that produces ' + self.attached_resource + ' over time.', 'Costs 1 movement point'])
        elif self.building_type == 'port':
            self.set_tooltip(['Builds a port, allowing ships to land in this tile.', 'Requires that this unit is adjacent to a water tile.', 'Costs 1 movement point'])
        else:
            self.set_tooltip(['placeholder'])

    def on_click(self):
        if self.can_show():
            self.showing_outline = True
            if self.attached_mob.movement_points >= 1:
                if self.attached_tile.cell.contained_buildings[self.building_type] == 'none':
                    if not self.global_manager.get('europe_grid') in self.attached_mob.grids:
                        if self.building_type == 'resource':
                            if not self.attached_resource == 'none':
                                self.construct()
                            else:
                                text_tools.print_to_screen("This building can only be built in tiles with resources.", self.global_manager)
                        elif self.building_type == 'port':
                            if self.attached_mob.adjacent_to_water():
                                if not self.attached_mob.images[0].current_cell.terrain == 'water':
                                    self.construct()
                                    text_tools.print_to_screen("This building can not be built on water.", self.global_manager)
                            else:
                                text_tools.print_to_screen("This building can only be built in tiles adjacent to water.", self.global_manager)
                    else:
                        text_tools.print_to_screen("This building can not be built in Europe.", self.global_manager)
                else:
                    text_tools.print_to_screen("This tile already contains a " + self.building_type + " building.", self.global_manager)
            else:
                text_tools.print_to_screen("You do not have enough movement points to construct a building.", self.global_manager)
                text_tools.print_to_screen("You have " + str(self.attached_mob.movement_points) + " movement points while 1 is required.", self.global_manager)
                    
            
    def construct(self): #move stuff from on click here
        self.attached_mob.set_movement_points(0)
        if self.building_type == 'resource':
            new_building = buildings.resource_building((self.attached_mob.x, self.attached_mob.y), self.attached_mob.grids, self.global_manager.get('resource_building_dict')[self.attached_resource], self.building_name, self.attached_resource,
                ['strategic'], self.global_manager)
        elif self.building_type == 'port':
            new_building = buildings.port((self.attached_mob.x, self.attached_mob.y), self.attached_mob.grids, 'buildings/port.png', self.building_name,
                ['strategic'], self.global_manager)
        else:
            new_building = buildings.building((self.attached_mob.x, self.attached_mob.y), self.attached_mob.grids, 'buildings/port.png', self.building_name, self.building_type,
                ['strategic'], self.global_manager)
        actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), self.attached_mob.images[0].current_cell.tile)
