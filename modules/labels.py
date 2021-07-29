import pygame
from .buttons import button
from . import scaling
from . import text_tools
from . import utility

class label(button):
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
        self.font_size = scaling.scale_width(25, global_manager)
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
        '''
        Inputs:
            string representing this label's new text
        Outputs:
            Sets this label's text to a list based on the inputted string and changes its size as needed
        '''
        self.message = new_message
        self.format_message()
        for text_line in self.message:
            if text_tools.message_width(text_line, self.font_size, self.font_name) + 10 > self.ideal_width:
                self.width = text_tools.message_width(text_line, self.font_size, self.font_name) + 10

    def format_message(self): #takes a string message and divides it into a list of strings based on length
        '''
        Inputs:
            none
        Outputs:
            Convert's this label's message string attribute to a list of strings representing lines that will appear on the label
        '''
        new_message = []
        next_line = ""
        next_word = ""
        for index in range(len(self.message)):
            next_word += self.message[index]
            if self.message[index] == " ":
                if text_tools.message_width(next_line + next_word, self.font_size, self.font_name) > self.ideal_width:
                    new_message.append(next_line)
                    next_line = ""
                next_line += next_word
                next_word = ""
        #if text_tools.message_width(next_line + next_word, self.font_size, self.font_name) > self.ideal_width and self in level_up_option_list: #normal labels shouldn't go to next line, but level up options should
        #    new_message.append(next_line)
        #    next_line = next_word
        #    new_message.append(next_line)
        #else: #obsolete
        next_line += next_word
        new_message.append(next_line)
            
        greatest_width = 0
        for line in new_message: #while formatting, trim each line to something close to ideal width, then set actual width to the longest one
            if text_tools.message_width(line, self.font_size, self.font_name) > greatest_width:
                greatest_width = text_tools.message_width(line, self.font_size, self.font_name)
        self.width = greatest_width + 10
        self.message = new_message

    def update_tooltip(self):
        '''
        Inputs:
            none
        Outputs:
            Sets this label's tooltip to be the same as the text it displays
        '''
        self.set_tooltip(self.message)
            
    def on_click(self):
        '''
        Inputs:
            none
        Outputs:
            none, unlike superclass
        '''
        i = 0

    def remove(self):
        '''
        Inputs:
            none
        Outputs:
            Removes the object from relevant lists and prevents it from further appearing in or affecting the program
        '''
        self.global_manager.set('label_list', utility.remove_from_list(self.global_manager.get('label_list'), self))
        self.global_manager.set('button_list', utility.remove_from_list(self.global_manager.get('button_list'), self))
        self.global_manager.set('image_list', utility.remove_from_list(self.global_manager.get('image_list'), self.image))

    def draw(self):
        '''
        Inputs:
            none
        Outputs:
            Draws this label's image with its text
        '''
        if self.global_manager.get('current_game_mode') in self.modes:
            self.image.draw()
            for text_line_index in range(len(self.message)):
                text_line = self.message[text_line_index]
                self.global_manager.get('game_display').blit(text_tools.text(text_line, self.font, self.global_manager), (self.x + 10, self.global_manager.get('display_height') - (self.y + self.height - (text_line_index * self.font_size))))
                
    def draw_tooltip(self, y_displacement):
        '''
        Inputs:
            int representing the number of vertical pixels the label will be moved by, allowing multiple tooltips to be shown at once
        Outputs:
            Draw's this label's tooltip at a position depending on the mouse's position and the inputted int
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
            self.global_manager.get('game_display').blit(text_tools.text(text_line, self.global_manager.get('myfont'), self.global_manager), (self.tooltip_box.x + 10, self.tooltip_box.y + (text_line_index * self.global_manager.get('font_size'))))

class instructions_page(label):
    '''
    Label shown when the instructions button is pressed that goes to the next instructions page when clicked, or stops showing instructions if it is the last one
    '''
    def __init__(self, instruction_text, global_manager):
        '''
        Inputs:
            string representing the text contained in the instructions page, global_manager_template object
        '''
        self.global_manager = global_manager
        super().__init__(scaling.scale_coordinates(60, 60, self.global_manager), scaling.scale_width(self.global_manager.get('default_display_width') - 120, self.global_manager), scaling.scale_height(self.global_manager.get('default_display_height') - 120, self.global_manager), ['strategic'], 'misc/default_instruction.png', instruction_text, global_manager)

    def on_click(self):
        '''
        Inputs:
            none
        Outputs:
            When clicked, goes to the next instructions page if possible, or closes the instructions if there are no more instructions pages
        '''
        if not self.global_manager.get('current_instructions_page_index') == len(self.global_manager.get('instructions_list')) - 1:
            self.global_manager.set('current_instructions_page_index', self.global_manager.get('current_instructions_page_index') + 1)
            self.global_manager.set('current_instructions_page_text', self.global_manager.get('instructions_list')[self.global_manager.get('current_instructions_page_index')])
            self.global_manager.set('current_instructions_page', instructions_page(self.global_manager.get('current_instructions_page_text')), self.global_manager) #create a new page and remove this one
            self.remove()
        else:
            self.remove()
            self.global_manager.set('current_instructions_page', 'none')
            
    def format_message(self):
        '''
        Inputs:
            none
        Outputs:
            Similar to superclass except describes to the user how to use the instructions
        '''
        new_message = []
        next_line = ""
        next_word = ""
        for index in range(len(self.message)):
            next_word += self.message[index]
            if self.message[index] == " ":
                if text_tools.message_width(next_line + next_word, self.font_size, self.font_name) > self.ideal_width:
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
        '''
        Inputs:
            none
        Outputs:
            Sets this instructions page's tooltip to describe how to use the instructions
        '''
        self.set_tooltip(["Click to go to the next instructions page.", "Press the display instructions button on the right side of the screen again to close the instructions."])

