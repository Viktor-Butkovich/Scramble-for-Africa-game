# Contains functionality for actor display buttons

import random
from ..interface_types.buttons import button
from ..util import (
    main_loop_utility,
    utility,
    actor_utility,
    minister_utility,
    trial_utility,
    text_utility,
    game_transitions,
)
import modules.constants.constants as constants
import modules.constants.status as status
import modules.constants.flags as flags


class embark_all_passengers_button(button):
    """
    Button that commands a vehicle to take all other mobs in its tile as passengers
    """

    def __init__(self, input_dict):
        """
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
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
        Output:
            None
        """
        self.vehicle_type = "none"
        input_dict["button_type"] = "embark all"
        super().__init__(input_dict)

    def on_click(self):
        """
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a vehicle to take all other mobs in its tile as passengers
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            vehicle = status.displayed_mob
            can_embark = True
            if self.vehicle_type == "train":
                if not vehicle.images[0].current_cell.has_intact_building(
                    "train_station"
                ):
                    text_utility.print_to_screen(
                        "A train can only pick up passengers at a train station."
                    )
                    can_embark = False
            if can_embark:
                if vehicle.sentry_mode:
                    vehicle.set_sentry_mode(False)
                for contained_mob in vehicle.images[0].current_cell.contained_mobs:
                    passenger = contained_mob
                    if (
                        passenger.is_pmob and not passenger.is_vehicle
                    ):  # vehicles and enemies won't be picked up as passengers
                        passenger.embark_vehicle(vehicle)
                constants.sound_manager.play_sound(
                    "voices/all aboard " + str(random.randrange(1, 4))
                )
        else:
            text_utility.print_to_screen(
                "You are busy and cannot embark all passengers."
            )

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn. Also updates this button to reflect a train or ship depending on the selected vehicle
        Input:
            None
        Output:
            boolean: Returns False if the selected vehicle has no crew, otherwise returns same as superclass
        """
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            displayed_mob = status.displayed_mob
            if not displayed_mob.has_crew:  # do not show if ship does not have crew
                return False
            if (not self.vehicle_type == displayed_mob.vehicle_type) and (
                not displayed_mob.vehicle_type == "vehicle"
            ):  # update vehicle type and image when shown if type has changed, like train to ship
                self.vehicle_type = displayed_mob.vehicle_type
                self.image.set_image(
                    "buttons/embark_" + self.vehicle_type + "_button.png"
                )
        return result


class disembark_all_passengers_button(button):
    """
    Button that commands a vehicle to eject all of its passengers
    """

    def __init__(self, input_dict):
        """
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
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
        Output:
            None
        """
        self.vehicle_type = "none"
        input_dict["button_type"] = "disembark all"
        super().__init__(input_dict)

    def on_click(self):
        """
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a vehicle to eject all of its passengers
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            vehicle = status.displayed_mob
            can_disembark = True
            if self.vehicle_type == "train":
                if not vehicle.images[0].current_cell.has_intact_building(
                    "train_station"
                ):
                    text_utility.print_to_screen(
                        "A train can only drop off passengers at a train station."
                    )
                    can_disembark = False
            if can_disembark:
                if vehicle.sentry_mode:
                    vehicle.set_sentry_mode(False)
                if len(vehicle.contained_mobs) > 0:
                    vehicle.contained_mobs[-1].selection_sound()
                vehicle.eject_passengers()
        else:
            text_utility.print_to_screen(
                "You are busy and cannot disembark all passengers."
            )

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn. Also updates this button to reflect a train or ship depending on the selected vehicle
        Input:
            None
        Output:
            boolean: Returns False if the selected vehicle has no crew, otherwise returns same as superclass
        """
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            vehicle = status.displayed_mob
            if not vehicle.has_crew:  # do not show if ship does not have crew
                return False
            if (not self.vehicle_type == vehicle.vehicle_type) and (
                not vehicle.vehicle_type == "vehicle"
            ):  # update vehicle type and image when shown if type has changed, like train to ship
                self.vehicle_type = vehicle.vehicle_type
                self.image.set_image(
                    "buttons/disembark_" + self.vehicle_type + "_button.png"
                )
        return result


class enable_sentry_mode_button(button):
    """
    Button that enables sentry mode for a unit, causing it to not be added to the turn cycle queue
    """

    def __init__(self, input_dict):
        """
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
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
        Output:
            None
        """
        input_dict["button_type"] = "enable sentry mode"
        super().__init__(input_dict)

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns True if the selected mob is a pmob and is not already in sentry mode, otherwise returns False
        """
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            displayed_mob = status.displayed_mob
            if not displayed_mob.is_pmob:
                return False
            elif displayed_mob.sentry_mode:
                return False
        return result

    def on_click(self):
        """
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button activates sentry mode for the selected unit
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            displayed_mob = status.displayed_mob
            displayed_mob.set_sentry_mode(True)
            if (
                constants.effect_manager.effect_active("promote_on_sentry")
                and (displayed_mob.is_group or displayed_mob.is_officer)
                and not displayed_mob.veteran
            ):  # purely for promotion testing, not normal functionality
                displayed_mob.promote()
        else:
            text_utility.print_to_screen("You are busy and cannot enable sentry mode.")


