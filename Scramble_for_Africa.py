#separate files:
#main,
#classes:
#   global_manager_template
#   input_manager_template
#   button_class
#   label
#       notification
#       instructions_page
#   bar
#       actor_bar
#   grid
#   cell
#   free_image
#       loading_image_class
#   actor_image
#       button_image
#       tile_image
#   actor
#       mob
#           explorer
#       tile_class
#           overlay_tile

#functions:
#   roll
#   remove_from_list
#   get_input
#   calculate_distance
#   text
#   rect_to_surface
#   message_width
#   display_image
#   display_image_angle
#   manage_text_list
#   add_to_message
#   print_to_screen
#   print_to_previous_message
#   clear_message
#   toggle
#   find_distance #find grid coordinate distance between two objects with x and y attributes
#   find_coordinate_distance #find grid coordinate distance between two tuples of coordinates
#   set_game_mode
#   create_strategic_map
#   draw_text_box
#   update_display
#   draw_loading_screen
#   start_loading
#   manage_tooltip_drawing
#   create_image_dict
#   display_notification
#   notification_to_front
#   show_tutorial_notifications
#   manage_rmb_down
#   manage_lmb_down
#   scale_coordinates
#   scale_width
#   scale_height
#   generate_article
#   display_instructions_page

#to do:
#create relevant actors
#review rules
#trigger button outlines when clicking, currently only works when pressing
#add more docstrings and comments
#move classes and functions to different files
#add global_manager as input to certain docstrings
#
#done since 6/15
#remove varision-specific program elements
#convert old game mode to a strategic game mode, removing other game modes
#add correct terrain types with corresponding colors and/or images
#change strategic map to correct size
#added docstring descriptions of certain classes and functions
#removed obsolete showing and can_show() variables and functions, respectively
#added images for all resources
#remove all global variables
#make better images for all resources
#add mobs
#add selecting and mouse boxes
#add movement and basic movement restrictions

import pygame
import time
import random
import math
pygame.init()
clock = pygame.time.Clock()

class global_manager_template():
    '''
    An object designed to be passed between functions and objects as a simpler alternative to passing each variable or object separately
    '''
    def __init__(self):#, global_dict):
        self.global_dict = {}#global_dict #dictionary with values in the format 'variable_name': variable_value
        
    def get(self, name):
        return(self.global_dict[name]) #variables in the dictionary are accessed with global_manager.get('variable_name')
    
    def set(self, name, value): #create a new dictionary value or change an existing one with global_manager.set('variable_name', new_variable_value)
        self.global_dict[name] = value

class input_manager_template():
    def __init__(self, global_manager):
        self.global_manager = global_manager
        self.previous_input = ''
        self.taking_input = False
        self.old_taking_input = self.taking_input
        self.stored_input = ''
        self.send_input_to = ''
        
    def check_for_input(self):
        if self.old_taking_input == True and self.taking_input == False: 
            return(True)
        else:
            return(False)
        
    def start_receiving_input(self, solicitant, message):
        print_to_screen(message)
        self.send_input_to = solicitant
        self.taking_input = True
        
    def update_input(self):
        self.old_taking_input = self.taking_input
        
    def receive_input(self, received_input): #to do: add do something button for testing
        if self.send_input_to == 'do something':
            if received_input == 'done':
                self.global_manager.set('crashed', True)
            else:
                print_to_screen("I didn't understand that.")
                
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
        self.image = button_image(self, self.width, self.height, image_id, self.global_manager)
        self.color = color_dict[color]
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
            if message_width(text_line, self.global_manager.get('font_size'), 'Times New Roman') + 10 > tooltip_width:
                tooltip_width = message_width(text_line, self.global_manager.get('font_size'), 'Times New Roman') + 10
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
            pygame.draw.rect(self.global_manager.get('game_display'), color_dict['dark gray'], self.outline)
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
            self.global_manager.get('game_display').blit(text(text_line, self.global_manager.get('myfont'), self.global_manager), (self.tooltip_box.x + 10, self.tooltip_box.y + (text_line_index * self.global_manager.get('font_size'))))

    def on_rmb_click(self):
        '''
        Controls what the button does when right clicked. All button objects need an on_rmb_click function so that button subclasses that do something different on right click work correctly.
        '''
        self.on_click()

    def on_click(self):
        '''
        Controls what the button does when left clicked. The action taken will depend on button_type's value.
        '''
        self.showing_outline = True
        if self.button_type == 'hi printer':
            print_to_screen('hi')

        elif self.button_type == 'move left':
            for mob in global_manager.get('mob_list'):
                if mob.selected and mob.can_move(-1, 0):
                    mob.move(-1, 0) #x_change, y_change
                    
        elif self.button_type == 'move right':
            for mob in global_manager.get('mob_list'):
                if mob.selected and mob.can_move(1, 0):
                    mob.move(1, 0)
                    
        elif self.button_type == 'move up':
            for mob in global_manager.get('mob_list'):
                if mob.selected and mob.can_move(0, 1):
                    mob.move(0, 1)
                    
        elif self.button_type == 'move down':
            for mob in global_manager.get('mob_list'):
                if mob.selected and mob.can_move(0, -1):
                    mob.move(0, -1)
                    
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
            get_input('do something', 'Placeholder do something message')
        elif self.button_type == 'instructions':
            if self.global_manager.get('current_instructions_page') == 'none':
                display_instructions_page(0, self.global_manager)
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
        self.global_manager.set('button_list', remove_from_list(self.global_manager.get('button_list'), self))
        self.global_manager.set('image_list', remove_from_list(self.global_manager.get('image_list'), self.image))

class label(button_class):
    '''
    A button that shares most of a normal button's image and tooltip behaviors but does nothing when clicked. Used to display information
    '''
    def __init__(self, coordinates, ideal_width, minimum_height, modes, image_id, message, global_manager): #message is initially a string
        '''
        Inputs:
            coordinates: tuple of 2 integers for initial coordinate x and y values
            ideal_width: int representing the width in pixels of the button. Depending on its message, the label may change its width slightly to avoid cutting off words.
            minimum_height: int representing the minimum height in pixels of the button. For long messages, the height will increase to accomodate the extra words. While this has often not worked correctly, the top of the label should stay in place while the bottom moves down.
            modes: list of strings representing the game modes in which this button is visible, such as 'strategic' for a button appearing when on the strategic map
            image_id: string representing the address of the button's image within the graphics folder such as 'misc/left_button.png' to represent SFA/graphics/misc/left_button.png
            message: string representing the contents of the label. This is converted by format_message to a list of strings, in which each string is a line of text on the label.
        '''
        self.global_manager = global_manager
        self.global_manager.get('label_list').append(self)
        self.modes = modes
        self.message = message
        self.ideal_width = ideal_width
        self.width = ideal_width
        self.font_size = scale_width(25, global_manager)
        self.font_name = "Times New Roman"
        self.font = pygame.font.SysFont(self.font_name, self.font_size)
        self.current_character = 'none'
        self.set_label(self.message)
        if self.width < ideal_width:
            self.width = ideal_width
        self.height = (self.font_size * len(self.message)) + 15
        if self.height < minimum_height:
            self.height = minimum_height
        super().__init__(coordinates, self.width, self.height, 'green', 'label', 'none', self.modes, image_id, global_manager)

    def set_label(self, new_message):
        self.message = new_message
        self.format_message()
        for text_line in self.message:
            if message_width(text_line, self.font_size, self.font_name) + 10 > self.ideal_width:
                self.width = message_width(text_line, self.font_size, self.font_name) + 10

    def format_message(self): #takes a string message and divides it into a list of strings based on length
        new_message = []
        next_line = ""
        next_word = ""
        for index in range(len(self.message)):
            next_word += self.message[index]
            if self.message[index] == " ":
                if message_width(next_line + next_word, self.font_size, self.font_name) > self.ideal_width:
                    new_message.append(next_line)
                    next_line = ""
                next_line += next_word
                next_word = ""
        #if message_width(next_line + next_word, self.font_size, self.font_name) > self.ideal_width and self in level_up_option_list: #normal labels shouldn't go to next line, but level up options should
        #    new_message.append(next_line)
        #    next_line = next_word
        #    new_message.append(next_line)
        #else: #obsolete
        next_line += next_word
        new_message.append(next_line)
            
        greatest_width = 0
        for line in new_message: #while formatting, trim each line to something close to ideal width, then set actual width to the longest one
            if message_width(line, self.font_size, self.font_name) > greatest_width:
                greatest_width = message_width(line, self.font_size, self.font_name)
        self.width = greatest_width + 10
        self.message = new_message

    def update_tooltip(self):
        self.set_tooltip(self.message)
            
    def on_click(self): #labels are buttons to have tooltip functionality but don't do anything when clicked
        i = 0

    def remove(self):
        self.global_manager.set('label_list', remove_from_list(self.global_manager.get('label_list'), self))
        self.global_manager.set('button_list', remove_from_list(self.global_manager.get('button_list'), self))
        self.global_manager.set('image_list', remove_from_list(self.global_manager.get('image_list'), self.image))

    def draw(self):
        if self.global_manager.get('current_game_mode') in self.modes:
            self.image.draw()
            for text_line_index in range(len(self.message)):
                text_line = self.message[text_line_index]
                self.global_manager.get('game_display').blit(text(text_line, self.font, self.global_manager), (self.x + 10, self.global_manager.get('display_height') - (self.y + self.height - (text_line_index * self.font_size))))
                
    def draw_tooltip(self, y_displacement):
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
            self.global_manager.get('game_display').blit(text(text_line, self.global_manager.get('myfont'), global_manager), (self.tooltip_box.x + 10, self.tooltip_box.y + (text_line_index * self.global_manager.get('font_size'))))

class notification(label):
    '''special label with slightly different message and disappears when clicked'''
    
    def __init__(self, coordinates, ideal_width, minimum_height, modes, image, message, global_manager):
        self.global_manager = global_manager
        self.global_manager.get('notification_list').append(self)
        super().__init__(coordinates, ideal_width, minimum_height, modes, image, message, global_manager)

    def format_message(self): #takes a string message and divides it into a list of strings based on length
        new_message = []
        next_line = ""
        next_word = ""
        for index in range(len(self.message)):
            next_word += self.message[index]
            if self.message[index] == " ":
                if message_width(next_line + next_word, self.font_size, self.font_name) > self.ideal_width:
                    new_message.append(next_line)
                    next_line = ""
                next_line += next_word
                next_word = ""
        next_line += next_word
        new_message.append(next_line)
        new_message.append("Click to remove this notification")
        self.message = new_message
                    
    def update_tooltip(self):
        self.set_tooltip(["Click to remove this notification"])
            
    def on_click(self):
        self.remove()
            
    def remove(self):
        super().remove()
        self.global_manager.set('notification_list', remove_from_list(self.global_manager.get('notification_list'), self))
        if len(self.global_manager.get('notification_queue')) >= 1:
            self.global_manager.get('notification_queue').pop(0)
        if len(self.global_manager.get('notification_queue')) > 0:
            notification_to_front(self.global_manager.get('notification_queue')[0], self.global_manager)

