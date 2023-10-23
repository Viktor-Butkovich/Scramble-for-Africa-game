#Contains functionality for actor display buttons

import random
from ..interface_types.buttons import button
from ..util import main_loop_utility, utility, actor_utility, minister_utility, trial_utility, text_utility, game_transitions
import modules.constants.constants as constants
import modules.constants.status as status
import modules.constants.flags as flags

class embark_all_passengers_button(button):
    '''
    Button that commands a vehicle to take all other mobs in its tile as passengers
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.vehicle_type = 'none'
        input_dict['button_type'] = 'embark all'
        super().__init__(input_dict, global_manager)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a vehicle to take all other mobs in its tile as passengers
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            vehicle = status.displayed_mob
            can_embark = True
            if self.vehicle_type == 'train':
                if vehicle.images[0].current_cell.contained_buildings['train_station'] == 'none':
                    text_utility.print_to_screen('A train can only pick up passengers at a train station.', self.global_manager)
                    can_embark = False
            if can_embark:
                if vehicle.sentry_mode:
                    vehicle.set_sentry_mode(False)
                for contained_mob in vehicle.images[0].current_cell.contained_mobs:
                    passenger = contained_mob
                    if passenger.is_pmob and not passenger.is_vehicle: #vehicles and enemies won't be picked up as passengers
                        passenger.embark_vehicle(vehicle)
                constants.sound_manager.play_sound('voices/all aboard ' + str(random.randrange(1, 4)))
        else:
            text_utility.print_to_screen('You are busy and cannot embark all passengers.', self.global_manager)

    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn. Also updates this button to reflect a train or ship depending on the selected vehicle
        Input:
            None
        Output:
            boolean: Returns False if the selected vehicle has no crew, otherwise returns same as superclass
        '''
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            displayed_mob = status.displayed_mob
            if not displayed_mob.has_crew: #do not show if ship does not have crew
                return(False)
            if (not self.vehicle_type == displayed_mob.vehicle_type) and (not displayed_mob.vehicle_type == 'vehicle'): #update vehicle type and image when shown if type has changed, like train to ship
                self.vehicle_type = displayed_mob.vehicle_type
                self.image.set_image('buttons/embark_' + self.vehicle_type + '_button.png')
        return(result)

class disembark_all_passengers_button(button):
    '''
    Button that commands a vehicle to eject all of its passengers
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.vehicle_type = 'none'
        input_dict['button_type'] = 'disembark all'
        super().__init__(input_dict, global_manager)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a vehicle to eject all of its passengers
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            vehicle = status.displayed_mob
            can_disembark = True
            if self.vehicle_type == 'train':
                if vehicle.images[0].current_cell.contained_buildings['train_station'] == 'none':
                    text_utility.print_to_screen('A train can only drop off passengers at a train station.', self.global_manager)
                    can_disembark = False
            if can_disembark:
                if vehicle.sentry_mode:
                    vehicle.set_sentry_mode(False)
                if len(vehicle.contained_mobs) > 0:
                    vehicle.contained_mobs[-1].selection_sound()
                vehicle.eject_passengers()
        else:
            text_utility.print_to_screen('You are busy and cannot disembark all passengers.', self.global_manager)

    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn. Also updates this button to reflect a train or ship depending on the selected vehicle
        Input:
            None
        Output:
            boolean: Returns False if the selected vehicle has no crew, otherwise returns same as superclass
        '''
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            vehicle = status.displayed_mob
            if not vehicle.has_crew: #do not show if ship does not have crew
                return(False)
            if (not self.vehicle_type == vehicle.vehicle_type) and (not vehicle.vehicle_type == 'vehicle'): #update vehicle type and image when shown if type has changed, like train to ship
                self.vehicle_type = vehicle.vehicle_type
                self.image.set_image('buttons/disembark_' + self.vehicle_type + '_button.png')
        return(result)

class enable_sentry_mode_button(button):
    '''
    Button that enables sentry mode for a unit, causing it to not be added to the turn cycle queue
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['button_type'] = 'enable sentry mode'
        super().__init__(input_dict, global_manager)
        
    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns True if the selected mob is a pmob and is not already in sentry mode, otherwise returns False
        '''
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            displayed_mob = status.displayed_mob
            if not displayed_mob.is_pmob:
                return(False)
            elif displayed_mob.sentry_mode:
                return(False)
        return(result)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button activates sentry mode for the selected unit
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):   
            displayed_mob = status.displayed_mob      
            displayed_mob.set_sentry_mode(True)
            if (constants.effect_manager.effect_active('promote_on_sentry') 
            and (displayed_mob.is_group or displayed_mob.is_officer) 
            and not displayed_mob.veteran): #purely for promotion testing, not normal functionality
                displayed_mob.promote()
        else:
            text_utility.print_to_screen('You are busy and cannot enable sentry mode.', self.global_manager)

class disable_sentry_mode_button(button):
    '''
    Button that disables sentry mode for a unit, causing it to not be added to the turn cycle queue
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['button_type'] = 'disable sentry mode'
        super().__init__(input_dict, global_manager)
        
    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns True if the selected mob is a pmob and is in sentry mode, otherwise returns False
        '''
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            displayed_mob = status.displayed_mob
            if not displayed_mob.is_pmob:
                return(False)
            elif not displayed_mob.sentry_mode:
                return(False)
        return(result)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button deactivates sentry mode for the selected unit
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            displayed_mob = status.displayed_mob     
            displayed_mob.set_sentry_mode(False)
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display'), displayed_mob)
        else:
            text_utility.print_to_screen('You are busy and cannot disable sentry mode.', self.global_manager)

