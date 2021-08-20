import pygame
import time
from . import images
from . import text_tools
#from . import instructions
from . import main_loop_tools
from . import actor_utility
from . import utility
from . import turn_management_tools
from . import market_tools
from . import notification_tools

class button():
    '''
    A button that will do something when clicked or when the corresponding key is pressed
    '''
    def __init__(self, coordinates, width, height, color, button_type, keybind_id, modes, image_id, global_manager):
        '''
        Input:
            coordinates: tuple of 2 integers for initial coordinate x and y values
            width: int representing the width in pixels of the button
            height: int representing the height in pixels of the button
            color: string representing a color in the color_dict dictionary
            button_type: string representing a subtype of button, such as a 'move up' button, determining its tooltip and behavior
            keybind_id: Pygame key object representing a key on the keyboard, such as pygame.K_a for a
            modes: list of strings representing the game modes in which this button is visible, such as 'strategic' for a button appearing when on the strategic map
            image_id: string representing the address of the button's image within the graphics folder such as 'misc/left_button.png' to represent SFA/graphics/misc/left_button.png
            global_manager: global_manager_template object used to manage a dictionary of shared variables
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
        self.outline = pygame.Rect(self.x - self.outline_width, self.global_manager.get('display_height') - (self.y + self.height + self.outline_width), self.width + (2 * self.outline_width), self.height + (self.outline_width * 2)) #Pygame Rect object that appears around a button when pressed
        self.button_type = button_type
        self.tooltip_text = []
        self.update_tooltip()
        self.confirming = False
        self.being_pressed = False
        self.in_notification = False #used to prioritize notification buttons in drawing and tooltips

    def update_tooltip(self):
        '''
        Input:
            none
        Output:
            Calls the set_tooltip function with a list of strings that will each be a line in this button's tooltip.
        '''
        if self.button_type == 'move up':
            self.set_tooltip(['Press to move up'])
        elif self.button_type == 'move down':
            self.set_tooltip(['Press to move down'])
        elif self.button_type == 'move left':
            self.set_tooltip(['Press to move left'])
        elif self.button_type == 'move right':
            self.set_tooltip(['Press to move right'])
        elif self.button_type == 'toggle grid lines':
            self.set_tooltip(['Press to show or hide grid lines'])
        elif self.button_type == 'toggle text box':
            self.set_tooltip(['Press to show or hide text box'])
        elif self.button_type == 'expand text box':
            self.set_tooltip(['Press to change the size of the text box'])
        elif self.button_type == 'instructions':
            self.set_tooltip(["Shows the game's instructions.", "Press this when instructions are not opened to open them.", "Press this when instructions are opened to close them."])
        elif self.button_type == 'merge':
            self.set_tooltip(["Merges a worker and an officer in the same tile to form a group with a type based on that of the officer.", "Requires that only an officer is selected in the same tile as a worker."])
        elif self.button_type == 'split':
            self.set_tooltip(["Splits a group into a separate worker and officer.", "Requires that only a group is selected."])
        elif self.button_type == 'crew':
            self.set_tooltip(["Merges a vehicle and a worker in the same tile to form a crewed vehicle. Requires that only an uncrewed vehicle is selected in the same tile as a worker."])
        elif self.button_type == 'uncrew':
            self.set_tooltip(["Orders a vehicle's crew to leave the vehicle, allowing the worker to act independently. Requires that only a crewed vehicle is selected."])
        elif self.button_type == 'embark':
            self.set_tooltip(["Orders all selected units to embark a vehicle.", "Requires a vehicle and other units are selected in the same tile."])
        elif self.button_type == 'disembark':
            self.set_tooltip(["Orders all units in a vehicle to disembark.", "Requires that a vehicle containing at least 1 unit is selected."]) 
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
                self.set_tooltip(["Detaches 1 worker from this " + self.attached_label.attached_building.name])
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
        else:
            self.set_tooltip(['placeholder'])
            
    def set_keybind(self, new_keybind):
        '''
        Input:
            new_keybind: Pygame key object representing a key on the keyboard, such as pygame.K_a for a
        Output:
            Sets keybind_name to a string used in the tooltip that describes the key to which this button is bound.
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
        Input:
            tooltip_text: a list of strings representing the lines of the tooltip message
        Output:
            Creates a tooltip message and the Pygame Rect objects (background and outline) required to display it.
        '''
        self.tooltip_text = tooltip_text
        if self.has_keybind:
            self.tooltip_text.append("Press " + self.keybind_name + " to use.")
        tooltip_width = 50
        for text_line in tooltip_text:
            if text_tools.message_width(text_line, self.global_manager.get('font_size'), 'Times New Roman') + 10 > tooltip_width:
                tooltip_width = text_tools.message_width(text_line, self.global_manager.get('font_size'), 'Times New Roman') + 10
        tooltip_height = (len(self.tooltip_text) * self.global_manager.get('font_size')) + 5
        self.tooltip_box = pygame.Rect(self.x, self.y, tooltip_width, tooltip_height)   
        self.tooltip_outline_width = 1
        self.tooltip_outline = pygame.Rect(self.x - self.tooltip_outline_width, self.y + self.tooltip_outline_width, tooltip_width + (2 * self.tooltip_outline_width), tooltip_height + (self.tooltip_outline_width * 2))

    def touching_mouse(self):
        '''
        Input:
            none
        Output:
            Returns whether this button and the mouse are colliding
        '''
        if self.Rect.collidepoint(pygame.mouse.get_pos()): #if mouse is in button
            return(True)
        else:
            return(False)

    def can_show_tooltip(self):
        '''
        Input:
            none
        Output:
            Returns whether the button's tooltip should be shown; its tooltip should be shown when the button is being displayed and is colliding with the mouse
        '''
        if self.touching_mouse() and self.can_show():
            return(True)
        else:
            return(False)
        
    def draw(self):
        '''
        Input:
            none
        Output:
            Draws this button with a description of its keybind if applicable, along with an outline if it's key is being pressed
        '''
        if self.can_show(): #self.global_manager.get('current_game_mode') in self.modes:
            if self.showing_outline: 
                pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')['white'], self.outline)
            pygame.draw.rect(self.global_manager.get('game_display'), self.color, self.Rect)
            self.image.draw()
            if self.has_keybind: #The key to which a button is bound will appear on the button's image
                message = self.keybind_name
                color = 'white'
                textsurface = self.global_manager.get('myfont').render(message, False, self.global_manager.get('color_dict')[color])
                self.global_manager.get('game_display').blit(textsurface, (self.x + 10, (self.global_manager.get('display_height') - (self.y + self.height - 5))))

    def draw_tooltip(self, below_screen, height, y_displacement):
        '''
        Input:
            y_displacement: int describing how far the tooltip should be moved along the y axis to avoid blocking other tooltips
        Output:
            Draws the button's tooltip when the button is visible and colliding with the mouse. If multiple tooltips are showing, tooltips beyond the first will be moved down to avoid blocking other tooltips.
        '''
        if self.can_show():
            self.update_tooltip()
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if below_screen:
                mouse_y = self.global_manager.get('display_height') + 10 - height
            mouse_y += y_displacement
            if (mouse_x + self.tooltip_box.width) > self.global_manager.get('display_width'):
                mouse_x = self.global_manager.get('display_width') - self.tooltip_box.width
            #if (self.global_manager.get('display_height') - mouse_y) - (len(self.tooltip_text) * self.global_manager.get('font_size') + 5 + self.tooltip_outline_width) < 0:
            #    mouse_y = self.global_manager.get('display_height') - self.tooltip_box.height
            self.tooltip_box.x = mouse_x
            self.tooltip_box.y = mouse_y
            self.tooltip_outline.x = self.tooltip_box.x - self.tooltip_outline_width
            self.tooltip_outline.y = self.tooltip_box.y - self.tooltip_outline_width
            pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')['black'], self.tooltip_outline)
            pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')['white'], self.tooltip_box)
            for text_line_index in range(len(self.tooltip_text)):
                text_line = self.tooltip_text[text_line_index]
                self.global_manager.get('game_display').blit(text_tools.text(text_line, self.global_manager.get('myfont'), self.global_manager), (self.tooltip_box.x + 10, self.tooltip_box.y + (text_line_index * self.global_manager.get('font_size'))))

    def on_rmb_click(self):
        '''
        Input:
            none
        Output:
            Controls the button's behavior when right clicked. By default, the button's right click behavior is the same as its left click behavior.
        '''
        self.on_click()

    def on_click(self): #sell commodity, sell all commodity
        '''
        Input:
            none
        Output:
            Controls the button's behavior when left clicked. This behavior depends on the button's button_type value.
        '''
        if self.can_show():
            self.showing_outline = True
            if self.button_type == 'hi printer':
                text_tools.print_to_screen('hi')

            elif self.button_type == 'move left':
                if len(actor_utility.get_selected_list(self.global_manager)) <= 1:
                    if main_loop_tools.action_possible(self.global_manager):
                        for mob in self.global_manager.get('mob_list'):
                            if mob.selected and mob.can_move(-1, 0):
                                mob.move(-1, 0)
                                self.global_manager.set('show_selection_outlines', True)
                                self.global_manager.set('last_selection_outline_switch', time.time())
                    else:
                        text_tools.print_to_screen("You are busy and can not move.", self.global_manager)
                else:
                    text_tools.print_to_screen("You can only move one entity at a time.", self.global_manager)
                        
            elif self.button_type == 'move right':
                if len(actor_utility.get_selected_list(self.global_manager)) <= 1:
                    if main_loop_tools.action_possible(self.global_manager):
                        for mob in self.global_manager.get('mob_list'):
                            if mob.selected and mob.can_move(1, 0):
                                mob.move(1, 0)
                                self.global_manager.set('show_selection_outlines', True)
                                self.global_manager.set('last_selection_outline_switch', time.time())
                    else:
                        text_tools.print_to_screen("You are busy and can not move.", self.global_manager)
                else:
                    text_tools.print_to_screen("You can only move one entity at a time.", self.global_manager)
                        
            elif self.button_type == 'move up':
                if len(actor_utility.get_selected_list(self.global_manager)) <= 1:
                    if main_loop_tools.action_possible(self.global_manager):
                        for mob in self.global_manager.get('mob_list'):
                            if mob.selected and mob.can_move(0, 1):
                                mob.move(0, 1)
                                self.global_manager.set('show_selection_outlines', True)
                                self.global_manager.set('last_selection_outline_switch', time.time())
                    else:
                        text_tools.print_to_screen("You are busy and can not move.", self.global_manager)
                else:
                    text_tools.print_to_screen("You can only move one entity at a time.", self.global_manager)
                        
            elif self.button_type == 'move down':
                if len(actor_utility.get_selected_list(self.global_manager)) <= 1:
                    if main_loop_tools.action_possible(self.global_manager):
                        for mob in self.global_manager.get('mob_list'):
                            if mob.selected and mob.can_move(0, -1):
                                mob.move(0, -1)
                                self.global_manager.set('show_selection_outlines', True)
                                self.global_manager.set('last_selection_outline_switch', time.time())
                    else:
                        text_tools.print_to_screen("You are busy and can not move.", self.global_manager)
                else:
                    text_tools.print_to_screen("You can only move one entity at a time.", self.global_manager)

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

            #elif self.button_type == 'instructions':
            #    if self.global_manager.get('current_instructions_page') == 'none':
            #        instructions.display_instructions_page(0, self.global_manager)
            #    else:
            #        if not self.global_manager.get('current_instructions_page') == 'none':
            #            self.global_manager.get('current_instructions_page').remove()
            #            self.global_manager.set('current_instructions_page', 'none')
            #        self.global_manager.set('current_instructions_page_index', 0)

            elif self.button_type == 'exploration':
                self.expedition.start_exploration(self.x_change, self.y_change)
                self.global_manager.get('money_tracker').change(self.expedition.exploration_cost * -1)

            elif self.button_type == 'drop commodity' or self.button_type == 'drop all commodity':
                if main_loop_tools.action_possible(self.global_manager):
                    displayed_mob = self.global_manager.get('displayed_mob')
                    displayed_tile = self.global_manager.get('displayed_tile')
                    commodity = displayed_mob.get_held_commodities()[self.attached_label.commodity_index]
                    num_commodity = 1
                    if self.button_type == 'drop all commodity':
                        num_commodity = displayed_mob.get_inventory(commodity)
                    if (not displayed_mob == 'none') and (not displayed_tile == 'none'):
                        displayed_mob.change_inventory(commodity, -1 * num_commodity)
                        displayed_tile.change_inventory(commodity, num_commodity)
                    else:
                        text_tools.print_to_screen('There is nothing to transfer this commodity to.', self.global_manager)
                else:
                     text_tools.print_to_screen("You are busy and can not transfer commodities.", self.global_manager)
                
            elif self.button_type == 'pick up commodity' or self.button_type == 'pick up all commodity':
                if main_loop_tools.action_possible(self.global_manager):
                    displayed_mob = self.global_manager.get('displayed_mob')
                    displayed_tile = self.global_manager.get('displayed_tile')
                    commodity = displayed_tile.get_held_commodities()[self.attached_label.commodity_index]
                    num_commodity = 1
                    if self.button_type == 'pick up all commodity':
                        num_commodity = displayed_tile.get_inventory(commodity)
                    if (not displayed_mob == 'none') and (not displayed_tile == 'none'):
                        displayed_mob.change_inventory(commodity, num_commodity)
                        displayed_tile.change_inventory(commodity, -1 * num_commodity)
                    else:
                        text_tools.print_to_screen('There is nothing to transfer this commodity to.', self.global_manager)
                else:
                     text_tools.print_to_screen("You are busy and can not transfer commodities.", self.global_manager)

            elif self.button_type == 'remove worker':
                if not self.attached_label.attached_building == 'none':
                    if not len(self.attached_label.attached_building.contained_workers) == 0:
                        self.attached_label.attached_building.contained_workers[0].leave_building(self.attached_label.attached_building)
                    else:
                        text_tools.print_to_screen("There are no workers to detach from this building.", self.global_manager)

            elif self.button_type == 'start end turn':
                if main_loop_tools.action_possible(self.global_manager):
                    choice_info_dict = {}
                    notification_tools.display_choice_notification('Are you sure you want to end your turn? ', ['end turn', 'none'], choice_info_dict, self.global_manager) #message, choices, choice_info_dict, global_manager
                else:
                    text_tools.print_to_screen("You are busy and can not end your turn.", self.global_manager)
    
            elif self.button_type == 'end turn':
                turn_management_tools.end_turn(self.global_manager)

            elif self.button_type == 'sell commodity' or self.button_type == 'sell all commodity':
                commodity_list = self.attached_label.actor.get_held_commodities()
                commodity = commodity_list[self.attached_label.commodity_index]
                num_present = self.attached_label.actor.get_inventory(commodity)
                num_sold = 0
                if self.button_type == 'sell commodity':
                    num_sold = 1
                else:
                    num_sold = num_present
                market_tools.sell(self.attached_label.actor, commodity, num_sold, self.global_manager)

            elif self.button_type == 'none': #used as option in confirmation notifications, remove anything created by opening notification, like exploration mark, when pressed
                if self.global_manager.get('ongoing_exploration'):
                    for current_exploration_mark in self.global_manager.get('exploration_mark_list'): #copy_exploration_mark_list:
                        current_exploration_mark.remove()
                    self.global_manager.set('ongoing_exploration', False)
                    self.global_manager.set('exploration_mark_list', [])
                
    def on_rmb_release(self):
        '''
        Input:
            none
        Output:
            Controls what the button does when right clicked and released. By default, buttons will stop showing their outlines when released.
        '''
        self.on_release() #if any rmb buttons did something different on release, change in subclass
                
    def on_release(self):
        '''
        Input:
            none
        Output:
            Controls what the button does when left clicked and released. By default, buttons will stop showing their outlines when released.
        '''
        self.showing_outline = False

    def remove(self):
        '''
        Input:
            none
        Output:
            Removes the object from relevant lists and prevents it from further appearing in or affecting the program
        '''
        self.global_manager.set('button_list', utility.remove_from_list(self.global_manager.get('button_list'), self))
        self.global_manager.set('image_list', utility.remove_from_list(self.global_manager.get('image_list'), self.image))

    def can_show(self):
        '''
        Input:
            none
        Output:
            Returns whether the button can currently be shown
        '''
        if self.global_manager.get('current_game_mode') in self.modes:
            return(True)

class selected_icon(button):
    '''
    A button whose appearance and tooltip matches that of a selected mob and moves the minimap to that mob when clicked
    '''
    def __init__(self, coordinates, width, height, color, modes, image_id, selection_index, is_last, global_manager):
        '''
        Input:
            coordinates: tuple of 2 integers for initial coordinate x and y values
            width: int representing the width in pixels of the button
            height: int representing the height in pixels of the button
            color: string representing a color in the color_dict dictionary
            modes: list of strings representing the game modes in which this button is visible, such as 'strategic' for a button appearing when on the strategic map
            image_id: string representing the address of the button's image within the graphics folder such as 'misc/left_button.png' to represent SFA/graphics/misc/left_button.png
            selection_index: int representing the index of the selected_list to which this selected_icon can be attached
            global_manager: global_manager_template object used to manage a dictionary of shared variables
        '''
        self.attached_mob = 'none'
        super().__init__(coordinates, width, height, color, 'selected', 'none', modes, image_id, global_manager)
        self.old_selected_list = []
        self.default_image_id = image_id
        self.selection_index = selection_index
        self.is_last = is_last
        if self.is_last:
            self.name_list = []

    def on_click(self):
        '''
        Input:
            none
        Output:
            Moves minimap to attached selected mob when clicked
        '''
        if self.can_show() and not self.is_last: #when clicked, calibrate minimap to attached mob and move it to the front of each stack
            self.showing_outline = True
            actor_utility.deselect_all(self.global_manager) #deselect others, select attached
            self.attached_mob.select() 
            if self.global_manager.get('minimap_grid') in self.attached_mob.grids: #move minimap to attached mob
                self.global_manager.get('minimap_grid').calibrate(self.attached_mob.x, self.attached_mob.y)
            else: #otherwise, show info of tile that mob is on without moving minimap
                actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('tile_info_display_list'), self.attached_mob.images[0].current_cell.tile)
            actor_utility.calibrate_actor_info_display(self.global_manager, self.global_manager.get('mob_info_display_list'), self.attached_mob)
            for current_image in self.attached_mob.images: #move mob to front of each stack it is in
                if not current_image.current_cell == 'none':
                    while not self.attached_mob == current_image.current_cell.contained_mobs[0]:
                        current_image.current_cell.contained_mobs.append(current_image.current_cell.contained_mobs.pop(0))
                         
    def draw(self):
        '''
        Input:
            none
        Output:
            Draws a copy of the attached selected mob's image at this button's location with the button's shape as a background
        '''
        new_selected_list = actor_utility.get_selected_list(self.global_manager)
        if not new_selected_list == self.old_selected_list:
            self.old_selected_list = new_selected_list
            if self.is_last and len(new_selected_list) > self.selection_index:
                self.attached_mob = 'last'
                self.image.set_image('misc/extra_selected_button.png')
                name_list = []
                for current_mob_index in range(len(self.old_selected_list)):
                    if current_mob_index > self.selection_index - 1:
                        name_list.append(self.old_selected_list[current_mob_index].name)
                self.name_list = name_list
                
            elif len(self.old_selected_list) > self.selection_index:
                self.attached_mob = self.old_selected_list[self.selection_index]
                self.image.set_image(self.attached_mob.images[0].image_id)
        if len(self.old_selected_list) > self.selection_index:
            super().draw()
        else:
            self.image.set_image('misc/empty.png')
            self.attached_mob = 'none'

    def can_show(self):
        '''
        Input:
            none
        Output:
            Returns True if this button has an attached selected mob - it is not visible when there is no attached selected mob
        '''
        if self.attached_mob == 'none':
            return(False)
        else:
            return(True)

    def update_tooltip(self):
        '''
        Input:
            none
        Output:
            Sets the button's tooltip to that of its attached selected mob
        '''
        if not self.can_show():
            self.set_tooltip([])
        else:
            if self.is_last:
                self.set_tooltip(["More: "] + self.name_list)
            else:
                self.attached_mob.update_tooltip()
                self.set_tooltip(self.attached_mob.tooltip_text + ["Click to deselect other units and focus on this one"])
        
class switch_theatre_button(button):
    def __init__(self, coordinates, width, height, color, keybind_id, modes, image_id, global_manager): #destination_grids
        '''
        Input:
            same as superclass
        '''
        super().__init__(coordinates, width, height, color, 'switch_theatre', keybind_id, modes, image_id, global_manager)
        #self.destination_grids = destination_grids

    def on_click(self):      
        '''
        Input:
            none
        Output:
            Controls the button's behavior when left clicked. Grid switching buttons require one mob to be selected and outside of this button's destination grid to be used, and move the selected mob to the destination grid when used.
        '''
        if self.can_show():
            self.showing_outline = True
            if len(actor_utility.get_selected_list(self.global_manager)) == 1:
                if main_loop_tools.action_possible(self.global_manager):
                    current_mob = actor_utility.get_selected_list(self.global_manager)[0]
                    if current_mob.movement_points == current_mob.max_movement_points:
                        if not (self.global_manager.get('strategic_map_grid') in current_mob.grids and current_mob.y > 0): #or in a harbor
                            if current_mob.can_leave(): #not current_mob.grids[0] in self.destination_grids and 
                                current_mob.end_turn_destination = 'none'
                                self.global_manager.set('choosing_destination', True)
                                self.global_manager.set('choosing_destination_info_dict', {'chooser': current_mob}) #, 'destination_grids': self.destination_grids
                        else:
                            text_tools.print_to_screen("You are inland and can not cross the ocean.", self.global_manager) 
                    else:
                        text_tools.print_to_screen("Crossing the ocean requires an entire turn of movement points.", self.global_manager)
                else:
                    text_tools.print_to_screen("You are busy and can not move.", self.global_manager)
            else:
                text_tools.print_to_screen("You can only move one entity at a time.", self.global_manager)

    def update_tooltip(self):
        '''
        Input:
            none
        Output:
            Sets this button's tooltip to what it should be. A switch_grid_button's tooltip should describe the location that it sends units to
        '''
        message = "Sends the currently selected ship to a different theatre (Africa or Europe)"
        self.set_tooltip([message])

    def can_show(self):
        '''
        Input:
            none
        Output:
            Returns whether the button can currently be shown. A grid switching button is only shown when there is one mob selected and that mob is not on this button's destination grid.
        '''
        selected_list = actor_utility.get_selected_list(self.global_manager)
        if not len(selected_list) == 1: #do not show if there is not exactly one mob selected
            return(False)
        #elif selected_list[0].grids[0] in self.destination_grids: #do not show if mob is in destination grid already
        #    return(False)
        elif not selected_list[0].can_travel(): #only ships can move between grids
            return(False)
        else:
            return(super().can_show()) #if nothing preventing being shown, use conditions of superclass