class instructions_page(label):
    def __init__(self, instruction_text, global_manager):
        self.global_manager = global_manager
        super().__init__(scale_coordinates(60, 60, self.global_manager), scale_width(self.global_manager.get('default_display_width') - 120, self.global_manager), scale_height(self.global_manager.get('default_display_height') - 120, self.global_manager), ['strategic'], 'misc/default_instruction.png', instruction_text, global_manager)

    def on_click(self):
        if not self.global_manager.get('current_instructions_page_index') == len(self.global_manager.get('instructions_list')) - 1:
            self.global_manager.set('current_instructions_page_index', self.global_manager.get('current_instructions_page_index') + 1)
            self.global_manager.set('current_instructions_page_text', self.global_manager.get('instructions_list')[self.global_manager.get('current_instructions_page_index')])
            self.global_manager.set('current_instructions_page', instructions_page(self.global_manager.get('current_instructions_page_text')), self.global_manager) #create a new page and remove this one
            self.remove()
        else:
            self.remove()
            self.global_manager.set('current_instructions_page', 'none')
            
    def format_message(self):
        '''takes a string message and divides it into a list of strings based on length'''
        new_message = []
        next_line = ""
        next_word = ""
        for index in range(len(self.message)):
            next_word += self.message[index]
            if self.message[index] == " ":
                if message_width(next_line + next_word, self.font_size, self.font_name) > self.ideal_width:
                    new_message.append(next_line)
                    next_line = ""
                next_line += next_word
                next_word = ""
        next_line += next_word
        new_message.append(next_line)
        new_message.append("Click to go to the next instructions page.") #not in superclass
        new_message.append("Press the display instructions button on the right side of the screen again to close the instructions.") #not in superclass
        new_message.append("Page " + str(self.global_manager.get('current_instructions_page_index') + 1))
        
        self.message = new_message
    def update_tooltip(self):
        self.set_tooltip(["Click to go to the next instructions page.", "Press the display instructions button on the right side of the screen again to close the instructions."])

class bar():
    def __init__(self, coordinates, minimum, maximum, current, width, height, full_color, empty_color, global_manager):
        self.global_manager = global_manager
        self.global_manager.get('bar_list').append(self)
        self.x, self.y = coordinates
        self.y = self.global_manager.get('display_height') - self.y
        self.minimum = minimum
        self.maximum = maximum
        self.current = current
        self.width = width
        self.height = height
        self.full_color = full_color
        self.empty_color = empty_color
        self.full_Rect = pygame.Rect(10, 10, 10, 10) #left top width height
        self.empty_Rect = pygame.Rect(10, 10, 10, 10)
        self.Rect = pygame.Rect(10, 10, 10, 10)

    def calculate_full_width(self):
        return(int((self.current/ self.maximum) * self.width))

    def calculate_empty_width(self, full_width):
        return(self.width - full_width)

    def update_bar(self):
        if self.current < self.minimum:
            self.current = self.minimum
        elif self.current > self.maximum:
            self.current = self.maximum
        self.full_Rect.x = self.x
        self.full_Rect.y = self.y
        self.full_Rect.width = self.calculate_full_width()
        self.full_Rect.height = self.height
        self.empty_Rect.height = self.height
        self.empty_Rect.width = self.calculate_empty_width(self.full_Rect.width)
        self.empty_Rect.x = self.x + self.full_Rect.width
        self.empty_Rect.y = self.y
        self.Rect.width = self.full_Rect.width + self.empty_Rect.width
        self.Rect.height = self.height
        self.Rect.x = self.full_Rect.x
        self.Rect.y = self.full_Rect.y

    def draw(self):
        self.update_bar()
        if self.full_Rect.width > 0:
            pygame.draw.rect(game_display, self.full_color, self.full_Rect)
        if self.empty_Rect.width > 0:
            pygame.draw.rect(game_display, self.empty_color, self.empty_Rect)

    def touching_mouse(self):
        if self.Rect.collidepoint(pygame.mouse.get_pos()): #if mouse is in button
            return(True)
        else:
            return(False)
        
class grid():
    def __init__(self, origin_coordinates, pixel_width, pixel_height, coordinate_width, coordinate_height, color, modes, global_manager):
        self.global_manager = global_manager
        self.global_manager.get('grid_list').append(self)
        self.modes = modes
        self.origin_x, self.origin_y = origin_coordinates
        self.coordinate_width = coordinate_width
        self.coordinate_height = coordinate_height
        self.pixel_width = pixel_width
        self.pixel_height = pixel_height
        self.color = color
        self.cell_list = []
        self.create_cells()
        if self.modes == ['strategic']:
            area = self.coordinate_width * self.coordinate_height
            num_worms = area // 5
            for i in range(num_worms):
                self.make_random_terrain_worm(round(area/24), round(area/12), self.global_manager.get('terrain_list')) #sand['mountain', 'grass', 'forest']
            for cell in self.cell_list:
                if cell.y == 0:
                    cell.set_terrain('water')
            num_rivers = random.randrange(2, 4)#2-3
            valid = False
            while not valid:
                valid = True
                start_x_list = []
                for i in range(num_rivers):
                    start_x_list.append(random.randrange(0, self.coordinate_width))
                for index in range(len(start_x_list)):
                    for other_index in range(len(start_x_list)):
                        if not index == other_index:
                            if abs(start_x_list[index] - start_x_list[other_index]) < 3:
                                valid = False
            
            for start_x in start_x_list:
                self.make_random_river_worm(round(coordinate_height * 0.75), round(coordinate_height * 1.25), start_x)
                #self.make_random_river_worm(10, 21, start_x)
            for cell in self.cell_list:
                if cell.y == 0 or cell.y == 1:
                    cell.set_visibility(True)
                
    def draw(self):
        if self.global_manager.get('current_game_mode') in self.modes:
            for cell in self.cell_list:
                cell.draw()

    def draw_grid_lines(self):
        if self.global_manager.get('show_grid_lines'):
            for x in range(0, self.coordinate_width+1):
                pygame.draw.line(self.global_manager.get('game_display'), color_dict['black'], self.convert_coordinates((x, 0)), self.convert_coordinates((x, self.coordinate_height)))
            for y in range(0, self.coordinate_height+1):
                pygame.draw.line(global_manager.get('game_display'), color_dict['black'], self.convert_coordinates((0, y)), self.convert_coordinates((self.coordinate_width, y)))                     



    def find_cell_center(self, coordinates):
        '''converts grid coordinates to pixel coordinates at center of cell'''
        x, y = coordinates
        return((int((self.pixel_width/(self.coordinate_width)) * x) + self.origin_x + int(self.get_cell_width()/2)), (display_height - (int((self.pixel_height/(self.coordinate_height)) * y) + self.origin_y + int(self.get_cell_height()/2))))

    def convert_coordinates(self, coordinates):
        '''converts grid coordinates to pixel coordinates'''
        x, y = coordinates
        return((int((self.pixel_width/(self.coordinate_width)) * x) + self.origin_x), (self.global_manager.get('display_height') - (int((self.pixel_height/(self.coordinate_height)) * y) + self.origin_y )))
    
    def get_height(self):
        return(self.coordinate_height)
    
    def get_width(self):
        return(self.coordinate_width)
    
    def get_cell_width(self):
        return(int(self.pixel_width/self.coordinate_width) + 1)

    def get_cell_height(self):
        return(int(self.pixel_height/self.coordinate_height) + 1)

    def find_cell(self, x, y):
        for cell in self.cell_list:
            if cell.x == x and cell.y == y:
                return(cell)
            
    def create_cells(self):
        for x in range(0, self.coordinate_width):
            for y in range(0, self.coordinate_height):
                self.create_cell(x, y, self)
        for current_cell in self.cell_list:
            current_cell.find_adjacent_cells()
                
    def create_cell(self, x, y, grid):
        new_cell = cell(x, y, self.get_cell_width(), self.get_cell_height(), self, self.color, self.global_manager)
        
    def is_clear(self, x, y):
        if self.find_cell(x, y).occupied == False:
            return(True)
        else:
            return(False)

    def make_resource_list(self, terrain):
        resource_list = []
        if terrain == 'clear':
            for i in range(135):
                resource_list.append('none')
            for i in range(5):
                resource_list.append('ivory')
            for i in range(20):
                resource_list.append('natives')
                
        elif terrain == 'mountain':
            for i in range(135):
                resource_list.append('none')
            resource_list.append('diamonds')
            for i in range(2):
                resource_list.append('gold')
            for i in range(4):
                resource_list.append('coffee')
            for i in range(4):
                resource_list.append('copper')
            for i in range(4):
                resource_list.append('iron')
            for i in range(10):
                resource_list.append('natives')
                
        elif terrain == 'hills':
            for i in range(135):
                resource_list.append('none')
            resource_list.append('diamonds')
            for i in range(2):
                resource_list.append('gold')
            for i in range(4):
                resource_list.append('coffee')
            for i in range(4):
                resource_list.append('copper')
            for i in range(4):
                resource_list.append('iron')
            for i in range(10):
                resource_list.append('natives')
        elif terrain == 'jungle':
            for i in range(125):
                resource_list.append('none')
            resource_list.append('diamonds')
            for i in range(6):
                resource_list.append('rubber')
            resource_list.append('coffee')
            for i in range(6):
                resource_list.append('exotic wood')
            for i in range(6):
                resource_list.append('fruit')
            for i in range(15):
                resource_list.append('natives')
        elif terrain == 'swamp':
            for i in range(130):
                resource_list.append('none')
            for i in range(4):
                resource_list.append('ivory')
            for i in range(4):
                resource_list.append('rubber')
            resource_list.append('coffee')
            for i in range(4):
                resource_list.append('exotic wood')
            for i in range(2):
                resource_list.append('fruit')
            for i in range(15):
                resource_list.append('natives')
        elif terrain == 'desert':
            for i in range(140):
                resource_list.append('none')
            for i in range(2):
                resource_list.append('diamonds')
            resource_list.append('gold')
            resource_list.append('ivory')
            for i in range(2):
                resource_list.append('fruit')
            for i in range(2):
                resource_list.append('copper')
            for i in range(2):
                resource_list.append('iron')
            for i in range(10):
                resource_list.append('natives')
        else:
            resource_list.append('none')
        return(resource_list)

    def set_resources(self):
        #terrain_list = ['clear', 'mountain', 'hills', 'jungle', 'swamp', 'desert']
        #clear_resources = make_resource_list('clear')
        #mountain_resources = make_resource_list('mountain')
        #hills_resources = make_resource_list('hills')
        #jungle_resources = make_resource_list('jungle')
        #swamp_resources = make_resource_list('desert')
        #water_resources = make_resource_list('water')
        #resource_list_dict = {'clear': clear_resources, 'mountain': mountain_resources, 'hills': hills_resources, 'jungle': jungle_resources, 'swamp': swamp_resources, 'desert': desert_resources, 'water': water_resources}
        resource_list_dict = {}
        for terrain in terrain_list:
            resource_list_dict[terrain] = self.make_resource_list(terrain)
        resource_list_dict['water'] = self.make_resource_list('water')
        for cell in self.cell_list:
            cell.set_resource(random.choice(resource_list_dict[cell.terrain]))
            
    def make_random_terrain_worm(self, min_len, max_len, possible_terrains):
        start_x = random.randrange(0, self.coordinate_width)
        start_y = random.randrange(0, self.coordinate_height)
        current_x = start_x
        current_y = start_y
        worm_length = random.randrange(min_len, max_len + 1)
        terrain = random.choice(possible_terrains)
        self.find_cell(current_x, current_y).set_terrain(terrain)
        counter = 0        
        while not counter == worm_length:           
            counter = counter + 1
            direction = random.randrange(1, 5) #1 north 2 east 3 south 4 west
            if not (((current_x == self.coordinate_width - 1) and direction == 2) or ((current_x == 0) and direction == 4) or ((current_y == self.coordinate_height - 1) and direction == 3) or ((current_y == 0) and direction == 1)):
                if direction == 3:
                    current_y = current_y + 1
                elif direction == 2:
                    current_x = current_x + 1
                elif direction == 1:
                    current_y = current_y - 1
                elif direction == 4:
                    current_x = current_x - 1
                self.find_cell(current_x, current_y).set_terrain(terrain)
                
    def make_random_river_worm(self, min_len, max_len, start_x):
        #start_x = random.randrange(0, self.coordinate_width)
        start_y = 1 #random.randrange(0, self.coordinate_height)
        current_x = start_x
        current_y = start_y
        worm_length = random.randrange(min_len, max_len + 1)
        terrain = 'water' #random.choice(possible_terrains)
        self.find_cell(current_x, current_y).set_terrain(terrain)
        counter = 0        
        while not counter == worm_length:           
            counter = counter + 1
            direction = random.randrange(1, 7) #1 north 2 east 3 south 4 west
            if direction == 1 or direction == 5 or direction == 6:
                direction = 3 #turns extras and south to north
            if not (((current_x == self.coordinate_width - 1) and direction == 2) or ((current_x == 0) and direction == 4) or ((current_y == self.coordinate_height - 1) and direction == 3) or ((current_y == 0) and direction == 1)):
                if direction == 3: #or direction == 1:
                    current_y = current_y + 1
                elif direction == 2:
                    current_x = current_x + 1
                #if direction == 1:
                #   current_y = current_y - 1
                elif direction == 4:
                    current_x = current_x - 1
                self.find_cell(current_x, current_y).set_terrain(terrain)
    '''            
    def make_coordinate_terrain_worm(self, start_x, start_y, min_len, max_len, possible_terrains):
        current_x = start_x
        current_y = start_y
        worm_length = random.randrange(min_len, max_len + 1)
        terrain = random.choice(possible_terrains)
        self.find_cell(current_x, current_y).set_terrain(terrain)
        counter = 0        
        while not counter == worm_length:           
            counter = counter + 1
            direction = random.randrange(1, 5)
            if not (((current_x == self.coordinate_width - 1) and direction == 2) or ((current_x == 0) and direction == 4) or ((current_y == self.coordinate_height - 1) and direction == 3) or ((current_y == 0) and direction == 1)):
                if direction == 3:
                    current_y = current_y + 1
                if direction == 2:
                    current_x = current_x + 1
                if direction == 1:
                   current_y = current_y - 1
                if direction == 4:
                    current_x = current_x - 1
                self.find_cell(current_x, current_y).set_terrain(terrain)
                
    def make_coordinate_river_worm(self, start_x, start_y, min_len, max_len):
        current_x = start_x
        current_y = start_y
        worm_length = random.randrange(min_len, max_len + 1)
        terrain = 'water' #random.choice(possible_terrains)
        self.find_cell(current_x, current_y).set_terrain(terrain)
        counter = 0        
        while not counter == worm_length:           
            counter = counter + 1
            direction = random.randrange(1, 5)
            if not (((current_x == self.coordinate_width - 1) and direction == 2) or ((current_x == 0) and direction == 4) or ((current_y == self.coordinate_height - 1) and direction == 3) or ((current_y == 0) and direction == 1)):
                if direction == 3 or direction == 1:
                    current_y = current_y + 1
                if direction == 2:
                    current_x = current_x + 1
                #if direction == 1:
                #   current_y = current_y - 1
                if direction == 4:
                    current_x = current_x - 1
                self.find_cell(current_x, current_y).set_terrain(terrain)
                '''