class disable_sentry_mode_button(button):
    """
    Button that disables sentry mode for a unit, causing it to not be added to the turn cycle queue
    """

    def __init__(self, input_dict):
        """
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
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
        Output:
            None
        """
        input_dict["button_type"] = "disable sentry mode"
        super().__init__(input_dict)

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns True if the selected mob is a pmob and is in sentry mode, otherwise returns False
        """
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            displayed_mob = status.displayed_mob
            if not displayed_mob.is_pmob:
                return False
            elif not displayed_mob.sentry_mode:
                return False
        return result

    def on_click(self):
        """
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button deactivates sentry mode for the selected unit
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            displayed_mob = status.displayed_mob
            displayed_mob.set_sentry_mode(False)
            actor_utility.calibrate_actor_info_display(
                status.mob_info_display, displayed_mob
            )
        else:
            text_utility.print_to_screen("You are busy and cannot disable sentry mode.")


class enable_automatic_replacement_button(button):
    """
    Button that enables automatic attrition replacement for a unit or one of its components
    """

    def __init__(self, input_dict):
        """
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
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'target_type': string value - Type of unit/subunit targeted by this button, such as 'unit', 'officer', or 'worker'
        Output:
            None
        """
        self.target_type = input_dict["target_type"]
        input_dict["button_type"] = "enable automatic replacement"
        super().__init__(input_dict)

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns True if the targeted unit component is present and does not already have automatic replacement, otherwise returns False
        """
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            displayed_mob = status.displayed_mob
            if not displayed_mob.is_pmob:
                return False
            elif displayed_mob.is_vehicle:
                return False
            elif displayed_mob.is_group and self.target_type == "unit":
                return False
            elif (not displayed_mob.is_group) and (not self.target_type == "unit"):
                return False
            elif (
                (self.target_type == "unit" and displayed_mob.automatically_replace)
                or (
                    self.target_type == "worker"
                    and displayed_mob.worker.automatically_replace
                )
                or (
                    self.target_type == "officer"
                    and displayed_mob.officer.automatically_replace
                )
            ):
                return False
        return result

    def on_click(self):
        """
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button enables automatic replacement for the selected unit
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            displayed_mob = status.displayed_mob
            if self.target_type == "unit":
                target = displayed_mob
            elif self.target_type == "worker":
                target = displayed_mob.worker
            elif self.target_type == "officer":
                target = displayed_mob.officer
            target.set_automatically_replace(True)
        else:
            text_utility.print_to_screen(
                "You are busy and cannot enable automatic replacement."
            )


class disable_automatic_replacement_button(button):
    """
    Button that disables automatic attrition replacement for a unit or one of its components
    """

    def __init__(self, input_dict):
        """
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
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'target_type': string value - Type of unit/subunit targeted by this button, such as 'unit', 'officer', or 'worker'
        Output:
            None
        """
        self.target_type = input_dict["target_type"]
        input_dict["button_type"] = "disable automatic replacement"
        super().__init__(input_dict)

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns True if the targeted unit component is present and has automatic replacement, otherwise returns False
        """
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            displayed_mob = status.displayed_mob
            if not displayed_mob.is_pmob:
                return False
            elif displayed_mob.is_vehicle:
                return False
            elif displayed_mob.is_group and self.target_type == "unit":
                return False
            elif (not displayed_mob.is_group) and (not self.target_type == "unit"):
                return False
            elif (
                (self.target_type == "unit" and not displayed_mob.automatically_replace)
                or (
                    self.target_type == "worker"
                    and not displayed_mob.worker.automatically_replace
                )
                or (
                    self.target_type == "officer"
                    and not displayed_mob.officer.automatically_replace
                )
            ):
                return False
        return result

    def on_click(self):
        """
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button disables automatic replacement for the selected unit
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            displayed_mob = status.displayed_mob
            if self.target_type == "unit":
                target = displayed_mob
            elif self.target_type == "worker":
                target = displayed_mob.worker
            elif self.target_type == "officer":
                target = displayed_mob.officer
            target.set_automatically_replace(False)
        else:
            text_utility.print_to_screen(
                "You are busy and cannot disable automatic replacement."
            )


class end_unit_turn_button(button):
    """
    Button that ends a unit's turn, removing it from the current turn's turn cycle queue
    """

    def __init__(self, input_dict):
        """
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
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
        Output:
            None
        """
        input_dict["button_type"] = "end unit turn"
        super().__init__(input_dict)

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns True if the selected mob is a pmob in the turn queue, otherwise returns False
        """
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            displayed_mob = status.displayed_mob
            if not displayed_mob.is_pmob:
                return False
            elif not displayed_mob in status.player_turn_queue:
                return False
        return result

    def on_click(self):
        """
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button removes the selected unit from the current turn's turn cycle queue
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            status.displayed_mob.remove_from_turn_queue()
            game_transitions.cycle_player_turn()
        else:
            text_utility.print_to_screen(
                "You are busy and cannot end this unit's turn."
            )


class remove_work_crew_button(button):
    """
    Button that removes a work crew from a building
    """

    def __init__(self, input_dict):
        """
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
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'attached_label': label value - Label that this button is attached to
                'building_type': Type of building to remove workers from, like 'resource building'
        Output:
            None
        """
        self.building_type = input_dict["building_type"]
        input_dict["button_type"] = "remove worker"
        super().__init__(input_dict)

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if there is not a corresponding work crew to remove, otherwise returns same as superclass
        """
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            if not self.attached_label.attached_list[
                self.attached_label.list_index
            ].in_building:
                return False
        return result

    def on_click(self):
        """
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button removes a work crew from a building
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            self.attached_label.attached_list[
                self.attached_label.list_index
            ].leave_building(
                self.attached_label.actor.cell.contained_buildings[self.building_type]
            )
        else:
            text_utility.print_to_screen(
                "You are busy and cannot remove a work crew from a building."
            )


