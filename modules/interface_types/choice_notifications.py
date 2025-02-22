# Contains functionality for choice notifications

from . import buttons, action_notifications
from ..util import text_utility, scaling, market_utility, utility
import modules.constants.constants as constants
import modules.constants.status as status
import modules.constants.flags as flags


class choice_notification(action_notifications.action_notification):
    """
    Notification that presents 2 choices and is removed when one is chosen rather than when the notification itself is clicked, causing a different outcome depending on the chosen option
    """

    def __init__(self, input_dict):
        """
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'coordinates': int tuple value - Two values representing x and y coordinates for the pixel location of this element
                'modes': string list value - Game modes during which this element can appear
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'message': string value - Default text for this label, with lines separated by /n
                'ideal_width': int value - Pixel width that this label will try to retain. Each time a word is added to the label, if the word extends past the ideal width, the next line
                    will be started
                'minimum_height': int value - Minimum pixel height of this label. Its height will increase if the contained text would extend past the bottom of the label
                'button_types': string list value - List of string corresponding to the button types of this notification's choice buttons, like ['end turn', 'none']
                    - Each button type could also be a dictionary value, in which case the created button will be an anonymous button with
                        functionality decided by the dictionary's contents
                'choice_info_dict': dictionary value - Dictionary containing any case-specific information for choice buttons to function as intended
        Output:
            None
        """
        button_height = scaling.scale_height(50)
        super().__init__(input_dict)
        self.choice_buttons = []
        self.choice_info_dict = input_dict["choice_info_dict"]
        button_types = input_dict["button_types"]
        for current_button_type_index in range(len(button_types)):
            if type(button_types[current_button_type_index]) == dict:
                init_type = "anonymous button"
            elif button_types[current_button_type_index] == "recruitment":
                init_type = "recruitment choice button"
            else:
                init_type = "choice button"
            self.choice_buttons.append(
                constants.actor_creation_manager.create_interface_element(
                    {
                        "coordinates": (
                            self.x
                            + (
                                current_button_type_index
                                * round(self.width / len(button_types))
                            ),
                            self.y - button_height,
                        ),
                        "width": round(self.width / len(button_types)),
                        "height": button_height,
                        "modes": self.modes,
                        "button_type": button_types[current_button_type_index],
                        "image_id": "misc/paper_label.png",
                        "notification": self,
                        "init_type": init_type,
                    }
                )
            )

    def on_click(self, choice_button_override=False):
        """
        Description:
            Controls this notification's behavior when clicked. Choice notifications do nothing when clicked, instead acting when their choice buttons are clicked
        Input:
            None
        Output:
            None
        """
        if choice_button_override:
            super().on_click()
        return  # does not remove self when clicked

    def update_tooltip(self):
        """
        Description:
            Sets this notification's tooltip to what it should be. Choice notifications prompt the user to click on one of its choice buttons to close it
        Input:
            None
        Output:
            None
        """
        self.set_tooltip(["Choose an option to close this notification"])

    def remove(self):
        """
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program. When a notification is removed, the next notification is shown, if there is one. Choice notifications are removed
                when one of their choice buttons is clicked
        Input:
            None
        Output:
            None
        """
        super().remove()
        for current_choice_button in self.choice_buttons:
            current_choice_button.remove_complete()


class choice_button(buttons.button):
    """
    Button with no keybind that is attached to a choice notification and removes its notification when clicked
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
                'button_type': string value - Determines the function of this button, like 'end turn'
                'keybind_id' = 'none': pygame key object value: Determines the keybind id that activates this button, like pygame.K_n, not passed for no-keybind buttons
                'image_id': string/dictionary/list value - String file path/offset image dictionary/combined list used for this object's image bundle
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'notification': choice_notification value: notification to which this choice button is attached
        Output:
            None
        """
        self.notification = input_dict["notification"]
        if input_dict["button_type"] == "recruitment":
            self.recruitment_type = self.notification.choice_info_dict[
                "recruitment_type"
            ]
            if self.recruitment_type in ["steamship", "slave workers"]:
                self.message = "Purchase"
                self.verb = "purchase"
            else:
                self.message = "Hire"
                self.verb = "hire"
            self.cost = self.notification.choice_info_dict["cost"]
            self.mob_image_id = self.notification.choice_info_dict.get(
                "mob_image_id"
            )  # Image ID provided for most units, but generated on creation for workers

        elif input_dict["button_type"] == "confirm main menu":
            self.message = "Main menu"

        elif input_dict["button_type"] == "confirm remove minister":
            self.message = "Confirm"

        elif input_dict["button_type"] == "quit":
            self.message = "Exit game"

        elif input_dict["button_type"] == "none":
            self.message = "Cancel"

        else:
            self.message = input_dict["button_type"].capitalize()
        super().__init__(input_dict)
        self.font = constants.fonts["default_notification"]
        self.in_notification = True

    def on_click(self):
        """
        Description:
            Controls this button's behavior when clicked. Choice buttons remove their notifications when clicked, along with the normal behaviors associated with their button_type
        Input:
            None
        Output:
            None
        """
        super().on_click()
        self.notification.on_click(choice_button_override=True)

    def draw(self):
        """
        Description:
            Draws this button below its choice notification and draws a description of what it does on top of it
        Input:
            None
        Output:
            None
        """
        super().draw()
        if self.showing:
            constants.game_display.blit(
                text_utility.text(self.message, self.font),
                (
                    self.x + scaling.scale_width(10),
                    constants.display_height - (self.y + self.height),
                ),
            )

    def update_tooltip(self):
        """
        Description:
            Sets this image's tooltip to what it should be, depending on its button_type
        Input:
            None
        Output:
            None
        """
        if self.button_type == "recruitment":
            if self.recruitment_type in [
                "African worker village",
                "African worker slums",
                "African worker labor broker",
            ]:
                self.set_tooltip(
                    [
                        utility.capitalize(self.verb)
                        + " an African worker for "
                        + str(self.cost)
                        + " money"
                    ]
                )
            else:
                self.set_tooltip(
                    [
                        utility.capitalize(self.verb)
                        + " a "
                        + self.recruitment_type
                        + " for "
                        + str(self.cost)
                        + " money"
                    ]
                )

        elif self.button_type == "end turn":
            self.set_tooltip(["End the current turn"])

        elif self.button_type == "confirm main menu":
            self.set_tooltip(["Exits to the main menu without saving"])

        elif self.button_type == "quit":
            self.set_tooltip(["Exits the game without saving"])

        elif self.button_type == "none":
            self.set_tooltip(["Cancel"])

        else:
            self.set_tooltip(
                [self.button_type.capitalize()]
            )  # stop trading -> ['Stop trading']


