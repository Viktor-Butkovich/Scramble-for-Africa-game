#to do
#create relevant actors
#review rules
#change strategic map to correct size
#add correct terrain types with corresponding colors and/or images
#trigger button outlines when clicking, currently only works when pressing
#
#done since 6/15
#remove varision-specific program elements
#convert old game mode to a strategic game mode, removing other game modes
import pygame
import time
import random
import math
pygame.init()
clock = pygame.time.Clock()

class input_manager_template():
    def __init__(self):
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
        
    def receive_input(self, received_input):#to do add do something button for testing
        if self.send_input_to == 'do something':
            if received_input == 'done':
                global crashed
                crashed = True
            #elif received_input == 'strategic':
            #    set_game_mode('strategic')
            else:
                print_to_screen("I didn't understand that.")
                
class button_class():
    def __init__(self, coordinates, width, height, color, button_type, showing, keybind_id, modes, image_id):
        global color_dict
        global display_height
        global button_list
        self.has_released = True
        self.modes = modes#game modes in which button is usable
        self.button_type = button_type
        button_list.append(self)
        self.showing = True
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
        self.Rect = pygame.Rect(self.x, display_height - (self.y + self.height), self.width, self.height)#(left, top, width, height), bottom left on coordinates
        self.image = button_image(self, self.width, self.height, image_id, self.showing)
        self.color = color_dict[color]
        self.outline_width = 2
        self.showing_outline = False
        self.outline = pygame.Rect(self.x - self.outline_width, display_height - (self.y + self.height + self.outline_width), self.width + (2 * self.outline_width), self.height + (self.outline_width * 2))
        self.button_type = button_type
        self.update_tooltip()
        self.confirming = False
        
    def can_show(self):
        global current_game_mode
        if current_game_mode in self.modes:
            return(True)
        else:
            return(False)

    def update_tooltip(self):
        global current_game_mode
        if self.button_type == 'move up':
            message = ['Press to move up']
            self.set_tooltip(message)
        elif self.button_type == 'move down':
            message = ['Press to move down']
            self.set_tooltip(message)
        elif self.button_type == 'move left':
            message = ['Press to move left']
            self.set_tooltip(message)
        elif self.button_type == 'move right':
            message = ['Press to move right']
            self.set_tooltip(message)
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
        global font_size
        self.tooltip_text = tooltip_text
        if self.has_keybind:
        #    if not self.tooltip_text[-1] == ("Press " + self.keybind_name + " to use."):#only add if not already there
        #        if self.tooltip_text[-1][0] == "P" and self.tooltip_text[-1][1] == "r" and self.tooltip_text[-1][2] == "e" and self.tooltip_text[-1][3] == "s" and self.tooltip_text[-1][4] == "s":#if a different press message, replace it
        #            self.tooltip_text[-1] = "Press " + self.keybind_name + " to use."
        #        else:
            self.tooltip_text.append("Press " + self.keybind_name + " to use.")
        tooltip_width = 50
        for text_line in tooltip_text:
            if message_width(text_line, font_size, 'Times New Roman') + 10 > tooltip_width:
                tooltip_width = message_width(text_line, font_size, 'Times New Roman') + 10
        tooltip_height = (len(self.tooltip_text) * font_size) + 5
        self.tooltip_box = pygame.Rect(self.x, self.y, tooltip_width, tooltip_height)   
        self.tooltip_outline_width = 1
        self.tooltip_outline = pygame.Rect(self.x - self.tooltip_outline_width, self.y + self.tooltip_outline_width, tooltip_width + (2 * self.tooltip_outline_width), tooltip_height + (self.tooltip_outline_width * 2))

    def touching_mouse(self):
        if self.Rect.collidepoint(pygame.mouse.get_pos()) and self.showing:#if mouse is in button
            return(True)
        else:
            return(False)

    def can_show_tooltip(self):
        global current_game_mode
        if self.touching_mouse() and current_game_mode in self.modes:
            return(True)
        else:
            return(False)
        
    def draw(self):
        global game_display
        global color_dict
        if self.showing:
            if self.button_type == 'do something':
                global text_box_height
                self.y = text_box_height
                self.Rect.y = display_height - (self.y + self.height)
                if text_box_height > 185:#moves button to the side to not block button on top of screen if text box is expanded high enough
                    self.x = 105
                    self.Rect.x = 105
                else:
                    self.x = 0
                    self.Rect.x = 0
            if self.showing_outline:
                pygame.draw.rect(game_display, color_dict['light gray'], self.outline)
            pygame.draw.rect(game_display, self.color, self.Rect)
            self.image.draw()
            myfont = pygame.font.SysFont('Times New Roman', 15)
            if self.has_keybind:
                message = self.keybind_name
                color = 'white'
                textsurface = myfont.render(message, False, color_dict[color])
                game_display.blit(textsurface, (self.x + 10, (display_height - (self.y + self.height - 5))))

    def draw_tooltip(self, y_displacement):
        global game_display
        global font_size
        global myfont
        self.update_tooltip()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_y += y_displacement
        if (mouse_x + self.tooltip_box.width) > display_width:
            mouse_x = display_width - self.tooltip_box.width
        if (display_height - mouse_y) - (len(self.tooltip_text) * font_size + 5 + self.tooltip_outline_width) < 0:
            mouse_y = display_height - self.tooltip_box.height
        self.tooltip_box.x = mouse_x
        self.tooltip_box.y = mouse_y
        self.tooltip_outline.x = self.tooltip_box.x - self.tooltip_outline_width
        self.tooltip_outline.y = self.tooltip_box.y - self.tooltip_outline_width
        pygame.draw.rect(game_display, color_dict['black'], self.tooltip_outline)
        pygame.draw.rect(game_display, color_dict['white'], self.tooltip_box)
        for text_line_index in range(len(self.tooltip_text)):
            text_line = self.tooltip_text[text_line_index]
            game_display.blit(text(text_line, myfont), (self.tooltip_box.x + 10, self.tooltip_box.y + (text_line_index * font_size)))

    def on_rmb_click(self):
        self.on_click()#change in subclasses that use right clicking

    def on_click(self):
        global actor_list
        global controlled_list
        global enemy_list
        global turn_ended
        global current_game_mode
        global mob_list
        global strategic_actor_list
        global retreat_time
        self.showing_outline = True
        if self.button_type == 'hi printer':
            print_to_screen('hi')
        #elif self.button_type == 'move up':
            #if current_game_mode == 'strategic':
            #    for strategic_actor in strategic_actor_list:
            #        if strategic_actor.controllable and strategic_actor.selected:
            #            strategic_actor.move('up')
            #else:
        #elif self.button_type == 'move down':
            #if current_game_mode == 'strategic':
            #    for strategic_actor in strategic_actor_list:
            #        if strategic_actor.controllable and strategic_actor.selected:
            #            strategic_actor.move('down')
            #else:
        #elif self.button_type == 'move right':
            #if current_game_mode == 'strategic':
            #    for strategic_actor in strategic_actor_list:
            #        if strategic_actor.controllable and strategic_actor.selected:
            #            strategic_actor.move('right')
            #else:
        #elif self.button_type == 'move left':
            #if current_game_mode == 'strategic':
            #    for strategic_actor in strategic_actor_list:
            #        if strategic_actor.controllable and strategic_actor.selected:
            #            strategic_actor.move('left')
            #else:
        elif self.button_type == 'toggle grid lines':
            global show_grid_lines
            if show_grid_lines:
                show_grid_lines = False
            else:
                show_grid_lines = True
        elif self.button_type == 'toggle text box':
            global show_text_box
            if show_text_box:
                show_text_box = False
            else:
                show_text_box = True
        elif self.button_type == 'expand text box':
            global text_box_height
            global default_text_box_height
            global display_height
            if text_box_height == default_text_box_height:
                text_box_height = default_display_height - 50#self.height
            else:
                text_box_height = default_text_box_height
        elif self.button_type == 'do something':
            get_input('do something', 'Placeholder do something message')
        elif self.button_type == 'instructions':
            global current_instructions_page
            if current_instructions_page == 'none':
                display_instructions_page(0)
            else:
                if not current_instructions_page == 'none':
                    current_instructions_page.remove()
                    current_instructions_page = 'none'
                global current_instructions_page_index
                current_instructions_page_index = 0

    def on_rmb_release(self):
        self.on_release()#if any rmb buttons did something different on release, change in subclass
                
    def on_release(self):
        self.showing_outline = False

    def remove(self):
        global button_list
        global image_list
        button_list = remove_from_list(button_list, self)
        image_list = remove_from_list(image_list, self.image)

