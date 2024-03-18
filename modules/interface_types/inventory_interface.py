# Contains inventory-specific interface classes

import pygame
from .interface_elements import ordered_collection
from .buttons import button
from ..util import actor_utility, utility, main_loop_utility, text_utility, minister_utility
import modules.constants.status as status
import modules.constants.constants as constants

class inventory_grid(ordered_collection):
    '''
    Ordered collection to display actor inventory
    '''
    def __init__(self, input_dict) -> None: #change inventory display to a collection so that it orders correctly
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
                'separation' = scaling.scale_height(5): int value - Distance to set between ordered members
                'direction' = 'vertical': string value - Direction to order members in
                'reversed' = False: boolean value - Whether to reverse the order of members in the specified direction (top to bottom or bottom to top)
                'second_dimension_increment' = 0: int value - Increment between each row/column of this collection - 2 elements with a difference of 1 second dimension
                    coordinate will be the increment away along the second dimension
                'anchor_coordinate' = None: int value - Optional relative coordinate around which each row/column of collection will be centered 
        Output:
            None
        '''
        self.inventory_page = 0
        self.actor = None
        super().__init__(input_dict)

    def scroll_update(self) -> None:
        '''
        Description:
            Updates the display when this collection is scrolled
        Input:
            None
        Output:
            None
        '''
        actor_type: str = self.get_actor_type()
        actor = getattr(status, 'displayed_' + actor_type)
        actor_utility.calibrate_actor_info_display(getattr(status, actor_type + '_info_display'), actor)
        actor_utility.calibrate_actor_info_display(getattr(status, actor_type + '_inventory_info_display'), None)
        return

    def show_scroll_button(self, scroll_button) -> bool:
        '''
        Description:
            Returns whether a particular scroll button should be shown
        Input:
            scroll_button scroll_button: Button being checked
        Output:
            bool: Returns whether the inputted scroll button should be shown
        '''
        actor_type: str = self.get_actor_type()
        if scroll_button.increment > 0: # If scroll down
            actor = getattr(status, 'displayed_' + actor_type)
            functional_capacity: int = max(actor.get_inventory_used(), actor.inventory_capacity)
            return(functional_capacity > (self.inventory_page + 1) * 27) # Can scroll down if another page exists
        elif scroll_button.increment < 0: # If scroll up
            return(self.inventory_page > 0) # Can scroll up if there are any previous pages

    def calibrate(self, new_actor, override_exempt=False):
        '''
        Description:
            Atttaches this collection and its members to inputted actor and updates their information based on the inputted actor
        Input:
            string/actor new_actor: The displayed actor whose information is matched by this label. If this equals 'none', the label does not match any actors.
        Output:
            None
        '''
        if self.inventory_page != 0 and new_actor != 'none' and not new_actor.infinite_inventory_capacity:
            functional_capacity = max(new_actor.inventory_capacity, new_actor.get_inventory_used())
            max_pages_required = (functional_capacity // 27)
            if max_pages_required < self.inventory_page:
                self.inventory_page = 0
        super().calibrate(new_actor, override_exempt)

class item_icon(button):
    '''
    Button that can calibrate to an item 
    '''
    def __init__(self, input_dict):
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
                    Example of possible image_id: ['buttons/default_button_alt.png', {'image_id': 'mobs/default/default.png', 'size': 0.95, 'x_offset': 0, 'y_offset': 0, 'level': 1}]
                    - Signifies default button image overlayed by a default mob image scaled to 0.95x size
                'icon_index': int value - Index in inventory that this button will display
        Output:
            None
        '''
        self.icon_index: int = input_dict['icon_index']
        self.current_item: str = None
        self.in_inventory_capacity: bool = False
        self.default_image_id = input_dict['image_id']
        self.actor_type = input_dict['actor_type']
        self.actor = 'none'
        input_dict['button_type'] = 'item_icon'
        super().__init__(input_dict)

    def get_display_order(self):
        '''
        Description:
            To determine whether cell is used in a particular configuration, convert
                0  1  2  3  4  5  6  7  8
                9  10 11 12 13 14 15 16 17
                18 19 20 21 22 23 24 25 26
            To
                0  1  2 9  10 11 18 19 20
                3  4  5 12 13 14 21 22 23
                6  7  8 15 16 17 24 25 26
            0-2: no change
            3-5: add 6
            6-8: add 12
            9-11: subtract 6
            12-14: no change
            15-17: add 6
            18-20: subtract 12
            21-23: subtract 6
            24-26: no change
        Input:
            None
        Output:
            int: Returns the "line number" of this item icon - if this number is < the number of items to display, this icon is active
        '''
        return((self.parent_collection.inventory_page * 27) + self.icon_index + {0: 0, 1: 6, 2: 12, 3: -6, 4: 0, 5: 6, 6: -12, 7: -6, 8: 0}[self.icon_index // 3])

    def calibrate(self, new_actor):
        '''
        Description:
            Attaches this button to the inputted actor and updates this button's image to that of the actor. May also display a shader over this button, if its particular
                requirements are fulfilled
        Input:
            string/actor new_actor: The minister whose information is matched by this button. If this equals 'none', this button is detached from any ministers
            bool override_exempt: Optional parameter that may be given to calibrate functions, does nothing for buttons
        Output:
            None
        '''
        self.actor = new_actor
        if new_actor != 'none':
            functional_capacity: int = max(new_actor.get_inventory_used(), new_actor.inventory_capacity)
            display_index: int = self.get_display_order()
            self.in_inventory_capacity = (functional_capacity >= display_index + 1 or new_actor.infinite_inventory_capacity)
            if self.in_inventory_capacity: #if inventory capacity 9 >= index 8 + 1, allow. If inventory capacity 9 >= index 9 + 1, disallow
                self.current_item = new_actor.check_inventory(display_index)
                if self.current_item:
                    if new_actor.inventory_capacity >= display_index + 1 or new_actor.infinite_inventory_capacity: # If item in capacity
                        self.image.set_image(utility.combine(self.default_image_id, 'misc/green_circle.png', 'scenery/resources/' + self.current_item + '.png'))
                    else: # If item over capacity
                        self.image.set_image(['misc/green_circle.png', 'scenery/resources/' + self.current_item + '.png', 'misc/warning_icon.png'])
                else:
                    self.image.set_image(self.default_image_id)
                    if self.icon_index == 0 and new_actor.infinite_inventory_capacity and self.parent_collection.inventory_page > 0:
                        # Force scroll up if on empty page in infinite warehouse
                        self.parent_collection.inventory_page -= 1
                        self.parent_collection.scroll_update()
        super().calibrate(new_actor)

    def draw(self):
        '''
        Description:
            Draws this button below its choice notification, along with an outline if it is selected
        Input:
            None
        Output:
            None
        '''
        if self.showing:
            if self == getattr(status, 'displayed_' + self.actor_type):
                pygame.draw.rect(constants.game_display, constants.color_dict['bright green'], self.outline, width=2)
        super().draw()

    def can_show(self, skip_parent_collection=False):
        '''
        Description:
            Returns whether this button can be shown - an item icon is shown if the corresponding actor has sufficient inventory capacity to fill this slot
        Input:
            None
        Output:
            boolean: Returns True if this button can appear, otherwise returns False
        '''
        return(super().can_show(skip_parent_collection=skip_parent_collection) and self.in_inventory_capacity)

    def update_tooltip(self):
        '''
        Description:
            Sets this button's tooltip depending on its contained item
        Input:
            None
        Output:
            None
        '''
        if self.current_item:
            self.set_tooltip([self.current_item.capitalize()])
        else:
            self.set_tooltip(['Empty'])

    def on_click(self):
        '''
        Description:
            Calibrates mob_inventory_info_display or tile_inventory_info_display to this icon, depending on this icon's actor type
        Input:
            None
        Output:
            None
        '''
        if not self.can_show(skip_parent_collection=True):
            self.current_item = None
        if self.current_item:
            actor_utility.calibrate_actor_info_display(getattr(status, self.actor_type + '_info_display'), self)
            if self.actor_type == 'mob_inventory':
                actor_utility.calibrate_actor_info_display(getattr(status, 'tile_inventory_info_display'), None)
            elif self.actor_type == 'tile_inventory':
                actor_utility.calibrate_actor_info_display(getattr(status, 'mob_inventory_info_display'), None)
        else:
            actor_utility.calibrate_actor_info_display(getattr(status, self.actor_type + '_info_display'), None)

    def transfer(self, amount):
        '''
        Description:
            Drops or picks up the inputted amount of this tile's current item type, depending on if this is a tile or mob item icon
        Input:
            str/int amount: Amount of item to transfer, either 'all' or a number
        Output:
            None
        '''
        if main_loop_utility.action_possible():
            if minister_utility.positions_filled():
                displayed_mob = status.displayed_mob
                displayed_tile = status.displayed_tile
                if displayed_mob and displayed_tile and displayed_mob.images[0].current_cell.tile == displayed_tile:
                    if amount == 'all':
                        if self.actor_type == 'tile_inventory':
                            amount = displayed_tile.get_inventory(self.current_item)
                        elif self.actor_type == 'mob_inventory':
                            amount = displayed_mob.get_inventory(self.current_item)
                    elif self.actor_type == 'mob_inventory' and amount > displayed_mob.get_inventory(self.current_item):
                        text_utility.print_to_screen('This unit does not have enough ' + self.current_item + ' to transfer.')
                        return
                    elif self.actor_type == 'tile_inventory' and amount > displayed_tile.get_inventory(self.current_item):
                        text_utility.print_to_screen('This tile does not have enough ' + self.current_item + ' to transfer.')
                        return
                    
                    if displayed_mob.is_vehicle and displayed_mob.vehicle_type == 'train' and not displayed_tile.cell.has_intact_building('train_station'):
                        text_utility.print_to_screen('A train can only transfer cargo at a train station.')
                        return
                    
                    if self.actor_type == 'tile_inventory':
                        if displayed_mob.get_inventory_remaining(amount) < 0:
                            amount = displayed_mob.get_inventory_remaining()
                            if amount == 0:
                                text_utility.print_to_screen('This unit can not pick up any ' + self.current_item + '.')
                                return

                    if displayed_mob.sentry_mode:
                        displayed_mob.set_sentry_mode(False)

                    if self.actor_type == 'tile_inventory': # Pick up item(s)
                        displayed_mob.change_inventory(self.current_item, amount)
                        displayed_tile.change_inventory(self.current_item, amount * -1)
                        actor_utility.select_interface_tab(status.mob_tabbed_collection, status.mob_inventory_collection)
                        actor_utility.calibrate_actor_info_display(status.tile_info_display, displayed_tile)

                    elif self.actor_type == 'mob_inventory': # Drop item(s)
                        displayed_tile.change_inventory(self.current_item, amount)
                        displayed_mob.change_inventory(self.current_item, amount * -1)
                        actor_utility.select_interface_tab(status.tile_tabbed_collection, status.tile_inventory_collection)
                        actor_utility.calibrate_actor_info_display(status.mob_info_display, displayed_mob)

                    self.on_click()

                elif self.actor_type == 'mob_inventory':
                    text_utility.print_to_screen('There is no tile to transfer this commodity to.')
                elif self.actor_type == 'tile_inventory':
                    text_utility.print_to_screen('There is no unit to transfer this commodity to.')
        else:
            text_utility.print_to_screen('You are busy and cannot transfer commodities.')
