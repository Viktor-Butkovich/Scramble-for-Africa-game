import pickle
import os
from typing import List
from ...util import scaling, action_utility
import modules.constants.constants as constants
import modules.constants.status as status


class achievement_manager_template:
    """
    Object that controls achievements
    """

    def __init__(self):
        """
        Description:
            Initializes this object
        Input:
            None
        Output:
            None
        """
        self.victory_conditions = []
        self.victory_conditions: List[str] = ["Rich"]
        self.achievements: List[str] = []
        loaded_achievements = []
        if os.path.exists(
            "save_games/achievements.pickle"
        ) and not constants.effect_manager.effect_active("reset_achievements"):
            with open("save_games/achievements.pickle", "rb") as file:
                loaded_achievements = pickle.load(file)
        self.achievement_display = (
            constants.actor_creation_manager.create_interface_element(
                {
                    "coordinates": scaling.scale_coordinates(
                        constants.default_display_width - 45, 100
                    ),
                    "width": scaling.scale_width(10),
                    "height": scaling.scale_height(30),
                    "modes": [
                        "strategic",
                        "main_menu",
                        "new_game_setup",
                    ],
                    "init_type": "ordered collection",
                    "direction": "vertical",
                    "reversed": True,
                }
            )
        )
        for achievement in loaded_achievements:
            self.achieve(achievement, verbose=False)

    def achieve(self, achievement_type: str, verbose: bool = True):
        """
        Description:
            Achieves an achievement, creating corresponding interface element and saving the achievement
        Input:
            None
        Output:
            None
        """
        if achievement_type in self.victory_conditions and verbose == True:
            if status.current_country.name == "Britain":
                self.achieve("Victorian Man")

        self.achievements.append(achievement_type)
        constants.actor_creation_manager.create_interface_element(
            {
                "coordinates": scaling.scale_coordinates(0, 0),
                "width": scaling.scale_width(45),
                "height": scaling.scale_height(45),
                "image_id": f"achievements/{achievement_type}.png",
                "init_type": "tooltip free image",
                "parent_collection": self.achievement_display,
                "tooltip_text": [
                    achievement_type + ": " + self.get_description(achievement_type),
                    self.get_quote(achievement_type),
                ],
            }
        )
        with open("save_games/achievements.pickle", "wb") as handle:
            pickle.dump(self.achievements, handle)
            handle.close()
        if verbose:
            if achievement_type in self.victory_conditions:
                constants.notification_manager.display_notification(
                    {
                        "message": f'Victory achievement unlocked - "{achievement_type}": {self.get_description(achievement_type)} /n /n{self.get_quote(achievement_type)} /n /n',
                        "attached_interface_elements": [
                            action_utility.generate_free_image_input_dict(
                                f"achievements/{achievement_type}.png",
                                200,
                                override_input_dict={
                                    "member_config": {
                                        "order_x_offset": scaling.scale_width(-75),
                                        "centered": True,
                                    }
                                },
                            )
                        ],
                        "choices": ["continue", "confirm main menu"],
                    }
                )
            else:
                constants.notification_manager.display_notification(
                    {
                        "message": f'Achievement unlocked - "{achievement_type}": {self.get_description(achievement_type)} /n /n{self.get_quote(achievement_type)} /n /n',
                        "attached_interface_elements": [
                            action_utility.generate_free_image_input_dict(
                                f"achievements/{achievement_type}.png",
                                200,
                                override_input_dict={
                                    "member_config": {
                                        "order_x_offset": scaling.scale_width(-75),
                                        "centered": True,
                                    }
                                },
                            )
                        ],
                        "notification_type": "action",
                    }
                )

    def get_description(self, achievement_type: str) -> str:
        """
        Description:
            Returns the description of an achievement
        Input:
            None
        Output:
            None
        """
        return {
            "Rich": "Start a turn with 10,000 money",
            "Victorian Man": "Win a game as Britain",
        }[achievement_type]

    def get_quote(self, achievement_type: str) -> str:
        return {
            "Rich": '"I believe the power to make money is a gift from God." - John D Rockefeller',
            "Victorian Man": '"Remember that you are an Englishman, and have consequently won first prize in the lottery of life." - Cecil John Rhodes',
        }.get(achievement_type, "")

    def check_achievements(self, achievement_type: str = None) -> str:
        """
        Description:
            Checks if the inputted achievement is being achieved, or checks all achievements if no input is given
        """
        if (
            achievement_type == "Rich"
            or achievement_type == "start of turn"
            or achievement_type == None
        ):
            if (
                constants.money_tracker.get() >= 1000
                and not "Rich" in self.achievements
            ):
                self.achieve("Rich")