class enable_automatic_replacement_button(button):
    '''
    Button that enables automatic attrition replacement for a unit or one of its components
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'target_type': string value - Type of unit/subunit targeted by this button, such as 'unit', 'officer', or 'worker'
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.target_type = input_dict['target_type']
        input_dict['button_type'] = 'enable automatic replacement'
        super().__init__(input_dict, global_manager)
        
    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns True if the targeted unit component is present and does not already have automatic replacement, otherwise returns False
        '''
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            displayed_mob = status.displayed_mob
            if not displayed_mob.is_pmob:
                return(False)
            elif displayed_mob.is_vehicle:
                return(False)
            elif displayed_mob.is_group and self.target_type == 'unit':
                return(False)
            elif (not displayed_mob.is_group) and (not self.target_type == 'unit'):
                return(False)
            elif ((self.target_type == 'unit' and displayed_mob.automatically_replace) or 
                (self.target_type == 'worker' and displayed_mob.worker.automatically_replace) or 
                (self.target_type == 'officer' and displayed_mob.officer.automatically_replace)):
                return(False)
        return(result)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button enables automatic replacement for the selected unit
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):     
            displayed_mob = status.displayed_mob    
            if self.target_type == 'unit':
                target = displayed_mob
            elif self.target_type == 'worker':
                target = displayed_mob.worker
            elif self.target_type == 'officer':
                target = displayed_mob.officer         
            target.set_automatically_replace(True)
        else:
            text_utility.print_to_screen('You are busy and cannot enable automatic replacement.', self.global_manager)

class disable_automatic_replacement_button(button):
    '''
    Button that disables automatic attrition replacement for a unit or one of its components
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'target_type': string value - Type of unit/subunit targeted by this button, such as 'unit', 'officer', or 'worker'
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.target_type = input_dict['target_type']
        input_dict['button_type'] = 'disable automatic replacement'
        super().__init__(input_dict, global_manager)
        
    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns True if the targeted unit component is present and has automatic replacement, otherwise returns False
        '''
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            displayed_mob = status.displayed_mob
            if not displayed_mob.is_pmob:
                return(False)
            elif displayed_mob.is_vehicle:
                return(False)
            elif displayed_mob.is_group and self.target_type == 'unit':
                return(False)
            elif (not displayed_mob.is_group) and (not self.target_type == 'unit'):
                return(False)
            elif ((self.target_type == 'unit' and not displayed_mob.automatically_replace) or 
                (self.target_type == 'worker' and not displayed_mob.worker.automatically_replace) or 
                (self.target_type == 'officer' and not displayed_mob.officer.automatically_replace)):
                return(False)
        return(result)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button disables automatic replacement for the selected unit
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            displayed_mob = status.displayed_mob
            if self.target_type == 'unit':
                target = displayed_mob
            elif self.target_type == 'worker':
                target = displayed_mob.worker
            elif self.target_type == 'officer':
                target = displayed_mob.officer         
            target.set_automatically_replace(False)
        else:
            text_utility.print_to_screen('You are busy and cannot disable automatic replacement.', self.global_manager)

class end_unit_turn_button(button):
    '''
    Button that ends a unit's turn, removing it from the current turn's turn cycle queue
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['button_type'] = 'end unit turn'
        super().__init__(input_dict, global_manager)
        
    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns True if the selected mob is a pmob in the turn queue, otherwise returns False
        '''
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            displayed_mob = status.displayed_mob
            if not displayed_mob.is_pmob:
                return(False)
            elif not displayed_mob in status.player_turn_queue:
                return(False)
        return(result)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button removes the selected unit from the current turn's turn cycle queue
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            status.displayed_mob.remove_from_turn_queue()
            game_transitions.cycle_player_turn(self.global_manager)
        else:
            text_utility.print_to_screen('You are busy and cannot end this unit\'s turn.', self.global_manager)

class remove_work_crew_button(button):
    '''
    Button that removes a work crew from a building
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'attached_label': label value - Label that this button is attached to
                'building_type': Type of building to remove workers from, like 'resource building'
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.building_type = input_dict['building_type']
        input_dict['button_type'] = 'remove worker'
        super().__init__(input_dict, global_manager)
        
    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if there is not a corresponding work crew to remove, otherwise returns same as superclass
        '''
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            if not self.attached_label.attached_list[self.attached_label.list_index].in_building:
                return(False)
        return(result)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button removes a work crew from a building
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):         
            self.attached_label.attached_list[self.attached_label.list_index].leave_building(self.attached_label.actor.cell.contained_buildings[self.building_type])
        else:
            text_utility.print_to_screen('You are busy and cannot remove a work crew from a building.', self.global_manager)

class disembark_vehicle_button(button):
    '''
    Button that disembarks a passenger from a vehicle
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'attached_label': label value - Label that this button is attached to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.vehicle_type = 'none'
        input_dict['button_type'] = 'disembark'
        super().__init__(input_dict, global_manager)
        
    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn. Also updates this button to reflect a train or ship depending on the selected vehicle
        Input:
            None
        Output:
            boolean: Returns False if there is not a corresponding passenger to disembark, otherwise returns same as superclass
        '''
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            if not self.attached_label.attached_list[self.attached_label.list_index].in_vehicle:
                return(False)
            old_vehicle_type = self.vehicle_type
            self.vehicle_type = self.attached_label.actor.vehicle_type
            if not self.vehicle_type == old_vehicle_type and not self.vehicle_type == 'none': #if changed
                self.image.set_image('buttons/disembark_' + self.vehicle_type + '_button.png')
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
        if main_loop_utility.action_possible(self.global_manager):         
            if len(self.attached_label.actor.contained_mobs) > 0:
                can_disembark = True
                if self.vehicle_type == 'train':
                    if self.attached_label.actor.images[0].current_cell.contained_buildings['train_station'] == 'none':
                        text_utility.print_to_screen('A train can only drop off passengers at a train station.', self.global_manager)
                        can_disembark = False
                if can_disembark:
                    passenger = self.attached_label.attached_list[self.attached_label.list_index]
                    if passenger.sentry_mode:
                        passenger.set_sentry_mode(False)
                    passenger.selection_sound()
                    self.attached_label.attached_list[self.attached_label.list_index].disembark_vehicle(self.attached_label.actor)
            else:
                text_utility.print_to_screen('You must select a ' + self.vehicle_type + 'with passengers to disembark passengers.', self.global_manager)
        else:
            text_utility.print_to_screen('You are busy and cannot disembark from a ' + self.vehicle_type + '.', self.global_manager)

