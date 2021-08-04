import pygame
from .buttons import button
from . import scaling
from . import text_tools
from . import utility

class label(button):
    '''
    A button that shares most of a normal button's image and tooltip behaviors but does nothing when clicked. Used to display information
    '''
    def __init__(self, coordinates, minimum_width, height, modes, image_id, message, global_manager): #message is initially a string
        '''
        Input:
            coordinates: tuple of 2 integers for initial coordinate x and y values
            minimum_width: int representing the minimum width in pixels of the button. As the length of its message increases, the label's width will increase to accomodate it. 
            height: int representing the height in pixels of the button
            modes: list of strings representing the game modes in which this button is visible, such as 'strategic' for a button appearing when on the strategic map
            image_id: string representing the address of the button's image within the graphics folder such as 'misc/left_button.png' to represent SFA/graphics/misc/left_button.png
            message: string representing the contents of the label. This is converted by format_message to a list of strings, in which each string is a line of text on the label. By default, labels have 1 line of text.
        '''
        self.global_manager = global_manager
        self.global_manager.get('label_list').append(self)
        self.modes = modes
        self.message = message
        self.minimum_width = minimum_width#self.ideal_width = ideal_width
        self.width = minimum_width#ideal_width
        self.font_size = scaling.scale_width(25, global_manager)
        self.font_name = "Times New Roman"
        self.font = pygame.font.SysFont(self.font_name, self.font_size)
        self.current_character = 'none'
        self.height = height#minimum_height
        super().__init__(coordinates, self.width, self.height, 'green', 'label', 'none', self.modes, image_id, global_manager)
        self.set_label(self.message)

    def set_label(self, new_message):
        '''
        Input:
            string representing this label's new text
        Output:
            Sets this label's text to a list based on the inputted string and changes its size as needed
        '''
        self.message = new_message
        if text_tools.message_width(self.message, self.font_size, self.font_name) + 10 > self.minimum_width: #self.ideal_width:
            self.width = text_tools.message_width(self.message, self.font_size, self.font_name) + 10
            self.image.width = self.width
            self.Rect.width = self.width
            self.image.set_image(self.image.image_id) #update width scaling
            self.image.Rect = self.Rect

    def update_tooltip(self):
        '''
        Input:
            none
        Output:
            Sets this label's tooltip to be the same as the text it displays
        '''
        self.set_tooltip([self.message])
            
    def on_click(self):
        '''
        Input:
            none
        Output:
            none, unlike superclass
        '''
        i = 0

    def remove(self):
        '''
        Input:
            none
        Output:
            Removes the object from relevant lists and prevents it from further appearing in or affecting the program
        '''
        self.global_manager.set('label_list', utility.remove_from_list(self.global_manager.get('label_list'), self))
        self.global_manager.set('button_list', utility.remove_from_list(self.global_manager.get('button_list'), self))
        self.global_manager.set('image_list', utility.remove_from_list(self.global_manager.get('image_list'), self.image))

    def draw(self):
        '''
        Input:
            none
        Output:
            Draws this label's image with its text
        '''
        if self.can_show():
            self.image.draw()
            self.global_manager.get('game_display').blit(text_tools.text(self.message, self.font, self.global_manager), (self.x + 10, self.global_manager.get('display_height') - (self.y + self.height)))
                
    def draw_tooltip(self, y_displacement):
        '''
        Input:
            int representing the number of vertical pixels the label will be moved by, allowing multiple tooltips to be shown at once
        Output:
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

class value_label(label):
    '''
    Label that tracks the value of a certain variable and is attached to a value_tracker object
    '''
    def __init__(self, coordinates, minimum_width, height, modes, image_id, value_name, global_manager):
        super().__init__(coordinates, minimum_width, height, modes, image_id, 'none', global_manager)
        self.value_name = value_name
        self.tracker = self.global_manager.get(value_name + '_tracker')
        self.tracker.value_label = self
        self.update_label(self.tracker.get())

    def update_label(self, new_value):
        self.set_label(self.value_name + ': ' + str(new_value))
    