class disembark_vehicle_button(button):
    """
    Button that disembarks a passenger from a vehicle
    """

    def __init__(self, input_dict):
        """
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
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'attached_label': label value - Label that this button is attached to
        Output:
            None
        """
        self.vehicle_type = "none"
        input_dict["button_type"] = "disembark"
        super().__init__(input_dict)

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn. Also updates this button to reflect a train or ship depending on the selected vehicle
        Input:
            None
        Output:
            boolean: Returns False if there is not a corresponding passenger to disembark, otherwise returns same as superclass
        """
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            if not self.attached_label.attached_list[
                self.attached_label.list_index
            ].in_vehicle:
                return False
            old_vehicle_type = self.vehicle_type
            self.vehicle_type = self.attached_label.actor.vehicle_type
            if (
                not self.vehicle_type == old_vehicle_type
                and not self.vehicle_type == "none"
            ):  # if changed
                self.image.set_image(
                    "buttons/disembark_" + self.vehicle_type + "_button.png"
                )
        return result

    def on_click(self):
        """
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button disembarks a passenger from a vehicle
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            if len(self.attached_label.actor.contained_mobs) > 0:
                can_disembark = True
                if self.vehicle_type == "train":
                    if not self.attached_label.actor.images[
                        0
                    ].current_cell.has_intact_building("train_station"):
                        text_utility.print_to_screen(
                            "A train can only drop off passengers at a train station."
                        )
                        can_disembark = False
                if can_disembark:
                    passenger = self.attached_label.attached_list[
                        self.attached_label.list_index
                    ]
                    if passenger.sentry_mode:
                        passenger.set_sentry_mode(False)
                    passenger.selection_sound()
                    self.attached_label.attached_list[
                        self.attached_label.list_index
                    ].disembark_vehicle(self.attached_label.actor)
            else:
                text_utility.print_to_screen(
                    "You must select a "
                    + self.vehicle_type
                    + "with passengers to disembark passengers."
                )
        else:
            text_utility.print_to_screen(
                "You are busy and cannot disembark from a " + self.vehicle_type + "."
            )


class embark_vehicle_button(button):
    """
    Button that commands a selected mob to embark a vehicle of the correct type in the same tile
    """

    def __init__(self, input_dict):
        """
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
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'vehicle_type': string value - Type of vehicle this button embarks, like 'train' or 'ship'
        Output:
            None
        """
        self.vehicle_type = input_dict["vehicle_type"]
        self.was_showing = False
        input_dict["button_type"] = "embark"
        super().__init__(input_dict)

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob cannot embark vehicles or if there is no vehicle in the tile to embark, otherwise returns same as superclass
        """
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            displayed_mob = status.displayed_mob
            if not displayed_mob.is_pmob:
                result = False
            elif displayed_mob.in_vehicle or displayed_mob.is_vehicle:
                result = False
            elif (
                not displayed_mob.actor_type == "minister"
                and not displayed_mob.images[0].current_cell.has_vehicle(
                    self.vehicle_type
                )
            ):
                result = False
        if (
            not result == self.was_showing
        ):  # if visibility changes, update actor info display
            self.was_showing = result
            actor_utility.calibrate_actor_info_display(
                status.mob_info_display, displayed_mob
            )
        self.was_showing = result
        return result

    def on_click(self):
        """
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a selected mob to embark a vehicle of the correct type in the same tile
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            if status.displayed_mob.images[0].current_cell.has_vehicle(
                self.vehicle_type
            ):
                rider = status.displayed_mob
                vehicles = rider.images[0].current_cell.get_vehicles(self.vehicle_type)
                can_embark = True
                if vehicles[0].vehicle_type == "train":
                    if not rider.images[0].current_cell.has_intact_building(
                        "train_station"
                    ):
                        text_utility.print_to_screen(
                            "A train can only pick up passengers at a train station."
                        )
                        can_embark = False
                if can_embark:
                    rider.set_sentry_mode(False)
                    if len(vehicles) > 1:
                        vehicles[0].select()
                        for vehicle in vehicles:
                            constants.notification_manager.display_notification(
                                {
                                    "message": "There are "
                                    + str(len(vehicles))
                                    + " possible vehicles to embark - click next until you find the vehicle you would like to embark. /n /n",
                                    "choices": [
                                        {
                                            "on_click": (
                                                self.finish_embark_vehicle,
                                                [rider, vehicle],
                                            ),
                                            "tooltip": ["Embarks this vehicle"],
                                            "message": "Embark",
                                        },
                                        {
                                            "on_click": (
                                                self.skip_embark_vehicle,
                                                [
                                                    rider,
                                                    vehicles,
                                                    vehicles.index(vehicle),
                                                ],
                                            ),
                                            "tooltip": [
                                                "Cycles to the next possible vehicle"
                                            ],
                                            "message": "Next vehicle",
                                        },
                                    ],
                                }
                            )
                    else:
                        vehicle = vehicles[0]
                        if vehicle.sentry_mode:
                            vehicle.set_sentry_mode(False)
                        rider.embark_vehicle(vehicle)
                        constants.sound_manager.play_sound(
                            "voices/all aboard " + str(random.randrange(1, 4))
                        )
            else:
                text_utility.print_to_screen(
                    "You must select a unit in the same tile as a crewed "
                    + self.vehicle_type
                    + " to embark."
                )
        else:
            text_utility.print_to_screen(
                "You are busy and cannot embark a " + self.vehicle_type + "."
            )

    def finish_embark_vehicle(self, rider, vehicle):
        """
        Description:
            Selects a vehicle to embark when multiple vehicle options are available, called by choice notification
        Input:
            pmob rider: Unit embarking vehicle
            vehicle vehicle: Vehicle to embark
        Output:
            None
        """
        constants.notification_manager.clear_notification_queue()  # Skip remaining embark notifications
        vehicle.set_sentry_mode(False)
        rider.embark_vehicle(vehicle)
        constants.sound_manager.play_sound(
            "voices/all aboard " + str(random.randrange(1, 4))
        )

    def skip_embark_vehicle(self, rider, vehicles, index):
        """
        Description:
            Selects the next possible vehicle to embark when multiple vehicle options are available, called by choice notification
        Input:
            pmob rider: Unit embarking vehicle
            vehicle vehicle: Vehicle to embark
        Output:
            None
        """
        if index == len(vehicles) - 1:
            rider.select()
        else:
            vehicles[index + 1].select()