class embark_vehicle_button(button):
    '''
    Button that commands a selected mob to embark a vehicle of the correct type in the same tile
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'vehicle_type': string value - Type of vehicle this button embarks, like 'train' or 'ship'
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.vehicle_type = input_dict['vehicle_type']
        self.was_showing = False
        input_dict['button_type'] = 'embark'
        super().__init__(input_dict, global_manager)
        
    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob cannot embark vehicles or if there is no vehicle in the tile to embark, otherwise returns same as superclass
        '''
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            displayed_mob = status.displayed_mob
            if not displayed_mob.is_pmob:
                result = False
            elif displayed_mob.in_vehicle or displayed_mob.is_vehicle:
                result = False
            elif not displayed_mob.actor_type == 'minister' and not displayed_mob.images[0].current_cell.has_vehicle(self.vehicle_type):
                result = False
        if not result == self.was_showing: #if visibility changes, update actor info display
            self.was_showing = result
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display'), displayed_mob)
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
        if main_loop_utility.action_possible(self.global_manager):
            displayed_mob = status.displayed_mob
            if displayed_mob.images[0].current_cell.has_vehicle(self.vehicle_type):
                vehicle = displayed_mob.images[0].current_cell.get_vehicle(self.vehicle_type)
                rider = displayed_mob
                can_embark = True
                if vehicle.vehicle_type == 'train':
                    if vehicle.images[0].current_cell.contained_buildings['train_station'] == 'none':
                        text_utility.print_to_screen('A train can only pick up passengers at a train station.', self.global_manager)
                        can_embark = False
                if can_embark:
                    if rider.sentry_mode:
                        rider.set_sentry_mode(False)
                    if vehicle.sentry_mode:
                        vehicle.set_sentry_mode(False)
                    rider.embark_vehicle(vehicle)
                    constants.sound_manager.play_sound('voices/all aboard ' + str(random.randrange(1, 4)))
            else:
                text_utility.print_to_screen('You must select a unit in the same tile as a crewed ' + self.vehicle_type + ' to embark.', self.global_manager)
        else:
            text_utility.print_to_screen('You are busy and cannot embark a ' + self.vehicle_type + '.', self.global_manager)

class cycle_passengers_button(button):
    '''
    Button that cycles the order of passengers displayed in a vehicle
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.vehicle_type = 'none'
        input_dict['button_type'] = 'cycle passengers'
        super().__init__(input_dict, global_manager)
        
    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not a vehicle or if the vehicle does not have enough passengers to cycle through, otherwise returns same as superclass
        '''
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            displayed_mob = status.displayed_mob
            if not displayed_mob.is_vehicle:
                return(False)
            elif not len(displayed_mob.contained_mobs) > 3: #only show if vehicle with 3+ passengers
                return(False)
            self.vehicle_type = displayed_mob.vehicle_type
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
        if main_loop_utility.action_possible(self.global_manager):
            displayed_mob = status.displayed_mob
            moved_mob = displayed_mob.contained_mobs.pop(0)
            displayed_mob.contained_mobs.append(moved_mob)
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display'), displayed_mob) #updates mob info display list to show changed passenger order
        else:
            text_utility.print_to_screen('You are busy and cannot cycle passengers.', self.global_manager)

class cycle_work_crews_button(button):
    '''
    Button that cycles the order of work crews in a building
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'attached_label': label value - Label that this button is attached to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.previous_showing_result = False
        input_dict['button_type'] = 'cycle work crews'
        super().__init__(input_dict, global_manager)
        
    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns same as superclass if the displayed tile's cell has a resource building containing more than 3 work crews, otherwise returns False
        '''
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            displayed_tile = status.displayed_tile
            if displayed_tile.cell.contained_buildings['resource'] == 'none':
                self.previous_showing_result = False
                return(False)
            elif not len(displayed_tile.cell.contained_buildings['resource'].contained_work_crews) > 3: #only show if building with 3+ work crews
                self.previous_showing_result = False
                return(False)
        if self.previous_showing_result == False and result == True:
            self.previous_showing_result = result
            self.attached_label.set_label(self.attached_label.message) #update label to update this button's location
        self.previous_showing_result = result
        return(result)
    
    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button cycles the order of work crews displayed in a building
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            displayed_tile = status.displayed_tile
            moved_mob = displayed_tile.cell.contained_buildings['resource'].contained_work_crews.pop(0)
            displayed_tile.cell.contained_buildings['resource'].contained_work_crews.append(moved_mob)
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display'), displayed_tile) #updates tile info display list to show changed work crew order
        else:
            text_utility.print_to_screen('You are busy and cannot cycle work crews.', self.global_manager)

class work_crew_to_building_button(button):
    '''
    Button that commands a work crew to work in a certain type of building in its tile
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'building_type': string value - Type of buliding this button attaches workers to, like 'resource building'
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.building_type = input_dict['building_type']
        self.attached_work_crew = None
        self.attached_building = None
        input_dict['button_type'] = 'worker to resource'
        super().__init__(input_dict, global_manager)

    def update_info(self):
        '''
        Description:
            Updates the building this button assigns workers to depending on the buildings present in this tile
        Input:
            None
        Output:
            None
        '''
        self.attached_work_crew = status.displayed_mob
        if self.attached_work_crew and self.attached_work_crew.is_work_crew:
            self.attached_building = self.attached_work_crew.images[0].current_cell.get_intact_building(self.building_type)
            if self.attached_building == 'none':
                self.attached_building = None
        else:
            self.attached_building = None
    
    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not a work crew, otherwise returns same as superclass
        '''
        self.update_info()
        return(super().can_show(skip_parent_collection=skip_parent_collection) and self.attached_work_crew and self.attached_work_crew.is_work_crew)
    
    def update_tooltip(self):
        '''
        Description:
            Sets this button's tooltip depending on the building it assigns workers to
        Input:
            None
        Output:
            None
        '''
        if self.attached_work_crew and self.attached_building:
            if self.building_type == 'resource':
                self.set_tooltip(['Assigns the selected work crew to the ' + self.attached_building.name + ', producing ' + self.attached_building.resource_type + ' over time.'])
            else:
                self.set_tooltip(['placeholder'])
        elif self.attached_work_crew:
            if self.building_type == 'resource':
                self.set_tooltip(['Assigns the selected work crew to a resource building, producing commodities over time.'])
        else:
            self.set_tooltip(['placeholder'])

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a work crew to work in a certain type of building in its tile
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            if self.attached_building:
                if self.attached_building.scale > len(self.attached_building.contained_work_crews): #if has extra space
                    if self.attached_work_crew.sentry_mode:
                        self.attached_work_crew.set_sentry_mode(False)
                    self.attached_work_crew.work_building(self.attached_building)
                else:
                    text_utility.print_to_screen('This building is at its work crew capacity.', self.global_manager)
                    text_utility.print_to_screen('Upgrade the building\'s scale to increase work crew capacity.', self.global_manager)
            else:
                text_utility.print_to_screen('This work crew must be in the same tile as a resource production building to work in it', self.global_manager)
        else:
            text_utility.print_to_screen('You are busy and cannot attach a work crew to a building.', self.global_manager)