class recruitment_choice_button(choice_button):
    """
    Choice_button that recruits a unit when clicked
    """

    def on_click(self):
        """
        Description:
            Controls this button's behavior when clicked. Recruitment choice buttons recruit a unit, pay for the unit's cost, and remove their attached notification when clicked
        Input:
            None
        Output:
            None
        """
        input_dict = {"select_on_creation": True}
        if self.recruitment_type == "slave workers":
            constants.money_tracker.change(-1 * self.cost, "unit_recruitment")
            input_dict.update(status.worker_types["slave"].generate_input_dict())
            input_dict["grids"] = [status.slave_traders_grid]
            attached_cell = input_dict["grids"][0].cell_list[0][0]
            input_dict["coordinates"] = (attached_cell.x, attached_cell.y)
            input_dict["modes"] = input_dict["grids"][0].modes
            input_dict["purchased"] = True
            constants.actor_creation_manager.create(False, input_dict)

        elif self.recruitment_type == "African worker village":
            status.displayed_tile.cell.get_building("village").recruit_worker()

        elif self.recruitment_type == "African worker slums":
            status.displayed_tile.cell.get_building("slums").recruit_worker()

        elif self.recruitment_type == "African worker labor broker":
            input_dict = {
                "select_on_creation": True,
                "coordinates": (
                    status.displayed_tile.cell.x,
                    status.displayed_tile.cell.y,
                ),
                "grids": [
                    status.displayed_tile.cell.grid,
                    status.displayed_tile.cell.grid.mini_grid,
                ],
                "modes": status.displayed_tile.cell.grid.modes,
            }
            input_dict.update(status.worker_types["African"].generate_input_dict())
            constants.money_tracker.change(
                -1 * self.notification.choice_info_dict["cost"], "unit_recruitment"
            )
            self.notification.choice_info_dict["village"].change_population(-1)
            market_utility.attempt_worker_upkeep_change(
                "decrease", "African"
            )  # adds 1 worker to the pool
            worker = constants.actor_creation_manager.create(False, input_dict)

        else:
            input_dict["coordinates"] = (0, 0)
            if (
                status.displayed_tile
            ):  # When recruiting in Asia, slave traders, Africa, etc., tile will be selected - use that tile's grids
                input_dict["grids"] = status.displayed_tile.grids
            else:  # If no tile selected, assume recruiting in Europe
                input_dict["grids"] = [status.europe_grid]
            if self.mob_image_id:
                input_dict["image"] = self.mob_image_id
            input_dict["modes"] = input_dict["grids"][0].modes
            constants.money_tracker.change(-1 * self.cost, "unit_recruitment")
            if self.recruitment_type in constants.officer_types:
                name = ""
                for character in self.recruitment_type:
                    if not character == "_":
                        name += character
                    else:
                        name += " "
                input_dict["name"] = name
                input_dict["init_type"] = self.recruitment_type
                input_dict["officer_type"] = self.recruitment_type

            elif self.recruitment_type.endswith(" workers"):
                input_dict.update(
                    status.worker_types[
                        self.recruitment_type.replace(" workers", "")
                    ].generate_input_dict()
                )  # Like European workers

            elif self.recruitment_type == "steamship":
                image_dict = {
                    "default": self.mob_image_id,
                    "uncrewed": "mobs/steamship/uncrewed.png",
                }
                input_dict["image_dict"] = image_dict
                input_dict["name"] = "steamship"
                input_dict["crew"] = "none"
                input_dict["init_type"] = "ship"
            constants.actor_creation_manager.create(False, input_dict)
        super().on_click()