class label(button_class):
    def __init__(self, coordinates, ideal_width, minimum_height, showing, modes, image, message):#message is initially a string
        global label_list
        label_list.append(self)
        self.modes = modes
        self.message = message
        self.ideal_width = ideal_width
        self.width = ideal_width
        self.font_size = scale_width(25)
        self.font_name = "Times New Roman"
        self.font = pygame.font.SysFont(self.font_name, self.font_size)
        self.current_character = 'none'
        self.set_label(self.message)
        if self.width < ideal_width:
            self.width = ideal_width
        self.height = (self.font_size * len(self.message)) + 15
        if self.height < minimum_height:
            self.height = minimum_height
        super().__init__(coordinates, self.width, self.height, 'green', 'label', showing, 'none', self.modes, image)

    def set_label(self, new_message):
        self.message = new_message
        self.format_message()
        for text_line in self.message:
            if message_width(text_line, self.font_size, self.font_name) + 10 > self.ideal_width:
                self.width = message_width(text_line, self.font_size, self.font_name) + 10

    def format_message(self):#takes a string message and divides it into a list of strings based on length
        global level_up_option_list
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
        if message_width(next_line + next_word, self.font_size, self.font_name) > self.ideal_width and self in level_up_option_list:#normal labels shouldn't go to next line, but level up options should
            new_message.append(next_line)
            next_line = next_word
            new_message.append(next_line)
        else:
            next_line += next_word
            new_message.append(next_line)
            
        greatest_width = 0
        for line in new_message:#while formatting, trim each line to something close to ideal width, then set actual width to the longest one
            if message_width(line, self.font_size, self.font_name) > greatest_width:
                greatest_width = message_width(line, self.font_size, self.font_name)
        self.width = greatest_width + 10
        self.message = new_message

    def update_tooltip(self):
        self.set_tooltip(self.message)
            
    def on_click(self):#labels are buttons to have tooltip functionality but don't do anything when clicked
        i = 0

    def remove(self):
        global label_list
        global button_list
        global image_list
        label_list = remove_from_list(label_list, self)
        button_list = remove_from_list(button_list, self)
        image_list = remove_from_list(image_list, self.image)

    def can_show(self):
        return(True)

    def draw(self):
        global game_display
        global color_dict
        global current_game_mode
        if current_game_mode in self.modes and self.showing:
            self.image.draw()
            for text_line_index in range(len(self.message)):
                text_line = self.message[text_line_index]
                game_display.blit(text(text_line, self.font), (self.x + 10, display_height -(self.y + self.height - (text_line_index * self.font_size))))
                
    def draw_tooltip(self, y_displacement):
        global game_display
        global font_size
        global myfont
        self.update_tooltip()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_y += y_displacement
        if (mouse_x + self.tooltip_box.width) > display_width:
            mouse_x = display_width - self.tooltip_box.width
        if (display_height - mouse_y) - (len(self.tooltip_text) * font_size + 5 + self.tooltip_outline_width) < 0:
            mouse_y = display_height - self.tooltip_box.height
        self.tooltip_box.x = mouse_x
        self.tooltip_box.y = mouse_y
        self.tooltip_outline.x = self.tooltip_box.x - self.tooltip_outline_width
        self.tooltip_outline.y = self.tooltip_box.y - self.tooltip_outline_width
        pygame.draw.rect(game_display, color_dict['black'], self.tooltip_outline)
        pygame.draw.rect(game_display, color_dict['white'], self.tooltip_box)
        for text_line_index in range(len(self.tooltip_text)):
            text_line = self.tooltip_text[text_line_index]
            game_display.blit(text(text_line, myfont), (self.tooltip_box.x + 10, self.tooltip_box.y + (text_line_index * font_size)))

class notification(label):#special label with slightly different message and disappears when clicked
    def __init__(self, coordinates, ideal_width, minimum_height, showing, modes, image, message):
        global notification_list
        notification_list.append(self)
        super().__init__(coordinates, ideal_width, minimum_height, showing, modes, image, message)

    def format_message(self):#takes a string message and divides it into a list of strings based on length
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
        global notification_list
        notification_list = remove_from_list(notification_list, self)
        global notification_queue
        if len(notification_queue) >= 1:
            notification_queue.pop(0)
        if len(notification_queue) > 0:
            notification_to_front(notification_queue[0])
''' old code, no current applications in SFA
class pointer(notification):
    def __init__(self, coordinates, ideal_width, minimum_height, showing, modes, image, message, direction, arrow_coordinates, remove_condition):
        super().__init__(coordinates, ideal_width, minimum_height, showing, modes, image, message)
        global pointer_list
        pointer_list.append(self)
        if direction == 'right':
            image_id = 'misc/right_arrow.png'
        elif direction == 'left':
            image_id = 'misc/left_arrow.png'
        elif direction == 'up':
            image_id = 'misc/up_arrow.png'
        elif direction == 'down':
            image_id = 'misc/down_arrow.png'
        self.arrow = free_image(image_id, arrow_coordinates, 100, 100, ['tavern'])#image_id, coordinates, width, height, modes
        self.remove_condition = remove_condition
        
    def remove(self):
        super().remove()
        self.arrow.remove()
        self.arrow = 'none'
        
    def check_removal(self, event):
        if event == self.remove_condition:
            self.remove()
'''
class instructions_page(label):
    def __init__(self, instruction_text):
        global default_display_width
        global default_display_height
        super().__init__(scale_coordinates(60, 60), scale_width(default_display_width - 120), scale_height(default_display_height - 120), True, ['strategic'], 'misc/default_instruction.png', instruction_text)

    def on_click(self):
        global current_instructions_page_index
        global current_instructions_page
        global instructions_list
        if not current_instructions_page_index == len(instructions_list) - 1:
            current_instructions_page_index += 1
            current_instructions_page_text = instructions_list[current_instructions_page_index]
            current_instructions_page = instructions_page(current_instructions_page_text)
            self.remove()
        else:
            self.remove()
            current_instructions_page = 'none'
            
    def format_message(self):#takes a string message and divides it into a list of strings based on length
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
        new_message.append("Click to go to the next instructions page.")#not in superclass
        new_message.append("Press the display instructions button on the right side of the screen again to close the instructions.")# not in superclass
        global current_instructions_page_index
        new_message.append("Page " + str(current_instructions_page_index + 1))
        
        self.message = new_message
    def update_tooltip(self):
        self.set_tooltip(["Click to go to the next instructions page.", "Press the display instructions button on the right side of the screen again to close the instructions."])

class bar():
    def __init__(self, coordinates, minimum, maximum, current, width, height, full_color, empty_color, showing):
        global bar_list
        bar_list.append(self)
        self.x, self.y = coordinates
        self.y = display_height - self.y
        self.showing = showing
        self.minimum = minimum
        self.maximum = maximum
        self.current = current
        self.width = width
        self.height = height
        self.full_color = full_color
        self.empty_color = empty_color
        self.full_Rect = pygame.Rect(10, 10, 10, 10)#left top width height
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
        if self.Rect.collidepoint(pygame.mouse.get_pos()) and self.showing:#if mouse is in button
            return(True)
        else:
            return(False)
        
