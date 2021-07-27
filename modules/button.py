import pygame
import time
from . import images
from . import text_tools
#from . import game_transitions
from . import instructions
from . import grids
from . import scaling
from . import main_loop
from . import actor_utility
#from . import groups

class button_class():
    '''
    A button that will do something when clicked or when the corresponding key is pressed
    '''
    def __init__(self, coordinates, width, height, color, button_type, keybind_id, modes, image_id, global_manager):
        '''
        Inputs:
            coordinates: tuple of 2 integers for initial coordinate x and y values
            width: int representing the width in pixels of the button
            height: int representing the height in pixels of the button
            color: string representing a color in the color_dict dictionary
            button_type: string representing a subtype of button, such as a 'move up' button
            keybind_id: Pygame key object representing a key on the keyboard, such as pygame.K_a for a
            modes: list of strings representing the game modes in which this button is visible, such as 'strategic' for a button appearing when on the strategic map
            image_id: string representing the address of the button's image within the graphics folder such as 'misc/left_button.png' to represent SFA/graphics/misc/left_button.png
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
        self.update_tooltip()
        self.confirming = False

    def update_tooltip(self):
        '''
        Inputs:
            none
        Outputs:
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
            self.set_tooltip(["Merges a worker and an officer in the same tile to form a group with a type based on that of the officer."])
        else:
            self.set_tooltip(['placeholder'])
            
    def set_keybind(self, new_keybind):
        '''
        Inputs:
            new_keybind: Pygame key object representing a key on the keyboard, such as pygame.K_a for a
        Outputs:
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
        Inputs:
            tooltip_text: a list of strings representing the lines of the tooltip message
        Outputs:
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
        Returns whether the button is colliding with the mouse
        '''
        if self.Rect.collidepoint(pygame.mouse.get_pos()): #if mouse is in button
            return(True)
        else:
            return(False)

    def can_show_tooltip(self):
        '''
        Returns whether the button's tooltip should be shown, which is when the button is currently displayed and the mouse is colliding with it.
        '''
        if self.touching_mouse() and self.global_manager.get('current_game_mode') in self.modes:
            return(True)
        else:
            return(False)
        
    def draw(self):
        '''
        Draws the button with a description of its keybind if applicable, along with an outline if being pressed
        '''
        if self.showing_outline: 
            pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')['dark gray'], self.outline)
        pygame.draw.rect(self.global_manager.get('game_display'), self.color, self.Rect)
        self.image.draw()
        myfont = pygame.font.SysFont('Times New Roman', 15)
        if self.has_keybind: #The key to which a button is bound will appear on the button's image
            message = self.keybind_name
            color = 'white'
            textsurface = self.global_manager.get('myfont').render(message, False, self.global_manager.get('color_dict')[color])
            self.global_manager.get('game_display').blit(textsurface, (self.x + 10, (self.global_manager.get('display_height') - (self.y + self.height - 5))))

    def draw_tooltip(self, y_displacement):
        '''
        Inputs:
            y_displacement: int describing how far the tooltip should be moved along the y axis to avoid blocking other tooltips
        Outputs:
            Draws the button's tooltip when the button is visible and colliding with the mouse. If multiple tooltips are showing, tooltips beyond the first will be moved down to avoid blocking other tooltips.
        '''
        if self.can_show():
            self.update_tooltip()
            mouse_x, mouse_y = pygame.mouse.get_pos()
            mouse_y += y_displacement
            if (mouse_x + self.tooltip_box.width) > self.global_manager.get('display_width'):
                mouse_x = self.global_manager.get('display_width') - self.tooltip_box.width
            if (self.global_manager.get('display_height') - mouse_y) - (len(self.tooltip_text) * self.global_manager.get('font_size') + 5 + self.tooltip_outline_width) < 0:
                mouse_y = self.global_manager.get('display_height') - self.tooltip_box.height
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
        Controls what the button does when right clicked. All button objects need an on_rmb_click function so that button subclasses that do something different on right click work correctly.
        '''
        self.on_click()

    def on_click(self):
        '''
        Controls what the button does when left clicked. The action taken will depend on button_type's value.
        '''
        if self.can_show():
            self.showing_outline = True
            if self.button_type == 'hi printer':
                text_tools.print_to_screen('hi')

            elif self.button_type == 'move left':
                if len(actor_utility.get_selected_list(self.global_manager)) <= 1:
                    if main_loop.action_possible(self.global_manager):
                        for mob in self.global_manager.get('mob_list'):
                            if mob.selected and mob.can_move(-1, 0):
                                mob.move(-1, 0) #x_change, y_change
                    else:
                        text_tools.print_to_screen("You are busy and can not move.", self.global_manager)
                else:
                    text_tools.print_to_screen("You can only move one entity at a time.", self.global_manager)
                        
            elif self.button_type == 'move right':
                if len(actor_utility.get_selected_list(self.global_manager)) <= 1:
                    if main_loop.action_possible(self.global_manager):
                        for mob in self.global_manager.get('mob_list'):
                            if mob.selected and mob.can_move(1, 0):
                                mob.move(1, 0)
                    else:
                        text_tools.print_to_screen("You are busy and can not move.", self.global_manager)
                else:
                    text_tools.print_to_screen("You can only move one entity at a time.", self.global_manager)
                        
            elif self.button_type == 'move up':
                if len(actor_utility.get_selected_list(self.global_manager)) <= 1:
                    if main_loop.action_possible(self.global_manager):
                        for mob in self.global_manager.get('mob_list'):
                            if mob.selected and mob.can_move(0, 1):
                                mob.move(0, 1)
                    else:
                        text_tools.print_to_screen("You are busy and can not move.", self.global_manager)
                else:
                    text_tools.print_to_screen("You can only move one entity at a time.", self.global_manager)
                        
            elif self.button_type == 'move down':
                if len(actor_utility.get_selected_list(self.global_manager)) <= 1:
                    if main_loop.action_possible(self.global_manager):
                        for mob in self.global_manager.get('mob_list'):
                            if mob.selected and mob.can_move(0, -1):
                                mob.move(0, -1)
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

            elif self.button_type == 'instructions':
                if self.global_manager.get('current_instructions_page') == 'none':
                    instructions.display_instructions_page(0, self.global_manager)
                else:
                    if not self.global_manager.get('current_instructions_page') == 'none':
                        self.global_manager.get('current_instructions_page').remove()
                        self.global_manager.set('current_instructions_page', 'none')
                    self.global_manager.set('current_instructions_page_index', 0)

    def on_rmb_release(self):
        '''
        Controls what the button does when right clicked and released. All button objects need an on_rmb_release function so that button subclasses that do something different on right click work correctly.
        '''
        self.on_release() #if any rmb buttons did something different on release, change in subclass
                
    def on_release(self):
        '''
        Controls what the button does when left clicked and released. By default, buttons will stop showing their outlines when released. Currently, buttons do not correctly show outlines when clicked
        '''
        self.showing_outline = False

    def remove(self):
        '''
        Function shared by most objects that removes them from all relevant lists and references
        '''
        self.global_manager.set('button_list', utility.remove_from_list(self.global_manager.get('button_list'), self))
        self.global_manager.set('image_list', utility.remove_from_list(self.global_manager.get('image_list'), self.image))

    def can_show(self):
        return(True)

class selected_icon(button_class):
    def __init__(self, coordinates, width, height, color, modes, image_id, selection_index, global_manager):
        self.attached_mob = 'none'
        super().__init__(coordinates, width, height, color, 'selected', 'none', modes, image_id, global_manager)
        self.old_selected_list = []
        self.default_image_id = image_id
        self.selection_index = selection_index

    def on_click(self):
        if self.can_show(): #when clicked, calibrate minimap to attached mob and move it to the front of each stack
            self.global_manager.get('minimap_grid').calibrate(self.attached_mob.x, self.attached_mob.y)
            for current_image in self.attached_mob.images:
                if not current_image.current_cell == 'none':
                    while not self.attached_mob == current_image.current_cell.contained_mobs[0]:
                        current_image.current_cell.contained_mobs.append(current_image.current_cell.contained_mobs.pop(0))
            self.global_manager.set('show_selection_outlines', True)
            self.global_manager.set('last_selection_outline_switch', time.time())#outlines should be shown immediately when selected
                        
    def draw(self):
        new_selected_list = actor_utility.get_selected_list(self.global_manager)
        if not new_selected_list == self.old_selected_list:
            self.old_selected_list = new_selected_list
            if len(self.old_selected_list) > self.selection_index:
                self.attached_mob = self.old_selected_list[self.selection_index]
                self.image.set_image(self.attached_mob.images[0].image_id)
        if len(self.old_selected_list) > self.selection_index:
            #self.set_tooltip(self.attached_mob.images[0].tooltip_text)
            super().draw()
        else:
            self.image.set_image('misc/empty.png')
            self.attached_mob = 'none'
            #self.set_tooltip('')

    def can_show(self):
        if self.attached_mob == 'none':
            return(False)
        else:
            return(True)

    def update_tooltip(self):
        if self.attached_mob == 'none':
            self.set_tooltip([])
        else:
            self.set_tooltip(self.attached_mob.images[0].tooltip_text)
        
            
    