class cycle_passengers_button(button):
    """
    Button that cycles the order of passengers displayed in a vehicle
    """

    def __init__(self, input_dict):
        """
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
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
        Output:
            None
        """
        self.vehicle_type = "none"
        input_dict["button_type"] = "cycle passengers"
        super().__init__(input_dict)

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not a vehicle or if the vehicle does not have enough passengers to cycle through, otherwise returns same as superclass
        """
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            displayed_mob = status.displayed_mob
            if not displayed_mob.is_vehicle:
                return False
            elif (
                not len(displayed_mob.contained_mobs) > 3
            ):  # only show if vehicle with 3+ passengers
                return False
            self.vehicle_type = displayed_mob.vehicle_type
        return result

    def on_click(self):
        """
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button cycles the order of passengers displayed in a vehicle
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            displayed_mob = status.displayed_mob
            moved_mob = displayed_mob.contained_mobs.pop(0)
            displayed_mob.contained_mobs.append(moved_mob)
            actor_utility.calibrate_actor_info_display(
                status.mob_info_display, displayed_mob
            )  # updates mob info display list to show changed passenger order
        else:
            text_utility.print_to_screen("You are busy and cannot cycle passengers.")


class cycle_work_crews_button(button):
    """
    Button that cycles the order of work crews in a building
    """

    def __init__(self, input_dict):
        """
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
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'attached_label': label value - Label that this button is attached to
        Output:
            None
        """
        self.previous_showing_result = False
        input_dict["button_type"] = "cycle work crews"
        super().__init__(input_dict)

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns same as superclass if the displayed tile's cell has a resource building containing more than 3 work crews, otherwise returns False
        """
        result = super().can_show(skip_parent_collection=skip_parent_collection)
        if result:
            displayed_tile = status.displayed_tile
            if displayed_tile.cell.contained_buildings["resource"] == "none":
                self.previous_showing_result = False
                return False
            elif (
                not len(
                    displayed_tile.cell.contained_buildings[
                        "resource"
                    ].contained_work_crews
                )
                > 3
            ):  # only show if building with 3+ work crews
                self.previous_showing_result = False
                return False
        if self.previous_showing_result == False and result == True:
            self.previous_showing_result = result
            self.attached_label.set_label(
                self.attached_label.message
            )  # update label to update this button's location
        self.previous_showing_result = result
        return result

    def on_click(self):
        """
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button cycles the order of work crews displayed in a building
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            displayed_tile = status.displayed_tile
            moved_mob = displayed_tile.cell.contained_buildings[
                "resource"
            ].contained_work_crews.pop(0)
            displayed_tile.cell.contained_buildings[
                "resource"
            ].contained_work_crews.append(moved_mob)
            actor_utility.calibrate_actor_info_display(
                status.tile_info_display, displayed_tile
            )  # updates tile info display list to show changed work crew order
        else:
            text_utility.print_to_screen("You are busy and cannot cycle work crews.")


class work_crew_to_building_button(button):
    """
    Button that commands a work crew to work in a certain type of building in its tile
    """

    def __init__(self, input_dict):
        """
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
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'building_type': string value - Type of buliding this button attaches workers to, like 'resource building'
        Output:
            None
        """
        self.building_type = input_dict["building_type"]
        self.attached_work_crew = None
        self.attached_building = None
        input_dict["button_type"] = "worker to resource"
        super().__init__(input_dict)

    def update_info(self):
        """
        Description:
            Updates the building this button assigns workers to depending on the buildings present in this tile
        Input:
            None
        Output:
            None
        """
        self.attached_work_crew = status.displayed_mob
        if self.attached_work_crew and self.attached_work_crew.is_work_crew:
            self.attached_building = self.attached_work_crew.images[
                0
            ].current_cell.get_intact_building(self.building_type)
            if self.attached_building == "none":
                self.attached_building = None
        else:
            self.attached_building = None

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not a work crew, otherwise returns same as superclass
        """
        self.update_info()
        return (
            super().can_show(skip_parent_collection=skip_parent_collection)
            and self.attached_work_crew
            and self.attached_work_crew.is_work_crew
        )

    def update_tooltip(self):
        """
        Description:
            Sets this button's tooltip depending on the building it assigns workers to
        Input:
            None
        Output:
            None
        """
        if self.attached_work_crew and self.attached_building:
            if self.building_type == "resource":
                self.set_tooltip(
                    [
                        "Assigns the selected work crew to the "
                        + self.attached_building.name
                        + ", producing "
                        + self.attached_building.resource_type
                        + " over time."
                    ]
                )
            else:
                self.set_tooltip(["placeholder"])
        elif self.attached_work_crew:
            if self.building_type == "resource":
                self.set_tooltip(
                    [
                        "Assigns the selected work crew to a resource building, producing commodities over time."
                    ]
                )
        else:
            self.set_tooltip(["placeholder"])

    def on_click(self):
        """
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands a work crew to work in a certain type of building in its tile
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            if self.attached_building:
                if self.attached_building.scale > len(
                    self.attached_building.contained_work_crews
                ):  # if has extra space
                    if self.attached_work_crew.sentry_mode:
                        self.attached_work_crew.set_sentry_mode(False)
                    self.attached_work_crew.work_building(self.attached_building)
                else:
                    text_utility.print_to_screen(
                        "This building is at its work crew capacity."
                    )
                    text_utility.print_to_screen(
                        "Upgrade the building's scale to increase work crew capacity."
                    )
            else:
                text_utility.print_to_screen(
                    "This work crew must be in the same tile as a resource production building to work in it"
                )
        else:
            text_utility.print_to_screen(
                "You are busy and cannot attach a work crew to a building."
            )