class grid():
    def __init__(self, origin_coordinates, pixel_width, pixel_height, coordinate_width, coordinate_height, showing, color, modes):
        global terrain_list
        grid_list.append(self)
        self.modes = modes
        self.origin_x, self.origin_y = origin_coordinates
        self.coordinate_width = coordinate_width
        self.coordinate_height = coordinate_height
        self.pixel_width = pixel_width
        self.pixel_height = pixel_height
        self.showing = showing
        self.color = color
        self.cell_list = []
        self.create_cells()
        if self.modes == ['strategic']:
            area = self.coordinate_width * self.coordinate_height
            num_worms = area // 5
            for i in range(num_worms):
                self.make_random_terrain_worm(round(area/24), round(area/12), terrain_list)#sand['mountain', 'grass', 'forest']
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
                
    def draw(self):
        global game_display
        global color_dict
        global current_game_mode
        global show_grid_lines
        if current_game_mode in self.modes:
            for cell in self.cell_list:
                cell.draw()

    def draw_grid_lines(self):
        if self.showing and show_grid_lines:
            for x in range(0, self.coordinate_width+1):
                pygame.draw.line(game_display, color_dict['black'], self.convert_coordinates((x, 0)), self.convert_coordinates((x, self.coordinate_height)))
            for y in range(0, self.coordinate_height+1):
                pygame.draw.line(game_display, color_dict['black'], self.convert_coordinates((0, y)), self.convert_coordinates((self.coordinate_width, y)))                     



    def find_cell_center(self, coordinates):#converts grid coordinates to pixel coordinates at center of cell
        x, y = coordinates
        return((int((self.pixel_width/(self.coordinate_width)) * x) + self.origin_x + int(self.get_cell_width()/2)), (display_height - (int((self.pixel_height/(self.coordinate_height)) * y) + self.origin_y + int(self.get_cell_height()/2))))

    def convert_coordinates(self, coordinates):#converts grid coordinates to pixel coordinates
        x, y = coordinates
        return((int((self.pixel_width/(self.coordinate_width)) * x) + self.origin_x), (display_height - (int((self.pixel_height/(self.coordinate_height)) * y) + self.origin_y )))
    
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
        global color_dict
        new_cell = cell(x, y, self.get_cell_width(), self.get_cell_height(), self, self.color)
        
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
        global terrain_list#terrain_list = ['clear', 'mountain', 'hills', 'jungle', 'swamp', 'desert']
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
            direction = random.randrange(1, 5)#1 north 2 east 3 south 4 west
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
        start_y = 1#random.randrange(0, self.coordinate_height)
        current_x = start_x
        current_y = start_y
        worm_length = random.randrange(min_len, max_len + 1)
        terrain = 'water'#random.choice(possible_terrains)
        self.find_cell(current_x, current_y).set_terrain(terrain)
        counter = 0        
        while not counter == worm_length:           
            counter = counter + 1
            direction = random.randrange(1, 7)#1 north 2 east 3 south 4 west
            if direction == 1 or direction == 5 or direction == 6:
                direction = 3#turns extras and south to north
            if not (((current_x == self.coordinate_width - 1) and direction == 2) or ((current_x == 0) and direction == 4) or ((current_y == self.coordinate_height - 1) and direction == 3) or ((current_y == 0) and direction == 1)):
                if direction == 3:# or direction == 1:
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
        terrain = 'water'#random.choice(possible_terrains)
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
    def __init__(self, x, y, width, height, grid, color):
        self.move_priority = 99
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.grid = grid
        self.color = color
        self.pixel_x, self.pixel_y = self.grid.convert_coordinates((self.x, self.y))
        self.Rect = pygame.Rect(self.pixel_x, self.pixel_y - self.height, self.width, self.height)#(left, top, width, height)
        self.corners = [(self.Rect.left, self.Rect.top ), (self.Rect.left + self.Rect.width, self.Rect.top), (self.Rect.left, self.Rect.top - self.Rect.height), (self.Rect.left + self.Rect.width, self.Rect.top - self.Rect.height)]
        self.occupied = False
        self.grid.cell_list.append(self)
        self.adjacent_list = []#list of 4 nearby cells, used for movement
        self.diagonal_adjacent_list = []#list of 8 nearby cells, used for melee attacks of opportunity
        self.tile = 'none'
        self.resource = 'none'
        self.terrain = 'none'
        self.set_terrain('clear')

    def set_resource(self, new_resource):
        self.resource = new_resource
        self.tile.set_resource(new_resource)

    def set_terrain(self, new_terrain):
        global color_dict
        self.terrain = new_terrain
        if (not self.tile == 'none') and self.tile.show_terrain:
            self.tile.set_terrain(new_terrain)
        self.color = terrain_colors[new_terrain]
            
    def draw(self):#eventually add a tutorial message the first time cells or multiple cells are shaded to explain cell shading mechanics
        global game_display
        global color_dict
        global controlled_list
        global enemy_list
        global my_font
        global show_range
        global current_game_mode
        global current_party
        global sight_range
        current_color = self.color
        red = current_color[0]
        green = current_color[1]
        blue = current_color[2]
        pygame.draw.rect(game_display, (red, green, blue), self.Rect)
        
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
    def __init__(self, image_id, coordinates, width, height, modes):
        global image_list
        self.modes = modes
        self.showing = True
        self.width = width
        self.height = height
        self.set_image(image_id)
        self.x, self.y = coordinates
        self.y = display_height - self.y
        image_list.append(self)
        
    def draw(self):
        global current_game_mode
        if current_game_mode in self.modes:
            display_image(self.image, self.x, self.y - self.height)

    def remove(self):
        global image_list
        image_list.remove(self)

    def set_image(self, new_image):
        self.image_id = new_image
        self.image = pygame.image.load('graphics/' + self.image_id)
        self.image = pygame.transform.scale(self.image, (self.width, self.height))

class loading_image_class(free_image):
    def __init__(self, image_id):
        super().__init__(image_id, (0, 0), display_width, display_height, [])
        global image_list
        image_list = remove_from_list(image_list, self)

    def draw(self):
        display_image(self.image, self.x, self.y - self.height)

class actor_image():
    def __init__(self, actor, width, height, grid, image_description, showing):
        global image_list
        global display_width
        global display_height
        self.last_image_switch = 0
        self.previous_idle_image = 'default'
        self.actor = actor
        self.modes = actor.modes
        self.width = width
        self.height = height
        self.set_image(image_description)
        self.image_description == image_description
        image_list.append(self)
        self.grid = grid
        self.Rect = pygame.Rect(self.actor.x, self.actor.y - self.height, self.width, self.height)#(left, top, width, height), bottom left on coordinates
        self.showing = showing
        self.outline_width = 2
        self.outline = pygame.Rect(self.actor.x - self.outline_width, display_height - (self.actor.y + self.height + self.outline_width), self.width + (2 * self.outline_width), self.height + (self.outline_width * 2))
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
        try:#use if there are any image path issues to help with file troubleshooting
            self.image = pygame.image.load('graphics/' + self.image_id)
        except:
            print('graphics/' + self.image_id)
            self.image = pygame.image.load('graphics/' + self.image_id)
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        
    def draw(self):
        global display_height
        global current_turn
        self.grid_x = self.actor.x
        self.grid_y = self.actor.y
        self.go_to_cell((self.grid_x, self.grid_y))
        #if show_selected:
        #    if self.actor.selected:
        #        pygame.draw.rect(game_display, color_dict['light gray'], (self.outline), self.outline_width)
        #    elif self.actor.targeted:
        #        pygame.draw.rect(game_display, color_dict['red'], (self.outline), self.outline_width)
        display_image(self.image, self.x, self.y - self.height)
        
    def go_to_cell(self, coordinates):
        self.x, self.y = self.grid.convert_coordinates(coordinates)
        self.Rect.x = self.x
        self.Rect.y = self.y - self.height
        self.outline.x = self.x - self.outline_width
        self.outline.y = self.y - (self.height + self.outline_width)
                
    def set_tooltip(self, tooltip_text):
        global font_size
        self.tooltip_text = tooltip_text
        tooltip_width = 50
        for text_line in tooltip_text:
            if message_width(text_line, font_size, 'Times New Roman') + 10 > tooltip_width:
                tooltip_width = message_width(text_line, font_size, 'Times New Roman') + 10
        tooltip_height = (font_size * len(tooltip_text)) + 5
        self.tooltip_box = pygame.Rect(self.actor.x, self.actor.y, tooltip_width, tooltip_height)   
        self.tooltip_outline_width = 1
        self.tooltip_outline = pygame.Rect(self.actor.x - self.tooltip_outline_width, self.actor.y + self.tooltip_outline_width, tooltip_width + (2 * self.tooltip_outline_width), tooltip_height + (self.tooltip_outline_width * 2))

