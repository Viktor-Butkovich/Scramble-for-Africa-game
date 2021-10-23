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
from . import vehicles

class actor_match_free_image(free_image):
    '''
    Free image that changes its appearance to match selected mobs or tiles
    '''
    def __init__(self, coordinates, width, height, modes, actor_image_type, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this image
            int width: Pixel width of this image
            int height: Pixel height of this image
            string list modes: Game modes during which this image can appear
            string actor_image_type: Type of actor whose appearance will be copied by this image
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.actor_image_type = actor_image_type
        self.actor = 'none'
        super().__init__('misc/empty.png', coordinates, width, height, modes, global_manager)

    def calibrate(self, new_actor):
        '''
        Description:
            Sets this image to match the inputted object's appearance to show in the actor info display
        Input:
            string/actor new_actor: If this equals 'none', hides this image. Otherwise, causes this image will match this input's appearance
        Output:
            None
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
            elif self.actor_image_type in ['port', 'train_station', 'trading_post', 'mission']:
                if not new_actor.cell.contained_buildings[self.actor_image_type] == 'none':
                    self.set_image('buildings/' + self.actor_image_type + '.png')
                else:
                    self.set_image('misc/empty.png')
            elif self.actor_image_type == 'infrastructure_middle':
                contained_infrastructure = new_actor.cell.contained_buildings['infrastructure']
                if not contained_infrastructure == 'none':
                    self.set_image(contained_infrastructure.image_dict['default'])
                else:
                    self.set_image('misc/empty.png')
            elif self.actor_image_type == 'infrastructure_connection':
                contained_infrastructure = new_actor.cell.contained_buildings['infrastructure']
                if not contained_infrastructure == 'none':
                    if contained_infrastructure.infrastructure_connection_images[self.direction].can_show():
                        self.set_image(contained_infrastructure.infrastructure_connection_images[self.direction].image_id)
                    else:
                        self.set_image('misc/empty.png')
                else:
                    self.set_image('misc/empty.png')
            elif self.actor_image_type == 'veteran_icon':
                if (self.actor.is_officer or self.actor.is_group) and self.actor.veteran:
                    self.set_image('misc/veteran_icon.png')
                else:
                    self.set_image('misc/empty.png')
            else:
                self.set_image(new_actor.image_dict['default'])
        else:
            self.set_image('misc/empty.png')

    def can_show(self):
        '''
        Description:
            Returns whether this image should be drawn
        Input:
            None
        Output:
            boolean: False if there is no actor in the info display, otherwise returns same value as superclass
        '''
        if self.actor == 'none':
            return(False)
        else:
            return(super().can_show())

class actor_match_infrastructure_connection_image(actor_match_free_image):
    '''
    Image appearing on tile info display to show the road/railroad connections of the displayed tile
    '''
    def __init__(self, coordinates, width, height, modes, actor_image_type, direction, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this image
            int width: Pixel width of this image
            int height: Pixel height of this image
            string list modes: Game modes during which this image can appear
            string actor_image_type: Type of actor whose appearance will be copied by this image
            string direction: 'up', 'down', 'left', or 'right', side of tile that this image points to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.direction = direction
        super().__init__(coordinates, width, height, modes, actor_image_type, global_manager)

class actor_match_background_image(free_image):
    '''
    Image appearing behind the displayed actor in the actor info display
    '''
    def __init__(self, image_id, coordinates, width, height, modes, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            string image_id: File path to the image used by this object
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this image
            int width: Pixel width of this image
            int height: Pixel height of this image
            string list modes: Game modes during which this image can appear
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(image_id, coordinates, width, height, modes, global_manager)
        self.actor = 'none'

    def calibrate(self, new_actor):
        '''
        Description:
            Updates which actor is in front of this image
        Input:
            string/actor new_actor: The displayed actor that goes in front of this image. If this equals 'none', there is no actor in front of it
        Output:
            None
        '''
        self.actor = new_actor

    def can_show(self):
        '''
        Description:
            Returns whether this image should be drawn
        Input:
            None
        Output:
            boolean: False if there is no actor in the info display, otherwise returns same value as superclass
        '''
        if self.actor == 'none':
            return(False)
        else:
            return(super().can_show())

    def update_tooltip(self):
        '''
        Description:
            Sets this image's tooltip to that of the actor in front of it
        Input:
            None
        Output:
            None
        '''
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
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this image
            int width: Pixel width of this image
            int height: Pixel height of this image
            string list modes: Game modes during which this image can appear
            label attached_label: The label that this image is attached to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.attached_label = attached_label
        super().__init__('misc/empty.png', coordinates, width, height, modes, global_manager)

    def can_show(self):
        '''
        Description:
            Returns whether this image should be drawn
        Input:
            None
        Output:
            boolean: False if this image's label is not showing, otherwise returns same value as superclass
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
        Description:
            Initializes this object. Depending on the actor_label_type, various buttons are created to appear next to this label
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this label
            int minimum_width: Minimum pixel width of this label. As the length of its message increases, this label's width will increase to accomodate it. 
            int height: Pixel height of this label
            string list modes: Game modes during which this label can appear
            string image_id: File path to the image used by this object
            string actor_label_type: Type of actor information shown by this label
            string actor_type: 'mob' or 'tile', depending on the type of actor this label displays the information of
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        message = ''
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
            self.attached_buttons.append(merge_button((self.x, self.y), self.height, self.height, pygame.K_m, self.modes, 'misc/merge_button.png', self, global_manager))
            self.attached_buttons.append(split_button((self.x, self.y), self.height, self.height, pygame.K_n, self.modes, 'misc/split_button.png', self, global_manager))
            self.attached_buttons.append(embark_vehicle_button((self.x, self.y), self.height, self.height, pygame.K_b, self.modes, 'misc/embark_ship_button.png', self, 'ship', global_manager))
            self.attached_buttons.append(embark_vehicle_button((self.x, self.y), self.height, self.height, pygame.K_b, self.modes, 'misc/embark_train_button.png', self, 'train', global_manager))
            self.attached_buttons.append(worker_crew_vehicle_button((self.x, self.y), self.height, self.height, pygame.K_m, self.modes, 'misc/crew_ship_button.png', self, 'ship', global_manager))
            self.attached_buttons.append(worker_crew_vehicle_button((self.x, self.y), self.height, self.height, pygame.K_m, self.modes, 'misc/crew_train_button.png', self, 'train', global_manager))
            self.attached_buttons.append(worker_to_building_button((self.x, self.y), self.height, self.height, pygame.K_f, 'resource', self.modes, 'misc/worker_to_building_button.png', self, global_manager))
            self.attached_buttons.append(switch_theatre_button((self.x, self.y), self.height, self.height, pygame.K_g, self.modes, 'misc/switch_theatre_button.png', self, global_manager))
            self.attached_buttons.append(construction_button((self.x, self.y), self.height, self.height, pygame.K_f, self.modes, self, 'resource', global_manager))
            self.attached_buttons.append(construction_button((self.x, self.y), self.height, self.height, pygame.K_p, self.modes, self, 'port', global_manager))
            self.attached_buttons.append(construction_button((self.x, self.y), self.height, self.height, pygame.K_r, self.modes, self, 'infrastructure', global_manager))
            self.attached_buttons.append(construction_button((self.x, self.y), self.height, self.height, pygame.K_t, self.modes, self, 'train_station', global_manager))
            self.attached_buttons.append(construction_button((self.x, self.y), self.height, self.height, pygame.K_y, self.modes, self, 'trading_post', global_manager))
            self.attached_buttons.append(construction_button((self.x, self.y), self.height, self.height, pygame.K_y, self.modes, self, 'mission', global_manager))
            self.attached_buttons.append(build_train_button((self.x, self.y), self.height, self.height, pygame.K_y, self.modes, 'misc/build_train_button.png', self, global_manager))
            self.attached_buttons.append(trade_button((self.x, self.y), self.height, self.height, pygame.K_r, self.modes, 'misc/trade_button.png', self, global_manager))
            self.attached_buttons.append(convert_button((self.x, self.y), self.height, self.height, pygame.K_t, self.modes, 'misc/convert_button.png', self, global_manager))
            self.attached_buttons.append(religious_campaign_button((self.x, self.y), self.height, self.height, pygame.K_t, self.modes, 'misc/religious_campaign_button.png', self, global_manager))
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
            self.attached_buttons.append(crew_vehicle_button((self.x, self.y), self.height, self.height, pygame.K_m, self.modes, 'misc/crew_ship_button.png', self, global_manager))
            self.attached_buttons.append(uncrew_vehicle_button((self.x, self.y), self.height, self.height, pygame.K_n, self.modes, 'misc/uncrew_ship_button.png', self, global_manager))
        elif self.actor_label_type == 'passengers':
            self.message_start = 'Passengers: '
            self.attached_buttons.append(cycle_passengers_button((self.x, self.y), self.height, self.height, pygame.K_4, self.modes, 'misc/cycle_passengers_down.png', self, global_manager))
            self.attached_buttons.append(pick_up_all_passengers_button((self.x, self.y), self.height, self.height, pygame.K_z, self.modes, 'misc/embark_ship_button.png', self, global_manager))
        elif self.actor_label_type == 'current passenger':
            self.message_start = ''
            keybind = 'none'
            if self.list_index == 0:
                keybind = pygame.K_1
            elif self.list_index == 1:
                keybind = pygame.K_2
            elif self.list_index == 2:
                keybind = pygame.K_3
            self.attached_buttons.append(disembark_vehicle_button((self.x, self.y), self.height, self.height, keybind, self.modes, 'misc/disembark_ship_button.png', self, global_manager))
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
        '''
        Description:
            Sets this label's tooltip based on the label's type and the information of the actor it is attached to
        Input:
            None
        Output:
            None
        '''
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
        Description:
            Attaches this label to the inputted actor and updates this label's information based on the inputted actor
        Input:
            string/actor new_actor: The displayed actor that whose information is matched by this label. If this equals 'none', the label does not match any actors.
        Output:
            None
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
                if not new_actor.has_infinite_movement:
                    self.set_label(self.message_start + str(new_actor.movement_points) + '/' + str(new_actor.max_movement_points))
                else:
                    if new_actor.is_vehicle and new_actor.vehicle_type == 'train':
                        if new_actor.movement_points == 0 or not new_actor.has_crew:
                            self.set_label("No movement")
                        else:
                            self.set_label("Infinite movement until cargo/passenger dropped")
                    else:
                        if new_actor.movement_points == 0 or not new_actor.has_crew:
                            self.set_label("No movement")
                        else:
                            self.set_label("Infinite movement")
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
                        self.set_label("A " + self.actor.vehicle_type + " requires crew to function")
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
        '''
        Description:
            Sets this label's text to the inputted string. Also changes locations of attached buttons since the length of the label may change.
        Input:
            string new_message: New text to set this label to
        Output:
            None
        '''
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
        '''
        Description:
            Sets this label's y position and that of its attached buttons
        Input:
            int new_y: New y coordinate to set this label and its buttons to
        Output:
            None
        '''
        self.y = new_y
        self.image.y = self.y
        self.Rect.y = self.global_manager.get('display_height') - (self.y + self.height)#self.y
        self.image.Rect = self.Rect    
        for current_button in self.attached_buttons:
            current_button.y = self.y
            current_button.Rect.y = self.global_manager.get('display_height') - (current_button.y + current_button.height)
            current_button.outline.y = current_button.Rect.y - current_button.outline_width

    def can_show(self):
        '''
        Description:
            Returns whether this label should be drawn
        Input:
            None
        Output:
            boolean: False if no actor displayed or if various conditions are present depending on label type, otherwise returns same value as superclass
        '''
        result = super().can_show()
        if self.actor == 'none':
            return(False)
        elif self.actor_label_type == 'tile inventory capacity' and not self.actor.cell.visible: #do not show inventory capacity in unexplored tiles
            return(False)
        elif self.actor_label_type == 'resource' and self.actor.grid.is_abstract_grid: #do not show resource label on the Europe tile
            return(False)
        elif self.actor_label_type in ['crew', 'passengers'] and not self.actor.is_vehicle: #do not show passenger or crew labels for non-vehicle mobs
            return(False)
        elif self.actor.actor_type == 'mob' and (self.actor.in_vehicle or self.actor.in_group or self.actor.in_building): #do not show mobs that are attached to another unit/building
            return(False)
        else:
            return(result)

class list_item_label(actor_match_label):
    '''
    Label that shows the information of a certain item in a list, like a train passenger among a list of passengers
    '''
    def __init__(self, coordinates, minimum_width, height, modes, image_id, actor_label_type, list_index, list_type, actor_type, global_manager):
        '''
        Description:
            Initializes this object. Depending on the actor_label_type, various buttons are created to appear next to this label
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this label
            int minimum_width: Minimum pixel width of this label. As the length of its message increases, this label's width will increase to accomodate it. 
            int height: Pixel height of this label
            string list modes: Game modes during which this label can appear
            string image_id: File path to the image used by this object
            string actor_label_type: Type of actor information shown by this label
            int list_index: Index to determine which item of a list is reflected by this label
            string list_type: Type of list reflected by this lagel, such as a 'resource building' for a label type of 'building worker' to show that this label shows the workers attached to resource buildings but not other buildings
            string actor_type: 'mob' or 'tile', depending on the type of actor this label displays the information of
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.list_index = list_index
        self.list_type = list_type
        self.attached_list = []
        super().__init__(coordinates, minimum_width, height, modes, image_id, actor_label_type, actor_type, global_manager)

    def calibrate(self, new_actor):
        '''
        Description:
            Attaches this label to the inputted actor and updates this label's information based on one of the inputted actor's lists
        Input:
            string/actor new_actor: The displayed actor that whose information is matched by this label. If this equals 'none', the label does not match any actors
        Output:
            None
        '''
        self.attached_list = []
        super().calibrate(new_actor)

    def can_show(self):
        '''
        Description:
            Returns whether this label should be drawn
        Input:
            None
        Output:
            boolean: Returns same value as superclass as long as this label's list is long enough to contain this label's index, otherwise returns False
        '''
        if len(self.attached_list) > self.list_index:
            return(super().can_show())
        return(False)

class building_workers_label(actor_match_label):
    '''
    Label at the top of the list of workers in a building that shows how many workers are in it
    '''
    def __init__(self, coordinates, minimum_width, height, modes, image_id, building_type, actor_type, global_manager):
        '''
        Description:
            Initializes this object. Depending on the actor_label_type, various buttons are created to appear next to this label
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this label
            int minimum_width: Minimum pixel width of this label. As the length of its message increases, this label's width will increase to accomodate it. 
            int height: Pixel height of this label
            string list modes: Game modes during which this label can appear
            string image_id: File path to the image used by this object
            string building_type: Type of building this label shows the workers of, like 'resource building'
            string actor_type: 'mob' or 'tile', depending on the type of actor this label displays the information of
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.remove_worker_button = 'none'
        super().__init__(coordinates, minimum_width, height, modes, image_id, 'building workers', actor_type, global_manager)
        self.building_type = building_type
        self.attached_building = 'none'
        self.showing = False

    def calibrate(self, new_actor):
        '''
        Description:
            Attaches this label to the inputted actor and updates this label's information based on the inputted actor
        Input:
            string/actor new_actor: The displayed actor that whose information is matched by this label. If this equals 'none', the label does not match any actors.
        Output:
            None
        '''
        self.actor = new_actor
        self.showing = False
        if not new_actor == 'none':
            self.attached_building = new_actor.cell.contained_buildings[self.building_type]
            if not self.attached_building == 'none':
                self.set_label("Workers: " + str(len(self.attached_building.contained_workers)) + '/' + str(self.attached_building.worker_capacity))
                self.showing = True

    def can_show(self):
        '''
        Description:
            Returns whether this label should be drawn
        Input:
            None
        Output:
            boolean: Returns same value as superclass as long as the displayed tile has a building of this label's building_type, otherwise returns False
        '''
        if self.showing:
            return(super().can_show())
        else:
            return(False)

class native_info_label(actor_match_label): #possible actor_label_types: native aggressiveness, native population, native available workers
    '''
    Label that shows the population, aggressiveness, or number of available workers in a displayed tile's village
    '''
    def can_show(self):
        '''
        Description:
            Returns whether this label should be drawn
        Input:
            None
        Output:
            boolean: Returns same value as superclass as long as the displayed tile is explored and has a village, otherwise returns False
        '''
        result = super().can_show()
        if result:
            if (not self.actor.cell.village == 'none') and self.actor.cell.visible:
                return(True)
        return(False)
        

class commodity_match_label(actor_match_label):
    '''
    Label that changes its text and attached image and button to match the commodity in a certain part of a currently selected actor's inventory    
    '''
    def __init__(self, coordinates, minimum_width, height, modes, image_id, commodity_index, matched_actor_type, global_manager):
        '''
        Description:
            Initializes this object. Depending on the actor_label_type, various buttons are created to appear next to this label
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this label
            int minimum_width: Minimum pixel width of this label. As the length of its message increases, this label's width will increase to accomodate it. 
            int height: Pixel height of this label
            string list modes: Game modes during which this label can appear
            string image_id: File path to the image used by this object
            int commodity_index: Index to determine which item of an actor's inventory is reflected by this label
            string matched_actor_type: 'mob' or 'tile', depending on the type of actor this label displays the information of
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.current_commodity = 'none'
        super().__init__(coordinates, minimum_width, height, modes, image_id, 'commodity', matched_actor_type, global_manager)
        self.showing_commodity = False
        self.commodity_index = commodity_index
        self.commodity_image = label_image((self.x - self.height, self.y), self.height, self.height, self.modes, self, self.global_manager) #self, coordinates, width, height, modes, attached_label, global_manager
        if matched_actor_type == 'mob':
            self.attached_buttons.append(label_button((self.x, self.y), self.height, self.height, 'drop commodity', 'none', self.modes, 'misc/commodity_drop_button.png', self, global_manager))
            self.attached_buttons.append(label_button((self.x + (self.height + 5), self.y), self.height, self.height, 'drop all commodity', 'none', self.modes, 'misc/commodity_drop_all_button.png', self, global_manager))
        elif matched_actor_type == 'tile':
            self.attached_buttons.append(label_button((self.x, self.y), self.height, self.height, 'pick up commodity', 'none', self.modes, 'misc/commodity_pick_up_button.png', self, global_manager))
            self.attached_buttons.append(label_button((self.x + (self.height + 5), self.y), self.height, self.height, 'pick up all commodity', 'none', self.modes, 'misc/commodity_pick_up_all_button.png', self, global_manager))
            self.attached_buttons.append(label_button((self.x + ((self.height + 5) * 2), self.y), self.height, self.height, 'sell commodity', 'none', ['europe'], 'misc/commodity_sell_button.png', self, global_manager))
            self.attached_buttons.append(label_button((self.x + ((self.height + 5) * 3), self.y), self.height, self.height, 'sell all commodity', 'none', ['europe'], 'misc/commodity_sell_all_button.png', self, global_manager))

    def set_label(self, new_message):
        '''
        Description:
            Sets this label's text to the inputted string and changes locations of attached buttons since the length of the label may change. Also changes this label's attached image to match the commodity
        Input:
            string new_message: New text to set this label to
        Output:
            None
        '''
        super().set_label(new_message)
        if not self.actor == 'none':
            commodity_list = self.actor.get_held_commodities()
            if len(commodity_list) > self.commodity_index:
                commodity = commodity_list[self.commodity_index]
                self.commodity_image.set_image('scenery/resources/' + commodity + '.png')
            

    def calibrate(self, new_actor):
        '''
        Description:
            Attaches this label to the inputted actor and updates this label's information based on the inputted actor
        Input:
            string/actor new_actor: The displayed actor that whose information is matched by this label. If this equals 'none', the label does not match any actors.
        Output:
            None
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
        Description:
            Returns whether this label should be drawn
        Input:
            None
        Output:
            boolean: Returns False if this label's commodity_index is not in the attached actor's inventory. Otherwise, returns same value as superclass
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
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string button_type: Determines the function of this button, like 'end turn'
            pygame key object keybind_id: Determines the keybind id that activates this button, like pygame.K_n
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            label attached_label: Label that this button is attached to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.attached_label = attached_label
        super().__init__(coordinates, width, height, 'blue', button_type, keybind_id, modes, image_id, global_manager)#coordinates, width, height, color, button_type, keybind_id, modes, image_id, global_manager

    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns same value as superclass if this button's label is showing, otherwise returns False. Exception for sell commodity buttons, which will not be not be able to sell consumer goods and will be hidden when
                attached to an inventory label showing consumer goods
        '''
        if self.attached_label.can_show():
            if not ((self.button_type == 'sell commodity' or self.button_type == 'sell all commodity') and self.attached_label.current_commodity == 'consumer goods'):
                return(super().can_show())
        return(False)


class worker_crew_vehicle_button(label_button):
    '''
    Button that commands a worker to crew a vehicle in its tile
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, vehicle_type, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string keybind_id: Determines the keybind id that activates this button, like 'pygame.K_n'
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            label attached_label: Label that this button is attached to
            string vehicle_type: 'train' or 'ship', determines what kind of vehicle this button crews
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.vehicle_type = vehicle_type
        self.was_showing = False
        super().__init__(coordinates, width, height, 'worker to crew', keybind_id, modes, image_id, attached_label, global_manager)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a worker to crew a vehicle in its tile
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):    
                selected_list = actor_utility.get_selected_list(self.global_manager)
                vehicle = self.attached_label.actor.images[0].current_cell.get_uncrewed_vehicle(self.vehicle_type)
                crew = self.attached_label.actor
                if (not (vehicle == 'none' or crew == 'none')) and (not vehicle.has_crew): #if vehicle and rider selected
                    if vehicle.x == crew.x and vehicle.y == crew.y: #ensure that this doesn't work across grids
                        crew.crew_vehicle(vehicle)
                    else:
                        text_tools.print_to_screen("You must select a worker in the same tile as an uncrewed " + self.vehicle_type + " to crew the " + self.vehicle_type + ".", self.global_manager)
                else:
                    text_tools.print_to_screen("You must select a worker in the same tile as an uncrewed " + self.vehicle_type + " to crew the " + self.vehicle_type + ".", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not crew a " + self.vehicle_type + ".", self.global_manager)

    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if a worker is not selected or if its tile does not have an uncrewed vehicle of the correct type, otherwise returns False
        '''
        result = super().can_show()
        if result:
            if (not (self.attached_label.actor.is_worker and not self.attached_label.actor.is_church_volunteers)) or (not self.attached_label.actor.images[0].current_cell.has_uncrewed_vehicle(self.vehicle_type)):
                result = False
        if not result == self.was_showing: #if visibility changes, update actor info display
            self.was_showing = result
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self.attached_label.actor)
        self.was_showing = result
        return(result)

class pick_up_all_passengers_button(label_button):
    '''
    Button that commands a vehicle to take all other mobs in its tile as passengers
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string keybind_id: Determines the keybind id that activates this button, like 'pygame.K_n'
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            label attached_label: Label that this button is attached to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.vehicle_type = 'none'
        super().__init__(coordinates, width, height, 'pick up all passengers', keybind_id, modes, image_id, attached_label, global_manager)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a vehicle to take all other mobs in its tile as passengers
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):    
                vehicle = self.attached_label.actor
                for contained_mob in vehicle.images[0].current_cell.contained_mobs:
                    passenger = contained_mob
                    if not passenger.is_vehicle: #vehicles won't be picked up as passengers
                        passenger.embark_vehicle(vehicle)
            else:
                text_tools.print_to_screen("You are busy and can not pick up passengers.", self.global_manager)

    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn. Also updates this button to reflect a train or ship depending on the selected vehicle
        Input:
            None
        Output:
            boolean: Returns False if the selected vehicle has no crew, otherwise returns same as superclass
        '''
        result = super().can_show()
        if result:
            if not self.attached_label.actor.has_crew: #do not show if ship does not have crew
                return(False)
            if (not self.vehicle_type == self.attached_label.actor.vehicle_type) and (not self.attached_label.actor.vehicle_type == 'vehicle'): #update vehicle type and image when shown if type has changed, like train to ship
                self.vehicle_type = self.attached_label.actor.vehicle_type
                self.image.set_image('misc/embark_' + self.vehicle_type + '_button.png')
        return(result)

class crew_vehicle_button(label_button):
    '''
    Button that commands a vehicle to take a worker in its tile as crew. Also updates this button to reflect a train or ship depending on the selected vehicle
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string keybind_id: Determines the keybind id that activates this button, like 'pygame.K_n'
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            label attached_label: Label that this button is attached to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.vehicle_type = 'none'
        super().__init__(coordinates, width, height, 'crew', keybind_id, modes, image_id, attached_label, global_manager)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a vehicle to take a worker in its tile as crew
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):    
                vehicle = self.attached_label.actor
                crew = vehicle.images[0].current_cell.get_worker() #'none'
                #for contained_mob in vehicle.images[0].current_cell.contained_mobs:
                #    if contained_mob.is_worker:
                #        crew = contained_mob
                if (not (vehicle == 'none' or crew == 'none')) and (not vehicle.has_crew): #if vehicle and rider selected
                    if vehicle.x == crew.x and vehicle.y == crew.y: #ensure that this doesn't work across grids
                        crew.crew_vehicle(vehicle)
                    else:
                        text_tools.print_to_screen("You must select an uncrewed " + self.vehicle_type + " in the same tile as a worker to crew the " + self.vehicle_type + ".", self.global_manager)
                else:
                    text_tools.print_to_screen("You must select an uncrewed " + self.vehicle_type + " in the same tile as a worker to crew the " + self.vehicle_type + ".", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not crew a " + self.vehicle_type + ".", self.global_manager)

    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn. Also updates this button to reflect a train or ship depending on the selected vehicle
        Input:
            None
        Output:
            boolean: Returns False if the selected vehicle has crew, otherwise returns same as superclass
        '''
        result = super().can_show()
        if result:
            if self.attached_label.actor.has_crew:
                return(False)
            if (not self.vehicle_type == self.attached_label.actor.vehicle_type) and (not self.attached_label.actor.vehicle_type == 'vehicle'): #update vehicle type and image when shown if type has changed, like train to ship
                self.vehicle_type = self.attached_label.actor.vehicle_type
                self.image.set_image('misc/crew_' + self.vehicle_type + '_button.png')
        return(result)

class uncrew_vehicle_button(label_button):
    '''
    Button that commands a vehicle's crew to leave the vehicle
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string keybind_id: Determines the keybind id that activates this button, like 'pygame.K_n'
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            label attached_label: Label that this button is attached to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.vehicle_type = 'none'
        super().__init__(coordinates, width, height, 'uncrew', keybind_id, modes, image_id, attached_label, global_manager)
        
    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn. Also updates this button to reflect a train or ship depending on the selected vehicle
        Input:
            None
        Output:
            boolean: Returns False if the selected vehicle has no crew, otherwise returns same as superclass
        '''
        result = super().can_show()
        if result:
            if not self.attached_label.actor.has_crew:
                return(False)
            if (not self.vehicle_type == self.attached_label.actor.vehicle_type) and (not self.attached_label.actor.vehicle_type == 'vehicle'):
                self.vehicle_type = self.attached_label.actor.vehicle_type
                self.image.set_image('misc/uncrew_' + self.vehicle_type + '_button.png')
        return(result)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a vehicle's crew to leave the vehicle
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):
                vehicle = self.attached_label.actor
                crew = vehicle.crew
                if len(vehicle.contained_mobs) == 0 and len(vehicle.get_held_commodities()) == 0:
                    crew.uncrew_vehicle(vehicle)
                else:
                    text_tools.print_to_screen("You can not remove the crew from a " + self.vehicle_type + " with passengers or cargo.", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not remove a " + self.vehicle_type + "'s crew.", self.global_manager)

class merge_button(label_button):
    '''
    Button that merges a selected officer with a worker in the same tile to form a group
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string keybind_id: Determines the keybind id that activates this button, like 'pygame.K_n'
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            label attached_label: Label that this button is attached to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(coordinates, width, height, 'merge', keybind_id, modes, image_id, attached_label, global_manager)
        
    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not an officer, otherwise returns same as superclass
        '''
        result = super().can_show()
        if result:
            if not self.attached_label.actor.is_officer:
                return(False)
        return(result)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button merges a selected officer with a worker in the same tile to form a group
        Input:
            None
        Output:
            None
        '''
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
                            if officer.officer_type == 'head missionary': #if head missionary, look for church volunteers
                                worker = officer.images[0].current_cell.get_church_volunteers()
                            else:
                                worker = officer.images[0].current_cell.get_worker()
                    if not (officer == 'none' or worker == 'none'): #if worker and officer selected
                        if officer.x == worker.x and officer.y == worker.y:
                            groups.create_group(worker, officer, self.global_manager) #groups.create_group(officer.images[0].current_cell.get_worker(), officer, self.global_manager)
                        else:
                            if (not officer == 'none') and officer.officer_type == 'head missionary':
                                text_tools.print_to_screen("You must select a head missionary in the same tile as church volunteers to create a group.", self.global_manager)
                            else:  
                                text_tools.print_to_screen("You must select an officer in the same tile as a worker to create a group.", self.global_manager)
                    else:
                        if (not officer == 'none') and officer.officer_type == 'head missionary':
                            text_tools.print_to_screen("You must select a head missionary in the same tile as church volunteers to create a group.", self.global_manager)
                        else:  
                            text_tools.print_to_screen("You must select an officer in the same tile as a worker to create a group.", self.global_manager)
                else:
                    text_tools.print_to_screen("You must select an officer in the same tile as a worker to create a group.", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not form a group.", self.global_manager)


class split_button(label_button):
    '''
    Button that splits a selected group into its component officer and worker
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string keybind_id: Determines the keybind id that activates this button, like 'pygame.K_n'
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            label attached_label: Label that this button is attached to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(coordinates, width, height, 'split', keybind_id, modes, image_id, attached_label, global_manager)
        
    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not a group, otherwise returns same as superclass
        '''
        result = super().can_show()
        if result:
            if not self.attached_label.actor.is_group:
                return(False)
        return(result)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button splits a selected group into its component officer and worker
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):         
                displayed_mob = self.global_manager.get('displayed_mob')#selected_list = actor_utility.get_selected_list(self.global_manager)
                if (not displayed_mob == 'none') and displayed_mob.is_group:
                    if not (displayed_mob.can_hold_commodities and len(displayed_mob.get_held_commodities()) > 0): #do not disband if trying to disband a porter who is carrying commodities
                        displayed_mob.disband()
                    else:
                        text_tools.print_to_screen("You can not split a unit that is carrying commodities.", self.global_manager)
                else:
                    text_tools.print_to_screen("Only a group can be split it into a worker and an officer.", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not split a group.", self.global_manager)

class remove_worker_button(label_button):
    '''
    Button that removes a worker from a building
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, building_type, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string keybind_id: Determines the keybind id that activates this button, like 'pygame.K_n'
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            label attached_label: Label that this button is attached to
            string building_type: Determines type of building this button removes workers from, like 'resource building'
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(coordinates, width, height, 'remove worker', keybind_id, modes, image_id, attached_label, global_manager)
        self.building_type = building_type
        
    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if there is not a corresponding worker to remove, otherwise returns same as superclass
        '''
        result = super().can_show()
        if result:
            if not self.attached_label.attached_list[self.attached_label.list_index].in_building:
                return(False)
        return(result)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button removes a worker from a building
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):         
                self.attached_label.attached_list[self.attached_label.list_index].leave_building(self.attached_label.actor.cell.contained_buildings[self.building_type])
            else:
                text_tools.print_to_screen("You are busy and can not remove a worker from a building.", self.global_manager)

class disembark_vehicle_button(label_button):
    '''
    Button that disembarks a passenger from a vehicle
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string keybind_id: Determines the keybind id that activates this button, like 'pygame.K_n'
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            label attached_label: Label that this button is attached to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.vehicle_type = 'none'
        super().__init__(coordinates, width, height, 'disembark', keybind_id, modes, image_id, attached_label, global_manager)
        
    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn. Also updates this button to reflect a train or ship depending on the selected vehicle
        Input:
            None
        Output:
            boolean: Returns False if there is not a corresponding passenger to disembark, otherwise returns same as superclass
        '''
        result = super().can_show()
        if result:
            if not self.attached_label.attached_list[self.attached_label.list_index].in_vehicle:
                return(False)
            old_vehicle_type = self.vehicle_type
            self.vehicle_type = self.attached_label.actor.vehicle_type
            if not self.vehicle_type == old_vehicle_type and not self.vehicle_type == 'none': #if changed
                self.image.set_image('misc/disembark_' + self.vehicle_type + '_button.png')
        return(result)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button disembarks a passenger from a vehicle
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):         
                if len(self.attached_label.actor.contained_mobs) > 0:
                    can_disembark = True
                    if self.vehicle_type == 'train':
                        if self.attached_label.actor.images[0].current_cell.contained_buildings['train_station'] == 'none':
                            text_tools.print_to_screen("A train can only drop off passengers at a train station.", self.global_manager)
                            can_disembark = False
                    if can_disembark:
                        if self.attached_label.actor.is_vehicle and self.attached_label.actor.vehicle_type == 'train': #trains can not move after dropping cargo or passenger
                            self.attached_label.actor.set_movement_points(0)
                        self.attached_label.attached_list[self.attached_label.list_index].disembark_vehicle(self.attached_label.actor)
                else:
                    text_tools.print_to_screen("You must select a " + self.vehicle_type + "with passengers to disembark passengers.", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not disembark from a " + self.vehicle_type + ".", self.global_manager)

class embark_vehicle_button(label_button):
    '''
    Button that commands a selected mob to embark a vehicle of the correct type in the same tile
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, vehicle_type, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string keybind_id: Determines the keybind id that activates this button, like 'pygame.K_n'
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            label attached_label: Label that this button is attached to
            string vehicle_type: 'train' or 'ship', determines what kind of vehicle this button embarks
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.vehicle_type = vehicle_type
        self.was_showing = False
        super().__init__(coordinates, width, height, 'embark', keybind_id, modes, image_id, attached_label, global_manager)
        
    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob can not embark vehicles or if there is no vehicle in the tile to embark, otherwise returns same as superclass
        '''
        result = super().can_show()
        if result:
            if self.attached_label.actor.in_vehicle or self.attached_label.actor.is_vehicle:
                result = False
            elif not self.attached_label.actor.images[0].current_cell.has_vehicle(self.vehicle_type):
                result = False
        if not result == self.was_showing: #if visibility changes, update actor info display
            self.was_showing = result
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self.attached_label.actor)
        self.was_showing = result
        return(result)
    
    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a selected mob to embark a vehicle of the correct type in the same tile
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):
                if self.attached_label.actor.images[0].current_cell.has_vehicle(self.vehicle_type):
                    selected_list = actor_utility.get_selected_list(self.global_manager)
                    num_vehicles = 0
                    vehicle = self.attached_label.actor.images[0].current_cell.get_vehicle(self.vehicle_type)
                    rider = self.attached_label.actor
                    can_embark = True
                    if vehicle.vehicle_type == 'train':
                        if vehicle.images[0].current_cell.contained_buildings['train_station'] == 'none':
                            text_tools.print_to_screen("A train can only pick up passengers at a train station.", self.global_manager)
                            can_embark = False
                    if can_embark:
                        rider.embark_vehicle(vehicle)
                else:
                    text_tools.print_to_screen("You must select a unit in the same tile as a crewed " + self.vehicle_type + " to embark.", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not embark a " + self.vehicle_type + ".", self.global_manager)

class cycle_passengers_button(label_button):
    '''
    Button that cycles the order of passengers displayed in a vehicle
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string keybind_id: Determines the keybind id that activates this button, like 'pygame.K_n'
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            label attached_label: Label that this button is attached to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.vehicle_type = 'none'
        super().__init__(coordinates, width, height, 'cycle passengers', keybind_id, modes, image_id, attached_label, global_manager)
        
    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not a vehicle or if the vehicle does not have enough passengers to cycle through, otherwise returns same as superclass
        '''
        result = super().can_show()
        if result:
            if not self.attached_label.actor.is_vehicle:
                return(False)
            elif not len(self.attached_label.actor.contained_mobs) > 3: #only show if vehicle with 3+ passengers
                return(False)
            self.vehicle_type = self.attached_label.actor.vehicle_type
        return(result)
    
    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button cycles the order of passengers displayed in a vehicle
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):
                moved_mob = self.attached_label.actor.contained_mobs.pop(0)
                self.attached_label.actor.contained_mobs.append(moved_mob)
                actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self.attached_label.actor) #updates mob info display list to show changed passenger order
            else:
                text_tools.print_to_screen("You are busy and can not cycle passengers.", self.global_manager)