class trade_button(button):
    '''
    Button that commands a caravan to trade with a village
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['button_type'] = 'trade'
        super().__init__(input_dict, global_manager)

    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not capable of trading, otherwise returns same as superclass
        '''
        return(super().can_show(skip_parent_collection=skip_parent_collection) and status.displayed_mob.can_trade)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a caravan to trade with a village
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            current_mob = status.displayed_mob
            if current_mob.movement_points >= 1:
                if constants.money >= constants.action_prices['trade']:
                    current_cell = current_mob.images[0].current_cell
                    if current_cell.has_building('village'):
                        if current_cell.get_building('village').population > 0:
                            if current_mob.get_inventory('consumer goods') > 0:
                                if minister_utility.positions_filled(self.global_manager):
                                    if current_mob.sentry_mode:
                                        current_mob.set_sentry_mode(False)
                                    current_mob.start_trade()
                                else:
                                    text_utility.print_to_screen('You cannot do any actions until all ministers have been appointed.', self.global_manager)
                            else:
                                text_utility.print_to_screen('Trading requires at least 1 unit of consumer goods.', self.global_manager)
                        else:
                            text_utility.print_to_screen('Trading is only possible in a village with population above 0.', self.global_manager)
                    else:
                        text_utility.print_to_screen('Trading is only possible in a village.', self.global_manager)
                else:
                    text_utility.print_to_screen('You do not have the ' + str(constants.action_prices['trade']) + ' money needed to trade with a village.', self.global_manager)
            else:
                text_utility.print_to_screen('Trading requires all remaining movement points, at least 1', self.global_manager)
        else:
            text_utility.print_to_screen('You are busy and cannot trade.', self.global_manager)

class rumor_search_button(button):
    '''
    Button that commands an expedition to search a village for rumors of the location of a lore mission artifact
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['button_type'] = 'rumor search'
        super().__init__(input_dict, global_manager)

    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not an expedition, otherwise returns same as superclass
        '''
        return(super().can_show(skip_parent_collection=skip_parent_collection) and status.displayed_mob.can_explore)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands missionaries to convert a native village
        Input:
            None
        Output:
            None
        '''
        if not self.global_manager.get('current_lore_mission') == 'none':
            if main_loop_utility.action_possible(self.global_manager):
                current_mob = status.displayed_mob
                if current_mob.movement_points >= 1:
                    if constants.money >= constants.action_prices['rumor_search']:
                        current_cell = current_mob.images[0].current_cell
                        if current_cell.has_building('village'):
                            if current_cell.get_building('village').population > 0:
                                if not self.global_manager.get('current_lore_mission').confirmed_all_locations_revealed:
                                    if not current_cell.get_building('village').found_rumors:
                                        if current_mob.ministers_appointed():
                                            if current_mob.sentry_mode:
                                                current_mob.set_sentry_mode(False)
                                            current_mob.start_rumor_search()
                                    else:
                                        text_utility.print_to_screen('This village\'s rumors regarding the location of the ' + self.global_manager.get('current_lore_mission').name + ' have already been found.', self.global_manager)
                                else:
                                    text_utility.print_to_screen('All possible locations of the ' + self.global_manager.get('current_lore_mission').name + ' have already been revealed.', self.global_manager)
                            else:
                                text_utility.print_to_screen('This village has no population and no rumors can be found.', self.global_manager)
                        else:
                            text_utility.print_to_screen('Searching for rumors is only possible in a village.', self.global_manager)
                    else:
                        text_utility.print_to_screen('You do not have the ' + str(constants.action_prices['rumor_search']) + ' money needed to attempt a rumor search.', self.global_manager)
                else:
                    text_utility.print_to_screen('A rumor search requires all remaining movement points, at least 1.', self.global_manager)
            else:
                text_utility.print_to_screen('You are busy and cannot search for rumors.', self.global_manager)
        else:
            text_utility.print_to_screen('There are no ongoing lore missions for which to find rumors.', self.global_manager)

class artifact_search_button(button):
    '''
    Button that commands an expedition to search a rumored location for a lore mission artifact
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['button_type'] = 'artifact search'
        super().__init__(input_dict, global_manager)

    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not an expedition, otherwise returns same as superclass
        '''
        return(super().can_show(skip_parent_collection=skip_parent_collection) and status.displayed_mob.can_explore)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands missionaries to convert a native village
        Input:
            None
        Output:
            None
        '''
        if self.global_manager.get('current_lore_mission') != 'none':
            if main_loop_utility.action_possible(self.global_manager):
                current_mob = status.displayed_mob
                if current_mob.movement_points >= 1:
                    if constants.money >= constants.action_prices['artifact_search']:
                        if self.global_manager.get('current_lore_mission').has_revealed_possible_artifact_location(current_mob.x, current_mob.y):
                            if current_mob.ministers_appointed():
                                if current_mob.sentry_mode:
                                    current_mob.set_sentry_mode(False)
                                current_mob.start_artifact_search()
                        else:
                            text_utility.print_to_screen('You have not found any rumors indicating that the ' + self.global_manager.get('current_lore_mission').name + ' may be at this location.', self.global_manager)
                    else:
                        text_utility.print_to_screen('You do not have the ' + str(constants.action_prices['artifact_search']) + ' money needed to attempt a artifact search.', self.global_manager)
                else:
                    text_utility.print_to_screen('An artifact search requires all remaining movement points, at least 1.', self.global_manager)
            else:
                text_utility.print_to_screen('You are busy and cannot search for artifact.', self.global_manager)
        else:
            text_utility.print_to_screen('There are no ongoing lore missions for which to find artifacts.', self.global_manager)