class cell():
    def __init__(self, x, y, width, height, grid, color, global_manager):
        self.global_manager = global_manager
        self.move_priority = 99
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.grid = grid
        self.color = color
        self.pixel_x, self.pixel_y = self.grid.convert_coordinates((self.x, self.y))
        self.Rect = pygame.Rect(self.pixel_x, self.pixel_y - self.height, self.width, self.height) #(left, top, width, height)
        self.corners = [(self.Rect.left, self.Rect.top ), (self.Rect.left + self.Rect.width, self.Rect.top), (self.Rect.left, self.Rect.top - self.Rect.height), (self.Rect.left + self.Rect.width, self.Rect.top - self.Rect.height)]
        self.occupied = False
        self.grid.cell_list.append(self)
        self.adjacent_list = [] #list of 4 nearby cells, used for movement
        self.diagonal_adjacent_list = [] #list of 8 nearby cells, used for melee attacks of opportunity
        self.tile = 'none'
        self.resource = 'none'
        self.terrain = 'none'
        self.set_terrain('clear')
        self.set_visibility(False)

    def set_visibility(self, new_visibility):
        self.visible = new_visibility
        if not self.tile == 'none':
            self.tile.set_visibility(new_visibility)
    
    def set_resource(self, new_resource):
        self.resource = new_resource
        self.tile.set_resource(new_resource)

    def set_terrain(self, new_terrain):
        self.terrain = new_terrain
        if (not self.tile == 'none') and self.tile.show_terrain:
            self.tile.set_terrain(new_terrain)
        self.color = terrain_colors[new_terrain]
            
    def draw(self):
        current_color = self.color
        red = current_color[0]
        green = current_color[1]
        blue = current_color[2]
        pygame.draw.rect(self.global_manager.get('game_display'), (red, green, blue), self.Rect)
        
    def find_adjacent_cells(self):
        adjacent_list = []
        diagonal_adjacent_list = []
        if not self.x == 0:
            adjacent_list.append(self.grid.find_cell(self.x - 1, self.y))
            diagonal_adjacent_list.append(self.grid.find_cell(self.x - 1, self.y))
            if not self.y == 0:
                diagonal_adjacent_list.append(self.grid.find_cell(self.x - 1, self.y - 1))
            elif not self.y == self.grid.coordinate_height - 1:
                diagonal_adjacent_list.append(self.grid.find_cell(self.x - 1, self.y + 1))
        if not self.x == self.grid.coordinate_width - 1:
            adjacent_list.append(self.grid.find_cell(self.x + 1, self.y))
            diagonal_adjacent_list.append(self.grid.find_cell(self.x + 1, self.y))
            if not self.y == 0:
                diagonal_adjacent_list.append(self.grid.find_cell(self.x + 1, self.y - 1))
            elif not self.y == self.grid.coordinate_height - 1:
                diagonal_adjacent_list.append(self.grid.find_cell(self.x + 1, self.y + 1))
        if not self.y == 0:
            adjacent_list.append(self.grid.find_cell(self.x, self.y - 1))
        if not self.y == self.grid.coordinate_height - 1:
            adjacent_list.append(self.grid.find_cell(self.x, self.y + 1))
        self.diagonal_adjacent_list = diagonal_adjacent_list
        self.adjacent_list = adjacent_list
        
class free_image():
    def __init__(self, image_id, coordinates, width, height, modes, global_manager):
        self.global_manager = global_manager
        self.modes = modes
        self.width = width
        self.height = height
        self.set_image(image_id)
        self.x, self.y = coordinates
        self.y = self.global_manager.get('display_height') - self.y
        self.global_manager.get('image_list').append(self)
        
    def draw(self):
        if self.global_manager.get('current_game_mode') in self.modes:
            display_image(self.image, self.x, self.y - self.height, self.global_manager)

    def remove(self):
        self.global_manager.get('image_list').remove(self)

    def set_image(self, new_image):
        self.image_id = new_image
        self.image = pygame.image.load('graphics/' + self.image_id)
        self.image = pygame.transform.scale(self.image, (self.width, self.height))

class loading_image_class(free_image):
    def __init__(self, image_id, global_manager):
        super().__init__(image_id, (0, 0), global_manager.get('display_width'), global_manager.get('display_height'), [], global_manager)
        self.global_manager.set('image_list', remove_from_list(self.global_manager.get('image_list'), self))

    def draw(self):
        display_image(self.image, self.x, self.y - self.height, self.global_manager)

class actor_image():
    def __init__(self, actor, width, height, grid, image_description, global_manager):
        self.global_manager = global_manager
        self.last_image_switch = 0
        self.previous_idle_image = 'default'
        self.actor = actor
        self.modes = actor.modes
        self.width = width
        self.height = height
        self.set_image(image_description)
        self.image_description == image_description
        self.global_manager.get('image_list').append(self)
        self.grid = grid
        self.Rect = pygame.Rect(self.actor.x, self.actor.y - self.height, self.width, self.height) #(left, top, width, height), bottom left on coordinates
        self.outline_width = 2
        self.outline = pygame.Rect(self.actor.x - self.outline_width, self.global_manager.get('display_height') - (self.actor.y + self.height + self.outline_width), self.width + (2 * self.outline_width), self.height + (self.outline_width * 2))
        self.x, self.y = self.grid.convert_coordinates((self.actor.x, self.actor.y))

    def get_center_coordinates(self):
        cell_width = self.grid.get_cell_width()
        cell_height = self.grid.get_cell_height()
        return((self.x + round(cell_width / 2), display_height -(self.y + round(cell_height / 2))))
        
    def set_image(self, new_image_description):
        self.last_image_switch = time.time()
        if new_image_description == 'default' or new_image_description == 'right' or new_image_description == 'left':
            self.previous_idle_image = new_image_description
        self.image_description = new_image_description
        self.image_id = self.actor.image_dict[new_image_description]
        try: #use if there are any image path issues to help with file troubleshooting
            self.image = pygame.image.load('graphics/' + self.image_id)
        except:
            print('graphics/' + self.image_id)
            self.image = pygame.image.load('graphics/' + self.image_id)
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        
    def draw(self):
        self.grid_x = self.actor.x
        self.grid_y = self.actor.y
        self.go_to_cell((self.grid_x, self.grid_y))
        #if self.actor.selected:
        #    pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')['light gray'], (self.outline), self.outline_width)
        #if show_selected:
        #    if self.actor.selected:
        #        pygame.draw.rect(game_display, color_dict['light gray'], (self.outline), self.outline_width)
        #    elif self.actor.targeted:
        #        pygame.draw.rect(game_display, color_dict['red'], (self.outline), self.outline_width)
        display_image(self.image, self.x, self.y - self.height, self.global_manager)
        
    def go_to_cell(self, coordinates):
        self.x, self.y = self.grid.convert_coordinates(coordinates)
        self.Rect.x = self.x
        self.Rect.y = self.y - self.height
        self.outline.x = self.x - self.outline_width
        self.outline.y = self.y - (self.height + self.outline_width)
                
    def set_tooltip(self, tooltip_text):
        self.tooltip_text = tooltip_text
        tooltip_width = 50
        for text_line in tooltip_text:
            if message_width(text_line, self.global_manager.get('font_size'), 'Times New Roman') + 10 > tooltip_width:
                tooltip_width = message_width(text_line, self.global_manager.get('font_size'), 'Times New Roman') + 10
        tooltip_height = (self.global_manager.get('font_size') * len(tooltip_text)) + 5
        self.tooltip_box = pygame.Rect(self.actor.x, self.actor.y, tooltip_width, tooltip_height)   
        self.tooltip_outline_width = 1
        self.tooltip_outline = pygame.Rect(self.actor.x - self.tooltip_outline_width, self.actor.y + self.tooltip_outline_width, tooltip_width + (2 * self.tooltip_outline_width), tooltip_height + (self.tooltip_outline_width * 2))

