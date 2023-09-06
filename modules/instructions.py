#Contains functionality for instructions pages

from .labels import label
from .buttons import button
from . import scaling
from . import text_tools

class instructions_button(button):
    '''
    Button that displays the first page of game instructions when clicked
    '''
    def on_click(self):
        '''
        Description:
            Controls this button's behavior when clicked. This type of button displays the first page of game instructions when clicked
        Input:
            None
        Output:
            None
        '''
        if self.global_manager.get('current_instructions_page') == 'none':
            display_instructions_page(0, self.global_manager)
        else:
            if not self.global_manager.get('current_instructions_page') == 'none':
                self.global_manager.get('current_instructions_page').remove()
                self.global_manager.set('current_instructions_page', 'none')
            self.global_manager.set('current_instructions_page_index', 0)

class instructions_page(label):
    '''
    Label shown when the instructions button is pressed that goes to the next instructions page when clicked, or stops showing instructions if it is the last one. Unlike other labels, can have multiple lines
    '''
    def __init__(self, input_dict, global_manager):
        '''
        Description:
            Initializes this object
        Input:
            dictionary input_dict: Keys corresponding to the values needed to initialize this object
                'parent_collection' = 'none': interface_collection value - Interface collection that this element directly reports to, not passed for independent element
                'message': string value - Default text for this label
            global_manager_template global_manager: Object that accesses shared variables
        Output:
            None
        '''
        self.global_manager = global_manager
        self.minimum_height = scaling.scale_height(self.global_manager.get('default_display_height') - 120, self.global_manager)
        self.ideal_width = scaling.scale_width(self.global_manager.get('default_display_width') - 120, self.global_manager)
        input_dict['coordinates'] = scaling.scale_coordinates(60, 60, self.global_manager)
        input_dict['minimum_width'] = self.ideal_width
        input_dict['height'] = self.minimum_height
        input_dict['modes'] = ['strategic', 'europe']
        input_dict['image_id'] = 'misc/default_instructions.png'
        super().__init__(input_dict, global_manager)

    def on_click(self):
        '''
        Description:
            Controls this button's behavior when clicked. This type of button displays the next page of game instructions when clicked, or closes the instructions if there are no more pages
        Input:
            None
        Output:
            None
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
        Description:
            Sets this page's text to the corresponding item in the inputted string, adjusting width and height as needed
        Input:
            string instruction_text: New text for this instructions page
        Output:
            None
        '''
        self.message = new_message
        self.format_message()
        for text_line in self.message:
            if text_tools.message_width(text_line, self.font_size, self.font_name) + 10 > self.minimum_width: #self.ideal_width:
                self.width = text_tools.message_width(text_line, self.font_size, self.font_name) + 10

    def draw(self):
        '''
        Description:
            Draws this page and draws its text on top of it
        Input:
            None
        Output:
            None
        '''
        if self.showing:
            self.image.draw()
            for text_line_index in range(len(self.message)):
                text_line = self.message[text_line_index]
                self.global_manager.get('game_display').blit(text_tools.text(text_line, self.font, self.global_manager), (self.x + 10, self.global_manager.get('display_height') - (self.y + self.height - (text_line_index * self.font_size))))

    def format_message(self):
        '''
        Description:
            Converts this page's string message to a list of strings, with each string representing a line of text. Each line of text ends when its width exceeds the ideal_width. Also describes how to close the instructions or go to
                the next page
        Input:
            None
        Output:
            None
        '''
        new_message = []
        next_line = ''
        next_word = ''
        for index in range(len(self.message)):
            next_word += self.message[index]
            if self.message[index] == ' ':
                if text_tools.message_width(next_line + next_word, self.font_size, self.font_name) > self.ideal_width:
                    new_message.append(next_line)
                    next_line = ''
                next_line += next_word
                next_word = ''
        next_line += next_word
        new_message.append(next_line)
        new_message.append('Click to go to the next instructions page.')
        new_message.append('Press the display instructions button on the right side of the screen again to close the instructions.')
        new_message.append('Page ' + str(self.global_manager.get('current_instructions_page_index') + 1))
        
        self.message = new_message
        
    def update_tooltip(self):
        '''
        Description:
            Sets this page's tooltip to what it should be. By default, instructions pages describe how to close the instructions or go to the next page
        Input:
            None
        Output:
            None
        '''
        self.set_tooltip(['Click to go to the next instructions page.', 'Press the display instructions button on the right side of the screen again to close the instructions.'])


def display_instructions_page(page_number, global_manager):
    '''
    Description:
        Displays a new instructions page with text corresponding to the inputted page number
    Input:
        int page_number: Page number of instructions to display,
        global_manager_template global_manager: Object that accesses shared variables
    Output:
        None
    '''
    global_manager.set('current_instructions_page_index', page_number)
    global_manager.set('current_instructions_page_text', global_manager.get('instructions_list')[page_number])
    global_manager.set('current_instructions_page', instructions_page(global_manager.get('current_instructions_page_text'), global_manager))