class worker_to_building_button(label_button):
    '''
    Button that commands a worker to work in a certain type of building in its tile
    '''
    def __init__(self, coordinates, width, height, keybind_id, building_type, modes, image_id, attached_label, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string keybind_id: Determines the keybind id that activates this button, like 'pygame.K_n'
            string building_type: Type of building this label attaches workers to, like 'resource building'
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            label attached_label: Label that this button is attached to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.building_type = building_type
        self.attached_worker = 'none'
        self.attached_building = 'none'
        self.building_type = building_type
        super().__init__(coordinates, width, height, 'worker to resource', keybind_id, modes, image_id, attached_label, global_manager)#coordinates, width, height, color, button_type, keybind_id, modes, image_id, global_manager

    def update_info(self):
        '''
        Description:
            Updates the building this button assigns workers to depending on the buildings present in this tile
        Input:
            None
        Output:
            None
        '''
        self.attached_worker = self.attached_label.actor #selected_list[0]
        if (not self.attached_worker == 'none') and self.attached_worker.is_worker:
            possible_attached_building = self.attached_worker.images[0].current_cell.contained_buildings[self.building_type]
            if (not possible_attached_building == 'none'): #and building has capacity
                self.attached_building = possible_attached_building
            else:
                self.attached_building = 'none'
        else:
            self.attached_building = 'none'
    
    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not a worker, otherwise returns same as superclass
        '''
        result = super().can_show()
        self.update_info()
        if result:
            if (not self.attached_worker == 'none') and not (self.attached_worker.is_worker and not self.attached_worker.is_church_volunteers): #if selected but not worker, return false
                return(False)
        return(result)
    
    def update_tooltip(self):
        '''
        Description:
            Sets this button's tooltip depending on the building it assigns workers to
        Input:
            None
        Output:
            None
        '''
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
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a worker to work in a certain type of building in its tile
        Input:
            None
        Output:
            None
        '''
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

class trade_button(label_button):
    '''
    Button that commands a caravan to trade with a village
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string keybind_id: Determines the keybind id that activates this button, like 'pygame.K_n'
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            label attached_label: Label that this button is attached to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(coordinates, width, height, 'trade', keybind_id, modes, image_id, attached_label, global_manager)

    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not capable of trading, otherwise returns same as superclass
        '''
        result = super().can_show()
        if result:
            if (not self.attached_label.actor.can_trade):
                return(False)
        return(result)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a caravan to trade with a village
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):
                current_mob = self.attached_label.actor
                if current_mob.movement_points == current_mob.max_movement_points:
                    current_cell = current_mob.images[0].current_cell
                    if current_cell.has_village():
                    #if current_cell.has_trading_post():
                        if current_mob.get_inventory('consumer goods') > 0:
                            #current_mob.set_movement_points(0) have confirmation message to ensure that player wants to trade before using movement points 
                            current_mob.start_trade()
                        else:
                            text_tools.print_to_screen("Trading requires at least 1 unit of consumer goods.", self.global_manager)
                    #elif current_cell.has_village():
                    #    text_tools.print_to_screen("This village does not have a trading post to trade in.", self.global_manager)
                    else:
                        text_tools.print_to_screen("Trading is only possible in a village.", self.global_manager)
                else:
                    text_tools.print_to_screen("Trading requires an entire turn of movement points.", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not trade.", self.global_manager)

class convert_button(label_button):
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, global_manager):
        super().__init__(coordinates, width, height, 'convert', keybind_id, modes, image_id, attached_label, global_manager)

    def can_show(self):
        result = super().can_show()
        if result:
            if (not self.attached_label.actor.can_convert):
                return(False)
        return(result)

    def on_click(self):
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):
                current_mob = self.attached_label.actor
                if current_mob.movement_points == current_mob.max_movement_points:
                    current_cell = current_mob.images[0].current_cell
                    if current_cell.has_village():
                        current_mob.start_converting()
                    else:
                        text_tools.print_to_screen("Converting is only possible in a village.", self.global_manager)
                else:
                    text_tools.print_to_screen("Converting requires an entire turn of movement points.", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not trade.", self.global_manager)

class religious_campaign_button(label_button):
    '''
    Button that starts commands a head missionary to do a religious campaign in Europe
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, global_manager):
        super().__init__(coordinates, width, height, 'religious campaign', keybind_id, modes, image_id, attached_label, global_manager)

    def can_show(self):
        result = super().can_show()
        if result:
            if (not (self.attached_label.actor.is_officer and self.attached_label.actor.officer_type == 'head missionary')):
                return(False)
        return(result)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a caravan to trade with a village
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):
                current_mob = self.attached_label.actor
                if self.global_manager.get('europe_grid') in current_mob.grids:
                    if current_mob.movement_points == current_mob.max_movement_points:
                        current_mob.start_religious_campaign()
                    else:
                        text_tools.print_to_screen("A religious campaign requires an entire turn of movement points.", self.global_manager)
                else:
                    text_tools.print_to_screen("Religious campaigns are only possible in Europe", self.global_manager)
            else:
                text_tools.print_to_screen("You are busy and can not start a religious campaign.", self.global_manager)

class switch_theatre_button(label_button):
    '''
    Button starts choosing a destination for a ship to travel between theatres, like between Europe and Africa. A destination is chosen when the player clicks a tile in another theatre.
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string keybind_id: Determines the keybind id that activates this button, like 'pygame.K_n'
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            label attached_label: Label that this button is attached to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(coordinates, width, height, 'switch theatre', keybind_id, modes, image_id, attached_label, global_manager)

    def on_click(self):      
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button starts choosing a destination for a ship to travel between theatres, like between Europe and Africa. A
                destination is chosen when the player clicks a tile in another theatre.
        Input:
            None
        Output:
            None
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
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not capable of traveling between theatres, otherwise returns same as superclass
        '''
        result = super().can_show()
        if result:
            if (not self.attached_label.actor.travel_possible): #if selected but not worker, return false
                return(False)
        return(result) 

class build_train_button(label_button):
    '''
    Button that commands a construction gang to build a train at a train station
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, attached_label, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string keybind_id: Determines the keybind id that activates this button, like 'pygame.K_n'
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            label attached_label: Label that this button is attached to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(coordinates, width, height, 'build train', keybind_id, modes, image_id, attached_label, global_manager)

    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not capable of constructing buildings, otherwise returns same as superclass
        '''
        result = super().can_show()
        if result:
            if (not self.attached_label.actor.can_construct): #if selected but not worker, return false
                return(False)
        return(result)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a construction gang to build a train at a train station
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.showing_outline = True
            if self.attached_label.actor.movement_points >= 1:
                    if not self.global_manager.get('europe_grid') in self.attached_label.actor.grids:
                        if not self.attached_label.actor.images[0].current_cell.terrain == 'water':
                            if not self.attached_label.actor.images[0].current_cell.contained_buildings['train_station'] == 'none': #if train station present
                                image_dict = {'default': 'mobs/train/crewed.png', 'crewed': 'mobs/train/crewed.png', 'uncrewed': 'mobs/train/uncrewed.png'}
                                new_train = vehicles.train((self.attached_label.actor.x, self.attached_label.actor.y), self.attached_label.actor.grids, image_dict, 'train', ['strategic'], 'none', self.global_manager)
                            else:
                                text_tools.print_to_screen("A train can only be built on a train station.", self.global_manager)
                        else:
                            text_tools.print_to_screen("A train can only be built on a train station.", self.global_manager)
                    else:
                        text_tools.print_to_screen("A train can only be built on a train station.", self.global_manager)
            else:
                text_tools.print_to_screen("You do not have enough movement points to construct a train.", self.global_manager)
                text_tools.print_to_screen("You have " + str(self.attached_label.actor.movement_points) + " movement points while 1 is required.", self.global_manager)

class construction_button(label_button): #coordinates, width, height, keybind_id, modes, image_id, attached_label, global_manager
    '''
    Button that commands a mob to construct a certain type of building
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, attached_label, building_type, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string keybind_id: Determines the keybind id that activates this button, like 'pygame.K_n'
            string list modes: Game modes during which this button can appear
            label attached_label: Label that this button is attached to
            string building_type: Type of building that this button builds, like 'resource building'
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.building_type = building_type
        self.attached_mob = 'none'
        self.attached_tile = 'none'
        self.building_name = 'none'
        self.requirement = 'can_construct'
        image_id = 'misc/default_button.png'
        if self.building_type == 'resource':
            self.attached_resource = 'none'
            image_id = global_manager.get('resource_building_button_dict')['none']
        elif self.building_type == 'port':
            image_id = 'buildings/buttons/port.png'
            self.building_name = 'port'
        elif self.building_type == 'infrastructure':
            self.road_image_id = 'misc/road_button.png'
            self.railroad_image_id = 'misc/railroad_button.png'
            image_id = self.road_image_id
        elif self.building_type == 'train_station':
            image_id = 'misc/train_station_button.png'
            self.building_name = 'train station'
        elif self.building_type == 'trading_post':
            image_id = 'misc/trading_post_button.png'
            self.building_name = 'trading post'
            self.requirement = 'can_trade'
        elif self.building_type == 'mission':
            image_id = 'misc/mission_button.png'
            self.building_name = 'mission'
            self.requirement = 'can_convert'
        super().__init__(coordinates, width, height, 'construction', keybind_id, modes, image_id, attached_label, global_manager)#coordinates, width, height, color, button_type, keybind_id, modes, image_id, global_manager

    def update_info(self):
        '''
        Description:
            Updates the exact kind of building constructed by this button depending on what is in the selected mob's tile, like building a road or upgrading a previously constructed road to a railroad
        Input:
            None
        Output:
            None
        '''
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
                elif self.building_type == 'infrastructure':
                    current_infrastructure = self.attached_tile.cell.contained_buildings['infrastructure']
                    if current_infrastructure == 'none':
                        self.building_name = 'road'
                        self.image.set_image('misc/road_button.png')
                    else: #if has road or railroad, show railroad icon
                        self.building_name = 'railroad'
                        self.image.set_image('misc/railroad_button.png')

    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not capable of constructing the building that this button constructs, otherwise returns same as superclass
        '''
        result = super().can_show()
        if result:
            self.update_info()
            can_create = 'none'
            if self.requirement == 'can_construct':
                can_create = self.attached_label.actor.can_construct
            elif self.requirement == 'can_trade':
                can_create = self.attached_label.actor.can_trade
            elif self.requirement == 'can_convert':
                can_create = self.attached_label.actor.can_convert
            if (not can_create): #show if unit selected can create this building
                return(False)
        return(result) 

    def update_tooltip(self):
        '''
        Description:
            Sets this button's tooltip depending on the type of building it constructs
        Input:
            None
        Output:
            None
        '''
        if self.building_type == 'resource':
            if self.attached_resource == 'none':
                self.set_tooltip(['Builds a building that produces commodities over time', 'Can only be built in the same tile as a resource', 'Costs 1 movement point'])
            else:
                self.set_tooltip(['Builds a ' + self.building_name + ' that produces ' + self.attached_resource + ' over time', 'Can only be built in the same tile as a ' + self.attached_resource + ' resource.',
                    'Costs 1 movement point'])
        elif self.building_type == 'port':
            self.set_tooltip(['Builds a port, allowing ships to land in this tile', 'Can only be built in a tile adjacent to water', 'Costs 1 movement point'])
        elif self.building_type == 'train_station':
            self.set_tooltip(['Builds a train station, allowing trains to pick up and drop off passengers and cargo', 'Can only be built on a railroad', 'Costs 1 movement point'])
        elif self.building_type == 'infrastructure':
            if self.building_name == 'railroad':
                self.set_tooltip(["Upgrades this tile's road into a railroad, allowing trains to move through this tile", "Retains the benefits of a road",
                    "Costs 1 movement point"])
            else:
                self.set_tooltip(['Builds a road, halving the cost to move between this tile and other tiles with roads or railroads', 'A road can be upgraded into a railroad that allows trains to move through this tile',
                    'Costs 1 movement point'])
        elif self.building_type == 'trading_post':
            self.set_tooltip(['Builds a trading post, allowing merchant caravans to trade with an attached village', 'Can only be built in a village', 'Costs 1 movement point'])
        elif self.building_type == 'mission':
            self.set_tooltip(['Builds a mission, allowing missionaries to convert an attached village', 'Can only be built in a village', 'Costs 1 movement point'])
        else:
            self.set_tooltip(['placeholder'])

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a mob to construct a certain type of building
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.showing_outline = True
            if self.attached_mob.movement_points >= 1:
                current_building = self.attached_tile.cell.contained_buildings[self.building_type]
                if current_building == 'none' or (self.building_name == 'railroad' and current_building.is_road): #able to upgrade to railroad even though road is present, later add this to all upgradable buildings
                    if not self.global_manager.get('europe_grid') in self.attached_mob.grids:
                        if not self.attached_tile.cell.terrain == 'water':
                            if self.building_type == 'resource':
                                if not self.attached_resource == 'none':
                                    self.construct()
                                else:
                                    text_tools.print_to_screen("This building can only be built in tiles with resources.", self.global_manager)
                            elif self.building_type == 'port':
                                if self.attached_mob.adjacent_to_water():
                                    if not self.attached_mob.images[0].current_cell.terrain == 'water':
                                        self.construct()
                                else:
                                    text_tools.print_to_screen("This building can only be built in tiles adjacent to water.", self.global_manager)
                            elif self.building_type == 'train_station':
                                if self.attached_tile.cell.has_railroad():
                                    self.construct()
                                else:
                                    text_tools.print_to_screen("This building can only be built on railroads.", self.global_manager)
                            elif self.building_type == 'infrastructure':
                                self.construct()
                            elif self.building_type == 'trading_post' or self.building_type == 'mission':
                                if self.attached_tile.cell.has_village():
                                    self.construct()
                                else:
                                    text_tools.print_to_screen("This building can only be built in villages.", self.global_manager)
                        else:
                            text_tools.print_to_screen("This building can not be built in water.", self.global_manager)
                    else:
                        text_tools.print_to_screen("This building can not be built in Europe.", self.global_manager)
                else:
                    if self.building_type == 'infrastructure': #if railroad
                        text_tools.print_to_screen("This tile already contains a railroad.", self.global_manager)
                    else:
                        text_tools.print_to_screen("This tile already contains a " + self.building_type + " building.", self.global_manager)
            else:
                text_tools.print_to_screen("You do not have enough movement points to construct a building.", self.global_manager)
                text_tools.print_to_screen("You have " + str(self.attached_mob.movement_points) + " movement points while 1 is required.", self.global_manager)
                    
            
    def construct(self):
        '''
        Description:
            Commands the selected mob to construct a certain type of building, depending on this button's building_type
        Input:
            None
        Output:
            None
        '''
        self.attached_mob.set_movement_points(0)
        if not self.attached_mob.images[0].current_cell.contained_buildings[self.building_type] == 'none': #if building of same type exists, remove it and replace with new one
            self.attached_mob.images[0].current_cell.contained_buildings[self.building_type].remove()
        if self.building_type == 'resource':
            new_building = buildings.resource_building((self.attached_mob.x, self.attached_mob.y), self.attached_mob.grids, self.global_manager.get('resource_building_dict')[self.attached_resource], self.building_name, self.attached_resource,
                ['strategic'], self.global_manager)
        elif self.building_type == 'port':
            new_building = buildings.port((self.attached_mob.x, self.attached_mob.y), self.attached_mob.grids, 'buildings/port.png', self.building_name, ['strategic'], self.global_manager)
        elif self.building_type == 'train_station':
            new_building = buildings.train_station((self.attached_mob.x, self.attached_mob.y), self.attached_mob.grids, 'buildings/train_station.png', self.building_name, ['strategic'], self.global_manager)
        elif self.building_type == 'infrastructure':
            building_image_id = 'none'
            if self.building_name == 'road':
                building_image_id = 'buildings/infrastructure/road.png'
            elif self.building_name == 'railroad':
                building_image_id = 'buildings/infrastructure/railroad.png'
            new_building = buildings.infrastructure_building((self.attached_mob.x, self.attached_mob.y), self.attached_mob.grids, building_image_id, self.building_name, self.building_name,
                ['strategic'], self.global_manager) #coordinates, grids, image_id, name, infrastructure_type, modes, global_manager
        elif self.building_type == 'trading_post':
            new_building = buildings.trading_post((self.attached_mob.x, self.attached_mob.y), self.attached_mob.grids, 'buildings/trading_post.png', self.building_name, ['strategic'], self.global_manager)
        elif self.building_type == 'mission':
            new_building = buildings.mission((self.attached_mob.x, self.attached_mob.y), self.attached_mob.grids, 'buildings/mission.png', self.building_name, ['strategic'], self.global_manager)
        else:
            new_building = buildings.building((self.attached_mob.x, self.attached_mob.y), self.attached_mob.grids, 'buildings/port.png', self.building_name, self.building_type,
                ['strategic'], self.global_manager)
        actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), self.attached_mob.images[0].current_cell.tile)