class button_image(actor_image):
    def __init__(self, button, width, height, image_id, global_manager): #image_type can be free or grid
        self.global_manager = global_manager
        self.button = button
        self.width = width
        self.height = height
        self.x = self.button.x
        self.y = self.global_manager.get('display_height') - (self.button.y + self.height) - self.height
        self.last_image_switch = 0
        self.modes = button.modes
        self.image_id = image_id
        self.set_image(image_id)
        self.global_manager.get('image_list').append(self)
        self.grid = grid
        self.Rect = self.button.Rect
        self.outline_width = 2
        self.outline = pygame.Rect(self.x - self.outline_width, self.global_manager.get('display_height') - (self.y + self.height + self.outline_width), self.width + (2 * self.outline_width), self.height + (self.outline_width * 2))

    def update_state(self, new_x, new_y, new_width, new_height):
        self.Rect = self.button.Rect
        self.outline.x = new_x - self.outline_width
        self.outline.y = display_height - (new_y + new_height + self.outline_width)
        self.outline.width = new_width + (2 * self.outline_width)
        self.outline.height = new_height + (self.outline_width * 2)
        self.set_image(self.image_id)
        
    def set_image(self, new_image_id):
        self.image_id = new_image_id
        try:
            self.image = pygame.image.load('graphics/' + self.image_id)#.convert()
        except:
            print('graphics/' + self.image_id)
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        
    def draw(self):
        if self.global_manager.get('current_game_mode') in self.button.modes:
            self.x = self.button.x
            self.y = self.global_manager.get('display_height') - (self.button.y + self.height) + self.height
            display_image(self.image, self.x, self.y - self.height, self.global_manager)
        
    def draw_tooltip(self): #button has tooltip already, so image doesn't need a new tooltip
        i = 0
        
    def set_tooltip(self, tooltip_text):
        i = 0

class actor_bar(bar):
    def __init__(self, coordinates, minimum, maximum, current, width, height, full_color, empty_color, actor, y_multiplier, global_manager):
        super().__init__(coordinates, minimum, maximum, current, width, height, full_color, empty_color, global_manager)
        self.actor = actor
        self.modes = self.actor.modes
        self.y_multiplier = y_multiplier
        
    def update_status(self):
        self.x = int(self.actor.image.x + (self.actor.image.width * 0.1))
        self.y = int(self.actor.image.y - (self.actor.image.height * (0.1 * self.y_multiplier)))
        self.width = int(self.actor.image.width * 0.8)
        self.height = int(self.actor.image.height * 0.075)
        
    def draw(self):
        self.update_status()
        bar.draw(self)
        
    def draw_tooltip(self):
        self.update_status()

class actor():
    def __init__(self, coordinates, grid, modes, global_manager):
        self.global_manager = global_manager
        global_manager.get('actor_list').append(self)
        self.modes = modes
        self.grid = grid
        self.x, self.y = coordinates
        self.name = ''
        self.set_name('placeholder')
        self.set_coordinates(self.x, self.y, False)
        #self.controllable = False# obsolete but possibly usable later
        self.selected = False
    
    def set_name(self, new_name):
        self.name = new_name        
       
    def is_clear(self, x, y):
        return self.grid.is_clear(x, y)
    
    def set_coordinates(self, x, y, able_to_print):
        if self.is_clear(x, y):
            self.grid.find_cell(self.x, self.y).occupied = False
            self.x = x
            self.y = y
            self.grid.find_cell(self.x, self.y).occupied = True
        else:#elif able_to_print:
            print_to_screen('This cell is blocked.', self.global_manager)
            
    def set_tooltip(self, new_tooltip):
        self.image.set_tooltip(new_tooltip)
    
    def update_tooltip(self):
        self.set_tooltip(['Name: ' + self.name])
        
    def remove(self):
        self.global_manager.set('actor_list', remove_from_list(self.global_manager.get('actor_list'), self))
        self.global_manager.set('image_list', remove_from_list(self.global_manager.get('image_list'), self.image))

    def interact(self, other):
        if other == None:
            print_to_screen(self.name + ' has nothing to interact with.')
        else:
            print_to_screen(self.name + ' is interacting with ' + other.name)

    def touching_mouse(self):
        if self.image.Rect.collidepoint(pygame.mouse.get_pos()): #if mouse is in button
            return(True)
        else:
            return(False)

    def can_show_tooltip(self): #moved to actor
        if self.touching_mouse() and self.global_manager.get('current_game_mode') in self.modes: #and not targeting_ability 
            return(True)
        else:
            return(False)

    def draw_tooltip(self, y_displacement):
        self.update_tooltip()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_y += y_displacement
        if (mouse_x + self.image.tooltip_box.width) > self.global_manager.get('display_width'):
            mouse_x = self.global_manager.get('display_width') - self.image.tooltip_box.width
        if (self.global_manager.get('display_height') - mouse_y) - (len(self.image.tooltip_text) * self.global_manager.get('font_size') + 5 + self.image.tooltip_outline_width) < 0:
            mouse_y = self.global_manager.get('display_height') - self.image.tooltip_box.height
        self.image.tooltip_box.x = mouse_x
        self.image.tooltip_box.y = mouse_y
        self.image.tooltip_outline.x = self.image.tooltip_box.x - self.image.tooltip_outline_width
        self.image.tooltip_outline.y = self.image.tooltip_box.y - self.image.tooltip_outline_width
        pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')['black'], self.image.tooltip_outline)
        pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')['white'], self.image.tooltip_box)
        for text_line_index in range(len(self.image.tooltip_text)):
            text_line = self.image.tooltip_text[text_line_index]
            self.global_manager.get('game_display').blit(text(text_line, self.global_manager.get('myfont'), self.global_manager), (self.image.tooltip_box.x + 10, self.image.tooltip_box.y + (text_line_index * self.global_manager.get('font_size'))))
            
class mob(actor):
    '''a mobile and selectable actor'''
    def __init__(self, coordinates, grid, image_id, name, modes, global_manager):
        super().__init__(coordinates, grid, modes, global_manager)
        self.image_dict = {'default': image_id}
        self.image = actor_image(self, self.grid.get_cell_width(), self.grid.get_cell_height(), self.grid, 'default', self.global_manager)#self, actor, width, height, grid, image_description, global_manager
        global_manager.get('mob_list').append(self)
        self.set_name(name)

    def draw_outline(self):
        pygame.draw.rect(self.global_manager.get('game_display'), self.global_manager.get('color_dict')['dark gray'], (self.image.outline), self.image.outline_width)

    def update_tooltip(self):
        self.set_tooltip([self.name])

    def remove(self):
        super().remove()
        global_manager.set('mob_list', remove_from_list(global_manager.get('mob_list'), self)) #make a version of mob_list without self and set mob_list to it

    def can_move(self, x_change, y_change):
        future_x = self.x + x_change
        future_y = self.y + y_change
        if future_x >= 0 and future_x < self.grid.coordinate_width and future_y >= 0 and future_y < self.grid.coordinate_height:
            if self.grid.find_cell(future_x, future_y).visible:
                if not self.grid.find_cell(future_x, future_y).terrain == 'water':
                    return(True)
                else:
                    if self.grid.find_cell(future_x, future_y).visible:
                        print_to_screen("You can't move into the water.", self.global_manager) #to do: change this when boats are added
                        return(False)
            else:
                print_to_screen("You can't move into an unexplored tile.", self.global_manager)
                return(False)

        else:
            print_to_screen("You can't move off of the map.", self.global_manager)
            return(False)

    def move(self, x_change, y_change):
        self.x += x_change
        self.y += y_change


class explorer(mob):
    '''mob that can explore tiles'''
    def __init__(self, coordinates, grid, image_id, name, modes, global_manager):
        super().__init__(coordinates, grid, image_id, name, modes, global_manager)
        self.grid.find_cell(self.x, self.y).set_visibility(True)
        self.veteran = False
        self.veteran_icon = 'none'
        
    def can_move(self, x_change, y_change):
        future_x = self.x + x_change
        future_y = self.y + y_change
        if future_x >= 0 and future_x < self.grid.coordinate_width and future_y >= 0 and future_y < self.grid.coordinate_height:
            if not self.grid.find_cell(future_x, future_y).terrain == 'water':
                return(True)
            else:
                if self.grid.find_cell(future_x, future_y).visible:
                    print_to_screen("You can't move into the water.", self.global_manager) #to do: change this when boats are added
                    return(False)
                else:
                    return(True) #will attempt to move there and discover it and discover it
        else:
            print_to_screen("You can't move off of the map.", self.global_manager)
            return(False)

    def move(self, x_change, y_change):
        future_x = self.x + x_change
        future_y = self.y + y_change
        died = False
        future_cell = self.grid.find_cell(future_x, future_y)
        if future_cell.visible == False:
            if self.veteran:
                print_to_screen("The veteran explorer can roll twice and pick the higher result.", self.global_manager)
                roll_result = max(roll(6, "Exploration roll", 4, self.global_manager), roll(6, "Exploration roll", 4, self.global_manager))
                print_to_screen("The higher result, " + str(roll_result) + ", was used.", self.global_manager)
                self.global_manager.get('roll_label').set_label("Roll: " + str(roll_result)) #label should show the roll that was used
            else:
                roll_result = roll(6, "Exploration roll", 4, self.global_manager)
                if roll_result == 6:
                    self.veteran = True
                    print_to_screen("This explorer has become a veteran explorer.", self.global_manager)
                    self.set_name("Veteran explorer")
                    self.veteran_icon = tile_class((self.x, self.y), self.grid, 'misc/veteran_icon.png', 'veteran icon', ['strategic'], False, self.global_manager)
            if roll_result > 4: #4+ required on D6 for exploration
                if not future_cell.resource == 'none':
                    print_to_screen("You discovered a " + future_cell.terrain + " tile with a " + future_cell.resource + " resource.", self.global_manager)
                else:
                    print_to_screen("You discovered a " + future_cell.terrain + " tile.", self.global_manager)
                future_cell.set_visibility(True)
                if not future_cell.terrain == 'water':
                    self.x += x_change
                    self.y += y_change
            else:
                print_to_screen("You were not able to explore the tile.", self.global_manager)
            if roll_result == 1:
                print_to_screen("This explorer has died.", self.global_manager)
                self.remove()
                died = True
                
        else:
            self.x += x_change
            self.y += y_change
        if not died and self.veteran:
            self.veteran_icon.x = self.x
            self.veteran_icon.y = self.y

    def remove(self):
        super().remove()
        if not self.veteran_icon == 'none':
            self.veteran_icon.remove()