class capture_slaves_button(button):
    '''
    Button that commands a battalion to capture slaves from a village
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['button_type'] = 'capture slaves'
        super().__init__(input_dict, global_manager)

    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not a group of missionaries, otherwise returns same as superclass
        '''
        return(super().can_show(skip_parent_collection=skip_parent_collection) and status.displayed_mob.is_battalion)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a battalion to capture slaves from a native village
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            current_mob = status.displayed_mob
            if current_mob.movement_points >= 1:
                if constants.money >= constants.action_prices['slave_capture']:
                    current_cell = current_mob.images[0].current_cell
                    if current_cell.has_building('village'):
                        if current_cell.get_building('village').population > 0:
                            if current_mob.ministers_appointed():
                                if current_mob.sentry_mode:
                                    current_mob.set_sentry_mode(False)
                                current_mob.start_capture_slaves()
                        else:
                            text_utility.print_to_screen('This village has no remaining population to be captured.', self.global_manager)
                    else:
                        text_utility.print_to_screen('Capturing slaves is only possible in a village.', self.global_manager)
                else:
                    text_utility.print_to_screen('You do not have the ' + str(constants.action_prices['slave_capture']) + ' money needed to attempt to capture slaves.', self.global_manager)
            else:
                text_utility.print_to_screen('Capturing slaves requires all remaining movement points, at least 1.', self.global_manager)
        else:
            text_utility.print_to_screen('You are busy and cannot capture slaves.', self.global_manager)

class labor_broker_button(button):
    '''
    Buttons that commands a vehicle without crew or an officer to use a labor broker in a port to recruit a worker from a nearby village, with a price based on the village's aggressiveness and distance
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['button_type'] = 'labor broker'
        super().__init__(input_dict, global_manager)

    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not an officer, a steamship, or a non-steamship vehicle without crew, otherwise returns same as superclass
        '''
        if super().can_show(skip_parent_collection=skip_parent_collection):
            displayed_mob = status.displayed_mob
            if displayed_mob.is_officer and displayed_mob.officer_type != 'evangelist':
                return(True)
            elif displayed_mob.is_vehicle and not (displayed_mob.can_swim_ocean or displayed_mob.has_crew):
                return(True)
        return(False)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands an officer or vehicle without crew to use a labor broker in a port
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            current_mob = status.displayed_mob
            if status.strategic_map_grid in current_mob.grids:
                if current_mob.images[0].current_cell.has_intact_building('port'):
                    cost_info_list = self.get_cost()
                    if not cost_info_list == 'none':
                        if current_mob.movement_points >= 1:
                            if constants.money_tracker.get() >= cost_info_list[1]:
                                if current_mob.ministers_appointed():
                                    if current_mob.sentry_mode:
                                        current_mob.set_sentry_mode(False)
                                    choice_info_dict = {'recruitment_type': 'African worker labor broker', 'cost': cost_info_list[1], 'mob_image_id': 'mobs/African worker/default.png', 'type': 'recruitment',
                                        'source_type': 'labor broker', 'village': cost_info_list[0]}
                                    constants.actor_creation_manager.display_recruitment_choice_notification(choice_info_dict, 'African workers', self.global_manager)
                            else:
                                text_utility.print_to_screen('You cannot afford the recruitment cost of ' + str(cost_info_list[1]) + ' for the cheapest available worker. ', self.global_manager)
                        else:
                            text_utility.print_to_screen('Using a labor broker requires all remaining movement points, at least 1.', self.global_manager)
                    else:
                        text_utility.print_to_screen('There are no eligible villages to recruit workers from.', self.global_manager)
                else:
                    text_utility.print_to_screen('A labor broker can only be used at a port.', self.global_manager)
            else:
                text_utility.print_to_screen('A labor broker can only be used at a port.', self.global_manager)
        else:
            text_utility.print_to_screen('You are busy and cannot use a labor broker.', self.global_manager)

    def get_cost(self):
        '''
        Description:
            Calculates and returns the cost of using a labor broker in a port at the currently selected unit's location, based on nearby villages' aggressiveness and distance from the port
        Input:
            None
        Output:
            string/list: If no valid villages are found, returns 'none'. Otherwise, returns a list with the village as the first item and the cost as the second item
        '''
        lowest_cost_village = 'none'
        lowest_cost = 0
        for current_village in status.village_list:
            if current_village.population > 0:
                distance = int(utility.find_object_distance(current_village, status.displayed_mob))
                cost = (5 * current_village.aggressiveness) + distance
                if cost < lowest_cost or lowest_cost_village == 'none':
                    lowest_cost_village = current_village
                    lowest_cost = cost
        if lowest_cost_village == 'none':
            return('none')
        else:
            return([lowest_cost_village, lowest_cost])

class track_beasts_button(button):
    '''
    Button that orders a safari to spend 1 movement point to attempt to reveal beasts in its tile and adjacent explored tiles
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['button_type'] = 'track beasts'
        super().__init__(input_dict, global_manager)

    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not a safari, otherwise returns same as superclass
        '''
        return(super().can_show(skip_parent_collection=skip_parent_collection) and status.displayed_mob.is_group and status.displayed_mob.is_safari)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a safari to attempt to track beasts
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            current_mob = status.displayed_mob
            if status.strategic_map_grid in current_mob.grids:
                if current_mob.movement_points >= 1:
                    if constants.money >= constants.action_prices['track_beasts']:
                        if current_mob.ministers_appointed():
                            if current_mob.sentry_mode:
                                current_mob.set_sentry_mode(False)
                            current_mob.track_beasts()
                    else:
                        text_utility.print_to_screen('You do not have the ' + str(constants.action_prices['track_beasts']) + ' money needed to track beasts.', self.global_manager)
                else:
                    text_utility.print_to_screen('Tracking beasts requires 1 movement point.', self.global_manager)
            else:
                text_utility.print_to_screen('A safari can only track beasts in Africa', self.global_manager)
        else:
            text_utility.print_to_screen('You are busy and cannot track beasts.', self.global_manager)

