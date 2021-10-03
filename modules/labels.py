import pygame
from .buttons import button
from . import scaling
from . import text_tools
from . import utility

class label(button):
    '''
    A button that shares most of a button's behaviors but displays a message and does nothing when clicked
    '''
    def __init__(self, coordinates, minimum_width, height, modes, image_id, message, global_manager): #message is initially a string
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this label
            int minimum_width: Minimum pixel width of this label. Its width will increase if the contained text would extend past the edge of the label
            int height: Pixel height of this label
            string list modes: Game modes during which this label can appear
            string image_id: File path to the image used by this object
            string message: Text that will appear on the label by default
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.global_manager = global_manager
        self.global_manager.get('label_list').append(self)
        self.modes = modes
        self.message = message
        self.minimum_width = minimum_width
        self.width = minimum_width
        self.font_size = scaling.scale_width(25, global_manager)
        self.font_name = self.global_manager.get('font_name')
        self.font = pygame.font.SysFont(self.font_name, self.font_size)
        self.current_character = 'none'
        self.height = height
        super().__init__(coordinates, self.width, self.height, 'green', 'label', 'none', self.modes, image_id, global_manager)
        self.set_label(self.message)

    def set_label(self, new_message):
        '''
        Description:
            Sets this label's text to the inputted string, adjusting width as needed
        Input:
            string new_message: New text for this label
        Output:
            None
        '''
        self.message = new_message
        if text_tools.message_width(self.message, self.font_size, self.font_name) + scaling.scale_width(10, self.global_manager) > self.minimum_width: #self.ideal_width:
            self.width = text_tools.message_width(self.message, self.font_size, self.font_name) + scaling.scale_width(10, self.global_manager)
        else:
            self.width = self.minimum_width
        self.image.width = self.width
        self.Rect.width = self.width
        self.image.set_image(self.image.image_id)
        self.image.Rect = self.Rect
            

    def update_tooltip(self):
        '''
        Description:
            Sets this label's tooltip to what it should be. By default, labels have tooltips matching their text
        Input:
            None
        Output:
            None
        '''
        self.set_tooltip([self.message])
            
    def on_click(self):
        '''
        Description:
            Controls this label's behavior when clicked. By default, labels do nothing when clicked
        Input:
            None
        Output:
            None
        '''
        i = 0

    def remove(self):
        '''
        Description:
            Removes this object from relevant lists and prevents it from further appearing in or affecting the program
        Input:
            None
        Output:
            None
        '''
        self.global_manager.set('label_list', utility.remove_from_list(self.global_manager.get('label_list'), self))
        self.global_manager.set('button_list', utility.remove_from_list(self.global_manager.get('button_list'), self))
        self.global_manager.set('image_list', utility.remove_from_list(self.global_manager.get('image_list'), self.image))

    def draw(self):
        '''
        Description:
            Draws this label and draws its text on top of it
        Input:
            None
        Output:
            None
        '''
        if self.can_show():
            self.image.draw()
            self.global_manager.get('game_display').blit(text_tools.text(self.message, self.font, self.global_manager), (self.x + scaling.scale_width(10, self.global_manager), self.global_manager.get('display_height') -
                (self.y + self.height)))

