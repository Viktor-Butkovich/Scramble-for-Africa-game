#Contains functionality for actor display labels

import pygame

from ..labels import label
from ..images import minister_type_image
from . import buttons
from . import images

class actor_display_label(label):
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
        #height += 5
        message = ''
        self.attached_buttons = []
        self.attached_images = []
        self.actor = 'none'
        self.actor_label_type = actor_label_type #name, terrain, resource, etc
        self.actor_type = actor_type #mob or tile, none if does not scale with shown labels, like tooltip labels
        self.image_y_displacement = 0
        super().__init__(coordinates, minimum_width, height, modes, image_id, message, global_manager)
        #all labels in a certain ordered label list will be placed in order on the side of the screen when the correct type of actor/minister is selected
        if not self.actor_label_type in ['tooltip', 'commodity', 'mob inventory capacity', 'tile inventory capacity']: #certain types of labels, like inventory capacity, are not ordered on the side of the screen and stay at set positions
            self.global_manager.get(self.actor_type + '_ordered_label_list').append(self) #like mob_ordered_label_list
        if self.actor_label_type == 'name':
            self.message_start = 'Name: '
            self.attached_buttons.append(buttons.merge_button((self.x, self.y), self.height + 6, self.height + 6, pygame.K_m, self.modes, 'buttons/merge_button.png', self, global_manager))
            self.attached_buttons.append(buttons.split_button((self.x, self.y), self.height + 6, self.height + 6, pygame.K_n, self.modes, 'buttons/split_button.png', self, global_manager))
            self.attached_buttons.append(buttons.embark_vehicle_button((self.x, self.y), self.height + 6, self.height + 6, pygame.K_b, self.modes, 'buttons/embark_ship_button.png', self, 'ship', global_manager))
            self.attached_buttons.append(buttons.embark_vehicle_button((self.x, self.y), self.height + 6, self.height + 6, pygame.K_b, self.modes, 'buttons/embark_train_button.png', self, 'train', global_manager))
            self.attached_buttons.append(buttons.worker_crew_vehicle_button((self.x, self.y), self.height + 6, self.height + 6, pygame.K_m, self.modes, 'buttons/crew_ship_button.png', self, 'ship', global_manager))
            self.attached_buttons.append(buttons.worker_crew_vehicle_button((self.x, self.y), self.height + 6, self.height + 6, pygame.K_m, self.modes, 'buttons/crew_train_button.png', self, 'train', global_manager))
            self.attached_buttons.append(buttons.work_crew_to_building_button((self.x, self.y), self.height + 6, self.height + 6, pygame.K_f, 'resource', self.modes, 'buttons/work_crew_to_building_button.png', self, global_manager))
            self.attached_buttons.append(buttons.switch_theatre_button((self.x, self.y), self.height + 6, self.height + 6, pygame.K_g, self.modes, 'buttons/switch_theatre_button.png', self, global_manager))
            self.attached_buttons.append(buttons.construction_button((self.x, self.y), self.height + 6, self.height + 6, pygame.K_f, self.modes, self, 'resource', global_manager))
            self.attached_buttons.append(buttons.upgrade_button((self.x, self.y), self.height, self.height + 6, pygame.K_k, self.modes, self, 'resource', 'scale', global_manager))
            self.attached_buttons.append(buttons.upgrade_button((self.x, self.y), self.height, self.height + 6, pygame.K_l, self.modes, self, 'resource', 'efficiency', global_manager))
            self.attached_buttons.append(buttons.construction_button((self.x, self.y), self.height + 6, self.height + 6, pygame.K_p, self.modes, self, 'port', global_manager))
            self.attached_buttons.append(buttons.construction_button((self.x, self.y), self.height + 6, self.height + 6, pygame.K_r, self.modes, self, 'infrastructure', global_manager))
            self.attached_buttons.append(buttons.construction_button((self.x, self.y), self.height + 6, self.height + 6, pygame.K_t, self.modes, self, 'train_station', global_manager))
            self.attached_buttons.append(buttons.construction_button((self.x, self.y), self.height + 6, self.height + 6, pygame.K_y, self.modes, self, 'trading_post', global_manager))
            self.attached_buttons.append(buttons.construction_button((self.x, self.y), self.height + 6, self.height + 6, pygame.K_y, self.modes, self, 'mission', global_manager))
            self.attached_buttons.append(buttons.build_train_button((self.x, self.y), self.height + 6, self.height + 6, pygame.K_y, self.modes, 'buttons/build_train_button.png', self, global_manager))
            self.attached_buttons.append(buttons.trade_button((self.x, self.y), self.height + 6, self.height + 6, pygame.K_r, self.modes, 'buttons/trade_button.png', self, global_manager))
            self.attached_buttons.append(buttons.convert_button((self.x, self.y), self.height + 6, self.height + 6, pygame.K_t, self.modes, 'buttons/convert_button.png', self, global_manager))
            self.attached_buttons.append(buttons.religious_campaign_button((self.x, self.y), self.height + 6, self.height + 6, pygame.K_t, self.modes, 'buttons/religious_campaign_button.png', self, global_manager))
            self.attached_buttons.append(buttons.advertising_campaign_button((self.x, self.y), self.height + 6, self.height + 6, pygame.K_t, self.modes, 'ministers/icons/trade.png', self, global_manager))
        elif self.actor_label_type == 'movement':
            self.message_start = 'Movement points: '
        elif self.actor_label_type == 'building workers':
            self.message_start = 'Work crews: '
            self.attached_buttons.append(buttons.cycle_work_crews_button((self.x, self.y), self.height + 6, self.height + 6, 'none', self.modes, 'buttons/cycle_passengers_down.png', self, global_manager))
        elif self.actor_label_type == 'building worker':
            self.message_start = ''
            self.attached_building = 'none'
            self.attached_buttons.append(buttons.remove_work_crew_button((self.x, self.y), self.height + 6, self.height + 6, 'none', self.modes, 'buttons/remove_work_crew_button.png', self, 'resource', global_manager))
        elif self.actor_label_type == 'crew':
            self.message_start = 'Crew: '
            self.attached_buttons.append(buttons.crew_vehicle_button((self.x, self.y), self.height + 6, self.height + 6, pygame.K_m, self.modes, 'buttons/crew_ship_button.png', self, global_manager))
            self.attached_buttons.append(buttons.uncrew_vehicle_button((self.x, self.y), self.height + 6, self.height + 6, pygame.K_n, self.modes, 'buttons/uncrew_ship_button.png', self, global_manager))
        elif self.actor_label_type == 'passengers':
            self.message_start = 'Passengers: '
            self.attached_buttons.append(buttons.cycle_passengers_button((self.x, self.y), self.height + 6, self.height + 6, pygame.K_4, self.modes, 'buttons/cycle_passengers_down.png', self, global_manager))
            self.attached_buttons.append(buttons.pick_up_all_passengers_button((self.x, self.y), self.height + 6, self.height + 6, pygame.K_z, self.modes, 'buttons/embark_ship_button.png', self, global_manager))
        elif self.actor_label_type == 'current passenger':
            self.message_start = ''
            keybind = 'none'
            if self.list_index == 0:
                keybind = pygame.K_1
            elif self.list_index == 1:
                keybind = pygame.K_2
            elif self.list_index == 2:
                keybind = pygame.K_3
            self.attached_buttons.append(buttons.disembark_vehicle_button((self.x, self.y), self.height + 6, self.height + 6, keybind, self.modes, 'buttons/disembark_ship_button.png', self, global_manager))
        elif self.actor_label_type == 'tooltip':
            self.message_start = ''
        elif self.actor_label_type == 'native aggressiveness':
            self.message_start = 'Aggressiveness: '
        elif self.actor_label_type == 'native population':
            self.message_start = 'Total population: '
        elif self.actor_label_type == 'native available workers':
            self.message_start = 'Available workers: '
            self.attached_buttons.append(buttons.hire_village_workers_button((self.x, self.y), self.height + 30, self.height + 30, 'none', self.modes, 'mobs/African worker/button.png', self, global_manager))
        elif self.actor_label_type in ['mob inventory capacity', 'tile inventory capacity']:
            self.message_start = 'Inventory: '
        elif self.actor_label_type == 'terrain':
            self.message_start = 'Terrain: '
            self.attached_buttons.append(buttons.buy_slaves_button((self.x, self.y), self.height + 30, self.height + 30, 'none', self.modes, 'mobs/slave worker/button.png', self, global_manager))
        elif self.actor_label_type == 'minister':
            self.message_start = 'Minister: '
            self.attached_images.append(minister_type_image((self.x - self.height - 10, self.y), self.height + 10, self.height + 10, self.modes, 'none', self, global_manager))
            self.image_y_displacement = 5
        elif self.actor_label_type == 'minister_name':
            self.message_start = 'Name: '
        elif self.actor_label_type == 'minister_office':
            self.message_start = 'Office: '
            self.attached_buttons.append(buttons.remove_minister_button((self.x, self.y), self.height + 6, self.height + 6, self, global_manager))
            for current_position in global_manager.get('minister_types'):
                self.attached_buttons.append(buttons.appoint_minister_button((self.x, self.y), self.height + 6, self.height + 6, self, current_position, global_manager))
        else:
            self.message_start = self.actor_label_type.capitalize() + ': ' #'worker' -> 'Worker: '
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
                        name_list.append("    " + current_passenger.name.capitalize())
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
                if self.actor.actor_type == 'tile': #show tooltips of buildings in tile
                    for current_building in self.actor.cell.get_buildings():
                        current_building.update_tooltip()
                        tooltip_text.append('')
                        tooltip_text += current_building.tooltip_text  
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
        elif self.actor_label_type == 'minister':
            tooltip_text = []
            if not self.actor == 'none':
                self.actor.update_tooltip()
                if not self.actor.controlling_minister == 'none':
                    tooltip_text = self.actor.controlling_minister.tooltip_text
                else:
                    tooltip_text = ["The " + self.actor.controlling_minister_type + " is responsible for controlling this unit.",
                                    "As there is currently no " + self.actor.controlling_minister_type + ", this unit will not be able to complete most actions until one is appointed."]
            self.set_tooltip(tooltip_text)
        elif self.actor_label_type == 'building workers':
            tooltip_text = [self.message]
            tooltip_text.append("Increase work crew capacity by upgrading the building's scale with a construction gang.")
            if (not self.attached_building == 'none'):
                tooltip_text.append("Work crews: ")
                for current_work_crew in self.attached_building.contained_work_crews:
                    tooltip_text.append("    " + current_work_crew.name.capitalize())
                if len(self.attached_building.contained_work_crews) == 0:
                    tooltip_text[-1] += 'none'
            self.set_tooltip(tooltip_text)
        elif self.actor_label_type == 'building efficiency':
            tooltip_text = [self.message]
            tooltip_text.append("Each work crew attached to this building can produce up to the building efficiency in commodities each turn.")
            tooltip_text.append("Increase work crew efficiency by upgrading the building's efficiency with a construction gang.")
            self.set_tooltip(tooltip_text)
        else:
            super().update_tooltip()

    def calibrate(self, new_actor):
        '''
        Description:
            Attaches this label to the inputted actor and updates this label's information based on the inputted actor
        Input:
            string/actor new_actor: The displayed actor whose information is matched by this label. If this equals 'none', the label does not match any actors.
        Output:
            None
        '''
        self.actor = new_actor
        if not new_actor == 'none':
            if self.actor_label_type == 'name':
                self.set_label(self.message_start + new_actor.name.capitalize())
            elif self.actor_label_type == 'terrain':
                if new_actor.grid.is_abstract_grid:
                    self.set_label(new_actor.grid.name.capitalize())
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
                        self.attached_list = self.attached_building.contained_work_crews
                        if len(self.attached_list) > self.list_index:
                            self.set_label(self.message_start + self.attached_list[self.list_index].name.capitalize())
                    else:
                        self.attached_building = 'none'
                        self.attached_list = []
                        
            elif self.actor_label_type == 'crew':
                if self.actor.is_vehicle:
                    if self.actor.has_crew:
                        self.set_label(self.message_start + self.actor.crew.name.capitalize())
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
                            self.set_label(self.message_start + self.attached_list[self.list_index].name.capitalize())

            elif self.actor_label_type in ['worker', 'officer']:
                if self.actor.is_group:
                    if self.actor_label_type == 'worker':
                        self.set_label(self.message_start + str(self.actor.worker.name.capitalize()))
                    else:
                        self.set_label(self.message_start + str(self.actor.officer.name.capitalize()))
            
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
            elif self.actor_label_type == 'minister':
                if not self.actor.controlling_minister == 'none':
                    self.set_label(self.message_start + self.actor.controlling_minister.name)
                self.attached_images[0].calibrate(self.actor.controlling_minister)
            elif self.actor_label_type == 'minister_name':
                self.set_label(self.message_start + new_actor.name)
            elif self.actor_label_type == 'minister_office':
                self.set_label(self.message_start + new_actor.current_position)
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
            current_button.set_y(self)
        for current_image in self.attached_images:
            current_image.set_y(self)

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
        elif self.actor_label_type in ['worker', 'officer'] and not self.actor.is_group:
            return(False)
        elif self.actor.actor_type == 'mob' and (self.actor.in_vehicle or self.actor.in_group or self.actor.in_building): #do not show mobs that are attached to another unit/building
            return(False)
        else:
            return(result)