class switch_theatre_button(button):
    '''
    Button starts choosing a destination for a ship to travel between theatres, like between Europe and Africa. A destination is chosen when the player clicks a tile in another theatre.
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['button_type'] = 'switch theatre'
        super().__init__(input_dict, global_manager)

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
        if main_loop_utility.action_possible(self.global_manager):
            current_mob = status.displayed_mob
            if current_mob.movement_points >= 1:
                if not (status.strategic_map_grid in current_mob.grids and (current_mob.y > 1 or (current_mob.y == 1 and not current_mob.images[0].current_cell.has_intact_building('port')))): #can leave if in ocean or if in coastal port
                    if current_mob.can_leave(): #not current_mob.grids[0] in self.destination_grids and
                        if current_mob.sentry_mode:
                            current_mob.set_sentry_mode(False)
                        if not constants.current_game_mode == 'strategic':
                            game_transitions.set_game_mode('strategic', self.global_manager)
                            current_mob.select()
                        current_mob.clear_automatic_route()
                        current_mob.end_turn_destination = 'none'
                        flags.choosing_destination = True
                else:
                    text_utility.print_to_screen('You are inland and cannot cross the ocean.', self.global_manager) 
            else:
                text_utility.print_to_screen('Crossing the ocean requires all remaining movement points, at least 1.', self.global_manager)
        else:
            text_utility.print_to_screen('You are busy and cannot move.', self.global_manager)

    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not capable of traveling between theatres, otherwise returns same as superclass
        '''
        return(super().can_show(skip_parent_collection=skip_parent_collection) and status.displayed_mob.is_pmob and status.displayed_mob.can_travel())

class appoint_minister_button(button):
    '''
    Button that appoints the selected minister to the office corresponding to this button
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'appoint_type': string value - Office appointed to by this button, like 'Minister of Trade'
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.appoint_type = input_dict['appoint_type']
        input_dict['button_type'] = 'appoint minister'
        input_dict['modes'] = ['ministers']
        input_dict['image_id'] = 'ministers/icons/' + global_manager.get('minister_type_dict')[self.appoint_type] + '.png'
        super().__init__(input_dict, global_manager)

    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns same as superclass if the minister office that this button is attached to is open, otherwise returns False
        '''
        if super().can_show(skip_parent_collection=skip_parent_collection):
            displayed_minister = status.displayed_minister
            if displayed_minister and displayed_minister.current_position == 'none': #if there is an available minister displayed
                if self.global_manager.get('current_ministers')[self.appoint_type] == 'none': #if the position that this button appoints is available
                    return(True)
        return(False)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button appoints the selected minister to the office corresponding to this button
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            appointed_minister = status.displayed_minister
            if not appointed_minister.just_removed:
                appointed_minister.respond('first hired')
            appointed_minister.appoint(self.appoint_type)
            minister_utility.calibrate_minister_info_display(self.global_manager, appointed_minister)
        else:
            text_utility.print_to_screen('You are busy and cannot appoint a minister.', self.global_manager)

class remove_minister_button(button):
    '''
    Button that removes the selected minister from their current office
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['button_type'] = 'remove minister'
        input_dict['modes'] = ['ministers']
        input_dict['image_id'] = 'buttons/remove_minister_button.png'
        super().__init__(input_dict, global_manager)

    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns same as superclass if the selected minister is currently in an office, otherwise returns False
        '''
        if super().can_show(skip_parent_collection=skip_parent_collection):
            displayed_minister = status.displayed_minister
            if displayed_minister and displayed_minister.current_position != 'none': #if there is an available minister displayed
                return(True)
        return(False)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button removes the selected minister from their current office, returning them to the pool of available
                ministers
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            appointed_minister = status.displayed_minister
            public_opinion_penalty = appointed_minister.status_number
            text = 'Are you sure you want to remove ' + appointed_minister.name + ' from office? If removed, he will return to the pool of available ministers and be available to reappoint until the end of the turn. /n /n.'
            text += 'Removing ' + appointed_minister.name + ' from office would incur a small public opinion penalty of ' + str(public_opinion_penalty) + ', even if he were reappointed. /n /n'
            text += appointed_minister.name + ' would expect to be reappointed to a different position by the end of the turn, and would be fired permanently and incur a much larger public opinion penalty if not reappointed. /n /n'
            if appointed_minister.status_number >= 3:
                if appointed_minister.status_number == 4:
                    text += appointed_minister.name + ' is of extremely high social status, and firing him would cause a national outrage. /n /n'
                else:
                    text += appointed_minister.name + ' is of high social status, and firing him would reflect particularly poorly on your company. /n /n'
            elif appointed_minister.status_number == 1:
                text += appointed_minister.name + ' is of low social status, and firing him would have a relatively minimal impact on your company\'s reputation. /n /n'
            constants.notification_manager.display_notification({
                'message': text,
                'choices': ['confirm remove minister', 'none']
            })
        else:
            text_utility.print_to_screen('You are busy and cannot remove a minister.', self.global_manager)