class button_image(actor_image):
    def __init__(self, button, width, height, image_id, showing):#image_type can be free or grid
        global image_list
        global display_width
        global display_height
        self.button = button
        self.width = width
        self.height = height
        self.x = self.button.x
        self.y = display_height - (self.button.y + self.height) - self.height
        self.last_image_switch = 0
        self.modes = button.modes
        self.image_id = image_id
        self.set_image(image_id)
        image_list.append(self)
        self.grid = grid
        self.Rect = self.button.Rect
        self.showing = showing
        self.outline_width = 2
        self.outline = pygame.Rect(self.x - self.outline_width, display_height - (self.y + self.height + self.outline_width), self.width + (2 * self.outline_width), self.height + (self.outline_width * 2))

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
        global display_height
        global current_turn
        global current_game_mode
        if self.button.can_show() and current_game_mode in self.button.modes:
            self.x = self.button.x
            self.y = display_height - (self.button.y + self.height) + self.height
            display_image(self.image, self.x, self.y - self.height)
        
    def draw_tooltip(self):#button has tooltip already, so image doesn't need a new tooltip
        i = 0
        
    def set_tooltip(self, tooltip_text):
        i = 0

class obstacle_image(actor_image):
    def __init(self, actor, width, height, grid, image_description, showing):
        super().__init__(actor, width, height, grid, image_description, showing)
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
        global display_height
        global show_selected
        global current_turn
        self.grid_x = self.actor.x
        self.grid_y = self.actor.y
        self.go_to_cell((self.grid_x, self.grid_y))
        #if show_selected:
        #    if self.actor.targeted:
        #        pygame.draw.rect(game_display, color_dict['red'], (self.outline), self.outline_width)
        display_image(self.image, self.x, self.y - self.height)

class animated_obstacle_image(obstacle_image):
    def __init__(self, actor, width, height, grid, image_description, showing):
        super().__init__(actor, width, height, grid, image_description, showing)
        self.last_switch = time.time()
        self.image_index = 0
    def draw(self):
        if self.last_switch + 0.5 < time.time():
            if self.image_index == 0:
                self.image_index = 1
            else:
                self.image_index = 0
            self.actor.image_dict['default'] = self.actor.images[self.image_index]
            self.set_image('default')
            self.last_switch = time.time()
        super().draw()

class actor_bar(bar):
    def __init__(self, coordinates, minimum, maximum, current, width, height, full_color, empty_color, showing, actor, y_multiplier):
        super().__init__(coordinates, minimum, maximum, current, width, height, full_color, empty_color, showing)
        self.actor = actor
        self.modes = self.actor.modes
        self.y_multiplier = y_multiplier
        
    def update_status(self):
        global current_game_mode
        global color_dict
        self.x = int(self.actor.image.x + (self.actor.image.width * 0.1))
        self.y = int(self.actor.image.y - (self.actor.image.height * (0.1 * self.y_multiplier)))
        self.width = int(self.actor.image.width * 0.8)
        self.height = int(self.actor.image.height * 0.075)
        if current_game_mode == 'tavern' and self.actor.main_character and self.full_color == color_dict['yellow']:#if action bar, don't show in tavern
            self.showing = False
    def draw(self):
        self.update_status()
        bar.draw(self)
        
    def draw_tooltip(self):
        self.update_status()

class actor():
    def __init__(self, coordinates, grid, showing, modes):
        global color_dict
        global actor_list
        global enemy_list
        global controlled_list
        actor_list.append(self)
        self.modes = modes
        self.controllable = False
        self.showing = showing
        self.grid = grid
        self.x, self.y = coordinates
        self.name = ''
        self.set_name('placeholder')
        self.set_coordinates(self.x, self.y, False)
        self.controllable = False
    
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
        elif able_to_print:
            print_to_screen('This cell is blocked.')
            
    def set_tooltip(self, new_tooltip):
        self.image.set_tooltip(new_tooltip)
    
    def update_tooltip(self):
        self.set_tooltip(['Name: ' + self.name])
        
    def remove(self):
        global actor_list
        global enemy_list
        global controlled_list
        global image_list
        global bar_list
        actor_list = remove_from_list(actor_list, self)
        image_list = remove_from_list(image_list, self.image)
        self.showing = False

    def interact(self, other):
        if other == None:
            print_to_screen(self.name + ' has nothing to interact with.')
        else:
            print_to_screen(self.name + ' is interacting with ' + other.name)

    def touching_mouse(self):
        if self.image.Rect.collidepoint(pygame.mouse.get_pos()):#if mouse is in button
            return(True)
        else:
            return(False)

    def can_show_tooltip(self):#moved to actor
        global targeting_ability
        global current_game_mode
        if self.touching_mouse() and current_game_mode in self.modes:# and not targeting_ability 
            return(True)
        else:
            return(False)

    def draw_tooltip(self, y_displacement):
        global game_display
        global font_size
        global myfont
        self.update_tooltip()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_y += y_displacement
        if (mouse_x + self.image.tooltip_box.width) > display_width:
            mouse_x = display_width - self.image.tooltip_box.width
        if (display_height - mouse_y) - (len(self.image.tooltip_text) * font_size + 5 + self.image.tooltip_outline_width) < 0:
            mouse_y = display_height - self.image.tooltip_box.height
        self.image.tooltip_box.x = mouse_x
        self.image.tooltip_box.y = mouse_y
        self.image.tooltip_outline.x = self.image.tooltip_box.x - self.image.tooltip_outline_width
        self.image.tooltip_outline.y = self.image.tooltip_box.y - self.image.tooltip_outline_width
        pygame.draw.rect(game_display, color_dict['black'], self.image.tooltip_outline)
        pygame.draw.rect(game_display, color_dict['white'], self.image.tooltip_box)
        for text_line_index in range(len(self.image.tooltip_text)):
            text_line = self.image.tooltip_text[text_line_index]
            game_display.blit(text(text_line, myfont), (self.image.tooltip_box.x + 10, self.image.tooltip_box.y + (text_line_index * font_size)))

class tile_class(actor):#like an obstacle without a tooltip or movement blocking
    def __init__(self, coordinates, grid, image, name, showing, modes, show_terrain):#show_terrain is like a subclass, true is terrain tile, false is non-terrain tile
        super().__init__(coordinates, grid, showing, modes)
        global tile_list
        self.set_name(name)
        tile_list.append(self)
        self.image_dict = {'default': image}
        self.image = tile_image(self, self.grid.get_cell_width(), self.grid.get_cell_height(), grid, 'default', showing)
        self.shader = tile_shader(self, self.grid.get_cell_width(), self.grid.get_cell_height(), grid, 'default', showing)
        self.show_terrain = show_terrain
        self.cell = self.grid.find_cell(self.x, self.y)
        if self.cell.tile == 'none':
            self.cell.tile = self
        if self.show_terrain:
            #self.cell.resource = 'none'
            self.resource_icon = 'none'#the resource icon is appearance, making it a property of the tile rather than the cell
            self.set_terrain(self.cell.terrain)#terrain is a property of the cell, being stored information rather than appearance, same for resource, set these in cell
        else:
            self.terrain = 'floor'
            
    def set_resource(self, new_resource):
        if not self.resource_icon == 'none':
            self.resource_icon.remove()
            self.resource_icon = 'none'
        self.resource = new_resource
        if not self.cell.resource == 'none':
            self.resource_icon = tile_class((self.x, self.y), self.grid, 'scenery/resources/' + self.cell.resource + '.png', 'resource icon', True, ['strategic'], False)
            
    def set_terrain(self, new_terrain):#to do, add variations like grass to all terrains
        #self.cell.resource = 'none'#reset resources when setting terrain
        #self.cell.terrain = 'new terrain'

            
        if new_terrain == 'clear':
            random_grass = random.randrange(1, 3)#clear, hills, jungle, water, mountain, swamp, desert
            self.image_dict['default'] = 'scenery/terrain/clear' + str(random_grass) + '.png'
            #random_resource = random.randrange(1, 3)#1-2
            #if random_resource == 1:
            #    self.cell.resource = 'gold'
            
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
            
        self.image.set_image('default')

    def update_tooltip(self):
        if self.show_terrain:#if is terrain, show tooltip
            tooltip_message = []
            tooltip_message.append('This is a ' + self.cell.terrain + ' tile.')
            if not self.cell.resource == 'none':
                tooltip_message.append('This tile has a ' + self.cell.resource + ' resource.')
            self.set_tooltip(tooltip_message)
        else:
            self.set_tooltip([])

    def set_coordinates(self, x, y, able_to_print):
        my_cell = self.grid.find_cell(self.x, self.y)
        if self.is_clear(x, y):
            my_cell.occupied = False
            self.x = x
            self.y = y
            my_cell = self.grid.find_cell(self.x, self.y)
            my_cell.occupied = False
        else:
            if self.controllable and able_to_print:
                print_to_screen("You can't move to an occupied cell.")
                
    def remove(self):
        super().remove()
        global tile_list
        tile_list = remove_from_list(tile_list, self)
        global image_list
        image_list = remove_from_list(image_list, self.image)
        image_list = remove_from_list(image_list, self.shader)
        self.cell.tile = 'none'

    def can_show_tooltip(self):#tiles don't have tooltips, except for terrain tiles
        global current_game_mode
        if self.show_terrain == True:
            if self.touching_mouse() and current_game_mode in self.modes:# and not targeting_ability 
                return(True)
            else:
                return(False)
        else:
            return(False)