class labor_broker_button(button):
    """
    Buttons that commands a vehicle without crew or an officer to use a labor broker in a port to recruit a worker from a nearby village, with a price based on the village's aggressiveness and distance
    """

    def __init__(self, input_dict):
        """
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
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
        Output:
            None
        """
        input_dict["button_type"] = "labor broker"
        super().__init__(input_dict)

    def on_click(self):
        """
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button commands an officer or vehicle without crew to use a labor broker in a port
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            if status.displayed_tile.cell.has_intact_building("port"):
                cost_info_list = self.get_cost()
                if cost_info_list != "none":
                    if constants.money_tracker.get() >= cost_info_list[1]:
                        if minister_utility.positions_filled():
                            constants.actor_creation_manager.display_recruitment_choice_notification(
                                {
                                    "recruitment_type": "African worker labor broker",
                                    "cost": cost_info_list[1],
                                    "mob_image_id": "mobs/African worker/default.png",
                                    "type": "recruitment",
                                    "source_type": "labor broker",
                                    "village": cost_info_list[0],
                                },
                                "African workers",
                            )
                    else:
                        text_utility.print_to_screen(
                            "You cannot afford the recruitment cost of "
                            + str(cost_info_list[1])
                            + " for the cheapest available worker. "
                        )
                else:
                    text_utility.print_to_screen(
                        "There are no eligible villages to recruit workers from."
                    )
            else:
                text_utility.print_to_screen(
                    "This port is damaged and cannot use a labor broker."
                )
        else:
            text_utility.print_to_screen("You are busy and cannot use a labor broker.")

    def get_cost(self):
        """
        Description:
            Calculates and returns the cost of using a labor broker in a port at the currently selected unit's location, based on nearby villages' aggressiveness and distance from the port
        Input:
            None
        Output:
            string/list: If no valid villages are found, returns 'none'. Otherwise, returns a list with the village as the first item and the cost as the second item
        """
        lowest_cost_village = "none"
        lowest_cost = 0
        for current_village in status.village_list:
            if current_village.population > 0:
                distance = int(
                    utility.find_object_distance(current_village, status.displayed_tile)
                )
                cost = (2 * current_village.aggressiveness) + distance
                if cost < lowest_cost or lowest_cost_village == "none":
                    lowest_cost_village = current_village
                    lowest_cost = cost
        if lowest_cost_village == "none":
            return "none"
        else:
            return [lowest_cost_village, lowest_cost]


class switch_theatre_button(button):
    """
    Button starts choosing a destination for a ship to travel between theatres, like between Europe and Africa. A destination is chosen when the player clicks a tile in another theatre.
    """

    def __init__(self, input_dict):
        """
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
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
        Output:
            None
        """
        input_dict["button_type"] = "switch theatre"
        super().__init__(input_dict)

    def on_click(self):
        """
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button starts choosing a destination for a ship to travel between theatres, like between Europe and Africa. A
                destination is chosen when the player clicks a tile in another theatre.
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            current_mob = status.displayed_mob
            if current_mob.movement_points >= 1:
                if not (
                    status.strategic_map_grid in current_mob.grids
                    and (
                        current_mob.y > 1
                        or (
                            current_mob.y == 1
                            and not current_mob.images[
                                0
                            ].current_cell.has_intact_building("port")
                        )
                    )
                ):  # can leave if in ocean or if in coastal port
                    if (
                        current_mob.can_leave()
                    ):  # not current_mob.grids[0] in self.destination_grids and
                        if current_mob.sentry_mode:
                            current_mob.set_sentry_mode(False)
                        if not constants.current_game_mode == "strategic":
                            game_transitions.set_game_mode("strategic")
                            current_mob.select()
                        current_mob.clear_automatic_route()
                        current_mob.end_turn_destination = "none"
                        current_mob.add_to_turn_queue()
                        flags.choosing_destination = True
                else:
                    text_utility.print_to_screen(
                        "You are inland and cannot cross the ocean."
                    )
            else:
                text_utility.print_to_screen(
                    "Crossing the ocean requires all remaining movement points, at least 1."
                )
        else:
            text_utility.print_to_screen("You are busy and cannot move.")

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the selected mob is not capable of traveling between theatres, otherwise returns same as superclass
        """
        return (
            super().can_show(skip_parent_collection=skip_parent_collection)
            and status.displayed_mob.is_pmob
            and status.displayed_mob.can_travel()
        )


class appoint_minister_button(button):
    """
    Button that appoints the selected minister to the office corresponding to this button
    """

    def __init__(self, input_dict):
        """
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
        Output:
            None
        """
        self.appoint_type = input_dict["appoint_type"]
        input_dict["button_type"] = "appoint minister"
        input_dict["modes"] = ["ministers"]
        input_dict["image_id"] = (
            "ministers/icons/"
            + constants.minister_type_dict[self.appoint_type]
            + ".png"
        )
        super().__init__(input_dict)

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns same as superclass if the minister office that this button is attached to is open, otherwise returns False
        """
        if super().can_show(skip_parent_collection=skip_parent_collection):
            displayed_minister = status.displayed_minister
            if (
                displayed_minister and displayed_minister.current_position == "none"
            ):  # if there is an available minister displayed
                if not status.current_ministers[
                    self.appoint_type
                ]:  # if the position that this button appoints is available
                    return True
        return False

    def on_click(self):
        """
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button appoints the selected minister to the office corresponding to this button
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            appointed_minister = status.displayed_minister
            if not appointed_minister.just_removed:
                appointed_minister.respond("first hired")
            appointed_minister.appoint(self.appoint_type)
            minister_utility.calibrate_minister_info_display(appointed_minister)
        else:
            text_utility.print_to_screen("You are busy and cannot appoint a minister.")


class remove_minister_button(button):
    """
    Button that removes the selected minister from their current office
    """

    def __init__(self, input_dict):
        """
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
        Output:
            None
        """
        input_dict["button_type"] = "remove minister"
        input_dict["modes"] = ["ministers"]
        input_dict["image_id"] = "buttons/remove_minister_button.png"
        super().__init__(input_dict)

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns same as superclass if the selected minister is currently in an office, otherwise returns False
        """
        if super().can_show(skip_parent_collection=skip_parent_collection):
            displayed_minister = status.displayed_minister
            if (
                displayed_minister and displayed_minister.current_position != "none"
            ):  # if there is an available minister displayed
                return True
        return False

    def on_click(self):
        """
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button removes the selected minister from their current office, returning them to the pool of available
                ministers
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            appointed_minister = status.displayed_minister
            public_opinion_penalty = appointed_minister.status_number
            text = (
                "Are you sure you want to remove "
                + appointed_minister.name
                + " from office? If removed, he will return to the pool of available ministers and be available to reappoint until the end of the turn. /n /n"
            )
            text += (
                "Removing "
                + appointed_minister.name
                + " from office would incur a small public opinion penalty of "
                + str(public_opinion_penalty)
                + ", even if he were reappointed. /n /n"
            )
            text += (
                appointed_minister.name
                + " expects to be reappointed to a different position by the end of the turn. If not reappointed, he will be fired permanently and incur a much larger public opinion penalty. /n /n"
            )
            if appointed_minister.status_number >= 3:
                if appointed_minister.status_number == 4:
                    text += (
                        appointed_minister.name
                        + " is of extremely high social status, so firing him would cause a national outrage. /n /n"
                    )
                else:
                    text += (
                        appointed_minister.name
                        + " is of high social status, so firing him would reflect particularly poorly on your company. /n /n"
                    )
            elif appointed_minister.status_number == 1:
                text += (
                    appointed_minister.name
                    + " is of low social status, so firing him would have a relatively minimal impact on your company's reputation. /n /n"
                )
            constants.notification_manager.display_notification(
                {"message": text, "choices": ["confirm remove minister", "none"]}
            )
        else:
            text_utility.print_to_screen("You are busy and cannot remove a minister.")


class to_trial_button(button):
    """
    Button that goes to the trial screen to remove the selected minister from their current office
    """

    def __init__(self, input_dict):
        """
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
        Output:
            None
        """
        input_dict["button_type"] = "to trial"
        input_dict["modes"] = input_dict["attached_label"].modes
        input_dict["image_id"] = "buttons/to_trial_button.png"
        super().__init__(input_dict)

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns same as superclass if a non-prosecutor minister with an office to be removed from is selected
        """
        if super().can_show(skip_parent_collection=skip_parent_collection):
            displayed_minister = status.displayed_minister
            if displayed_minister and (
                not displayed_minister.current_position in ["none", "Prosecutor"]
            ):  # if there is an available non-prosecutor minister displayed
                return True
        return False

    def on_click(self):
        """
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button goes to the trial screen to remove the selected minister from the game and confiscate a portion of their
                stolen money
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            if constants.money >= constants.action_prices["trial"]:
                if minister_utility.positions_filled():
                    if len(status.minister_list) > 8:  # if any available appointees
                        defense = status.displayed_minister
                        prosecution = status.current_ministers["Prosecutor"]
                        game_transitions.set_game_mode("trial")
                        minister_utility.trial_setup(
                            defense, prosecution
                        )  # sets up defense and prosecution displays
                    else:
                        text_utility.print_to_screen(
                            "There are currently no available appointees to replace this minister in the event of a successful trial."
                        )
            else:
                text_utility.print_to_screen(
                    "You do not have the "
                    + str(constants.action_prices["trial"])
                    + " money needed to start a trial."
                )
        else:
            text_utility.print_to_screen("You are busy and cannot start a trial.")


class fabricate_evidence_button(button):
    """
    Button in the trial screen that fabricates evidence to use against the defense in the current trial. Fabricated evidence disappears at the end of the trial or at the end of the turn
    """

    def __init__(self, input_dict):
        """
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
        Output:
            None
        """
        input_dict["button_type"] = "fabricate evidence"
        input_dict["modes"] = ["trial", "ministers"]
        input_dict["image_id"] = "buttons/fabricate_evidence_button.png"
        super().__init__(input_dict)

    def get_cost(self):
        """
        Description:
            Returns the cost of fabricating another piece of evidence. The cost increases for each existing fabricated evidence against the selected minister
        Input:
            None
        Output:
            Returns the cost of fabricating another piece of evidence
        """
        defense = status.displayed_defense
        return trial_utility.get_fabricated_evidence_cost(defense.fabricated_evidence)

    def on_click(self):
        """
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button spends money to fabricate a piece of evidence against the selected minister
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            if constants.money >= self.get_cost():
                constants.money_tracker.change(-1 * self.get_cost(), "trial")
                defense = status.displayed_defense
                prosecutor = status.displayed_prosecution
                prosecutor.display_message(
                    prosecutor.current_position
                    + " "
                    + prosecutor.name
                    + " reports that evidence has been successfully fabricated for "
                    + str(self.get_cost())
                    + " money. /n /nEach new fabricated evidence will cost twice as much as the last, and fabricated evidence becomes useless at the end of the turn or after it is used in a trial. /n /n"
                )
                defense.fabricated_evidence += 1
                defense.corruption_evidence += 1
                minister_utility.calibrate_trial_info_display(
                    status.defense_info_display, defense
                )  # updates trial display with new evidence
            else:
                text_utility.print_to_screen(
                    "You do not have the "
                    + str(self.get_cost())
                    + " money needed to fabricate evidence."
                )
        else:
            text_utility.print_to_screen("You are busy and cannot fabricate evidence.")