class list_item_label(actor_display_label):
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

class building_work_crews_label(actor_display_label):
    '''
    Label at the top of the list of work crews in a building that shows how many work crews are in it
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
        self.remove_work_crew_button = 'none'
        self.showing = False
        self.attached_building = 'none'
        super().__init__(coordinates, minimum_width, height, modes, image_id, 'building workers', actor_type, global_manager)
        self.building_type = building_type
        #self.showing = False

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
                self.set_label(self.message_start + str(len(self.attached_building.contained_work_crews)) + '/' + str(self.attached_building.scale))
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

class building_efficiency_label(actor_display_label):
    '''
    Label that shows a production building's efficiency, which is the number of attempts work crews at the building have to produce commodities
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
        self.remove_work_crew_button = 'none'
        self.showing = False
        super().__init__(coordinates, minimum_width, height, modes, image_id, 'building efficiency', actor_type, global_manager)
        self.building_type = building_type
        self.attached_building = 'none'
        #self.showing = False

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
                self.set_label("Efficiency: " + str(self.attached_building.efficiency))
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

class native_info_label(actor_display_label): #possible actor_label_types: native aggressiveness, native population, native available workers
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
        

class commodity_display_label(actor_display_label):
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
        self.commodity_image = images.label_image((self.x - self.height, self.y), self.height, self.height, self.modes, self, self.global_manager) #self, coordinates, width, height, modes, attached_label, global_manager
        if matched_actor_type == 'mob':
            self.attached_buttons.append(buttons.label_button((self.x, self.y), self.height, self.height, 'drop commodity', 'none', self.modes, 'buttons/commodity_drop_button.png', self, global_manager))
            self.attached_buttons.append(buttons.label_button((self.x + (self.height + 6), self.y), self.height, self.height, 'drop all commodity', 'none', self.modes, 'buttons/commodity_drop_all_button.png', self,
                global_manager))
        elif matched_actor_type == 'tile':
            self.attached_buttons.append(buttons.label_button((self.x, self.y), self.height, self.height, 'pick up commodity', 'none', self.modes, 'buttons/commodity_pick_up_button.png', self, global_manager))
            self.attached_buttons.append(buttons.label_button((self.x + (self.height + 6), self.y), self.height, self.height, 'pick up all commodity', 'none', self.modes, 'buttons/commodity_pick_up_all_button.png',
                self, global_manager))
            self.attached_buttons.append(buttons.label_button((self.x + ((self.height + 6) * 2), self.y), self.height, self.height, 'sell commodity', 'none', ['europe'], 'buttons/commodity_sell_button.png', self,
                global_manager))
            self.attached_buttons.append(buttons.label_button((self.x + ((self.height + 6) * 3), self.y), self.height, self.height, 'sell all commodity', 'none', ['europe'], 'buttons/commodity_sell_all_button.png', self,
                global_manager))

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


