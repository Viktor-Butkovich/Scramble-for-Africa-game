# Contains all functionality for building canoes

import pygame
from . import action
from ..util import action_utility, text_utility, actor_utility
import modules.constants.constants as constants
import modules.constants.status as status
import modules.constants.flags as flags


class canoe_consruction(action.action):
    """
    Action for expedition/safari to build canoes
    """

    def initial_setup(self):
        """
        Description:
            Completes any configuration required for this action during setup - automatically called during action_setup
        Input:
            None
        Output:
            None
        """
        super().initial_setup()
        constants.transaction_descriptions[self.action_type] = "canoe construction"
        self.name = "canoe construction"
        self.allow_critical_failures = False

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
        initial_input_dict["keybind_id"] = pygame.K_v
        initial_input_dict["image_id"] = [
            "buttons/default_button.png",
            "misc/green_circle.png",
            "items/canoes.png",
            "misc/repair_hammer.png",
        ]
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
        return [
            f"Attempts to build canoes for {constants.action_prices[self.action_type]} money",
            "If successful, builds and equips canoes for this unit",
            "African workers can build canoes more easily",
            "Easier than buying canoes from an aggressive village",
            "Costs all remaining movement points, at least 1",
        ]

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
            text = "Are you sure you want to attempt to build canoes? If successful, this unit will be equipped with canoes. /n /n"
            text += f"The {self.name} will cost {constants.action_prices[self.action_type]} money. /n /n"
            if self.current_unit.worker.worker_type in ["African", "slave"]:
                text += "The African workers have some familiarity with canoes and can build them more easily. /n /n"
            else:
                text += "The workers do not have familiarity with canoes and will have difficulty building them. /n /n"
        elif subject == "initial":
            text += (
                f"The {status.displayed_mob.group_type} tries to build canoes. /n /n"
            )
        elif subject == "success":
            text += (
                f"The {status.displayed_mob.group_type} successfuly built canoes. /n /n"
            )
        elif subject == "failure":
            text += f"The {status.displayed_mob.group_type} failed to make any functional canoes. /n /n"
        elif subject == "critical_success":
            text += self.generate_notification_text("success")
            text += f"The {status.displayed_mob.officer.name} is now a veteran and will be more successful in future ventures. /n /n"
        return text

    def generate_current_roll_modifier(self):
        """
        Description:
            Calculates and returns the current flat roll modifier for this action - this is always applied, while many modifiers are applied only half the time
                A positive modifier increases the action's success chance and vice versa
        Input:
            None
        Output:
            int: Returns the current flat roll modifier for this action
        """
        roll_modifier = super().generate_current_roll_modifier()
        if not self.current_unit.worker.worker_type in ["African", "slave"]:
            roll_modifier -= 1
        return roll_modifier

    def can_show(self):
        """
        Description:
            Returns whether a button linked to this action should be drawn
        Input:
            None
        Output:
            boolean: Returns whether a button linked to this action should be drawn
        """
        return (
            super().can_show()
            and status.displayed_mob.is_group
            and (
                status.displayed_mob.group_type == "expedition"
                or status.displayed_mob.group_type == "safari"
            )
        )

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
            if unit.equipment.get("canoes", False):
                text_utility.print_to_screen("This unit already has canoes equipped.")
            else:
                self.start(unit)

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
                            "tooltip": ["Start canoe construction"],
                            "message": "Start construction",
                        },
                        {"tooltip": ["Cancel"], "message": "Cancel"},
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
        super().complete()
        village = self.current_unit.images[0].current_cell.get_building("village")
        if self.roll_result >= self.current_min_success:
            status.equipment_types["canoes"].equip(self.current_unit)
            actor_utility.select_interface_tab(
                status.mob_tabbed_collection, status.mob_inventory_collection
            )