class overlay_tile(tile_class):#kind of tile, preferably transparent, that appears in front of obstacles. Good for darkness and such
    def __init__(self, actor, width, height, grid, image_id, showing, show_terrain):
        super().__init__(actor, width, height, grid, image_id, showing, show_terrain)
        global overlay_tile_list
        overlay_tile_list.append(self)
        
    def remove(self):
        super().remove()
        global overlay_tile_list
        overlay_tile_list = remove_from_list(overlay_tile_list, self)

class tile_image(actor_image):
    def __init__(self, actor, width, height, grid, image_description, showing):
        super().__init__(actor, width, height, grid, image_description, showing)
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
        global current_game_mode
        global current_party
        global display_height
        self.grid_x = self.actor.x
        self.grid_y = self.actor.y
        self.go_to_cell((self.grid_x, self.grid_y))
        display_image(self.image, self.x, self.y - self.height)

class tile_shader(tile_image):
    def __init__(self, actor, width, height, grid, image_description, showing):
        super().__init__(actor, width, height, grid, image_description, showing)
        self.shading = False
        self.image = pygame.image.load('graphics/misc/yellow_shader.png')
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        
    def draw(self):
        if self.shading:
            super().draw()
        
        
class strategic_actor(actor):#actor that operates on the strategic map: able to move and use actions unlike actor, able to ignore whether cells are occupied and not have health unlike mob
    def __init__(self, coordinates, grid, image_dict, showing, controllable, modes):
        super().__init__(coordinates, grid, showing, modes)
        self.image_dict = image_dict
        self.image = actor_image(self, self.grid.get_cell_width(), self.grid.get_cell_height(), grid, 'default', showing)
        self.controllable = controllable
        self.image.set_image('default')
        strategic_actor_list.append(self)
        self.set_name('strategic actor')

    def set_coordinates(self, x, y, able_to_print):#on the strategic map there can be multiple strategic actors on each other, such as the player's party on a location, able to print is an unnecessary parameter from parent kept for inheritance rules
        self.x = x
        self.y = y
                
    def update_tooltip(self):
        self.set_tooltip(['Strategic actor tooltip'])
        
    def remove(self):
        global strategic_actor_list
        super().remove()
        strategic_actor_list = remove_from_list(strategic_actor_list, self)
        self.showing = False
    
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

def text(message, font):
    global color_dict
    return(font.render(message, False, color_dict['black']))

def rect_to_surface(rect):
    return pygame.Surface((rect.width, rect.height))

def message_width(message, fontsize, font_name):
    current_font = pygame.font.SysFont(font_name, fontsize)
    text_width, text_height = current_font.size(message)
    return(text_width)

def display_image(image, x, y):
    global display_height
    game_display.blit(image, (x, y))

def display_image_angle(image, x, y, angle):
    topleft = (x, y)
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)
    game_display.blit(rotated_image, new_rect.topleft)
    
def manage_text_list(text_list, max_length):
    if len(text_list) > max_length:
        while not len(text_list) == max_length:
            text_list.pop(0)
    return(text_list)

def add_to_message(message, new):
    return (message + new)

def print_to_screen(input_message):
    global text_list
    global message
    global text_to_write_by_letter
    global writing_text_by_letter
    text_list.append(input_message)

def print_to_previous_message(message):
    global text_list
    text_list[-1] = text_list[-1] + message
    
def clear_message():
    global message
    message = ''
    
def toggle(variable):
    if variable == True:
        return(False)
    elif variable == False:
        return(True)
        
def find_distance(first, second):#takes objects with x and y attributes
    return((((first.x - second.x) ** 2) + ((first.y - second.y) ** 2)) ** 0.5)

def find_coordinate_distance(first, second):#takes sets of coordinates
    first_x, first_y = first
    second_x, second_y = second
    return((((first_x - second_x) ** 2) + ((first_y - second_y) ** 2)) ** 0.5)

def move_group(direction):
    global mob_list
    for i in range(10):#loop number is arbitrary
        moving_list = []
        for mob in mob_list:
            if mob.moving:
                moving_list.append(mob)
        for mob in moving_list:
            if mob.can_move(direction):
                mob.move(direction)
                mob.moving = False
    for mob in moving_list:
        mob.move(direction)
        mob.moving = False

def set_game_mode(new_game_mode):
    global current_game_mode
    global text_box_height
    global default_text_box_height
    global stored_party
    global obstacle_list
    global tile_list
    global actor_list
    global image_list
    global text_list
    global loading
    text_list = []
    previous_game_mode = current_game_mode
    if new_game_mode == previous_game_mode:
        return()
    elif new_game_mode == 'strategic':
        start_loading()
        global stored_party
        global controlled_list
        global enemy_list
        global current_turn
        current_game_mode = 'strategic'
        default_text_box_height = 185
        text_box_height = default_text_box_height
        copy_tile_list = tile_list
        for current_tile in copy_tile_list:
            current_tile.remove()
        create_strategic_map()
        print_to_screen("Entering strategic map")
    else:
        current_game_mode = new_game_mode
    #to do, spawn in actors

def create_strategic_map():
    global party_x
    global party_y
    global stored_location_list
    global stored_party
    print_to_screen('Creating map...')
    update_display()
    for current_cell in strategic_map_grid.cell_list:#recreates the tiles that were deleted upon switching modes, tiles match the stored cell terrain types
        new_terrain = tile_class((current_cell.x, current_cell.y), current_cell.grid, 'misc/empty.png', 'default', True, ['strategic'], True)#creates a terrain tile that will be modified to the grid cell's terrain type
    strategic_map_grid.set_resources()
    