class value_label(label):
    '''
    Label that tracks the value of a certain variable and is attached to a value_tracker object. Whenever the value of the value_tracker changes, this label is automatically changed
    '''
    def __init__(self, coordinates, minimum_width, height, modes, image_id, value_name, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this label
            int minimum_width: Minimum pixel width of this label. Its width will increase if the contained text would extend past the edge of the label
            int height: Pixel height of this label
            string list modes: Game modes during which this label can appear
            string image_id: File path to the image used by this object
            string value_name: Type of value tracked by this label, like 'turn' for turn number
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(coordinates, minimum_width, height, modes, image_id, 'none', global_manager)
        self.value_name = value_name
        self.tracker = self.global_manager.get(value_name + '_tracker')
        self.tracker.value_label = self
        self.update_label(self.tracker.get())

    def update_label(self, new_value):
        '''
        Description:
            Updates the value shown by this label when to match the value of its value_tracker
        Input:
            int new_value: New value of this label's value_tracker
        Output:
            None
        '''
        self.set_label(self.value_name + ': ' + str(new_value))

class money_label(value_label):
    '''
    Special type of value label that tracks money
    '''
    def __init__(self, coordinates, minimum_width, height, modes, image_id, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this label
            int minimum_width: Minimum pixel width of this label. Its width will increase if the contained text would extend past the edge of the label
            int height: Pixel height of this label
            string list modes: Game modes during which this label can appear
            string image_id: File path to the image used by this object
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        super().__init__(coordinates, minimum_width, height, modes, image_id, 'money', global_manager)

    def update_tooltip(self):
        '''
        Description:
            Sets this label's tooltip to what it should be. A money_label's tooltip shows its text followed by the upkeep of the player's units each turn
        Input:
            None
        Output:
            None
        '''
        tooltip_text = [self.message]
        num_workers = self.global_manager.get('num_workers')
        worker_upkeep = self.global_manager.get('worker_upkeep')
        total_upkeep = num_workers * worker_upkeep
        tooltip_text.append("Each of your " + str(num_workers) + " workers will cost " + str(worker_upkeep) + " money per turn, totaling to " + str(total_upkeep) + " money")
        self.set_tooltip(tooltip_text)

class commodity_prices_label(label):
    '''
    Label that shows the price of each commodity. Unlike most labels, its message is a list of strings rather than a string, allowing it to have a line for each commodity
    '''
    def __init__(self, coordinates, minimum_width, height, modes, image_id, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            int tuple coordinates: Two values representing x and y coordinates for the pixel location of this label
            int minimum_width: Minimum pixel width of this label. Its width will increase if the contained text would extend past the edge of the label
            int height: Pixel height of this label
            string list modes: Game modes during which this label can appear
            string image_id: File path to the image used by this object
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.ideal_width = minimum_width
        self.minimum_height = height
        super().__init__(coordinates, minimum_width, height, modes, image_id, 'none', global_manager) #coordinates, minimum_width, height, modes, image_id, message, global_manager
        self.font_size = scaling.scale_height(30, global_manager)
        self.font_name = self.global_manager.get('font_name')#self.font_name = "Times New Roman"
        self.font = pygame.font.SysFont(self.font_name, self.font_size)
        self.update_label()

    def update_label(self):
        '''
        Description:
            Updates the values shown by this label when commodity prices change
        Input:
            None
        Output:
            None
        '''
        message = ["Prices: "]
        widest_commodity_width = 0 #text_tools.message_width(message, fontsize, font_name)
        for current_commodity in self.global_manager.get('commodity_types'):
            current_message_width = text_tools.message_width(current_commodity, self.font_size, self.font_name)
            if current_message_width > widest_commodity_width:
                widest_commodity_width = current_message_width
        for current_commodity in self.global_manager.get('commodity_types'):
            current_line = ''
            while text_tools.message_width(current_line + current_commodity, self.font_size, self.font_name) < widest_commodity_width:
                current_line += ' '
            current_line += current_commodity + ": " +  str(self.global_manager.get('commodity_prices')[current_commodity])
            message.append(current_line)
        self.set_label(message)
            
    def set_label(self, new_message):
        '''
        Description:
            Sets each line of this label's text to the corresponding item in the inputted list, adjusting width as needed
        Input:
            string list new_message: New text for this label, with each item corresponding to a line of text
        Output:
            None
        '''
        self.message = new_message
        for text_line in self.message:
            if text_tools.message_width(text_line, self.font_size, self.font_name) > self.ideal_width - scaling.scale_width(10, self.global_manager) and text_tools.message_width(text_line, self.font_size, self.font_name) + scaling.scale_width(10, self.global_manager) > self.width:
                self.width = text_tools.message_width(text_line, self.font_size, self.font_name) + scaling.scale_width(20, self.global_manager)# + 20
                self.image.width = self.width
                self.Rect.width = self.width
                self.image.set_image(self.image.image_id) #update width scaling
                self.image.Rect = self.Rect

    def draw(self):
        '''
        Description:
            Draws this label and draws its text on top of it
        Input:
            None
        Output:
            None
        '''
        if self.global_manager.get('current_game_mode') in self.modes:
            self.image.draw()
            for text_line_index in range(len(self.message)):
                text_line = self.message[text_line_index]
                self.global_manager.get('game_display').blit(text_tools.text(text_line, self.font, self.global_manager), (self.x + scaling.scale_width(10, self.global_manager), self.global_manager.get('display_height') -
                    (self.y + self.height - (text_line_index * self.font_size))))

    def update_tooltip(self):
        '''
        Input:
            none
        Output:
            Sets this label's tooltip to be the same as the text it displays
        '''
        self.set_tooltip(self.message)