class tile_class(actor):
    '''like an obstacle without a tooltip or movement blocking'''
    def __init__(self, coordinates, grid, image, name, modes, show_terrain, global_manager): #show_terrain is like a subclass, true is terrain tile, false is non-terrain tile
        super().__init__(coordinates, grid, modes, global_manager)
        self.set_name(name)
        self.global_manager.get('tile_list').append(self)
        self.image_dict = {'default': image}
        self.image = tile_image(self, self.grid.get_cell_width(), self.grid.get_cell_height(), grid, 'default', global_manager)
        #self.shader = tile_shader(self, self.grid.get_cell_width(), self.grid.get_cell_height(), grid, 'default', global_manager)
        self.show_terrain = show_terrain
        self.cell = self.grid.find_cell(self.x, self.y)
        if self.cell.tile == 'none':
            self.cell.tile = self
        if self.show_terrain: #to do: make terrain tiles a subclass
            self.resource_icon = 'none' #the resource icon is appearance, making it a property of the tile rather than the cell
            self.set_terrain(self.cell.terrain) #terrain is a property of the cell, being stored information rather than appearance, same for resource, set these in cell
            self.image_dict['hidden'] = 'scenery/paper_hidden.png'#'scenery/hidden.png'
            self.set_visibility(self.cell.visible)
        elif self.name == 'resource icon':
            self.image_dict['hidden'] = 'misc/empty.png'
        else:
            self.terrain = 'floor'

    def set_visibility(self, new_visibility):
        if new_visibility == True:
            image_name = 'default'
        else:
            image_name = 'hidden'
            
        self.image.set_image(image_name)
        self.image.previous_idle_image = image_name
        if not self.resource_icon == 'none':
            self.resource_icon.image.set_image(image_name)
            self.resource_icon.image.previous_idle_image = image_name
            
    def set_resource(self, new_resource):
        if not self.resource_icon == 'none':
            self.resource_icon.remove()
            self.resource_icon = 'none'
        self.resource = new_resource
        if not self.cell.resource == 'none':
            self.resource_icon = tile_class((self.x, self.y), self.grid, 'scenery/resources/' + self.cell.resource + '.png', 'resource icon', ['strategic'], False, global_manager)
            self.set_visibility(self.cell.visible)
            
    def set_terrain(self, new_terrain): #to do, add variations like grass to all terrains
        if new_terrain == 'clear':
            #random_grass = random.randrange(1, 3) #clear, hills, jungle, water, mountain, swamp, desert
            #self.image_dict['default'] = 'scenery/terrain/clear' + str(random_grass) + '.png'
            self.image_dict['default'] = 'scenery/terrain/clear.png'
            
        elif new_terrain == 'hills':
            self.image_dict['default'] = 'scenery/terrain/hills.png'
            
        elif new_terrain == 'jungle':
            self.image_dict['default'] = 'scenery/terrain/jungle.png'
            
        elif new_terrain == 'water':
            self.image_dict['default'] = 'scenery/terrain/water.png'
            
        elif new_terrain == 'mountain':
            self.image_dict['default'] = 'scenery/terrain/mountain.png'
            
        elif new_terrain == 'swamp':
            self.image_dict['default'] = 'scenery/terrain/swamp.png'
            
        elif new_terrain == 'desert':
            self.image_dict['default'] = 'scenery/terrain/desert.png'
            
        #self.image.set_image('default')

    def update_tooltip(self):
        if self.show_terrain: #if is terrain, show tooltip
            tooltip_message = []
            if self.cell.visible:
                tooltip_message.append('This is a ' + self.cell.terrain + ' tile.')
                if not self.cell.resource == 'none':
                    tooltip_message.append('This tile has a ' + self.cell.resource + ' resource.')
            else:
                tooltip_message .append('This tile has not been explored.')
            self.set_tooltip(tooltip_message)
        else:
            self.set_tooltip([])

    def set_coordinates(self, x, y, able_to_print):
        my_cell = self.grid.find_cell(self.x, self.y)
        #if self.is_clear(x, y):
        #my_cell.occupied = False
        self.x = x
        self.y = y
        my_cell = self.grid.find_cell(self.x, self.y)
        #my_cell.occupied = False
        #else:
        #    if self.controllable and able_to_print:
        #        print_to_screen("You can't move to an occupied cell.")
                
    def remove(self):
        super().remove()
        self.global_manager.set('tile_list', remove_from_list(self.global_manager.get('tile_list'), self))
        self.global_manager.set('image_list', remove_from_list(self.global_manager.get('image_list'), self.image))
        #self.global_manager.set('image_list', remove_from_list(self.global_manager.get('image_list'), self.shader))
        self.cell.tile = 'none'

    def can_show_tooltip(self): #tiles don't have tooltips, except for terrain tiles
        if self.show_terrain == True:
            if self.touching_mouse() and self.global_manager.get('current_game_mode') in self.modes: #and not targeting_ability 
                return(True)
            else:
                return(False)
        else:
            return(False)

class overlay_tile(tile_class):
    '''kind of tile, preferably transparent, that appears in front of obstacles. Good for darkness and such'''
    def __init__(self, actor, width, height, grid, image_id, show_terrain, global_manager):
        super().__init__(actor, width, height, grid, image_id, show_terrain, global_manager)
        self.global_manager.get('overlay_tile_list').append(self)
        
    def remove(self):
        super().remove()
        self.global_manager.set('overlay_tile_list', remove_from_list(self.global_manager.get('overlay_tile_list'), self))

class tile_image(actor_image):
    def __init__(self, actor, width, height, grid, image_description, global_manager):
        super().__init__(actor, width, height, grid, image_description, global_manager)
        self.grid_x = self.actor.x
        self.grid_y = self.actor.y
        self.go_to_cell((self.grid_x, self.grid_y))

    def go_to_cell(self, coordinates):
        self.x, self.y = self.grid.convert_coordinates(coordinates)
        self.Rect.x = self.x
        self.Rect.y = self.y - self.height
        self.outline.x = self.x - self.outline_width
        self.outline.y = self.y - (self.height + self.outline_width)
        
    def draw(self):
        self.grid_x = self.actor.x
        self.grid_y = self.actor.y
        self.go_to_cell((self.grid_x, self.grid_y))
        display_image(self.image, self.x, self.y - self.height, self.global_manager)

'''class tile_shader(tile_image):
    def __init__(self, actor, width, height, grid, image_description, global_manager):
        super().__init__(actor, width, height, grid, image_description, global_manager)
        self.shading = False
        self.image = pygame.image.load('graphics/misc/yellow_shader.png')
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        
    def draw(self):
        if self.shading:
            super().draw()'''
        
        
'''class strategic_actor(actor): #just add locations as a class when needed
    #actor that operates on the strategic map: able to move and use actions unlike actor, able to ignore whether cells are occupied and not have health unlike mob
    def __init__(self, coordinates, grid, image_dict, controllable, modes, global_manager):
        super().__init__(coordinates, grid, modes, global_manager)
        self.image_dict = image_dict
        self.image = actor_image(self, self.grid.get_cell_width(), self.grid.get_cell_height(), grid, 'default', global_manager)
        self.controllable = controllable
        self.image.set_image('default')
        strategic_actor_list.append(self)
        self.set_name('strategic actor')

    def set_coordinates(self, x, y, able_to_print):
        #on the strategic map there can be multiple strategic actors on each other, such as the player's party on a location, able to print is an unnecessary parameter from parent kept for inheritance rules
        self.x = x
        self.y = y
                
    def update_tooltip(self):
        self.set_tooltip(['Strategic actor tooltip'])
        
    def remove(self):
        super().remove()
        self.global_manager.set('strategic_actor_list', remove_from_list(global_manager.get('strategic_actor_list'), self))'''

def roll(num_sides, roll_type, requirement, global_manager):
    print_to_screen("", global_manager)
    result = random.randrange(1, num_sides + 1)
    global_manager.get('roll_label').set_label("Roll: " + str(result))
    print_to_screen(roll_type + ": " + str(requirement) + "+ required to succeed", global_manager)
    if result >= requirement:
        print_to_screen("You rolled a " + str(result) + ": success!", global_manager)
        #return(True)
    else:
        print_to_screen("You rolled a " + str(result) + ": failure", global_manager)
        #return(False)
    return(result) #returns int rather than boolean
    
def remove_from_list(received_list, item_to_remove):
    output_list = []
    for item in received_list:
        if not item == item_to_remove:
            output_list.append(item)
    return(output_list)

def get_input(solicitant, message):
    input_manager.start_receiving_input(solicitant, message)

def calculate_distance(coordinate1, coordinate2):
    x1, y1 = coordinate1
    x2, y2 = coordinate2
    return(((x1 - x2) ** 2) + ((y1 - y2) ** 2)) ** 0.5

def text(message, font, global_manager):
    return(font.render(message, False, global_manager.get('color_dict')['black']))

def rect_to_surface(rect):
    return pygame.Surface((rect.width, rect.height))

def message_width(message, fontsize, font_name):
    current_font = pygame.font.SysFont(font_name, fontsize)
    text_width, text_height = current_font.size(message)
    return(text_width)

def display_image(image, x, y, global_manager):
    global_manager.get('game_display').blit(image, (x, y))

def display_image_angle(image, x, y, angle, global_manager):
    topleft = (x, y)
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)
    global_manager.get('game_display').blit(rotated_image, new_rect.topleft)
    
def manage_text_list(text_list, max_length):
    if len(text_list) > max_length:
        while not len(text_list) == max_length:
            text_list.pop(0)
    return(text_list)

def add_to_message(message, new):
    return (message + new)

def print_to_screen(input_message, global_manager):
    global_manager.get('text_list').append(input_message)

def print_to_previous_message(message, global_manager):
    global_manager.get('text_list')[-1] = global_manager.get('text_list')[-1] + message
    
def clear_message(global_manager):
    global_manager.set('message', '')
    
def toggle(variable):
    if variable == True:
        return(False)
    elif variable == False:
        return(True)
        
def find_distance(first, second):
    '''takes objects with x and y attributes'''
    return((((first.x - second.x) ** 2) + ((first.y - second.y) ** 2)) ** 0.5)

def find_coordinate_distance(first, second):
    '''takes sets of coordinates'''
    first_x, first_y = first
    second_x, second_y = second
    return((((first_x - second_x) ** 2) + ((first_y - second_y) ** 2)) ** 0.5)