def draw_text_box():
    global typing
    global ctrl
    global button_list
    global grid_list
    global image_list
    global display_height
    global display_width
    global text_list
    global message
    global font_size
    global making_mouse_box
    global mouse_origin_x
    global mouse_origin_y
    global mouse_destination_x
    global mouse_destination_y
    global show_range
    global current_game_mode
    global text_box_height
    global default_text_box_height
    global current_turn
    if current_game_mode == 'strategic':
        greatest_width = 300
    else:
        greatest_width = 300
    greatest_width = scale_width(greatest_width)
    max_screen_lines = (default_display_height // 15) - 1
    max_text_box_lines = (text_box_height // 15) - 1
    text_index = 0
    for text_index in range(len(text_list)):
        if text_index < max_text_box_lines:
            if message_width(text_list[-text_index - 1], font_size, 'Times New Roman') > greatest_width:
                greatest_width = message_width(text_list[-text_index - 1], font_size, 'Times New Roman')#manages the width of already printed text lines
    if input_manager.taking_input:
        if message_width("Response: " + message, font_size, 'Times New Roman') > greatest_width:#manages width of user input
            greatest_width = message_width("Response: " + message, font_size, 'Times New Roman')
    else:
        if message_width(message, font_size, 'Times New Roman') > greatest_width:#manages width of user input
            greatest_width = message_width(message, font_size, 'Times New Roman')
    text_box_width = greatest_width + 10
    x, y = scale_coordinates(0, default_display_height - text_box_height)
    pygame.draw.rect(game_display, color_dict['white'], (x, y, text_box_width, text_box_height))#draws white rect to prevent overlapping
    if typing:
        x, y = scale_coordinates(0, default_display_height - text_box_height)
        pygame.draw.rect(game_display, color_dict['red'], (x, y, text_box_width, text_box_height), 3)
        pygame.draw.line(game_display, color_dict['red'], (0, display_height - (font_size + 5)), (text_box_width, display_height - (font_size + 5)))
    else:
        x, y = scale_coordinates(0, default_display_height - text_box_height)
        pygame.draw.rect(game_display, color_dict['black'], (x, y, text_box_width, text_box_height), 3)
        #x, y = (0, default_display_height - (font_size))
        pygame.draw.line(game_display, color_dict['black'], (0, display_height - (font_size + 5)), (text_box_width, display_height - (font_size + 5)))

    text_list = manage_text_list(text_list, max_screen_lines)#number of lines
    myfont = pygame.font.SysFont('Times New Roman', scale_width(15))
    for text_index in range(len(text_list)):
        if text_index < max_text_box_lines:
            textsurface = myfont.render(text_list[(-1 * text_index) - 1], False, (0, 0, 0))
            game_display.blit(textsurface,(10, (-1 * font_size * text_index) + display_height - ((2 * font_size) + 5)))
    if input_manager.taking_input:
        textsurface = myfont.render('Response: ' + message, False, (0, 0, 0))
    else:
        textsurface = myfont.render(message, False, (0, 0, 0))
    game_display.blit(textsurface,(10, display_height - (font_size + 5)))
    
def update_display():
    global loading
    if loading:
        global loading_start_time
        loading_start_time -= 1#makes it faster if the program starts repeating this part
        draw_loading_screen()
    else:
        global typing
        global ctrl
        global button_list
        global grid_list
        global image_list
        global display_height
        global display_width
        global text_list
        global message
        global font_size
        global making_mouse_box
        global mouse_origin_x
        global mouse_origin_y
        global mouse_destination_x
        global mouse_destination_y
        global show_range
        global current_game_mode
        global text_box_height
        global default_text_box_height
        global show_text_box
        global notification_list
        global mouse_follower
        global current_instructions_page
        global mouse_moved_time
        global old_mouse_x
        global old_mouse_y
        game_display.fill((125, 125, 125))
        possible_tooltip_drawers = []
        if not current_game_mode == 'tavern':
            show_range = True

        for grid in grid_list:
            if current_game_mode in grid.modes:
                grid.draw()

        for image in image_list:
            image.has_drawn = False
        for tile in tile_list:
            if current_game_mode in tile.image.modes and tile.image.showing and not tile in overlay_tile_list:
                tile.image.draw()
                tile.image.has_drawn = True
        for image in image_list:
            if not image.has_drawn:
                if current_game_mode in image.modes and image.showing:
                    image.draw()
                    image.has_drawn = True
        for bar in bar_list:
            if current_game_mode in bar.modes and bar.showing:
                bar.draw()
        for overlay_tile in overlay_tile_list:
          if current_game_mode in overlay_tile.image.modes and overlay_tile.image.showing:
                overlay_tile.image.draw()
                overlay_tile.image.has_drawn = True
                
        for grid in grid_list:
            if current_game_mode in grid.modes:
                grid.draw_grid_lines()
            
        for actor in actor_list:
            #if show_selected and current_game_mode in actor.image.modes:
            #    if actor.selected:
            #        pygame.draw.rect(game_display, color_dict['light gray'], (actor.image.outline), actor.image.outline_width)
            #    elif actor.targeted:
            #        pygame.draw.rect(game_display, color_dict['red'], (actor.image.outline), actor.image.outline_width)
            if actor.can_show_tooltip():
                possible_tooltip_drawers.append(actor)#only one of these will be drawn to prevent overlapping tooltips

        for button in button_list:
            if button.can_show():#can_show checks game mode
                button.showing = True
            else:
                button.showing = False
            if not button in notification_list:#notifications are drawn later
                button.draw()
            if button.can_show_tooltip():
                possible_tooltip_drawers.append(button)#only one of these will be drawn to prevent overlapping tooltips
        for label in label_list:
            if not label in notification_list:
                label.draw()
        for notification in notification_list:
            if not notification == current_instructions_page:
                notification.draw()
        if show_text_box:
            draw_text_box()
        if not current_instructions_page == 'none':
            current_instructions_page.draw()
        if not (old_mouse_x, old_mouse_y) == pygame.mouse.get_pos():
            mouse_moved_time = time.time()
            old_mouse_x, old_mouse_y = pygame.mouse.get_pos()
        if time.time() > mouse_moved_time + 0.15:#show tooltip when mouse is still
            manage_tooltip_drawing(possible_tooltip_drawers)
        pygame.display.update()
        loading_start_time = loading_start_time - 3

def draw_loading_screen():
    global loading_start_time
    global loading
    game_display.fill((125, 125, 125))
    loading_image.draw()
    pygame.display.update()    
    if loading_start_time + 2 < time.time():#max of 1 second, subtracts 1 in update_display to lower loading screen showing time
        loading = False

def start_loading():
    global loading_start_time
    global loading
    loading = True
    loading_start_time = time.time()
    update_display()#draw_loading_screen()

def manage_tooltip_drawing(possible_tooltip_drawers):
    global current_instructions_page
    possible_tooltip_drawers_length = len(possible_tooltip_drawers)
    if possible_tooltip_drawers_length == 0:
        return()
    elif possible_tooltip_drawers_length == 1:
        possible_tooltip_drawers[0].draw_tooltip(60)
    else:
        tooltip_index = 1
        stopping = False
        for possible_tooltip_drawer in possible_tooltip_drawers:
            if possible_tooltip_drawer == current_instructions_page:
                possible_tooltip_drawer.draw_tooltip(tooltip_index * 60)
                stopping = True
            if (possible_tooltip_drawer in notification_list) and not stopping:
                possible_tooltip_drawer.draw_tooltip(tooltip_index * 60)
                stopping = True
        if not stopping:
            for possible_tooltip_drawer in possible_tooltip_drawers:
                possible_tooltip_drawer.draw_tooltip(tooltip_index * 60)
                tooltip_index += 1
            
def create_image_dict(stem):#if stem is a certain value, add extra ones, such as special combat animations: only works for images in graphics/mobs
    stem = 'mobs/' + stem
    stem += '/'#goes to that folder
    image_dict = {}
    image_dict['default'] = stem + 'default.png'
    image_dict['right'] = stem + 'right.png'  
    image_dict['left'] = stem + 'left.png'
    return(image_dict)

def display_notification(message):
    global notification_queue
    notification_queue.append(message)
    if len(notification_queue) == 1:
        notification_to_front(message)

def notification_to_front(message):#displays a notification from the queue, which is a list of string messages that this formats into notifications
    new_notification = notification(scale_coordinates(610, 236), scale_width(500), scale_height(500), True, ['strategic'], 'misc/default_notification.png', message)#coordinates, ideal_width, minimum_height, showing, modes, image, message

def show_tutorial_notifications():
    intro_message = "Placeholder tutorial/opener notification"
    display_notification(intro_message)

def manage_rmb_down(clicked_button):
    nothing = 0
    
def manage_lmb_down(clicked_button):
    nothing = 0
    #may be used for selection and such, copy code from other program but no mouse boxes needed

def scale_coordinates(x, y):
    global display_width
    global display_height
    global default_display_width
    global default_display_height
    x_ratio = display_width/default_display_width
    y_ratio = display_height/default_display_height
    scaled_x = round(x * x_ratio)
    scaled_y = round(y * y_ratio)
    return(scaled_x, scaled_y)

def scale_width(width):
    global display_width
    global default_display_width
    ratio = display_width/default_display_width
    scaled_width = round(width * ratio)
    return(scaled_width)

def scale_height(height):
    global display_height
    global default_display_height
    ratio = display_height/default_display_height
    scaled_height = round(height * ratio)
    return(scaled_height)

def generate_article(word):
    global vowels
    if word[0] in vowels:
        return('an')
    else:
        return('a')

def display_instructions_page(page_number):
    global current_instructions_page
    global current_instructions_page_index
    global instructions_list
    current_instructions_page_index = page_number
    current_instructions_page_text = instructions_list[page_number]
    current_instructions_page = instructions_page(current_instructions_page_text)
    
vowels = ['a', 'e', 'i', 'o', 'u']
resolution_finder = pygame.display.Info()
default_display_width = 1728#all parts of game made to be at default and scaled to display
default_display_height = 972
display_width = resolution_finder.current_w - round(default_display_width/10)# + -500
display_height = resolution_finder.current_h - round(default_display_height/10)# - 600
loading = True
loading_start_time = time.time()
myfont = pygame.font.SysFont('Times New Roman', scale_width(15))
font_size = scale_width(15)
game_display = pygame.display.set_mode((display_width, display_height))
pygame.display.set_caption('')
color_dict = {'black': (0, 0, 0), 'white': (255, 255, 255), 'light gray': (230, 230, 230), 'red': (255, 0, 0), 'dark green': (0, 150, 0), 'green': (0, 200, 0), 'bright green': (0, 255, 0), 'blue': (0, 0, 255), 'yellow': (255, 255, 0), 'brown': (132, 94, 59)}
terrain_list = ['clear', 'mountain', 'hills', 'jungle', 'swamp', 'desert']
terrain_colors = {'clear': (150, 200, 104), 'hills': (50, 205, 50), 'jungle': (0, 100, 0), 'water': (0, 0, 200), 'mountain': (100, 100, 100), 'swamp': (100, 100, 50), 'desert': (255, 248, 104)}
game_display.fill(color_dict['white'])
default_text_box_height = 0
text_box_height = 0#set in update display
button_list = []
current_instructions_page = 'none'
current_instructions_page_index = 0
instructions_list = []
#page 1
instructions_message = "Placeholder instructions, use += to add"
instructions_list.append(instructions_message)

grid_list = []
text_list = ['']
image_list = []
bar_list = []
actor_list = []
strategic_actor_list = []
location_list = []
stored_location_list = []
obstacle_list = []
tile_list = []
overlay_tile_list = []
notification_list = []
label_list = []
notification_queue = []
sight_range = 3.5
pygame.key.set_repeat(300, 200)#100)
crashed = False
lmb_down = False
rmb_down = False
mmb_down = False
typing = False
message = ''
show_grid_lines = True
show_text_box = True
mouse_origin_x = 0
mouse_origin_y = 0
mouse_destination_x = 0
mouse_destination_y = 0
show_grid_lines = True
input_manager = input_manager_template()

location_name_image_dict = {}
 
loading_image = loading_image_class('misc/loading.png')
#strategic_map_grid = grid(scale_coordinates(729, 150), scale_width(870), scale_height(810), 64, 60, True, color_dict['dark green'], ['strategic'])
#strategic_map_grid = grid(scale_coordinates(729, 150), scale_width(870), scale_height(810), 32, 30, True, color_dict['dark green'], ['strategic'])
strategic_map_grid = grid(scale_coordinates(729, 150), scale_width(870), scale_height(810), 16, 15, True, color_dict['dark green'], ['strategic'])
#mouse_follower = mouse_follower_class()
button_start_x = 600#x position of leftmost button
button_separation = 60#x separation between each button
current_button_number = 12#tracks current button to move each one farther right

left_arrow_button = button_class(scale_coordinates(button_start_x + (current_button_number * button_separation), 20), scale_width(50), scale_height(50), 'blue', 'move left', True, pygame.K_a, ['strategic'], 'misc/left_button.png')
current_button_number += 1
down_arrow_button = button_class(scale_coordinates(button_start_x + (current_button_number * button_separation), 20), scale_width(50), scale_height(50), 'blue', 'move down', True, pygame.K_s, ['strategic'], 'misc/down_button.png')#movement buttons should be usable in any mode with a grid

up_arrow_button = button_class(scale_coordinates(button_start_x + (current_button_number * button_separation), 80), scale_width(50), scale_height(50), 'blue', 'move up', True, pygame.K_w, ['strategic'], 'misc/up_button.png')
current_button_number += 1
right_arrow_button = button_class(scale_coordinates(button_start_x + (current_button_number * button_separation), 20), scale_width(50), scale_height(50), 'blue', 'move right', True, pygame.K_d, ['strategic'], 'misc/right_button.png')
current_button_number += 2#move more when switching categories

current_button_number += 1

expand_text_box_button = button_class(scale_coordinates(0, default_display_height - 50), scale_width(50), scale_height(50), 'black', 'expand text box', True, pygame.K_j, ['strategic'], 'misc/text_box_size_button.png')#'none' for no keybind
toggle_grid_lines_button = button_class(scale_coordinates(default_display_width - 50, default_display_height - 50), scale_width(50), scale_height(50), 'blue', 'toggle grid lines', True, pygame.K_g, ['strategic'], 'misc/grid_line_button.png')
instructions_button = button_class(scale_coordinates(default_display_width - 50, default_display_height - 170), scale_width(50), scale_height(50), 'blue', 'instructions', True, pygame.K_i, ['strategic'], 'misc/instructions.png')
toggle_text_box_button = button_class(scale_coordinates(75, default_display_height - 50), scale_width(50), scale_height(50), 'blue', 'toggle text box', True, pygame.K_t, ['strategic'], 'misc/toggle_text_box_button.png')

r_shift = 'up'
l_shift = 'up'
capital = False
r_ctrl = 'up'
l_ctrl = 'up'
ctrl = False
start_time = time.time()
current_time = time.time()
mouse_moved_time = time.time()
old_mouse_x, old_mouse_y = pygame.mouse.get_pos()#used in tooltip drawing timing
show_tutorial_notifications()
current_game_mode = 'none'
set_game_mode('strategic')
while not crashed:
    if len(notification_list) == 0:
        stopping = False
    input_manager.update_input()
    if input_manager.taking_input:
        typing = True
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            crashed = True
        if r_shift == 'down' or l_shift == 'down':
            capital = True
        else:
            capital = False
        if r_ctrl == 'down' or l_ctrl == 'down':
            ctrl = True
        else:
            ctrl = False
        if event.type == pygame.KEYDOWN:
            for button in button_list:
                if button.showing and not typing:
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
                r_shift = 'down'
            if event.key == pygame.K_LSHIFT:
                l_shift = 'down'
            if event.key == pygame.K_RCTRL:
                r_ctrl = 'down'
            if event.key == pygame.K_LCTRL:
                l_ctrl = 'down'
            if event.key == pygame.K_ESCAPE:
                typing = False
                message = ''
            if event.key == pygame.K_SPACE:
                if typing:
                    message = add_to_message(message, ' ')
            if event.key == pygame.K_BACKSPACE:
                if typing:
                    message = message[:-1]
            if event.key == pygame.K_a:
                if typing and not capital:
                    message = add_to_message(message, 'a')
                elif typing and capital:
                    message = add_to_message(message, 'A')
            if event.key == pygame.K_b:
                if typing and not capital:
                    message = add_to_message(message, 'b')
                elif typing and capital:
                    message = add_to_message(message, 'B')
            if event.key == pygame.K_c:
                if typing and not capital:
                    message = add_to_message(message, 'c')
                elif typing and capital:
                    message = add_to_message(message, 'C')
            if event.key == pygame.K_d:
                if typing and not capital:
                    message = add_to_message(message, 'd')
                elif typing and capital:
                    message = add_to_message(message, 'D')
            if event.key == pygame.K_e:
                if typing and not capital:
                    message = add_to_message(message, 'e')
                elif typing and capital:
                    message = add_to_message(message, 'E')
            if event.key == pygame.K_f:
                if typing and not capital:
                    message = add_to_message(message, 'f')
                elif typing and capital:
                    message = add_to_message(message, 'F')
            if event.key == pygame.K_g:
                if typing and not capital:
                    message = add_to_message(message, 'g')
                elif typing and capital:
                    message = add_to_message(message, 'G')
            if event.key == pygame.K_h:
                if typing and not capital:
                    message = add_to_message(message, 'h')
                elif typing and capital:
                    message = add_to_message(message, 'H')
            if event.key == pygame.K_i:
                if typing and not capital:
                    message = add_to_message(message, 'i')
                elif typing and capital:
                    message = add_to_message(message, 'I')
            if event.key == pygame.K_j:
                if typing and not capital:
                    message = add_to_message(message, 'j')
                elif typing and capital:
                    message = add_to_message(message, 'J')
            if event.key == pygame.K_k:
                if typing and not capital:
                    message = add_to_message(message, 'k')
                elif typing and capital:
                    message = add_to_message(message, 'K')
            if event.key == pygame.K_l:
                if typing and not capital:
                    message = add_to_message(message, 'l')
                elif typing and capital:
                    message = add_to_message(message, 'L')
            if event.key == pygame.K_m:
                if typing and not capital:
                    message = add_to_message(message, 'm')
                elif typing and capital:
                    message = add_to_message(message, 'M')
            if event.key == pygame.K_n:
                if typing and not capital:
                    message = add_to_message(message, 'n')
                elif typing and capital:
                    message = add_to_message(message, 'N')
            if event.key == pygame.K_o:
                if typing and not capital:
                    message = add_to_message(message, 'o')
                elif typing and capital:
                    message = add_to_message(message, 'O')
            if event.key == pygame.K_p:
                if typing and not capital:
                    message = add_to_message(message, 'p')
                elif typing and capital:
                    message = add_to_message(message, 'P')
            if event.key == pygame.K_q:
                if typing and not capital:
                    message = add_to_message(message, 'q')
                elif typing and capital:
                    message = add_to_message(message, 'Q')
            if event.key == pygame.K_r:
                if typing and not capital:
                    message = add_to_message(message, 'r')
                elif typing and capital:
                    message = add_to_message(message, 'R')
            if event.key == pygame.K_s:
                if typing and not capital:
                    message = add_to_message(message, 's')
                elif typing and capital:
                    message = add_to_message(message, 'S')
            if event.key == pygame.K_t:
                if typing and not capital:
                    message = add_to_message(message, 't')
                elif typing and capital:
                    message = add_to_message(message, 'T')
            if event.key == pygame.K_u:
                if typing and not capital:
                    message = add_to_message(message, 'u')
                elif typing and capital:
                    message = add_to_message(message, 'U')
            if event.key == pygame.K_v:
                if typing and not capital:
                    message = add_to_message(message, 'v')
                elif typing and capital:
                    message = add_to_message(message, 'V')
            if event.key == pygame.K_w:
                if typing and not capital:
                    message = add_to_message(message, 'w')
                elif typing and capital:
                    message = add_to_message(message, 'W')
            if event.key == pygame.K_x:
                if typing and not capital:
                    message = add_to_message(message, 'x')
                elif typing and capital:
                    message = add_to_message(message, 'X')
            if event.key == pygame.K_y:
                if typing and not capital:
                    message = add_to_message(message, 'y')
                elif typing and capital:
                    message = add_to_message(message, 'Y')
            if event.key == pygame.K_z:
                if typing and not capital:
                    message = add_to_message(message, 'z')
                elif typing and capital:
                    message = add_to_message(message, 'Z')
            if event.key == pygame.K_1:
                if typing and not capital:
                    message = add_to_message(message, '1')
                elif typing and capital:
                    message = add_to_message(message, '!')
            if event.key == pygame.K_2:
                if typing and not capital:
                    message = add_to_message(message, '2')
                elif typing and capital:
                    message = add_to_message(message, '@')
            if event.key == pygame.K_3:
                if typing and not capital:
                    message = add_to_message(message, '3')
                elif typing and capital:
                    message = add_to_message(message, '#')
            if event.key == pygame.K_4:
                if typing and not capital:
                    message = add_to_message(message, '4')
                elif typing and capital:
                    message = add_to_message(message, '$')
            if event.key == pygame.K_5:
                if typing and not capital:
                    message = add_to_message(message, '5')
                elif typing and capital:
                    message = add_to_message(message, '%')
            if event.key == pygame.K_6:
                if typing and not capital:
                    message = add_to_message(message, '6')
                elif typing and capital:
                    message = add_to_message(message, '^')
            if event.key == pygame.K_7:
                if typing and not capital:
                    message = add_to_message(message, '7')
                elif typing and capital:
                    message = add_to_message(message, '&')
            if event.key == pygame.K_8:
                if typing and not capital:
                    message = add_to_message(message, '8')
                elif typing and capital:
                    message = add_to_message(message, '*')
            if event.key == pygame.K_9:
                if typing and not capital:
                    message = add_to_message(message, '9')
                elif typing and capital:
                    message = add_to_message(message, '(')
            if event.key == pygame.K_0:
                if typing and not capital:
                    message = add_to_message(message, '0')
                elif typing and capital:
                    message = add_to_message(message, ')')
        if event.type == pygame.KEYUP:
            for button in button_list:
                if not typing or button.keybind_id == pygame.K_TAB or button.keybind_id == pygame.K_e:
                    if button.has_keybind:
                        if event.key == button.keybind_id:
                            button.on_release()
                            button.has_released = True
            if event.key == pygame.K_RSHIFT:
                r_shift = 'up'
            if event.key == pygame.K_LSHIFT:
                l_shift = 'up'
            if event.key == pygame.K_LCTRL:
                l_ctrl = 'up'
            if event.key == pygame.K_RCTRL:
                r_ctrl = 'up'
            if event.key == pygame.K_RETURN:
                if typing:
                    if input_manager.taking_input:
                        input_response = message
                        input_manager.taking_input = False
                        print_to_screen('Response: ' + message)
                        input_manager.receive_input(message)
                        check_pointer_removal('not typing')
                    else:
                        print_to_screen(message)
                    typing = False
                    message = ''
                else:
                    typing = True
    old_lmb_down = lmb_down
    old_rmb_down = rmb_down
    old_mmb_down = mmb_down
    lmb_down, mmb_down, rmb_down = pygame.mouse.get_pressed()

    if not old_rmb_down == rmb_down:#if lmb changes
        if not rmb_down:#if user just released lmb
            clicked_button = False
            stopping = False
            if current_instructions_page == 'none':
                for button in button_list:
                    if button.touching_mouse() and current_game_mode in button.modes and button in notification_list and not stopping:
                        button.on_rmb_click()#prioritize clicking buttons that appear above other buttons and don't press the ones 
                        button.on_rmb_release()
                        clicked_button = True
                        stopping = True
            else:
                if current_instructions_page.touching_mouse() and current_game_mode in current_instructions_page.modes:
                    current_instructions_page.on_rmb_click()
                    clicked_button = True
                    stopping = True
            if not stopping:
                for button in button_list:
                    if button.touching_mouse() and current_game_mode in button.modes:
                        button.on_rmb_click()
                        button.on_rmb_release()
                        clicked_button = True
            manage_rmb_down(clicked_button)

        else:#if user just clicked rmb
            mouse_origin_x, mouse_origin_y = pygame.mouse.get_pos()
            making_mouse_box = True
            
    if not old_lmb_down == lmb_down:#if lmb changes
        if not lmb_down:#if user just released lmb
            clicked_button = False
            stopping = False
            if current_instructions_page == 'none':
                for button in button_list:
                    if button.touching_mouse() and current_game_mode in button.modes and (button in notification_list) and not stopping:
                        button.on_click()#prioritize clicking buttons that appear above other buttons and don't press the ones 
                        button.on_release()
                        clicked_button = True
                        stopping = True
            else:
                if current_instructions_page.touching_mouse() and current_game_mode in current_instructions_page.modes:
                    current_instructions_page.on_click()
                    clicked_button = True
                    stopping = True
            if not stopping:
                for button in button_list:
                    if button.touching_mouse() and current_game_mode in button.modes:
                        button.on_click()
                        button.on_release()
                        clicked_button = True
            manage_lmb_down(clicked_button)#whether button was clicked or not determines whether characters are deselected
            
        else:#if user just clicked lmb
            mouse_origin_x, mouse_origin_y = pygame.mouse.get_pos()
            making_mouse_box = True

    if not loading:
        update_display()
    else:
        draw_loading_screen()
    current_time = time.time()
    for actor in actor_list:
        if not actor.image.image_description == actor.image.previous_idle_image and time.time() >= actor.image.last_image_switch + 0.6:
            actor.image.set_image(actor.image.previous_idle_image)
    start_time = time.time()
pygame.quit()
