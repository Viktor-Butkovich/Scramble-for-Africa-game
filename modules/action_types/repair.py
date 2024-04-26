# Contains all functionality for building repairs

from . import action
from ..util import actor_utility, action_utility
import modules.constants.constants as constants
import modules.constants.status as status


class repair(action.action):
    """
    Action for unit to repair a damaged building
    """

    def initial_setup(self, **kwargs):
        """
        Description:
            Completes any configuration required for this action during setup - automatically called during action_setup
        Input:
            None
        Output:
            None
        """
        super().initial_setup(**kwargs)
        self.building_type = kwargs.get("building_type", "none")
        self.requirement = status.actions[self.building_type].requirement
        del status.actions[self.action_type]
        status.actions["repair_" + self.building_type] = self
        self.current_building = "none"

        constants.transaction_descriptions[self.action_type] = "repairs"
        self.name = "repair"
        self.allow_critical_failures = False

    def generate_current_roll_modifier(self):
        """
        Description:
            Calculates and returns the current flat roll modifier for this action - this is always applied, while many modifiers are applied only half the time.
                A positive modifier increases the action's success chance and vice versa
        Input:
            None
        Output:
            int: Returns the current flat roll modifier for this action
        """
        return super().generate_current_roll_modifier() + 1

    def generate_action_type(self):
        """
        Description:
            Determines this action's action type, usually based on the class name
        Input:
            None
        Output:
            None
        """
        return "construction"

    def button_setup(self, initial_input_dict):
        """
        Description:
            Completes the inputted input_dict with any values required to create a button linked to this action - automatically called during actor display label
                setup
        Input:
            None
        Output:
            None
        """
        initial_input_dict = super().button_setup(initial_input_dict)
        initial_input_dict["image_id"] = (
            "buildings/buttons/repair_" + self.building_type + ".png"
        )
        initial_input_dict["keybind_id"] = status.actions[
            self.building_type
        ].button.keybind_id
        return initial_input_dict

    def update_tooltip(self):
        """
        Description:
            Sets this tooltip of a button linked to this action
        Input:
            None
        Output:
            None
        """
        message = []
        unit = status.displayed_mob
        if unit != None:
            self.current_building = unit.images[0].current_cell.get_building(
                self.building_type
            )
            message.append(
                "Attempts to repair this tile's "
                + self.current_building.name
                + " for "
                + str(self.get_price())
                + " money"
            )
            if self.building_type in ["port", "train_station", "resource"]:
                message.append("If successful, also repairs this tile's warehouses")
            message.append("Costs all remaining movement points, at least 1")
        return message

    def generate_notification_text(self, subject):
        """
        Description:
            Returns text regarding a particular subject for this action
        Input:
            string subject: Determines type of text to return
        Output:
            string: Returns text for the inputted subject
        """
        text = super().generate_notification_text(subject)
        if subject == "confirmation":
            text += (
                "Are you sure you want to start repairing this "
                + self.current_building.name
                + "? /n /n"
            )
            text += (
                "The planning and materials will cost "
                + str(self.get_price())
                + " money (half of the building's initial cost). /n /n"
            )
            text += (
                "If successful, the "
                + self.current_building.name
                + " will be restored to full functionality. /n /n"
            )
        elif subject == "initial":
            text += (
                "The "
                + self.current_unit.name
                + " attempts to repair the "
                + self.current_building.name
                + ". /n /n"
            )
        elif subject == "success":
            text += (
                "The "
                + self.current_unit.name
                + " successfully repaired the "
                + self.current_building.name
                + ". /n /n"
            )
        elif subject == "failure":
            text += (
                "Little progress was made and the "
                + self.current_unit.officer.name
                + " requests more time and funds to complete the repair. /n /n"
            )
        elif subject == "critical_success":
            text += self.generate_notification_text("success")
            text += (
                "The "
                + self.current_unit.officer.name
                + " managed the repair well enough to become a veteran. /n /n"
            )
        return text

    def get_price(self):
        """
        Description:
            Calculates and returns the price of this action
        Input:
            None
        Output:
            float: Returns price of this action
        """
        building = self.current_building
        if building == "none":
            building = status.displayed_mob.images[0].current_cell.get_building(
                self.building_type
            )
        return building.get_repair_cost()

    def can_show(self):
        """
        Description:
            Returns whether a button linked to this action should be drawn - if correct type of unit selected and building not yet present in tile
        Input:
            None
        Output:
            boolean: Returns whether a button linked to this action should be drawn
        """
        unit = status.displayed_mob
        building = unit.images[0].current_cell.get_building(self.building_type)
        can_show = (
            super().can_show()
            and unit.is_group
            and getattr(unit, self.requirement)
            and building != "none"
            and building.damaged
        )
        return can_show

    def on_click(self, unit):
        """
        Description:
            Used when the player clicks a linked action button - checks if the unit can do the action, proceeding with 'start' if applicable
        Input:
            pmob unit: Unit selected when the linked button is clicked
        Output:
            None
        """
        if super().on_click(unit):
            self.start(unit)

    def pre_start(self, unit):
        """
        Description:
            Prepares for starting an action starting with roll modifiers, setting ongoing action, etc.
        Input:
            pmob unit: Unit selected when the linked button is clicked
        Output:
            none
        """
        super().pre_start(unit)
        self.current_building = unit.images[0].current_cell.get_building(
            self.building_type
        )

    def start(self, unit):
        """
        Description:
            Used when the player clicks on the start action button, displays a choice notification that allows the player to start or not
        Input:
            pmob unit: Unit selected when the linked button is clicked
        Output:
            None
        """
        if super().start(unit):
            constants.notification_manager.display_notification(
                {
                    "message": action_utility.generate_risk_message(self, unit)
                    + self.generate_notification_text("confirmation"),
                    "choices": [
                        {
                            "on_click": (self.middle, []),
                            "tooltip": ["Start " + self.name],
                            "message": "Start " + self.name,
                        },
                        {
                            "tooltip": ["Stop " + self.name],
                            "message": "Stop " + self.name,
                        },
                    ],
                }
            )

    def complete(self):
        """
        Description:
            Used when the player finishes rolling, shows the action's results and makes any changes caused by the result
        Input:
            None
        Output:
            None
        """
        if self.roll_result >= self.current_min_success:
            self.current_building.set_damaged(False)
            actor_utility.calibrate_actor_info_display(
                status.tile_info_display, self.current_unit.images[0].current_cell.tile
            )  # update tile display to show building repair
        super().complete()
