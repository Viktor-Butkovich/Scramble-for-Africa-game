#Contains functionality for buttons

import pygame
import time
from . import images
from . import text_tools
from . import scaling
from . import main_loop_tools
from . import actor_utility
from . import utility
from . import turn_management_tools
from . import market_tools
from . import notification_tools
from . import game_transitions
from . import minister_utility

class button():
    '''
    An object does something when clicked or when the corresponding key is pressed
    '''
    def __init__(self, coordinates, width, height, color, button_type, keybind_id, modes, image_id, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string color: Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
            string button_type: Determines the function of this button, like 'end turn'
            pygame key object keybind_id: Determines the keybind id that activates this button, like pygame.K_n
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.global_manager = global_manager
        self.has_released = True
        self.modes = modes
        self.button_type = button_type
        self.global_manager.get('button_list').append(self)
        if keybind_id == 'none':
            self.has_keybind = False
            self.keybind_id = 'none'
        else:
            self.has_keybind = True
            self.keybind_id = keybind_id
            self.set_keybind(self.keybind_id)
        self.x, self.y = coordinates
        self.width = width
        self.height = height
        self.Rect = pygame.Rect(self.x, self.global_manager.get('display_height') - (self.y + self.height), self.width, self.height) #Pygame Rect object to track mouse collision
        self.image = images.button_image(self, self.width, self.height, image_id, self.global_manager)
        self.color = self.global_manager.get('color_dict')[color]
        self.outline_width = 2
        self.showing_outline = False
        self.showing_background = True
        self.outline = pygame.Rect(self.x - self.outline_width, self.global_manager.get('display_height') - (self.y + self.height + self.outline_width), self.width + (2 * self.outline_width), self.height + (self.outline_width * 2)) #Pygame Rect object that appears around a button when pressed
        self.button_type = button_type
        self.tooltip_text = []
        self.update_tooltip()
        self.confirming = False
        self.being_pressed = False
        self.in_notification = False #used to prioritize notification buttons in drawing and tooltips

    def set_y(self, attached_label): #called by actor display labels to move to their y position
        '''
        Description:
            Sets this button's y position to be at the same height as the inputted label
        Input:
            actor_display_label attached_label: Label to match this button's y position with
        Output:
            None
        '''
        self.y = attached_label.y
        self.Rect.y = self.global_manager.get('display_height') - (attached_label.y + self.height)
        self.outline.y = self.Rect.y - self.outline_width

    def update_tooltip(self):
        '''
        Description:
            Sets this button's tooltip to what it should be, depending on its button_type
        Input:
            None
        Output:
            None
        '''
        if self.button_type in ['move up', 'move down', 'move left', 'move right']:
            direction = 'none'
            x_change = 0
            y_change = 0
            if self.button_type == 'move up':
                direction = 'north'
                non_cardinal_direction = 'up'
                y_change = 1
            elif self.button_type == 'move down':
                direction = 'south'
                non_cardinal_direction = 'down'
                y_change = -1
            elif self.button_type == 'move left':
                direction = 'west'
                non_cardinal_direction = 'left'
                x_change = -1
            elif self.button_type == 'move right':
                direction = 'east'
                non_cardinal_direction = 'right'
                x_change = 1
            tooltip_text = ["Press to move to the " + direction]
            selected_list = actor_utility.get_selected_list(self.global_manager)
            if len(selected_list) > 0:
                current_mob = selected_list[0]
                message = ""
                movement_cost = current_mob.get_movement_cost(x_change, y_change)
                local_infrastructure = current_mob.images[0].current_cell.get_intact_building('infrastructure')
                adjacent_cell = current_mob.images[0].current_cell.adjacent_cells[non_cardinal_direction]
                if not adjacent_cell == 'none':
                    if current_mob.can_walk:
                        tooltip_text.append("Costs 1 movement point, or 0.5 movement points if moving between two tiles with roads or railroads")
                        if current_mob.can_explore:
                            tooltip_text.append("Costs 0.5 movements points if moving to a water tile")
                        adjacent_infrastructure = adjacent_cell.get_intact_building('infrastructure')
                        message = "Moving " + direction + " costs " + str(movement_cost) + " movement points because "
                        if current_mob.can_explore and adjacent_cell.terrain == 'water':
                            message += "the tile moved to is a water tile"
                        elif (not local_infrastructure == 'none') and (not adjacent_infrastructure == 'none'): #if both have infrastructure
                            message += "this tile has a " + local_infrastructure.infrastructure_type + " and the tile moved to has a " + adjacent_infrastructure.infrastructure_type
                        elif local_infrastructure == 'none' and not adjacent_infrastructure == 'none': #if local has no infrastructure but adjacent does
                            message += "this tile has no road or railroad to connect to the " + adjacent_infrastructure.infrastructure_type + " of the tile moved to"
                        elif not local_infrastructure == 'none': #if local has infrastructure but not adjacent
                            message += "the tile moved to has no road or railroad to connect to this tile's " + local_infrastructure.infrastructure_type
                        else: #
                            message += "there are no roads or railroads between this tile and the tile moved to"
                    else:
                        tooltip_text.append("Costs 1 movement point")
                else:
                    message = "Moving in this direction would move off of the map"
                if not message == "":
                    tooltip_text.append(message)
                if current_mob.can_walk:
                    tooltip_text.append("Can move on land")
                else:
                    tooltip_text.append("Can not move on land")
                if current_mob.can_swim:
                    if current_mob.can_explore:
                        tooltip_text.append("Can move twice as quickly in water")
                    else:
                        tooltip_text.append("Can move in water")
                else:
                    tooltip_text.append("Can not move in water, but can embark on a ship in the water by moving to it")
                if current_mob.can_explore:
                    tooltip_text.append("Can attempt to explore unexplored areas by moving into them")
                else:
                    tooltip_text.append("Can not move into unexplored areas")
            self.set_tooltip(tooltip_text)
        elif self.button_type == 'toggle grid lines':
            self.set_tooltip(['Press to show or hide grid lines'])
        elif self.button_type == 'toggle text box':
            self.set_tooltip(['Press to show or hide text box'])
        elif self.button_type == 'expand text box':
            self.set_tooltip(['Press to change the size of the text box'])
        elif self.button_type == 'instructions':
            self.set_tooltip(["Shows the game's instructions.", "Press this when instructions are not opened to open them.", "Press this when instructions are opened to close them."])
        elif self.button_type == 'merge':
            if (not self.attached_label.actor == 'none') and self.attached_label.actor.is_officer and self.attached_label.actor.officer_type == 'evangelist':
                self.set_tooltip(["Merges this evangelist with church volunteers in the same tile to form a group of missionaries.", "Requires that an evangelist is selected in the same tile as church volunteers."])
            else:
                self.set_tooltip(["Merges this officer with a worker in the same tile to form a group with a type based on that of the officer.", "Requires that an officer is selected in the same tile as a worker."])
        elif self.button_type == 'split':
            self.set_tooltip(["Splits a group into its worker and officer."])
        elif self.button_type == 'crew': #clicked on vehicle side
            self.set_tooltip(["Merges this " + self.vehicle_type + " with a worker in the same tile to form a crewed " + self.vehicle_type + ".",
                "Requires that an uncrewed " + self.vehicle_type + " is selected in the same tile as a worker."])
        elif self.button_type == 'worker to crew': #clicked on worker side
            self.set_tooltip(["Merges this worker with a " + self.vehicle_type + " in the same tile to form a crewed " + self.vehicle_type + ".",
                "Requires that a worker is selected in the same tile as an uncrewed " + self.vehicle_type + "."])
        elif self.button_type == 'uncrew':
            self.set_tooltip(["Orders this " + self.vehicle_type + "'s crew to abandon the " + self.vehicle_type + "."])
        elif self.button_type == 'embark':
            self.set_tooltip(["Orders this unit to embark a " + self.vehicle_type + " in the same tile.", "Requires that a unit is selected in the same tile as a crewed " + self.vehicle_type + "."])
        elif self.button_type == 'disembark':
            self.set_tooltip(["Orders this unit to disembark the " + self.vehicle_type + "."])
        elif self.button_type == 'pick up all passengers':
            self.set_tooltip(["Orders this " + self.vehicle_type + " take all non-vehicle units in this tile as passengers."])
        elif self.button_type == 'pick up commodity':
            if not self.attached_label.actor == 'none':
                self.set_tooltip(["Transfers 1 unit of " + self.attached_label.actor.get_held_commodities()[self.attached_label.commodity_index] + " to the currently displayed unit in this tile"])
            else:
                self.set_tooltip(['none'])
        elif self.button_type == 'pick up all commodity':
            if not self.attached_label.actor == 'none':
                self.set_tooltip(["Transfers all units of " + self.attached_label.actor.get_held_commodities()[self.attached_label.commodity_index] + " to the currently displayed unit in this tile"])
            else:
                self.set_tooltip(['none'])
        elif self.button_type == 'drop commodity':
            if not self.attached_label.actor == 'none':
                self.set_tooltip(["Transfers 1 unit of " + self.attached_label.actor.get_held_commodities()[self.attached_label.commodity_index] + " into this unit's tile"])
            else:
                self.set_tooltip(['none'])
        elif self.button_type == 'drop all commodity':
            if not self.attached_label.actor == 'none':
                self.set_tooltip(["Transfers all units of " + self.attached_label.actor.get_held_commodities()[self.attached_label.commodity_index] + " into this unit's tile"])
            else:
                self.set_tooltip(['none'])
        elif self.button_type == 'remove worker':
            if not self.attached_label.attached_building == 'none':
                self.set_tooltip(["Detaches this work crew from the " + self.attached_label.attached_building.name])
            else:
                self.set_tooltip(['none'])
        elif self.button_type == 'start end turn': #different from end turn from choice buttons - start end turn brings up a choice notification
            self.set_tooltip(['Ends the current turn'])
        elif self.button_type == 'sell commodity' or self.button_type == 'sell all commodity':
            if not self.attached_label.actor == 'none':
                commodity_list = self.attached_label.actor.get_held_commodities()
                commodity = commodity_list[self.attached_label.commodity_index]
                sell_price = self.global_manager.get('commodity_prices')[commodity]
                if self.button_type == 'sell commodity':
                    self.set_tooltip(["Sells 1 unit of " + commodity + " for " + str(sell_price) + " money", "Each unit of " + commodity + " sold has a chance of reducing the price"])
                else:
                    num_present = self.attached_label.actor.get_inventory(commodity)
                    self.set_tooltip(["Sells your entire stockpile of " + commodity + " for " + str(sell_price) + " money each, totaling to " + str(sell_price * num_present) + " money",
                        "Each unit of " + commodity + " sold has a chance of reducing the price"])
            else:
                self.set_tooltip(['none'])
        elif self.button_type == 'switch theatre':
           self.set_tooltip(["Moves this ship between Africa and Europe", " Requires that this ship has all of its movement points and is not inland"])
        elif self.button_type == 'cycle passengers':
            tooltip_text = ["Cycles through this " + self.vehicle_type + "'s passengers"]
            tooltip_text.append("Passengers: " )
            if self.can_show():
                for current_passenger in self.attached_label.actor.contained_mobs:
                    tooltip_text.append("    " + current_passenger.name)
            self.set_tooltip(tooltip_text)
        elif self.button_type == 'cycle work crews':
            tooltip_text = ["Cycles through this  building's work crews"]
            tooltip_text.append("Work crews: " )
            if self.can_show():
                for current_work_crew in self.attached_label.actor.cell.get_building('resource').contained_work_crews:
                    tooltip_text.append("    " + current_work_crew.name)
            self.set_tooltip(tooltip_text)
        elif self.button_type == 'cycle tile mobs':
            tooltip_text = ["Cycles through this tile's units"]
            tooltip_text.append("Units: " )
            if self.can_show():
                for current_mob in self.global_manager.get('displayed_tile').cell.contained_mobs:
                    tooltip_text.append("    " + current_mob.name)
            self.set_tooltip(tooltip_text)
        elif self.button_type == 'build train':
            self.set_tooltip(["Builds a train in this unit's tile", "Can only be built on a train station", "Costs 1 movement point"])
        elif self.button_type == 'cycle units':
            self.set_tooltip(["Selects the next unit that has movement remaining"])
        elif self.button_type == 'trade':
            self.set_tooltip(["Attempts to trade with natives, paying consumer goods for random commodities", "Can only be done in a village", "The number of possible trades per turn depends on the village's population and aggressiveness",
                "Each trade spends a unit of consumer goods for a chance of a random commodity", "Regardless of a trade's success, the lure of consumer goods has a chance of convincing natives to become available workers",
                "Has higher success chance and lower risk when a trading post is present", "Costs an entire turn of movement points"])
        elif self.button_type == 'religious campaign':
            self.set_tooltip(["Starts a religious campaign in an effort to find religious volunteers.", "Can only be done in Europe",
                "If successful, recruits a free unit of church volunteers that can join with an evangelist to form a group of missionaries that can convert native villages", "Costs an entire turn of movement points."])
        elif self.button_type == 'advertising campaign':
            self.set_tooltip(["Starts an advertising campaign to increase a certain commodity's price.", "Can only be done in Europe",
                "If successful, increases the price of a selected commodity while randomly decreasing the price of another", "Costs an entire turn of movement points."])
        elif self.button_type == 'take loan':
            self.set_tooltip(["Finds a loan offer for 100 money and an interest rate based on the merchant's experience and the minister's skill and corruption.", "Can only be done in Europe",
                "Costs an entire turn of movement points."])
        elif self.button_type == 'convert':
            self.set_tooltip(["Attempts to make progress in converting natives", "Can only be done in a village", "If successful, reduces the aggressiveness of the village, improving all company interactions with the village.",
                "Has higher success chance and lower risk when a mission is present", "Costs an entire turn of movement points."])
        elif self.button_type == 'new game':
            self.set_tooltip(["Starts a new game"])
        elif self.button_type == 'save game':
            self.set_tooltip(["Saves this game"])
        elif self.button_type == 'load game':
            self.set_tooltip(["Loads a saved game"])
        elif self.button_type == 'cycle available ministers':
            self.set_tooltip(["Cycles through the ministers available to be appointed"])
        elif self.button_type == 'appoint minister':
            self.set_tooltip(["Appoints this minister as " + self.appoint_type])
        elif self.button_type == 'remove minister':
            self.set_tooltip(["Removes this minister from their current office"])
        elif self.button_type == 'fire':
            self.set_tooltip(["Removes this unit, any units attached to it, and their associated upkeep"])
        elif self.button_type == 'hire village worker':
            self.set_tooltip(["Hires villagers as workers, reducing the village's population", "African workers cost nothing to recruit but have an upkeep each turn of " +
                                str(self.global_manager.get('african_worker_upkeep')) + " money. If fired, the workers will eventually move into slums"])
        elif self.button_type == 'hire slums worker':
            self.set_tooltip(["Hires unemployed workers, reducing the slum's population", "African workers cost nothing to recruit but have an upkeep each turn of " +
                                str(self.global_manager.get('african_worker_upkeep')) + " money. If fired, the workers will eventually move into slums"])
        elif self.button_type == 'buy slaves':
            self.set_tooltip(["Buys slave workers from Arab slave traders", "Slaves currently cost " + str(self.global_manager.get('recruitment_costs')['slave workers']) + " money to purchase and have an upkeep each turn of " +
                                str(self.global_manager.get('slave_worker_upkeep')) + " money", "This is a morally reprehensible action and will be faced with a public opinion penalty"])
        elif self.button_type == 'show previous financial report':
            self.set_tooltip(["Displays the previous turn's financial report"])
        else:
            self.set_tooltip(['placeholder'])
            
    def set_keybind(self, new_keybind):
        '''
        Description:
            Records a string version of the inputted pygame key object, allowing in-game descriptions of keybind to be shown
        Input:
            pygame key object new_keybind: The keybind id that activates this button, like pygame.K_n
        Output:
            None
        '''
        if new_keybind == pygame.K_a:
            self.keybind_name = 'a'
        if new_keybind == pygame.K_b:
            self.keybind_name = 'b'
        if new_keybind == pygame.K_c:
            self.keybind_name = 'c'
        if new_keybind == pygame.K_d:
            self.keybind_name = 'd'
        if new_keybind == pygame.K_e:
            self.keybind_name = 'e'
        if new_keybind == pygame.K_f:
            self.keybind_name = 'f'
        if new_keybind == pygame.K_g:
            self.keybind_name = 'g'
        if new_keybind == pygame.K_h:
            self.keybind_name = 'h'
        if new_keybind == pygame.K_i:
            self.keybind_name = 'i'
        if new_keybind == pygame.K_j:
            self.keybind_name = 'j'
        if new_keybind == pygame.K_k:
            self.keybind_name = 'k'
        if new_keybind == pygame.K_l:
            self.keybind_name = 'l'
        if new_keybind == pygame.K_m:
            self.keybind_name = 'm'
        if new_keybind == pygame.K_n:
            self.keybind_name = 'n'
        if new_keybind == pygame.K_o:
            self.keybind_name = 'o'
        if new_keybind == pygame.K_p:
            self.keybind_name = 'p'
        if new_keybind == pygame.K_q:
            self.keybind_name = 'q'
        if new_keybind == pygame.K_r:
            self.keybind_name = 'r'
        if new_keybind == pygame.K_s:
            self.keybind_name = 's'
        if new_keybind == pygame.K_t:
            self.keybind_name = 't'
        if new_keybind == pygame.K_u:
            self.keybind_name = 'u'
        if new_keybind == pygame.K_v:
            self.keybind_name = 'v'
        if new_keybind == pygame.K_w:
            self.keybind_name = 'w'
        if new_keybind == pygame.K_x:
            self.keybind_name = 'x'
        if new_keybind == pygame.K_y:
            self.keybind_name = 'y'
        if new_keybind == pygame.K_z:
            self.keybind_name = 'z'
        if new_keybind == pygame.K_DOWN:
            self.keybind_name = 'down arrow'
        if new_keybind == pygame.K_UP:
            self.keybind_name = 'up arrow'
        if new_keybind == pygame.K_LEFT:
            self.keybind_name = 'left arrow'
        if new_keybind == pygame.K_RIGHT:
            self.keybind_name = 'right arrow'
        if new_keybind == pygame.K_1:
            self.keybind_name = '1'
        if new_keybind == pygame.K_2:
            self.keybind_name = '2'
        if new_keybind == pygame.K_3:
            self.keybind_name = '3'
        if new_keybind == pygame.K_4:
            self.keybind_name = '4'
        if new_keybind == pygame.K_5:
            self.keybind_name = '5'
        if new_keybind == pygame.K_6:
            self.keybind_name = '6'
        if new_keybind == pygame.K_7:
            self.keybind_name = '7'
        if new_keybind == pygame.K_8:
            self.keybind_name = '8'
        if new_keybind == pygame.K_9:
            self.keybind_name = '9'
        if new_keybind == pygame.K_0:
            self.keybind_name = '0'
        if new_keybind == pygame.K_SPACE:
            self.keybind_name = 'space'
        if new_keybind == pygame.K_RETURN:
            self.keybind_name = 'enter'
        if new_keybind == pygame.K_TAB:
            self.keybind_name = 'tab'
        if new_keybind == pygame.K_ESCAPE:
            self.keybind_name = 'escape'

    def set_tooltip(self, tooltip_text):
        '''
        Description:
            Sets this actor's tooltip to the inputted list, with each inputted list representing a line of the tooltip
        Input:
            string list new_tooltip: Lines for this actor's tooltip
        Output:
            None
        '''
        self.tooltip_text = tooltip_text
        if self.has_keybind:
            self.tooltip_text.append("Press " + self.keybind_name + " to use.")
        tooltip_width = 0#50
        font_name = self.global_manager.get('font_name')
        font_size = self.global_manager.get('font_size')
        for text_line in tooltip_text:
            if text_tools.message_width(text_line, font_size, font_name) + scaling.scale_width(10, self.global_manager) > tooltip_width:
                tooltip_width = text_tools.message_width(text_line, font_size, font_name) + scaling.scale_width(10, self.global_manager)
        tooltip_height = (len(self.tooltip_text) * font_size) + scaling.scale_height(5, self.global_manager)
        self.tooltip_box = pygame.Rect(self.x, self.y, tooltip_width, tooltip_height)   
        self.tooltip_outline_width = 1
        self.tooltip_outline = pygame.Rect(self.x - self.tooltip_outline_width, self.y + self.tooltip_outline_width, tooltip_width + (2 * self.tooltip_outline_width), tooltip_height + (self.tooltip_outline_width * 2))

    def touching_mouse(self):
        '''
        Description:
            Returns whether this button is colliding with the mouse
        Input:
            None
        Output:
            boolean: Returns True if this button is colliding with the mouse, otherwise returns False
        '''
        if self.Rect.collidepoint(pygame.mouse.get_pos()): #if mouse is in button
            return(True)
        else:
            return(False)

    def can_show_tooltip(self):
        '''
        Description:
            Returns whether this button's tooltip can be shown. By default, its tooltip can be shown when it is visible and colliding with the mouse
        Input:
            None
        Output:
            None
        '''
        if self.touching_mouse() and self.can_show():
            return(True)
        else:
            return(False)
        
    def draw(self):
        '''
        Description:
            Draws this button with a description of its keybind if it has one, along with an outline if its keybind is being pressed
        Input:
            None
        Output:
            None
        '''
        if self.can_show(): #self.global_manager.get('current_game_mode') in self.modes:
            if self.showing_outline: 
                pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')['white'], self.outline)
            if self.showing_background:
                pygame.draw.rect(self.global_manager.get('game_display'), self.color, self.Rect)
            self.image.draw()
            if self.has_keybind: #The key to which a button is bound will appear on the button's image
                message = self.keybind_name
                color = 'white'
                textsurface = self.global_manager.get('myfont').render(message, False, self.global_manager.get('color_dict')[color])
                self.global_manager.get('game_display').blit(textsurface, (self.x + scaling.scale_width(10, self.global_manager), (self.global_manager.get('display_height') -
                    (self.y + self.height - scaling.scale_height(5, self.global_manager)))))

    def draw_tooltip(self, below_screen, beyond_screen, height, width, y_displacement):
        '''
        Description:
            Draws this button's tooltip when moused over. The tooltip's location may vary when the tooltip is near the edge of the screen or if multiple tooltips are being shown
        Input:
            boolean below_screen: Whether any of the currently showing tooltips would be below the bottom edge of the screen. If True, moves all tooltips up to prevent any from being below the screen
            boolean beyond_screen: Whether any of the currently showing tooltips would be beyond the right edge of the screen. If True, moves all tooltips to the left to prevent any from being beyond the screen
            int height: Combined pixel height of all tooltips
            int width: Pixel width of the widest tooltip
            int y_displacement: How many pixels below the mouse this tooltip should be, depending on the order of the tooltips
        Output:
            None
        '''
        if self.can_show():
            self.update_tooltip()
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if below_screen:
                mouse_y = self.global_manager.get('display_height') + 10 - height
            if beyond_screen:
                mouse_x = self.global_manager.get('display_width') - width
            mouse_y += y_displacement
            self.tooltip_box.x = mouse_x
            self.tooltip_box.y = mouse_y
            self.tooltip_outline.x = self.tooltip_box.x - self.tooltip_outline_width
            self.tooltip_outline.y = self.tooltip_box.y - self.tooltip_outline_width
            pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')['black'], self.tooltip_outline)
            pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')['white'], self.tooltip_box)
            for text_line_index in range(len(self.tooltip_text)):
                text_line = self.tooltip_text[text_line_index]
                self.global_manager.get('game_display').blit(text_tools.text(text_line, self.global_manager.get('myfont'), self.global_manager), (self.tooltip_box.x + scaling.scale_width(10, self.global_manager), self.tooltip_box.y +
                    (text_line_index * self.global_manager.get('font_size'))))

    def on_rmb_click(self):
        '''
        Description:
            Controls this button's behavior when right clicked. By default, the button's right click behavior is the same as its left click behavior.
        Input:
            None
        Output:
            None
        '''
        self.on_click()

    def on_click(self): #sell commodity, sell all commodity
        '''
        Description:
            Controls this button's behavior when left clicked. This behavior depends on the button's button_type
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.showing_outline = True
            if self.button_type in ['move left', 'move right', 'move up', 'move down']:
                x_change = 0
                y_change = 0
                if self.button_type == 'move left':
                    x_change = -1
                elif self.button_type == 'move right':
                    x_change = 1
                elif self.button_type == 'move up':
                    y_change = 1
                elif self.button_type == 'move down':
                    y_change = -1
                selected_list = actor_utility.get_selected_list(self.global_manager)
                if main_loop_tools.action_possible(self.global_manager):
                    if len(selected_list) == 1:
                        if self.global_manager.get('current_game_mode') == 'strategic':
                            mob = selected_list[0]
                            if mob.can_move(x_change, y_change):
                                mob.move(x_change, y_change)
                                self.global_manager.set('show_selection_outlines', True)
                                self.global_manager.set('last_selection_outline_switch', time.time())
                        else:
                            text_tools.print_to_screen("You can not move while in the European HQ screen.", self.global_manager)
                    elif len(selected_list) < 1:
                        text_tools.print_to_screen("There are no selected units to move.", self.global_manager)
                    else:
                        text_tools.print_to_screen("You can only move one unit at a time.", self.global_manager)
                else:
                    text_tools.print_to_screen("You are busy and can not move.", self.global_manager)
            elif self.button_type == 'toggle grid lines':
                if self.global_manager.get('show_grid_lines'):
                    self.global_manager.set('show_grid_lines', False)
                else:
                    self.global_manager.set('show_grid_lines', True)

            elif self.button_type == 'toggle text box':
                if self.global_manager.get('show_text_box'):
                    self.global_manager.set('show_text_box', False)
                else:
                    self.global_manager.set('show_text_box', True)

            elif self.button_type == 'expand text box':
                if self.global_manager.get('text_box_height') == self.global_manager.get('default_text_box_height'):
                    self.global_manager.set('text_box_height', self.global_manager.get('default_display_height') - 50) #self.height
                else:
                    self.global_manager.set('text_box_height', self.global_manager.get('default_text_box_height'))

            elif self.button_type == 'do something':
                text_tools.get_input('do something', 'Placeholder do something message', self.global_manager)
                
            elif self.button_type == 'exploration':
                self.expedition.start_exploration(self.x_change, self.y_change)

            elif self.button_type == 'attack':
                self.battalion.remove_attack_marks()
                self.battalion.move(self.x_change, self.y_change, True)

            elif self.button_type == 'drop commodity' or self.button_type == 'drop all commodity':
                if main_loop_tools.action_possible(self.global_manager):
                    if main_loop_tools.check_if_minister_appointed(self.global_manager.get('type_minister_dict')['transportation'], self.global_manager):
                        displayed_mob = self.global_manager.get('displayed_mob')
                        displayed_tile = self.global_manager.get('displayed_tile')
                        commodity = displayed_mob.get_held_commodities()[self.attached_label.commodity_index]
                        num_commodity = 1
                        if self.button_type == 'drop all commodity':
                            num_commodity = displayed_mob.get_inventory(commodity)
                        if (not displayed_mob == 'none') and (not displayed_tile == 'none'):
                            if displayed_mob in displayed_tile.cell.contained_mobs:
                                can_drop_off = True
                                if displayed_mob.is_vehicle and displayed_mob.vehicle_type == 'train' and not displayed_mob.images[0].current_cell.has_intact_building('train_station'):
                                    can_drop_off = False
                                    text_tools.print_to_screen("A train can only drop off cargo at a train station.", self.global_manager)
                                if can_drop_off:
                                    displayed_mob.change_inventory(commodity, -1 * num_commodity)
                                    displayed_tile.change_inventory(commodity, num_commodity)
                                    if displayed_mob.is_vehicle and displayed_mob.vehicle_type == 'train': #trains can not move after dropping cargo or passenger
                                        displayed_mob.set_movement_points(0)
                                    if displayed_tile.get_inventory_remaining() < 0 and not displayed_tile.can_hold_infinite_commodities:
                                        text_tools.print_to_screen('This tile can not hold this many commodities.', self.global_manager)
                                        text_tools.print_to_screen("Any commodities exceeding this tile's inventory capacity of " + str(displayed_tile.inventory_capacity) + " will disappear at the end of the turn.", self.global_manager)
                            else:
                                text_tools.print_to_screen('This unit is not in this tile.', self.global_manager)
                        else:
                            text_tools.print_to_screen('There is no tile to transfer this commodity to.', self.global_manager)
                else:
                     text_tools.print_to_screen("You are busy and can not transfer commodities.", self.global_manager)
                
            elif self.button_type == 'pick up commodity' or self.button_type == 'pick up all commodity':
                if main_loop_tools.action_possible(self.global_manager):
                    if main_loop_tools.check_if_minister_appointed(self.global_manager.get('type_minister_dict')['transportation'], self.global_manager):
                        displayed_mob = self.global_manager.get('displayed_mob')
                        displayed_tile = self.global_manager.get('displayed_tile')
                        commodity = displayed_tile.get_held_commodities()[self.attached_label.commodity_index]
                        num_commodity = 1
                        if self.button_type == 'pick up all commodity':
                            num_commodity = displayed_tile.get_inventory(commodity)
                        if (not displayed_mob == 'none') and (not displayed_tile == 'none'):
                            if displayed_mob in displayed_tile.cell.contained_mobs:
                                if displayed_mob.can_hold_commodities:
                                    can_pick_up = True
                                    if displayed_mob.is_vehicle and displayed_mob.vehicle_type == 'train' and not displayed_mob.images[0].current_cell.has_intact_building('train_station'):
                                        can_pick_up = False
                                        text_tools.print_to_screen("A train can only pick up cargo at a train station.", self.global_manager)
                                    if can_pick_up:
                                        if displayed_mob.get_inventory_remaining(num_commodity) >= 0: #see if adding commodities would exceed inventory capacity
                                            amount_transferred = num_commodity
                                        else:
                                            amount_transferred = displayed_mob.get_inventory_remaining()
                                            text_tools.print_to_screen("This unit can currently only pick up " + str(amount_transferred) + " units of " + commodity + ".", self.global_manager)
                                        displayed_mob.change_inventory(commodity, amount_transferred)
                                        displayed_tile.change_inventory(commodity, -1 * amount_transferred)
                                else:
                                    text_tools.print_to_screen('This unit can not hold commodities.', self.global_manager)
                            else:
                                text_tools.print_to_screen('This unit is not in this tile.', self.global_manager)
                        else:
                            text_tools.print_to_screen('There is no unit to transfer this commodity to.', self.global_manager)
                else:
                     text_tools.print_to_screen("You are busy and can not transfer commodities.", self.global_manager)

            elif self.button_type == 'remove worker':
                if not self.attached_label.attached_building == 'none':
                    if not len(self.attached_label.attached_building.contained_workers) == 0:
                        self.attached_label.attached_building.contained_workers[0].leave_building(self.attached_label.attached_building)
                    else:
                        text_tools.print_to_screen("There are no workers to remove from this building.", self.global_manager)

            elif self.button_type == 'start end turn':
                if main_loop_tools.action_possible(self.global_manager):
                    stopping = False
                    for current_position in self.global_manager.get('minister_types'):
                        if self.global_manager.get("current_ministers")[current_position] == 'none':
                            stopping = True
                    if stopping:
                        text_tools.print_to_screen("You can not end turn until a minister is appointed in each office.", self.global_manager)
                        text_tools.print_to_screen("Press Q to see the minister interface.", self.global_manager)
                    else:
                        if not self.global_manager.get('current_game_mode') == 'strategic':
                            game_transitions.set_game_mode('strategic', self.global_manager)
                        choice_info_dict = {'type': 'end turn'}
                        notification_tools.display_choice_notification('Are you sure you want to end your turn? ', ['end turn', 'none'], choice_info_dict, self.global_manager) #message, choices, choice_info_dict, global_manager
                else:
                    text_tools.print_to_screen("You are busy and can not end your turn.", self.global_manager)
    
            elif self.button_type == 'end turn':
                turn_management_tools.end_turn(self.global_manager)

            elif self.button_type == 'sell commodity' or self.button_type == 'sell all commodity':
                if main_loop_tools.check_if_minister_appointed(self.global_manager.get('type_minister_dict')['trade'], self.global_manager):
                    commodity_list = self.attached_label.actor.get_held_commodities()
                    commodity = commodity_list[self.attached_label.commodity_index]
                    num_present = self.attached_label.actor.get_inventory(commodity)
                    num_sold = 0
                    if self.button_type == 'sell commodity':
                        num_sold = 1
                    else:
                        num_sold = num_present
                    market_tools.sell(self.attached_label.actor, commodity, num_sold, self.global_manager)

            elif self.button_type == 'cycle units':
                if main_loop_tools.action_possible(self.global_manager):
                    mob_list = self.global_manager.get('pmob_list')
                    cycled_mob = 'none'
                    cycled_index = 0
                    for current_mob_index in range(len(mob_list)):
                        current_mob = mob_list[current_mob_index]
                        if current_mob.movement_points > 0 and not (current_mob.in_vehicle or current_mob.in_group or current_mob.in_building): #find mob that is independent and can move
                            if not (current_mob.is_vehicle and not current_mob.has_crew): #skip uncrewed vehicles
                                if not current_mob == self.global_manager.get('displayed_mob'): #skip the currently selected mob
                                    if self.global_manager.get('current_game_mode') in current_mob.modes: #skip units that are not on the current game mode, like ones in Africa when looking at Europe
                                        cycled_mob = current_mob
                                        cycled_index = current_mob_index
                                        break
                    if cycled_mob == 'none':
                        text_tools.print_to_screen("There are no units that have movement points remaining.", self.global_manager)
                    else:
                        mob_list.append(mob_list.pop(cycled_index)) #moves unit to end of mob list, allowing other unit to be selected next time
                        cycled_mob.select()
                        cycled_mob.move_to_front()
                        #for current_image in cycled_mob.images:
                        #    current_cell = cycled_mob.images[0].current_cell
                        #    while not current_cell.contained_mobs[0] == cycled_mob: #move to front of tile
                        #        current_cell.contained_mobs.append(current_cell.contained_mobs.pop(0))
                        if not cycled_mob.grids[0].mini_grid == 'none': #if cycled unit is on the strategic map, calibrate minimap to it
                            cycled_mob.grids[0].mini_grid.calibrate(cycled_mob.x, cycled_mob.y)
                        else: #if on Europe or other abstract grid, calibrate tile info display but not minimap to it
                            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), cycled_mob.images[0].current_cell.tile)
                else:
                    text_tools.print_to_screen("You are busy and can not cycle through units.", self.global_manager)

            elif self.button_type == 'new game':
                self.global_manager.get('save_load_manager').new_game()

            elif self.button_type == 'save game':
                if main_loop_tools.action_possible(self.global_manager):
                    self.global_manager.get('save_load_manager').save_game('save1.pickle')
                else:
                    text_tools.print_to_screen("You are busy and can not save the game", self.global_manager)

            elif self.button_type == 'load game':
                self.global_manager.get('save_load_manager').load_game('save1.pickle')

            elif self.button_type == 'fire':
                fired_unit = self.global_manager.get('displayed_mob')
                fired_unit.fire()

            elif self.button_type == 'stop exploration':
                actor_utility.stop_exploration(self.global_manager)

            elif self.button_type == 'start trading':
                caravan = self.notification.choice_info_dict['caravan']
                caravan.willing_to_trade(self.notification)

            elif self.button_type == 'start religious campaign':
                evangelist = self.notification.choice_info_dict['evangelist']
                evangelist.religious_campaign()

            elif self.button_type == 'start advertising campaign':
                merchant = self.notification.choice_info_dict['merchant']
                merchant.advertising_campaign()

            elif self.button_type == 'start loan search':
                merchant = self.notification.choice_info_dict['merchant']
                merchant.loan_search()
                for current_minister_image in self.global_manager.get('dice_roll_minister_images'):
                    current_minister_image.remove()

            elif self.button_type == 'start converting':
                evangelist = self.notification.choice_info_dict['evangelist']
                evangelist.convert()

            elif self.button_type == 'start construction':
                constructor = self.notification.choice_info_dict['constructor']
                constructor.construct()

            elif self.button_type == 'start upgrade':
                constructor = self.notification.choice_info_dict['constructor']
                constructor.upgrade()

            elif self.button_type == 'trade':
                caravan = self.notification.choice_info_dict['caravan']
                caravan.trade(self.notification)

            elif self.button_type == 'stop attack':
                self.global_manager.set('ongoing_combat', False)
                self.notification.choice_info_dict['battalion'].remove_attack_marks()

            elif self.button_type == 'stop trading':
                self.global_manager.set('ongoing_trade', False)
                
            elif self.button_type == 'stop religious campaign':
                self.global_manager.set('ongoing_religious_campaign', False)

            elif self.button_type == 'stop advertising campaign':
                self.global_manager.set('ongoing_advertising_campaign', False)

            elif self.button_type in ['stop loan search', 'decline loan offer']:
                self.global_manager.set('ongoing_loan_search', False)
                for current_minister_image in self.global_manager.get('dice_roll_minister_images'):
                    current_minister_image.remove()

            elif self.button_type == 'stop converting':
                self.global_manager.set('ongoing_conversion', False)

            elif self.button_type in ['stop construction', 'stop upgrade']:
                self.global_manager.set('ongoing_construction', False)

            elif self.button_type == 'accept loan offer':
                input_dict = {}
                input_dict['principal'] = self.notification.choice_info_dict['principal']
                input_dict['interest'] = self.notification.choice_info_dict['interest']
                input_dict['remaining_duration'] = 10
                new_loan = market_tools.loan(False, input_dict, self.global_manager)
                self.global_manager.set('ongoing_loan_search', False)
                
    def on_rmb_release(self):
        '''
        Description:
            Controls what this button does when right clicked and released. By default, buttons will stop showing their outlines when released.
        Input:
            None
        Output:
            None
        '''
        self.on_release()
                
    def on_release(self):
        '''
        Description:
            Controls what this button does when left clicked and released. By default, buttons will stop showing their outlines when released.
        Input:
            None
        Output:
            None
        '''
        self.showing_outline = False

    def remove(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program
        Input:
            None
        Output:
            None
        '''
        self.global_manager.set('button_list', utility.remove_from_list(self.global_manager.get('button_list'), self))
        self.global_manager.set('image_list', utility.remove_from_list(self.global_manager.get('image_list'), self.image))

    def can_show(self):
        '''
        Description:
            Returns whether this button can be shown. By default, it can be shown during game modes in which this button can appear
        Input:
            None
        Output:
            boolean: Returns True if this button can appear during the current game mode, otherwise returns False
        '''
        if self.global_manager.get('current_game_mode') in self.modes:
            if self.button_type in ['move left', 'move right', 'move down', 'move up']:
                if self.global_manager.get('displayed_mob') == 'none' or (not self.global_manager.get('displayed_mob').is_pmob):
                    return(False)
            return(True)
        return(False)

class cycle_same_tile_button(button):
    '''
    Button that appears near the displayed tile and cycles the order of mobs displayed in a tile
    '''
    def __init__(self, coordinates, width, height, color, modes, image_id, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string color: Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(coordinates, width, height, color, 'cycle tile mobs', 'none', modes, image_id, global_manager)

    def on_click(self):
        '''
        Description:
            Controls this button's behavior when clicked. This type of button cycles the order of mobs displayed in a tile, moving the first one shown to the bototm and moving others up
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):
                cycled_tile = self.global_manager.get('displayed_tile')
                moved_mob = cycled_tile.cell.contained_mobs.pop(0)
                cycled_tile.cell.contained_mobs.append(moved_mob)
                cycled_tile.cell.contained_mobs[0].select()
                actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), cycled_tile) #updates mob info display list to show changed passenger order
            else:
                text_tools.print_to_screen("You are busy and can not cycle units.", self.global_manager)

    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if the currently displayed tile contains 3 or less mobs. Otherwise, returns same as superclass
        '''
        result = super().can_show()
        if result:
            displayed_tile = self.global_manager.get('displayed_tile')
            if not displayed_tile == 'none':
                if len(displayed_tile.cell.contained_mobs) >= 4:
                    return(True)
        return(False)
    

class same_tile_icon(button):
    '''
    Button that appears near the displayed tile and selects mobs that are not currently at the top of the tile
    '''
    def __init__(self, coordinates, width, height, color, modes, image_id, index, is_last, global_manager):
        '''
        Description:
            Initializes this object. Depending on the actor_label_type, various buttons are created to appear next to this label
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this label
            int width: Pixel width of this label
            int height: Pixel height of this label
            string color: Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
            string list modes: Game modes during which this label can appear
            string image_id: File path to the image used by this object
            int index: Index to determine which item of the displayed tile's cell's list of contained mobs is selected by this button
            boolean is_last: Whether this is the last of the displayed tile's selection icons. If it is last, it will show all mobs are not being shown rather than being attached to a specific mob
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.attached_mob = 'none'
        super().__init__(coordinates, width, height, color, 'same tile', 'none', modes, image_id, global_manager)
        self.old_contained_mobs = []#selected_list = []
        self.default_image_id = image_id
        self.index = index
        self.is_last = is_last
        if self.is_last:
            self.name_list = []

    def on_click(self):
        '''
        Description:
            Controls this button's behavior when clicked. This type of button selects the mob that it is currently attached to when clicked
        Input:
            None
        Output:
            None
        '''
        if self.can_show() and (not self.is_last) and (not self.attached_mob == 'none'):
            if main_loop_tools.action_possible(self.global_manager): #when clicked, calibrate minimap to attached mob and move it to the front of each stack
                self.showing_outline = True
                self.attached_mob.select() 
                for current_image in self.attached_mob.images: #move mob to front of each stack it is in
                    if not current_image.current_cell == 'none':
                        while not self.attached_mob == current_image.current_cell.contained_mobs[0]:
                            current_image.current_cell.contained_mobs.append(current_image.current_cell.contained_mobs.pop(0))
            else:
                text_tools.print_to_screen("You are busy and can not select a different unit", self.global_manager)

    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if there is no tile selected, otherwise returns same as superclass
        '''
        if (not self.global_manager.get('displayed_tile') == 'none') and self.global_manager.get('displayed_tile').cell.visible:
            return(super().can_show())
        else:
            return(False)

    def can_show_tooltip(self):
        '''
        Description:
            Returns whether this button's tooltip can be shown. A same tile icon has the the normal requirements for a tooltip to be shown, along with requiring that it is attached to a unit
        Input:
            None
        Output:
            None
        '''
        if super().can_show_tooltip():
            if not self.attached_mob == 'none':
                return(True)
        return(False)
                         
    def draw(self):
        '''
        Description:
            Draws this button and draws a copy of the this button's attached mob's image on top of it
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            if not self.global_manager.get('displayed_tile') == 'none':
                new_contained_mobs = self.global_manager.get('displayed_tile').cell.contained_mobs #actor_utility.get_selected_list(self.global_manager)
                if not new_contained_mobs == self.old_contained_mobs:
                    self.old_contained_mobs = []
                    for current_item in new_contained_mobs:
                        self.old_contained_mobs.append(current_item)
                    if self.is_last and len(new_contained_mobs) > self.index:
                        self.attached_mob = 'last'
                        self.image.set_image('buttons/extra_selected_button.png')
                        name_list = []
                        for current_mob_index in range(len(self.old_contained_mobs)):
                            if current_mob_index > self.index - 1:
                                name_list.append(self.old_contained_mobs[current_mob_index].name)
                        self.name_list = name_list
                        
                    elif len(self.old_contained_mobs) > self.index:
                        self.attached_mob = self.old_contained_mobs[self.index]
                        self.image.set_image(self.attached_mob.images[0].image_id)
            else:
                self.image.set_image('misc/empty.png')
                self.attached_mob = 'none'
                
            if len(self.old_contained_mobs) > self.index:
                displayed_tile = self.global_manager.get('displayed_tile')
                if self.index == 0 and self.can_show() and not displayed_tile == 'none':
                    if displayed_tile.cell.contained_mobs[0].selected: #self.global_manager.get('displayed_tile').cell.contained_mobs[0].selected:
                        pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')['bright green'], self.outline)
                    else:
                        pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')['white'], self.outline)
                super().draw()

            else:
                self.image.set_image('misc/empty.png')
                self.attached_mob = 'none'

    def update_tooltip(self):
        '''
        Description:
            Sets this button's tooltip to what it should be, depending on its button_type. This type of button copies the tooltip of its attached mob
        Input:
            None
        Output:
            None
        '''
        if not self.can_show():
            self.set_tooltip([])
        else:
            if self.is_last:
                self.set_tooltip(["More: "] + self.name_list)
            else:
                self.attached_mob.update_tooltip()
                self.set_tooltip(self.attached_mob.tooltip_text + ["Click to select this unit"])

class fire_unit_button(button):
    '''
    Button that fires the selected unit, removing it from the game as if it died
    '''
    def __init__(self, coordinates, width, height, color, modes, image_id, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string color: Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.attached_mob = 'none'
        super().__init__(coordinates, width, height, color, 'fire unit', 'none', modes, image_id, global_manager)
        self.old_contained_mobs = []#selected_list = []

    def on_click(self):
        '''
        Description:
            Controls this button's behavior when clicked. This type of button fires the selected unit
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            if main_loop_tools.action_possible(self.global_manager): #when clicked, calibrate minimap to attached mob and move it to the front of each stack
                self.showing_outline = True
                message = "Are you sure you want to fire this unit? Firing this unit would remove it, any units attached to it, and any associated upkeep from the game. /n /n "
                if self.attached_mob.is_worker:
                    if self.attached_mob.worker_type in ['European', 'religious']:
                        message += "Unlike African workers, fired European workers will never settle in slums and are truly removed from the game."
                    elif self.attached_mob.worker_type == 'African':
                        message += "Fired workers will enter the labor pool and wander, eventually settling in slums where they may be hired again."
                    elif self.attached_mob.worker_type == 'slave':
                        message += "Firing slaves frees them, increasing public opinion and entering them into the labor pool. Freed slaves will wander and eventually settle in slums, where they may be hired as workers."
                notification_tools.display_choice_notification(message, ['fire', 'cancel'], {}, self.global_manager)
                #self.attached_mob.die()
            else:
                text_tools.print_to_screen("You are busy and can not fire a unit", self.global_manager)

    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns same as superclass if there is a selected unit, otherwise returns False
        '''
        if super().can_show():
            if not self.attached_mob == self.global_manager.get('displayed_mob'):
                self.attached_mob = self.global_manager.get('displayed_mob')
            if not self.attached_mob == 'none':
                if self.attached_mob.controllable:
                    return(True)
        return(False)

    def update_tooltip(self):
        '''
        Description:
            Sets this button's tooltip to what it should be, depending on its button_type. This type of button describes how firing units works
        Input:
            None
        Output:
            None
        '''
        if not self.can_show():
            self.set_tooltip([])
        else:
            tooltip_text = ["Click to fire this unit"]
            if self.attached_mob.is_group or self.attached_mob.is_worker:
                tooltip_text.append("Once fired, this unit will cost no longer cost upkeep")
            elif self.attached_mob.is_vehicle:
                tooltip_text.append("Firing this unit will also fire all of its passengers.")
            self.set_tooltip(tooltip_text)

class switch_game_mode_button(button):
    '''
    Button that switches between game modes, like from the strategic map to the minister conference room
    '''
    def __init__(self, coordinates, width, height, color, keybind_id, to_mode, modes, image_id, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string color: Color in the color_dict dictionary for this button when it has no image, like 'bright blue'
            pygame key object keybind_id: Determines the keybind id that activates this button, like pygame.K_n
            string to_mode: game mode that this button switches to. If this equals 'previous', it switches to the previous game mode rather than a preset one
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        button_type = 'switch_game_mode'
        self.to_mode = to_mode
        self.to_mode_tooltip_dict = {}
        self.to_mode_tooltip_dict['main menu'] = ["Exits to the main menu", "Does not automatically save the game"]
        self.to_mode_tooltip_dict['strategic'] = ["Enters the strategic map screen"]
        self.to_mode_tooltip_dict['europe'] = ["Enters the European headquarters screen"]
        self.to_mode_tooltip_dict['ministers'] = ["Enters the minister conference room screen"]
        super().__init__(coordinates, width, height, color, button_type, keybind_id, modes, image_id, global_manager)

    def on_click(self):
        '''
        Description:
            Controls this button's behavior when clicked. This type of button transtions from the current game mode to either the previous game mode or one specified on button initialization
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.showing_outline = True
            if main_loop_tools.action_possible(self.global_manager):
                if self.global_manager.get("minister_appointment_tutorial_completed"):
                    if self.to_mode == 'main menu':
                        game_transitions.to_main_menu(self.global_manager)
                    if not self.to_mode == 'previous':
                        game_transitions.set_game_mode(self.to_mode, self.global_manager)
                    else:
                        self.global_manager.set('exit_minister_screen_tutorial_completed', True)
                        game_transitions.set_game_mode(self.global_manager.get('previous_game_mode'), self.global_manager)
                else:
                    text_tools.print_to_screen("You have not yet appointed a minister in each office.", self.global_manager)
            else:
                text_tools.print_to_screen('You are busy and can not switch screens.', self.global_manager)

    def update_tooltip(self):
        '''
        Description:
            Sets this button's tooltip to what it should be, depending on its button_type. This type of button describes which game mode it switches to
        Input:
            None
        Output:
            None
        '''
        if self.to_mode == 'previous':
            self.set_tooltip(utility.copy_list(self.to_mode_tooltip_dict[self.global_manager.get('previous_game_mode')]))
        else:
            self.set_tooltip(utility.copy_list(self.to_mode_tooltip_dict[self.to_mode]))

class minister_portrait_image(button): #image of minister's portrait - button subclass because can be clicked to select minister
    '''
    Button that can be calibrated to a minister to show that minister's portrait and selects the minister when clicked
    '''
    def __init__(self, coordinates, width, height, modes, minister_type, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string list modes: Game modes during which this button can appear
            string minister_type: Minister office that this button is linked to, causing this button to always be connected to the minister in that office. If this equals 'none', this can be calibrated to an available minister
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.default_image_id = 'ministers/empty_portrait.png'
        super().__init__(coordinates, width, height, 'gray', 'minister portrait', 'none', modes, self.default_image_id, global_manager)
        self.minister_type = minister_type #position, like General
        if self.minister_type == 'none': #if available minister portrait
            self.global_manager.get('available_minister_portrait_list').append(self)
        else:
            self.type_keyword = self.global_manager.get('minister_type_dict')[self.minister_type]
        self.global_manager.get('minister_image_list').append(self)
        self.calibrate('none')

    def draw(self):
        '''
        Description:
            Draws this button's image along with a white background and, if currently selected, a flashing green outline
        Input:
            None
        Output:
            None
        '''
        if self.can_show(): #draw outline around portrait if minister selected
            if not self.current_minister == 'none':
                pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')['white'], self.Rect) #draw white background
                if self.global_manager.get('displayed_minister') == self.current_minister and self.global_manager.get('show_selection_outlines'): 
                    pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')['bright green'], self.outline)
        super().draw()

    def on_click(self):
        '''
        Description:
            Controls this button's behavior when clicked. This type of button selects its attached minister when clicked
        Input:
            None
        Output:
            None
        '''
        if not self.current_minister == 'none':
            minister_utility.calibrate_minister_info_display(self.global_manager, self.current_minister)

    def calibrate(self, new_minister):
        '''
        Description:
            Attaches this button to the inputted minister and updates this button's image to that of the minister
        Input:
            string/minister new_minister: The minister whose information is matched by this button. If this equals 'none', this button is detached from any ministers
        Output:
            None
        '''
        if not new_minister == 'none':
            new_minister.update_tooltip()
            self.tooltip_text = new_minister.tooltip_text #[self.minister_type + ' ' + new_minister.name]
            self.image.set_image(new_minister.image_id)
        else:
            if self.minister_type == 'none': #if available minister portrait
                self.tooltip_text = ['There is no available minister in this slot.']
            else: #if appointed minister portrait
                self.tooltip_text = ['No ' + self.minister_type + ' is currently appointed.', 'Without a ' + self.minister_type + ', ' + self.type_keyword + '-oriented actions are not possible']
            self.image.set_image(self.default_image_id)
        self.current_minister = new_minister

    def update_tooltip(self):
        '''
        Description:
            Sets this button's tooltip to what it should be, depending on its button_type. This type of button copies the tooltip text of its attached minister, or says there is no attached minister if there is none attached
        Input:
            None
        Output:
            None
        '''
        self.set_tooltip(self.tooltip_text)

class cycle_available_ministers_button(button):
    '''
    Button that cycles through the ministers available to be appointed
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, direction, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            pygame key object keybind_id: Determines the keybind id that activates this button, like pygame.K_n
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            string direction: If this equals 'right', this button cycles forward in the list of available ministers. If this equals 'left', this button cycles backwards in the list of available ministers
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.direction = direction
        super().__init__(coordinates, width, height, 'blue', 'cycle available ministers', keybind_id, modes, image_id, global_manager)

    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False if clicking this button would move more than 1 past the edge of the list of available ministers, otherwise returns same as superclass
        '''
        if self.direction == 'left':
            if self.global_manager.get('available_minister_left_index') > -1:
                return(super().can_show())
            else:
                return(False)
        elif self.direction == 'right': #left index = 0, left index + 4 = 4 which is greater than the length of a 3-minister list, so can't move right farther
            if not self.global_manager.get('available_minister_left_index') + 3 > len(self.global_manager.get('available_minister_list')):
                return(super().can_show())
            else:
                return(False)

    def on_click(self):
        '''
        Description:
            Controls this button's behavior when clicked. This type of button changes the range of available ministers that are displayed depending on its direction
        Input:
            None
        Output:
            None
        '''
        if self.direction == 'left':
            self.global_manager.set('available_minister_left_index', self.global_manager.get('available_minister_left_index') - 1)
        if self.direction == 'right':
            self.global_manager.set('available_minister_left_index', self.global_manager.get('available_minister_left_index') + 1)
        minister_utility.update_available_minister_display(self.global_manager)
        self.global_manager.get('available_minister_portrait_list')[1].on_click() #select new middle portrait

class commodity_button(button):
    '''
    Button appearing near commodity prices label that can be clicked as a target for advertising campaigns
    '''
    def __init__(self, coordinates, width, height, modes, image_id, commodity, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            string list modes: Game modes during which this button can appear
            string commodity: Commodity that this button corresponds to
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.commodity = commodity
        super().__init__(coordinates, width, height, 'blue', 'commodity selection', 'none', modes, image_id, global_manager)
        self.showing_background = False
        self.outline.width = 0
        self.outline.height = 0
        self.outline.x = 0
        self.outline.y = 0

    def on_click(self):
        '''
        Description:
            Controls this button's behavior when clicked. When the player is choosing a target for an advertising campaign, clicking on this button starts an advertising campaign for this button's commodity
        Input:
            None
        Output:
            None
        '''
        if self.global_manager.get('choosing_advertised_commodity'):
            if self.commodity == 'consumer goods':
                text_tools.print_to_screen("You can not advertise consumer goods.", self.global_manager)
            else:
                can_advertise = False
                for current_commodity in self.global_manager.get('collectable_resources'):
                    if (not current_commodity == self.commodity) and self.global_manager.get('commodity_prices')[current_commodity] > 1:
                        can_advertise = True
                        break
                if can_advertise:
                    self.global_manager.get('displayed_mob').start_advertising_campaign(self.commodity)
                    self.global_manager.set('choosing_advertised_commodity', False)
                else:
                    text_tools.print_to_screen("You can not advertise " + self.commodity + " because all other commodities are already at the minimum price.", self.global_manager)

    def can_show_tooltip(self):
        '''
        Description:
            Returns whether this button's tooltip can be shown. A commodity button never shows a tooltip
        Input:
            None
        Output:
            None
        '''
        return(False)

class show_previous_financial_report_button(button):
    '''
    Button appearing near money label that can be clicked to display the previous turn's financial report again
    '''
    def __init__(self, coordinates, width, height, keybind_id, modes, image_id, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this button
            int width: Pixel width of this button
            int height: Pixel height of this button
            pygame key object keybind_id: Determines the keybind id that activates this button, like pygame.K_n
            string list modes: Game modes during which this button can appear
            string image_id: File path to the image used by this object
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(coordinates, width, height, 'blue', 'show previous financial report', keybind_id, modes, image_id, global_manager)

    def can_show(self):
        '''
        Description:
            Returns whether this button should be drawn
        Input:
            None
        Output:
            boolean: Returns False during the first turn when there is no previous financial report to show, otherwise returns same as superclass
        '''
        if super().can_show():
            if not self.global_manager.get('previous_financial_report') == 'none':
                return(True)
        return(False)
    
    def on_click(self):
        '''
        Description:
            Controls this button's behavior when clicked. This type of button displays the previous turn's financial report again
        Input:
            None
        Output:
            None
        '''
        self.showing_outline = True
        if main_loop_tools.action_possible(self.global_manager):
            notification_tools.display_notification(self.global_manager.get('previous_financial_report'), 'default', self.global_manager)
        else:
            text_tools.print_to_screen("You are busy and can not view the last turn's financial report", self.global_manager)
