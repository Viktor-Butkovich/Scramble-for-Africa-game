# Contains all functionality for public relations campaigns

import pygame
from . import action
from ..util import action_utility, text_utility, actor_utility
import modules.constants.constants as constants
import modules.constants.status as status


class religious_campaign(action.campaign):
    """
    Action for evangelist in Europe to recruit church volunteers
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
        constants.transaction_descriptions[self.action_type] = "religious campaigning"
        self.name = "religious campaign"

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
        initial_input_dict["keybind_id"] = pygame.K_t
        return super().button_setup(initial_input_dict)

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
            "Attempts to campaign for church volunteers for "
            + str(self.get_price())
            + " money",
            "Can only be done in Europe",
            "If successful, recruits a free unit of church volunteers that can join with an evangelist to form a group of missionaries that can convert native villages",
            "Costs all remaining movement points, at least 1",
            "Each "
            + self.name
            + " attempted doubles the cost of other "
            + self.name
            + "s in the same turn",
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
            text += "Are you sure you want to start a religious campaign? /n /nIf successful, a religious campaign will convince church volunteers to join you, allowing the formation of groups of missionaries that can convert native "
            text += (
                "villages. /n /nThe campaign will cost "
                + str(self.get_price())
                + " money. /n /n"
            )
        elif subject == "initial":
            text += "The evangelist campaigns for the support of church volunteers to join him in converting the African natives. /n /n"
        elif subject == "success":
            text += "Inspired by the evangelist's message to save the heathens from their own ignorance, a group of church volunteers joins you. /n /n"
        elif subject == "failure":
            text += "Whether by a lack of charisma, a reluctant audience, or a doomed cause, the evangelist fails to gather any volunteers. /n /n"
        elif subject == "critical_failure":
            text += self.generate_notification_text("failure")
            text += "The evangelist is disturbed by the lack of faith of your country's people and decides to abandon your company. /n /n"
        elif subject == "critical_success":
            text += self.generate_notification_text("success")
            text += "With fiery word and true belief in his cause, the evangelist becomes a veteran and will be more successful in future ventures. /n /n"
        return text

    def generate_attached_interface_elements(self, subject):
        """
        Description:
            Returns list of input dicts of interface elements to attach to a notification regarding a particular subject for this action
        Input:
            string subject: Determines input dicts
        Output:
            dictionary list: Returns list of input dicts for inputted subject
        """
        return_list = super().generate_attached_interface_elements(subject)
        if subject in ["success", "critical_success"]:
            return_list.append(
                action_utility.generate_free_image_input_dict(
                    [
                        "buttons/default_button_alt.png",
                        actor_utility.generate_unit_component_image_id(
                            "mobs/church volunteers/default.png", "left", to_front=True
                        ),
                        actor_utility.generate_unit_component_image_id(
                            "mobs/church volunteers/default.png", "right", to_front=True
                        ),
                    ],
                    200,
                    override_input_dict={
                        "member_config": {
                            "second_dimension_coordinate": -2,
                            "centered": True,
                        }
                    },
                )
            )
        return return_list

    def generate_audio(self, subject):
        """
        Description:
            Returns list of audio dicts of sounds to play when notification appears, based on the inputted subject and other current circumstances
        Input:
            string subject: Determines sound dicts
        Output:
            dictionary list: Returns list of sound dicts for inputted subject
        """
        audio = super().generate_audio(subject)
        if subject == "roll_finished":
            if self.roll_result >= self.current_min_success:
                if status.current_country.religion == "protestant":
                    sound_id = "effects/onward_christian_soldiers"
                elif status.current_country.religion == "catholic":
                    sound_id = "effects/ave_maria"
                audio.append({"sound_id": sound_id, "dampen_music": True})
        return audio

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
            and status.displayed_mob.is_officer
            and status.displayed_mob.officer_type == "evangelist"
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
            if status.europe_grid in unit.grids:
                self.start(unit)
            else:
                text_utility.print_to_screen(
                    self.name.capitalize() + "s are only possible in Europe"
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
                            "tooltip": [
                                "Starts a "
                                + self.name
                                + ", possibly convincing church volunteers to join you"
                            ],
                            "message": "Start campaign",
                        },
                        {"tooltip": ["Stop " + self.name], "message": "Stop campaign"},
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
            church_volunteers = constants.actor_creation_manager.create(
                False,
                {
                    "coordinates": (0, 0),
                    "grids": [status.europe_grid],
                    "image": "mobs/church volunteers/default.png",
                    "name": "church volunteers",
                    "modes": ["strategic", "europe"],
                    "init_type": "church_volunteers",
                    "worker_type": "religious",  # not european - doesn't count as a European worker for upkeep
                },
            )

            self.current_unit = constants.actor_creation_manager.create_group(
                church_volunteers, self.current_unit
            )

        elif self.roll_result <= self.current_max_crit_fail:
            self.current_unit.die("quit")
        super().complete()
