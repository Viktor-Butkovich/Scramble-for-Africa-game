from .labels import label
from .buttons import button
from . import scaling
from . import text_tools

class instructions_button(button):
    def __init__(self, coordinates, width, height, color, button_type, keybind_id, modes, image_id, global_manager):
        super().__init__(coordinates, width, height, color, button_type, keybind_id, modes, image_id, global_manager)
        
    def on_click(self):
        if self.can_show():
            self.showing_outline = True
            if self.global_manager.get('current_instructions_page') == 'none':
                display_instructions_page(0, self.global_manager)
            else:
                if not self.global_manager.get('current_instructions_page') == 'none':
                    self.global_manager.get('current_instructions_page').remove()
                    self.global_manager.set('current_instructions_page', 'none')
                self.global_manager.set('current_instructions_page_index', 0)

class instructions_page(label):
    '''
    Label shown when the instructions button is pressed that goes to the next instructions page when clicked, or stops showing instructions if it is the last one, can also have multiple lines
    '''
    def __init__(self, instruction_text, global_manager):
        '''
        Input:
            string representing the text contained in the instructions page, global_manager_template object
        '''
        self.global_manager = global_manager
        self.minimum_height = scaling.scale_height(self.global_manager.get('default_display_height') - 120, self.global_manager)
        self.ideal_width = scaling.scale_width(self.global_manager.get('default_display_width') - 120, self.global_manager)
        super().__init__(scaling.scale_coordinates(60, 60, self.global_manager), self.ideal_width, self.minimum_height, ['strategic'], 'misc/default_instruction.png', instruction_text, global_manager)

    def on_click(self):
        '''
        Input:
            none
        Output:
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

    def set_label(self, new_message):
        '''
        Input:
            string representing this label's new text
        Output:
            Sets this label's text to a list based on the inputted string and changes its size as needed
        '''
        self.message = new_message
        self.format_message()
        for text_line in self.message:
            if text_tools.message_width(text_line, self.font_size, self.font_name) + 10 > self.minimum_width: #self.ideal_width:
                self.width = text_tools.message_width(text_line, self.font_size, self.font_name) + 10

    def draw(self):
        '''
        Input:
            none
        Output:
            Draws this label's image with its text
        '''
        if self.can_show():
            self.image.draw()
            for text_line_index in range(len(self.message)):
                text_line = self.message[text_line_index]
                self.global_manager.get('game_display').blit(text_tools.text(text_line, self.font, self.global_manager), (self.x + 10, self.global_manager.get('display_height') - (self.y + self.height - (text_line_index * self.font_size))))

            
    def format_message(self):
        '''
        Input:
            none
        Output:
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
        new_message.append("Click to go to the next instructions page.")
        new_message.append("Press the display instructions button on the right side of the screen again to close the instructions.")
        new_message.append("Page " + str(self.global_manager.get('current_instructions_page_index') + 1))
        
        self.message = new_message
        
    def update_tooltip(self):
        '''
        Input:
            none
        Output:
            Sets this instructions page's tooltip to describe how to use the instructions
        '''
        self.set_tooltip(["Click to go to the next instructions page.", "Press the display instructions button on the right side of the screen again to close the instructions."])


def display_instructions_page(page_number, global_manager):
    '''
    Input:
        int representing the page number to display, global_manager_template object
    Output:
        Displays a new instructions page corresponding to the inputted page number
    '''
    global_manager.set('current_instructions_page_index', page_number)
    global_manager.set('current_instructions_page_text', global_manager.get('instructions_list')[page_number])
    global_manager.set('current_instructions_page', instructions_page(global_manager.get('current_instructions_page_text'), global_manager))