class to_trial_button(button):
    '''
    Button that goes to the trial screen to remove the selected minister from their current office
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['button_type'] = 'to trial'
        input_dict['modes'] = input_dict['attached_label'].modes
        input_dict['image_id'] = 'buttons/to_trial_button.png'
        super().__init__(input_dict, global_manager)

    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns same as superclass if a non-prosecutor minister with an office to be removed from is selected
        '''
        if super().can_show(skip_parent_collection=skip_parent_collection):
            displayed_minister = status.displayed_minister
            if displayed_minister and (not displayed_minister.current_position in ['none', 'Prosecutor']): #if there is an available non-prosecutor minister displayed
                return(True)
        return(False)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button goes to the trial screen to remove the selected minister from the game and confiscate a portion of their
                stolen money
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            if constants.money >= constants.action_prices['trial']:
                if minister_utility.positions_filled(self.global_manager):
                    if len(status.minister_list) > 8: #if any available appointees
                        defense = status.displayed_minister
                        prosecution = self.global_manager.get('current_ministers')['Prosecutor']
                        game_transitions.set_game_mode('trial', self.global_manager)
                        minister_utility.trial_setup(defense, prosecution, self.global_manager) #sets up defense and prosecution displays
                    else:
                        text_utility.print_to_screen('There are currently no available appointees to replace this minister in the event of a successful trial.', self.global_manager)
                else:
                    game_transitions.force_minister_appointment(self.global_manager)
            else:
                text_utility.print_to_screen('You do not have the ' + str(constants.action_prices['trial']) + ' money needed to start a trial.', self.global_manager)
        else:
            text_utility.print_to_screen('You are busy and cannot start a trial.', self.global_manager)

class active_investigation_button(button):
    '''
    Button that starts an active investigation on a minister
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['button_type'] = 'active investigation'
        input_dict['modes'] = ['ministers']
        input_dict['image_id'] = 'buttons/fabricate_evidence_button.png'
        super().__init__(input_dict, global_manager)

    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns same as superclass if a non-prosecutor minister with an office to be removed from is selected
        '''
        if super().can_show(skip_parent_collection=skip_parent_collection):
            displayed_minister = status.displayed_minister
            if displayed_minister and displayed_minister.current_position != 'Prosecutor':
                return(True)
        return(False)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button goes to the trial screen to remove the selected minister from the game and confiscate a portion of their
                stolen money
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            if constants.money >= constants.action_prices['active_investigation']:
                if minister_utility.positions_filled(self.global_manager):
                    cost = constants.action_prices['active_investigation']
                    constants.money_tracker.change(-1 * cost, 'active_investigation')
                    status.displayed_minister.attempt_active_investigation(self.global_manager.get('current_ministers')['Prosecutor'], cost)
                    actor_utility.double_action_price(self.global_manager, 'active_investigation')
                else:
                    game_transitions.force_minister_appointment(self.global_manager)
            else:
                text_utility.print_to_screen('You do not have the ' + str(constants.action_prices['active_investigation']) + ' money needed to start an active investigation.', self.global_manager)
        else:
            text_utility.print_to_screen('You are busy and cannot start an active investigation.', self.global_manager)

class fabricate_evidence_button(button):
    '''
    Button in the trial screen that fabricates evidence to use against the defense in the current trial. Fabricated evidence disappears at the end of the trial or at the end of the turn
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['button_type'] = 'fabricate evidence'
        input_dict['modes'] = ['trial', 'ministers']
        input_dict['image_id'] = 'buttons/fabricate_evidence_button.png'
        super().__init__(input_dict, global_manager)

    def get_cost(self):
        '''
        Description:
            Returns the cost of fabricating another piece of evidence. The cost increases for each existing fabricated evidence against the selected minister
        Input:
            None
        Output:
            Returns the cost of fabricating another piece of evidence
        '''
        defense = status.displayed_defense
        return(trial_utility.get_fabricated_evidence_cost(defense.fabricated_evidence))

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button spends money to fabricate a piece of evidence against the selected minister
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            if constants.money >= self.get_cost():
                constants.money_tracker.change(-1 * self.get_cost(), 'trial')
                defense = status.displayed_defense
                prosecutor = status.displayed_prosecution
                prosecutor.display_message(prosecutor.current_position + ' ' + prosecutor.name + ' reports that evidence has been successfully fabricated for ' + str(self.get_cost()) +
                    ' money. /n /nEach new fabricated evidence will cost twice as much as the last, and fabricated evidence becomes useless at the end of the turn or after it is used in a trial. /n /n')
                defense.fabricated_evidence += 1
                defense.corruption_evidence += 1
                minister_utility.calibrate_trial_info_display(self.global_manager, self.global_manager.get('defense_info_display'), defense) #updates trial display with new evidence
            else:
                text_utility.print_to_screen('You do not have the ' + str(self.get_cost()) + ' money needed to fabricate evidence.', self.global_manager)
        else:
            text_utility.print_to_screen('You are busy and cannot fabricate evidence.', self.global_manager)

class bribe_judge_button(button):
    '''
    Button in the trial screen that bribes the judge to get an advantage in the next trial this turn
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['button_type'] = 'bribe judge'
        input_dict['modes'] = ['trial']
        input_dict['image_id'] = 'buttons/bribe_judge_button.png'
        super().__init__(input_dict, global_manager)

    def get_cost(self):
        '''
        Description:
            Returns the cost of bribing the judge, which is as much as the first piece of fabricated evidence
        Input:
            None
        Output:
            Returns the cost of bribing the judge
        '''
        return(trial_utility.get_fabricated_evidence_cost(0)) #costs as much as 1st piece of fabricated evidence

    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns same as superclass if judge has not been bribed yet, otherwise returns False
        '''
        if super().can_show(skip_parent_collection=skip_parent_collection):
            if not flags.prosecution_bribed_judge:
                return(True)
        return(False)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button spends money to bribe the judge
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            if constants.money >= self.get_cost():
                if not flags.prosecution_bribed_judge:
                    constants.money_tracker.change(-1 * self.get_cost(), 'trial')
                    flags.prosecution_bribed_judge = True
                    prosecutor = status.displayed_prosecution
                    prosecutor.display_message(prosecutor.current_position + ' ' + prosecutor.name + ' reports that the judge has been successfully bribed for ' + str(self.get_cost()) +
                        ' money. /n /nThis may provide a bonus in the next trial this turn. /n /n')
                else:
                    text_utility.print_to_screen('The judge has already been bribed for this trial.', self.global_manager)
            else:
                text_utility.print_to_screen('You do not have the ' + str(self.get_cost()) + ' money needed to bribe the judge.', self.global_manager)
        else:
            text_utility.print_to_screen('You are busy and cannot fabricate evidence.', self.global_manager)  
    
class hire_african_workers_button(button):
    '''
    Button that hires available workers from the displayed village/slum
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'hire_source_type': string value - Type of location workers are hired from, like 'village' or 'slums'
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.hire_source_type = input_dict['hire_source_type']
        if self.hire_source_type == 'village':
            input_dict['button_type'] = 'hire village worker'
        elif self.hire_source_type == 'slums':
            input_dict['button_type'] = 'hire slums worker'
        super().__init__(input_dict, global_manager)

    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns same as superclass if a village/slum with available workers is displayed, otherwise returns False
        '''
        if super().can_show(skip_parent_collection=skip_parent_collection):
            if status.displayed_tile:
                if self.hire_source_type == 'village':
                    attached_village = status.displayed_tile.cell.get_building('village')
                    if not attached_village == 'none':
                        if attached_village.can_recruit_worker():
                            return(True)
                elif self.hire_source_type == 'slums':
                    attached_slums = status.displayed_tile.cell.contained_buildings['slums']
                    if not attached_slums == 'none':
                        return(True)
        return(False)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button hires an available worker from the displayed village/slum
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            choice_info_dict = {'recruitment_type': 'African worker ' + self.hire_source_type, 'cost': 0, 'mob_image_id': 'mobs/African worker/default.png', 'type': 'recruitment', 'source_type': self.hire_source_type}
            constants.actor_creation_manager.display_recruitment_choice_notification(choice_info_dict, 'African workers', self.global_manager)
        else:
            text_utility.print_to_screen('You are busy and cannot hire a worker.', self.global_manager)

class buy_slaves_button(button):
    '''
    Button that buys slaves from slave traders
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        input_dict['button_type'] = 'buy slaves'
        super().__init__(input_dict, global_manager)

    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns same as superclass if the displayed tile is in the slave traders grid, otherwise returns False
        '''
        if super().can_show(skip_parent_collection=skip_parent_collection):
            if status.displayed_tile and status.displayed_tile.cell.grid == status.slave_traders_grid:
                if self.global_manager.get('slave_traders_strength') > 0:
                    return(True)
        return(False)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button buys slaves from slave traders
        Input:
            None
        Output:
            None
        '''
        if main_loop_utility.action_possible(self.global_manager):
            self.cost = self.global_manager.get('recruitment_costs')['slave workers']
            if constants.money_tracker.get() >= self.cost:
                choice_info_dict = {'recruitment_type': 'slave workers', 'cost': self.cost, 'mob_image_id': 'mobs/slave workers/default.png', 'type': 'recruitment'}
                constants.actor_creation_manager.display_recruitment_choice_notification(choice_info_dict, 'slave workers', self.global_manager)
            else:
                text_utility.print_to_screen('You do not have enough money to buy slaves.', self.global_manager)
        else:
            text_utility.print_to_screen('You are busy and cannot buy slaves.', self.global_manager)