class bribe_judge_button(button):
    """
    Button in the trial screen that bribes the judge to get an advantage in the next trial this turn
    """

    def __init__(self, input_dict):
        """
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
        Output:
            None
        """
        input_dict["button_type"] = "bribe judge"
        input_dict["modes"] = ["trial"]
        input_dict["image_id"] = "buttons/bribe_judge_button.png"
        super().__init__(input_dict)

    def get_cost(self):
        """
        Description:
            Returns the cost of bribing the judge, which is as much as the first piece of fabricated evidence
        Input:
            None
        Output:
            Returns the cost of bribing the judge
        """
        return trial_utility.get_fabricated_evidence_cost(
            0
        )  # costs as much as 1st piece of fabricated evidence

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns same as superclass if judge has not been bribed yet, otherwise returns False
        """
        if super().can_show(skip_parent_collection=skip_parent_collection):
            if not flags.prosecution_bribed_judge:
                return True
        return False

    def on_click(self):
        """
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button spends money to bribe the judge
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            if constants.money >= self.get_cost():
                if not flags.prosecution_bribed_judge:
                    constants.money_tracker.change(-1 * self.get_cost(), "trial")
                    flags.prosecution_bribed_judge = True
                    prosecutor = status.displayed_prosecution
                    prosecutor.display_message(
                        prosecutor.current_position
                        + " "
                        + prosecutor.name
                        + " reports that the judge has been successfully bribed for "
                        + str(self.get_cost())
                        + " money. /n /nThis may provide a bonus in the next trial this turn. /n /n"
                    )
                else:
                    text_utility.print_to_screen(
                        "The judge has already been bribed for this trial."
                    )
            else:
                text_utility.print_to_screen(
                    "You do not have the "
                    + str(self.get_cost())
                    + " money needed to bribe the judge."
                )
        else:
            text_utility.print_to_screen("You are busy and cannot fabricate evidence.")