def set_game_mode(new_game_mode, global_manager):
    text_list = []
    previous_game_mode = global_manager.get('current_game_mode')
    if new_game_mode == previous_game_mode:
        return()
    elif new_game_mode == 'strategic':
        start_loading(global_manager)
        global_manager.set('current_game_mode', 'strategic')
        global_manager.set('default_text_box_height', 185)
        global_manager.set('text_box_height', global_manager.get('default_text_box_height'))
        copy_tile_list = global_manager.get('tile_list')
        for current_tile in copy_tile_list:
            current_tile.remove()
        create_strategic_map(global_manager)
        print_to_screen("Entering strategic map", global_manager)
    else:
        global_manager.set('current_game_mode', new_game_mode)

def create_strategic_map(global_manager):
    print_to_screen('Creating map...', global_manager)
    update_display(global_manager)
    for current_cell in global_manager.get('strategic_map_grid').cell_list: #recreates the tiles that were deleted upon switching modes, tiles match the stored cell terrain types
        new_terrain = tile_class((current_cell.x, current_cell.y), current_cell.grid, 'misc/empty.png', 'default', ['strategic'], True, global_manager) #creates a terrain tile that will be modified to the grid cell's terrain type
    strategic_map_grid.set_resources()
    

def draw_text_box(global_manager):
    #if global_manager.get('current_game_mode') == 'strategic': #obsolete, text box width could be different on different game modes
    #    greatest_width = 300
    #else:
    greatest_width = 300
    greatest_width = scale_width(greatest_width, global_manager)
    max_screen_lines = (global_manager.get('default_display_height') // 15) - 1
    max_text_box_lines = (global_manager.get('text_box_height') // 15) - 1
    text_index = 0 #probably obsolete, to do: verify that this is obsolete
    for text_index in range(len(global_manager.get('text_list'))):
        if text_index < max_text_box_lines:
            if message_width(global_manager.get('text_list')[-text_index - 1], global_manager.get('font_size'), 'Times New Roman') > greatest_width:
                greatest_width = message_width(global_manager.get('text_list')[-text_index - 1], global_manager.get('font_size'), 'Times New Roman') #manages the width of already printed text lines
    if global_manager.get('input_manager').taking_input:
        if message_width("Response: " + global_manager.get('message'), font_size, 'Times New Roman') > greatest_width: #manages width of user input
            greatest_width = message_width("Response: " + global_manager.get('message'), global_manager.get('font_size'), 'Times New Roman')
    else:
        if message_width(global_manager.get('message'), global_manager.get('font_size'), 'Times New Roman') > greatest_width: #manages width of user input
            greatest_width = message_width(global_manager.get('message'), global_manager.get('font_size'), 'Times New Roman')
    text_box_width = greatest_width + 10
    x, y = scale_coordinates(0, global_manager.get('default_display_height') - global_manager.get('text_box_height'), global_manager)
    pygame.draw.rect(global_manager.get('game_display'), global_manager.get('color_dict')['white'], (x, y, text_box_width, global_manager.get('text_box_height'))) #draws white rect to prevent overlapping
    if global_manager.get('typing'):
        x, y = scale_coordinates(0, global_manager.get('default_display_height') - global_manager.get('text_box_height'), global_manager)
        pygame.draw.rect(global_manager.get('game_display'), global_manager.get('color_dict')['red'], (x, y, text_box_width, global_manager.get('text_box_height')), 3)
        pygame.draw.line(global_manager.get('game_display'), global_manager.get('color_dict')['red'], (0, global_manager.get('display_height') - (global_manager.get('font_size') + 5)), (text_box_width, global_manager.get('display_height') - (global_manager.get('font_size') + 5)))
    else:
        x, y = scale_coordinates(0, global_manager.get('default_display_height') - global_manager.get('text_box_height'), global_manager)
        pygame.draw.rect(global_manager.get('game_display'), global_manager.get('color_dict')['black'], (x, y, text_box_width, global_manager.get('text_box_height')), 3)
        #x, y = (0, default_display_height - (font_size))
        pygame.draw.line(global_manager.get('game_display'), global_manager.get('color_dict')['black'], (0, global_manager.get('display_height') - (global_manager.get('font_size') + 5)), (text_box_width, global_manager.get('display_height') - (global_manager.get('font_size') + 5)))

    global_manager.set('text_list', manage_text_list(global_manager.get('text_list'), max_screen_lines)) #number of lines
    myfont = pygame.font.SysFont('Times New Roman', scale_width(15, global_manager))
    for text_index in range(len(global_manager.get('text_list'))):
        if text_index < max_text_box_lines:
            textsurface = myfont.render(global_manager.get('text_list')[(-1 * text_index) - 1], False, (0, 0, 0))
            global_manager.get('game_display').blit(textsurface,(10, (-1 * global_manager.get('font_size') * text_index) + global_manager.get('display_height') - ((2 * global_manager.get('font_size')) + 5)))
    if global_manager.get('input_manager').taking_input:
        textsurface = myfont.render('Response: ' + global_manager.get('message'), False, (0, 0, 0))
    else:
        textsurface = myfont.render(global_manager.get('message'), False, (0, 0, 0))
    global_manager.get('game_display').blit(textsurface,(10, global_manager.get('display_height') - (global_manager.get('font_size') + 5)))
    
def update_display(global_manager): #to do: transfer if current game mode in modes to draw functions, do not manage it here
    if global_manager.get('loading'):
        global_manager.set('loading_start_time', global_manager.get('loading_start_time') - 1) #makes it faster if the program starts repeating this part
        draw_loading_screen(global_manager)
    else:
        global_manager.get('game_display').fill((125, 125, 125))
        possible_tooltip_drawers = []

        for grid in global_manager.get('grid_list'):
            if global_manager.get('current_game_mode') in grid.modes:
                grid.draw()

        for image in global_manager.get('image_list'):
            image.has_drawn = False

        global_manager.get('background_image').draw()
        global_manager.get('background_image').has_drawn = True
            
        for tile in global_manager.get('tile_list'):
            if global_manager.get('current_game_mode') in tile.image.modes and not tile in global_manager.get('overlay_tile_list'):
                tile.image.draw()
                tile.image.has_drawn = True
        
        for image in global_manager.get('image_list'):
            if not image.has_drawn:
                if global_manager.get('current_game_mode') in image.modes:
                    image.draw()
                    image.has_drawn = True
        for bar in global_manager.get('bar_list'):
            if global_manager.get('current_game_mode') in bar.modes:
                bar.draw()
        for overlay_tile in global_manager.get('overlay_tile_list'):
            if global_manager.get('current_game_mode') in overlay_tile.image.modes:
                overlay_tile.image.draw()
                overlay_tile.image.has_drawn = True
                
        for grid in global_manager.get('grid_list'):
            if global_manager.get('current_game_mode') in grid.modes:
                grid.draw_grid_lines()

        for mob in global_manager.get('mob_list'):
            if mob.selected and global_manager.get('current_game_mode') in mob.image.modes:
                mob.draw_outline()
            
        for actor in global_manager.get('actor_list'):
            #if show_selected and current_game_mode in actor.image.modes:
            #    if actor.selected:
            #        pygame.draw.rect(game_display, color_dict['light gray'], (actor.image.outline), actor.image.outline_width)
            #    elif actor.targeted:
            #        pygame.draw.rect(game_display, color_dict['red'], (actor.image.outline), actor.image.outline_width)
            if actor.can_show_tooltip():
                possible_tooltip_drawers.append(actor) #only one of these will be drawn to prevent overlapping tooltips

        for button in global_manager.get('button_list'):
            if not button in global_manager.get('notification_list'): #notifications are drawn later
                button.draw()
            if button.can_show_tooltip():
                possible_tooltip_drawers.append(button) #only one of these will be drawn to prevent overlapping tooltips
        for label in global_manager.get('label_list'):
            if not label in global_manager.get('notification_list'):
                label.draw()
        for notification in global_manager.get('notification_list'):
            if not notification == global_manager.get('current_instructions_page'):
                notification.draw()
        if global_manager.get('show_text_box'):
            draw_text_box(global_manager)

        if global_manager.get('making_mouse_box'):
            mouse_destination_x, mouse_destination_y = pygame.mouse.get_pos()
            global_manager.set('mouse_destination_x', mouse_destination_x + 4)
            global_manager.set('mouse_destination_y', mouse_destination_y + 4)
            #mouse_destination_y += 4
            if abs(mouse_destination_x - global_manager.get('mouse_origin_x')) > 3 or (mouse_destination_y - global_manager.get('mouse_origin_y')) > 3:
                mouse_box_color = 'dark gray'
                pygame.draw.rect(global_manager.get('game_display'), global_manager.get('color_dict')[mouse_box_color], (min(global_manager.get('mouse_destination_x'), global_manager.get('mouse_origin_x')), min(global_manager.get('mouse_destination_y'), global_manager.get('mouse_origin_y')), abs(global_manager.get('mouse_destination_x') - global_manager.get('mouse_origin_x')), abs(global_manager.get('mouse_destination_y') - global_manager.get('mouse_origin_y'))), 3)
            
        if not global_manager.get('current_instructions_page') == 'none':
            global_manager.get('current_instructions_page').draw()
        if not (global_manager.get('old_mouse_x'), global_manager.get('old_mouse_y')) == pygame.mouse.get_pos():
            global_manager.set('mouse_moved_time', time.time())
            old_mouse_x, old_mouse_y = pygame.mouse.get_pos()
            global_manager.set('old_mouse_x', old_mouse_x)
            global_manager.set('old_mouse_y', old_mouse_y)
        if time.time() > global_manager.get('mouse_moved_time') + 0.15:#show tooltip when mouse is still
            manage_tooltip_drawing(possible_tooltip_drawers, global_manager)
        pygame.display.update()
        global_manager.set('loading_start_time', global_manager.get('loading_start_time') - 3)

def draw_loading_screen(global_manager):
    global_manager.get('game_display').fill((125, 125, 125))
    global_manager.get('loading_image').draw()
    pygame.display.update()    
    if global_manager.get('loading_start_time') + 2 < time.time():#max of 1 second, subtracts 1 in update_display to lower loading screen showing time
        global_manager.set('loading', False)

def start_loading(global_manager):
    global_manager.set('loading', True)
    global_manager.set('loading_start_time', time.time())
    update_display(global_manager)#draw_loading_screen()

def manage_tooltip_drawing(possible_tooltip_drawers, global_manager):
    possible_tooltip_drawers_length = len(possible_tooltip_drawers)
    if possible_tooltip_drawers_length == 0:
        return()
    elif possible_tooltip_drawers_length == 1:
        possible_tooltip_drawers[0].draw_tooltip(60)
    else:
        tooltip_index = 1
        stopping = False
        for possible_tooltip_drawer in possible_tooltip_drawers:
            if possible_tooltip_drawer == global_manager.get('current_instructions_page'):
                possible_tooltip_drawer.draw_tooltip(tooltip_index * 60)
                stopping = True
            if (possible_tooltip_drawer in global_manager.get('notification_list')) and not stopping:
                possible_tooltip_drawer.draw_tooltip(tooltip_index * 60)
                stopping = True
        if not stopping:
            for possible_tooltip_drawer in possible_tooltip_drawers:
                possible_tooltip_drawer.draw_tooltip(tooltip_index * 60)
                tooltip_index += 1
            
def create_image_dict(stem):
    '''if stem is a certain value, add extra ones, such as special combat animations: only works for images in graphics/mobs'''
    stem = 'mobs/' + stem
    stem += '/'#goes to that folder
    image_dict = {}
    image_dict['default'] = stem + 'default.png'
    image_dict['right'] = stem + 'right.png'  
    image_dict['left'] = stem + 'left.png'
    return(image_dict)

def display_notification(message, global_manager):
    global_manager.get('notification_queue').append(message)
    if len(global_manager.get('notification_queue')) == 1:
        notification_to_front(message, global_manager)

def notification_to_front(message, global_manager):
    '''#displays a notification from the queue, which is a list of string messages that this formats into notifications'''
    new_notification = notification(scale_coordinates(610, 236, global_manager), scale_width(500, global_manager), scale_height(500, global_manager), ['strategic'], 'misc/default_notification.png', message, global_manager)#coordinates, ideal_width, minimum_height, showing, modes, image, message

def show_tutorial_notifications(global_manager):
    intro_message = "Placeholder tutorial/opener notification"
    display_notification(intro_message, global_manager)

def manage_rmb_down(clicked_button, global_manager):
    manage_lmb_down(clicked_button, global_manager)
    
def manage_lmb_down(clicked_button, global_manager): #to do: seems to be called when lmb/rmb is released rather than pressed, clarify name
    if global_manager.get('making_mouse_box'): 
        if not clicked_button:#do not do selecting operations if user was trying to click a button
            for mob in global_manager.get('mob_list'):
                if mob.image.Rect.colliderect((min(global_manager.get('mouse_destination_x'), global_manager.get('mouse_origin_x')), min(global_manager.get('mouse_destination_y'), global_manager.get('mouse_origin_y')), abs(global_manager.get('mouse_destination_x') - global_manager.get('mouse_origin_x')), abs(global_manager.get('mouse_destination_y') - global_manager.get('mouse_origin_y')))):
                    mob.selected = True
                else:
                    mob.selected = False
        global_manager.set('making_mouse_box', False) #however, stop making mouse box regardless of if a button was pressed

def scale_coordinates(x, y, global_manager):
    x_ratio = global_manager.get('display_width')/global_manager.get('default_display_width')
    y_ratio = global_manager.get('display_height')/global_manager.get('default_display_height')
    scaled_x = round(x * x_ratio)
    scaled_y = round(y * y_ratio)
    return(scaled_x, scaled_y)

def scale_width(width, global_manager):
    ratio = global_manager.get('display_width')/global_manager.get('default_display_width')
    scaled_width = round(width * ratio)
    return(scaled_width)

def scale_height(height, global_manager):
    ratio = global_manager.get('display_height')/global_manager.get('default_display_height')
    scaled_height = round(height * ratio)
    return(scaled_height)

def generate_article(word):
    vowels = ['a', 'e', 'i', 'o', 'u']
    if word[0] in vowels:
        return('an')
    else:
        return('a')

def display_instructions_page(page_number, global_manager):
    global_manager.set('current_instructions_page_index', page_number)
    global_manager.set('current_instructions_page_text', global_manager.get('instructions_list')[page_number])
    global_manager.set('current_instructions_page', instructions_page(global_manager.get('current_instructions_page_text'), global_manager))

global_manager = global_manager_template()#manager of a dzictionary of what would be global variables passed between functions and classes
resolution_finder = pygame.display.Info()
global_manager.set('default_display_width', 1728)#all parts of game made to be at default and scaled to display
global_manager.set('default_display_height', 972)
global_manager.set('display_width', resolution_finder.current_w - round(global_manager.get('default_display_width')/10))
global_manager.set('display_height', resolution_finder.current_h - round(global_manager.get('default_display_height')/10))
global_manager.set('loading', True)
global_manager.set('loading_start_time', time.time())
global_manager.set('myfont', pygame.font.SysFont('Times New Roman', scale_width(15, global_manager)))
global_manager.set('font_size', scale_width(15, global_manager))
global_manager.set('game_display', pygame.display.set_mode((global_manager.get('display_width'), global_manager.get('display_height'))))

pygame.display.set_caption('SFA')
color_dict = {'black': (0, 0, 0), 'white': (255, 255, 255), 'light gray': (230, 230, 230), 'dark gray': (150, 150, 150), 'red': (255, 0, 0), 'dark green': (0, 150, 0), 'green': (0, 200, 0), 'bright green': (0, 255, 0), 'blue': (0, 0, 255), 'yellow': (255, 255, 0), 'brown': (132, 94, 59)}
global_manager.set('color_dict', color_dict)
terrain_list = ['clear', 'mountain', 'hills', 'jungle', 'swamp', 'desert']
global_manager.set('terrain_list', terrain_list)
terrain_colors = {'clear': (150, 200, 104), 'hills': (50, 205, 50), 'jungle': (0, 100, 0), 'water': (0, 0, 200), 'mountain': (100, 100, 100), 'swamp': (100, 100, 50), 'desert': (255, 248, 104)}
global_manager.set('terrain_colors', terrain_colors)
global_manager.get('game_display').fill(global_manager.get('color_dict')['white'])
global_manager.set('button_list', [])
global_manager.set('current_instructions_page', 'none')
global_manager.set('current_instructions_page_index', 0)
global_manager.set('instructions_list', [])
#page 1
instructions_message = "Placeholder instructions, use += to add"
global_manager.get('instructions_list').append(instructions_message)


global_manager.set('grid_list', [])
global_manager.set('text_list', [])
global_manager.set('image_list', [])
global_manager.set('bar_list', [])
global_manager.set('actor_list', [])
global_manager.set('mob_list', [])
global_manager.set('tile_list', [])
global_manager.set('overlay_tile_list', [])
global_manager.set('notification_list', [])
global_manager.set('label_list', [])
global_manager.set('notification_queue', [])
pygame.key.set_repeat(300, 200)
global_manager.set('crashed', False)
global_manager.set('lmb_down', False)
global_manager.set('rmb_down', False)
global_manager.set('mmb_down', False)
global_manager.set('typing', False)
global_manager.set('message', '')
global_manager.set('show_grid_lines', True)
global_manager.set('show_text_box', True)
global_manager.set('mouse_origin_x', 0)
global_manager.set('mouse_origin_y', 0)
global_manager.set('mouse_destination_x', 0)
mouse_destination_y = 0
global_manager.set('mouse_destination_y', 0)
global_manager.set('making_mouse_box', False)

global_manager.set('r_shift', 'up')
global_manager.set('l_shift', 'up')
global_manager.set('capital', False)
global_manager.set('r_ctrl', 'up')
global_manager.set('l_ctrl', 'up')
global_manager.set('ctrl', 'up')
global_manager.set('start_time', time.time())
global_manager.set('current_time', time.time())
mouse_moved_time = time.time()
global_manager.set('mouse_moved_time', time.time())
old_mouse_x, old_mouse_y = pygame.mouse.get_pos()#used in tooltip drawing timing
global_manager.set('old_mouse_x', old_mouse_x)
global_manager.set('old_mouse_y', old_mouse_y)
show_tutorial_notifications(global_manager)
global_manager.set('loading_image', loading_image_class('misc/loading.png', global_manager))
global_manager.set('current_game_mode', 'none')
global_manager.set('input_manager', input_manager_template(global_manager))
global_manager.set('background_image', free_image('misc/background.png', (0, 0), global_manager.get('display_width'), global_manager.get('display_height'), ['strategic'], global_manager))
#strategic_map_grid = grid(scale_coordinates(729, 150, global_manager), scale_width(870, global_manager), scale_height(810, global_manager), 64, 60, True, color_dict['dark green'], ['strategic']) #other map sizes
#strategic_map_grid = grid(scale_coordinates(729, 150, global_manager), scale_width(870, global_manager), scale_height(810, global_manager), 32, 30, True, color_dict['dark green'], ['strategic'])
#strategic_map_grid = grid(scale_coordinates(695, 150, global_manager), scale_width(864, global_manager), scale_height(810, global_manager), 16, 15, color_dict['dark green'], ['strategic'], global_manager) #54 by 54
strategic_map_grid = grid(scale_coordinates(695, 50, global_manager), scale_width(960, global_manager), scale_height(900, global_manager), 16, 15, color_dict['dark green'], ['strategic'], global_manager) #60 by 60
global_manager.set('strategic_map_grid', strategic_map_grid)

set_game_mode('strategic', global_manager)

roll_label = label(scale_coordinates(580, global_manager.get('default_display_height') - 50, global_manager), scale_width(90, global_manager), scale_height(50, global_manager), ['strategic'], 'misc/small_label.png', 'Roll: ', global_manager) #coordinates, ideal_width, minimum_height, modes, image_id, message, global_manager
global_manager.set('roll_label', roll_label)

button_start_x = 500#600#x position of leftmost button
button_separation = 60#x separation between each button
current_button_number = 0#tracks current button to move each one farther right

left_arrow_button = button_class(scale_coordinates(button_start_x + (current_button_number * button_separation), 20, global_manager), scale_width(50, global_manager), scale_height(50, global_manager), 'blue', 'move left', pygame.K_a, ['strategic'], 'misc/left_button.png', global_manager)
current_button_number += 1
down_arrow_button = button_class(scale_coordinates(button_start_x + (current_button_number * button_separation), 20, global_manager), scale_width(50, global_manager), scale_height(50, global_manager), 'blue', 'move down', pygame.K_s, ['strategic'], 'misc/down_button.png', global_manager)#movement buttons should be usable in any mode with a grid

up_arrow_button = button_class(scale_coordinates(button_start_x + (current_button_number * button_separation), 80, global_manager), scale_width(50, global_manager), scale_height(50, global_manager), 'blue', 'move up', pygame.K_w, ['strategic'], 'misc/up_button.png', global_manager)
current_button_number += 1
right_arrow_button = button_class(scale_coordinates(button_start_x + (current_button_number * button_separation), 20, global_manager), scale_width(50, global_manager), scale_height(50, global_manager), 'blue', 'move right', pygame.K_d, ['strategic'], 'misc/right_button.png', global_manager)
current_button_number += 2#move more when switching categories

current_button_number += 1

expand_text_box_button = button_class(scale_coordinates(0, global_manager.get('default_display_height') - 50, global_manager), scale_width(50, global_manager), scale_height(50, global_manager), 'black', 'expand text box', pygame.K_j, ['strategic'], 'misc/text_box_size_button.png', global_manager) #'none' for no keybind
toggle_grid_lines_button = button_class(scale_coordinates(global_manager.get('default_display_width') - 50, global_manager.get('default_display_height') - 50, global_manager), scale_width(50, global_manager), scale_height(50, global_manager), 'blue', 'toggle grid lines', pygame.K_g, ['strategic'], 'misc/grid_line_button.png', global_manager)
instructions_button = button_class(scale_coordinates(global_manager.get('default_display_width') - 50, global_manager.get('default_display_height') - 170, global_manager), scale_width(50, global_manager), scale_height(50, global_manager), 'blue', 'instructions', pygame.K_i, ['strategic'], 'misc/instructions.png', global_manager)
toggle_text_box_button = button_class(scale_coordinates(75, global_manager.get('default_display_height') - 50, global_manager), scale_width(50, global_manager), scale_height(50, global_manager), 'blue', 'toggle text box', pygame.K_t, ['strategic'], 'misc/toggle_text_box_button.png', global_manager)

while True: #to do: prevent 2nd row from the bottom of the map grid from ever being completely covered with water due to unusual river RNG, causing infinite loop here, or start increasing y until land is found
    start_x = random.randrange(0, global_manager.get('strategic_map_grid').coordinate_width)
    start_y = 1
    if not(global_manager.get('strategic_map_grid').find_cell(start_x, start_y).terrain == 'water'): #if there is land at that coordinate, break and allow explorer to spawn there
        break
new_explorer = explorer((start_x, start_y), global_manager.get('strategic_map_grid'), 'mobs/explorer/default.png', 'Explorer', ['strategic'], global_manager)#self, coordinates, grid, image_id, name, modes, global_manager

#while True: 
#    start_x = random.randrange(0, global_manager.get('strategic_map_grid').coordinate_width)
#    start_y = 1
#    if not(global_manager.get('strategic_map_grid').find_cell(start_x, start_y).terrain == 'water'): #if there is land at that coordinate, break and allow explorer to spawn there
#        break
#new_worker = mob((start_x, start_y), global_manager.get('strategic_map_grid'), 'mobs/default/default.png', 'Worker', ['strategic'], global_manager)#self, coordinates, grid, image_id, name, modes, global_manager


while not global_manager.get('crashed'):
    if len(global_manager.get('notification_list')) == 0:
        stopping = False
    global_manager.get('input_manager').update_input()
    if global_manager.get('input_manager').taking_input:
        typing = True
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            global_manager.set('crashed', True)
        if global_manager.get('r_shift') == 'down' or global_manager.get('l_shift') == 'down':
            global_manager.set('capital', True)
        else:
            global_manager.set('capital', False)
        if global_manager.get('r_ctrl') == 'down' or global_manager.get('l_ctrl') == 'down':
            global_manager.set('ctrl', True)
        else:
            global_manager.set('ctrl', False)
        if event.type == pygame.KEYDOWN:
            for button in global_manager.get('button_list'):
                if global_manager.get('current_game_mode') in button.modes and not global_manager.get('typing'):
                    if button.has_keybind:
                        if event.key == button.keybind_id:
                            if button.has_released:
                                button.on_click()
                                button.has_released = False
                        else:#stop confirming an important button press if user starts doing something else
                            button.confirming = False
                    else:
                        button.confirming = False
            if event.key == pygame.K_RSHIFT:
                global_manager.set('r_shift', 'down')
            if event.key == pygame.K_LSHIFT:
                global_manager.set('l_shift', 'down')
            if event.key == pygame.K_RCTRL:
                global_manager.set('r_ctrl', 'down')
            if event.key == pygame.K_LCTRL:
                global_manager.set('l_ctrl', 'down')
            if event.key == pygame.K_ESCAPE:
                global_manager.set('typing', False)
                global_manager.set('message', '')
            if event.key == pygame.K_SPACE:
                if global_manager.get('typing'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), ' ')) #add space to message and set message to it
            if event.key == pygame.K_BACKSPACE:
                if global_manager.get('typing'):
                    global_manager.set('message', global_manager.get('message')[:-1]) #remove last character from message and set message to it
            if event.key == pygame.K_a:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'a'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'A'))
            if event.key == pygame.K_b:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'b'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'B'))
            if event.key == pygame.K_c:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'c'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'C'))
            if event.key == pygame.K_d:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'd'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'D'))
            if event.key == pygame.K_e:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'e'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'E'))
            if event.key == pygame.K_f:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'f'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'F'))
            if event.key == pygame.K_g:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'g'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'G'))
            if event.key == pygame.K_h:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'h'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'H'))
            if event.key == pygame.K_i:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'i'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'I'))
            if event.key == pygame.K_j:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'j'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'J'))
            if event.key == pygame.K_k:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'k'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'K'))
            if event.key == pygame.K_l:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'l'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'L'))
            if event.key == pygame.K_m:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'm'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'M'))
            if event.key == pygame.K_n:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'n'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'N'))
            if event.key == pygame.K_o:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'o'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'O'))
            if event.key == pygame.K_p:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'p'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'P'))
            if event.key == pygame.K_q:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'q'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'Q'))
            if event.key == pygame.K_r:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'r'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'R'))
            if event.key == pygame.K_s:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 's'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'S'))
            if event.key == pygame.K_t:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 't'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'T'))
            if event.key == pygame.K_u:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'u'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'U'))
            if event.key == pygame.K_v:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'v'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'V'))
            if event.key == pygame.K_w:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'w'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'W'))
            if event.key == pygame.K_x:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'x'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'X'))
            if event.key == pygame.K_y:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'y'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'Y'))
            if event.key == pygame.K_z:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'z'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), 'Z'))

            if event.key == pygame.K_1:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), '1'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), '!'))
            if event.key == pygame.K_2:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), '2'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), '@'))
            if event.key == pygame.K_3:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), '3'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), '#'))
            if event.key == pygame.K_4:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), '4'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), '$'))
            if event.key == pygame.K_5:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), '5'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), '%'))
            if event.key == pygame.K_6:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), '6'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), '^'))
            if event.key == pygame.K_7:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), '7'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), '&'))
            if event.key == pygame.K_8:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), '8'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), '*'))
            if event.key == pygame.K_9:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), '9'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), '('))
            if event.key == pygame.K_0:
                if global_manager.get('typing') and not global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), '0'))
                elif global_manager.get('typing') and global_manager.get('capital'):
                    global_manager.set('message', add_to_message(global_manager.get('message'), ')'))
                    
        if event.type == pygame.KEYUP:
            for button in global_manager.get('button_list'):
                if not global_manager.get('typing') or button.keybind_id == pygame.K_TAB or button.keybind_id == pygame.K_e:
                    if button.has_keybind:
                        if event.key == button.keybind_id:
                            button.on_release()
                            button.has_released = True
            if event.key == pygame.K_RSHIFT:
                global_manager.set('r_shift', 'up')
            if event.key == pygame.K_LSHIFT:
                global_manager.set('l_shift', 'up')
            if event.key == pygame.K_LCTRL:
                global_manager.set('l_ctrl', 'up')
            if event.key == pygame.K_RCTRL:
                global_manager.set('r_ctrl', 'up')
            if event.key == pygame.K_RETURN:
                if global_manager.get('typing'):
                    if global_manager.get('input_manager').taking_input:
                        #input_response = message
                        global_manager.get('input_manager').taking_input = False
                        print_to_screen('Response: ' + global_manager.get('message'), global_manager)
                        input_manager.receive_input(global_manager.get('message'))
                        check_pointer_removal('not typing')
                    else:
                        print_to_screen(global_manager.get('message'), global_manager)
                    global_manager.set('typing', False)
                    global_manager.set('message', '')
                else:
                    global_manager.set('typing', True)
    global_manager.set('old_lmb_down', global_manager.get('lmb_down'))
    global_manager.set('old_rmb_down', global_manager.get('rmb_down'))
    global_manager.set('old_mmb_down', global_manager.get('mmb_down'))
    lmb_down, mmb_down, rmb_down = pygame.mouse.get_pressed()
    global_manager.set('lmb_down', lmb_down)
    global_manager.set('mmb_down', mmb_down)
    global_manager.set('rmb_down', rmb_down)

    if not global_manager.get('old_rmb_down') == global_manager.get('rmb_down'): #if rmb changes
        if not global_manager.get('rmb_down'): #if user just released rmb
            clicked_button = False
            stopping = False
            if current_instructions_page == 'none':
                for button in global_manager.get('button_list'):
                    if button.touching_mouse() and current_game_mode in button.modes and button in global_manager.get('notification_list') and not stopping:
                        button.on_rmb_click()#prioritize clicking buttons that appear above other buttons and don't press the ones 
                        button.on_rmb_release()
                        clicked_button = True
                        stopping = True
            else:
                if global_manager.get('current_instructions_page').touching_mouse() and current_game_mode in global_manager.get('current_instructions_page').modes:
                    global_manager.get('current_instructions_page').on_rmb_click()
                    clicked_button = True
                    stopping = True
            if not stopping:
                for button in global_manager.get('button_list'):
                    if button.touching_mouse() and global_manager.get('current_game_mode') in button.modes:
                        button.on_rmb_click()
                        button.on_rmb_release()
                        clicked_button = True
            manage_rmb_down(clicked_button, global_manager)

        else:#if user just clicked rmb
            mouse_origin_x, mouse_origin_y = pygame.mouse.get_pos()
            global_manager.set('mouse_origin_x', mouse_origin_x)
            global_manager.set('mouse_origin_y', mouse_origin_y)
            global_manager.set('making_mouse_box', True)
            
    if not global_manager.get('old_lmb_down') == global_manager.get('lmb_down'):#if lmb changes
        if not global_manager.get('lmb_down'):#if user just released lmb
            clicked_button = False
            stopping = False
            if global_manager.get('current_instructions_page') == 'none':
                for button in global_manager.get('button_list'):
                    if button.touching_mouse() and global_manager.get('current_game_mode') in button.modes and (button in global_manager.get('notification_list')) and not stopping:
                        button.on_click()#prioritize clicking buttons that appear above other buttons and don't press the ones 
                        button.on_release()
                        clicked_button = True
                        stopping = True
            else:
                if global_manager.get('current_instructions_page').touching_mouse() and global_manager.get('current_game_mode') in global_manager.get('current_instructions_page').modes:
                    global_manager.get('current_instructions_page').on_click()
                    clicked_button = True
                    stopping = True
            if not stopping:
                for button in global_manager.get('button_list'):
                    if button.touching_mouse() and global_manager.get('current_game_mode') in button.modes:
                        button.on_click()
                        button.on_release()
                        clicked_button = True
            manage_lmb_down(clicked_button, global_manager)#whether button was clicked or not determines whether characters are deselected
            
        else:#if user just clicked lmb
            mouse_origin_x, mouse_origin_y = pygame.mouse.get_pos()
            global_manager.set('mouse_origin_x', mouse_origin_x)
            global_manager.set('mouse_origin_y', mouse_origin_y)
            global_manager.set('making_mouse_box', True)

    if not global_manager.get('loading'):
        update_display(global_manager)
    else:
        draw_loading_screen(global_manager)
    current_time = time.time()
    global_manager.set('current_time', current_time)
    for actor in global_manager.get('actor_list'):
        if not actor.image.image_description == actor.image.previous_idle_image and time.time() >= actor.image.last_image_switch + 0.6:
            actor.image.set_image(actor.image.previous_idle_image)
    start_time = time.time()
    global_manager.set('start_time', start_time)
pygame.quit()