class automatic_route_button(button):
    '''
    Button that modifies a unit's automatic movement route, with an effect depending on the button's type
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'width': int value - pixel width of this element
                'height': int value - pixel height of this element
                'button_type': string value - Determines the function of this button, like 'clear automatic route', 'follow automatic route', or 'draw automatic route'
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'color': string value - Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['mobs/default/button.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(input_dict, global_manager)

    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button should be drawn. All automatic route buttons can only appear if the selected unit is porters or a crewed vehicle. Additionally, clear and follow automatic route buttons require that an automatic
                route already exists
        Input:
            None
        Output:
            boolean: Returns whether this button should be drawn
        '''
        if super().can_show(skip_parent_collection=skip_parent_collection):
            attached_mob = status.displayed_mob
            if attached_mob.inventory_capacity > 0 and (not (attached_mob.is_group and attached_mob.can_trade)) and (not (attached_mob.is_vehicle and attached_mob.crew == 'none')):
                if self.button_type in ['clear automatic route', 'follow automatic route']:
                    if len(attached_mob.base_automatic_route) > 0:
                        return(True)
                else:
                    return(True)
        return(False)

    def on_click(self):
        '''
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. Clear automatic route buttons remove the selected unit's automatic route. Draw automatic route buttons enter the route
            drawing mode, in which the player can click on consecutive tiles to add them to the route. Follow automatic route buttons command the selected unit to execute its in-progress automatic route, stopping when it cannot
            continue the route for any reason
        Input:
            None
        Output:
            None
        '''
        attached_mob = status.displayed_mob
        if main_loop_utility.action_possible(self.global_manager):
            if status.strategic_map_grid in attached_mob.grids:
                if self.button_type == 'clear automatic route':
                    attached_mob.clear_automatic_route()
                    
                elif self.button_type == 'draw automatic route':
                    if attached_mob.is_vehicle and attached_mob.vehicle_type == 'train' and not attached_mob.images[0].current_cell.has_intact_building('train_station'):
                        text_utility.print_to_screen('A train can only start a movement route from a train station.', self.global_manager)
                        return()
                    attached_mob.clear_automatic_route()
                    attached_mob.add_to_automatic_route((attached_mob.x, attached_mob.y))
                    flags.drawing_automatic_route = True
                    
                elif self.button_type == 'follow automatic route':
                    if attached_mob.can_follow_automatic_route():
                        attached_mob.follow_automatic_route()
                        attached_mob.remove_from_turn_queue()
                        actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display'), attached_mob) #updates mob info display if automatic route changed anything
                    else:
                        text_utility.print_to_screen('This unit is currently not able to progress along its designated route.', self.global_manager)
            else:
                text_utility.print_to_screen('You can only create movement routes in Africa.', self.global_manager)
        else:
            if self.button_type == 'follow automatic route':
                text_utility.print_to_screen('You are busy and cannot move this unit.', self.global_manager)
            else:
                text_utility.print_to_screen('You are busy and cannot modify this unit\'s movement route.', self.global_manager)