class hire_african_workers_button(button):
    """
    Button that hires available workers from the displayed village/slum
    """

    def __init__(self, input_dict):
        """
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
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'hire_source_type': string value - Type of location workers are hired from, like 'village' or 'slums'
        Output:
            None
        """
        self.hire_source_type = input_dict["hire_source_type"]
        if self.hire_source_type == "village":
            input_dict["button_type"] = "hire village worker"
        elif self.hire_source_type == "slums":
            input_dict["button_type"] = "hire slums worker"
        super().__init__(input_dict)

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns same as superclass if a village/slum with available workers is displayed, otherwise returns False
        """
        if super().can_show(skip_parent_collection=skip_parent_collection):
            if status.displayed_tile:
                if self.hire_source_type == "village":
                    attached_village = status.displayed_tile.cell.get_building(
                        "village"
                    )
                    if not attached_village == "none":
                        if attached_village.can_recruit_worker():
                            return True
                elif self.hire_source_type == "slums":
                    attached_slums = status.displayed_tile.cell.contained_buildings[
                        "slums"
                    ]
                    if not attached_slums == "none":
                        return True
        return False

    def on_click(self):
        """
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button hires an available worker from the displayed village/slum
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            if not status.displayed_tile.cell.has_npmob():
                choice_info_dict = {
                    "recruitment_type": "African worker " + self.hire_source_type,
                    "cost": 0,
                    "mob_image_id": "mobs/African worker/default.png",
                    "type": "recruitment",
                    "source_type": self.hire_source_type,
                }
                constants.actor_creation_manager.display_recruitment_choice_notification(
                    choice_info_dict, "African workers"
                )
            else:
                text_utility.print_to_screen(
                    "You cannot recruit workers when hostile units are present."
                )
        else:
            text_utility.print_to_screen("You are busy and cannot hire a worker.")


