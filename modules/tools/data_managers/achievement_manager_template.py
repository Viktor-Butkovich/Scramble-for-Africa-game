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
        self.victory_conditions: List[str] = [
            "Entrepreneur",
            "Heart of Darkness",
            "It Belongs in a Museum",
            "Industrialist",
            "Minimum Wage",
        ]
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
                        constants.default_display_width - 50, 100
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
        if not achievement_type in self.achievements:
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
                        achievement_type
                        + ": "
                        + self.get_description(achievement_type),
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
                                    120,
                                    override_input_dict={
                                        "member_config": {
                                            "order_x_offset": scaling.scale_width(-75),
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
                                    120,
                                    override_input_dict={
                                        "member_config": {
                                            "order_x_offset": scaling.scale_width(-75),
                                        }
                                    },
                                )
                            ],
                            "notification_type": "action",
                        }
                    )

        if achievement_type in self.victory_conditions and verbose == True:
            if (
                status.current_country.name == "Britain"
                and "Victorian Man" not in self.achievements
            ):
                self.achieve("Victorian Man")
            elif (
                status.current_country.name == "France"
                and "L'enterprise, c'est moi" not in self.achievements
            ):
                self.achieve("L'enterprise, c'est moi")
            elif (
                status.current_country.name == "Germany"
                and "Second Reich" not in self.achievements
            ):
                self.achieve("Second Reich")
            elif (
                status.current_country.name == "Belgium"
                and "Absolutely Flemished" not in self.achievements
            ):
                self.achieve("Absolutely Flemished")
            elif (
                status.current_country.name == "Italy"
                and "New Empire" not in self.achievements
            ):
                self.achieve("New Empire")
            elif (
                status.current_country.name == "Portugal"
                and "Mapa Cor-de-Rosa" not in self.achievements
            ):
                self.achieve("Mapa Cor-de-Rosa")

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
            "Entrepreneur": "Start a turn with 10,000 money",
            "Heart of Darkness": "Explore the entire map",
            "It Belongs in a Museum": "Complete 3 lore missions",
            "Industrialist": "Upgrade a resource production facility to 6 efficiency and 6 scale",
            "Minimum Wage": "Decrease African worker upkeep to 0.5 while employing at least 10 African workers",
            "Victorian Man": "Win a game as Britain",
            "L'enterprise, c'est moi": "Win a game as France",
            "Second Reich": "Win a game as Germany",
            "Absolutely Flemished": "Win a game as Belgium",
            "Mapa Cor-de-Rosa": "Win a game as Portugal",
            "New Empire": "Win a game as Italy",
        }[achievement_type]

    def get_quote(self, achievement_type: str) -> str:
        return {
            "Entrepreneur": '"I believe the power to make money is a gift from God." - John D. Rockefeller',
            "Heart of Darkness": '"We live in the flicker - may it last as long as the old earth keeps rolling! But darkness was here yesterday." - Joseph Conrad',
            "It Belongs in a Museum": '"Archaeologists only look at what lies beneath their feet. The sky and heavens don\'t exist for them." - Agatha Christie',
            "Industrialist": '"Never be a minion, always be an owner." - Cornelius Vanderbilt',
            "Minimum Wage": '"What an alteration there would be if they were brought under Anglo-Saxon influence, look again at the extra employment a new country added to our dominions gives." - Cecil John Rhodes',
            "Victorian Man": '"Remember that you are an Englishman, and have consequently won first prize in the lottery of life." - Cecil John Rhodes',
            "L'enterprise, c'est moi": 'I see only my objective - the obstacles must give way." - Napoleon Bonaparte',
            "Second Reich": '"The great questions of the day will not be settled by means of speeches and majority decisions but by iron and blood." - Otto von Bismarck',
            "Absolutely Flemished": 'There are no small countries, only small minds." - Leopold II',
            "Mapa Cor-de-Rosa": '"To speak of Portuguese colonies in East Africa is to speak of a mere fiction - a fiction colourably sustained by a few scattered seaboard settlements, beyond whose narrow littoral and local limits colonisation and government have no existence." - Henry O\'Neill',
            "New Empire": '"I offer neither pay, nor quarters, nor food; I offer only hunger, thirst, forced marches, battles, and death. Let him who loves his country with his heart, and not merely with his lips, follow me." - Giuseppe Garibaldi',
        }.get(achievement_type, "")

    def check_achievements(self, achievement_type: str = None) -> None:
        """
        Description:
            Checks if the inputted achievement is being achieved, or checks all achievements if no input is given
        """
        if achievement_type == "Entrepreneur" or achievement_type == "start of turn":
            if constants.money_tracker.get() >= 10000:
                self.achieve("Entrepreneur")

        if achievement_type == "Heart of Darkness":
            if status.strategic_map_grid:
                for current_cell in status.strategic_map_grid.get_flat_cell_list():
                    if not current_cell.visible:
                        return
                self.achieve("Heart of Darkness")

        if achievement_type == "It Belongs in a Museum":
            if len(constants.completed_lore_missions) >= 3:
                self.achieve("It Belongs in a Museum")

        if achievement_type == "Minimum Wage":
            if (
                status.worker_types["African"].upkeep <= 0.5
                and status.worker_types["African"].number >= 10
            ):
                self.achieve("Minimum Wage")