class recruit_workers_button(button):
    """
    Button that buys workers from an abstract grid - currently either slave workers from slave traders or Asian workers from Asia
    """

    def __init__(self, input_dict):
        """
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
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'worker_type': str value - Type of workers this button recruits, like 'slave' or 'Asian'
        Output:
            None
        """
        input_dict["button_type"] = "recruit workers"
        self.worker_type = input_dict["worker_type"]
        super().__init__(input_dict)

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns same as superclass if the displayed tile is in the slave traders grid, otherwise returns False
        """
        if (
            super().can_show(skip_parent_collection=skip_parent_collection)
            and status.displayed_tile
        ):
            if self.worker_type == "slave":
                if (
                    status.displayed_tile.cell.grid == status.slave_traders_grid
                    and constants.slave_traders_strength > 0
                ):
                    return True
            elif self.worker_type == "Asian":
                if status.displayed_tile.cell.grid == status.asia_grid:
                    return True
        return False

    def on_click(self):
        """
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. This type of button buys slaves from slave traders
        Input:
            None
        Output:
            None
        """
        if main_loop_utility.action_possible():
            cost = status.worker_types[self.worker_type].recruitment_cost
            if constants.money_tracker.get() >= cost:
                choice_info_dict = {
                    "recruitment_type": self.worker_type + " workers",
                    "cost": cost,
                }
                constants.actor_creation_manager.display_recruitment_choice_notification(
                    choice_info_dict, self.worker_type + " workers"
                )
            else:
                text_utility.print_to_screen(
                    "You do not have enough money to purhase "
                    + self.worker_type
                    + " workers."
                )
        else:
            text_utility.print_to_screen(
                "You are busy and cannot purchase " + self.worker_type + " workers."
            )


class automatic_route_button(button):
    """
    Button that modifies a unit's automatic movement route, with an effect depending on the button's type
    """

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn. All automatic route buttons can only appear if the selected unit is porters or a crewed vehicle. Additionally, clear and execute automatic route buttons require that an automatic
                route already exists
        Input:
            None
        Output:
            boolean: Returns whether this button should be drawn
        """
        if super().can_show(skip_parent_collection=skip_parent_collection):
            attached_mob = status.displayed_mob
            if (
                attached_mob.inventory_capacity > 0
                and (not (attached_mob.is_group and attached_mob.can_trade))
                and (not (attached_mob.is_vehicle and attached_mob.crew == "none"))
            ):
                if self.button_type in [
                    "clear automatic route",
                    "execute automatic route",
                ]:
                    if len(attached_mob.base_automatic_route) > 0:
                        return True
                else:
                    return True
        return False

    def on_click(self):
        """
        Description:
            Does a certain action when clicked or when corresponding key is pressed, depending on button_type. Clear automatic route buttons remove the selected unit's automatic route. Draw automatic route buttons enter the route
            drawing mode, in which the player can click on consecutive tiles to add them to the route. Execute automatic route buttons command the selected unit to execute its in-progress automatic route, stopping when it cannot
            continue the route for any reason
        Input:
            None
        Output:
            None
        """
        attached_mob = status.displayed_mob
        if main_loop_utility.action_possible():
            if status.strategic_map_grid in attached_mob.grids:
                if self.button_type == "clear automatic route":
                    attached_mob.clear_automatic_route()

                elif self.button_type == "draw automatic route":
                    if (
                        attached_mob.is_vehicle
                        and attached_mob.vehicle_type == "train"
                        and not attached_mob.images[0].current_cell.has_intact_building(
                            "train_station"
                        )
                    ):
                        text_utility.print_to_screen(
                            "A train can only start a movement route from a train station."
                        )
                        return ()
                    attached_mob.clear_automatic_route()
                    attached_mob.add_to_automatic_route(
                        (attached_mob.x, attached_mob.y)
                    )
                    flags.drawing_automatic_route = True

                elif self.button_type == "execute automatic route":
                    if attached_mob.can_follow_automatic_route():
                        attached_mob.follow_automatic_route()
                        attached_mob.remove_from_turn_queue()
                        actor_utility.calibrate_actor_info_display(
                            status.mob_info_display, attached_mob
                        )  # updates mob info display if automatic route changed anything
                    else:
                        text_utility.print_to_screen(
                            "This unit is currently not able to progress along its designated route."
                        )
            else:
                text_utility.print_to_screen(
                    "You can only create movement routes in Africa."
                )
        else:
            if self.button_type == "execute automatic route":
                text_utility.print_to_screen("You are busy and cannot move this unit.")
            else:
                text_utility.print_to_screen(
                    "You are busy and cannot modify this unit's movement route."
                )


class toggle_button(button):
    """
    Button that monitors and toggles a boolean variable on the attached actor
    """

    def __init__(self, input_dict):
        """
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
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'toggle_variable': string value - Name of the variable that this button toggles
        Output:
            None
        """
        self.toggle_variable = input_dict["toggle_variable"]
        super().__init__(input_dict)

    def on_click(self):
        """
        Description:
            Toggles this button's variable on the attached actor
        Input:
            None
        Output:
            None
        """
        setattr(
            self.attached_label.actor,
            self.toggle_variable,
            not getattr(self.attached_label.actor, self.toggle_variable),
        )

    def can_show(self, skip_parent_collection=False):
        """
        Description:
            Returns whether this button should be drawn. All automatic route buttons require that an automatic route already exists
        Input:
            None
        Output:
            boolean: Returns whether this button should be drawn
        """
        if (
            not self.attached_label.actor in ["none", None]
        ) and self.attached_label.actor.is_pmob:
            self.showing_outline = getattr(
                self.attached_label.actor, self.toggle_variable
            )
            if super().can_show(skip_parent_collection=skip_parent_collection):
                if self.toggle_variable == "wait_until_full":
                    return bool(status.displayed_mob.base_automatic_route)
                else:
                    return True
        return False

    def update_tooltip(self):
        """
        Description:
            Sets this button's tooltip depending on the variable it toggles
        Input:
            None
        Output:
            None
        """
        tooltip_text = []
        if not self.attached_label.actor in [None, "none"]:
            if self.toggle_variable == "wait_until_full":
                tooltip_text.append(
                    "Toggles wait until full - waiting until there is a full load to transport or no remaining warehouse space before starting automatic route"
                )
                if getattr(self.attached_label.actor, self.toggle_variable):
                    tooltip_text.append("Currently waiting until full")
                else:
                    tooltip_text.append(
                        "Currently waiting until there is anything to transport"
                    )
        self.set_tooltip(tooltip_text)
